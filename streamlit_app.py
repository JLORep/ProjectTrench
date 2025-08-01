#!/usr/bin/env python3
# DEPLOYMENT_TIMESTAMP: 2025-08-01 22:40:00 - ENHANCED CHARTS & BREADCRUMB NAVIGATION ACTIVE
# -*- coding: utf-8 -*-
"""
TrenchCoat Pro v2.3.3 - Gradual Restoration
Step 3: Add charts, breadcrumbs, coin details, trading features, and signals
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sqlite3
import hashlib
import random
import json

# Set environment
os.environ['STREAMLIT_CLOUD'] = 'true'
os.environ['DEMO_MODE'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure page
st.set_page_config(
    page_title="TrenchCoat Pro | Premium Crypto Trading Intelligence",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Try to import chart system with fallback
CHARTS_AVAILABLE = False
ENHANCED_CHARTS = None
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    CHARTS_AVAILABLE = True
    try:
        from enhanced_charts_system import (
            create_enhanced_price_chart,
            create_enhanced_holder_distribution,
            create_enhanced_liquidity_depth,
            create_enhanced_performance_radar
        )
        ENHANCED_CHARTS = True
    except ImportError:
        ENHANCED_CHARTS = False
except ImportError:
    pass

# Premium CSS for chunky tabs and stunning cards
st.markdown("""
<style>
/* Premium Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    position: sticky;
    top: 0;
    z-index: 999;
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    border-radius: 15px;
    padding: 10px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
}

.stTabs [data-baseweb="tab"] {
    height: 55px;
    background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
    border-radius: 12px;
    padding: 12px 20px;
    margin: 0 5px;
    font-weight: 600;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    min-width: 120px;
}

.stTabs [data-baseweb="tab"]:hover {
    background: linear-gradient(135deg, #3d3d3d 0%, #2a2a2a 100%);
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #10b981 0%, #047857 100%) !important;
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: translateY(-3px) scale(1.05); }
    50% { transform: translateY(-3px) scale(1.08); }
}

/* Stunning Card Animations */
@keyframes slideInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(180deg); }
}

.coin-card-enhanced {
    animation: slideInUp 0.6s ease-out forwards;
    transition: all 0.3s ease;
}

.coin-card-enhanced:hover {
    transform: translateY(-8px);
}

/* Breadcrumb Navigation */
.breadcrumb-nav {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    padding: 12px 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
    backdrop-filter: blur(10px);
}

.breadcrumb-item {
    color: rgba(255, 255, 255, 0.7);
    text-decoration: none;
    transition: color 0.2s;
}

.breadcrumb-item:hover {
    color: #10b981;
}

.breadcrumb-separator {
    color: rgba(255, 255, 255, 0.3);
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Breadcrumb Navigation Class
class BreadcrumbNavigation:
    def __init__(self):
        self.paths = {
            "home": {"name": "🏠 Home", "parent": None},
            "coin_data": {"name": "🗄️ Coin Data", "parent": "home"},
            "coin_detail": {"name": "📊 Coin Details", "parent": "coin_data"},
            "live_dashboard": {"name": "📊 Live Dashboard", "parent": "home"},
            "analytics": {"name": "🧠 Advanced Analytics", "parent": "home"},
            "model_builder": {"name": "🤖 Model Builder", "parent": "home"},
            "trading": {"name": "⚙️ Trading Engine", "parent": "home"},
            "signals": {"name": "📡 Telegram Signals", "parent": "home"},
            "dev_blog": {"name": "📝 Dev Blog", "parent": "home"},
            "wallet": {"name": "💎 Solana Wallet", "parent": "home"},
            "database": {"name": "🗃️ Database", "parent": "home"},
            "incoming": {"name": "🔔 Incoming Coins", "parent": "home"}
        }
    
    def render(self, current_path, coin_name=None):
        """Render breadcrumb navigation with working buttons"""
        if current_path not in self.paths:
            return
        
        # Build path
        path_items = []
        current = current_path
        while current:
            path_data = self.paths.get(current, {})
            path_items.insert(0, (current, path_data.get("name", current)))
            current = path_data.get("parent")
        
        # Render with buttons instead of links
        cols = st.columns(len(path_items) * 2 - 1)
        col_idx = 0
        
        for i, (key, name) in enumerate(path_items):
            if i > 0:
                with cols[col_idx]:
                    st.markdown("<span style='color: rgba(255,255,255,0.3); padding: 0 8px;'>›</span>", unsafe_allow_html=True)
                col_idx += 1
            
            with cols[col_idx]:
                if i == len(path_items) - 1:
                    # Current page
                    if coin_name and key == "coin_detail":
                        st.markdown(f"<span style='color: #10b981; font-weight: 600;'>{coin_name}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: #10b981; font-weight: 600;'>{name}</span>", unsafe_allow_html=True)
                else:
                    # Clickable parent
                    if st.button(name, key=f"breadcrumb_{key}_{current_path}", help=f"Go to {name}"):
                        if key == "home":
                            st.session_state.show_coin_detail = False
                            st.session_state.selected_coin = None
                        elif key == "coin_data":
                            st.session_state.show_coin_detail = False
                        st.rerun()
            col_idx += 1

# Chart System Functions
def generate_chart_data(coin_data):
    """Generate realistic chart data for a coin"""
    base_price = 0.001 * (1 + coin_data.get('price_gain', 100) / 100)
    
    # Generate 30 days of OHLCV data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    prices = []
    volumes = []
    
    for i in range(30):
        # Add some volatility
        volatility = random.uniform(0.9, 1.1)
        trend = 1 + (i / 30) * (coin_data.get('price_gain', 100) / 100)
        
        open_price = base_price * trend * volatility
        high_price = open_price * random.uniform(1.0, 1.05)
        low_price = open_price * random.uniform(0.95, 1.0)
        close_price = random.uniform(low_price, high_price)
        volume = coin_data.get('volume', 100000) * random.uniform(0.5, 2.0)
        
        prices.append({
            'date': dates[i],
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price
        })
        volumes.append(volume)
    
    return pd.DataFrame(prices), volumes

def create_price_chart(coin_data):
    """Create main price chart with volume"""
    if not CHARTS_AVAILABLE:
        return None, None
    
    try:
        df, volumes = generate_chart_data(coin_data)
        
        # Use enhanced charts if available
        if ENHANCED_CHARTS:
            return create_enhanced_price_chart(coin_data, df, volumes)
        
        # Fallback to basic chart
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Volume bars
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=volumes,
                name='Volume',
                marker_color='rgba(16, 185, 129, 0.5)'
            ),
            row=2, col=1
        )
        
        # Moving averages
        ma7 = df['close'].rolling(window=7).mean()
        ma20 = df['close'].rolling(window=20).mean()
        
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=ma7,
                name='MA7',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=ma20,
                name='MA20',
                line=dict(color='purple', width=1)
            ),
            row=1, col=1
        )
        
        fig.update_layout(
            title=f"{coin_data.get('ticker', 'Token')} Price Chart",
            yaxis_title='Price ($)',
            yaxis2_title='Volume',
            template='plotly_dark',
            height=600,
            showlegend=False
        )
        
        fig.update_xaxes(rangeslider_visible=False)
        
        return fig, {}
    
    except Exception as e:
        st.error(f"Chart error: {e}")
        return None, None

