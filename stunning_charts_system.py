"""
Stunning Charts System for TrenchCoat Pro
Beautiful, interactive charts for each coin with appropriate stats
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from typing import List, Dict, Optional, Tuple
import random

def generate_price_data(base_price: float, volatility: float = 0.02, trend: float = 0.001, periods: int = 168) -> List[float]:
    """Generate realistic price data for demonstration (7 days of hourly data)"""
    prices = [base_price]
    for i in range(1, periods):
        # Random walk with trend
        change = np.random.normal(trend, volatility)
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, base_price * 0.5))  # Prevent negative prices
    return prices

def create_main_price_chart(coin_data: Dict) -> go.Figure:
    """Create the main candlestick/line chart with volume"""
    # Generate sample data if no historical data
    current_price = coin_data.get('current_price', 0.001)
    periods = 168  # 7 days of hourly data
    
    # Generate timestamps
    timestamps = pd.date_range(end=datetime.now(), periods=periods, freq='H')
    
    # Generate OHLCV data
    prices = generate_price_data(current_price, volatility=0.03)
    volumes = [coin_data.get('volume', 10000) * np.random.uniform(0.5, 1.5) for _ in range(periods)]
    
    # Create OHLC data
    ohlc_data = []
    for i in range(len(prices)):
        open_price = prices[i] * np.random.uniform(0.98, 1.02)
        close_price = prices[i]
        high_price = max(open_price, close_price) * np.random.uniform(1, 1.02)
        low_price = min(open_price, close_price) * np.random.uniform(0.98, 1)
        ohlc_data.append({
            'timestamp': timestamps[i],
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volumes[i]
        })
    
    df = pd.DataFrame(ohlc_data)
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('', '')
    )
    
    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='#10b981',
            decreasing_line_color='#ef4444',
            increasing_fillcolor='#10b981',
            decreasing_fillcolor='#ef4444'
        ),
        row=1, col=1
    )
    
    # Add volume bars
    colors = ['#10b981' if df['close'][i] > df['open'][i] else '#ef4444' 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # Add moving averages
    ma_20 = df['close'].rolling(window=20).mean()
    ma_50 = df['close'].rolling(window=50).mean()
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=ma_20,
            name='MA20',
            line=dict(color='#3b82f6', width=1),
            opacity=0.7
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=ma_50,
            name='MA50',
            line=dict(color='#f59e0b', width=1),
            opacity=0.7
        ),
        row=1, col=1
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f"{coin_data.get('ticker', 'COIN')} Price Chart",
            'font': {'size': 24, 'color': '#10b981'}
        },
        template='plotly_dark',
        height=600,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(0,0,0,0.5)'
        ),
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        font=dict(color='white')
    )
    
    # Update axes
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)', row=2, col=1)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)', title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)', title_text="Volume", row=2, col=1)
    
    return fig

def create_liquidity_depth_chart(coin_data: Dict) -> go.Figure:
    """Create a beautiful liquidity depth chart"""
    liquidity = coin_data.get('liquidity', 100000)
    
    # Generate sample bid/ask data
    price_levels = 50
    current_price = coin_data.get('current_price', 0.001)
    
    bid_prices = [current_price * (1 - i * 0.001) for i in range(1, price_levels + 1)]
    ask_prices = [current_price * (1 + i * 0.001) for i in range(1, price_levels + 1)]
    
    # Generate cumulative liquidity
    bid_liquidity = [liquidity * (1 - i * 0.015) for i in range(price_levels)]
    ask_liquidity = [liquidity * (1 - i * 0.015) for i in range(price_levels)]
    
    fig = go.Figure()
    
    # Add bid side (green)
    fig.add_trace(go.Scatter(
        x=bid_prices[::-1],
        y=bid_liquidity[::-1],
        fill='tozeroy',
        name='Bids',
        line=dict(color='#10b981', width=2),
        fillcolor='rgba(16, 185, 129, 0.3)'
    ))
    
    # Add ask side (red)
    fig.add_trace(go.Scatter(
        x=ask_prices,
        y=ask_liquidity,
        fill='tozeroy',
        name='Asks',
        line=dict(color='#ef4444', width=2),
        fillcolor='rgba(239, 68, 68, 0.3)'
    ))
    
    # Add current price line
    fig.add_vline(
        x=current_price,
        line_width=2,
        line_dash="dash",
        line_color="#f59e0b",
        annotation_text=f"Current: ${current_price:.6f}",
        annotation_position="top"
    )
    
    fig.update_layout(
        title="Liquidity Depth",
        template='plotly_dark',
        height=400,
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        font=dict(color='white'),
        xaxis_title="Price ($)",
        yaxis_title="Liquidity ($)"
    )
    
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def create_holder_distribution_chart(coin_data: Dict) -> go.Figure:
    """Create a stunning holder distribution donut chart"""
    # Sample holder distribution
    holder_categories = ['Whales (>1%)', 'Large (0.1-1%)', 'Medium (0.01-0.1%)', 'Small (<0.01%)']
    holder_percentages = [15, 25, 35, 25]  # Sample data
    
    colors = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b']
    
    fig = go.Figure(data=[go.Pie(
        labels=holder_categories,
        values=holder_percentages,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textfont=dict(size=14, color='white'),
        textposition='outside',
        textinfo='label+percent'
    )])
    
    # Add center text
    holders_count = coin_data.get('smart_wallets', 1000)
    fig.add_annotation(
        text=f"{holders_count:,}<br>Holders",
        x=0.5, y=0.5,
        font=dict(size=20, color='white'),
        showarrow=False
    )
    
    fig.update_layout(
        title="Holder Distribution",
        template='plotly_dark',
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(t=50, b=0, l=0, r=0)
    )
    
    return fig

def create_performance_metrics_chart(coin_data: Dict) -> go.Figure:
    """Create a radar chart showing various performance metrics"""
    categories = ['Liquidity', 'Volume', 'Holders', 'Price Trend', 'Market Cap', 'Activity']
    
    # Calculate scores (0-100) for each metric
    scores = [
        min(100, (coin_data.get('liquidity', 0) / 1000000) * 100),  # Liquidity score
        min(100, (coin_data.get('volume', 0) / 100000) * 100),      # Volume score
        min(100, (coin_data.get('smart_wallets', 0) / 1000) * 100), # Holders score
        np.random.randint(40, 90),  # Price trend score (simulated)
        min(100, (coin_data.get('market_cap', 0) / 10000000) * 100), # Market cap score
        np.random.randint(50, 95)   # Activity score (simulated)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Performance',
        line=dict(color='#10b981', width=2),
        fillcolor='rgba(16, 185, 129, 0.3)'
    ))
    
    # Add benchmark
    benchmark = [60, 60, 60, 60, 60, 60]
    fig.add_trace(go.Scatterpolar(
        r=benchmark,
        theta=categories,
        name='Average',
        line=dict(color='#6b7280', width=1, dash='dash'),
        fillcolor='rgba(107, 114, 128, 0.1)'
    ))
    
    fig.update_layout(
        title="Performance Metrics",
        template='plotly_dark',
        height=400,
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.1)'
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.1)'
            )
        )
    )
    
    return fig

def create_volume_heatmap(coin_data: Dict) -> go.Figure:
    """Create a beautiful volume heatmap by hour and day"""
    # Generate sample volume data for last 7 days
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = [f"{i:02d}:00" for i in range(24)]
    
    # Generate volume data with patterns (higher during certain hours)
    base_volume = coin_data.get('volume', 10000) / 24
    volume_data = []
    for day in range(7):
        day_data = []
        for hour in range(24):
            # Higher volume during trading hours
            multiplier = 1.5 if 9 <= hour <= 16 else 0.7
            volume = base_volume * multiplier * np.random.uniform(0.5, 1.5)
            day_data.append(volume)
        volume_data.append(day_data)
    
    fig = go.Figure(data=go.Heatmap(
        z=volume_data,
        x=hours,
        y=days,
        colorscale='Viridis',
        text=[[f"${v:,.0f}" for v in row] for row in volume_data],
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Trading Volume Heatmap (24h x 7d)",
        template='plotly_dark',
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Hour (UTC)",
        yaxis_title="Day"
    )
    
    return fig

def render_stunning_charts(coin_data: Dict):
    """Render all charts for a coin in a stunning layout"""
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
    
    # Trading statistics
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 📊 Key Trading Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        price_change = coin_data.get('price_gain', 0)
        color = "#10b981" if price_change > 0 else "#ef4444"
        st.markdown(f"""
        <div style="text-align: center;">
            <h4 style="color: {color}; margin: 0;">24h Change</h4>
            <h2 style="color: {color}; margin: 0;">{price_change:+.2f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        volume = coin_data.get('volume', 0)
        st.markdown(f"""
        <div style="text-align: center;">
            <h4 style="color: #3b82f6; margin: 0;">24h Volume</h4>
            <h2 style="color: #3b82f6; margin: 0;">${volume:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        liquidity = coin_data.get('liquidity', 0)
        st.markdown(f"""
        <div style="text-align: center;">
            <h4 style="color: #8b5cf6; margin: 0;">Liquidity</h4>
            <h2 style="color: #8b5cf6; margin: 0;">${liquidity:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        holders = coin_data.get('smart_wallets', 0)
        st.markdown(f"""
        <div style="text-align: center;">
            <h4 style="color: #f59e0b; margin: 0;">Holders</h4>
            <h2 style="color: #f59e0b; margin: 0;">{holders:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Example usage
if __name__ == "__main__":
    # Sample coin data
    sample_coin = {
        'ticker': '$SAMPLE',
        'current_price': 0.00123,
        'price_gain': 145.7,
        'liquidity': 250000,
        'volume': 125000,
        'market_cap': 5000000,
        'smart_wallets': 1547
    }
    
    st.set_page_config(page_title="Stunning Charts Demo", layout="wide")
    st.title("🎨 Stunning Charts System Demo")
    
    render_stunning_charts(sample_coin)