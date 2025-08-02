#!/usr/bin/env python3
"""
Health Check System - Comprehensive System Monitoring
Provides real-time health monitoring, alerting, and system diagnostics
"""

import time
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import logging
from pathlib import Path
import streamlit as st

class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = None
    response_time_ms: float = 0.0
    timestamp: datetime = None
    critical: bool = True
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    cache_hit_rate: float
    database_response_time: float
    api_success_rate: float
    uptime_seconds: int

class HealthChecker:
    """
    Comprehensive health checking system
    """
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.checks = {}
        self.check_history = []
        self.max_history = 1000
        self.start_time = time.time()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize default checks
        self._register_default_checks()
        
        # Background monitoring
        self.monitoring_thread = None
        self.monitoring_active = False
        
    def _register_default_checks(self):
        """Register default system health checks"""
        
        # Database connectivity
        self.register_check(
            "database_connection",
            self._check_database_connection,
            critical=True,
            description="Database connectivity and responsiveness"
        )
        
        # Database integrity
        self.register_check(
            "database_integrity",
            self._check_database_integrity,
            critical=True,
            description="Database structure and data consistency"
        )
        
        # System resources
        self.register_check(
            "system_resources",
            self._check_system_resources,
            critical=False,
            description="CPU, memory, and disk usage"
        )
        
        # Cache system
        self.register_check(
            "cache_system",
            self._check_cache_system,
            critical=False,
            description="Cache system performance"
        )
        
        # File system
        self.register_check(
            "file_system",
            self._check_file_system,
            critical=True,
            description="Required files and directories"
        )
        
        # API endpoints
        self.register_check(
            "api_endpoints",
            self._check_api_endpoints,
            critical=False,
            description="External API connectivity"
        )
        
        # Data freshness
        self.register_check(
            "data_freshness",
            self._check_data_freshness,
            critical=False,
            description="Data age and update frequency"
        )
    
    def register_check(self, 
                      name: str, 
                      check_func: Callable, 
                      critical: bool = True,
                      description: str = "",
                      interval: int = 300):
        """
        Register a health check
        
        Args:
            name: Unique name for the check
            check_func: Function that performs the check
            critical: Whether failure affects overall health
            description: Human-readable description
            interval: Check interval in seconds
        """
        self.checks[name] = {
            'func': check_func,
            'critical': critical,
            'description': description,
            'interval': interval,
            'last_run': 0,
            'consecutive_failures': 0
        }
        
        self.logger.info(f"Registered health check: {name}")
    
    def _check_database_connection(self) -> HealthCheckResult:
        """Check database connectivity"""
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # Simple query to test connectivity
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Test write capability
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            
            conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            if response_time > 1000:  # > 1 second
                status = HealthStatus.WARNING
                message = f"Database slow to respond ({response_time:.0f}ms)"
            else:
                status = HealthStatus.HEALTHY
                message = f"Database connected successfully ({response_time:.0f}ms)"
            
            return HealthCheckResult(
                name="database_connection",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "table_count": table_count,
                    "journal_mode": journal_mode,
                    "db_path": str(self.db_path)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="database_connection",
                status=HealthStatus.CRITICAL,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    def _check_database_integrity(self) -> HealthCheckResult:
        """Check database integrity and structure"""
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            # Check main table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coins'")
            coins_table = cursor.fetchone()
            
            if not coins_table:
                return HealthCheckResult(
                    name="database_integrity",
                    status=HealthStatus.CRITICAL,
                    message="Main 'coins' table not found",
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check record count
            cursor.execute("SELECT COUNT(*) FROM coins")
            total_coins = cursor.fetchone()[0]
            
            # Check for recent data
            cursor.execute("""
                SELECT COUNT(*) FROM coins 
                WHERE enrichment_timestamp > datetime('now', '-24 hours')
            """)
            recent_updates = cursor.fetchone()[0]
            
            # Check for data quality
            cursor.execute("""
                SELECT COUNT(*) FROM coins 
                WHERE current_price_usd IS NOT NULL AND current_price_usd > 0
            """)
            valid_prices = cursor.fetchone()[0]
            
            conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status
            status = HealthStatus.HEALTHY
            message = f"Database integrity verified ({total_coins:,} coins)"
            
            if total_coins == 0:
                status = HealthStatus.CRITICAL
                message = "Database is empty"
            elif recent_updates == 0:
                status = HealthStatus.WARNING
                message = f"No recent updates (24h) - {total_coins:,} total coins"
            elif valid_prices < total_coins * 0.1:  # Less than 10% have valid prices
                status = HealthStatus.WARNING
                message = f"Low data quality - only {valid_prices:,}/{total_coins:,} coins with valid prices"
            
            return HealthCheckResult(
                name="database_integrity",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "total_coins": total_coins,
                    "recent_updates": recent_updates,
                    "valid_prices": valid_prices,
                    "data_quality_pct": (valid_prices / max(total_coins, 1)) * 100
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="database_integrity",
                status=HealthStatus.CRITICAL,
                message=f"Database integrity check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    def _check_system_resources(self) -> HealthCheckResult:
        """Check system resource usage"""
        start_time = time.time()
        
        try:
            # Try to import psutil, fallback to basic checks
            try:
                import psutil
                
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                
                # Disk usage
                disk = psutil.disk_usage('/')
                
                # Process info
                process = psutil.Process()
                process_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                psutil_available = True
                
            except ImportError:
                # Fallback to basic system checks
                cpu_percent = 50.0  # Placeholder
                memory = type('Memory', (), {'percent': 50.0, 'available': 1024*1024*1024})()
                disk = type('Disk', (), {'percent': 50.0, 'free': 10*1024*1024*1024})()
                process_memory = 100.0  # Placeholder
                psutil_available = False
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status
            status = HealthStatus.HEALTHY
            warnings = []
            
            if cpu_percent > 90:
                status = HealthStatus.WARNING
                warnings.append(f"High CPU usage ({cpu_percent:.1f}%)")
            
            if memory.percent > 90:
                status = HealthStatus.WARNING
                warnings.append(f"High memory usage ({memory.percent:.1f}%)")
            
            if disk.percent > 90:
                status = HealthStatus.WARNING
                warnings.append(f"High disk usage ({disk.percent:.1f}%)")
            
            if process_memory > 1000:  # > 1GB
                warnings.append(f"Process using {process_memory:.0f}MB RAM")
            
            message = "System resources normal"
            if warnings:
                message = "; ".join(warnings)
            elif not psutil_available:
                message = "System resources check (basic mode - psutil not available)"
            
            return HealthCheckResult(
                name="system_resources",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / 1024 / 1024 / 1024,
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                    "process_memory_mb": process_memory,
                    "psutil_available": psutil_available
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="system_resources",
                status=HealthStatus.WARNING,
                message=f"Could not check system resources: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    def _check_cache_system(self) -> HealthCheckResult:
        """Check cache system performance"""
        start_time = time.time()
        
        try:
            # Try to import and check cache system
            try:
                from enhanced_caching_system import get_cache_system
                cache_system = get_cache_system()
                stats = cache_system.get_stats()
                
                hit_rate = stats.get('hit_rate', 0)
                memory_usage = stats.get('memory_size_mb', 0)
                
                status = HealthStatus.HEALTHY
                message = f"Cache system operational (hit rate: {hit_rate:.1f}%)"
                
                if hit_rate < 50:
                    status = HealthStatus.WARNING
                    message = f"Low cache hit rate ({hit_rate:.1f}%)"
                
                details = stats
                
            except ImportError:
                status = HealthStatus.WARNING
                message = "Enhanced cache system not available"
                details = {"cache_type": "streamlit_default"}
            
            return HealthCheckResult(
                name="cache_system",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                details=details
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="cache_system",
                status=HealthStatus.WARNING,
                message=f"Cache check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    def _check_file_system(self) -> HealthCheckResult:
        """Check required files and directories"""
        start_time = time.time()
        
        try:
            required_paths = [
                "data/",
                "data/trench.db",
                "streamlit_app.py",
                "requirements.txt"
            ]
            
            missing_paths = []
            existing_paths = []
            
            for path_str in required_paths:
                path = Path(path_str)
                if path.exists():
                    existing_paths.append(path_str)
                else:
                    missing_paths.append(path_str)
            
            # Check permissions
            data_dir = Path("data")
            writable = data_dir.is_dir() and data_dir.stat().st_mode & 0o200
            
            status = HealthStatus.HEALTHY
            message = f"File system check passed ({len(existing_paths)}/{len(required_paths)} files found)"
            
            if missing_paths:
                if any(path in ["data/", "data/trench.db"] for path in missing_paths):
                    status = HealthStatus.CRITICAL
                else:
                    status = HealthStatus.WARNING
                message = f"Missing files: {', '.join(missing_paths)}"
            
            if not writable:
                status = HealthStatus.WARNING
                message += " (data directory not writable)"
            
            return HealthCheckResult(
                name="file_system",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                details={
                    "existing_paths": existing_paths,
                    "missing_paths": missing_paths,
                    "data_dir_writable": writable
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="file_system",
                status=HealthStatus.WARNING,
                message=f"File system check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    def _check_api_endpoints(self) -> HealthCheckResult:
        """Check external API connectivity"""
        start_time = time.time()
        
        test_endpoints = [
            {"name": "DexScreener", "url": "https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112"},
            {"name": "Jupiter", "url": "https://price.jup.ag/v4/price?ids=SOL"},
        ]
        
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for endpoint in test_endpoints:
            try:
                response = requests.get(endpoint["url"], timeout=5)
                
                if response.status_code == 200:
                    results.append({
                        "name": endpoint["name"],
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds() * 1000
                    })
                else:
                    results.append({
                        "name": endpoint["name"],
                        "status": "error",
                        "status_code": response.status_code
                    })
                    overall_status = HealthStatus.WARNING
                    
            except Exception as e:
                results.append({
                    "name": endpoint["name"],
                    "status": "failed",
                    "error": str(e)
                })
                overall_status = HealthStatus.WARNING
        
        healthy_count = sum(1 for r in results if r["status"] == "healthy")
        message = f"API connectivity: {healthy_count}/{len(test_endpoints)} endpoints healthy"
        
        return HealthCheckResult(
            name="api_endpoints",
            status=overall_status,
            message=message,
            response_time_ms=(time.time() - start_time) * 1000,
            details={"endpoints": results}
        )
    
    def _check_data_freshness(self) -> HealthCheckResult:
        """Check data freshness and update frequency"""
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # Check most recent enrichment
            cursor.execute("""
                SELECT MAX(enrichment_timestamp) as latest,
                       COUNT(*) as total_enriched
                FROM coins 
                WHERE enrichment_timestamp IS NOT NULL
            """)
            result = cursor.fetchone()
            
            if result and result[0]:
                latest_str = result[0]
                total_enriched = result[1]
                
                # Parse timestamp
                latest = datetime.fromisoformat(latest_str.replace('Z', '+00:00'))
                age_minutes = (datetime.now() - latest.replace(tzinfo=None)).total_seconds() / 60
                
                status = HealthStatus.HEALTHY
                message = f"Data is fresh (latest update {age_minutes:.0f} minutes ago)"
                
                if age_minutes > 60:  # > 1 hour
                    status = HealthStatus.WARNING
                    message = f"Data getting stale ({age_minutes:.0f} minutes old)"
                
                if age_minutes > 1440:  # > 24 hours
                    status = HealthStatus.CRITICAL
                    message = f"Data very stale ({age_minutes/60:.1f} hours old)"
                
                details = {
                    "latest_update": latest_str,
                    "age_minutes": age_minutes,
                    "total_enriched": total_enriched
                }
                
            else:
                status = HealthStatus.CRITICAL
                message = "No enriched data found"
                details = {"total_enriched": 0}
            
            conn.close()
            
            return HealthCheckResult(
                name="data_freshness",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                details=details
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="data_freshness",
                status=HealthStatus.WARNING,
                message=f"Data freshness check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                details={"error": str(e)}
            )
    
    def run_check(self, check_name: str) -> HealthCheckResult:
        """Run a specific health check"""
        if check_name not in self.checks:
            return HealthCheckResult(
                name=check_name,
                status=HealthStatus.UNKNOWN,
                message=f"Check '{check_name}' not found"
            )
        
        check_config = self.checks[check_name]
        
        try:
            result = check_config['func']()
            result.critical = check_config['critical']
            
            # Update last run time
            check_config['last_run'] = time.time()
            
            # Track consecutive failures
            if result.status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
                check_config['consecutive_failures'] += 1
            else:
                check_config['consecutive_failures'] = 0
            
            # Add to history
            self.check_history.append(result)
            if len(self.check_history) > self.max_history:
                self.check_history.pop(0)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Health check '{check_name}' failed: {e}")
            
            check_config['consecutive_failures'] += 1
            
            return HealthCheckResult(
                name=check_name,
                status=HealthStatus.CRITICAL,
                message=f"Check execution failed: {str(e)}",
                critical=check_config['critical'],
                details={"error": str(e)}
            )
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks"""
        results = {}
        
        for check_name in self.checks:
            results[check_name] = self.run_check(check_name)
        
        return results
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        results = self.run_all_checks()
        
        # Determine overall status
        critical_failures = []
        warnings = []
        healthy = []
        
        for name, result in results.items():
            if result.status == HealthStatus.CRITICAL and result.critical:
                critical_failures.append(name)
            elif result.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
                warnings.append(name)
            else:
                healthy.append(name)
        
        if critical_failures:
            overall_status = HealthStatus.CRITICAL
            status_message = f"Critical issues: {', '.join(critical_failures)}"
        elif warnings:
            overall_status = HealthStatus.WARNING
            status_message = f"Warnings: {', '.join(warnings)}"
        else:
            overall_status = HealthStatus.HEALTHY
            status_message = "All systems operational"
        
        # Calculate uptime
        uptime_seconds = int(time.time() - self.start_time)
        
        return {
            "overall_status": overall_status.value,
            "status_message": status_message,
            "uptime_seconds": uptime_seconds,
            "checks_total": len(results),
            "checks_healthy": len(healthy),
            "checks_warning": len(warnings),
            "checks_critical": len(critical_failures),
            "timestamp": datetime.now().isoformat(),
            "individual_checks": {name: asdict(result) for name, result in results.items()}
        }
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # System resources
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
            except ImportError:
                cpu_percent = 50.0
                memory_percent = 50.0
                disk_percent = 50.0
            
            # Database metrics
            try:
                conn = sqlite3.connect(self.db_path, timeout=1.0)
                start_time = time.time()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM coins LIMIT 1")
                cursor.fetchone()
                db_response_time = (time.time() - start_time) * 1000
                conn.close()
            except:
                db_response_time = -1
            
            # Cache metrics
            try:
                from enhanced_caching_system import get_cache_system
                cache_stats = get_cache_system().get_stats()
                cache_hit_rate = cache_stats.get('hit_rate', 0)
            except:
                cache_hit_rate = 0
            
            # Connection pool metrics
            try:
                from database_connection_pool import get_database_pool
                pool_stats = get_database_pool().get_stats()
                active_connections = pool_stats.get('active_connections', 0)
            except:
                active_connections = 1
            
            uptime_seconds = int(time.time() - self.start_time)
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                active_connections=active_connections,
                cache_hit_rate=cache_hit_rate,
                database_response_time=db_response_time,
                api_success_rate=95.0,  # Placeholder
                uptime_seconds=uptime_seconds
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0, memory_percent=0, disk_percent=0,
                active_connections=0, cache_hit_rate=0,
                database_response_time=-1, api_success_rate=0,
                uptime_seconds=0
            )
    
    def start_monitoring(self, interval: int = 60):
        """Start background health monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    # Run checks that are due
                    current_time = time.time()
                    
                    for check_name, check_config in self.checks.items():
                        if current_time - check_config['last_run'] >= check_config['interval']:
                            result = self.run_check(check_name)
                            
                            # Log critical issues
                            if result.status == HealthStatus.CRITICAL and result.critical:
                                self.logger.error(f"CRITICAL: {check_name} - {result.message}")
                            elif result.status == HealthStatus.WARNING:
                                self.logger.warning(f"WARNING: {check_name} - {result.message}")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    self.logger.error(f"Monitoring loop error: {e}")
                    time.sleep(interval)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop background health monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Health monitoring stopped")
    
    def render_health_dashboard(self):
        """Render health check dashboard in Streamlit"""
        st.subheader("🏥 System Health Dashboard")
        
        # Get overall health
        health_data = self.get_overall_health()
        overall_status = health_data['overall_status']
        
        # Status indicator
        if overall_status == 'healthy':
            st.success(f"✅ {health_data['status_message']}")
        elif overall_status == 'warning':
            st.warning(f"⚠️ {health_data['status_message']}")
        else:
            st.error(f"❌ {health_data['status_message']}")
        
        # System metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            uptime_hours = health_data['uptime_seconds'] / 3600
            st.metric("Uptime", f"{uptime_hours:.1f}h")
        
        with col2:
            st.metric("Healthy Checks", f"{health_data['checks_healthy']}/{health_data['checks_total']}")
        
        with col3:
            st.metric("Warnings", health_data['checks_warning'])
        
        with col4:
            st.metric("Critical", health_data['checks_critical'])
        
        # Individual checks
        st.markdown("---")
        st.subheader("📋 Individual Health Checks")
        
        for check_name, check_data in health_data['individual_checks'].items():
            status = check_data['status']
            message = check_data['message']
            response_time = check_data.get('response_time_ms', 0)
            
            with st.expander(f"{'✅' if status == 'healthy' else '⚠️' if status == 'warning' else '❌'} {check_name.replace('_', ' ').title()}"):
                st.write(f"**Status:** {status.upper()}")
                st.write(f"**Message:** {message}")
                st.write(f"**Response Time:** {response_time:.1f}ms")
                
                if check_data.get('details'):
                    st.write("**Details:**")
                    st.json(check_data['details'])
        
        # System metrics chart
        if st.button("🔄 Refresh Health Checks"):
            st.rerun()

# Global health checker instance
_health_checker = None

def get_health_checker() -> HealthChecker:
    """Get or create the global health checker"""
    global _health_checker
    
    if _health_checker is None:
        _health_checker = HealthChecker()
    
    return _health_checker