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
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📊 Live Dashboard", "🧠 Advanced Analytics", "🤖 Model Builder", "⚙️ Trading Engine", "📡 Telegram Signals", "📝 Dev Blog", "💎 Solana Wallet", "🗄️ Coin Data"])
        
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
        
        with tab8:
            # Coin Data Tab
            self.render_coin_data_tab()
    
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
    
    def render_coin_data_tab(self):
        """Render beautiful coin data analytics from trench.db"""
        # Title with gradient background
        st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
                    border-radius: 15px; border: 1px solid rgba(16, 185, 129, 0.3);'>
            <h1 style='color: #10b981; margin: 0; font-size: 2.5rem; font-weight: 700;'>
                🗄️ TrenchCoat Coin Database
            </h1>
            <p style='color: #a3a3a3; margin-top: 0.5rem; font-size: 1.2rem;'>
                Live Analytics from 1,733+ Verified Coins
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Database stats row
        self.render_database_stats()
        
        st.markdown("---")
        
        # Main content in columns
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Top coins by different metrics
            self.render_top_coins_analysis()
        
        with col2:
            # Distribution charts
            self.render_coin_distributions()
        
        st.markdown("---")
        
        # Full coin table with search
        self.render_searchable_coin_table()
    
    def render_database_stats(self):
        """Render database statistics"""
        if database_available and streamlit_db:
            try:
                coins = streamlit_db.get_all_coins()
                
                # Calculate stats
                total_coins = len(coins)
                total_liquidity = sum(c.get('liquidity', 0) for c in coins)
                avg_smart_wallets = sum(c.get('smart_wallets', 0) for c in coins) / total_coins if total_coins > 0 else 0
                total_volume = sum(c.get('axiom_volume', 0) for c in coins)
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "📊 Total Coins",
                        f"{total_coins:,}",
                        "Live Database",
                        help="Total number of coins in trench.db"
                    )
                
                with col2:
                    st.metric(
                        "💰 Total Liquidity",
                        f"${total_liquidity/1e6:.1f}M",
                        f"${total_liquidity/total_coins:,.0f} avg" if total_coins > 0 else "$0 avg",
                        help="Combined liquidity across all coins"
                    )
                
                with col3:
                    st.metric(
                        "🧠 Avg Smart Wallets",
                        f"{avg_smart_wallets:.1f}",
                        "Per coin",
                        help="Average number of smart wallets holding each coin"
                    )
                
                with col4:
                    st.metric(
                        "📈 Total Volume",
                        f"${total_volume/1e6:.1f}M",
                        "24h volume",
                        help="Combined 24h trading volume"
                    )
            except Exception as e:
                st.error(f"Error loading database stats: {e}")
        else:
            # Demo stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Coins", "1,733", "Demo Data")
            with col2:
                st.metric("💰 Total Liquidity", "$42.7M", "$24.6K avg")
            with col3:
                st.metric("🧠 Avg Smart Wallets", "156.3", "Per coin")
            with col4:
                st.metric("📈 Total Volume", "$127.9M", "24h volume")
    
    def render_top_coins_analysis(self):
        """Render top coins by various metrics"""
        st.subheader("🏆 Top Performing Coins")
        
        metric_choice = st.selectbox(
            "Sort by:",
            ["Smart Wallets", "Liquidity", "Volume", "Price Change"],
            key="coin_metric_sort"
        )
        
        if database_available and streamlit_db:
            try:
                coins = streamlit_db.get_all_coins()
                df = pd.DataFrame(coins)
                
                # Sort by selected metric - ensure columns exist
                if metric_choice == "Smart Wallets" and 'smart_wallets' in df.columns:
                    df = df.nlargest(10, 'smart_wallets')
                    display_col = 'smart_wallets'
                    format_str = '{:.0f} wallets'
                elif metric_choice == "Liquidity" and 'liquidity' in df.columns:
                    df = df.nlargest(10, 'liquidity')
                    display_col = 'liquidity'
                    format_str = '${:,.0f}'
                elif metric_choice == "Volume" and 'axiom_volume' in df.columns:
                    df = df.nlargest(10, 'axiom_volume')
                    display_col = 'axiom_volume'
                    format_str = '${:,.0f}'
                else:  # Price Change
                    if 'axiom_price' in df.columns and 'discovery_price' in df.columns:
                        df['price_change'] = ((df['axiom_price'] - df['discovery_price']) / df['discovery_price'] * 100).fillna(0)
                        df = df.nlargest(10, 'price_change')
                        display_col = 'price_change'
                        format_str = '{:.1f}%'
                    else:
                        # Fallback to smart wallets if available
                        if 'smart_wallets' in df.columns:
                            df = df.nlargest(10, 'smart_wallets')
                            display_col = 'smart_wallets'
                            format_str = '{:.0f} wallets'
                        else:
                            st.error("No suitable data columns found")
                            return
                
                # Display top coins
                for idx, row in df.iterrows():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{row['ticker']}**")
                        st.caption(f"CA: {row['ca'][:8]}...{row['ca'][-6:]}")
                    
                    with col2:
                        value = row[display_col]
                        st.markdown(f"<p style='text-align: right; color: #10b981; font-weight: bold;'>{format_str.format(value)}</p>", unsafe_allow_html=True)
                    
                    with col3:
                        if display_col == 'price_change':
                            color = '#10b981' if value > 0 else '#ef4444'
                            arrow = '↑' if value > 0 else '↓'
                            st.markdown(f"<p style='text-align: center; color: {color}; font-size: 1.5rem;'>{arrow}</p>", unsafe_allow_html=True)
                    
                    st.markdown("<hr style='margin: 0.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Error loading coin data: {e}")
        else:
            # Demo data
            demo_coins = [
                {"ticker": "TRUMP", "value": "2,847", "change": "↑"},
                {"ticker": "BODEN", "value": "1,923", "change": "↑"},
                {"ticker": "PEPE", "value": "1,756", "change": "↓"},
                {"ticker": "WIF", "value": "1,542", "change": "↑"},
                {"ticker": "BONK", "value": "1,389", "change": "↑"},
            ]
            
            for coin in demo_coins[:5]:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{coin['ticker']}**")
                with col2:
                    st.markdown(f"<p style='text-align: right; color: #10b981; font-weight: bold;'>{coin['value']} wallets</p>", unsafe_allow_html=True)
                with col3:
                    color = '#10b981' if coin['change'] == '↑' else '#ef4444'
                    st.markdown(f"<p style='text-align: center; color: {color}; font-size: 1.5rem;'>{coin['change']}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 0.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
    
    def render_coin_distributions(self):
        """Render distribution charts for coin metrics"""
        st.subheader("📊 Coin Distributions")
        
        if database_available and streamlit_db:
            try:
                coins = streamlit_db.get_all_coins()
                df = pd.DataFrame(coins)
                
                if df.empty:
                    st.warning("No coin data available")
                    return
                
                # Debug: show available columns
                # st.write(f"Available columns: {list(df.columns)}")
                
                # Smart wallet distribution
                if 'smart_wallets' in df.columns:
                    fig1 = go.Figure()
                    smart_wallet_data = pd.to_numeric(df['smart_wallets'], errors='coerce').fillna(0)
                    fig1.add_trace(go.Histogram(
                        x=smart_wallet_data,
                        nbinsx=30,
                        marker_color='rgba(16, 185, 129, 0.7)',
                        name='Smart Wallets'
                    ))
                    fig1.update_layout(
                        title="Smart Wallet Distribution",
                        xaxis_title="Number of Smart Wallets",
                        yaxis_title="Number of Coins",
                        template="plotly_dark",
                        height=250,
                        margin=dict(t=40, b=40, l=40, r=40),
                        showlegend=False
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                # Liquidity distribution (log scale)
                if 'liquidity' in df.columns:
                    fig2 = go.Figure()
                    liquidity_data = pd.to_numeric(df['liquidity'], errors='coerce').fillna(1)
                    # Replace 0 with 1 for log scale, filter out negative values
                    liquidity_data = liquidity_data.replace(0, 1)
                    liquidity_data = liquidity_data[liquidity_data > 0]
                    
                    fig2.add_trace(go.Histogram(
                        x=np.log10(liquidity_data),
                        nbinsx=30,
                        marker_color='rgba(59, 130, 246, 0.7)',
                        name='Liquidity'
                    ))
                    fig2.update_layout(
                        title="Liquidity Distribution (Log Scale)",
                        xaxis_title="Log10(Liquidity USD)",
                        yaxis_title="Number of Coins",
                        template="plotly_dark",
                        height=250,
                        margin=dict(t=40, b=40, l=40, r=40),
                        showlegend=False
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error creating distributions: {e}")
                # Show detailed error for debugging
                import traceback
                st.code(traceback.format_exc())
        else:
            # Demo charts
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=np.random.lognormal(5, 1.5, 1000),
                nbinsx=30,
                marker_color='rgba(16, 185, 129, 0.7)'
            ))
            fig.update_layout(
                title="Smart Wallet Distribution",
                template="plotly_dark",
                height=250,
                margin=dict(t=40, b=40, l=40, r=40)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_searchable_coin_table(self):
        """Render searchable table of all coins"""
        st.subheader("🔍 Coin Database Explorer")
        
        # Search and filter controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search coins:", placeholder="Enter ticker, contract address...")
        
        with col2:
            min_wallets = st.number_input("Min Smart Wallets:", min_value=0, value=0, step=10)
        
        with col3:
            min_liquidity = st.number_input("Min Liquidity ($):", min_value=0, value=0, step=1000)
        
        if database_available and streamlit_db:
            try:
                coins = streamlit_db.get_all_coins()
                df = pd.DataFrame(coins)
                
                # Convert numeric columns to ensure proper filtering
                if 'smart_wallets' in df.columns:
                    df['smart_wallets'] = pd.to_numeric(df['smart_wallets'], errors='coerce').fillna(0)
                if 'liquidity' in df.columns:
                    df['liquidity'] = pd.to_numeric(df['liquidity'], errors='coerce').fillna(0)
                if 'axiom_volume' in df.columns:
                    df['axiom_volume'] = pd.to_numeric(df['axiom_volume'], errors='coerce').fillna(0)
                if 'axiom_price' in df.columns:
                    df['axiom_price'] = pd.to_numeric(df['axiom_price'], errors='coerce').fillna(0)
                if 'discovery_price' in df.columns:
                    df['discovery_price'] = pd.to_numeric(df['discovery_price'], errors='coerce').fillna(0)
                
                # Apply filters
                if search_term:
                    if 'ticker' in df.columns and 'ca' in df.columns:
                        mask = (df['ticker'].astype(str).str.contains(search_term, case=False, na=False) | 
                               df['ca'].astype(str).str.contains(search_term, case=False, na=False))
                        df = df[mask]
                
                if 'smart_wallets' in df.columns:
                    df = df[df['smart_wallets'] >= min_wallets]
                if 'liquidity' in df.columns:
                    df = df[df['liquidity'] >= min_liquidity]
                
                # Calculate additional metrics
                if 'axiom_price' in df.columns and 'discovery_price' in df.columns:
                    df['price_change_%'] = ((df['axiom_price'] - df['discovery_price']) / df['discovery_price'] * 100).fillna(0)
                
                # Select available columns for display
                available_cols = ['ticker', 'ca', 'smart_wallets', 'liquidity', 'axiom_volume', 'discovery_price', 'axiom_price']
                display_cols = [col for col in available_cols if col in df.columns]
                
                if 'price_change_%' in df.columns:
                    display_cols.append('price_change_%')
                
                display_df = df[display_cols].rename(columns={
                    'ticker': 'Ticker',
                    'ca': 'Contract Address',
                    'smart_wallets': 'Smart Wallets',
                    'liquidity': 'Liquidity ($)',
                    'axiom_volume': 'Volume ($)',
                    'discovery_price': 'Discovery Price',
                    'axiom_price': 'Current Price',
                    'price_change_%': 'Change %'
                })
                
                # Format the dataframe
                st.markdown(f"**Found {len(display_df)} coins matching your criteria**")
                
                # Display with custom formatting
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Contract Address": st.column_config.TextColumn(
                            width="small",
                            help="Solana contract address"
                        ),
                        "Smart Wallets": st.column_config.NumberColumn(
                            format="%d",
                            help="Number of smart wallets holding this coin"
                        ),
                        "Liquidity ($)": st.column_config.NumberColumn(
                            format="$%,.0f",
                            help="Total liquidity in USD"
                        ),
                        "Volume ($)": st.column_config.NumberColumn(
                            format="$%,.0f",
                            help="24h trading volume"
                        ),
                        "Discovery Price": st.column_config.NumberColumn(
                            format="%.8f",
                            help="Price when first discovered"
                        ),
                        "Current Price": st.column_config.NumberColumn(
                            format="%.8f",
                            help="Latest recorded price"
                        ),
                        "Change %": st.column_config.NumberColumn(
                            format="%.1f%%",
                            help="Price change since discovery"
                        )
                    },
                    hide_index=True
                )
                
            except Exception as e:
                st.error(f"Error loading coin table: {e}")
        else:
            # Demo table
            st.info("📊 Live database connection not available. Showing demo data.")
            demo_df = pd.DataFrame({
                'Ticker': ['TRUMP', 'BODEN', 'PEPE', 'WIF', 'BONK'],
                'Smart Wallets': [2847, 1923, 1756, 1542, 1389],
                'Liquidity ($)': [5234000, 3892000, 2156000, 1893000, 1654000],
                'Volume ($)': [8923000, 6234000, 4892000, 3421000, 2987000],
                'Change %': [234.5, 156.3, -23.4, 89.7, 123.4]
            })
            st.dataframe(demo_df, use_container_width=True)

# Create the dashboard instance
def create_dashboard():
    """Create and return dashboard instance"""
    return StreamlitSafeDashboard()

# For direct import compatibility
UltraPremiumDashboard = StreamlitSafeDashboard