"""
🗄️ TrenchCoat Pro - Advanced Database Management
Backup, migration, and optimization for SQLite
"""

import sqlite3
import shutil
import gzip
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import pandas as pd
import schedule
import threading

from config import config
from monitoring import logger, monitor, log_errors

class DatabaseManager:
    """Advanced database management with backup and optimization"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.get_database_url()
        self.backup_dir = Path(config.DATABASE_BACKUP_DIR)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure database exists
        self._init_database()
        
        # Start backup scheduler in background
        self._start_backup_scheduler()
    
    def _init_database(self):
        """Initialize database with proper settings"""
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            
            # Create indexes for performance
            self._create_indexes(conn)
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Create performance indexes"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_coins_ticker ON coins(ticker)",
            "CREATE INDEX IF NOT EXISTS idx_coins_ca ON coins(ca)",
            "CREATE INDEX IF NOT EXISTS idx_coins_axiom_mc ON coins(axiom_mc DESC)",
            "CREATE INDEX IF NOT EXISTS idx_history_ca_time ON coin_history(contract_address, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_price_history ON price_history(contract_address, timestamp)"
        ]
        
        for idx in indexes:
            try:
                conn.execute(idx)
            except sqlite3.OperationalError:
                pass  # Index might already exist
    
    @log_errors
    def backup_database(self, compress: bool = True) -> str:
        """Create database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"trench_backup_{timestamp}.db"
        
        if compress:
            backup_name += ".gz"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            if compress:
                # Compressed backup
                with open(self.db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Regular backup
                shutil.copy2(self.db_path, backup_path)
            
            logger.log_info(f"Database backed up to {backup_path}")
            monitor.record_metric("db_backup_success", 1)
            
            # Clean old backups
            self._clean_old_backups()
            
            return str(backup_path)
            
        except Exception as e:
            logger.log_error(f"Backup failed", e)
            monitor.record_metric("db_backup_failure", 1)
            raise
    
    def _clean_old_backups(self, keep_days: int = 7):
        """Remove backups older than keep_days"""
        cutoff = datetime.now() - timedelta(days=keep_days)
        
        for backup in self.backup_dir.glob("trench_backup_*.db*"):
            # Extract timestamp from filename
            try:
                timestamp_str = backup.stem.split('_')[2] + backup.stem.split('_')[3]
                file_date = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
                
                if file_date < cutoff:
                    backup.unlink()
                    logger.log_info(f"Deleted old backup: {backup}")
            except:
                pass  # Skip if can't parse timestamp
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup"""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            logger.log_error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Create safety backup of current database
            safety_backup = self.backup_database(compress=False)
            
            # Restore from backup
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(self.db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, self.db_path)
            
            logger.log_info(f"Database restored from {backup_path}")
            return True
            
        except Exception as e:
            logger.log_error(f"Restore failed", e)
            # Try to restore safety backup
            if 'safety_backup' in locals():
                shutil.copy2(safety_backup, self.db_path)
            return False
    
    def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance"""
        results = {}
        
        with sqlite3.connect(self.db_path) as conn:
            # Get initial size
            initial_size = Path(self.db_path).stat().st_size
            
            # Run VACUUM to reclaim space
            conn.execute("VACUUM")
            
            # Analyze tables for query optimizer
            conn.execute("ANALYZE")
            
            # Get final size
            final_size = Path(self.db_path).stat().st_size
            
            # Get table statistics
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            table_stats = {}
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                table_stats[table[0]] = count
            
            results = {
                'initial_size_mb': initial_size / 1024 / 1024,
                'final_size_mb': final_size / 1024 / 1024,
                'space_saved_mb': (initial_size - final_size) / 1024 / 1024,
                'tables': table_stats,
                'optimized_at': datetime.now().isoformat()
            }
            
            logger.log_info(f"Database optimized, saved {results['space_saved_mb']:.2f} MB")
            
        return results
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {}
        
        with sqlite3.connect(self.db_path) as conn:
            # Database size
            db_size = Path(self.db_path).stat().st_size
            stats['size_mb'] = db_size / 1024 / 1024
            
            # Table counts
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            stats['tables'] = {}
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                stats['tables'][table[0]] = count
            
            # Get schema version
            try:
                version = conn.execute("PRAGMA user_version").fetchone()[0]
                stats['schema_version'] = version
            except:
                stats['schema_version'] = 0
            
            # Performance metrics
            stats['page_size'] = conn.execute("PRAGMA page_size").fetchone()[0]
            stats['cache_size'] = conn.execute("PRAGMA cache_size").fetchone()[0]
            stats['journal_mode'] = conn.execute("PRAGMA journal_mode").fetchone()[0]
            
            # Backup info
            backups = list(self.backup_dir.glob("trench_backup_*.db*"))
            stats['backup_count'] = len(backups)
            if backups:
                latest = max(backups, key=lambda p: p.stat().st_mtime)
                stats['latest_backup'] = latest.name
                stats['latest_backup_age_hours'] = (
                    datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)
                ).total_seconds() / 3600
        
        return stats
    
    def migrate_schema(self, target_version: int):
        """Run database migrations"""
        with sqlite3.connect(self.db_path) as conn:
            current_version = conn.execute("PRAGMA user_version").fetchone()[0]
            
            if current_version >= target_version:
                logger.log_info(f"Database already at version {current_version}")
                return
            
            # Run migrations
            for version in range(current_version + 1, target_version + 1):
                migration_func = getattr(self, f"_migrate_to_v{version}", None)
                if migration_func:
                    logger.log_info(f"Running migration to version {version}")
                    migration_func(conn)
                    conn.execute(f"PRAGMA user_version = {version}")
                    conn.commit()
    
    def _migrate_to_v1(self, conn: sqlite3.Connection):
        """Migration to version 1: Add historical tables"""
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS coin_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                contract_address TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                price_usd REAL,
                volume_24h REAL,
                market_cap REAL,
                liquidity REAL,
                holders INTEGER,
                price_change_24h REAL,
                data_sources TEXT,
                enrichment_score REAL,
                security_score REAL,
                UNIQUE(contract_address, timestamp)
            );
            
            CREATE TABLE IF NOT EXISTS price_history (
                contract_address TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                price REAL NOT NULL,
                volume REAL,
                source TEXT NOT NULL,
                UNIQUE(contract_address, timestamp, source)
            );
        """)
    
    def _start_backup_scheduler(self):
        """Start automatic backup scheduler"""
        def run_scheduler():
            # Schedule daily backups at 3 AM
            schedule.every().day.at("03:00").do(self.backup_database)
            
            # Schedule weekly optimization
            schedule.every().sunday.at("04:00").do(self.optimize_database)
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.log_info("Database backup scheduler started")

# Global instance
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get or create global database manager"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

# Streamlit integration
def render_database_management():
    """Render database management UI in Streamlit"""
    import streamlit as st
    
    st.header("🗄️ Database Management")
    
    manager = get_db_manager()
    stats = manager.get_database_stats()
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Database Size", f"{stats['size_mb']:.2f} MB")
    
    with col2:
        st.metric("Total Records", sum(stats['tables'].values()))
    
    with col3:
        st.metric("Backup Count", stats['backup_count'])
    
    with col4:
        if 'latest_backup_age_hours' in stats:
            st.metric("Last Backup", f"{stats['latest_backup_age_hours']:.1f}h ago")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Backup Now", type="primary"):
            try:
                backup_path = manager.backup_database()
                st.success(f"Backup created: {backup_path}")
            except Exception as e:
                st.error(f"Backup failed: {e}")
    
    with col2:
        if st.button("🔧 Optimize Database"):
            results = manager.optimize_database()
            st.success(f"Saved {results['space_saved_mb']:.2f} MB")
    
    with col3:
        if st.button("📊 Detailed Stats"):
            st.json(stats)