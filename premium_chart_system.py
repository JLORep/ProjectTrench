#!/usr/bin/env python3
"""
Premium Chart System for TrenchCoat Pro
High-quality interactive charting with Plotly and advanced features
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import streamlit as st
from typing import Dict, List, Optional, Tuple
import json
import requests
from dataclasses import dataclass

@dataclass
class ChartConfig:
    """Configuration for chart appearance and behavior"""
    theme: str = "plotly_dark"
    height: int = 600
    primary_color: str = "#10b981"
    secondary_color: str = "#3b82f6"
    accent_color: str = "#f59e0b"
    danger_color: str = "#ef4444"
    success_color: str = "#10b981"
    background_color: str = "rgba(15, 20, 25, 0.95)"
    grid_color: str = "rgba(255, 255, 255, 0.1)"
    font_family: str = "Inter, system-ui, sans-serif"

class PremiumChartSystem:
    """
    High-quality charting system for cryptocurrency data visualization
    """
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.config = ChartConfig()
        self.chart_cache = {}
        
    def get_coin_data(self, ticker: str = None, limit: int = 100) -> pd.DataFrame:
        """Retrieve coin data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if ticker:
                query = """
                SELECT * FROM coins 
                WHERE ticker = ? AND current_price_usd IS NOT NULL 
                ORDER BY enrichment_timestamp DESC 
                LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=(ticker, limit))
            else:
                query = """
                SELECT * FROM coins 
                WHERE current_price_usd IS NOT NULL 
                ORDER BY market_cap_usd DESC NULLS LAST
                LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=(limit,))
            
            conn.close()
            return df
            
        except Exception as e:
            st.error(f"Database error: {e}")
            return pd.DataFrame()
    
    def create_price_chart(self, coin_data: Dict, historical_data: List[Dict] = None) -> go.Figure:
        """
        Create an advanced price chart with technical indicators
        """
        fig = go.Figure()
        
        # Sample data for demonstration (in production, use real historical data)
        if not historical_data:
            # Generate sample historical data
            current_price = coin_data.get('current_price_usd', 1.0)
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            
            # Generate realistic price movement
            np.random.seed(42)  # For consistent demo data
            price_changes = np.random.normal(0, 0.05, 30)  # 5% daily volatility
            prices = [current_price]
            
            for change in price_changes[1:]:
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 0.000001))  # Prevent negative prices
            
            historical_data = [
                {"date": date.isoformat(), "price": price, "volume": np.random.randint(10000, 100000)}
                for date, price in zip(dates, prices)
            ]
        
        # Extract data for plotting
        dates = [datetime.fromisoformat(item["date"]) for item in historical_data]
        prices = [item["price"] for item in historical_data]
        volumes = [item.get("volume", 0) for item in historical_data]
        
        # Main price line with gradient fill
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name='Price (USD)',
            line=dict(
                color=self.config.primary_color,
                width=3,
                shape='spline'
            ),
            fill='tonexty',
            fillcolor=f'rgba(16, 185, 129, 0.1)',
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Price: $%{y:.8f}<br>' +
                         '<extra></extra>'
        ))
        
        # Add volume bars (secondary y-axis)
        fig.add_trace(go.Bar(
            x=dates,
            y=volumes,
            name='Volume',
            marker_color=f'rgba(59, 130, 246, 0.3)',
            yaxis='y2',
            hovertemplate='<b>Volume</b><br>' +
                         'Date: %{x}<br>' +
                         'Volume: %{y:,.0f}<br>' +
                         '<extra></extra>'
        ))
        
        # Add moving averages
        if len(prices) >= 7:
            ma7 = pd.Series(prices).rolling(window=7).mean()
            fig.add_trace(go.Scatter(
                x=dates,
                y=ma7,
                mode='lines',
                name='7-Day MA',
                line=dict(
                    color=self.config.secondary_color,
                    width=2,
                    dash='dash'
                ),
                hovertemplate='<b>7-Day MA</b><br>' +
                             'Date: %{x}<br>' +
                             'Price: $%{y:.8f}<br>' +
                             '<extra></extra>'
            ))
        
        if len(prices) >= 14:
            ma14 = pd.Series(prices).rolling(window=14).mean()
            fig.add_trace(go.Scatter(
                x=dates,
                y=ma14,
                mode='lines',
                name='14-Day MA',
                line=dict(
                    color=self.config.accent_color,
                    width=2,
                    dash='dot'
                ),
                hovertemplate='<b>14-Day MA</b><br>' +
                             'Date: %{x}<br>' +
                             'Price: $%{y:.8f}<br>' +
                             '<extra></extra>'
            ))
        
        # Calculate support and resistance levels
        recent_prices = prices[-14:] if len(prices) >= 14 else prices
        resistance = max(recent_prices)
        support = min(recent_prices)
        
        # Add support and resistance lines
        fig.add_hline(
            y=resistance,
            line_dash="dash",
            line_color=self.config.danger_color,
            annotation_text="Resistance",
            annotation_position="right"
        )
        
        fig.add_hline(
            y=support,
            line_dash="dash", 
            line_color=self.config.success_color,
            annotation_text="Support",
            annotation_position="right"
        )
        
        # Update layout with premium styling
        fig.update_layout(
            title=dict(
                text=f"<b>{coin_data.get('ticker', 'Unknown')} Price Analysis</b>",
                font=dict(size=24, color='white', family=self.config.font_family),
                x=0.5,
                xanchor='center'
            ),
            template=self.config.theme,
            height=self.config.height,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="rgba(255,255,255,0.2)",
                borderwidth=1
            ),
            xaxis=dict(
                title="Date",
                gridcolor=self.config.grid_color,
                showgrid=True,
                zeroline=False,
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                title="Price (USD)",
                gridcolor=self.config.grid_color,
                showgrid=True,
                zeroline=False,
                tickformat='.8f',
                tickfont=dict(color='white')
            ),
            yaxis2=dict(
                title="Volume",
                overlaying='y',
                side='right',
                showgrid=False,
                tickfont=dict(color='white')
            ),
            plot_bgcolor=self.config.background_color,
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=60, b=0),
            hovermode='x unified'
        )
        
        return fig
    
    def create_market_overview_chart(self, coin_data: pd.DataFrame) -> go.Figure:
        """
        Create market overview with multiple visualizations
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Market Cap Distribution", "Price vs Volume", "Discovery MC Analysis", "Smart Wallets"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.10
        )
        
        # 1. Market Cap Distribution (Histogram)
        market_cap_data = coin_data[coin_data['market_cap_usd'].notna()]['market_cap_usd']
        if not market_cap_data.empty:
            fig.add_trace(
                go.Histogram(
                    x=market_cap_data,
                    nbinsx=20,
                    marker_color=self.config.primary_color,
                    opacity=0.7,
                    name="Market Cap Distribution"
                ),
                row=1, col=1
            )
        
        # 2. Price vs Volume Scatter
        scatter_data = coin_data[
            (coin_data['current_price_usd'].notna()) & 
            (coin_data['current_volume_24h'].notna())
        ]
        if not scatter_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=scatter_data['current_volume_24h'],
                    y=scatter_data['current_price_usd'],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=scatter_data['market_cap_usd'],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Market Cap", x=0.48, len=0.4)
                    ),
                    text=scatter_data['ticker'],
                    hovertemplate='<b>%{text}</b><br>' +
                                 'Volume: $%{x:,.0f}<br>' +
                                 'Price: $%{y:.8f}<br>' +
                                 '<extra></extra>',
                    name="Price vs Volume"
                ),
                row=1, col=2
            )
        
        # 3. Discovery MC Analysis (Bar chart)
        discovery_data = coin_data[coin_data['discovery_mc'].notna()].nlargest(10, 'discovery_mc')
        if not discovery_data.empty:
            fig.add_trace(
                go.Bar(
                    x=discovery_data['ticker'],
                    y=discovery_data['discovery_mc'],
                    marker_color=self.config.accent_color,
                    opacity=0.8,
                    name="Discovery MC"
                ),
                row=2, col=1
            )
        
        # 4. Smart Wallets Analysis (Horizontal bar)
        smart_wallets_data = coin_data[coin_data['smart_wallets'].notna()].nlargest(10, 'smart_wallets')
        if not smart_wallets_data.empty:
            fig.add_trace(
                go.Bar(
                    x=smart_wallets_data['smart_wallets'],
                    y=smart_wallets_data['ticker'],
                    orientation='h',
                    marker_color=self.config.secondary_color,
                    opacity=0.8,
                    name="Smart Wallets"
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="<b>Market Overview Dashboard</b>",
                font=dict(size=24, color='white', family=self.config.font_family),
                x=0.5,
                xanchor='center'
            ),
            template=self.config.theme,
            height=800,
            showlegend=False,
            plot_bgcolor=self.config.background_color,
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    def create_performance_chart(self, coin_data: pd.DataFrame) -> go.Figure:
        """
        Create performance comparison chart
        """
        # Get top performers by price change
        performance_data = coin_data[coin_data['price_change_24h'].notna()].copy()
        
        if performance_data.empty:
            return self.create_empty_chart("No performance data available")
        
        # Sort by price change
        performance_data = performance_data.sort_values('price_change_24h', ascending=True)
        
        # Take top 20 performers (10 best, 10 worst)
        top_performers = performance_data.tail(10)
        worst_performers = performance_data.head(10)
        combined_data = pd.concat([worst_performers, top_performers])
        
        # Create color map
        colors = [self.config.danger_color if change < 0 else self.config.success_color 
                 for change in combined_data['price_change_24h']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=combined_data['price_change_24h'],
            y=combined_data['ticker'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255,255,255,0.2)', width=1)
            ),
            text=[f"{change:+.2f}%" for change in combined_data['price_change_24h']],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>' +
                         'Change: %{x:+.2f}%<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>24H Performance Leaders & Laggards</b>",
                font=dict(size=20, color='white', family=self.config.font_family),
                x=0.5,
                xanchor='center'
            ),
            template=self.config.theme,
            height=600,
            xaxis=dict(
                title="24H Price Change (%)",
                gridcolor=self.config.grid_color,
                zeroline=True,
                zerolinecolor='rgba(255,255,255,0.3)',
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                title="",
                tickfont=dict(color='white')
            ),
            plot_bgcolor=self.config.background_color,
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=100, r=50, t=60, b=50)
        )
        
        return fig
    
    def create_correlation_heatmap(self, coin_data: pd.DataFrame) -> go.Figure:
        """
        Create correlation heatmap for various metrics
        """
        # Select numeric columns for correlation
        numeric_cols = [
            'current_price_usd', 'market_cap_usd', 'current_volume_24h',
            'price_change_24h', 'discovery_mc', 'liquidity', 'smart_wallets'
        ]
        
        # Filter to available columns
        available_cols = [col for col in numeric_cols if col in coin_data.columns]
        correlation_data = coin_data[available_cols].corr()
        
        if correlation_data.empty:
            return self.create_empty_chart("Insufficient data for correlation analysis")
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_data.values,
            x=correlation_data.columns,
            y=correlation_data.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_data.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10, "color": "white"},
            hoverongaps=False,
            hovertemplate='<b>%{y} vs %{x}</b><br>' +
                         'Correlation: %{z:.3f}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>Metrics Correlation Matrix</b>",
                font=dict(size=20, color='white', family=self.config.font_family),
                x=0.5,
                xanchor='center'
            ),
            template=self.config.theme,
            height=500,
            plot_bgcolor=self.config.background_color,
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=60, b=50)
        )
        
        return fig
    
    def create_empty_chart(self, message: str) -> go.Figure:
        """Create an empty chart with a message"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            font=dict(size=16, color='rgba(255,255,255,0.6)'),
            showarrow=False
        )
        
        fig.update_layout(
            template=self.config.theme,
            height=400,
            plot_bgcolor=self.config.background_color,
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        
        return fig
    
    def render_chart_dashboard(self, coin_data: pd.DataFrame, selected_coin: Dict = None):
        """
        Render the complete chart dashboard
        """
        if coin_data.empty:
            st.warning("No data available for charting")
            return
        
        # Chart selection tabs
        chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs([
            "📈 Market Overview", 
            "🎯 Performance", 
            "🔗 Correlations",
            "💎 Individual Coin"
        ])
        
        with chart_tab1:
            with st.spinner("Generating market overview..."):
                overview_chart = self.create_market_overview_chart(coin_data)
                st.plotly_chart(overview_chart, use_container_width=True)
        
        with chart_tab2:
            with st.spinner("Analyzing performance..."):
                performance_chart = self.create_performance_chart(coin_data)
                st.plotly_chart(performance_chart, use_container_width=True)
        
        with chart_tab3:
            with st.spinner("Computing correlations..."):
                correlation_chart = self.create_correlation_heatmap(coin_data)
                st.plotly_chart(correlation_chart, use_container_width=True)
        
        with chart_tab4:
            if selected_coin:
                with st.spinner("Loading coin analysis..."):
                    price_chart = self.create_price_chart(selected_coin)
                    st.plotly_chart(price_chart, use_container_width=True)
            else:
                st.info("Select a coin from the Coins tab to view individual analysis")
                
                # Coin selector for chart viewing
                available_coins = coin_data[coin_data['ticker'].notna()]['ticker'].unique()
                if len(available_coins) > 0:
                    selected = st.selectbox(
                        "Choose a coin for analysis:",
                        options=available_coins,
                        key="chart_coin_selector"
                    )
                    
                    if selected:
                        coin_info = coin_data[coin_data['ticker'] == selected].iloc[0].to_dict()
                        price_chart = self.create_price_chart(coin_info)
                        st.plotly_chart(price_chart, use_container_width=True)

# Global instance for easy import
premium_chart_system = PremiumChartSystem()