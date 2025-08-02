#!/usr/bin/env python3
"""
Database Connection Pool - High Performance Database Management
Provides connection pooling, automatic retry, and transaction management
"""

import sqlite3
import queue
import threading
import time
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
import weakref

@dataclass
class ConnectionStats:
    """Statistics for database connection usage"""
    total_connections: int = 0
    active_connections: int = 0
    peak_connections: int = 0
    total_queries: int = 0
    failed_queries: int = 0
    average_query_time: float = 0.0
    connection_reuses: int = 0

class DatabaseConnection:
    """Enhanced database connection with automatic retry and statistics"""
    
    def __init__(self, db_path: str, connection_id: int):
        self.db_path = db_path
        self.connection_id = connection_id
        self.connection = None
        self.created_at = time.time()
        self.last_used = time.time()
        self.query_count = 0
        self.is_healthy = True
        self.lock = threading.Lock()
        
        self._create_connection()
    
    def _create_connection(self):
        """Create and configure database connection"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0,
                isolation_level=None  # Autocommit mode
            )
            
            # Optimize SQLite settings for performance
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("PRAGMA synchronous=NORMAL")
            self.connection.execute("PRAGMA cache_size=-64000")  # 64MB cache
            self.connection.execute("PRAGMA temp_store=MEMORY")
            self.connection.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
            
            # Enable foreign keys and row factory
            self.connection.execute("PRAGMA foreign_keys=ON")
            self.connection.row_factory = sqlite3.Row
            
            self.is_healthy = True
            logging.info(f"Database connection {self.connection_id} created successfully")
            
        except Exception as e:
            self.is_healthy = False
            logging.error(f"Failed to create database connection {self.connection_id}: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = None) -> Any:
        """Execute query with automatic retry and error handling"""
        with self.lock:
            self.last_used = time.time()
            self.query_count += 1
            
            start_time = time.time()
            
            try:
                if not self.is_healthy:
                    self._create_connection()
                
                cursor = self.connection.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                result = None
                if fetch == 'one':
                    result = cursor.fetchone()
                elif fetch == 'all':
                    result = cursor.fetchall()
                elif fetch == 'many':
                    result = cursor.fetchmany()
                else:
                    result = cursor.rowcount
                
                self.connection.commit()
                
                query_time = time.time() - start_time
                logging.debug(f"Query executed in {query_time:.3f}s on connection {self.connection_id}")
                
                return result
                
            except sqlite3.Error as e:
                logging.error(f"Database query error on connection {self.connection_id}: {e}")
                self.is_healthy = False
                raise
            except Exception as e:
                logging.error(f"Unexpected error on connection {self.connection_id}: {e}")
                raise
    
    def close(self):
        """Close the database connection"""
        with self.lock:
            if self.connection:
                try:
                    self.connection.close()
                    logging.info(f"Database connection {self.connection_id} closed")
                except Exception as e:
                    logging.error(f"Error closing connection {self.connection_id}: {e}")
                finally:
                    self.connection = None
                    self.is_healthy = False

class DatabaseConnectionPool:
    """
    High-performance database connection pool with automatic management
    """
    
    def __init__(self, db_path: str, pool_size: int = 10, max_overflow: int = 5):
        self.db_path = Path(db_path)
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool = queue.Queue(maxsize=pool_size + max_overflow)
        self.all_connections = weakref.WeakSet()
        self.stats = ConnectionStats()
        self.lock = threading.Lock()
        self._connection_counter = 0
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize connection pool
        self._initialize_pool()
        
        # Start background maintenance thread
        self.maintenance_thread = threading.Thread(target=self._maintenance_worker, daemon=True)
        self.maintenance_thread.start()
    
    def _initialize_pool(self):
        """Initialize the connection pool with base connections"""
        try:
            # Ensure database file exists
            if not self.db_path.exists():
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                # Create empty database
                temp_conn = sqlite3.connect(str(self.db_path))
                temp_conn.close()
            
            # Create initial connections
            for i in range(self.pool_size):
                conn = self._create_connection()
                self.pool.put(conn, block=False)
                
            self.logger.info(f"Database connection pool initialized with {self.pool_size} connections")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def _create_connection(self) -> DatabaseConnection:
        """Create a new database connection"""
        with self.lock:
            self._connection_counter += 1
            conn = DatabaseConnection(str(self.db_path), self._connection_counter)
            self.all_connections.add(conn)
            self.stats.total_connections += 1
            return conn
    
    @contextmanager
    def get_connection(self, timeout: float = 10.0):
        """
        Get a connection from the pool with automatic return
        
        Usage:
            with pool.get_connection() as conn:
                result = conn.execute_query("SELECT * FROM coins", fetch='all')
        """
        conn = None
        start_time = time.time()
        
        try:
            # Try to get connection from pool
            try:
                conn = self.pool.get(timeout=timeout)
                self.stats.connection_reuses += 1
            except queue.Empty:
                # Pool exhausted, create overflow connection if allowed
                if self.stats.active_connections < self.pool_size + self.max_overflow:
                    conn = self._create_connection()
                    self.logger.warning("Created overflow connection")
                else:
                    raise Exception("Connection pool exhausted and max overflow reached")
            
            # Update statistics
            with self.lock:
                self.stats.active_connections += 1
                self.stats.peak_connections = max(self.stats.peak_connections, self.stats.active_connections)
            
            # Yield connection for use
            yield conn
            
        except Exception as e:
            self.logger.error(f"Connection pool error: {e}")
            if conn:
                conn.is_healthy = False
            raise
        finally:
            # Return connection to pool
            if conn:
                with self.lock:
                    self.stats.active_connections -= 1
                
                # Only return healthy connections to pool
                if conn.is_healthy and self.pool.qsize() < self.pool_size:
                    try:
                        self.pool.put(conn, block=False)
                    except queue.Full:
                        # Pool full, close overflow connection
                        conn.close()
                else:
                    # Close unhealthy or overflow connections
                    conn.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = None, timeout: float = 10.0) -> Any:
        """
        Execute a query using a pooled connection
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: 'one', 'all', 'many', or None
            timeout: Connection timeout
        
        Returns:
            Query result based on fetch parameter
        """
        start_time = time.time()
        
        try:
            with self.get_connection(timeout=timeout) as conn:
                result = conn.execute_query(query, params, fetch)
                
                # Update statistics
                query_time = time.time() - start_time
                with self.lock:
                    self.stats.total_queries += 1
                    
                    # Update average query time (rolling average)
                    if self.stats.total_queries == 1:
                        self.stats.average_query_time = query_time
                    else:
                        self.stats.average_query_time = (
                            (self.stats.average_query_time * (self.stats.total_queries - 1) + query_time) 
                            / self.stats.total_queries
                        )
                
                return result
                
        except Exception as e:
            with self.lock:
                self.stats.failed_queries += 1
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[tuple], timeout: float = 30.0) -> int:
        """Execute multiple queries in a transaction"""
        try:
            with self.get_connection(timeout=timeout) as conn:
                with conn.lock:
                    cursor = conn.connection.cursor()
                    cursor.execute("BEGIN TRANSACTION")
                    
                    try:
                        for params in params_list:
                            cursor.execute(query, params)
                        
                        cursor.execute("COMMIT")
                        return len(params_list)
                        
                    except Exception as e:
                        cursor.execute("ROLLBACK")
                        raise e
                        
        except Exception as e:
            self.logger.error(f"Batch execution failed: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            return {
                "pool_size": self.pool_size,
                "max_overflow": self.max_overflow,
                "available_connections": self.pool.qsize(),
                "total_connections": self.stats.total_connections,
                "active_connections": self.stats.active_connections,
                "peak_connections": self.stats.peak_connections,
                "total_queries": self.stats.total_queries,
                "failed_queries": self.stats.failed_queries,
                "success_rate": (
                    (self.stats.total_queries - self.stats.failed_queries) / max(self.stats.total_queries, 1) * 100
                ),
                "average_query_time": self.stats.average_query_time,
                "connection_reuses": self.stats.connection_reuses,
                "pool_efficiency": (
                    self.stats.connection_reuses / max(self.stats.total_queries, 1) * 100
                )
            }
    
    def _maintenance_worker(self):
        """Background thread for connection maintenance"""
        while True:
            try:
                time.sleep(300)  # Run every 5 minutes
                
                # Clean up stale connections
                current_time = time.time()
                stale_connections = []
                
                # Check all connections for staleness (unused for 30+ minutes)
                for conn in list(self.all_connections):
                    if current_time - conn.last_used > 1800:  # 30 minutes
                        stale_connections.append(conn)
                
                # Close stale connections
                for conn in stale_connections:
                    conn.close()
                
                if stale_connections:
                    self.logger.info(f"Cleaned up {len(stale_connections)} stale connections")
                
                # Log statistics
                stats = self.get_stats()
                self.logger.info(f"Pool stats: {stats['available_connections']}/{stats['pool_size']} available, "
                               f"{stats['total_queries']} queries, {stats['success_rate']:.1f}% success rate")
                
            except Exception as e:
                self.logger.error(f"Maintenance worker error: {e}")
    
    def close_all(self):
        """Close all connections in the pool"""
        self.logger.info("Closing all database connections...")
        
        # Close all connections in pool
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except queue.Empty:
                break
        
        # Close any remaining connections
        for conn in list(self.all_connections):
            conn.close()
        
        self.logger.info("All database connections closed")

# Global pool instance
_db_pool = None

def get_database_pool(db_path: str = "data/trench.db", pool_size: int = 10) -> DatabaseConnectionPool:
    """Get or create the global database pool"""
    global _db_pool
    
    if _db_pool is None:
        _db_pool = DatabaseConnectionPool(db_path, pool_size)
    
    return _db_pool

# Convenience functions for easy migration
def execute_query(query: str, params: tuple = None, fetch: str = None) -> Any:
    """Execute query using the global pool"""
    pool = get_database_pool()
    return pool.execute_query(query, params, fetch)

def execute_many(query: str, params_list: List[tuple]) -> int:
    """Execute multiple queries using the global pool"""
    pool = get_database_pool()
    return pool.execute_many(query, params_list)

# Context manager for database transactions
@contextmanager
def database_transaction():
    """Database transaction context manager"""
    pool = get_database_pool()
    with pool.get_connection() as conn:
        with conn.lock:
            cursor = conn.connection.cursor()
            cursor.execute("BEGIN TRANSACTION")
            
            try:
                yield conn
                cursor.execute("COMMIT")
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e