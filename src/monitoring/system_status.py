#!/usr/bin/env python3
"""
SYSTEM STATUS MONITORING
Real-time token refresh timing and model tracking
"""
import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import json
from dataclasses import dataclass, field
import anthropic
from pathlib import Path

@dataclass
class TokenUsage:
    """Track API token usage and refresh timing"""
    api_name: str
    tokens_used: int = 0
    tokens_limit: int = 1000000
    reset_time: Optional[datetime] = None
    last_request: Optional[datetime] = None
    requests_per_minute: int = 60
    requests_made: int = 0
    
    @property
    def tokens_remaining(self) -> int:
        return max(0, self.tokens_limit - self.tokens_used)
    
    @property
    def usage_percentage(self) -> float:
        return (self.tokens_used / self.tokens_limit) * 100
    
    @property
    def time_until_reset(self) -> Optional[timedelta]:
        if self.reset_time:
            return max(timedelta(0), self.reset_time - datetime.now())
        return None
    
    @property
    def status_color(self) -> str:
        if self.usage_percentage < 70:
            return "#10b981"  # Green
        elif self.usage_percentage < 90:
            return "#f59e0b"  # Yellow
        else:
            return "#ef4444"  # Red

@dataclass
class ModelInfo:
    """Track active AI models and their status"""
    model_name: str
    provider: str
    status: str = "active"
    last_used: Optional[datetime] = None
    tokens_used: int = 0
    requests_count: int = 0
    average_response_time: float = 0.0
    error_count: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.requests_count == 0:
            return 100.0
        return ((self.requests_count - self.error_count) / self.requests_count) * 100

