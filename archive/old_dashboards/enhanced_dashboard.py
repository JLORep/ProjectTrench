#!/usr/bin/env python3
"""
ENHANCED TRENCHCOAT DASHBOARD
Comprehensive Solana memecoin data with Top 10 strategies
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import json
import sqlite3
from typing import Dict, List, Optional, Any
import time

# Import our enhanced systems
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data.comprehensive_enricher import ComprehensiveEnricher, ComprehensiveTokenData, store_comprehensive_data
from src.strategies.top10_strategies import Top10Strategies, StrategyResult
from src.analysis.rug_intelligence import RugIntelligenceEngine
from src.trading.automated_trader import AutomatedTrader, Trade, TradeStatus
from src.data.database import CoinDatabase
from auth_config import SimpleAuth

# Page config
st.set_page_config(
    page_title="TrenchCoat Elite Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown("""
<style>
    /* Enhanced professional styling */
    :root {
        --primary-color: #1f2937;
        --secondary-color: #374151;
        --accent-color: #10b981;
        --danger-color: #ef4444;
        --warning-color: #f59e0b;
        --success-color: #059669;
        --text-primary: #f9fafb;
        --text-secondary: #9ca3af;
        --background: #111827;
        --surface: #1f2937;
        --surface-hover: #374151;
    }
    
    .stApp {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        color: var(--text-primary);
    }
    
    /* Strategy cards */
    .strategy-card {
        background: linear-gradient(135deg, var(--surface) 0%, var(--surface-hover) 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--secondary-color);
        box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.25);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .strategy-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px -5px rgba(0, 0, 0, 0.4);
        border-color: var(--accent-color);
    }
    
    /* Performance cards */
    .perf-card {
        background: var(--surface);
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid var(--accent-color);
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .perf-card-danger {
        border-left-color: var(--danger-color);
    }
    
    .perf-card-warning {
        border-left-color: var(--warning-color);
    }
    
    /* Data enrichment status */
    .enrichment-status {
        background: linear-gradient(90deg, var(--surface) 0%, rgba(16, 185, 129, 0.1) 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--accent-color);
        margin: 0.5rem 0;
    }
    
    /* Strategy ranking */
    .strategy-rank {
        display: inline-block;
        background: var(--accent-color);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-weight: bold;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    
    .strategy-rank-1 { background: #ffd700; color: #000; }
    .strategy-rank-2 { background: #c0c0c0; color: #000; }
    .strategy-rank-3 { background: #cd7f32; color: #fff; }
    
    /* Token data table */
    .token-table {
        background: var(--surface);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--secondary-color);
        margin: 1rem 0;
    }
    
    /* Main header enhanced */
    .main-header-enhanced {
        background: linear-gradient(135deg, var(--surface) 0%, var(--secondary-color) 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 2px solid var(--accent-color);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .main-header-enhanced::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(16, 185, 129, 0.05) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .main-title-enhanced {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-color) 0%, #06d6a0 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle-enhanced {
        color: var(--text-secondary);
        font-size: 1.3rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Data source badges */
    .data-source-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: var(--accent-color);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.7rem;
        margin: 0.2rem;
        border: 1px solid var(--accent-color);
    }
    
    /* Strategy performance indicators */
    .strategy-perf {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
    }
    
    .strategy-metric {
        text-align: center;
        flex: 1;
    }
    
    .strategy-metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--accent-color);
    }
    
    .strategy-metric-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

class EnhancedTrenchCoatDashboard:
    """Enhanced dashboard with comprehensive data and strategy testing"""
    
    def __init__(self):
        self.db = CoinDatabase()
        self.enricher = None
        self.strategies = Top10Strategies()
        self.rug_engine = RugIntelligenceEngine(self.db)
        self.trader = AutomatedTrader()
        
        # Initialize session state
        if 'comprehensive_data' not in st.session_state:
            st.session_state.comprehensive_data = []
        if 'strategy_results' not in st.session_state:
            st.session_state.strategy_results = {}
        if 'optimal_combination' not in st.session_state:
            st.session_state.optimal_combination = {}
        if 'enrichment_running' not in st.session_state:
            st.session_state.enrichment_running = False
        if 'daily_coins' not in st.session_state:
            st.session_state.daily_coins = 75
        if 'trading_coins' not in st.session_state:
            st.session_state.trading_coins = 30
    
    def render_enhanced_header(self):
        """Render enhanced header"""
        st.markdown("""
        <div class="main-header-enhanced">
            <h1 class="main-title-enhanced">💎 TrenchCoat Elite Pro</h1>
            <p class="main-subtitle-enhanced">Advanced Solana Memecoin Trading • Comprehensive Data • Top 10 Strategies</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_data_enrichment_panel(self):
        """Render comprehensive data enrichment panel"""
        st.subheader("🔍 Comprehensive Data Enrichment")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("""
            <div class="enrichment-status">
                <strong>Multi-API Data Sources:</strong><br>
                <span class="data-source-badge">DexScreener</span>
                <span class="data-source-badge">Birdeye</span>
                <span class="data-source-badge">Jupiter</span>
                <span class="data-source-badge">Solscan</span>
                <span class="data-source-badge">CoinGecko</span>
                <span class="data-source-badge">RugCheck</span>
                <span class="data-source-badge">Honeypot.is</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🚀 Enrich Sample Data", type="primary"):
                st.session_state.enrichment_running = True
                self.run_sample_enrichment()
        
        with col3:
            enriched_count = len(st.session_state.comprehensive_data)
            st.metric("Enriched Tokens", enriched_count)
        
        # Show enrichment progress
        if st.session_state.enrichment_running:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate enrichment progress
            for i in range(101):
                progress_bar.progress(i)
                status_text.text(f'Enriching tokens... {i}%')
                time.sleep(0.02)
            
            st.session_state.enrichment_running = False
            st.success("✅ Sample data enrichment complete!")
    
    def run_sample_enrichment(self):
        """Run sample data enrichment"""
        # Generate sample comprehensive data
        sample_tokens = []
        
        # Popular Solana tokens for demo
        sample_contracts = [
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "So11111111111111111111111111111111111111112",     # SOL  
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",     # USDT
        ]
        
        for i, contract in enumerate(sample_contracts):
            token = ComprehensiveTokenData(
                contract_address=contract,
                symbol=f"TOKEN{i+1}" if i > 2 else ["USDC", "SOL", "USDT"][i],
                name=f"Sample Token {i+1}",
                price_usd=np.random.uniform(0.001, 10.0),
                price_change_5m=np.random.normal(2, 10),
                price_change_1h=np.random.normal(5, 15),
                price_change_6h=np.random.normal(8, 20),
                price_change_24h=np.random.normal(12, 25),
                volume_5m=np.random.uniform(1000, 50000),
                volume_1h=np.random.uniform(5000, 200000),
                volume_6h=np.random.uniform(20000, 500000),
                volume_24h=np.random.uniform(50000, 2000000),
                market_cap=np.random.uniform(100000, 50000000),
                liquidity_usd=np.random.uniform(10000, 1000000),
                holder_count=np.random.randint(100, 5000),
                top_10_holders_percent=np.random.uniform(15, 60),
                whale_count=np.random.randint(1, 15),
                pair_count=np.random.randint(2, 8),
                main_dex="Raydium",
                twitter_followers=np.random.randint(100, 10000),
                telegram_members=np.random.randint(50, 5000),
                website_url="https://example.com",
                rsi_14=np.random.uniform(20, 80),
                rug_risk_score=np.random.uniform(0, 0.5),
                honeypot_risk=np.random.uniform(0, 0.3),
                mint_disabled=np.random.choice([True, False]),
                freeze_disabled=np.random.choice([True, False]),
                buy_pressure=np.random.uniform(0.3, 0.8),
                sell_pressure=np.random.uniform(0.2, 0.7),
                data_sources=["dexscreener", "birdeye", "jupiter", "solscan", "coingecko"]
            )
            sample_tokens.append(token)
        
        # Add more sample tokens to reach 75
        for i in range(3, 75):
            token = ComprehensiveTokenData(
                contract_address=f"sample_contract_{i}",
                symbol=f"MEME{i}",
                name=f"Memecoin {i}",
                price_usd=np.random.uniform(0.0001, 1.0),
                price_change_5m=np.random.normal(0, 20),
                price_change_1h=np.random.normal(0, 30),
                price_change_24h=np.random.normal(0, 50),
                volume_24h=np.random.uniform(1000, 500000),
                market_cap=np.random.uniform(10000, 5000000),
                liquidity_usd=np.random.uniform(1000, 100000),
                holder_count=np.random.randint(10, 1000),
                top_10_holders_percent=np.random.uniform(20, 80),
                whale_count=np.random.randint(0, 10),
                rug_risk_score=np.random.uniform(0, 1),
                honeypot_risk=np.random.uniform(0, 0.8),
                mint_disabled=np.random.choice([True, False]),
                freeze_disabled=np.random.choice([True, False]),
                data_sources=np.random.choice(["dexscreener", "birdeye", "jupiter"], size=np.random.randint(1, 4), replace=False).tolist()
            )
            sample_tokens.append(token)
        
        st.session_state.comprehensive_data = sample_tokens
    
    def render_strategy_testing_panel(self):
        """Render strategy testing and results"""
        st.subheader("🧪 Top 10 Strategy Testing")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Daily Trading Parameters:**")
            daily_coins = st.number_input("Daily New Coins", min_value=50, max_value=200, value=75, step=5)
            trading_coins = st.number_input("Coins to Trade", min_value=10, max_value=50, value=30, step=5)
            
            st.session_state.daily_coins = daily_coins
            st.session_state.trading_coins = trading_coins
            
            st.info(f"📊 **Strategy:** Trade {trading_coins} best coins out of {daily_coins} daily opportunities")
        
        with col2:
            if st.button("🚀 Run Strategy Backtests", type="primary"):
                self.run_strategy_backtests()
        
        # Show strategy results if available
        if st.session_state.strategy_results:
            self.render_strategy_results()
    
    def run_strategy_backtests(self):
        """Run backtests for all strategies"""
        if not st.session_state.comprehensive_data:
            st.error("No data available. Please enrich data first.")
            return
        
        with st.spinner("Running strategy backtests..."):
            # Generate 30 days of historical data
            historical_data = []
            for day in range(30):
                # Simulate daily variation in the data
                daily_tokens = []
                for token in st.session_state.comprehensive_data:
                    # Create a variation of the token for this day
                    varied_token = ComprehensiveTokenData(
                        contract_address=f"{token.contract_address}_day_{day}",
                        symbol=token.symbol,
                        name=token.name,
                        price_usd=token.price_usd * np.random.uniform(0.8, 1.2),
                        price_change_5m=np.random.normal(0, 15),
                        price_change_1h=np.random.normal(0, 20),
                        price_change_24h=np.random.normal(0, 30),
                        volume_24h=token.volume_24h * np.random.uniform(0.5, 2.0),
                        market_cap=token.market_cap * np.random.uniform(0.9, 1.1),
                        liquidity_usd=token.liquidity_usd * np.random.uniform(0.8, 1.2),
                        holder_count=max(1, int(token.holder_count * np.random.uniform(0.95, 1.05))),
                        top_10_holders_percent=max(5, min(95, token.top_10_holders_percent + np.random.normal(0, 5))),
                        whale_count=max(0, int(token.whale_count + np.random.randint(-2, 3))),
                        rug_risk_score=max(0, min(1, token.rug_risk_score + np.random.normal(0, 0.1))),
                        honeypot_risk=max(0, min(1, token.honeypot_risk + np.random.normal(0, 0.05))),
                        mint_disabled=token.mint_disabled,
                        freeze_disabled=token.freeze_disabled,
                        data_sources=token.data_sources
                    )
                    daily_tokens.append(varied_token)
                historical_data.extend(daily_tokens)
            
            # Run all strategy backtests
            results = self.strategies.backtest_all_strategies(historical_data, 30)
            st.session_state.strategy_results = results
            
            # Get optimal combination
            optimal = self.strategies.get_optimal_strategy_combination()
            st.session_state.optimal_combination = optimal
        
        st.success("✅ Strategy backtests complete!")
    
    def render_strategy_results(self):
        """Render strategy backtest results"""
        st.subheader("📊 Strategy Performance Results")
        
        results = st.session_state.strategy_results
        
        # Strategy ranking
        ranked_strategies = sorted(results.items(), key=lambda x: x[1].total_return, reverse=True)
        
        # Top 3 strategies highlight
        col1, col2, col3 = st.columns(3)
        
        for i, (name, result) in enumerate(ranked_strategies[:3]):
            col = [col1, col2, col3][i]
            rank_class = ["strategy-rank-1", "strategy-rank-2", "strategy-rank-3"][i]
            
            with col:
                st.markdown(f"""
                <div class="strategy-card">
                    <span class="{rank_class}">#{i+1}</span>
                    <h3>{name.replace('_', ' ').title()}</h3>
                    <div class="strategy-perf">
                        <div class="strategy-metric">
                            <div class="strategy-metric-value">{result.total_return:.1f}%</div>
                            <div class="strategy-metric-label">Total Return</div>
                        </div>
                        <div class="strategy-metric">
                            <div class="strategy-metric-value">{result.win_rate:.1%}</div>
                            <div class="strategy-metric-label">Win Rate</div>
                        </div>
                        <div class="strategy-metric">
                            <div class="strategy-metric-value">{result.trades_per_day:.1f}</div>
                            <div class="strategy-metric-label">Trades/Day</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed results table
        st.subheader("📈 Detailed Strategy Comparison")
        
        # Create comparison DataFrame
        comparison_data = []
        for name, result in results.items():
            comparison_data.append({
                'Strategy': name.replace('_', ' ').title(),
                'Total Return (%)': f"{result.total_return:.1f}%",
                'Win Rate (%)': f"{result.win_rate:.1%}",
                'Trades/Day': f"{result.trades_per_day:.1f}",
                'Sharpe Ratio': f"{result.sharpe_ratio:.2f}",
                'Max Drawdown (%)': f"{result.max_drawdown:.1f}%",
                'Profit Factor': f"{result.profit_factor:.2f}",
                'Best Trade (%)': f"{result.best_trade:.1f}%",
                'Worst Trade (%)': f"{result.worst_trade:.1f}%"
            })
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
        
        # Performance visualization
        self.render_strategy_performance_chart(results)
        
        # Optimal combination
        self.render_optimal_combination()
    
    def render_strategy_performance_chart(self, results: Dict[str, StrategyResult]):
        """Render strategy performance visualization"""
        st.subheader("📊 Strategy Performance Visualization")
        
        # Create performance comparison chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total Return vs Win Rate', 'Risk-Return Profile', 
                          'Trade Frequency vs Success Rate', 'Sharpe Ratio Comparison'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "bar"}]]
        )
        
        strategies = list(results.keys())
        returns = [results[s].total_return for s in strategies]
        win_rates = [results[s].win_rate * 100 for s in strategies]
        sharpe_ratios = [results[s].sharpe_ratio for s in strategies]
        max_drawdowns = [results[s].max_drawdown for s in strategies]
        trades_per_day = [results[s].trades_per_day for s in strategies]
        
        # Return vs Win Rate scatter
        fig.add_trace(
            go.Scatter(
                x=win_rates, y=returns,
                mode='markers+text',
                text=[s.replace('_', ' ').title()[:15] for s in strategies],
                textposition="top center",
                marker=dict(size=10, color=returns, colorscale='Viridis'),
                name="Strategies"
            ),
            row=1, col=1
        )
        
        # Risk-Return scatter
        fig.add_trace(
            go.Scatter(
                x=max_drawdowns, y=returns,
                mode='markers+text',
                text=[s.replace('_', ' ').title()[:15] for s in strategies],
                textposition="top center",
                marker=dict(size=10, color=sharpe_ratios, colorscale='RdYlGn'),
                name="Risk-Return"
            ),
            row=1, col=2
        )
        
        # Trade frequency vs success
        fig.add_trace(
            go.Scatter(
                x=trades_per_day, y=win_rates,
                mode='markers+text',
                text=[s.replace('_', ' ').title()[:15] for s in strategies],
                textposition="top center",
                marker=dict(size=10, color='lightblue'),
                name="Frequency vs Success"
            ),
            row=2, col=1
        )
        
        # Sharpe ratio bar chart
        fig.add_trace(
            go.Bar(
                x=[s.replace('_', ' ').title() for s in strategies],
                y=sharpe_ratios,
                marker_color=sharpe_ratios,
                marker_colorscale='RdYlGn',
                name="Sharpe Ratio"
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            showlegend=False,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Win Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="Total Return (%)", row=1, col=1)
        fig.update_xaxes(title_text="Max Drawdown (%)", row=1, col=2)
        fig.update_yaxes(title_text="Total Return (%)", row=1, col=2)
        fig.update_xaxes(title_text="Trades/Day", row=2, col=1)
        fig.update_yaxes(title_text="Win Rate (%)", row=2, col=1)
        fig.update_xaxes(title_text="Strategy", row=2, col=2)
        fig.update_yaxes(title_text="Sharpe Ratio", row=2, col=2)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_optimal_combination(self):
        """Render optimal strategy combination"""
        if not st.session_state.optimal_combination:
            return
        
        optimal = st.session_state.optimal_combination
        
        st.subheader("🎯 Optimal Strategy Combination")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div class="perf-card">
                <h3>📈 Expected Performance</h3>
                <p><strong>Daily Return:</strong> {optimal['expected_daily_return']:.2f}%</p>
                <p><strong>Combined Win Rate:</strong> {optimal['combined_win_rate']:.1%}</p>
                <p><strong>Monthly Return:</strong> {optimal['expected_daily_return'] * 30:.1f}%</p>
                <p><strong>Annual Return:</strong> {optimal['expected_daily_return'] * 365:.0f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Portfolio allocation pie chart
            allocations = optimal['portfolio_allocation']
            
            fig = go.Figure(data=[go.Pie(
                labels=[name.replace('_', ' ').title() for name in allocations.keys()],
                values=list(allocations.values()),
                hole=0.4,
                marker_colors=px.colors.qualitative.Set3
            )])
            
            fig.update_layout(
                title="Optimal Portfolio Allocation",
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed allocation table
        st.markdown("**Portfolio Allocation Details:**")
        allocation_df = pd.DataFrame([
            {
                'Strategy': name.replace('_', ' ').title(),
                'Allocation (%)': f"{allocation:.1f}%",
                'Expected Contribution': f"{allocation * optimal['expected_daily_return'] / 100:.3f}%"
            }
            for name, allocation in allocations.items()
        ])
        st.dataframe(allocation_df, use_container_width=True)
    
    def render_comprehensive_token_data(self):
        """Render comprehensive token data table"""
        if not st.session_state.comprehensive_data:
            st.info("No comprehensive data available. Please run data enrichment first.")
            return
        
        st.subheader("📊 Comprehensive Token Data")
        
        # Create detailed DataFrame
        token_data = []
        for token in st.session_state.comprehensive_data[:20]:  # Show top 20
            token_data.append({
                'Symbol': token.symbol,
                'Price (USD)': f"${token.price_usd:.6f}",
                'Market Cap': f"${token.market_cap:,.0f}",
                'Volume 24h': f"${token.volume_24h:,.0f}",
                'Change 5m (%)': f"{token.price_change_5m:+.1f}%",
                'Change 1h (%)': f"{token.price_change_1h:+.1f}%",
                'Change 24h (%)': f"{token.price_change_24h:+.1f}%",
                'Liquidity': f"${token.liquidity_usd:,.0f}",
                'Holders': f"{token.holder_count:,}",
                'Top10 (%)': f"{token.top_10_holders_percent:.1f}%",
                'Whales': token.whale_count,
                'Rug Risk': f"{token.rug_risk_score:.2f}",
                'Data Sources': len(token.data_sources)
            })
        
        df = pd.DataFrame(token_data)
        st.dataframe(df, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_mcap = np.mean([t.market_cap for t in st.session_state.comprehensive_data])
            st.metric("Avg Market Cap", f"${avg_mcap:,.0f}")
        
        with col2:
            avg_volume = np.mean([t.volume_24h for t in st.session_state.comprehensive_data])
            st.metric("Avg Volume 24h", f"${avg_volume:,.0f}")
        
        with col3:
            avg_holders = np.mean([t.holder_count for t in st.session_state.comprehensive_data])
            st.metric("Avg Holders", f"{avg_holders:,.0f}")
        
        with col4:
            avg_risk = np.mean([t.rug_risk_score for t in st.session_state.comprehensive_data])
            st.metric("Avg Rug Risk", f"{avg_risk:.2f}")
    
    def render_sidebar_enhanced(self):
        """Render enhanced sidebar"""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0; border-bottom: 2px solid var(--accent-color);">
                <h1 style="margin: 0; color: var(--accent-color);">💎 TrenchCoat</h1>
                <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary);">Elite Pro Dashboard</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation
            st.markdown("### 📋 Navigation")
            page = st.radio(
                "Select Page",
                [
                    "🏠 Enhanced Dashboard", 
                    "🔍 Data Enrichment", 
                    "🧪 Strategy Testing",
                    "📊 Comprehensive Data",
                    "⚙️ Settings"
                ],
                label_visibility="collapsed"
            )
            
            # Enhanced stats
            st.markdown("---")
            st.markdown("### 📊 System Status")
            
            enriched_tokens = len(st.session_state.comprehensive_data)
            tested_strategies = len(st.session_state.strategy_results)
            
            st.success(f"📊 **Enriched Tokens:** {enriched_tokens}")
            st.info(f"🧪 **Tested Strategies:** {tested_strategies}/10")
            
            if st.session_state.optimal_combination:
                expected_return = st.session_state.optimal_combination['expected_daily_return']
                st.metric("Expected Daily Return", f"{expected_return:.2f}%")
            
            # Quick actions
            st.markdown("---")
            st.markdown("### ⚡ Quick Actions")
            
            if st.button("🚀 Full System Test", type="primary"):
                if not st.session_state.comprehensive_data:
                    st.session_state.enrichment_running = True
                self.run_sample_enrichment()
                self.run_strategy_backtests()
                st.success("✅ Full system test complete!")
            
            if st.button("📤 Export Results"):
                if st.session_state.strategy_results:
                    # Create export data
                    export_data = {
                        'timestamp': datetime.now().isoformat(),
                        'strategy_results': {
                            name: {
                                'total_return': result.total_return,
                                'win_rate': result.win_rate,
                                'trades_per_day': result.trades_per_day,
                                'sharpe_ratio': result.sharpe_ratio
                            }
                            for name, result in st.session_state.strategy_results.items()
                        },
                        'optimal_combination': st.session_state.optimal_combination
                    }
                    
                    st.download_button(
                        "Download Results JSON",
                        json.dumps(export_data, indent=2),
                        "trenchcoat_results.json",
                        "application/json"
                    )
            
            return page
    
    def run(self):
        """Main dashboard runner"""
        # Authentication
        auth = SimpleAuth()
        if not auth.check_auth():
            return
        
        # Render sidebar and get selected page
        page = self.render_sidebar_enhanced()
        
        # Render header
        self.render_enhanced_header()
        
        # Route to selected page
        if page == "🏠 Enhanced Dashboard":
            col1, col2 = st.columns([2, 1])
            
            with col1:
                self.render_data_enrichment_panel()
                self.render_strategy_testing_panel()
            
            with col2:
                if st.session_state.strategy_results:
                    # Show top 3 strategies summary
                    st.subheader("🏆 Top Strategies")
                    results = st.session_state.strategy_results
                    top_3 = sorted(results.items(), key=lambda x: x[1].total_return, reverse=True)[:3]
                    
                    for i, (name, result) in enumerate(top_3):
                        st.markdown(f"""
                        **#{i+1} {name.replace('_', ' ').title()}**
                        - Return: {result.total_return:.1f}%
                        - Win Rate: {result.win_rate:.1%}
                        - Trades/Day: {result.trades_per_day:.1f}
                        """)
                
                if st.session_state.optimal_combination:
                    st.subheader("🎯 Optimal Strategy")
                    optimal = st.session_state.optimal_combination
                    st.metric("Expected Daily Return", f"{optimal['expected_daily_return']:.2f}%")
                    st.metric("Combined Win Rate", f"{optimal['combined_win_rate']:.1%}")
        
        elif page == "🔍 Data Enrichment":
            self.render_data_enrichment_panel()
            self.render_comprehensive_token_data()
        
        elif page == "🧪 Strategy Testing":
            self.render_strategy_testing_panel()
        
        elif page == "📊 Comprehensive Data":
            self.render_comprehensive_token_data()
        
        elif page == "⚙️ Settings":
            st.subheader("⚙️ System Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Data Enrichment Settings**")
                st.number_input("API Rate Limit (calls/min)", min_value=10, max_value=1000, value=100)
                st.checkbox("Enable Real-time Updates", True)
                st.selectbox("Primary Data Source", ["DexScreener", "Birdeye", "Jupiter"])
            
            with col2:
                st.markdown("**Strategy Settings**")
                st.slider("Risk Tolerance", 0.0, 1.0, 0.5, 0.1)
                st.slider("Position Size Limit (%)", 1, 10, 5)
                st.checkbox("Enable Auto-trading", False)

# Main app
def main():
    dashboard = EnhancedTrenchCoatDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()