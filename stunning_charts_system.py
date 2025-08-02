"""
Stunning Charts System - Advanced Chart Types for TrenchCoat Pro
Implements candlestick, radar, donut, and other premium chart types
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Chart configuration with export and advanced features
CHART_CONFIG = {
    'displayModeBar': True,
    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'trenchcoat_chart',
        'height': 1080,
        'width': 1920,
        'scale': 2
    }
}

def create_candlestick_chart(price_data: pd.DataFrame, coin_name: str = "Coin") -> go.Figure:
    """Create advanced candlestick chart with moving averages"""
    try:
        fig = go.Figure()
        
        # Add candlestick
        fig.add_trace(go.Candlestick(
            x=price_data['timestamp'],
            open=price_data['open'],
            high=price_data['high'],
            low=price_data['low'],
            close=price_data['close'],
            name='Price',
            increasing_line_color='#10b981',
            decreasing_line_color='#ef4444'
        ))
        
        # Add moving averages
        if 'ma20' in price_data.columns:
            fig.add_trace(go.Scatter(
                x=price_data['timestamp'],
                y=price_data['ma20'],
                name='MA20',
                line=dict(color='#3b82f6', width=2)
            ))
        
        if 'ma50' in price_data.columns:
            fig.add_trace(go.Scatter(
                x=price_data['timestamp'],
                y=price_data['ma50'],
                name='MA50',
                line=dict(color='#f59e0b', width=2)
            ))
        
        # Update layout
        fig.update_layout(
            title=f"{coin_name} Price Chart",
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1h", step="hour", stepmode="backward"),
                        dict(count=24, label="24h", step="hour", stepmode="backward"),
                        dict(count=7, label="7d", step="day", stepmode="backward"),
                        dict(count=30, label="30d", step="day", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=False),
                type="date"
            )
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating candlestick chart: {e}")
        return None

def create_performance_radar(coin_metrics: Dict) -> go.Figure:
    """Create radar chart for multi-dimensional performance analysis"""
    try:
        categories = ['Price Gain', 'Volume', 'Smart Money', 'Liquidity', 'Social Score', 'Tech Score']
        
        # Normalize values to 0-100 scale
        values = [
            min(100, max(0, coin_metrics.get('price_gain_score', 50))),
            min(100, max(0, coin_metrics.get('volume_score', 50))),
            min(100, max(0, coin_metrics.get('smart_money_score', 50))),
            min(100, max(0, coin_metrics.get('liquidity_score', 50))),
            min(100, max(0, coin_metrics.get('social_score', 50))),
            min(100, max(0, coin_metrics.get('tech_score', 50)))
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Current',
            line_color='#10b981',
            fillcolor='rgba(16, 185, 129, 0.3)'
        ))
        
        # Add benchmark
        benchmark = [60, 60, 60, 60, 60, 60]
        fig.add_trace(go.Scatterpolar(
            r=benchmark,
            theta=categories,
            fill='toself',
            name='Market Average',
            line_color='#6b7280',
            fillcolor='rgba(107, 114, 128, 0.1)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color='#9ca3af')
                ),
                angularaxis=dict(
                    tickfont=dict(color='#e5e7eb')
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=True,
            template="plotly_dark",
            height=500,
            title="Performance Analysis"
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating radar chart: {e}")
        return None

def create_holder_distribution_donut(holder_data: Dict) -> go.Figure:
    """Create donut chart for holder distribution"""
    try:
        labels = ['Whales (>1%)', 'Large (0.1-1%)', 'Medium (0.01-0.1%)', 'Small (<0.01%)']
        values = [
            holder_data.get('whale_count', 10),
            holder_data.get('large_count', 50),
            holder_data.get('medium_count', 200),
            holder_data.get('small_count', 500)
        ]
        
        colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.6,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Holders: %{value}<br>%{percent}<extra></extra>'
        )])
        
        # Add center annotation
        total_holders = sum(values)
        fig.add_annotation(
            text=f'{total_holders:,}<br>Total Holders',
            x=0.5, y=0.5,
            font=dict(size=20, color='#e5e7eb'),
            showarrow=False
        )
        
        fig.update_layout(
            title="Holder Distribution",
            template="plotly_dark",
            height=500,
            showlegend=True,
            margin=dict(t=60, b=60, l=60, r=60)
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating donut chart: {e}")
        return None

def create_volume_heatmap(volume_data: pd.DataFrame) -> go.Figure:
    """Create volume heatmap over time"""
    try:
        # Prepare data for heatmap
        hours = volume_data['hour'].unique()
        days = volume_data['day'].unique()
        
        z_data = []
        for day in days:
            day_data = []
            for hour in hours:
                vol = volume_data[(volume_data['day'] == day) & (volume_data['hour'] == hour)]['volume'].values
                day_data.append(vol[0] if len(vol) > 0 else 0)
            z_data.append(day_data)
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=hours,
            y=days,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='Day: %{y}<br>Hour: %{x}<br>Volume: $%{z:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Volume Activity Heatmap",
            xaxis_title="Hour (UTC)",
            yaxis_title="Day",
            template="plotly_dark",
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating volume heatmap: {e}")
        return None

def create_liquidity_depth_chart(order_book: Dict) -> go.Figure:
    """Create order book depth chart"""
    try:
        fig = go.Figure()
        
        # Buy orders (bids)
        if 'bids' in order_book:
            bids = order_book['bids']
            bid_prices = [b[0] for b in bids]
            bid_cumulative = np.cumsum([b[1] for b in bids])
            
            fig.add_trace(go.Scatter(
                x=bid_prices,
                y=bid_cumulative,
                mode='lines',
                name='Bids',
                line=dict(color='#10b981', width=2),
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.3)'
            ))
        
        # Sell orders (asks)
        if 'asks' in order_book:
            asks = order_book['asks']
            ask_prices = [a[0] for a in asks]
            ask_cumulative = np.cumsum([a[1] for a in asks])
            
            fig.add_trace(go.Scatter(
                x=ask_prices,
                y=ask_cumulative,
                mode='lines',
                name='Asks',
                line=dict(color='#ef4444', width=2),
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.3)'
            ))
        
        fig.update_layout(
            title="Liquidity Depth",
            xaxis_title="Price",
            yaxis_title="Cumulative Volume",
            template="plotly_dark",
            height=400,
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating liquidity depth chart: {e}")
        return None

def render_chart_with_error_handling(chart_func, *args, **kwargs):
    """Wrapper to render charts with error handling and fallback"""
    try:
        fig = chart_func(*args, **kwargs)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
            return True
        else:
            st.error(f"Failed to create {chart_func.__name__}")
            return False
    except Exception as e:
        st.error(f"Chart error: {str(e)}")
        # Fallback to simple chart
        try:
            # Create a simple line chart as fallback
            st.line_chart(pd.DataFrame(np.random.randn(20, 3), columns=['A', 'B', 'C']))
            st.info("Showing sample data due to chart error")
        except:
            st.error("Unable to display chart")
        return False

def create_chart_container(title: str, description: str = "") -> None:
    """Create a styled container for charts"""
    st.markdown(f"""
    <div class="glass-card" style="padding: 20px; margin: 10px 0; border-radius: 12px;">
        <h3 style="color: #10b981; margin-bottom: 5px;">{title}</h3>
        {f'<p style="color: #9ca3af; font-size: 14px; margin-bottom: 15px;">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)