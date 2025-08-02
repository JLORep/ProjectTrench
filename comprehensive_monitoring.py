#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrenchCoat Pro Comprehensive Monitoring System
Real-time system monitoring, performance tracking, and health checks
"""

import streamlit as st
import psutil
import time
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import subprocess
import os
import sys
import threading
from typing import Dict, List, Any, Optional
import sqlite3
import requests

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass

class SystemMonitor:
    """Comprehensive system monitoring and health checks"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.db_path = self.project_root / "data" / "trench.db"
        self.metrics_file = self.project_root / "monitoring_metrics.json"
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage(str(self.project_root))
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            except:
                network_stats = None
            
            # Process metrics for current Python process
            process = psutil.Process()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': network_stats,
                'process': {
                    'memory_info': process.memory_info()._asdict(),
                    'cpu_percent': process.cpu_percent(),
                    'num_threads': process.num_threads(),
                    'connections': len(process.connections()) if hasattr(process, 'connections') else 0
                }
            }
        except Exception as e:
            return {'error': f"Failed to get system metrics: {e}"}
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'database_accessible': False,
            'total_coins': 0,
            'enriched_coins': 0,
            'recent_activity': False,
            'database_size': 0,
            'query_performance': {}
        }
        
        try:
            if self.db_path.exists():
                # Get database size
                health_status['database_size'] = self.db_path.stat().st_size
                
                # Connect and test queries
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Test basic connectivity
                start_time = time.time()
                cursor.execute("SELECT COUNT(*) FROM coins")
                total_coins = cursor.fetchone()[0]
                query_time = time.time() - start_time
                
                health_status['database_accessible'] = True
                health_status['total_coins'] = total_coins
                health_status['query_performance']['count_query'] = query_time
                
                # Check enriched coins
                try:
                    start_time = time.time()
                    cursor.execute("SELECT COUNT(*) FROM coins WHERE market_cap > 0")
                    enriched_coins = cursor.fetchone()[0]
                    query_time = time.time() - start_time
                    
                    health_status['enriched_coins'] = enriched_coins
                    health_status['query_performance']['enriched_query'] = query_time
                except:
                    pass
                
                # Check for recent activity (if there's a timestamp column)
                try:
                    cursor.execute("SELECT MAX(created_at) FROM coins")
                    last_activity = cursor.fetchone()[0]
                    if last_activity:
                        health_status['recent_activity'] = True
                        health_status['last_activity'] = last_activity
                except:
                    pass
                
                conn.close()
                
        except Exception as e:
            health_status['error'] = str(e)
        
        return health_status
    
    def check_api_endpoints(self) -> Dict[str, Any]:
        """Check external API endpoint health"""
        endpoints = {
            'coingecko': 'https://api.coingecko.com/api/v3/ping',
            'dexscreener': 'https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112',
            'birdeye': 'https://public-api.birdeye.so/public/tokenlist',
        }
        
        results = {}
        
        for name, url in endpoints.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = time.time() - start_time
                
                results[name] = {
                    'status': 'healthy' if response.status_code == 200 else 'degraded',
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                results[name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get git repository status"""
        try:
            # Git status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            status = {
                'clean': result.returncode == 0 and not result.stdout.strip(),
                'uncommitted_changes': bool(result.stdout.strip()),
                'files_changed': len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            }
            
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True, cwd=self.project_root
            )
            status['current_branch'] = branch_result.stdout.strip()
            
            # Get last commit
            commit_result = subprocess.run(
                ['git', 'log', '-1', '--oneline'],
                capture_output=True, text=True, cwd=self.project_root
            )
            status['last_commit'] = commit_result.stdout.strip()
            
            return status
            
        except Exception as e:
            return {'error': f"Git status check failed: {e}"}

def render_monitoring_dashboard():
    """Main function to render monitoring dashboard"""
    st.header("📊 Comprehensive System Monitoring")
    st.subheader("Real-time performance tracking and health monitoring")
    
    # Initialize monitor
    monitor = SystemMonitor()
    
    # Auto-refresh toggle
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🎯 System Health Overview")
    
    with col2:
        auto_refresh = st.checkbox("🔄 Auto Refresh (30s)", value=True)
    
    with col3:
        if st.button("🔄 Refresh Now", type="primary"):
            st.rerun()
    
    # Get current metrics
    current_metrics = monitor.get_system_metrics()
    db_health = monitor.check_database_health()
    api_health = monitor.check_api_endpoints()
    git_status = monitor.get_git_status()
    
    # System status overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # System health
        if 'error' not in current_metrics:
            cpu_percent = current_metrics.get('cpu', {}).get('percent', 0)
            if cpu_percent < 70:
                st.success(f"💻 **SYSTEM OK**\nCPU: {cpu_percent:.1f}%")
            elif cpu_percent < 90:
                st.warning(f"⚠️ **SYSTEM BUSY**\nCPU: {cpu_percent:.1f}%")
            else:
                st.error(f"🔥 **SYSTEM STRESSED**\nCPU: {cpu_percent:.1f}%")
        else:
            st.error("❌ **SYSTEM ERROR**")
    
    with col2:
        # Database health
        if db_health.get('database_accessible'):
            total_coins = db_health.get('total_coins', 0)
            enriched_coins = db_health.get('enriched_coins', 0)
            enrichment_rate = (enriched_coins / total_coins * 100) if total_coins > 0 else 0
            st.success(f"🗄️ **DATABASE OK**\n{total_coins} coins ({enrichment_rate:.1f}% enriched)")
        else:
            st.error("❌ **DATABASE ERROR**")
    
    with col3:
        # API health
        healthy_apis = sum(1 for api_status in api_health.values() 
                         if api_status.get('status') == 'healthy')
        total_apis = len(api_health)
        
        if healthy_apis == total_apis:
            st.success(f"🌐 **APIS OK**\n{healthy_apis}/{total_apis} healthy")
        elif healthy_apis > total_apis // 2:
            st.warning(f"⚠️ **APIS DEGRADED**\n{healthy_apis}/{total_apis} healthy")
        else:
            st.error(f"❌ **APIS DOWN**\n{healthy_apis}/{total_apis} healthy")
    
    with col4:
        # Git status
        if 'error' not in git_status:
            if git_status.get('clean', False):
                st.success("📝 **GIT CLEAN**\nNo uncommitted changes")
            else:
                changes = git_status.get('files_changed', 0)
                st.info(f"📝 **GIT ACTIVE**\n{changes} files changed")
        else:
            st.error("❌ **GIT ERROR**")
    
    # Create monitoring tabs
    tab1, tab2, tab3 = st.tabs([
        "💻 System Performance",
        "🗄️ Database Health", 
        "🌐 API Monitoring"
    ])
    
    with tab1:
        # System Performance
        if 'error' not in current_metrics:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🖥️ CPU Performance")
                cpu_data = current_metrics.get('cpu', {})
                
                st.metric("CPU Usage", f"{cpu_data.get('percent', 0):.1f}%")
                st.metric("CPU Cores", cpu_data.get('count', 'Unknown'))
                if cpu_data.get('frequency'):
                    st.metric("CPU Frequency", f"{cpu_data.get('frequency', 0):.0f} MHz")
            
            with col2:
                st.markdown("#### 💾 Memory Performance")
                memory_data = current_metrics.get('memory', {})
                
                total_gb = memory_data.get('total', 0) / (1024**3)
                used_gb = memory_data.get('used', 0) / (1024**3)
                available_gb = memory_data.get('available', 0) / (1024**3)
                
                st.metric("Memory Usage", f"{memory_data.get('percent', 0):.1f}%")
                st.metric("Total Memory", f"{total_gb:.1f} GB")
                st.metric("Available Memory", f"{available_gb:.1f} GB")
        else:
            st.error(f"Error getting system metrics: {current_metrics['error']}")
    
    with tab2:
        # Database Health
        if db_health.get('database_accessible', False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_coins = db_health.get('total_coins', 0)
                st.metric("Total Coins", total_coins)
            
            with col2:
                enriched_coins = db_health.get('enriched_coins', 0)
                st.metric("Enriched Coins", enriched_coins)
            
            with col3:
                db_size_mb = db_health.get('database_size', 0) / (1024**2)
                st.metric("Database Size", f"{db_size_mb:.1f} MB")
            
            # Enrichment progress
            if total_coins > 0:
                enrichment_rate = (enriched_coins / total_coins) * 100
                
                st.markdown("#### 📊 Enrichment Progress")
                progress_bar = st.progress(enrichment_rate / 100)
                st.write(f"**{enrichment_rate:.1f}%** of coins are enriched ({enriched_coins:,} / {total_coins:,})")
        else:
            st.error("❌ Database is not accessible!")
            if 'error' in db_health:
                st.error(f"Error: {db_health['error']}")
    
    with tab3:
        # API Monitoring
        if api_health:
            # API status overview
            api_data = []
            for name, status in api_health.items():
                api_data.append({
                    'API': name.title(),
                    'Status': status.get('status', 'unknown').title(),
                    'Response Time': f"{status.get('response_time', 0)*1000:.0f}ms" if 'response_time' in status else 'N/A',
                    'Status Code': status.get('status_code', 'N/A'),
                    'Last Check': status.get('timestamp', 'Unknown')
                })
            
            df = pd.DataFrame(api_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No API endpoints configured for monitoring")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(1)  # Small delay to prevent excessive refreshing
        st.rerun()

if __name__ == "__main__":
    render_monitoring_dashboard()