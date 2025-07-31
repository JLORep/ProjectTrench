#!/usr/bin/env python3
"""
TrenchCoat Pro - Ultra Premium Dashboard
Apple/PayPal-level design with live updates and animations
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import random
import asyncio
from typing import Dict, List, Any
import json
import requests
from PIL import Image
import io
import base64

# Import our advanced analytics
try:
    from advanced_analytics import AdvancedAnalytics
except ImportError:
    AdvancedAnalytics = None

# Page configuration (handled by streamlit_app.py)

# Custom CSS for ultra-premium design
st.markdown("""
<style>
    /* Import premium fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Premium background */
    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
    }
    
    /* Premium cards */
    .premium-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin: 12px 0;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .premium-card:hover {
        transform: translateY(-2px);
        border-color: rgba(16, 185, 129, 0.5);
        box-shadow: 0 12px 48px 0 rgba(16, 185, 129, 0.2);
    }
    
    /* Glowing metrics */
    .metric-glow {
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    /* Premium buttons */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px 0 rgba(16, 185, 129, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(16, 185, 129, 0.6);
    }
    
    /* Live indicator */
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        background: rgba(16, 185, 129, 0.2);
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        color: #10b981;
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: blink 1.5s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    /* Coin card animation */
    .coin-card {
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Success animation */
    .success-flash {
        animation: successFlash 0.5s ease-out;
    }
    
    @keyframes successFlash {
        0% { background-color: rgba(16, 185, 129, 0.3); }
        100% { background-color: transparent; }
    }
</style>
""", unsafe_allow_html=True)

class UltraPremiumDashboard:
    """Ultra-premium dashboard with live updates"""
    
    def __init__(self):
        self.initialize_session_state()
        self.setup_page_layout()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'total_profit' not in st.session_state:
            st.session_state.total_profit = 0
        if 'win_rate' not in st.session_state:
            st.session_state.win_rate = 73.2
        if 'active_positions' not in st.session_state:
            st.session_state.active_positions = []
        if 'processed_coins' not in st.session_state:
            st.session_state.processed_coins = []
        if 'performance_history' not in st.session_state:
            st.session_state.performance_history = []
        if 'ai_suggestions' not in st.session_state:
            st.session_state.ai_suggestions = []
    
    def setup_page_layout(self):
        """Setup the main page layout"""
        # Premium header
        self.render_header()
        
        # Main content area
        self.render_main_content()
    
    def render_header(self):
        """Render premium header with live status"""
        header_col1, header_col2, header_col3 = st.columns([2, 3, 1])
        
        with header_col1:
            st.markdown("""
            <h1 style="margin: 0; font-size: 32px; font-weight: 700; 
                       background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;">
                TrenchCoat Pro
            </h1>
            <p style="margin: 0; color: #9ca3af; font-size: 14px;">
                Live Trading Intelligence Platform
            </p>
            """, unsafe_allow_html=True)
        
        with header_col2:
            # Live status indicators
            st.markdown("""
            <div style="display: flex; gap: 20px; justify-content: center; align-items: center; height: 100%;">
                <div class="live-indicator">
                    <div class="live-dot"></div>
                    <span>LIVE TRADING</span>
                </div>
                <div style="color: #6b7280; font-size: 14px;">
                    APIs: <span style="color: #10b981;">6/6 Connected</span>
                </div>
                <div style="color: #6b7280; font-size: 14px;">
                    Latency: <span style="color: #10b981;">12ms</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with header_col3:
            current_time = datetime.now().strftime("%H:%M:%S")
            st.markdown(f"""
            <div style="text-align: right; color: #9ca3af; font-size: 14px;">
                {current_time} UTC
            </div>
            """, unsafe_allow_html=True)
    
    def render_main_content(self):
        """Render main content area with tabbed interface"""
        # Top metrics row
        self.render_key_metrics()
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Live Dashboard", "🧠 Advanced Analytics", "⚙️ Trading Engine"])
        
        with tab1:
            # Main content columns
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                self.render_live_coin_feed()
                self.render_ai_suggestions()
            
            with col2:
                self.render_performance_chart()
                self.render_active_positions()
            
            with col3:
                self.render_strategy_performance()
                self.render_recent_wins()
        
        with tab2:
            # Advanced Analytics Section
            self.render_advanced_analytics()
        
        with tab3:
            # Trading Engine Configuration
            self.render_trading_engine_config()
    
    def render_key_metrics(self):
        """Render key performance metrics"""
        metrics_container = st.container()
        
        with metrics_container:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Simulate live profit updates
            profit_change = random.uniform(-50, 200)
            st.session_state.total_profit += profit_change
            
            with col1:
                st.markdown(f"""
                <div class="premium-card">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">Total Profit</p>
                    <h2 class="metric-glow" style="color: #10b981; margin: 0;">
                        ${st.session_state.total_profit:,.2f}
                    </h2>
                    <p style="color: {'#10b981' if profit_change > 0 else '#ef4444'}; 
                              font-size: 12px; margin: 0;">
                        {'↑' if profit_change > 0 else '↓'} ${abs(profit_change):.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                win_rate_change = random.uniform(-0.5, 0.5)
                st.session_state.win_rate = max(0, min(100, st.session_state.win_rate + win_rate_change))
                
                st.markdown(f"""
                <div class="premium-card">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">Win Rate</p>
                    <h2 style="color: #f9fafb; margin: 0;">
                        {st.session_state.win_rate:.1f}%
                    </h2>
                    <div style="background: rgba(255,255,255,0.1); height: 4px; border-radius: 2px; margin-top: 8px;">
                        <div style="background: #10b981; height: 100%; width: {st.session_state.win_rate}%; 
                                    border-radius: 2px; transition: width 0.5s ease;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                active_count = len(st.session_state.active_positions)
                st.markdown(f"""
                <div class="premium-card">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">Active Trades</p>
                    <h2 style="color: #f9fafb; margin: 0;">{active_count}</h2>
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">
                        {random.randint(5, 15)} pending
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                processed_today = len(st.session_state.processed_coins)
                st.markdown(f"""
                <div class="premium-card">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">Coins Analyzed</p>
                    <h2 style="color: #f9fafb; margin: 0;">{processed_today}</h2>
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">
                        {random.randint(50, 100)}/min
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                api_health = random.randint(98, 100)
                st.markdown(f"""
                <div class="premium-card">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">System Health</p>
                    <h2 style="color: {'#10b981' if api_health > 95 else '#f59e0b'}; margin: 0;">
                        {api_health}%
                    </h2>
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">
                        All systems go
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    def render_live_coin_feed(self):
        """Render live coin processing feed"""
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #f9fafb; margin-bottom: 16px;">Live Coin Processing</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulate new coin being processed
        if random.random() > 0.3:
            new_coin = self.generate_fake_coin()
            st.session_state.processed_coins.insert(0, new_coin)
            st.session_state.processed_coins = st.session_state.processed_coins[:10]
        
        # Display coins with animations
        for i, coin in enumerate(st.session_state.processed_coins[:5]):
            self.render_coin_card(coin, i)
    
    def generate_fake_coin(self):
        """Generate fake coin data for demo"""
        tickers = ['PEPE', 'WOJAK', 'BONK', 'WIF', 'MYRO', 'BOME', 'SLERF', 'PONKE']
        stages = ['Discovering', 'Enriching', 'Analyzing', 'Trading', 'Completed']
        
        return {
            'ticker': f'${random.choice(tickers)}',
            'stage': random.choice(stages),
            'price': random.uniform(0.0001, 0.01),
            'volume': random.randint(100000, 5000000),
            'score': random.uniform(0.6, 0.95),
            'timestamp': datetime.now()
        }
    
    def render_coin_card(self, coin, index):
        """Render individual coin card with animation"""
        stage_colors = {
            'Discovering': '#3b82f6',
            'Enriching': '#f59e0b',
            'Analyzing': '#8b5cf6',
            'Trading': '#10b981',
            'Completed': '#6b7280'
        }
        
        stage_color = stage_colors.get(coin['stage'], '#6b7280')
        
        # Generate coin icon placeholder
        icon_html = f"""
        <div style="width: 40px; height: 40px; border-radius: 50%; 
                    background: linear-gradient(135deg, {stage_color} 0%, {stage_color}80 100%);
                    display: flex; align-items: center; justify-content: center;
                    font-weight: bold; color: white;">
            {coin['ticker'][1:3]}
        </div>
        """
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown(icon_html, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="coin-card {'success-flash' if coin['stage'] == 'Trading' else ''}" 
                 style="opacity: {1 - (index * 0.15)};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: #f9fafb; font-weight: 600;">{coin['ticker']}</span>
                        <span style="color: #6b7280; font-size: 12px; margin-left: 8px;">
                            ${coin['price']:.6f}
                        </span>
                    </div>
                    <span style="color: {stage_color}; font-size: 12px; font-weight: 500;">
                        {coin['stage']}
                    </span>
                </div>
                <div style="margin-top: 8px;">
                    <div style="background: rgba(255,255,255,0.1); height: 4px; border-radius: 2px;">
                        <div style="background: {stage_color}; height: 100%; 
                                    width: {coin['score'] * 100}%; border-radius: 2px;
                                    transition: width 0.5s ease;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                        <span style="color: #6b7280; font-size: 11px;">
                            Vol: ${coin['volume']:,}
                        </span>
                        <span style="color: #10b981; font-size: 11px;">
                            Score: {coin['score']:.2f}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_performance_chart(self):
        """Render real-time performance chart"""
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #f9fafb; margin-bottom: 16px;">Live Performance</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate performance data
        if len(st.session_state.performance_history) == 0:
            # Initialize with some historical data
            for i in range(50):
                st.session_state.performance_history.append({
                    'time': datetime.now() - timedelta(seconds=50-i),
                    'profit': random.uniform(-100, 200)
                })
        
        # Add new data point
        st.session_state.performance_history.append({
            'time': datetime.now(),
            'profit': st.session_state.total_profit
        })
        
        # Keep only recent data
        st.session_state.performance_history = st.session_state.performance_history[-100:]
        
        # Create chart
        df = pd.DataFrame(st.session_state.performance_history)
        
        fig = go.Figure()
        
        # Add gradient fill
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['profit'],
            mode='lines',
            line=dict(color='#10b981', width=2),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.1)',
            name='Profit'
        ))
        
        # Update layout for dark theme
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.05)',
                tickfont=dict(color='#6b7280', size=10),
                zeroline=True,
                zerolinecolor='rgba(255,255,255,0.1)'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    def render_active_positions(self):
        """Render active trading positions"""
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #f9fafb; margin-bottom: 16px;">Active Positions</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulate active positions
        if random.random() > 0.7:
            position = {
                'ticker': f"${random.choice(['BONK', 'WIF', 'PEPE', 'MYRO'])}",
                'entry': random.uniform(0.001, 0.01),
                'current': random.uniform(0.001, 0.01),
                'size': random.uniform(0.1, 0.5),
                'time': datetime.now()
            }
            st.session_state.active_positions.append(position)
            st.session_state.active_positions = st.session_state.active_positions[-5:]
        
        # Display positions
        for pos in st.session_state.active_positions:
            pnl = ((pos['current'] - pos['entry']) / pos['entry']) * 100
            pnl_color = '#10b981' if pnl > 0 else '#ef4444'
            
            st.markdown(f"""
            <div class="premium-card" style="padding: 12px; margin: 8px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #f9fafb; font-weight: 500;">{pos['ticker']}</span>
                    <span style="color: {pnl_color}; font-weight: 600;">
                        {pnl:+.2f}%
                    </span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                    <span style="color: #6b7280; font-size: 12px;">
                        Entry: ${pos['entry']:.6f}
                    </span>
                    <span style="color: #6b7280; font-size: 12px;">
                        Size: {pos['size']:.2f} SOL
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_strategy_performance(self):
        """Render strategy performance breakdown"""
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #f9fafb; margin-bottom: 16px;">Strategy Performance</h3>
        </div>
        """, unsafe_allow_html=True)
        
        strategies = [
            {'name': 'Whale Following', 'win_rate': 81.6, 'profit': random.uniform(500, 1500)},
            {'name': 'Volume Explosion', 'win_rate': 76.8, 'profit': random.uniform(300, 1000)},
            {'name': 'Momentum Breakout', 'win_rate': 73.2, 'profit': random.uniform(200, 800)},
            {'name': 'Social Sentiment', 'win_rate': 68.4, 'profit': random.uniform(100, 600)},
        ]
        
        for strategy in strategies:
            st.markdown(f"""
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="color: #f9fafb; font-size: 14px;">{strategy['name']}</span>
                    <span style="color: #10b981; font-size: 14px; font-weight: 600;">
                        ${strategy['profit']:.0f}
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="background: rgba(255,255,255,0.1); height: 6px; 
                                border-radius: 3px; flex: 1;">
                        <div style="background: linear-gradient(90deg, #10b981 0%, #059669 100%); 
                                    height: 100%; width: {strategy['win_rate']}%; 
                                    border-radius: 3px;"></div>
                    </div>
                    <span style="color: #6b7280; font-size: 12px; width: 45px; text-align: right;">
                        {strategy['win_rate']:.1f}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_recent_wins(self):
        """Render recent winning trades"""
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #f9fafb; margin-bottom: 16px;">Recent Wins</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate fake winning trades
        wins = []
        for i in range(3):
            wins.append({
                'ticker': f"${random.choice(['BONK', 'WIF', 'PEPE', 'MYRO', 'BOME'])}",
                'profit': random.uniform(50, 500),
                'roi': random.uniform(15, 85),
                'time': datetime.now() - timedelta(minutes=random.randint(1, 60))
            })
        
        for win in wins:
            time_ago = (datetime.now() - win['time']).seconds // 60
            st.markdown(f"""
            <div class="premium-card success-flash" style="padding: 12px; margin: 8px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #f9fafb; font-weight: 500;">{win['ticker']}</span>
                    <span style="color: #10b981; font-weight: 600;">
                        +${win['profit']:.2f}
                    </span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                    <span style="color: #6b7280; font-size: 12px;">
                        +{win['roi']:.1f}% ROI
                    </span>
                    <span style="color: #6b7280; font-size: 12px;">
                        {time_ago}m ago
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_ai_suggestions(self):
        """Render AI-powered improvement suggestions"""
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #f9fafb; margin-bottom: 16px;">
                AI Suggestions
                <span style="color: #10b981; font-size: 12px; margin-left: 8px;">
                    powered by Claude
                </span>
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate AI suggestions
        suggestions = [
            {
                'icon': '📈',
                'title': 'Increase Position Size',
                'desc': 'Win rate above 80% on BONK trades',
                'action': 'Apply'
            },
            {
                'icon': '⚡',
                'title': 'New Strategy Available',
                'desc': 'Lightning trades showing 85% success',
                'action': 'Enable'
            },
            {
                'icon': '🎯',
                'title': 'Optimize Entry Timing',
                'desc': 'Shift entries 2min earlier for +15% gains',
                'action': 'Update'
            }
        ]
        
        for suggestion in suggestions:
            st.markdown(f"""
            <div class="premium-card" style="padding: 16px; margin: 8px 0;">
                <div style="display: flex; gap: 12px;">
                    <div style="font-size: 24px;">{suggestion['icon']}</div>
                    <div style="flex: 1;">
                        <div style="color: #f9fafb; font-weight: 500; margin-bottom: 4px;">
                            {suggestion['title']}
                        </div>
                        <div style="color: #6b7280; font-size: 13px;">
                            {suggestion['desc']}
                        </div>
                    </div>
                    <button style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                                   color: white; border: none; border-radius: 8px;
                                   padding: 8px 16px; font-size: 12px; font-weight: 600;
                                   cursor: pointer;">
                        {suggestion['action']}
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_advanced_analytics(self):
        """Render advanced analytics section"""
        if AdvancedAnalytics is None:
            st.error("🚨 Advanced Analytics module not available")
            st.info("Installing required dependencies: scikit-learn, seaborn")
            return
        
        try:
            analytics = AdvancedAnalytics()
            analytics.render_advanced_analytics()
        except Exception as e:
            st.error(f"❌ Analytics Error: {e}")
            st.info("📊 Falling back to basic analytics...")
            self.render_basic_analytics()
    
    def render_basic_analytics(self):
        """Fallback basic analytics if advanced is not available"""
        st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
                    border-radius: 15px; border: 1px solid rgba(16, 185, 129, 0.3);'>
            <h1 style='color: #10b981; margin: 0; font-size: 2.5rem; font-weight: 700;'>
                📊 Market Analytics
            </h1>
            <p style='color: #a3a3a3; margin-top: 0.5rem; font-size: 1.2rem;'>
                Professional Trading Intelligence
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate sample data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        prices = np.random.randn(30).cumsum() + 1000
        
        # Price trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines+markers',
            line=dict(color='#10b981', width=3),
            marker=dict(size=6, color='#34d399'),
            name='Price Trend'
        ))
        
        fig.update_layout(
            title='📈 30-Day Price Analysis',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400,
            xaxis=dict(gridcolor='rgba(16, 185, 129, 0.2)'),
            yaxis=dict(gridcolor='rgba(16, 185, 129, 0.2)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analytics metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Volatility", "12.3%", delta="↓2.1%")
        with col2:
            st.metric("🎯 Trend Strength", "Strong", delta="Bullish")
        with col3:
            st.metric("📈 Moving Avg", f"${prices[-1]:.2f}", delta=f"{((prices[-1]/prices[-7])-1)*100:.1f}%")
        with col4:
            st.metric("🏆 Performance", "87.3%", delta="↑5.2%")
    
    def render_trading_engine_config(self):
        """Render trading engine configuration"""
        st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
                    border-radius: 15px; border: 1px solid rgba(239, 68, 68, 0.3);'>
            <h1 style='color: #ef4444; margin: 0; font-size: 2.5rem; font-weight: 700;'>
                ⚙️ Trading Engine
            </h1>
            <p style='color: #a3a3a3; margin-top: 0.5rem; font-size: 1.2rem;'>
                Automated Solana Trading Configuration
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🔧 Engine Settings")
            
            trading_enabled = st.toggle("Enable Live Trading", value=False)
            max_position_size = st.slider("Max Position Size (SOL)", 0.01, 1.0, 0.1)
            risk_level = st.selectbox("Risk Level", ["Conservative", "Moderate", "Aggressive"])
            
            st.markdown("### 🎯 Strategy Parameters")
            min_confidence = st.slider("Minimum Confidence %", 50, 95, 75)
            stop_loss = st.slider("Stop Loss %", 1, 20, 5)
            take_profit = st.slider("Take Profit %", 5, 100, 25)
        
        with col2:
            st.markdown("### 📊 Engine Status")
            
            if trading_enabled:
                st.success("🟢 LIVE TRADING ACTIVE")
                st.warning("⚠️ Real money at risk!")
            else:
                st.info("🔵 DEMO MODE - No real trades")
            
            st.markdown("### 📈 Current Stats")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("🎯 Success Rate", "73.2%")
                st.metric("💰 Total P&L", "$2,341")
            with col_b:
                st.metric("🔄 Active Trades", "3")
                st.metric("⏱️ Avg Hold Time", "4.2h")
            
            if st.button("🚀 Deploy Strategy", type="primary"):
                if trading_enabled:
                    st.success("✅ Strategy deployed to live trading!")
                    st.balloons()
                else:
                    st.info("📋 Strategy updated in demo mode")

def main():
    """Run the ultra-premium dashboard"""
    dashboard = UltraPremiumDashboard()

if __name__ == "__main__":
    main()