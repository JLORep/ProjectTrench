#!/usr/bin/env python3
"""
Premium UI Components for TrenchCoat Pro
Advanced visualizations and animations
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional
import random

class CoinLogoService:
    """Service to fetch and cache coin logos"""
    
    def __init__(self):
        self.logo_cache = {}
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
    async def get_coin_logo(self, symbol: str) -> Optional[str]:
        """Get coin logo URL from CoinGecko or generate placeholder"""
        if symbol in self.logo_cache:
            return self.logo_cache[symbol]
        
        try:
            # Try to get from CoinGecko
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.coingecko_base}/coins/markets",
                    params={
                        'vs_currency': 'usd',
                        'symbols': symbol.lower(),
                        'per_page': 1
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            logo_url = data[0].get('image', '')
                            self.logo_cache[symbol] = logo_url
                            return logo_url
        except:
            pass
        
        # Generate placeholder if not found
        return self.generate_placeholder_logo(symbol)
    
    def generate_placeholder_logo(self, symbol: str) -> str:
        """Generate a beautiful placeholder logo"""
        # Create gradient background
        size = 100
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Generate random gradient colors based on symbol
        hash_val = hash(symbol)
        hue = (hash_val % 360) / 360
        color1 = self.hsv_to_rgb(hue, 0.8, 0.9)
        color2 = self.hsv_to_rgb((hue + 0.1) % 1, 0.9, 0.7)
        
        # Draw gradient circle
        for i in range(size):
            for j in range(size):
                # Calculate distance from center
                dx = i - size/2
                dy = j - size/2
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance < size/2:
                    # Interpolate colors
                    ratio = distance / (size/2)
                    r = int(color1[0] * (1-ratio) + color2[0] * ratio)
                    g = int(color1[1] * (1-ratio) + color2[1] * ratio)
                    b = int(color1[2] * (1-ratio) + color2[2] * ratio)
                    draw.point((i, j), (r, g, b, 255))
        
        # Add symbol text
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        text = symbol[:3].upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text(
            ((size - text_width) / 2, (size - text_height) / 2),
            text,
            fill=(255, 255, 255, 255),
            font=font
        )
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB"""
        import colorsys
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return tuple(int(x * 255) for x in rgb)


