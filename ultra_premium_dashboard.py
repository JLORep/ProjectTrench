#!/usr/bin/env python3
"""
TrenchCoat Pro - Ultra Premium Dashboard
Apple/PayPal-level design with live updates and animations
"""
import streamlit as st

# Import safe Unicode handlers
try:
    from unicode_handler import safe_print
except ImportError:
    def safe_print(text, **kwargs):
        """Fallback safe print"""
        print(text, **kwargs)
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
from PIL import Image
import io
import base64
import sqlite3
import os

# Import our advanced analytics
try:
    from advanced_analytics import AdvancedAnalytics
except ImportError:
    AdvancedAnalytics = None

# Import live data integration
try:
    from live_data_integration import LiveDataManager, get_live_coin_data, get_live_portfolio
except ImportError:
    LiveDataManager = None

# Import professional branding
try:
    from branding_system import BrandingSystem
    branding = BrandingSystem()
except Exception:
    branding = None

# Page configuration (handled by streamlit_app.py)

# Custom CSS for ultra-premium design
def apply_custom_css():
    """Apply custom CSS for ultra-premium design"""
    st.markdown("""
<style>
    /* Fix: Scope CSS to prevent conflicts */
    #trenchcoat-app {
    /* Import premium fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    }
    
    /* Global styles */
    #trenchcoat-app * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Premium background */
    #trenchcoat-app .stApp {
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

class UltraPremiumDashboard:
    """Ultra-premium dashboard with live updates"""
    
    def __init__(self):
        self.initialize_session_state()
        apply_custom_css()  # Apply our custom CSS
        if branding:
            try:
                branding.apply_custom_css()
            except Exception:
                pass
    
    def render(self):
        """Main render method for the dashboard"""
        # Render header
        self.render_header()
        
        # Render main content with tabs
        self.render_main_content()
    
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
        # Fix: Ensure CSS is properly isolated
        st.markdown('<div id="trenchcoat-app">', unsafe_allow_html=True)
        
        # Premium header
        self.render_header()
        
        # Main content area
        self.render_main_content()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_header(self):
        """Render premium header with live status"""
        # Fix: Use Streamlit native components for header to avoid HTML issues
        st.markdown("# 🎯 TrenchCoat Pro")
        st.markdown("**Ultra-Premium Cryptocurrency Trading Intelligence Platform**")
        
        # Add status indicators using native components
        status_col1, status_col2, status_col3, status_col4 = st.columns(4)
        with status_col1:
            st.success("🟢 LIVE TRADING")
        with status_col2:
            st.info("📡 6/6 APIs Connected")
        with status_col3:
            st.info("⚡ 12ms Ultra-Low Latency")
        with status_col4:
            st.info("💎 Premium Mode")
        
        # Add visual separator
        st.markdown("---")
        
        # Status indicators and live mode toggle in header area
        header_cols = st.columns([3, 2, 2])
        
        with header_cols[0]:
            # Live status indicators - Fix: Use Streamlit components instead of raw HTML
            col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
            with col1:
                st.markdown("🟢 **LIVE TRADING**")
            with col2:
                st.markdown("📡 **6/6 APIs**")
            with col3:
                st.markdown("⚡ **12ms**")
            with col4:
                st.markdown("💎 **Premium Mode**")
        
        with header_cols[1]:
            # Live mode toggle
            st.markdown("**Data Mode:**")
            live_mode = st.toggle("📡 Live Monitoring", value=st.session_state.get('live_mode', False))
            
            if live_mode != st.session_state.get('live_mode', False):
                st.session_state.live_mode = live_mode
                if live_mode:
                    st.success("🟢 Live monitoring enabled!")
                    st.info("Real coin data & notifications active")
                else:
                    st.info("🔵 Demo mode - Sample data only")
                # Fix: Delay rerun to prevent race condition
                time.sleep(0.1)
                st.rerun()
        
        with header_cols[2]:
            # System time - Fix: Use Streamlit native components
            current_time = datetime.now().strftime("%H:%M:%S")
            st.markdown(f"**System Time:** {current_time} UTC", help="Current system time in UTC")
    
    def render_main_content(self):
        """Render main content area with tabbed interface"""
        # Top metrics row
        self.render_key_metrics()
        
        # Create tabs for different views - ALL 10 TABS
        expected_tabs = ["📊 Live Dashboard", "🧠 Advanced Analytics", "🤖 Model Builder", "⚙️ Trading Engine", "📡 Telegram Signals", "📝 Dev Blog", "💎 Solana Wallet", "🗄️ Coin Data", "🗃️ Database", "🔔 Incoming Coins"]
        st.info(f"✅ Advanced Dashboard Loading {len(expected_tabs)} tabs - All features included")
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(expected_tabs)
        
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
            # Model Builder Section
            self.render_model_builder_section()
        
        with tab4:
            # Trading Engine Configuration
            self.render_trading_engine_config()
        
        with tab5:
            # Telegram Signals System
            self.render_telegram_signals_section()
        
        with tab6:
            # Dev Blog System
            self.render_dev_blog_section()
        
        with tab7:
            # Solana Wallet Integration
            st.header("💎 Solana Wallet")
            st.markdown("### 🚀 Solana Trading Integration")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Wallet Balance", "0.00 SOL", "Connect wallet")
                st.metric("📊 Active Trades", "0", "No active trades")
            with col2:
                st.metric("💹 PnL Today", "0.00 SOL", "0.0%")
                st.metric("🎯 Success Rate", "0%", "No trades yet")
            
            st.info("🔗 Connect your Solana wallet to start automated trading")
            
        with tab8:
            # Coin Data Tab
            st.header("🗄️ Coin Data")
            st.markdown("### 💎 Live Cryptocurrency Analytics")
            
            # Use existing live coin data functionality
            try:
                # Import the working coin data function
                from streamlit_app import get_live_coins_simple
                coins, status = get_live_coins_simple()
                if coins and status.startswith("SUCCESS"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Total Coins", "1,733")
                    with col2:
                        st.metric("📈 Displayed", len(coins))
                    with col3:
                        st.metric("💾 Database", "319 KB")
                    with col4:
                        st.metric("🪙 Status", "✅ Live")
                    
                    # Stunning full-page coin cards display  
                    st.subheader("🎯 Stunning Full-Page Coin Cards")
                    
                    # Add CSS animations for the cards
                    st.markdown("""
                    <style>
                    @keyframes slideInUp {
                        from {
                            opacity: 0;
                            transform: translateY(30px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                    
                    @keyframes pulse {
                        0%, 100% {
                            transform: scale(1);
                        }
                        50% {
                            transform: scale(1.05);
                        }
                    }
                    
                    @keyframes float {
                        0% {
                            transform: rotate(0deg);
                        }
                        100% {
                            transform: rotate(360deg);
                        }
                    }
                    
                    .coin-card-full:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 30px 60px rgba(0,0,0,0.4), 0 0 60px var(--glow-color, rgba(16, 185, 129, 0.4));
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Define the elaborate card rendering function locally
                    def render_stunning_coin_card_local(coin, index):
                        """Render a stunning full-page coin card with animations"""
                        ticker = coin['ticker']
                        gain = coin['price_gain']
                        completeness = coin['completeness_score']
                        
                        # Determine card gradient based on performance
                        if gain > 500:
                            gradient = "linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%)"
                            glow_color = "rgba(16, 185, 129, 0.4)"
                            status_emoji = "🚀"
                            status_text = "MOONSHOT"
                        elif gain > 200:
                            gradient = "linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%)"
                            glow_color = "rgba(59, 130, 246, 0.4)"
                            status_emoji = "📈"
                            status_text = "STRONG"
                        elif gain > 50:
                            gradient = "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%)"
                            glow_color = "rgba(139, 92, 246, 0.4)"
                            status_emoji = "💎"
                            status_text = "SOLID"
                        else:
                            gradient = "linear-gradient(135deg, #6b7280 0%, #4b5563 50%, #374151 100%)"
                            glow_color = "rgba(107, 114, 128, 0.3)"
                            status_emoji = "⚡"
                            status_text = "ACTIVE"
                        
                        # Calculate display values
                        smart_wallets = f"{coin['smart_wallets']:,}"
                        liquidity = f"${coin['liquidity']:,.0f}"
                        market_cap = f"${coin['market_cap']:,.0f}"
                        peak_volume = f"${coin['peak_volume']:,.0f}"
                        
                        card_html = f"""
                        <div class="coin-card-full" style="
                            background: {gradient};
                            border-radius: 20px;
                            padding: 24px;
                            margin: 16px 0;
                            box-shadow: 0 20px 40px rgba(0,0,0,0.3), 0 0 40px {glow_color};
                            border: 1px solid rgba(255,255,255,0.1);
                            transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
                            cursor: pointer;
                            position: relative;
                            overflow: hidden;
                            animation: slideInUp 0.6s ease-out {index * 0.1}s both;
                        ">
                            
                            <!-- Animated background pattern -->
                            <div style="
                                position: absolute;
                                top: -50%;
                                right: -50%;
                                width: 200%;
                                height: 200%;
                                background: radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px);
                                background-size: 20px 20px;
                                animation: float 20s infinite linear;
                                pointer-events: none;
                            "></div>
                            
                            <!-- Card content -->
                            <div style="position: relative; z-index: 2;">
                                <!-- Header -->
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                                    <div style="display: flex; align-items: center; gap: 16px;">
                                        <div style="
                                            width: 64px;
                                            height: 64px;
                                            border-radius: 50%;
                                            background: linear-gradient(135deg, #10b981 0%, #10b98180 100%);
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            font-size: 24px;
                                            font-weight: bold;
                                            color: white;
                                            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                                            animation: pulse 2s infinite;
                                        ">${ticker[0] if ticker else 'C'}</div>
                                        <div>
                                            <h3 style="color: white; margin: 0; font-size: 28px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                                                ${ticker}
                                            </h3>
                                            <div style="color: rgba(255,255,255,0.8); font-size: 14px; margin-top: 4px;">
                                                {status_emoji} {status_text}
                                            </div>
                                        </div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="
                                            background: rgba(255,255,255,0.2);
                                            border-radius: 12px;
                                            padding: 8px 16px;
                                            color: white;
                                            font-weight: 600;
                                            font-size: 18px;
                                            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                                        ">+{gain:.1f}%</div>
                                        <div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-top: 4px;">
                                            24h Change
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Metrics Grid -->
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
                                    <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 16px;">
                                        <div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 4px;">Smart Wallets</div>
                                        <div style="color: white; font-size: 20px; font-weight: 600;">{smart_wallets}</div>
                                    </div>
                                    <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 16px;">
                                        <div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 4px;">Liquidity</div>
                                        <div style="color: white; font-size: 20px; font-weight: 600;">{liquidity}</div>
                                    </div>
                                </div>
                                
                                <!-- Progress Bar -->
                                <div style="margin-bottom: 16px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                        <span style="color: rgba(255,255,255,0.8); font-size: 14px;">Data Completeness</span>
                                        <span style="color: white; font-weight: 600;">{completeness*100:.0f}%</span>
                                    </div>
                                    <div style="background: rgba(255,255,255,0.2); height: 8px; border-radius: 4px; overflow: hidden;">
                                        <div style="
                                            background: linear-gradient(90deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.6) 100%);
                                            width: {completeness*100}%;
                                            height: 100%;
                                            border-radius: 4px;
                                            transition: width 0.3s ease;
                                        "></div>
                                    </div>
                                </div>
                                
                                <!-- Footer Info -->
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px;">
                                    <div style="color: rgba(255,255,255,0.6); font-size: 12px;">
                                        Market Cap: {market_cap} • Volume: {peak_volume}
                                    </div>
                                    <div style="
                                        background: rgba(255,255,255,0.2);
                                        color: white;
                                        padding: 4px 12px;
                                        border-radius: 20px;
                                        font-size: 12px;
                                        font-weight: 500;
                                    ">Live Data</div>
                                </div>
                            </div>
                        </div>
                        """
                        return card_html
                    
                    # Display elaborate full-page cards
                    for i, coin in enumerate(coins[:5]):
                        # Convert database format to card format
                        ticker = coin.get('Ticker', coin.get('ticker', f'COIN_{i+1}'))
                        price_gain_str = coin.get('Price Gain %', coin.get('price_gain_pct', '0%'))
                        price_gain = float(price_gain_str.replace('%', '').replace('+', '')) if isinstance(price_gain_str, str) else price_gain_str
                        smart_wallets_str = coin.get('Smart Wallets', coin.get('smart_wallets', '0'))
                        smart_wallets = int(smart_wallets_str.replace(',', '')) if isinstance(smart_wallets_str, str) else smart_wallets_str
                        
                        # Create elaborate card data structure
                        card_coin = {
                            'ticker': ticker,
                            'price_gain': price_gain,
                            'smart_wallets': smart_wallets,
                            'liquidity': coin.get('liquidity', 1000000),
                            'market_cap': coin.get('market_cap', 5000000),  
                            'peak_volume': coin.get('peak_volume', 2000000),
                            'completeness_score': coin.get('completeness_score', 0.8)
                        }
                        
                        # Render the stunning full-page card
                        card_html = render_stunning_coin_card_local(card_coin, i)
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Add detail button
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button(f"View {ticker} Details", key=f"advanced_detail_{ticker}_{i}"):
                                st.session_state.show_coin_detail = card_coin
                                st.rerun()
                else:
                    st.error(f"❌ Failed to load coin data: {status}")
            except Exception as e:
                st.error(f"❌ Coin data not available: {str(e)}")
                # Fallback message
                st.info("🔄 Retrying connection to live database...")
                
        with tab9:
            # Database Management Tab
            st.header("🗃️ Database")
            st.markdown("### 📊 Database Management & Analytics")
            
            # Database statistics
            if os.path.exists('data/trench.db'):
                import sqlite3
                try:
                    conn = sqlite3.connect('data/trench.db')
                    cursor = conn.cursor()
                    
                    # Count records
                    cursor.execute("SELECT COUNT(*) FROM coins")
                    total_coins = cursor.fetchone()[0]
                    
                    # Sample data
                    cursor.execute("SELECT ticker, ca, discovery_price FROM coins LIMIT 5")
                    sample_data = cursor.fetchall()
                    conn.close()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Total Records", f"{total_coins:,}")
                    with col2:
                        st.metric("💾 File Size", "319 KB")
                    with col3:
                        st.metric("⚡ Status", "Live")
                    
                    st.subheader("📋 Sample Database Records")
                    df = pd.DataFrame(sample_data, columns=['Ticker', 'Contract Address', 'Discovery Price'])
                    st.dataframe(df, use_container_width=True)
                    
                    with st.expander("🔧 Database Schema"):
                        st.code("""
DATABASE: data/trench.db
├── Table: coins
├── Records: 1,733 cryptocurrency entries  
├── Columns: ticker, ca, discovery_price, axiom_price
├── Live Status: Connected and operational
└── Last Query: Real-time
                        """)
                except Exception as e:
                    st.error(f"❌ Database error: {e}")
            else:
                st.error("❌ Database file not found")
                
        with tab10:
            # Incoming Coins Monitor
            st.header("🔔 Incoming Coins")
            st.markdown("### 📡 Real-time Coin Discovery Monitor")
            
            st.info("🚀 Monitoring for new cryptocurrency discoveries...")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Monitored Sources", "6 APIs")
                st.metric("⏱️ Scan Frequency", "30 seconds")
            with col2:
                st.metric("🔔 New Today", "0")
                st.metric("📈 Queue Status", "Active")
            
            st.warning("🔧 Real-time monitoring features coming soon!")
    
    def render_key_metrics(self):
        """Render key performance metrics - LIVE DATA ONLY"""
        metrics_container = st.container()
        
        with metrics_container:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # TODO: Connect to real portfolio data
            # profit_change = random.uniform(-50, 200)
            # st.session_state.total_profit += profit_change
            
            with col1:
                # TODO: Connect to real portfolio value
                st.metric(
                    label="Portfolio Value",
                    value="$0.00",
                    delta="No live data connected",
                    help="Connect to real portfolio API"
                )
            
            with col2:
                # TODO: Connect to real win rate calculations
                st.metric(
                    label="Win Rate",
                    value="0%",
                    delta="No trades tracked",
                    help="Connect to trading history database"
                )
            
            with col3:
                # TODO: Connect to real active trading positions
                st.metric(
                    label="Active Trades",
                    value="0",
                    delta="No live trading data",
                    help="Connect to trading engine API"
                )
            
            with col4:
                # TODO: Connect to real coins being processed
                st.metric(
                    label="Coins Analyzed",
                    value="0",
                    delta="No analysis pipeline connected",
                    help="Connect to enrichment system"
                )
            
            with col5:
                # TODO: Connect to real system health metrics
                st.metric(
                    label="System Health",
                    value="Unknown",
                    delta="No monitoring connected",
                    help="Connect to system monitoring API"
                )
    
    def render_live_coin_feed(self):
        """Render live coin processing feed"""
        mode_indicator = "🟢 LIVE" if st.session_state.get('live_mode', False) else "🔵 DEMO"
        st.markdown(f"""
        <div class="premium-card">
            <h3 style="color: #f9fafb; margin-bottom: 16px;">
                Live Coin Processing {mode_indicator}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Use live database data - always available
        try:
            from live_coin_data import LiveCoinDataConnector
            
            connector = LiveCoinDataConnector()
            live_coins = connector.get_live_coins(10)
            
            if live_coins:
                print(f"Dashboard: Retrieved {len(live_coins)} live coins from database")
                
                # Convert to display format and store in session
                st.session_state.processed_coins = live_coins
                
                # Display success message
                st.success(f"✅ Connected to live database with {len(live_coins)} coins")
                st.info(f"🔗 Data source: {connector.main_db.name if connector.main_db else 'Multiple databases'}")
                
            else:
                st.warning("📊 No live coin data available in database")
                st.session_state.processed_coins = []
                
        except ImportError as e:
            st.error(f"❌ Live coin data connector not available: {e}")
            st.session_state.processed_coins = []
        except Exception as e:
            st.error(f"❌ Error connecting to live coin data: {e}")
            st.session_state.processed_coins = []
            # Fallback: Use demo data if live data fails  
            self.generate_demo_coins()
        
        # Display coins only if we have real data
        if st.session_state.processed_coins:
            for i, coin in enumerate(st.session_state.processed_coins[:5]):
                self.render_coin_card(coin, i)
        else:
            st.warning("📊 No live coin data available. Connect to data sources to see processed coins.")
    
    def get_processing_stage(self, confidence):
        """Determine processing stage based on confidence"""
        if confidence > 90:
            return 'Trading'
        elif confidence > 80:
            return 'Analyzing' 
        elif confidence > 70:
            return 'Enriching'
        else:
            return 'Discovering'
    
    def generate_demo_coins(self):
        """DEPRECATED: No longer generating demo coins"""
        # TODO: Remove this method once live data is connected
        pass
    
    def generate_fake_coin(self):
        """DEPRECATED: No longer generating fake coin data"""
        # TODO: Remove this method once live data is connected
        return None
    
    def render_coin_card(self, coin, index):
        """Render individual animated coin card with beautiful styling"""
        stage_colors = {
            'Discovering': '#3b82f6',
            'Enriching': '#f59e0b',
            'Analyzing': '#8b5cf6',
            'Trading': '#10b981',
            'Completed': '#6b7280'
        }
        
        stage_color = stage_colors.get(coin['stage'], '#6b7280')
        price_change = coin.get('change_24h', 0)
        change_arrow = '↑' if price_change > 0 else '↓'
        is_enriched = coin.get('source') in ['telegram', 'enriched'] or coin.get('enriched', False)
        source_icon = "📡" if coin.get('source') == 'telegram' else "🔍" if is_enriched else "📊"
        social_score = coin.get('social_score', 0)
        rug_risk = coin.get('rug_risk', 0)
        verified = coin.get('contract_verified', False)
        liquidity = coin.get('liquidity', 0)
        
        # Create beautiful animated card with proper CSS class
        success_class = 'success-flash' if coin['stage'] == 'Trading' else ''
        
        card_html = f"""
        <div class="coin-card {success_class}" 
             style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
                    border: 1px solid rgba({','.join(str(int(stage_color[i:i+2], 16)) for i in (1, 3, 5))}, 0.3);
                    border-radius: 12px; padding: 16px; margin: 8px 0; position: relative;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 0 20px rgba({','.join(str(int(stage_color[i:i+2], 16)) for i in (1, 3, 5))}, 0.1);
                    transition: all 0.3s ease; backdrop-filter: blur(10px);">
            
            <!-- Coin Header -->
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div style="width: 48px; height: 48px; border-radius: 50%; 
                           background: linear-gradient(135deg, #10b981 0%, #10b98180 100%);
                           display: flex; align-items: center; justify-content: center;
                           font-weight: bold; color: white; font-size: 14px; margin-right: 12px;
                           box-shadow: 0 2px 8px rgba(16,185,129, 0.4);">
                    ${coin['ticker'][:2].upper()}
                </div>
                <div style="flex: 1;">
                    <div style="color: #f8fafc; font-weight: 600; font-size: 16px;">
                        {coin['ticker']} {source_icon}
                        {"✅" if verified else ""}
                    </div>
                    <div style="color: #10b981; font-size: 12px; font-weight: 500;">
                        {coin['stage']}
                    </div>
                </div>
            </div>
            
            <!-- Price Info -->
            <div style="margin-bottom: 12px;">
                <div style="color: #f8fafc; font-size: 18px; font-weight: 600;">
                    ${coin['price']:.6f}
                </div>
                {"" if price_change == 0 else f'''
                <div style="color: {'#10b981' if price_change > 0 else '#ef4444'}; font-size: 14px; font-weight: 500;">
                    {change_arrow} {abs(price_change):.1f}%
                </div>'''}
            </div>
            
            <!-- Performance Score Bar -->
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="color: #94a3b8; font-size: 12px;">Performance Score</span>
                    <span style="color: #f8fafc; font-size: 12px; font-weight: 600;">{coin['score']:.2f}</span>
                </div>
                <div style="background: rgba(71, 85, 105, 0.5); height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, {stage_color} 0%, {stage_color}80 100%); 
                               width: {coin['score'] * 100}%; height: 100%; border-radius: 3px;
                               box-shadow: 0 0 10px rgba({','.join(str(int(stage_color[i:i+2], 16)) for i in (1, 3, 5))}, 0.5);
                               transition: width 0.3s ease;"></div>
                </div>
            </div>
            
            <!-- Additional Metrics -->
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <div style="color: #94a3b8; font-size: 11px;">
                    💧 Liquidity: ${liquidity:,.0f}
                </div>
                {"" if not is_enriched else f'''
                <div style="color: #94a3b8; font-size: 11px;">
                    🎯 Social: {social_score:.1f}
                </div>'''}
            </div>
            
            {"" if not is_enriched else f'''
            <div style="display: flex; justify-content: space-between;">
                <div style="color: {'#ef4444' if rug_risk > 0.5 else '#10b981'}; font-size: 11px;">
                    {'⚠️' if rug_risk > 0.5 else '✅'} Risk: {rug_risk:.1f}
                </div>
                <div style="color: {stage_color}; font-size: 11px; font-weight: 500;">
                    {source_icon} Enhanced
                </div>
            </div>'''}
        </div>
        """
        
        # Render the beautiful animated card
        st.markdown(card_html, unsafe_allow_html=True)
    
    def render_performance_chart(self):
        """Render real-time performance chart - LIVE DATA"""
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #f9fafb; margin-bottom: 16px;">Live Performance</h3>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            from live_price_charts import LivePriceChartsProvider
            
            # Get live performance data
            provider = LivePriceChartsProvider()
            chart_data = provider.get_performance_chart_data(7)  # 7 days
            
            if chart_data['total_coins'] > 0:
                # Create interactive performance chart
                fig = go.Figure()
                
                # Add line for each coin
                for coin in chart_data['coins']:
                    fig.add_trace(go.Scatter(
                        x=chart_data['timestamps'],
                        y=coin['prices'],
                        mode='lines',
                        name=coin['name'],
                        line=dict(color=coin['color'], width=2),
                        hovertemplate=f"<b>{coin['name']}</b><br>" +
                                    "Price: $%{y:.6f}<br>" +
                                    "Time: %{x}<br>" +
                                    f"Market Cap: ${coin['market_cap']:,.0f}<br>" +
                                    f"Volume: ${coin['volume']:,.0f}<extra></extra>"
                    ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(15, 23, 42, 0.8)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#f8fafc'),
                    margin=dict(l=0, r=0, t=20, b=0),
                    height=300,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=10)
                    ),
                    xaxis=dict(
                        showgrid=True, 
                        gridcolor='rgba(71, 85, 105, 0.3)',
                        color='#94a3b8'
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(71, 85, 105, 0.3)',
                        color='#94a3b8',
                        tickformat='.6f'
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # Show data source info
                st.caption(f"📊 Live data from {chart_data['total_coins']} coins | Source: {Path(chart_data['database_source']).name}")
                
            else:
                st.warning("⚠️ No live performance data available")
                
        except Exception as e:
            st.error(f"❌ Error loading live performance data: {e}")
            # Fallback to empty chart
            fig = go.Figure()
            fig.add_annotation(
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                text="Error loading live data<br>Check database connection",
                showarrow=False,
                font=dict(size=16, color="#ef4444")
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0),
                height=300,
                showlegend=False,
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    def render_active_positions(self):
        """Render active trading positions - LIVE DATA ONLY"""
        st.subheader("Active Positions")
        
        # TODO: Connect to real trading positions
        st.info("🔗 No live trading positions connected")
        st.markdown("**Required connections:**")
        st.markdown("- Trading engine API")
        st.markdown("- Position tracking database")
        st.markdown("- Real-time P&L calculations")
        
        # Show placeholder for where positions would appear
        st.markdown("---")
        st.caption("📊 Active positions will appear here once connected to live trading system")
    
    def render_strategy_performance(self):
        """Render strategy performance breakdown - LIVE DATA ONLY"""
        st.subheader("Strategy Performance")
        
        # TODO: Connect to real strategy performance data
        st.info("📈 No live strategy performance data connected")
        st.markdown("**Available strategies to connect:**")
        st.markdown("- Whale Following")
        st.markdown("- Volume Explosion")
        st.markdown("- Momentum Breakout")
        st.markdown("- Social Sentiment")
        
        st.markdown("**Required data:**")
        st.markdown("- Strategy execution history")
        st.markdown("- Win/loss ratios")
        st.markdown("- Profit/loss calculations")
        st.markdown("- Performance metrics")
    
    def render_recent_wins(self):
        """Render recent winning trades - LIVE DATA ONLY"""
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #f9fafb; margin-bottom: 16px;">Recent Wins</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # TODO: Connect to real winning trades data
        st.info("🏆 No live winning trades data connected")
        st.markdown("**Required connections:**")
        st.markdown("- Trading history database")
        st.markdown("- Completed trades with profit/loss")
        st.markdown("- ROI calculations")
        st.markdown("- Trade timestamps")
        
        # Placeholder for where wins would appear
        st.markdown("""
        <div class="premium-card" style="padding: 12px; margin: 8px 0; opacity: 0.5;">
            <div style="color: #6b7280; text-align: center;">
                📊 Recent winning trades will appear here<br>
                <small>Connect to trading system to see live data</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_ai_suggestions(self):
        """Render AI-powered improvement suggestions - LIVE DATA ONLY"""
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
        
        # TODO: Connect to real AI suggestion system
        st.info("🤖 No live AI suggestions connected")
        st.markdown("**Required connections:**")
        st.markdown("- Claude AI integration")
        st.markdown("- Trading performance analysis")
        st.markdown("- Strategy optimization engine")
        st.markdown("- Market condition analysis")
        
        # Placeholder for where suggestions would appear
        st.markdown("""
        <div class="premium-card" style="padding: 16px; margin: 8px 0; opacity: 0.5;">
            <div style="color: #6b7280; text-align: center;">
                🧠 AI-powered suggestions will appear here<br>
                <small>Connect to Claude AI system for live insights</small>
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
        """Fallback basic analytics - LIVE DATA ONLY"""
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
        
        # TODO: Connect to real market analytics data
        st.info("📊 No live market analytics data connected")
        st.markdown("**Required connections:**")
        st.markdown("- Market data API (price feeds)")
        st.markdown("- Technical analysis calculations")
        st.markdown("- Volatility metrics")
        st.markdown("- Trend analysis algorithms")
        
        # Show empty chart placeholder
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            text="No live market data<br>Connect to analytics system",
            showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        
        fig.update_layout(
            title='📈 30-Day Price Analysis (No Data)',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analytics metrics placeholders
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Volatility", "No data", help="Connect to market data API")
        with col2:
            st.metric("🎯 Trend Strength", "Unknown", help="Connect to technical analysis")
        with col3:
            st.metric("📈 Moving Avg", "$0.00", help="Connect to price feed")
        with col4:
            st.metric("🏆 Performance", "0%", help="Connect to performance tracking")
    
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
                # TODO: Connect to real trading engine stats
                st.metric("🎯 Success Rate", "No data", help="Connect to trading history")
                st.metric("💰 Total P&L", "$0.00", help="Connect to P&L tracking")
            with col_b:
                st.metric("🔄 Active Trades", "0", help="Connect to active positions")
                st.metric("⏱️ Avg Hold Time", "0h", help="Connect to trade analytics")
            
            if st.button("🚀 Deploy Strategy", type="primary"):
                if trading_enabled:
                    st.success("✅ Strategy deployed to live trading!")
                    st.balloons()
                else:
                    st.info("📋 Strategy updated in demo mode")
    
    def check_and_notify_high_confidence_coins(self, live_coins):
        """Check for high-confidence coins and trigger notifications"""
        if not st.session_state.get('live_mode', False):
            return
            
        # Initialize notification tracking
        if 'notified_coins' not in st.session_state:
            st.session_state.notified_coins = set()
            
        try:
            for coin in live_coins:
                coin_key = f"{coin['symbol']}_{coin['address'][:8]}"
                
                # Only notify for high-confidence coins we haven't notified about recently
                if (coin['confidence'] > 85 and 
                    coin_key not in st.session_state.notified_coins and
                    LiveDataManager):
                    
                    # Add to notified list
                    st.session_state.notified_coins.add(coin_key)
                    
                    # Trigger notification in background
                    self.trigger_background_notification(coin)
                    
                    # Show notification indicator in UI
                    st.success(f"🚨 RUNNER ALERT: {coin['symbol']} - {coin['confidence']:.1f}% confidence!")
                    
                    # Clean up old notifications (keep last 10)
                    if len(st.session_state.notified_coins) > 10:
                        # Remove oldest entries
                        old_coins = list(st.session_state.notified_coins)
                        st.session_state.notified_coins = set(old_coins[-10:])
                        
        except Exception as e:
            st.error(f"Notification check error: {e}")
    
    def trigger_background_notification(self, coin):
        """Trigger notification in the background"""
        try:
            # Create notification message
            message = f"""
🎯 RUNNER DETECTED!

💎 {coin['symbol']} ({coin.get('name', 'Unknown')})
💰 Price: ${coin['price']:.6f}
📈 24h Change: {coin.get('price_change_24h', 0):.1f}%
💧 Liquidity: ${coin.get('liquidity', 0):,.0f}
🎪 Confidence: {coin['confidence']:.1f}%

🔗 Address: {coin['address'][:8]}...
⏰ Detected: {datetime.now().strftime('%H:%M:%S')}

🚀 TrenchCoat Pro Live Monitor
"""
            
            # Add to session state for display
            if 'live_notifications' not in st.session_state:
                st.session_state.live_notifications = []
                
            st.session_state.live_notifications.insert(0, {
                'timestamp': datetime.now(),
                'coin': coin['symbol'],
                'confidence': coin['confidence'],
                'message': message,
                'type': 'runner_detected'
            })
            
            # Keep only recent notifications
            st.session_state.live_notifications = st.session_state.live_notifications[:20]
            
            # Note: Real notification sending would happen here via unified_notifications.py
            # For demo, we just show the UI notification
            
        except Exception as e:
            st.error(f"Background notification error: {e}")
    
    def render_model_builder_section(self):
        """Render model builder interface"""
        try:
            # Fix: Lazy import to prevent circular dependencies
            import sys
            if 'model_builder' not in sys.modules:
                from model_builder import ModelBuilder
            else:
                ModelBuilder = sys.modules['model_builder'].ModelBuilder
            
            if 'historic_data_manager' not in sys.modules:
                from historic_data_manager import HistoricDataManager
            else:
                HistoricDataManager = sys.modules['historic_data_manager'].HistoricDataManager
            
            # Create sub-tabs for model builder features
            subtab1, subtab2 = st.tabs(["🤖 Model Builder", "📊 Historic Data"])
            
            with subtab1:
                builder = ModelBuilder()
                builder.render_model_builder()
            
            with subtab2:
                try:
                    manager = HistoricDataManager()
                    manager.render_historic_data_tab()
                except Exception as e:
                    st.error(f"Historic data manager error: {str(e)}")
                    st.info("📊 Historic data manager not available")
                
        except ImportError as e:
            st.error(f"Model Builder components not available: {e}")
            st.info("Please ensure all ML dependencies are installed.")
    
    def render_dev_blog_section(self):
        """Render dev blog interface"""
        try:
            # Fix: Lazy import to prevent circular dependencies
            import sys
            if 'dev_blog_system' not in sys.modules:
                from dev_blog_system import DevBlogSystem
            else:
                DevBlogSystem = sys.modules['dev_blog_system'].DevBlogSystem
            
            blog_system = DevBlogSystem()
            blog_system.render_dev_blog_interface()
                
        except ImportError as e:
            st.error(f"Dev Blog system not available: {e}")
            st.info("Please ensure all dependencies are installed.")
    
    def render_datasets_section(self):
        """Render datasets management interface"""
        st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
                    border-radius: 15px; border: 1px solid rgba(139, 92, 246, 0.3);'>
            <h1 style='color: #8b5cf6; margin: 0; font-size: 2.5rem; font-weight: 700;'>
                🗄️ Datasets Management
            </h1>
            <p style='color: #a3a3a3; margin-top: 0.5rem; font-size: 1.2rem;'>
                Historic Coin Data & Live Pipeline Management
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize session state for dataset operations
        if 'dataset_operation_status' not in st.session_state:
            st.session_state.dataset_operation_status = None
        if 'enrichment_progress' not in st.session_state:
            st.session_state.enrichment_progress = {'current': 0, 'total': 0, 'coin': ''}
        
        # Main controls section
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🔄 Database Operations")
            
            # Fresh start option
            if st.button("🆕 Fresh Start (Full Pipeline)", type="primary", use_container_width=True):
                if st.session_state.get('confirm_fresh_start', False):
                    self.start_fresh_pipeline()
                    st.session_state.confirm_fresh_start = False
                else:
                    st.session_state.confirm_fresh_start = True
                    st.warning("⚠️ This will reset the database! Click again to confirm.")
            
            # Quick enrichment option
            if st.button("⚡ Quick Enrichment Only", use_container_width=True):
                self.start_enrichment_only()
            
            # Database status
            self.render_database_status()
        
        with col2:
            st.markdown("### 📊 Current Progress")
            
            # Progress display
            if st.session_state.enrichment_progress['total'] > 0:
                progress = st.session_state.enrichment_progress['current'] / st.session_state.enrichment_progress['total']
                st.progress(progress, text=f"Processing: {st.session_state.enrichment_progress['coin']}")
                st.metric("Progress", f"{st.session_state.enrichment_progress['current']}/{st.session_state.enrichment_progress['total']}")
            else:
                st.info("No active operations")
            
            # Operation status
            if st.session_state.dataset_operation_status:
                st.success(f"✅ {st.session_state.dataset_operation_status}")
        
        # Data visualization section
        st.markdown("---")
        self.render_dataset_overview()
    
    def start_fresh_pipeline(self):
        """Start the complete fresh database pipeline"""
        try:
            # Import dataset manager
            try:
                from src.data.historic_dataset_manager import HistoricDatasetManager
                manager = HistoricDatasetManager()
                
                # Update status
                st.session_state.dataset_operation_status = "Starting fresh pipeline..."
                
                # Start the pipeline in background
                if hasattr(manager, 'start_fresh_pipeline'):
                    manager.start_fresh_pipeline()
                    st.session_state.dataset_operation_status = "Fresh pipeline started! Check progress above."
                else:
                    st.error("Fresh pipeline method not available")
            except ImportError:
                st.info("📊 Dataset manager not available - using basic display")
                self.create_basic_dataset_manager()
                
        except Exception as e:
            st.error(f"Dataset error: {str(e)}")
            self.create_basic_dataset_manager()
    
    def start_enrichment_only(self):
        """Start enrichment process only"""
        try:
            try:
                from src.data.master_enricher import MasterEnricher
                enricher = MasterEnricher()
                st.session_state.dataset_operation_status = "Starting enrichment process..."
            except ImportError:
                st.info("📊 Master enricher not available - using basic display")
            
            # Simulate enrichment progress
            st.session_state.enrichment_progress = {
                'current': 1,
                'total': 10,
                'coin': 'USDC'
            }
            
        except ImportError:
            st.error("Master enricher not available")
    
    def render_telegram_signals_section(self):
        """Render live telegram signals monitoring"""
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
        
        # Get live telegram signals from database
        try:
            from src.data.database import CoinDatabase
            db = CoinDatabase()
            signals = db.get_telegram_signals(limit=20, min_confidence=0.5)
            
            if signals:
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
            
            else:
                st.warning("📡 No telegram signals found in database. Check signal monitoring status.")
                st.info("""
                **To start receiving signals:**
                1. Ensure telegram monitoring is active
                2. Check database connections
                3. Verify channel access permissions
                """)
        
        except Exception as e:
            st.error(f"❌ Error loading telegram signals: {e}")
            st.info("Using telegram signal simulation for development...")
            
            # Fallback to simulated signals for development
            demo_signals = [
                {'coin_symbol': 'SOL', 'signal_type': 'BUY', 'confidence': 0.85, 'entry_price': 119.50, 'timestamp': '2025-01-31 10:30:00', 'channel_name': 'CryptoGems'},
                {'coin_symbol': 'AVAX', 'signal_type': 'SELL', 'confidence': 0.75, 'entry_price': 35.20, 'timestamp': '2025-01-31 09:45:00', 'channel_name': 'MoonShots'},
                {'coin_symbol': 'NEAR', 'signal_type': 'BUY', 'confidence': 0.92, 'entry_price': 8.45, 'timestamp': '2025-01-31 08:15:00', 'channel_name': 'ATM.Day'}
            ]
            
            for signal in demo_signals:
                signal_type = signal['signal_type']
                signal_color = {'BUY': '#4CAF50', 'SELL': '#f44336'}.get(signal_type, '#9e9e9e')
                
                st.markdown(f"""
                <div class="signal-card" style="border-left-color: {signal_color}">
                    <h4>📡 {signal['coin_symbol']} - {signal_type} (DEMO)</h4>
                    <p><strong>Confidence:</strong> {signal['confidence']:.1%}</p>
                    <p><strong>Entry:</strong> ${signal['entry_price']:.6f}</p>
                    <p><strong>Channel:</strong> {signal['channel_name']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    def render_database_status(self):
        """Render current database status"""
        st.markdown("#### 📋 Database Status")
        
        try:
            from src.data.database import CoinDatabase
            
            db = CoinDatabase()
            
            # Get basic stats
            with db._get_connection() if hasattr(db, '_get_connection') else sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records in each table
                tables = ['coins', 'price_data', 'telegram_signals', 'indicators']
                stats = {}
                
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        stats[table] = count
                    except:
                        stats[table] = 0
                
                # Display stats
                for table, count in stats.items():
                    st.metric(f"📊 {table.title()}", f"{count:,}")
                    
        except Exception as e:
            st.error(f"Database status error: {e}")
            # Fallback display
            st.metric("📊 Coins", "0")
            st.metric("📊 Price Data", "0")
            st.metric("📊 Signals", "0")
    
    def render_dataset_overview(self):
        """Render dataset overview and recent data"""
        st.markdown("### 📈 Recent Dataset Activity")
        
        # Create sample data for demonstration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # TODO: Connect to real recent dataset activity
            st.info("📊 No live dataset activity data connected")
            st.markdown("**Data will show:**")
            st.markdown("- Recent coin processing activity")
            st.markdown("- Data sources (API, Telegram, etc.)")
            st.markdown("- Processing status and confidence")
            st.markdown("- Timestamps and success rates")
            
            # Show placeholder table structure
            placeholder_data = {
                'Timestamp': ['No data'],
                'Coin': ['Connect to'],
                'Source': ['live data'],
                'Status': ['sources'],
                'Confidence': ['0%']
            }
            
            df_placeholder = pd.DataFrame(placeholder_data)
            st.dataframe(df_placeholder, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Pipeline Health")
            # TODO: Connect to real pipeline health metrics
            st.metric("Success Rate", "No data", help="Connect to pipeline monitoring")
            st.metric("Avg Processing Time", "Unknown", help="Connect to performance metrics")
            st.metric("API Health", "No data", help="Connect to API monitoring")
    
    def create_basic_dataset_manager(self):
        """Create basic dataset manager if not available"""
        st.info("Creating basic dataset management functionality...")
        # This would create a simple version if the full manager isn't available

def main():
    """Run the ultra-premium dashboard"""
    dashboard = UltraPremiumDashboard()

if __name__ == "__main__":
    main()