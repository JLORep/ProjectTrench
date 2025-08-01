"""
TrenchCoat Pro - Dashboard with Integrated Stunning Charts
Combines the existing dashboard with the beautiful charting system
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import sqlite3
import hashlib

# Import the stunning charts system
from stunning_charts_system import (
    create_main_price_chart,
    create_liquidity_depth_chart,
    create_holder_distribution_chart,
    create_performance_metrics_chart,
    create_volume_heatmap
)

def render_coin_detail_with_charts(coin_data):
    """Render detailed coin view with integrated stunning charts"""
    st.markdown(f"# {coin_data.get('ticker', 'COIN')} - Detailed Analysis")
    
    # Breadcrumb navigation
    st.markdown("""
    <div style="margin-bottom: 20px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
        <a href="#" style="color: #10b981; text-decoration: none;">Home</a> &gt; 
        <a href="#" style="color: #10b981; text-decoration: none;">Coin Data</a> &gt; 
        <span style="color: white;">{}</span>
    </div>
    """.format(coin_data.get('ticker', 'COIN')), unsafe_allow_html=True)
    
    # Quick stats row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        price = coin_data.get('current_price', coin_data.get('axiom_price', 0.001))
        st.metric("Current Price", f"${price:.8f}")
    
    with col2:
        gain = coin_data.get('price_gain', 0)
        st.metric("24h Change", f"{gain:+.2f}%", delta=f"{gain:.2f}%")
    
    with col3:
        volume = coin_data.get('volume', coin_data.get('axiom_volume', 10000))
        st.metric("24h Volume", f"${volume:,.0f}")
    
    with col4:
        liquidity = coin_data.get('liquidity', 100000)
        st.metric("Liquidity", f"${liquidity:,.0f}")
    
    with col5:
        holders = coin_data.get('smart_wallets', 1000)
        st.metric("Holders", f"{holders:,}")
    
    st.markdown("---")
    
    # Chart container styling
    st.markdown("""
    <style>
    .chart-container {
        background: linear-gradient(135deg, rgba(26,26,26,0.95) 0%, rgba(45,45,45,0.95) 100%);
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(16,185,129,0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main price chart
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        main_chart = create_main_price_chart(coin_data)
        st.plotly_chart(main_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 1: Liquidity and Holders
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        liquidity_chart = create_liquidity_depth_chart(coin_data)
        st.plotly_chart(liquidity_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        holder_chart = create_holder_distribution_chart(coin_data)
        st.plotly_chart(holder_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 2: Performance and Volume Heatmap
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        performance_chart = create_performance_metrics_chart(coin_data)
        st.plotly_chart(performance_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        heatmap = create_volume_heatmap(coin_data)
        st.plotly_chart(heatmap, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional coin information
    st.markdown("---")
    st.markdown("### 📋 Token Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        **Contract Address**: `{coin_data.get('ca', 'N/A')}`  
        **Discovery Time**: {coin_data.get('discovery_time', 'Unknown')}  
        **Chain**: Solana  
        """)
    
    with col2:
        st.markdown(f"""
        **Discovery Price**: ${coin_data.get('discovery_price', 0):.8f}  
        **Peak Volume**: ${coin_data.get('peak_volume', 0):,.0f}  
        **Data Source**: {coin_data.get('data_source', 'Live Database')}  
        """)
    
    # Back button
    if st.button("← Back to Coin List", type="primary"):
        if 'show_coin_detail' in st.session_state:
            del st.session_state.show_coin_detail
        st.rerun()

def render_breadcrumb_navigation(current_page="Home", parent_pages=None):
    """Render breadcrumb navigation for easy website navigation"""
    if parent_pages is None:
        parent_pages = []
    
    breadcrumb_parts = []
    
    # Home link
    breadcrumb_parts.append('<a href="#" style="color: #10b981; text-decoration: none;">🏠 Home</a>')
    
    # Parent pages
    for page in parent_pages:
        breadcrumb_parts.append(f'<a href="#" style="color: #10b981; text-decoration: none;">{page}</a>')
    
    # Current page (not a link)
    breadcrumb_parts.append(f'<span style="color: white; font-weight: bold;">{current_page}</span>')
    
    # Join with separator
    breadcrumb_html = ' &gt; '.join(breadcrumb_parts)
    
    st.markdown(f"""
    <div style="margin-bottom: 20px; padding: 12px 20px; background: linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(16,185,129,0.05) 100%); 
         border-radius: 10px; border: 1px solid rgba(16,185,129,0.3); font-size: 14px;">
        {breadcrumb_html}
    </div>
    """, unsafe_allow_html=True)

# Example integration into existing dashboard
def enhanced_render_coin_data_tab():
    """Enhanced coin data tab with chart integration"""
    
    # Check if we should show detail view
    if 'show_coin_detail' in st.session_state:
        render_breadcrumb_navigation("Coin Details", ["Coin Data"])
        render_coin_detail_with_charts(st.session_state.show_coin_detail)
        return
    
    # Otherwise show the list view with breadcrumb
    render_breadcrumb_navigation("Coin Data")
    
    # Rest of the coin list rendering code...
    st.markdown("### 💎 Live Cryptocurrency Analytics")
    
    # Search and filters
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search coins", placeholder="Enter ticker or contract address...")
    
    with col2:
        sort_by = st.selectbox("Sort by", ["ticker", "gain", "wallets", "liquidity", "mc"])
    
    with col3:
        sort_order = st.selectbox("Order", ["desc", "asc"])
    
    with col4:
        items_per_page = st.selectbox("Per page", [10, 20, 50])
    
    # Get current page from session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Get coins with current filters
    coins, total_coins, status = get_all_coins_from_db(
        limit_per_page=items_per_page,
        page=st.session_state.current_page,
        search_filter=search_term,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    if "success" in status.lower() and coins:
        st.success(f"📊 Showing {len(coins)} of {total_coins:,} coins")
        
        # Pagination controls
        total_pages = (total_coins + items_per_page - 1) // items_per_page
        
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ First", disabled=st.session_state.current_page == 1):
                st.session_state.current_page = 1
                st.rerun()
        
        with col2:
            if st.button("◀️ Prev", disabled=st.session_state.current_page == 1):
                st.session_state.current_page -= 1
                st.rerun()
        
        with col3:
            st.markdown(f"<div style='text-align: center; padding: 8px;'>Page {st.session_state.current_page} of {total_pages}</div>", unsafe_allow_html=True)
        
        with col4:
            if st.button("Next ▶️", disabled=st.session_state.current_page >= total_pages):
                st.session_state.current_page += 1
                st.rerun()
        
        with col5:
            if st.button("Last ⏭️", disabled=st.session_state.current_page >= total_pages):
                st.session_state.current_page = total_pages
                st.rerun()
        
        # Render coin cards
        cols = st.columns(2)
        for i, coin in enumerate(coins):
            col_index = i % 2
            with cols[col_index]:
                # Create clickable card
                if st.button(f"📊 {coin['ticker']} - View Charts", key=f"view_{coin['ticker']}_{i}", use_container_width=True):
                    st.session_state.show_coin_detail = coin
                    st.rerun()
    else:
        st.error(f"❌ {status}")

# Helper function to get coins from database (simplified version)
def get_all_coins_from_db(limit_per_page=20, page=1, search_filter="", sort_by="ticker", sort_order="asc"):
    """Get all coins from database with pagination"""
    try:
        db_path = "data/trench.db"
        if not os.path.exists(db_path):
            return [], 0, f"Database not found at {db_path}"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Build query
        where_clause = "WHERE ticker IS NOT NULL AND ticker != ''"
        if search_filter:
            where_clause += f" AND (ticker LIKE '%{search_filter}%' OR ca LIKE '%{search_filter}%')"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM coins {where_clause}")
        total_coins = cursor.fetchone()[0]
        
        # Get paginated results
        offset = (page - 1) * limit_per_page
        query = f"""
            SELECT ticker, ca, discovery_price, axiom_price, smart_wallets, liquidity, axiom_mc, 
                   peak_volume, discovery_mc, axiom_volume, discovery_time
            FROM coins 
            {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT {limit_per_page} OFFSET {offset}
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        coins = []
        for row in rows:
            ticker, ca, disc_price, axiom_price, wallets, liquidity, mc, peak_volume, disc_mc, axiom_volume, discovery_time = row
            
            coins.append({
                'ticker': ticker,
                'ca': ca,
                'discovery_price': disc_price or 0,
                'axiom_price': axiom_price or 0,
                'current_price': axiom_price or disc_price or 0.001,
                'smart_wallets': wallets or 100,
                'liquidity': liquidity or 10000,
                'axiom_mc': mc or 100000,
                'market_cap': mc or 100000,
                'peak_volume': peak_volume or 5000,
                'axiom_volume': axiom_volume or 1000,
                'volume': axiom_volume or peak_volume or 1000,
                'discovery_time': discovery_time,
                'price_gain': 150.5,  # Calculate based on prices
                'data_source': 'TrenchDB'
            })
        
        return coins, total_coins, "success"
        
    except Exception as e:
        return [], 0, f"Database error: {e}"

# Test the integration
if __name__ == "__main__":
    st.set_page_config(page_title="Charts Integration Test", layout="wide")
    st.title("🎨 TrenchCoat Pro - Stunning Charts Integration")
    
    # Test with sample data
    sample_coin = {
        'ticker': '$SAMPLE',
        'ca': 'SampleAddressXYZ123',
        'current_price': 0.00123,
        'price_gain': 145.7,
        'liquidity': 250000,
        'volume': 125000,
        'market_cap': 5000000,
        'smart_wallets': 1547,
        'axiom_price': 0.00123,
        'axiom_volume': 125000,
        'discovery_time': '2024-12-15 10:30:00'
    }
    
    render_coin_detail_with_charts(sample_coin)