class SystemStatusMonitor:
    """
    Comprehensive system status monitoring for TrenchCoat Elite
    """
    
    def __init__(self):
        # Initialize token usage tracking
        self.token_usage = {
            "claude": TokenUsage(
                api_name="Claude API",
                tokens_limit=1000000,  # 1M tokens per month
                reset_time=self._get_next_month_reset(),
                requests_per_minute=60
            ),
            "coingecko": TokenUsage(
                api_name="CoinGecko API",
                tokens_limit=10000,  # 10K calls per month (free tier)
                reset_time=self._get_next_month_reset(),
                requests_per_minute=50
            ),
            "dexscreener": TokenUsage(
                api_name="DexScreener API",
                tokens_limit=100000,  # No official limit, track requests
                reset_time=self._get_next_day_reset(),
                requests_per_minute=100
            ),
            "birdeye": TokenUsage(
                api_name="Birdeye API",
                tokens_limit=100000,
                reset_time=self._get_next_day_reset(),
                requests_per_minute=60
            ),
            "jupiter": TokenUsage(
                api_name="Jupiter API",
                tokens_limit=1000000,
                reset_time=self._get_next_day_reset(),
                requests_per_minute=120
            )
        }
        
        # Initialize model tracking
        self.active_models = {
            "claude-sonnet-4": ModelInfo(
                model_name="Claude Sonnet 4",
                provider="Anthropic",
                status="active"
            ),
            "claude-opus": ModelInfo(
                model_name="Claude Opus",
                provider="Anthropic",
                status="fallback"
            ),
            "local_processing": ModelInfo(
                model_name="Local Processing",
                provider="TrenchCoat",
                status="backup"
            )
        }
        
        # Load usage data if exists
        self.load_usage_data()
        
        # System metrics
        self.system_start_time = datetime.now()
        self.last_update = datetime.now()
    
    def _get_next_month_reset(self) -> datetime:
        """Get next month's reset time"""
        now = datetime.now()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        else:
            return datetime(now.year, now.month + 1, 1)
    
    def _get_next_day_reset(self) -> datetime:
        """Get next day's reset time"""
        now = datetime.now()
        return datetime(now.year, now.month, now.day) + timedelta(days=1)
    
    def load_usage_data(self):
        """Load usage data from file"""
        try:
            usage_file = Path("data/usage_tracking.json")
            if usage_file.exists():
                with open(usage_file, 'r') as f:
                    data = json.load(f)
                    
                # Update token usage from saved data
                for api_name, usage_data in data.get('token_usage', {}).items():
                    if api_name in self.token_usage:
                        self.token_usage[api_name].tokens_used = usage_data.get('tokens_used', 0)
                        self.token_usage[api_name].requests_made = usage_data.get('requests_made', 0)
                        if usage_data.get('last_request'):
                            self.token_usage[api_name].last_request = datetime.fromisoformat(usage_data['last_request'])
                
                # Update model info from saved data
                for model_name, model_data in data.get('models', {}).items():
                    if model_name in self.active_models:
                        self.active_models[model_name].tokens_used = model_data.get('tokens_used', 0)
                        self.active_models[model_name].requests_count = model_data.get('requests_count', 0)
                        self.active_models[model_name].error_count = model_data.get('error_count', 0)
                        if model_data.get('last_used'):
                            self.active_models[model_name].last_used = datetime.fromisoformat(model_data['last_used'])
        
        except Exception as e:
            st.error(f"Error loading usage data: {e}")
    
    def save_usage_data(self):
        """Save usage data to file"""
        try:
            usage_file = Path("data/usage_tracking.json")
            usage_file.parent.mkdir(exist_ok=True)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'token_usage': {
                    api_name: {
                        'tokens_used': usage.tokens_used,
                        'requests_made': usage.requests_made,
                        'last_request': usage.last_request.isoformat() if usage.last_request else None
                    }
                    for api_name, usage in self.token_usage.items()
                },
                'models': {
                    model_name: {
                        'tokens_used': model.tokens_used,
                        'requests_count': model.requests_count,
                        'error_count': model.error_count,
                        'last_used': model.last_used.isoformat() if model.last_used else None
                    }
                    for model_name, model in self.active_models.items()
                }
            }
            
            with open(usage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            st.error(f"Error saving usage data: {e}")
    
    def update_token_usage(self, api_name: str, tokens_used: int = 1):
        """Update token usage for an API"""
        if api_name in self.token_usage:
            self.token_usage[api_name].tokens_used += tokens_used
            self.token_usage[api_name].requests_made += 1
            self.token_usage[api_name].last_request = datetime.now()
            self.save_usage_data()
    
    def update_model_usage(self, model_name: str, tokens_used: int = 0, success: bool = True):
        """Update model usage statistics"""
        if model_name in self.active_models:
            model = self.active_models[model_name]
            model.tokens_used += tokens_used
            model.requests_count += 1
            model.last_used = datetime.now()
            if not success:
                model.error_count += 1
            self.save_usage_data()
    
    def get_system_uptime(self) -> str:
        """Get system uptime formatted"""
        uptime = datetime.now() - self.system_start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"
    
    def render_token_status_dashboard(self):
        """Render token usage and refresh timing dashboard"""
        st.subheader("🔑 API Token Status & Refresh Timing")
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_apis = len(self.token_usage)
        healthy_apis = sum(1 for usage in self.token_usage.values() if usage.usage_percentage < 90)
        warning_apis = sum(1 for usage in self.token_usage.values() if 70 <= usage.usage_percentage < 90)
        critical_apis = sum(1 for usage in self.token_usage.values() if usage.usage_percentage >= 90)
        
        with col1:
            st.metric("Total APIs", total_apis)
        
        with col2:
            st.metric("Healthy", healthy_apis, delta=f"{(healthy_apis/total_apis)*100:.0f}%")
        
        with col3:
            st.metric("Warning", warning_apis, delta=f"{(warning_apis/total_apis)*100:.0f}%")
        
        with col4:
            st.metric("Critical", critical_apis, delta=f"{(critical_apis/total_apis)*100:.0f}%")
        
        # Individual API status cards
        for api_name, usage in self.token_usage.items():
            time_until_reset = usage.time_until_reset
            reset_str = "Unknown"
            if time_until_reset:
                if time_until_reset.days > 0:
                    reset_str = f"{time_until_reset.days}d {time_until_reset.seconds//3600}h"
                else:
                    reset_str = f"{time_until_reset.seconds//3600}h {(time_until_reset.seconds%3600)//60}m"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                       padding: 1.5rem; border-radius: 12px; margin: 1rem 0; 
                       border-left: 4px solid {usage.status_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: {usage.status_color};">{usage.api_name}</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #9ca3af;">
                            Usage: {usage.tokens_used:,} / {usage.tokens_limit:,} 
                            ({usage.usage_percentage:.1f}%)
                        </p>
                        <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.9rem;">
                            Requests: {usage.requests_made:,} | Rate: {usage.requests_per_minute}/min
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #10b981; font-size: 1.2rem; font-weight: bold;">
                            {reset_str}
                        </div>
                        <div style="color: #9ca3af; font-size: 0.8rem;">Until Reset</div>
                    </div>
                </div>
                
                <div style="margin-top: 1rem;">
                    <div style="background: #374151; border-radius: 10px; height: 8px; overflow: hidden;">
                        <div style="background: {usage.status_color}; height: 100%; 
                                   width: {min(100, usage.usage_percentage)}%; 
                                   transition: width 0.3s ease;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_model_status_dashboard(self):
        """Render active models status dashboard"""
        st.subheader("🤖 Active AI Models Status")
        
        # Model overview
        active_count = sum(1 for model in self.active_models.values() if model.status == "active")
        total_requests = sum(model.requests_count for model in self.active_models.values())
        avg_success_rate = sum(model.success_rate for model in self.active_models.values()) / len(self.active_models)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Models", active_count)
        
        with col2:
            st.metric("Total Requests", f"{total_requests:,}")
        
        with col3:
            st.metric("Avg Success Rate", f"{avg_success_rate:.1f}%")
        
        # Individual model status
        for model_name, model in self.active_models.items():
            status_color = {
                "active": "#10b981",
                "fallback": "#f59e0b", 
                "backup": "#6b7280",
                "error": "#ef4444"
            }.get(model.status, "#9ca3af")
            
            last_used_str = "Never"
            if model.last_used:
                time_diff = datetime.now() - model.last_used
                if time_diff.days > 0:
                    last_used_str = f"{time_diff.days}d ago"
                elif time_diff.seconds > 3600:
                    last_used_str = f"{time_diff.seconds//3600}h ago"
                else:
                    last_used_str = f"{time_diff.seconds//60}m ago"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                       padding: 1.5rem; border-radius: 12px; margin: 1rem 0; 
                       border-left: 4px solid {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: {status_color};">
                            {model.model_name}
                            <span style="background: {status_color}; color: white; 
                                        padding: 0.2rem 0.5rem; border-radius: 12px; 
                                        font-size: 0.7rem; margin-left: 0.5rem;">
                                {model.status.upper()}
                            </span>
                        </h4>
                        <p style="margin: 0.5rem 0 0 0; color: #9ca3af;">
                            Provider: {model.provider} | Last Used: {last_used_str}
                        </p>
                        <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.9rem;">
                            Requests: {model.requests_count:,} | 
                            Success Rate: {model.success_rate:.1f}% | 
                            Tokens: {model.tokens_used:,}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {status_color}; font-size: 1.2rem; font-weight: bold;">
                            {model.success_rate:.1f}%
                        </div>
                        <div style="color: #9ca3af; font-size: 0.8rem;">Success Rate</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_system_health_dashboard(self):
        """Render overall system health dashboard"""
        st.subheader("⚡ System Health & Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("System Uptime", self.get_system_uptime())
        
        with col2:
            # Calculate overall API health score
            health_scores = [
                100 - usage.usage_percentage for usage in self.token_usage.values()
            ]
            avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
            st.metric("API Health", f"{avg_health:.0f}%")
        
        with col3:
            # Calculate model reliability
            model_reliability = sum(model.success_rate for model in self.active_models.values()) / len(self.active_models)
            st.metric("Model Reliability", f"{model_reliability:.1f}%")
        
        with col4:
            st.metric("Last Update", self.last_update.strftime("%H:%M:%S"))
        
        # Real-time status indicators
        st.markdown("### 🔴 Live Status Indicators")
        
        status_indicators = []
        
        # API Status
        critical_apis = [name for name, usage in self.token_usage.items() if usage.usage_percentage >= 90]
        if critical_apis:
            status_indicators.append(f"🔴 **Critical:** {', '.join(critical_apis)} APIs near limit")
        
        warning_apis = [name for name, usage in self.token_usage.items() if 70 <= usage.usage_percentage < 90]
        if warning_apis:
            status_indicators.append(f"🟡 **Warning:** {', '.join(warning_apis)} APIs at 70%+ usage")
        
        # Model Status
        error_models = [name for name, model in self.active_models.items() if model.success_rate < 95]
        if error_models:
            status_indicators.append(f"🟡 **Models:** {', '.join(error_models)} showing errors")
        
        # Claude API specific status
        claude_usage = self.token_usage.get('claude')
        if claude_usage and claude_usage.time_until_reset:
            reset_hours = claude_usage.time_until_reset.total_seconds() / 3600
            if reset_hours < 24:
                status_indicators.append(f"⏰ **Claude API:** Resets in {reset_hours:.1f} hours")
        
        if not status_indicators:
            st.success("🟢 **All Systems Operational** - No issues detected")
        else:
            for indicator in status_indicators:
                st.markdown(indicator)
    
    def render_refresh_countdown(self):
        """Render countdown timers for various API resets"""
        st.subheader("⏰ Token Refresh Countdown")
        
        # Create a real-time updating display
        countdown_placeholder = st.empty()
        
        with countdown_placeholder.container():
            cols = st.columns(len(self.token_usage))
            
            for i, (api_name, usage) in enumerate(self.token_usage.items()):
                with cols[i]:
                    time_until_reset = usage.time_until_reset
                    if time_until_reset:
                        total_seconds = time_until_reset.total_seconds()
                        hours = int(total_seconds // 3600)
                        minutes = int((total_seconds % 3600) // 60)
                        seconds = int(total_seconds % 60)
                        
                        countdown_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                        
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; 
                                   background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                                   border-radius: 8px; border: 1px solid {usage.status_color};">
                            <h4 style="margin: 0; color: {usage.status_color};">{api_name.split()[0]}</h4>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #10b981; 
                                       font-family: monospace; margin: 0.5rem 0;">
                                {countdown_str}
                            </div>
                            <div style="color: #9ca3af; font-size: 0.8rem;">Until Reset</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; 
                                   background: #374151; border-radius: 8px;">
                            <h4 style="margin: 0; color: #9ca3af;">{api_name.split()[0]}</h4>
                            <div style="color: #6b7280;">No Reset Info</div>
                        </div>
                        """, unsafe_allow_html=True)

def render_system_status_interface():
    """Main function to render the system status interface"""
    monitor = SystemStatusMonitor()
    
    # Update the last update time
    monitor.last_update = datetime.now()
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                border-radius: 16px; margin-bottom: 2rem; border: 2px solid #10b981;">
        <h1 style="color: #10b981; margin: 0;">📊 System Status Dashboard</h1>
        <p style="color: #d1d5db; margin: 0.5rem 0 0 0;">
            Real-time monitoring of API tokens, model usage, and system health
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different status views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔑 Token Status", 
        "🤖 Model Status", 
        "⚡ System Health", 
        "⏰ Refresh Timers"
    ])
    
    with tab1:
        monitor.render_token_status_dashboard()
    
    with tab2:
        monitor.render_model_status_dashboard()
    
    with tab3:
        monitor.render_system_health_dashboard()
    
    with tab4:
        monitor.render_refresh_countdown()
    
    # Auto-refresh functionality
    if st.button("🔄 Refresh Status", type="primary"):
        st.rerun()
    
    # Auto-refresh every 30 seconds
    st.markdown("""
    <script>
    setTimeout(function(){
        window.location.reload();
    }, 30000);
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_system_status_interface()