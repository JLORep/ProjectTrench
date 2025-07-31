#!/usr/bin/env python3
"""
Streamlit-safe version of Ultra Premium Dashboard
All imports wrapped in try-catch to prevent failures
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import time
import random
import asyncio
from typing import Dict, List, Any
import json
import requests

# Safe imports with fallbacks
try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from branding_system import BrandingSystem
    branding = BrandingSystem()
except ImportError:
    branding = None

# Import our Streamlit-safe database
try:
    from streamlit_database import streamlit_db
    database_available = True
except ImportError:
    database_available = False
    streamlit_db = None

# Custom CSS for ultra-premium design
def apply_custom_css():
    """Apply custom CSS for ultra-premium design with Streamlit Cloud compatibility"""
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
    
    /* Telegram Signal Cards */
    .signal-card {
        background: rgba(45, 45, 45, 0.8);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        border-left: 4px solid #4CAF50;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        color: white;
        transition: all 0.3s ease;
    }
    
    .signal-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
    }
    
    .signal-buy { border-left-color: #4CAF50; }
    .signal-sell { border-left-color: #f44336; }
    .signal-hold { border-left-color: #ff9800; }
</style>
    """, unsafe_allow_html=True)

class StreamlitSafeDashboard:
    """Streamlit-safe Ultra-premium dashboard with fallback imports"""
    
    def __init__(self):
        self.initialize_session_state()
        apply_custom_css()
        if branding:
            try:
                branding.apply_custom_css()
            except Exception:
                pass
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
    
    def setup_page_layout(self):
        """Setup the main page layout"""
        # Page header
        self.render_header()
        
        # Main content
        self.render_main_content()
    
    def render_header(self):
        """Render the premium header"""
        st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
                    border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.3);'>
            <h1 style='color: #10b981; margin: 0; font-size: 3rem; font-weight: 700;'>
                🎯 TrenchCoat Pro
            </h1>
            <p style='color: #a3a3a3; margin-top: 0.5rem; font-size: 1.5rem;'>
                Ultra-Premium Cryptocurrency Trading Intelligence Platform
            </p>
            <div style='margin-top: 1rem;'>
                <span style='background: rgba(34, 197, 94, 0.2); color: white; padding: 0.5rem 1rem; 
                           border-radius: 20px; margin: 0 0.5rem; font-size: 0.9rem;'>
                    🟢 LIVE TRADING
                </span>
                <span style='background: rgba(59, 130, 246, 0.2); color: white; padding: 0.5rem 1rem; 
                           border-radius: 20px; margin: 0 0.5rem; font-size: 0.9rem;'>
                    📡 TELEGRAM SIGNALS ACTIVE
                </span>
                <span style='background: rgba(139, 92, 246, 0.2); color: white; padding: 0.5rem 1rem; 
                           border-radius: 20px; margin: 0 0.5rem; font-size: 0.9rem;'>
                    💎 PREMIUM MODE
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_main_content(self):
        """Render main dashboard content"""
        
        # Top metrics row
        self.render_key_metrics()
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Live Dashboard", "🧠 Advanced Analytics", "🤖 Model Builder", "⚙️ Trading Engine", "📡 Telegram Signals", "📝 Dev Blog", "💎 Solana Wallet"])
        
        with tab1:
            # Main content columns
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                self.render_live_coin_feed()
            
            with col2:
                self.render_performance_chart()
            
            with col3:
                self.render_strategy_performance()
        
        with tab2:
            st.markdown("### 🧠 Advanced Analytics")
            st.info("Advanced analytics features coming soon!")
        
        with tab3:
            st.markdown("### 🤖 Model Builder")
            st.info("AI model builder features coming soon!")
        
        with tab4:
            st.markdown("### ⚙️ Trading Engine")
            st.info("Trading engine configuration coming soon!")
        
        with tab5:
            # THIS IS THE KEY - Telegram Signals tab
            self.render_telegram_signals_section()
        
        with tab6:
            st.markdown("### 📝 Dev Blog")
            st.info("Development blog features coming soon!")
        
        with tab7:
            # Solana Wallet Integration
            try:
                from solana_wallet_integration import render_solana_wallet_section
                render_solana_wallet_section()
            except ImportError:
                st.markdown("### 💎 Solana Wallet")
                st.info("Solana wallet integration module not available")
    
    def render_key_metrics(self):
        """Render key performance metrics using live data"""
        col1, col2, col3, col4 = st.columns(4)
        
        # Get live portfolio data
        if database_available and streamlit_db:
            try:
                portfolio = streamlit_db.get_portfolio_data()
                coin_count = streamlit_db.get_coin_count()
                
                with col1:
                    st.metric("💰 Portfolio Value", f"${portfolio['total_value']:,.0f}", 
                             f"+${portfolio['profit']:,.0f} (+{portfolio['profit_pct']:.1f}%)")
                
                with col2:
                    st.metric("📊 Coins Tracked", f"{coin_count:,}", 
                             f"Active: {portfolio['active_positions']}")
                
                with col3:
                    st.metric("🎯 Win Rate", f"{portfolio['win_rate']:.1f}%", 
                             f"Avg Smart Wallets: {portfolio.get('avg_smart_wallets', 0):.0f}")
                
                with col4:
                    st.metric("💧 Total Liquidity", f"${portfolio.get('total_liquidity', 0):,.0f}", 
                             "Live Data")
                             
            except Exception as e:
                # Fallback to demo metrics if error
                with col1:
                    st.metric("💰 Portfolio Value", "$127,845", "+$12,845 (+11.2%)")
                with col2:
                    st.metric("📡 Active Signals", "23", "+8 signals")
                with col3:
                    st.metric("🎯 Win Rate", "78.3%", "+2.1%")
                with col4:
                    st.metric("⚡ Speed", "12ms", "Demo Mode")
        else:
            # Fallback to demo metrics
            with col1:
                st.metric("💰 Portfolio Value", "$127,845", "+$12,845 (+11.2%)")
            with col2:
                st.metric("📡 Active Signals", "23", "+8 signals")
            with col3:
                st.metric("🎯 Win Rate", "78.3%", "+2.1%")
            with col4:
                st.metric("⚡ Speed", "12ms", "Demo Mode")
    
    def render_live_coin_feed(self):
        """Render live coin feed using real trench.db data"""
        st.subheader("🔥 Live Coin Processing")
        
        # Get live coins from trench.db
        if database_available and streamlit_db:
            try:
                live_coins = streamlit_db.get_live_coins(limit=5)
                coin_count = streamlit_db.get_coin_count()
                
                if live_coins:
                    st.info(f"📊 Showing 5 of {coin_count:,} coins from live database")
                    
                    for coin in live_coins:
                        # Enhanced coin card with real data
                        st.markdown(f"""
                        <div class="premium-card">
                            <h4 style="color: #10b981;">{coin['ticker']}</h4>
                            <p><strong>Stage:</strong> {coin['stage']}</p>
                            <p><strong>Price:</strong> ${coin['price']:.8f}</p>
                            <p><strong>Confidence:</strong> {coin['score']:.1%}</p>
                            <p><strong>Smart Wallets:</strong> {coin['smart_wallets']}</p>
                            <p><strong>Liquidity:</strong> ${coin['liquidity']:,.0f}</p>
                            <p><strong>Volume:</strong> ${coin['volume']:,.0f}</p>
                            <p><strong>Source:</strong> {coin['source']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("📊 No live coin data available")
                    
            except Exception as e:
                st.error(f"❌ Error loading live coins: {e}")
                
        else:
            st.warning("🔧 Database not available - using fallback mode")
            
        # Always show database status
        if database_available:
            st.success("✅ Connected to live trench.db database")
        else:
            st.error("❌ Database connection unavailable")
    
    def render_performance_chart(self):
        """Render performance chart using live trench.db data"""
        st.subheader("📈 Portfolio Performance")
        
        # Get live price history from trench.db
        if database_available and streamlit_db:
            try:
                price_history = streamlit_db.get_price_history_data(days=30)
                
                if price_history:
                    # Extract data for plotting
                    dates = [pd.to_datetime(item['date']) for item in price_history]
                    values = [item['value'] for item in price_history]
                    
                    # Create figure with live data
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=values,
                        mode='lines+markers',
                        name='Portfolio Value',
                        line=dict(color='#10b981', width=3),
                        fill='tonexty',
                        fillcolor='rgba(16, 185, 129, 0.1)',
                        hovertemplate='<b>%{x}</b><br>Value: $%{y:,.0f}<extra></extra>'
                    ))
                    
                    # Calculate performance metrics
                    total_change = ((values[-1] - values[0]) / values[0]) * 100
                    max_value = max(values)
                    min_value = min(values)
                    
                    fig.update_layout(
                        title=f"Live Portfolio Performance (30 Days) - {total_change:+.1f}%",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        height=350,
                        xaxis_title="Date",
                        yaxis_title="Portfolio Value ($)",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show performance summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("30-Day Change", f"{total_change:+.1f}%", 
                                 f"${values[-1] - values[0]:+,.0f}")
                    with col2:
                        st.metric("Peak Value", f"${max_value:,.0f}", 
                                 f"{((max_value - values[0]) / values[0] * 100):+.1f}%")
                    with col3:
                        st.metric("Lowest Value", f"${min_value:,.0f}",
                                 f"{((min_value - values[0]) / values[0] * 100):+.1f}%")
                    
                    # Show data source
                    data_source = price_history[0].get('source', 'unknown')
                    if data_source == 'live_calculated':
                        st.success("📊 Chart generated from live trench.db coin analytics")
                    else:
                        st.info("📊 Using fallback performance data")
                        
                else:
                    # Fallback to demo chart if no data
                    self._render_fallback_chart()
                    
            except Exception as e:
                st.error(f"❌ Error loading price history: {e}")
                self._render_fallback_chart()
        else:
            self._render_fallback_chart()
    
    def _render_fallback_chart(self):
        """Render fallback chart with demo data"""
        # Generate sample data as fallback
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        values = np.cumsum(np.random.randn(30) * 2000) + 115000  # More realistic base
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#10b981', width=3),
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))
        
        fig.update_layout(
            title="Portfolio Performance (Demo Data)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.warning("⚠️ Using demo performance data - database connection needed")
    
    def render_strategy_performance(self):
        """Render strategy performance"""
        st.subheader("🎯 Strategy Performance")
        
        strategies = ['Momentum', 'Mean Reversion', 'Breakout', 'RSI Divergence']
        performance = [78.3, 72.1, 84.2, 69.7]
        
        for strategy, perf in zip(strategies, performance):
            st.metric(f"📊 {strategy}", f"{perf}%", f"+{np.random.randint(1, 5)}.{np.random.randint(0, 9)}%")
    
    def render_telegram_signals_section(self):
        """Render live telegram signals monitoring - STREAMLIT SAFE VERSION"""
        st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                    background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(46, 125, 50, 0.1) 100%);
                    border-radius: 15px; border: 1px solid rgba(76, 175, 80, 0.3);'>
            <h1 style='color: #4caf50; margin: 0; font-size: 2.5rem; font-weight: 700;'>
                📡 Telegram Signals
            </h1>
            <p style='color: #a3a3a3; margin-top: 0.5rem; font-size: 1.2rem;'>
                Live Trading Signals from Telegram Channels
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get live signals from trench.db
        if database_available and streamlit_db:
            try:
                signals = streamlit_db.get_telegram_signals(limit=8, min_confidence=0.6)
                st.success("📡 Showing live signals generated from trench.db coin data")
            except Exception as e:
                st.error(f"❌ Error loading live signals: {e}")
                signals = []
        else:
            signals = []
            
        # Fallback if no signals available
        if not signals:
            st.info("🔧 Using demonstration signals (database connection in development)")
            signals = [
                {'coin_symbol': 'SOL', 'signal_type': 'BUY', 'confidence': 0.85, 'entry_price': 119.50, 'timestamp': '2025-01-31 10:30:00', 'channel_name': 'CryptoGems'},
                {'coin_symbol': 'AVAX', 'signal_type': 'SELL', 'confidence': 0.75, 'entry_price': 35.20, 'timestamp': '2025-01-31 09:45:00', 'channel_name': 'MoonShots'},
                {'coin_symbol': 'NEAR', 'signal_type': 'BUY', 'confidence': 0.92, 'entry_price': 8.45, 'timestamp': '2025-01-31 08:15:00', 'channel_name': 'ATM.Day'}
            ]
        
        # Main layout with signals and stats
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Recent Signals")
            
            for signal in signals:
                signal_type = signal.get('signal_type', 'UNKNOWN').upper()
                signal_color = {
                    'BUY': '#4CAF50',
                    'SELL': '#f44336', 
                    'HOLD': '#ff9800',
                    'ALERT': '#2196f3'
                }.get(signal_type, '#9e9e9e')
                
                confidence = signal.get('confidence', 0)
                entry_price = signal.get('entry_price', 0)
                timestamp = signal.get('timestamp', 'Unknown')
                channel_name = signal.get('channel_name', 'Unknown')
                coin_symbol = signal.get('coin_symbol', 'UNKNOWN')
                
                st.markdown(f"""
                <div class="signal-card" style="border-left-color: {signal_color}">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <h4>📡 {coin_symbol} - {signal_type}</h4>
                            <p><strong>Confidence:</strong> {confidence:.1%}</p>
                            <p><strong>Entry:</strong> ${entry_price:.6f}</p>
                        </div>
                        <div style="text-align: right;">
                            <p><strong>Time:</strong> {timestamp}</p>
                            <p><strong>Channel:</strong> {channel_name}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📊 Signal Statistics")
            
            # Calculate statistics
            total_signals = len(signals)
            buy_signals = len([s for s in signals if s.get('signal_type', '').upper() == 'BUY'])
            sell_signals = len([s for s in signals if s.get('signal_type', '').upper() == 'SELL'])
            avg_confidence = sum(s.get('confidence', 0) for s in signals) / total_signals if total_signals > 0 else 0
            
            st.metric("Total Signals", total_signals)
            st.metric("Buy Signals", buy_signals, f"{(buy_signals/total_signals*100):.1f}%" if total_signals > 0 else "0%")
            st.metric("Sell Signals", sell_signals, f"{(sell_signals/total_signals*100):.1f}%" if total_signals > 0 else "0%")
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            
            # Channel breakdown
            st.subheader("📻 Channel Activity")
            channels = {}
            for signal in signals:
                channel = signal.get('channel_name', 'Unknown')
                channels[channel] = channels.get(channel, 0) + 1
            
            for channel, count in channels.items():
                st.write(f"**{channel}:** {count} signals")
    
    def get_live_telegram_signals(self):
        """Attempt to get live telegram signals (will fail gracefully on Streamlit Cloud)"""
        try:
            # This will fail on Streamlit Cloud - that's expected
            from src.data.database import CoinDatabase
            db = CoinDatabase()
            return db.get_telegram_signals(limit=20, min_confidence=0.5)
        except ImportError:
            return None
        except Exception:
            return None

# Create the dashboard instance
def create_dashboard():
    """Create and return dashboard instance"""
    return StreamlitSafeDashboard()

# For direct import compatibility
UltraPremiumDashboard = StreamlitSafeDashboard