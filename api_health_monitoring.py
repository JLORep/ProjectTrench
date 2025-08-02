#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Health Monitoring System
Real-time monitoring and alerting for 100+ API providers
Created: 2025-08-02
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
import statistics
from enum import Enum
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class HealthStatus(Enum):
    """API health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

@dataclass
class HealthMetric:
    """Single health metric measurement"""
    timestamp: datetime
    response_time_ms: float
    status_code: int
    success: bool
    error_message: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None

@dataclass 
class APIHealthStatus:
    """Current health status for an API"""
    provider: str
    status: HealthStatus
    uptime_percentage: float
    avg_response_time_ms: float
    error_rate: float
    last_check: datetime
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    rate_limit_status: Dict[str, Any] = field(default_factory=dict)
    recent_metrics: deque = field(default_factory=lambda: deque(maxlen=100))

@dataclass
class HealthAlert:
    """Health alert for monitoring"""
    provider: str
    severity: str  # critical, warning, info
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class APIHealthMonitor:
    """
    Monitors health of all API providers
    """
    
    def __init__(self, check_interval: int = 300):  # 5 minutes default
        self.check_interval = check_interval
        self.health_status: Dict[str, APIHealthStatus] = {}
        self.alerts: List[HealthAlert] = []
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.alert_callbacks: List[callable] = []
        
        # Thresholds
        self.thresholds = {
            'response_time_warning': 1000,  # ms
            'response_time_critical': 3000,  # ms
            'error_rate_warning': 0.05,  # 5%
            'error_rate_critical': 0.20,  # 20%
            'uptime_warning': 0.95,  # 95%
            'uptime_critical': 0.90,  # 90%
            'consecutive_failures_warning': 3,
            'consecutive_failures_critical': 5
        }
        
        # Historical data for analysis
        self.historical_data: Dict[str, List[HealthMetric]] = defaultdict(list)
        
    async def start_monitoring(self, providers: List[str]):
        """Start monitoring specified providers"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        for provider in providers:
            if provider not in self.monitoring_tasks:
                task = asyncio.create_task(self._monitor_provider(provider))
                self.monitoring_tasks[provider] = task
                
                # Initialize health status
                self.health_status[provider] = APIHealthStatus(
                    provider=provider,
                    status=HealthStatus.UNKNOWN,
                    uptime_percentage=100.0,
                    avg_response_time_ms=0.0,
                    error_rate=0.0,
                    last_check=datetime.utcnow()
                )
    
    async def stop_monitoring(self, providers: Optional[List[str]] = None):
        """Stop monitoring specified providers or all"""
        providers_to_stop = providers or list(self.monitoring_tasks.keys())
        
        for provider in providers_to_stop:
            if provider in self.monitoring_tasks:
                self.monitoring_tasks[provider].cancel()
                del self.monitoring_tasks[provider]
        
        if not self.monitoring_tasks and self.session:
            await self.session.close()
            self.session = None
    
    async def _monitor_provider(self, provider: str):
        """Monitor a single provider continuously"""
        while True:
            try:
                # Perform health check
                metric = await self._check_provider_health(provider)
                
                # Update health status
                self._update_health_status(provider, metric)
                
                # Store historical data
                self.historical_data[provider].append(metric)
                
                # Trim historical data to last 24 hours
                cutoff = datetime.utcnow() - timedelta(hours=24)
                self.historical_data[provider] = [
                    m for m in self.historical_data[provider]
                    if m.timestamp > cutoff
                ]
                
                # Check for alerts
                await self._check_alerts(provider)
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error monitoring {provider}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _check_provider_health(self, provider: str) -> HealthMetric:
        """Perform health check for a provider"""
        # Get endpoint configuration
        endpoint = self._get_health_endpoint(provider)
        
        start_time = datetime.utcnow()
        try:
            async with self.session.get(
                endpoint['url'],
                headers=endpoint.get('headers', {}),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Extract rate limit info if available
                rate_limit_remaining = None
                rate_limit_reset = None
                
                if 'x-ratelimit-remaining' in response.headers:
                    rate_limit_remaining = int(response.headers['x-ratelimit-remaining'])
                if 'x-ratelimit-reset' in response.headers:
                    rate_limit_reset = datetime.fromtimestamp(
                        int(response.headers['x-ratelimit-reset'])
                    )
                
                return HealthMetric(
                    timestamp=start_time,
                    response_time_ms=response_time,
                    status_code=response.status,
                    success=response.status < 400,
                    error_message=None if response.status < 400 else f"HTTP {response.status}",
                    rate_limit_remaining=rate_limit_remaining,
                    rate_limit_reset=rate_limit_reset
                )
                
        except asyncio.TimeoutError:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthMetric(
                timestamp=start_time,
                response_time_ms=response_time,
                status_code=0,
                success=False,
                error_message="Timeout"
            )
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return HealthMetric(
                timestamp=start_time,
                response_time_ms=response_time,
                status_code=0,
                success=False,
                error_message=str(e)
            )
    
    def _get_health_endpoint(self, provider: str) -> Dict[str, Any]:
        """Get health check endpoint for provider"""
        endpoints = {
            'coingecko': {
                'url': 'https://api.coingecko.com/api/v3/ping',
                'headers': {}
            },
            'coinmarketcap': {
                'url': 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?limit=1',
                'headers': {}  # Credential manager will add auth
            },
            'dexscreener': {
                'url': 'https://api.dexscreener.com/latest/dex/search?q=test',
                'headers': {}
            },
            'jupiter': {
                'url': 'https://quote-api.jup.ag/v6/tokens',
                'headers': {}
            },
            'etherscan': {
                'url': 'https://api.etherscan.io/api?module=stats&action=ethsupply',
                'headers': {}
            },
            'moralis': {
                'url': 'https://deep-index.moralis.io/api/v2/info',
                'headers': {}
            },
            'birdeye': {
                'url': 'https://public-api.birdeye.so/public/price?address=So11111111111111111111111111111111111111112',
                'headers': {}
            },
            'solscan': {
                'url': 'https://public-api.solscan.io/chaininfo',
                'headers': {}
            }
        }
        
        # Default endpoint for unknown providers
        default = {
            'url': f'https://api.{provider}.com/health',
            'headers': {}
        }
        
        return endpoints.get(provider, default)
    
    def _update_health_status(self, provider: str, metric: HealthMetric):
        """Update health status based on new metric"""
        status = self.health_status[provider]
        
        # Add to recent metrics
        status.recent_metrics.append(metric)
        status.last_check = metric.timestamp
        
        # Update consecutive failures
        if metric.success:
            status.consecutive_failures = 0
        else:
            status.consecutive_failures += 1
            status.last_error = metric.error_message
        
        # Calculate metrics from recent data
        recent_list = list(status.recent_metrics)
        if recent_list:
            # Response time
            response_times = [m.response_time_ms for m in recent_list]
            status.avg_response_time_ms = statistics.mean(response_times)
            
            # Error rate
            failures = sum(1 for m in recent_list if not m.success)
            status.error_rate = failures / len(recent_list)
            
            # Uptime (from last 100 checks)
            status.uptime_percentage = (len(recent_list) - failures) / len(recent_list)
        
        # Update rate limit status
        if metric.rate_limit_remaining is not None:
            status.rate_limit_status = {
                'remaining': metric.rate_limit_remaining,
                'reset': metric.rate_limit_reset,
                'percentage': metric.rate_limit_remaining / 100  # Assume 100 is max
            }
        
        # Determine overall status
        status.status = self._calculate_health_status(status)
    
    def _calculate_health_status(self, status: APIHealthStatus) -> HealthStatus:
        """Calculate overall health status from metrics"""
        if status.consecutive_failures >= self.thresholds['consecutive_failures_critical']:
            return HealthStatus.OFFLINE
        
        issues = 0
        
        # Check response time
        if status.avg_response_time_ms > self.thresholds['response_time_critical']:
            issues += 2
        elif status.avg_response_time_ms > self.thresholds['response_time_warning']:
            issues += 1
        
        # Check error rate
        if status.error_rate > self.thresholds['error_rate_critical']:
            issues += 2
        elif status.error_rate > self.thresholds['error_rate_warning']:
            issues += 1
        
        # Check uptime
        if status.uptime_percentage < self.thresholds['uptime_critical']:
            issues += 2
        elif status.uptime_percentage < self.thresholds['uptime_warning']:
            issues += 1
        
        # Determine status
        if issues >= 3:
            return HealthStatus.UNHEALTHY
        elif issues >= 1:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    async def _check_alerts(self, provider: str):
        """Check if alerts need to be triggered"""
        status = self.health_status[provider]
        
        # Check for critical alerts
        if status.status == HealthStatus.OFFLINE:
            await self._create_alert(
                provider, 
                "critical",
                f"{provider} is OFFLINE - {status.consecutive_failures} consecutive failures"
            )
        elif status.status == HealthStatus.UNHEALTHY:
            await self._create_alert(
                provider,
                "warning", 
                f"{provider} is UNHEALTHY - Response time: {status.avg_response_time_ms:.0f}ms, Error rate: {status.error_rate:.1%}"
            )
        
        # Check rate limiting
        if status.rate_limit_status.get('remaining', 100) < 10:
            await self._create_alert(
                provider,
                "warning",
                f"{provider} approaching rate limit - {status.rate_limit_status['remaining']} requests remaining"
            )
    
    async def _create_alert(self, provider: str, severity: str, message: str):
        """Create and dispatch alert"""
        # Check if similar alert already exists
        existing = next(
            (a for a in self.alerts 
             if a.provider == provider and a.message == message and not a.resolved),
            None
        )
        
        if existing:
            return  # Don't create duplicate
        
        alert = HealthAlert(
            provider=provider,
            severity=severity,
            message=message,
            timestamp=datetime.utcnow()
        )
        
        self.alerts.append(alert)
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                print(f"Error in alert callback: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display"""
        return {
            'overall_health': self._calculate_overall_health(),
            'provider_status': {
                provider: {
                    'status': status.status.value,
                    'uptime': status.uptime_percentage,
                    'response_time': status.avg_response_time_ms,
                    'error_rate': status.error_rate,
                    'last_check': status.last_check.isoformat(),
                    'rate_limit': status.rate_limit_status
                }
                for provider, status in self.health_status.items()
            },
            'recent_alerts': [
                asdict(alert) for alert in self.alerts[-20:]  # Last 20 alerts
            ],
            'metrics_summary': self._get_metrics_summary()
        }
    
    def _calculate_overall_health(self) -> Dict[str, Any]:
        """Calculate overall system health"""
        if not self.health_status:
            return {'status': 'unknown', 'score': 0}
        
        statuses = [s.status for s in self.health_status.values()]
        
        # Count by status
        status_counts = {
            'healthy': sum(1 for s in statuses if s == HealthStatus.HEALTHY),
            'degraded': sum(1 for s in statuses if s == HealthStatus.DEGRADED),
            'unhealthy': sum(1 for s in statuses if s == HealthStatus.UNHEALTHY),
            'offline': sum(1 for s in statuses if s == HealthStatus.OFFLINE)
        }
        
        # Calculate score (0-100)
        total = len(statuses)
        score = (
            status_counts['healthy'] * 100 +
            status_counts['degraded'] * 70 +
            status_counts['unhealthy'] * 30
        ) / total
        
        # Overall status
        if status_counts['offline'] > total * 0.2:
            overall_status = 'critical'
        elif status_counts['unhealthy'] > total * 0.3:
            overall_status = 'warning'
        elif status_counts['degraded'] > total * 0.5:
            overall_status = 'attention'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'score': round(score, 1),
            'counts': status_counts
        }
    
    def _get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary metrics across all providers"""
        if not self.health_status:
            return {}
        
        response_times = [
            s.avg_response_time_ms 
            for s in self.health_status.values()
            if s.avg_response_time_ms > 0
        ]
        
        error_rates = [
            s.error_rate 
            for s in self.health_status.values()
        ]
        
        return {
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'avg_error_rate': statistics.mean(error_rates) if error_rates else 0,
            'providers_monitored': len(self.health_status),
            'active_alerts': sum(1 for a in self.alerts if not a.resolved)
        }


def render_health_monitoring_dashboard(monitor: APIHealthMonitor):
    """Render Streamlit dashboard for API health monitoring"""
    st.header("🏥 API Health Monitoring Dashboard")
    
    # Get dashboard data
    data = monitor.get_dashboard_data()
    
    # Overall health status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        health = data['overall_health']
        color = {
            'healthy': '#10b981',
            'attention': '#f59e0b',
            'warning': '#ef4444',
            'critical': '#991b1b'
        }.get(health['status'], '#6b7280')
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: {color}; border-radius: 10px;">
            <h3 style="margin: 0; color: white;">Overall Health</h3>
            <h1 style="margin: 10px 0; color: white;">{health['score']:.1f}%</h1>
            <p style="margin: 0; color: white;">{health['status'].upper()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric(
            "Providers Monitored",
            data['metrics_summary'].get('providers_monitored', 0),
            help="Total number of API providers being monitored"
        )
    
    with col3:
        st.metric(
            "Avg Response Time",
            f"{data['metrics_summary'].get('avg_response_time', 0):.0f}ms",
            help="Average response time across all providers"
        )
    
    with col4:
        st.metric(
            "Active Alerts",
            data['metrics_summary'].get('active_alerts', 0),
            help="Number of unresolved alerts"
        )
    
    # Provider status grid
    st.subheader("📊 Provider Status")
    
    # Create provider cards
    providers = list(data['provider_status'].keys())
    if providers:
        # Sort by status (worst first)
        status_order = {'offline': 0, 'unhealthy': 1, 'degraded': 2, 'healthy': 3}
        providers.sort(
            key=lambda p: status_order.get(
                data['provider_status'][p]['status'], 4
            )
        )
        
        # Display in grid
        cols_per_row = 4
        for i in range(0, len(providers), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(providers):
                    provider = providers[i + j]
                    provider_data = data['provider_status'][provider]
                    
                    with col:
                        # Status color
                        status_colors = {
                            'healthy': '#10b981',
                            'degraded': '#f59e0b',
                            'unhealthy': '#ef4444',
                            'offline': '#991b1b',
                            'unknown': '#6b7280'
                        }
                        color = status_colors.get(provider_data['status'], '#6b7280')
                        
                        # Provider card
                        st.markdown(f"""
                        <div style="border: 2px solid {color}; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                            <h4 style="margin: 0 0 10px 0; color: {color};">{provider.upper()}</h4>
                            <p style="margin: 5px 0; font-size: 14px;">
                                Status: <strong>{provider_data['status'].upper()}</strong><br>
                                Uptime: <strong>{provider_data['uptime']:.1%}</strong><br>
                                Response: <strong>{provider_data['response_time']:.0f}ms</strong><br>
                                Errors: <strong>{provider_data['error_rate']:.1%}</strong>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Historical charts
    st.subheader("📈 Performance Metrics")
    
    # Response time chart
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Response Times (ms)", "Error Rates (%)"),
        vertical_spacing=0.1
    )
    
    # Add traces for each provider
    for provider, history in monitor.historical_data.items():
        if history:
            timestamps = [m.timestamp for m in history]
            response_times = [m.response_time_ms for m in history]
            error_rate = []
            
            # Calculate rolling error rate
            for i in range(len(history)):
                window = history[max(0, i-10):i+1]
                failures = sum(1 for m in window if not m.success)
                error_rate.append(failures / len(window) * 100)
            
            # Response time trace
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=response_times,
                    mode='lines',
                    name=provider,
                    line=dict(width=2)
                ),
                row=1, col=1
            )
            
            # Error rate trace
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=error_rate,
                    mode='lines',
                    name=provider,
                    line=dict(width=2),
                    showlegend=False
                ),
                row=2, col=1
            )
    
    fig.update_layout(height=600, showlegend=True)
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="Response Time (ms)", row=1, col=1)
    fig.update_yaxes(title_text="Error Rate (%)", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent alerts
    st.subheader("🚨 Recent Alerts")
    
    recent_alerts = data['recent_alerts']
    if recent_alerts:
        # Convert to DataFrame for display
        alerts_df = pd.DataFrame(recent_alerts)
        alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'])
        alerts_df = alerts_df.sort_values('timestamp', ascending=False)
        
        # Display with styling
        st.dataframe(
            alerts_df[['timestamp', 'provider', 'severity', 'message', 'resolved']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No recent alerts")


# Example usage
async def main():
    # Initialize monitor
    monitor = APIHealthMonitor(check_interval=60)  # 1 minute for demo
    
    # Start monitoring key providers
    providers = [
        'coingecko', 'coinmarketcap', 'dexscreener', 
        'jupiter', 'etherscan', 'moralis', 'birdeye'
    ]
    
    await monitor.start_monitoring(providers)
    
    # Simulate running for a bit
    await asyncio.sleep(300)  # 5 minutes
    
    # Get dashboard data
    dashboard_data = monitor.get_dashboard_data()
    print(json.dumps(dashboard_data, indent=2, default=str))
    
    # Stop monitoring
    await monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())