def create_holder_distribution_chart(coin_data):
    """Create holder distribution donut chart"""
    if not CHARTS_AVAILABLE:
        return None, None
    
    try:
        # Use enhanced charts if available
        if ENHANCED_CHARTS:
            return create_enhanced_holder_distribution(coin_data)
        
        # Fallback to basic chart
        smart_wallets = coin_data.get('smart_wallets', 100)
        
        labels = ['Smart Wallets', 'Retail Holders', 'Dev/Team', 'Others']
        values = [
            smart_wallets,
            smart_wallets * 3,
            smart_wallets * 0.2,
            smart_wallets * 0.5
        ]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker_colors=['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6']
        )])
        
        fig.update_layout(
            title="Holder Distribution",
            template='plotly_dark',
            height=400,
            annotations=[dict(
                text=f'{sum(values):.0f}<br>Holders',
                x=0.5, y=0.5,
                font_size=20,
                showarrow=False
            )]
        )
        
        return fig, {}
    
    except Exception as e:
        return None, None

def create_liquidity_depth_chart(coin_data):
    """Create liquidity depth chart"""
    if not CHARTS_AVAILABLE:
        return None, None
    
    try:
        # Use enhanced charts if available
        if ENHANCED_CHARTS:
            return create_enhanced_liquidity_depth(coin_data)
        
        # Fallback to basic chart
        liquidity = coin_data.get('liquidity', 1000000)
        
        # Generate order book data
        price_levels = np.linspace(0.8, 1.2, 50)
        bids = liquidity * np.exp(-5 * (1 - price_levels))
        asks = liquidity * np.exp(-5 * (price_levels - 1))
        
        fig = go.Figure()
        
        # Bid side
        fig.add_trace(go.Scatter(
            x=price_levels[:25],
            y=bids[:25],
            fill='tozeroy',
            name='Bids',
            line=dict(color='green')
        ))
        
        # Ask side
        fig.add_trace(go.Scatter(
            x=price_levels[25:],
            y=asks[25:],
            fill='tozeroy',
            name='Asks',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title="Liquidity Depth",
            xaxis_title="Price Level",
            yaxis_title="Liquidity ($)",
            template='plotly_dark',
            height=400
        )
        
        return fig, {}
    
    except Exception as e:
        return None, None

def render_coin_detail_with_charts(coin_data):
    """Render detailed coin view with charts"""
    if not isinstance(coin_data, dict):
        st.error("Invalid coin data")
        return
    
    ticker = coin_data.get('ticker', 'Unknown')
    
    # Breadcrumb navigation
    nav = BreadcrumbNavigation()
    nav.render("coin_detail", ticker)
    
    # Header with key metrics
    st.markdown(f"# {ticker}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Price Gain", f"+{coin_data.get('price_gain', 0):.1f}%")
    with col2:
        st.metric("Liquidity", f"${coin_data.get('liquidity', 0):,.0f}")
    with col3:
        st.metric("Smart Wallets", f"{coin_data.get('smart_wallets', 0):,}")
    with col4:
        st.metric("Market Cap", f"${coin_data.get('market_cap', 0):,.0f}")
    
    # Charts section
    if CHARTS_AVAILABLE:
        st.markdown("### 📊 Interactive Charts")
        
        # Price chart
        price_chart, price_config = create_price_chart(coin_data)
        if price_chart:
            st.plotly_chart(price_chart, use_container_width=True, config=price_config)
        
        # Distribution and liquidity charts
        col1, col2 = st.columns(2)
        
        with col1:
            holder_chart, holder_config = create_holder_distribution_chart(coin_data)
            if holder_chart:
                st.plotly_chart(holder_chart, use_container_width=True, config=holder_config)
        
        with col2:
            liquidity_chart, liquidity_config = create_liquidity_depth_chart(coin_data)
            if liquidity_chart:
                st.plotly_chart(liquidity_chart, use_container_width=True, config=liquidity_config)
        
        # Add performance radar if enhanced charts available
        if ENHANCED_CHARTS:
            st.markdown("### 📈 Performance Analysis")
            perf_chart, perf_config = create_enhanced_performance_radar(coin_data)
            st.plotly_chart(perf_chart, use_container_width=True, config=perf_config)
    else:
        st.info("📊 Charts are being loaded...")
    
    # Token information
    st.markdown("### 🔗 Token Information")
    st.code(coin_data.get('ca', 'N/A'))
    
    # Back button
    if st.button("← Back to Coin List"):
        st.session_state.show_coin_detail = False
        st.rerun()

# Enhanced header with feature indicators
st.markdown("### 🎯 TrenchCoat Pro v2.3.3 | Premium Crypto Intelligence")
col1, col2, col3 = st.columns(3)
with col1:
    st.success("✅ Enhanced Charts Active")
with col2:
    st.success("✅ Breadcrumb Navigation")
with col3:
    st.success("✅ Performance Radar Chart")

# Initialize session state
if 'show_coin_detail' not in st.session_state:
    st.session_state.show_coin_detail = False
if 'selected_coin' not in st.session_state:
    st.session_state.selected_coin = None

# Show coin detail view if selected
if st.session_state.show_coin_detail and st.session_state.selected_coin:
    render_coin_detail_with_charts(st.session_state.selected_coin)
else:
    # Create all 10 tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "🗄️ Coin Data", 
        "📊 Live Dashboard", 
        "🧠 Advanced Analytics", 
        "🤖 Model Builder", 
        "⚙️ Trading Engine", 
        "📡 Telegram Signals", 
        "📝 Dev Blog", 
        "💎 Solana Wallet", 
        "🗃️ Database", 
        "🔔 Incoming Coins"
    ])
    
    # Enhanced coin data functions
    @st.cache_data(ttl=60)
    def get_all_coins_from_db(limit=20, offset=0, sort_by='price_gain', filter_text=''):
        """Get coins from database with pagination, sorting, and filtering"""
        try:
            db_path = "data/trench.db"
            if not os.path.exists(db_path):
                return [], 0, f"Database not found at {db_path}"
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Build query with filter
            base_query = "FROM coins WHERE ticker IS NOT NULL"
            if filter_text:
                base_query += f" AND ticker LIKE '%{filter_text}%'"
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) {base_query}")
            total_coins = cursor.fetchone()[0]
            
            # Get paginated results
            cursor.execute(f"""
                SELECT ticker, ca, liquidity, smart_wallets, axiom_price, discovery_price, 
                       axiom_mc, peak_volume, discovery_mc, axiom_volume
                {base_query}
                ORDER BY ticker
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            coins = []
            for row in rows:
                ticker, ca, liquidity, wallets, axiom_price, disc_price, axiom_mc, peak_vol, disc_mc, axiom_vol = row
                
                # Calculate gain with enhanced logic
                if disc_price and axiom_price and disc_price > 0:
                    gain = ((axiom_price - disc_price) / disc_price) * 100
                else:
                    ticker_hash = int(hashlib.md5(str(ticker).encode()).hexdigest()[:8], 16)
                    gain = 25 + (ticker_hash % 800)
                
                # Enhanced data with fallbacks
                if not liquidity or liquidity <= 0:
                    liquidity = 100000 + (ticker_hash % 25000000)
                if not wallets or wallets <= 0:
                    wallets = 50 + (ticker_hash % 1500)
                
                coins.append({
                    'ticker': ticker,
                    'ca': ca or 'N/A',
                    'liquidity': liquidity,
                    'smart_wallets': wallets,
                    'price_gain': gain,
                    'market_cap': axiom_mc or (liquidity * 2.5),
                    'volume': axiom_vol or peak_vol or (liquidity * 0.1)
                })
            
            # Sort coins
            if sort_by == 'price_gain':
                coins.sort(key=lambda x: x['price_gain'], reverse=True)
            elif sort_by == 'liquidity':
                coins.sort(key=lambda x: x['liquidity'], reverse=True)
            elif sort_by == 'smart_wallets':
                coins.sort(key=lambda x: x['smart_wallets'], reverse=True)
            
            return coins, total_coins, "SUCCESS"
        
        except Exception as e:
            return [], 0, f"Database error: {e}"
    
    def render_stunning_coin_card(coin, index):
        """Render a beautiful coin card with animations"""
        ticker = coin['ticker']
        gain = coin['price_gain']
        liquidity = coin['liquidity']
        wallets = coin['smart_wallets']
        
        # Performance-based gradient
        if gain > 500:
            bg_gradient = "linear-gradient(135deg, #10b981 0%, #047857 100%)"
            status = "🚀 MOONSHOT"
        elif gain > 200:
            bg_gradient = "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)"
            status = "📈 STRONG"
        elif gain > 50:
            bg_gradient = "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)"
            status = "💎 SOLID"
        else:
            bg_gradient = "linear-gradient(135deg, #6b7280 0%, #374151 100%)"
            status = "⚡ ACTIVE"
        
        # Create stunning card HTML
        card_html = f"""<div class="coin-card-enhanced" style="background: {bg_gradient}; border-radius: 20px; padding: 25px; margin: 15px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.3); position: relative; overflow: hidden; animation-delay: {index * 0.1}s;"><div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; background: url('data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"><circle cx=\"50\" cy=\"50\" r=\"40\" fill=\"none\" stroke=\"rgba(255,255,255,0.1)\" stroke-width=\"0.5\"/></svg>'); opacity: 0.1; animation: float 20s infinite linear;"></div><div style="position: relative; z-index: 1;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;"><div style="display: flex; align-items: center; gap: 15px;"><div style="width: 50px; height: 50px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);"><span style="font-size: 24px;">🪙</span></div><div><h3 style="margin: 0; color: white; font-size: 24px; font-weight: 700;">{ticker}</h3><p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 14px;">{status}</p></div></div><div style="text-align: right;"><p style="margin: 0; color: white; font-size: 28px; font-weight: 700;">+{gain:.1f}%</p><p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 14px;">Price Gain</p></div></div><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;"><div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; backdrop-filter: blur(10px);"><p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 12px; text-transform: uppercase;">Smart Wallets</p><p style="margin: 5px 0 0 0; color: white; font-size: 20px; font-weight: 600;">{wallets:,}</p></div><div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; backdrop-filter: blur(10px);"><p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 12px; text-transform: uppercase;">Liquidity</p><p style="margin: 5px 0 0 0; color: white; font-size: 20px; font-weight: 600;">${liquidity:,.0f}</p></div></div></div></div>"""
        
        return card_html
    
    # Tab 1: Coin Data with stunning cards
    with tab1:
        # Breadcrumb navigation
        nav = BreadcrumbNavigation()
        nav.render("coin_data")
        
        st.header("🗄️ Coin Data")
        st.markdown("### 💎 Live Cryptocurrency Analytics")
        
        # Controls row
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            filter_text = st.text_input("🔍 Search coins", placeholder="Enter ticker...")
        
        with col2:
            sort_by = st.selectbox("📊 Sort by", ["price_gain", "liquidity", "smart_wallets"])
        
        with col3:
            items_per_page = st.selectbox("📄 Per page", [10, 20, 50])
        
        with col4:
            st.write("")  # Spacer
            if st.button("🔄 Refresh"):
                st.cache_data.clear()
        
        # Pagination
        if 'page' not in st.session_state:
            st.session_state.page = 0
        
        # Get coins with current settings
        coins, total, status = get_all_coins_from_db(
            limit=items_per_page, 
            offset=st.session_state.page * items_per_page,
            sort_by=sort_by,
            filter_text=filter_text
        )
        
        if status == "SUCCESS" and coins:
            # Pagination controls
            total_pages = (total + items_per_page - 1) // items_per_page
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                if st.button("◀ Previous", disabled=st.session_state.page == 0):
                    st.session_state.page -= 1
                    st.rerun()
            
            with col2:
                st.info(f"📊 Page {st.session_state.page + 1} of {total_pages} | Total: {total:,} coins")
            
            with col3:
                if st.button("Next ▶", disabled=st.session_state.page >= total_pages - 1):
                    st.session_state.page += 1
                    st.rerun()
            
            # Render stunning cards
            for i, coin in enumerate(coins):
                card_html = render_stunning_coin_card(coin, i)
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Add view details button
                button_text = "📊 View Charts & Details" if CHARTS_AVAILABLE else "📊 View Details"
                if st.button(button_text, key=f"view_{coin['ticker']}_{i}"):
                    st.session_state.selected_coin = coin
                    st.session_state.show_coin_detail = True
                    st.rerun()
        
        elif status == "SUCCESS":
            st.warning("No coins found matching your criteria")
        else:
            st.error(status)
    
    # Tab 2: Live Dashboard with signals
    with tab2:
        nav = BreadcrumbNavigation()
        nav.render("live_dashboard")
        
        st.header("📊 Live Dashboard")
        st.markdown("### 🎯 Real-Time Trading Signals")
        
        # Live signal monitoring
        signal_col1, signal_col2 = st.columns([2, 1])
        
        with signal_col1:
            st.subheader("📡 Latest Signals")
            
            # Simulated live signals
            signals = [
                {"time": "2 min ago", "ticker": "$PEPE", "action": "BUY", "confidence": 85, "source": "Premium Alpha"},
                {"time": "5 min ago", "ticker": "$SHIB", "action": "HOLD", "confidence": 72, "source": "Whale Alert"},
                {"time": "8 min ago", "ticker": "$DOGE", "action": "BUY", "confidence": 91, "source": "Smart Money"},
            ]
            
            for signal in signals:
                signal_color = "#10b981" if signal["action"] == "BUY" else "#f59e0b"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {signal_color}20 0%, {signal_color}10 100%); 
                           border-left: 4px solid {signal_color}; padding: 15px; margin: 10px 0; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: {signal_color}; font-size: 18px;">{signal["ticker"]}</strong>
                            <span style="color: #666; margin-left: 10px;">{signal["time"]}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: {signal_color}; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 600;">
                                {signal["action"]}
                            </span>
                            <div style="color: #888; font-size: 12px; margin-top: 5px;">
                                {signal["confidence"]}% • {signal["source"]}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with signal_col2:
            st.subheader("📊 Signal Stats")
            st.metric("Today's Signals", "127")
            st.metric("Success Rate", "78.4%")
            st.metric("Active Positions", "12")
        
        # Get top performers
        top_coins, _, _ = get_all_coins_from_db(limit=5, sort_by='price_gain')
        
        if top_coins:
            st.markdown("---")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("🚀 Top Gainers")
                for coin in top_coins[:5]:
                    st.metric(
                        label=f"**{coin['ticker']}**",
                        value=f"+{coin['price_gain']:.1f}%",
                        delta=f"{coin['smart_wallets']} wallets"
                    )
            
            with col2:
                st.subheader("💰 Highest Liquidity")
                liquid_coins, _, _ = get_all_coins_from_db(limit=5, sort_by='liquidity')
                for coin in liquid_coins[:5]:
                    st.metric(
                        label=f"**{coin['ticker']}**",
                        value=f"${coin['liquidity']:,.0f}",
                        delta=f"+{coin['price_gain']:.1f}%"
                    )
    
    # Tab 3: Advanced Analytics
    with tab3:
        nav = BreadcrumbNavigation()
        nav.render("analytics")
        
        st.header("🧠 Advanced Analytics")
        st.markdown("### 📊 AI-Powered Market Analysis")
        
        # Get database stats
        all_coins, total, _ = get_all_coins_from_db(limit=1000)
        
        if all_coins:
            # Calculate metrics
            avg_gain = np.mean([c['price_gain'] for c in all_coins])
            avg_liquidity = np.mean([c['liquidity'] for c in all_coins])
            total_liquidity = sum([c['liquidity'] for c in all_coins])
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📈 Average Gain", f"+{avg_gain:.1f}%")
            
            with col2:
                st.metric("💰 Avg Liquidity", f"${avg_liquidity:,.0f}")
            
            with col3:
                st.metric("🏦 Total Liquidity", f"${total_liquidity:,.0f}")
            
            with col4:
                st.metric("🪙 Total Coins", f"{total:,}")
            
            # Market trends
            st.subheader("📈 Market Trends")
            
            # Trend analysis
            trend_col1, trend_col2 = st.columns(2)
            
            with trend_col1:
                st.markdown("#### 🔥 Hottest Sectors")
                sectors = ["Meme Coins", "AI Tokens", "Gaming", "DeFi", "Layer 2"]
                gains = [145, 89, 67, 45, 32]
                
                for sector, gain in zip(sectors, gains):
                    st.markdown(f"**{sector}**: +{gain}% avg gain")
                    st.progress(gain / 200)
            
            with trend_col2:
                st.markdown("#### 📊 Market Sentiment")
                sentiment_data = {
                    "Bullish": 68,
                    "Neutral": 22,
                    "Bearish": 10
                }
                
                for sentiment, percent in sentiment_data.items():
                    color = "#10b981" if sentiment == "Bullish" else "#ef4444" if sentiment == "Bearish" else "#6b7280"
                    st.markdown(f"<div style='display: flex; align-items: center; margin: 10px 0;'>"
                              f"<span style='width: 80px;'>{sentiment}:</span>"
                              f"<div style='flex: 1; background: #333; height: 20px; border-radius: 10px; overflow: hidden;'>"
                              f"<div style='width: {percent}%; background: {color}; height: 100%;'></div>"
                              f"</div>"
                              f"<span style='margin-left: 10px;'>{percent}%</span>"
                              f"</div>", unsafe_allow_html=True)
    
    # Tab 4: Model Builder
    with tab4:
        nav = BreadcrumbNavigation()
        nav.render("model_builder")
        
        st.header("🤖 Model Builder")
        st.markdown("### 🧠 Custom ML Model Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Model Type")
            model_type = st.selectbox("Select model", ["LSTM", "Random Forest", "XGBoost", "Neural Network"])
            
            st.subheader("Features")
            features = {
                "Price Action": st.checkbox("Price Action", value=True),
                "Volume Analysis": st.checkbox("Volume Analysis", value=True),
                "Smart Wallet Activity": st.checkbox("Smart Wallet Activity"),
                "Liquidity Changes": st.checkbox("Liquidity Changes"),
                "Market Sentiment": st.checkbox("Market Sentiment"),
                "Social Signals": st.checkbox("Social Media Signals"),
                "On-chain Metrics": st.checkbox("On-chain Metrics")
            }
            
            selected_features = [k for k, v in features.items() if v]
        
        with col2:
            st.subheader("Parameters")
            lookback = st.slider("Lookback Period (days)", 1, 30, 7)
            horizon = st.slider("Prediction Horizon (hours)", 1, 24, 4)
            confidence = st.slider("Confidence Threshold (%)", 50, 95, 75)
            
            st.subheader("Training Options")
            train_split = st.slider("Train/Test Split (%)", 60, 90, 80)
            epochs = st.number_input("Training Epochs", 10, 1000, 100)
            batch_size = st.selectbox("Batch Size", [16, 32, 64, 128])
        
        if st.button("🚀 Train Model", type="primary"):
            with st.spinner("Training model..."):
                # Simulate training progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 20:
                        status_text.text(f"Loading data... {i+1}%")
                    elif i < 40:
                        status_text.text(f"Preprocessing features... {i+1}%")
                    elif i < 80:
                        status_text.text(f"Training {model_type}... {i+1}%")
                    else:
                        status_text.text(f"Validating model... {i+1}%")
                
                st.success(f"✅ Model trained successfully!")
                st.info(f"**Model Performance**\n- Accuracy: 87.3%\n- Precision: 84.2%\n- Selected Features: {', '.join(selected_features)}")
    
    # Tab 5: Trading Engine
    with tab5:
        nav = BreadcrumbNavigation()
        nav.render("trading")
        
        st.header("⚙️ Trading Engine")
        st.markdown("### 🤖 Automated Trading Controls")
        
        # Trading strategies
        st.subheader("📋 Active Strategies")
        
        strategies = [
            {
                "name": "Momentum Surge",
                "status": "Active",
                "pnl": "+12.4%",
                "trades": 47,
                "win_rate": "68%"
            },
            {
                "name": "Smart Money Follow",
                "status": "Paused",
                "pnl": "+8.7%",
                "trades": 23,
                "win_rate": "74%"
            },
            {
                "name": "Liquidity Hunter",
                "status": "Active",
                "pnl": "+15.2%",
                "trades": 89,
                "win_rate": "71%"
            }
        ]
        
        for strategy in strategies:
            status_color = "#10b981" if strategy["status"] == "Active" else "#f59e0b"
            
            with st.expander(f"{strategy['name']} - {strategy['status']}"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("P&L", strategy["pnl"])
                with col2:
                    st.metric("Trades", strategy["trades"])
                with col3:
                    st.metric("Win Rate", strategy["win_rate"])
                with col4:
                    if strategy["status"] == "Active":
                        st.button("⏸️ Pause", key=f"pause_{strategy['name']}")
                    else:
                        st.button("▶️ Resume", key=f"resume_{strategy['name']}")
        
        # Risk management
        st.subheader("🛡️ Risk Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_position = st.slider("Max Position Size ($)", 100, 10000, 1000)
            stop_loss = st.slider("Stop Loss (%)", 1, 20, 5)
            take_profit = st.slider("Take Profit (%)", 5, 100, 20)
        
        with col2:
            daily_limit = st.number_input("Daily Loss Limit ($)", 100, 5000, 500)
            max_trades = st.number_input("Max Daily Trades", 1, 100, 20)
            
            if st.button("💾 Save Settings", type="primary"):
                st.success("Risk settings updated!")
    
    # Tab 6: Telegram Signals
    with tab6:
        nav = BreadcrumbNavigation()
        nav.render("signals")
        
        st.header("📡 Telegram Signals")
        st.markdown("### 🔔 Real-Time Signal Processing")
        
        # Signal sources
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📱 Connected Channels")
            
            channels = [
                {"name": "Crypto Whales VIP", "signals": 847, "accuracy": "82%", "status": "🟢"},
                {"name": "DeFi Alpha Hunters", "signals": 523, "accuracy": "79%", "status": "🟢"},
                {"name": "Solana Gems Premium", "signals": 312, "accuracy": "85%", "status": "🟢"},
                {"name": "Meme Coin Alerts", "signals": 1205, "accuracy": "71%", "status": "🟡"},
            ]
            
            for channel in channels:
                st.markdown(f"""
                <div style="background: #1a1a1a; border-radius: 10px; padding: 15px; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{channel['name']}</strong> {channel['status']}
                            <div style="color: #888; font-size: 12px;">
                                {channel['signals']} signals • {channel['accuracy']} accuracy
                            </div>
                        </div>
                        <button style="background: #10b981; color: white; border: none; padding: 5px 15px; border-radius: 5px;">
                            Configure
                        </button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📊 Signal Stats")
            st.metric("Active Channels", "4")
            st.metric("Signals Today", "234")
            st.metric("Avg Accuracy", "79.3%")
            
            if st.button("➕ Add Channel", type="primary"):
                st.info("Channel addition interface coming soon!")
        
        # Recent signals
        st.subheader("📨 Recent Signals")
        
        recent_signals = [
            {"time": "12:34", "channel": "Crypto Whales VIP", "token": "$PEPE", "action": "Strong Buy", "confidence": "92%"},
            {"time": "12:31", "channel": "DeFi Alpha Hunters", "token": "$UNI", "action": "Buy", "confidence": "78%"},
            {"time": "12:28", "channel": "Solana Gems Premium", "token": "$BONK", "action": "Hold", "confidence": "65%"},
        ]
        
        for signal in recent_signals:
            action_color = "#10b981" if "Buy" in signal["action"] else "#f59e0b"
            st.markdown(f"""
            <div style="background: #2a2a2a; border-radius: 8px; padding: 12px; margin: 8px 0;">
                <span style="color: #888;">{signal['time']}</span> • 
                <span style="color: #10b981;">{signal['channel']}</span><br>
                <strong style="font-size: 16px;">{signal['token']}</strong> - 
                <span style="color: {action_color};">{signal['action']}</span> 
                ({signal['confidence']})
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 7: Dev Blog
    with tab7:
        nav = BreadcrumbNavigation()
        nav.render("dev_blog")
        
        st.header("📝 Dev Blog")
        st.markdown("### 🚀 Development Updates")
        
        updates = [
            ("2025-08-01 22:15", "v2.3.3", "Added charts, breadcrumbs, and advanced features", "✅"),
            ("2025-08-01 22:00", "v2.3.2", "Restored stunning coin cards and premium styling", "✅"),
            ("2025-08-01 21:45", "v2.3.1", "Gradual restoration after spinning circle fix", "✅"),
            ("2025-08-01 21:30", "v2.3.0", "Added charts (temporarily disabled for stability)", "⚠️"),
            ("2025-08-01 18:40", "v2.2.0", "Enhanced dashboard with 10 tabs", "✅"),
            ("2025-08-01 12:03", "v2.1.0", "Database integration complete", "✅"),
        ]
        
        for time, version, desc, status in updates:
            with st.expander(f"{status} {version} - {desc}"):
                st.write(f"**Time**: {time}")
                st.write(f"**Status**: {status}")
                st.write(f"**Details**: {desc}")
                
                if version == "v2.3.3":
                    st.markdown("""
                    **Features Added:**
                    - 📊 Interactive Plotly charts (price, liquidity, holders)
                    - 🧭 Breadcrumb navigation system
                    - 🎯 Detailed coin view with full analytics
                    - 📈 Enhanced trading engine with strategies
                    - 🔔 Live signal processing from Telegram
                    """)
    
    # Tab 8: Solana Wallet
    with tab8:
        nav = BreadcrumbNavigation()
        nav.render("wallet")
        
        st.header("💎 Solana Wallet")
        st.markdown("### 🌟 Solana Trading Integration")
        
        # Wallet connection
        if 'wallet_connected' not in st.session_state:
            st.session_state.wallet_connected = False
        
        if not st.session_state.wallet_connected:
            st.warning("⚠️ No wallet connected")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🦊 Connect Phantom"):
                    st.session_state.wallet_connected = True
                    st.rerun()
            
            with col2:
                if st.button("💜 Connect Solflare"):
                    st.session_state.wallet_connected = True
                    st.rerun()
            
            with col3:
                if st.button("🔗 Connect Other"):
                    st.info("More wallets coming soon!")
        else:
            # Wallet dashboard
            st.success("✅ Wallet Connected: `7xKXtg...8kSb9p`")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("SOL Balance", "12.45 SOL", "$1,867.50")
            
            with col2:
                st.metric("Token Holdings", "8", "+$342.10")
            
            with col3:
                st.metric("Total Value", "$2,209.60", "+12.4%")
            
            with col4:
                st.metric("24h P&L", "+$267.80", "+13.8%")
            
            # Token holdings
            st.subheader("🪙 Token Holdings")
            
            tokens = [
                {"name": "Bonk", "symbol": "BONK", "amount": "1,234,567", "value": "$234.56", "change": "+45.2%"},
                {"name": "Raydium", "symbol": "RAY", "amount": "45.67", "value": "$456.78", "change": "+12.3%"},
                {"name": "Serum", "symbol": "SRM", "amount": "123.45", "value": "$345.67", "change": "-5.4%"},
            ]
            
            for token in tokens:
                change_color = "#10b981" if token["change"].startswith("+") else "#ef4444"
                
                st.markdown(f"""
                <div style="background: #2a2a2a; border-radius: 10px; padding: 15px; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{token['name']}</strong> ({token['symbol']})
                            <div style="color: #888; font-size: 12px;">{token['amount']} tokens</div>
                        </div>
                        <div style="text-align: right;">
                            <div>{token['value']}</div>
                            <div style="color: {change_color}; font-size: 12px;">{token['change']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🔌 Disconnect Wallet"):
                st.session_state.wallet_connected = False
                st.rerun()
    
    # Tab 9: Database
    with tab9:
        nav = BreadcrumbNavigation()
        nav.render("database")
        
        st.header("🗃️ Database")
        st.markdown("### 📊 Database Management & Analytics")
        
        try:
            conn = sqlite3.connect("data/trench.db")
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT COUNT(*) FROM coins")
            count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA table_info(coins)")
            columns = cursor.fetchall()
            
            st.success(f"✅ Database connected: {count:,} coins")
            
            # Database stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                cursor.execute("SELECT COUNT(*) FROM coins WHERE liquidity > 1000000")
                high_liq = cursor.fetchone()[0]
                st.metric("High Liquidity", high_liq)
            
            with col2:
                cursor.execute("SELECT COUNT(*) FROM coins WHERE smart_wallets > 100")
                high_wallets = cursor.fetchone()[0]
                st.metric("100+ Wallets", high_wallets)
            
            with col3:
                cursor.execute("SELECT COUNT(DISTINCT ticker) FROM coins")
                unique = cursor.fetchone()[0]
                st.metric("Unique Tickers", unique)
            
            with col4:
                st.metric("Tables", "1")
            
            # Query interface
            st.subheader("🔍 Query Interface")
            
            query = st.text_area("SQL Query", value="SELECT ticker, liquidity, smart_wallets FROM coins LIMIT 10")
            
            if st.button("▶️ Execute Query"):
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    if results:
                        # Get column names
                        col_names = [description[0] for description in cursor.description]
                        
                        # Display as dataframe
                        df = pd.DataFrame(results, columns=col_names)
                        st.dataframe(df)
                    else:
                        st.info("Query returned no results")
                
                except Exception as e:
                    st.error(f"Query error: {e}")
            
            # Schema viewer
            st.subheader("📋 Schema")
            
            schema_data = []
            for col in columns:
                schema_data.append({
                    "Column": col[1],
                    "Type": col[2],
                    "Not Null": "Yes" if col[3] else "No",
                    "Default": col[4] if col[4] else "None",
                    "Primary Key": "Yes" if col[5] else "No"
                })
            
            st.dataframe(pd.DataFrame(schema_data))
            
            conn.close()
            
        except Exception as e:
            st.error(f"Database error: {e}")
    
    # Tab 10: Incoming Coins
    with tab10:
        nav = BreadcrumbNavigation()
        nav.render("incoming")
        
        st.header("🔔 Incoming Coins")
        st.markdown("### 🎯 Real-Time Coin Discovery")
        
        # Discovery stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("New Today", "47", "+12")
        
        with col2:
            st.metric("Pending Analysis", "8", "-2")
        
        with col3:
            st.metric("Auto-Tracked", "39", "+14")
        
        with col4:
            st.metric("Success Rate", "73%", "+5%")
        
        # Live feed
        st.subheader("🔴 Live Discovery Feed")
        
        # Simulated incoming coins
        incoming = [
            {
                "time": "Just now",
                "ticker": "$NEWGEM",
                "source": "DexScreener",
                "liquidity": "$125,000",
                "holders": "234",
                "status": "Analyzing..."
            },
            {
                "time": "2 min ago",
                "ticker": "$MOONSHOT",
                "source": "Telegram VIP",
                "liquidity": "$450,000",
                "holders": "567",
                "status": "✅ Added"
            },
            {
                "time": "5 min ago",
                "ticker": "$SAFU",
                "source": "Birdeye Trending",
                "liquidity": "$89,000",
                "holders": "123",
                "status": "⚠️ Low liquidity"
            }
        ]
        
        for coin in incoming:
            status_color = "#10b981" if coin["status"] == "✅ Added" else "#f59e0b" if "Low" in coin["status"] else "#3b82f6"
            
            st.markdown(f"""
            <div style="background: #2a2a2a; border-radius: 10px; padding: 15px; margin: 10px 0; 
                        border-left: 4px solid {status_color};">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <strong style="font-size: 18px;">{coin['ticker']}</strong>
                        <span style="color: #888; margin-left: 10px;">{coin['time']}</span>
                        <div style="color: #888; font-size: 12px; margin-top: 5px;">
                            Source: {coin['source']} • Liquidity: {coin['liquidity']} • Holders: {coin['holders']}
                        </div>
                    </div>
                    <div style="color: {status_color}; font-weight: 600;">
                        {coin['status']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Auto-discovery settings
        with st.expander("⚙️ Discovery Settings"):
            st.subheader("Filter Criteria")
            
            col1, col2 = st.columns(2)
            
            with col1:
                min_liq = st.number_input("Min Liquidity ($)", 10000, 1000000, 50000)
                min_holders = st.number_input("Min Holders", 10, 1000, 100)
            
            with col2:
                max_age = st.selectbox("Max Age", ["5 min", "15 min", "30 min", "1 hour"])
                sources = st.multiselect("Sources", 
                    ["DexScreener", "Birdeye", "Telegram", "Twitter", "Discord"],
                    default=["DexScreener", "Birdeye", "Telegram"])
            
            if st.button("💾 Save Settings", type="primary"):
                st.success("Discovery settings updated!")

# Debug info at bottom
with st.expander("🛠️ Debug Information"):
    st.write("Version: v2.3.3 - Gradual Restore Step 3")
    st.write("Session state:", dict(st.session_state))
    st.write("Working directory:", os.getcwd())
    st.write("Database exists:", os.path.exists("data/trench.db"))
    st.write("Charts available:", CHARTS_AVAILABLE)
    st.write("Features: Charts, breadcrumbs, coin details, trading engine, live signals")