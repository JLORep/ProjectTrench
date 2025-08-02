"""
📊 TrenchCoat Pro - Monitoring & Logging System
Comprehensive error tracking and performance monitoring
"""

import logging
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import wraps
import pandas as pd
from dataclasses import dataclass, asdict
import streamlit as st

# Create logs directory
Path("logs").mkdir(exist_ok=True)

@dataclass
class MetricEvent:
    """Performance metric event"""
    timestamp: float
    name: str
    value: float
    tags: Dict[str, str]
    
class TrenchCoatLogger:
    """Advanced logging system with error tracking"""
    
    def __init__(self, name: str = "TrenchCoat"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console.setFormatter(console_format)
        
        # File handler for errors
        error_file = logging.FileHandler('logs/errors.log')
        error_file.setLevel(logging.ERROR)
        error_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        error_file.setFormatter(error_format)
        
        # File handler for all logs
        all_file = logging.FileHandler('logs/app.log')
        all_file.setLevel(logging.DEBUG)
        all_file.setFormatter(error_format)
        
        self.logger.addHandler(console)
        self.logger.addHandler(error_file)
        self.logger.addHandler(all_file)
        
        # Error tracking
        self.error_counts = {}
        self.last_errors = []
        
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with context"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Track error frequency
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Store last 100 errors
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_msg,
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.last_errors.append(error_info)
        if len(self.last_errors) > 100:
            self.last_errors.pop(0)
        
        # Log to file
        self.logger.error(f"{error_type}: {error_msg}", extra={'context': context})
        
        # Save error details
        with open('logs/error_details.json', 'w') as f:
            json.dump(self.last_errors, f, indent=2)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_types': self.error_counts,
            'recent_errors': self.last_errors[-10:]
        }

class PerformanceMonitor:
    """Performance monitoring system"""
    
    def __init__(self):
        self.metrics = []
        self.timers = {}
        
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance metric"""
        metric = MetricEvent(
            timestamp=time.time(),
            name=name,
            value=value,
            tags=tags or {}
        )
        self.metrics.append(metric)
        
        # Keep only last 1000 metrics
        if len(self.metrics) > 1000:
            self.metrics.pop(0)
    
    def start_timer(self, name: str):
        """Start a performance timer"""
        self.timers[name] = time.time()
    
    def stop_timer(self, name: str, tags: Dict[str, str] = None):
        """Stop a timer and record the duration"""
        if name in self.timers:
            duration = time.time() - self.timers[name]
            self.record_metric(f"{name}_duration", duration, tags)
            del self.timers[name]
            return duration
        return None
    
    def get_metrics_summary(self) -> pd.DataFrame:
        """Get metrics as DataFrame"""
        if not self.metrics:
            return pd.DataFrame()
        
        data = []
        for metric in self.metrics:
            row = asdict(metric)
            row['datetime'] = datetime.fromtimestamp(metric.timestamp)
            data.append(row)
        
        return pd.DataFrame(data)
    
    @contextmanager
    def timer(self, name: str, tags: Dict[str, str] = None):
        """Context manager for timing operations"""
        start = time.time()
        yield
        duration = time.time() - start
        self.record_metric(f"{name}_duration", duration, tags)

# Global instances
logger = TrenchCoatLogger()
monitor = PerformanceMonitor()

# Decorators
def log_errors(func):
    """Decorator to log function errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.log_error(e, {
                'function': func.__name__,
                'args': str(args)[:100],
                'kwargs': str(kwargs)[:100]
            })
            raise
    return wrapper

def monitor_performance(name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metric_name = name or func.__name__
            monitor.start_timer(metric_name)
            try:
                result = func(*args, **kwargs)
                monitor.stop_timer(metric_name, {'status': 'success'})
                return result
            except Exception as e:
                monitor.stop_timer(metric_name, {'status': 'error', 'error': str(e)})
                raise
        return wrapper
    return decorator

def create_monitoring_dashboard():
    """Create monitoring dashboard in Streamlit"""
    st.header("📊 System Monitoring")
    
    # Error summary
    error_summary = logger.get_error_summary()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Errors", error_summary['total_errors'])
    with col2:
        st.metric("Error Types", len(error_summary['error_types']))
    with col3:
        st.metric("Recent Errors", len(error_summary['recent_errors']))
    
    # Performance metrics
    metrics_df = monitor.get_metrics_summary()
    if not metrics_df.empty:
        st.subheader("Performance Metrics")
        
        # Average response times
        avg_times = metrics_df.groupby('name')['value'].agg(['mean', 'count'])
        st.dataframe(avg_times)
        
        # Time series chart
        if st.checkbox("Show performance timeline"):
            st.line_chart(metrics_df.set_index('datetime')['value'])
    
    # Recent errors
    if error_summary['recent_errors']:
        st.subheader("Recent Errors")
        for error in error_summary['recent_errors'][-5:]:
            with st.expander(f"{error['type']} - {error['timestamp']}"):
                st.text(error['message'])
                st.code(error['traceback'])

# Export convenience functions
def log_info(message: str):
    logger.logger.info(message)

def log_warning(message: str):
    logger.logger.warning(message)

def log_error(message: str, error: Exception = None):
    if error:
        logger.log_error(error, {'message': message})
    else:
        logger.logger.error(message)