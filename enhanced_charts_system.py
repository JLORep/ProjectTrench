#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Chart System with Stylish, Reactive, Auto-Scaling Visualizations
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def create_enhanced_price_chart(coin_data, df, volumes):
    """Create stunning price chart with enhanced styling and interactivity"""
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.75, 0.25],
        subplot_titles=(f"<b>{coin_data.get('ticker', 'Token')} Price Action</b>", "<b>Volume Analysis</b>")
    )
    
    # Enhanced candlestick with gradient colors
    increasing_color = 'rgba(16, 185, 129, 0.8)'  # Green
    decreasing_color = 'rgba(239, 68, 68, 0.8)'   # Red
    
    fig.add_trace(
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing=dict(line=dict(color=increasing_color, width=1), fillcolor=increasing_color),
            decreasing=dict(line=dict(color=decreasing_color, width=1), fillcolor=decreasing_color),
            hoverlabel=dict(font_size=14),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>' +
                          'Open: $%{open:.6f}<br>' +
                          'High: $%{high:.6f}<br>' +
                          'Low: $%{low:.6f}<br>' +
                          'Close: $%{close:.6f}<br>' +
                          '<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Enhanced volume bars with gradient
    colors = ['rgba(16, 185, 129, 0.6)' if df['close'].iloc[i] >= df['open'].iloc[i] 
              else 'rgba(239, 68, 68, 0.6)' for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=volumes,
            name='Volume',
            marker=dict(
                color=colors,
                line=dict(width=0)
            ),
            hoverlabel=dict(font_size=14),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Volume: $%{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Enhanced moving averages with glow effect
    ma7 = df['close'].rolling(window=7).mean()
    ma20 = df['close'].rolling(window=20).mean()
    
    # MA7 with glow
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=ma7,
            name='MA7',
            line=dict(color='rgba(251, 191, 36, 0.3)', width=6),  # Glow
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=ma7,
            name='MA7',
            line=dict(color='#fbbf24', width=2),
            hoverlabel=dict(font_size=14),
            hovertemplate='MA7: $%{y:.6f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # MA20 with glow
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=ma20,
            name='MA20',
            line=dict(color='rgba(139, 92, 246, 0.3)', width=6),  # Glow
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=ma20,
            name='MA20',
            line=dict(color='#8b5cf6', width=2),
            hoverlabel=dict(font_size=14),
            hovertemplate='MA20: $%{y:.6f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add price change annotation
    price_change = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
    change_color = '#10b981' if price_change > 0 else '#ef4444'
    
    fig.add_annotation(
        x=df['date'].iloc[-1],
        y=df['high'].max() * 1.05,
        text=f"<b>{price_change:+.1f}%</b>",
        showarrow=False,
        font=dict(size=20, color=change_color),
        row=1, col=1
    )
    
    # Enhanced layout with dark theme
    fig.update_layout(
        template='plotly_dark',
        height=700,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(26, 26, 26, 0.9)',
        plot_bgcolor='rgba(26, 26, 26, 0.9)',
        font=dict(family='Arial, sans-serif', size=12, color='#ffffff'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=14),
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            borderwidth=1
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(26, 26, 26, 0.9)',
            font_size=14,
            font_family='Arial, sans-serif'
        ),
        dragmode='zoom',
        selectdirection='horizontal',
        xaxis=dict(
            rangeslider=dict(visible=False),
            rangeselector=dict(
                bgcolor='rgba(26, 26, 26, 0.9)',
                bordercolor='rgba(255, 255, 255, 0.2)',
                borderwidth=1,
                buttons=list([
                    dict(count=7, label="<b>1W</b>", step="day", stepmode="backward"),
                    dict(count=14, label="<b>2W</b>", step="day", stepmode="backward"),
                    dict(count=1, label="<b>1M</b>", step="month", stepmode="backward"),
                    dict(label="<b>ALL</b>", step="all")
                ]),
                font=dict(size=14, color='#ffffff'),
                x=0,
                y=1.05
            )
        )
    )
    
    # Update axes styling
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255, 255, 255, 0.1)',
        showline=True,
        linewidth=1,
        linecolor='rgba(255, 255, 255, 0.2)',
        zeroline=False
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255, 255, 255, 0.1)',
        showline=True,
        linewidth=1,
        linecolor='rgba(255, 255, 255, 0.2)',
        zeroline=False,
        title_font=dict(size=14)
    )
    
    # Auto-scaling with padding
    fig.update_yaxes(autorange=True, fixedrange=False, row=1, col=1)
    fig.update_yaxes(autorange=True, fixedrange=False, row=2, col=1)
    
    # Add custom modebar buttons
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'{coin_data.get("ticker", "chart")}_price_chart',
            'height': 700,
            'width': 1200,
            'scale': 2
        }
    }
    
    return fig, config