class AdvancedCharts:
    """Advanced chart components"""
    
    @staticmethod
    def create_3d_portfolio_visualization(positions: List[Dict]) -> go.Figure:
        """Create 3D portfolio visualization"""
        if not positions:
            positions = AdvancedCharts.generate_sample_positions()
        
        # Extract data
        tickers = [p['ticker'] for p in positions]
        profits = [p['profit'] for p in positions]
        volumes = [p['volume'] for p in positions]
        scores = [p['score'] for p in positions]
        
        # Create 3D scatter plot
        fig = go.Figure(data=[go.Scatter3d(
            x=volumes,
            y=scores,
            z=profits,
            mode='markers+text',
            text=tickers,
            textposition="top center",
            marker=dict(
                size=[max(10, min(50, abs(p)/10)) for p in profits],
                color=profits,
                colorscale=[
                    [0, '#ef4444'],
                    [0.5, '#6b7280'],
                    [1, '#10b981']
                ],
                showscale=True,
                colorbar=dict(
                    title="Profit ($)",
                    tickfont=dict(color='#9ca3af')
                ),
                line=dict(color='rgba(255,255,255,0.2)', width=1)
            ),
            textfont=dict(color='#f9fafb', size=10)
        )])
        
        # Update layout
        fig.update_layout(
            scene=dict(
                xaxis=dict(
                    title='Volume',
                    gridcolor='rgba(255,255,255,0.1)',
                    showbackground=False,
                    tickfont=dict(color='#9ca3af')
                ),
                yaxis=dict(
                    title='Score',
                    gridcolor='rgba(255,255,255,0.1)',
                    showbackground=False,
                    tickfont=dict(color='#9ca3af')
                ),
                zaxis=dict(
                    title='Profit ($)',
                    gridcolor='rgba(255,255,255,0.1)',
                    showbackground=False,
                    tickfont=dict(color='#9ca3af')
                ),
                bgcolor='rgba(0,0,0,0)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_heatmap_calendar(daily_profits: Dict) -> go.Figure:
        """Create GitHub-style contribution calendar"""
        # Generate data for the last 12 weeks
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=12)
        
        # Create date range
        dates = pd.date_range(start=start_date, end=end_date)
        
        # Generate profit data
        data = []
        for date in dates:
            profit = daily_profits.get(date.strftime('%Y-%m-%d'), 
                                     random.uniform(-100, 500))
            data.append({
                'date': date,
                'profit': profit,
                'week': date.isocalendar()[1],
                'day': date.weekday()
            })
        
        df = pd.DataFrame(data)
        
        # Pivot for heatmap
        heatmap_data = df.pivot(index='day', columns='week', values='profit')
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            colorscale=[
                [0, '#1a1a1a'],
                [0.25, '#ef4444'],
                [0.5, '#6b7280'],
                [0.75, '#10b981'],
                [1, '#059669']
            ],
            showscale=False,
            hoverongaps=False,
            hovertemplate='Week %{x}<br>%{y}<br>Profit: $%{z:.2f}<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(color='#6b7280', size=10),
                zeroline=False
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=0, t=0, b=0),
            height=150
        )
        
        return fig
    
    @staticmethod
    def create_radar_chart(strategy_metrics: Dict) -> go.Figure:
        """Create radar chart for strategy performance"""
        categories = list(strategy_metrics.keys())
        values = list(strategy_metrics.values())
        
        # Close the radar chart
        categories.append(categories[0])
        values.append(values[0])
        
        fig = go.Figure()
        
        # Add trace
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(16, 185, 129, 0.2)',
            line=dict(color='#10b981', width=2),
            marker=dict(size=8, color='#10b981'),
            name='Performance'
        ))
        
        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color='#6b7280', size=10),
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                angularaxis=dict(
                    tickfont=dict(color='#9ca3af', size=12),
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=50, b=50),
            height=300
        )
        
        return fig
    
    @staticmethod
    def create_flow_diagram(stages: List[Dict]) -> go.Figure:
        """Create Sankey diagram for coin flow"""
        # Define nodes
        labels = []
        for stage in ['Discovery', 'Enrichment', 'Analysis', 'Trading', 'Profit', 'Loss']:
            labels.append(stage)
        
        # Define links
        source = [0, 1, 2, 3, 3]  # From nodes
        target = [1, 2, 3, 4, 5]  # To nodes
        value = [100, 85, 70, 50, 20]  # Flow values
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='rgba(255,255,255,0.1)', width=0.5),
                label=labels,
                color=['#3b82f6', '#f59e0b', '#8b5cf6', '#10b981', '#10b981', '#ef4444']
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color='rgba(255,255,255,0.1)'
            )
        )])
        
        # Update layout
        fig.update_layout(
            font=dict(size=12, color='#9ca3af'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=300
        )
        
        return fig
    
    @staticmethod
    def generate_sample_positions() -> List[Dict]:
        """Generate sample position data"""
        positions = []
        tickers = ['BONK', 'WIF', 'PEPE', 'MYRO', 'BOME', 'SLERF']
        
        for ticker in tickers:
            positions.append({
                'ticker': f'${ticker}',
                'profit': random.uniform(-200, 1000),
                'volume': random.uniform(100000, 5000000),
                'score': random.uniform(0.6, 0.95)
            })
        
        return positions


class LiveDataSimulator:
    """Simulate live data updates"""
    
    def __init__(self):
        self.price_history = {}
        self.volume_history = {}
        
    def generate_price_movement(self, ticker: str, current_price: float) -> Dict:
        """Generate realistic price movement"""
        # Initialize history if needed
        if ticker not in self.price_history:
            self.price_history[ticker] = [current_price] * 20
        
        # Generate movement based on momentum
        momentum = np.mean(np.diff(self.price_history[ticker][-5:]))
        volatility = np.std(self.price_history[ticker][-10:])
        
        # Add some randomness with momentum bias
        change_percent = np.random.normal(momentum * 10, volatility * 2)
        change_percent = np.clip(change_percent, -10, 10) / 100
        
        new_price = current_price * (1 + change_percent)
        
        # Update history
        self.price_history[ticker].append(new_price)
        self.price_history[ticker] = self.price_history[ticker][-50:]
        
        return {
            'price': new_price,
            'change_percent': change_percent * 100,
            'momentum': 'bullish' if momentum > 0 else 'bearish',
            'volatility': 'high' if volatility > 0.05 else 'low'
        }
    
    def generate_volume_spike(self, ticker: str, base_volume: float) -> Dict:
        """Generate volume data with occasional spikes"""
        # Random spike probability
        spike_prob = 0.1
        
        if random.random() < spike_prob:
            # Generate spike
            spike_multiplier = random.uniform(3, 10)
            volume = base_volume * spike_multiplier
            is_spike = True
        else:
            # Normal volume with some variance
            volume = base_volume * random.uniform(0.8, 1.2)
            is_spike = False
        
        return {
            'volume': volume,
            'is_spike': is_spike,
            'spike_multiplier': volume / base_volume
        }


class PremiumNotifications:
    """Premium notification system"""
    
    @staticmethod
    def show_success_notification(message: str, profit: float):
        """Show success notification with animation"""
        notification_html = f"""
        <div class="notification success-notification">
            <div class="notification-icon">💰</div>
            <div class="notification-content">
                <div class="notification-title">Successful Trade!</div>
                <div class="notification-message">{message}</div>
                <div class="notification-profit">+${profit:.2f}</div>
            </div>
        </div>
        
        <style>
            .notification {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                gap: 12px;
                box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);
                animation: slideIn 0.5s ease-out, slideOut 0.5s ease-out 3s forwards;
                z-index: 1000;
            }}
            
            .notification-icon {{
                font-size: 24px;
            }}
            
            .notification-title {{
                font-weight: 600;
                margin-bottom: 4px;
            }}
            
            .notification-message {{
                font-size: 14px;
                opacity: 0.9;
            }}
            
            .notification-profit {{
                font-size: 18px;
                font-weight: 700;
                margin-top: 4px;
            }}
            
            @keyframes slideIn {{
                from {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
                to {{
                    transform: translateX(0);
                    opacity: 1;
                }}
            }}
            
            @keyframes slideOut {{
                from {{
                    transform: translateX(0);
                    opacity: 1;
                }}
                to {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
            }}
        </style>
        """
        
        return notification_html


# Additional helper functions
def format_number(num: float) -> str:
    """Format number with appropriate suffix"""
    if num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.2f}K"
    else:
        return f"${num:.2f}"


def generate_mock_enrichment_data():
    """Generate mock enrichment data for demonstration"""
    return {
        'dexscreener': {
            'price': random.uniform(0.0001, 0.01),
            'volume': random.uniform(100000, 5000000),
            'liquidity': random.uniform(50000, 1000000),
            'price_change_24h': random.uniform(-20, 50)
        },
        'birdeye': {
            'holders': random.randint(1000, 50000),
            'top_10_holders_percent': random.uniform(20, 60),
            'unique_traders_24h': random.randint(100, 5000)
        },
        'solscan': {
            'transactions_24h': random.randint(1000, 100000),
            'creator_balance': random.uniform(0, 10),
            'contract_verified': random.choice([True, False])
        },
        'rugcheck': {
            'score': random.uniform(0, 1),
            'risks': random.choice([
                ['High creator holdings'],
                ['Low liquidity'],
                ['Unverified contract'],
                []
            ])
        }
    }