def create_enhanced_holder_distribution(coin_data):
    """Create enhanced holder distribution with animations"""
    
    # Generate distribution data
    smart_wallets = coin_data.get('smart_wallets', 100)
    
    labels = ['Smart Money', 'Retail Traders', 'Development', 'Others']
    values = [
        smart_wallets,
        smart_wallets * 3,
        smart_wallets * 0.2,
        smart_wallets * 0.5
    ]
    
    # Enhanced colors with gradients
    colors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6']
    
    fig = go.Figure()
    
    # Add outer ring
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=.65,
        marker=dict(
            colors=colors,
            line=dict(color='rgba(255, 255, 255, 0.2)', width=2)
        ),
        textfont=dict(size=16, color='white'),
        textposition='outside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Holders: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>',
        hoverlabel=dict(font_size=14),
        pull=[0.1 if i == 0 else 0 for i in range(len(labels))]  # Pull out smart money
    ))
    
    # Add center text
    total_holders = sum(values)
    fig.add_annotation(
        text=f'<b>{total_holders:,.0f}</b><br>Total Holders',
        x=0.5, y=0.5,
        font=dict(size=24, color='white'),
        showarrow=False
    )
    
    # Enhanced layout
    fig.update_layout(
        template='plotly_dark',
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(26, 26, 26, 0.9)',
        plot_bgcolor='rgba(26, 26, 26, 0.9)',
        font=dict(family='Arial, sans-serif', size=14, color='#ffffff'),
        title=dict(
            text='<b>Holder Distribution Analysis</b>',
            font=dict(size=20),
            x=0.5,
            xanchor='center'
        ),
        showlegend=False,
        hoverlabel=dict(
            bgcolor='rgba(26, 26, 26, 0.9)',
            font_size=14
        )
    )
    
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'{coin_data.get("ticker", "chart")}_holders',
            'height': 500,
            'width': 600,
            'scale': 2
        }
    }
    
    return fig, config

def create_enhanced_liquidity_depth(coin_data):
    """Create enhanced liquidity depth chart with animations"""
    
    liquidity = coin_data.get('liquidity', 1000000)
    
    # Generate more detailed order book data
    price_range = 0.4  # 40% range
    price_points = 100
    current_price = 1.0
    
    prices = np.linspace(current_price * (1 - price_range/2), 
                        current_price * (1 + price_range/2), 
                        price_points)
    
    # Generate bid/ask volumes with realistic distribution
    mid_point = len(prices) // 2
    
    # Bids (buy orders)
    bid_volumes = np.zeros(mid_point)
    for i in range(mid_point):
        distance_from_mid = (mid_point - i) / mid_point
        bid_volumes[i] = liquidity * np.exp(-3 * (1 - distance_from_mid)) * distance_from_mid
    bid_cumulative = np.cumsum(bid_volumes[::-1])[::-1]
    
    # Asks (sell orders)
    ask_volumes = np.zeros(price_points - mid_point)
    for i in range(len(ask_volumes)):
        distance_from_mid = i / len(ask_volumes)
        ask_volumes[i] = liquidity * np.exp(-3 * distance_from_mid) * (1 - distance_from_mid)
    ask_cumulative = np.cumsum(ask_volumes)
    
    fig = go.Figure()
    
    # Add bid depth with gradient
    fig.add_trace(go.Scatter(
        x=prices[:mid_point],
        y=bid_cumulative,
        fill='tozeroy',
        name='Bids',
        line=dict(color='#10b981', width=3),
        fillcolor='rgba(16, 185, 129, 0.3)',
        hovertemplate='Price: $%{x:.6f}<br>Cumulative Bids: $%{y:,.0f}<extra></extra>',
        hoverlabel=dict(font_size=14)
    ))
    
    # Add ask depth with gradient
    fig.add_trace(go.Scatter(
        x=prices[mid_point:],
        y=ask_cumulative,
        fill='tozeroy',
        name='Asks',
        line=dict(color='#ef4444', width=3),
        fillcolor='rgba(239, 68, 68, 0.3)',
        hovertemplate='Price: $%{x:.6f}<br>Cumulative Asks: $%{y:,.0f}<extra></extra>',
        hoverlabel=dict(font_size=14)
    ))
    
    # Add current price line
    fig.add_vline(
        x=current_price,
        line=dict(color='#fbbf24', width=2, dash='dash'),
        annotation=dict(
            text=f'<b>Current Price</b><br>${current_price:.6f}',
            font=dict(size=14, color='#fbbf24'),
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='#fbbf24',
            borderwidth=1
        )
    )
    
    # Add spread indicator
    spread = prices[mid_point] - prices[mid_point-1]
    spread_pct = (spread / current_price) * 100
    
    fig.add_annotation(
        x=current_price,
        y=max(max(bid_cumulative), max(ask_cumulative)) * 0.9,
        text=f'<b>Spread: {spread_pct:.3f}%</b>',
        showarrow=False,
        font=dict(size=16, color='white'),
        bgcolor='rgba(26, 26, 26, 0.8)',
        bordercolor='rgba(255, 255, 255, 0.2)',
        borderwidth=1
    )
    
    # Enhanced layout
    fig.update_layout(
        template='plotly_dark',
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(26, 26, 26, 0.9)',
        plot_bgcolor='rgba(26, 26, 26, 0.9)',
        font=dict(family='Arial, sans-serif', size=12, color='#ffffff'),
        title=dict(
            text='<b>Order Book Depth</b>',
            font=dict(size=20),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='<b>Price Level</b>',
            title_font=dict(size=14),
            tickformat='.6f',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        yaxis=dict(
            title='<b>Cumulative Volume ($)</b>',
            title_font=dict(size=14),
            tickformat=',.0f',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=14),
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            borderwidth=1
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(26, 26, 26, 0.9)',
            font_size=14
        )
    )
    
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'{coin_data.get("ticker", "chart")}_liquidity',
            'height': 500,
            'width': 800,
            'scale': 2
        }
    }
    
    return fig, config

def create_enhanced_performance_radar(coin_data):
    """Create enhanced radar chart for performance metrics"""
    
    # Generate performance metrics
    categories = ['Liquidity', 'Volume', 'Holders', 'Price Trend', 'Market Cap', 'Activity']
    
    # Normalize metrics to 0-100 scale
    liquidity_score = min(100, (coin_data.get('liquidity', 0) / 1000000) * 20)
    volume_score = min(100, (coin_data.get('volume', 0) / 100000) * 20)
    holders_score = min(100, (coin_data.get('smart_wallets', 0) / 100) * 20)
    price_score = min(100, coin_data.get('price_gain', 0) / 5)
    mcap_score = min(100, (coin_data.get('market_cap', 0) / 10000000) * 20)
    activity_score = random.randint(60, 90)  # Simulated activity score
    
    values = [liquidity_score, volume_score, holders_score, price_score, mcap_score, activity_score]
    
    fig = go.Figure()
    
    # Add the main radar trace
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(16, 185, 129, 0.3)',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8, color='#10b981'),
        name='Current',
        hovertemplate='%{theta}<br>Score: %{r:.1f}/100<extra></extra>',
        hoverlabel=dict(font_size=14)
    ))
    
    # Add benchmark trace
    benchmark = [70, 70, 70, 70, 70, 70]
    fig.add_trace(go.Scatterpolar(
        r=benchmark,
        theta=categories,
        fill='toself',
        fillcolor='rgba(251, 191, 36, 0.1)',
        line=dict(color='#fbbf24', width=2, dash='dot'),
        marker=dict(size=6, color='#fbbf24'),
        name='Benchmark',
        hovertemplate='%{theta}<br>Benchmark: %{r}/100<extra></extra>',
        hoverlabel=dict(font_size=14)
    ))
    
    # Enhanced layout
    fig.update_layout(
        template='plotly_dark',
        height=500,
        margin=dict(l=80, r=80, t=80, b=80),
        paper_bgcolor='rgba(26, 26, 26, 0.9)',
        plot_bgcolor='rgba(26, 26, 26, 0.9)',
        font=dict(family='Arial, sans-serif', size=12, color='#ffffff'),
        title=dict(
            text='<b>Performance Metrics</b>',
            font=dict(size=20),
            x=0.5,
            xanchor='center'
        ),
        polar=dict(
            bgcolor='rgba(26, 26, 26, 0.5)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showline=False,
                showticklabels=True,
                tickfont=dict(size=10),
                gridcolor='rgba(255, 255, 255, 0.1)',
                gridwidth=1
            ),
            angularaxis=dict(
                showline=True,
                linewidth=1,
                linecolor='rgba(255, 255, 255, 0.2)',
                gridcolor='rgba(255, 255, 255, 0.1)',
                gridwidth=1,
                tickfont=dict(size=14)
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=14),
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor='rgba(26, 26, 26, 0.9)',
            font_size=14
        )
    )
    
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'{coin_data.get("ticker", "chart")}_performance',
            'height': 500,
            'width': 600,
            'scale': 2
        }
    }
    
    return fig, config