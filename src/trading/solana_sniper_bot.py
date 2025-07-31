#!/usr/bin/env python3
"""
SOLANA MEMECOIN SNIPER BOT
Advanced bot for sniping profitable memecoin opportunities
"""
import streamlit as st
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import logging

from src.data.comprehensive_enricher import ComprehensiveTokenData
from src.strategies.top10_strategies import Top10Strategies
from src.telegram.signal_monitor import TelegramSignalMonitor
from src.analysis.rug_intelligence import RugIntelligenceEngine

@dataclass
class SniperTrade:
    """Represents a sniper trade execution"""
    token_address: str
    symbol: str
    entry_price: float
    entry_time: datetime
    amount_sol: float = 0.1  # Default test trade size
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    strategy_used: str = ""
    confidence_score: float = 0.0
    status: str = "active"  # active, closed, stopped
    max_price_reached: float = 0.0
    drawdown: float = 0.0
    hold_time_minutes: int = 0
    rug_detected: bool = False
    
    @property
    def is_profitable(self) -> bool:
        return self.profit_loss_percent and self.profit_loss_percent > 0
    
    @property
    def roi_percentage(self) -> float:
        if self.profit_loss_percent:
            return self.profit_loss_percent
        return 0.0

@dataclass
class SniperSignal:
    """Represents a potential sniping opportunity"""
    token_data: ComprehensiveTokenData
    strategy_scores: Dict[str, float]
    combined_score: float
    recommendation: str  # BUY, HOLD, AVOID
    entry_price: float
    profit_target: float
    stop_loss: float
    confidence: float
    reasoning: List[str]
    telegram_signal: Optional[Dict] = None
    timestamp: datetime = field(default_factory=datetime.now)

class SolanaSniperBot:
    """
    Advanced Solana memecoin sniper bot with strategy integration
    """
    
    def __init__(self):
        self.strategies = Top10Strategies()
        self.rug_engine = RugIntelligenceEngine(None)  # Will need proper DB connection
        self.telegram_monitor = TelegramSignalMonitor()
        
        # Bot configuration
        self.test_trade_amount = 0.1  # SOL amount for test trades
        self.max_concurrent_trades = 5
        self.profit_target_multiplier = 1.5  # 50% profit target
        self.stop_loss_multiplier = 0.85    # 15% stop loss
        self.max_hold_time_hours = 4        # Maximum hold time
        
        # Initialize session state
        if 'sniper_trades' not in st.session_state:
            st.session_state.sniper_trades = []
        if 'sniper_signals' not in st.session_state:
            st.session_state.sniper_signals = []
        if 'sniper_config' not in st.session_state:
            st.session_state.sniper_config = {
                'auto_snipe': False,
                'min_confidence': 0.7,
                'strategies_enabled': ['momentum_breakout', 'volume_surge', 'social_sentiment']
            }
        if 'simulation_mode' not in st.session_state:
            st.session_state.simulation_mode = True
        if 'portfolio_balance' not in st.session_state:
            st.session_state.portfolio_balance = 10.0  # Starting with 10 SOL for testing
    
    def analyze_telegram_signal(self, signal_data: Dict) -> SniperSignal:
        """Analyze a Telegram signal and generate sniper recommendation"""
        
        # Extract token data from signal
        token_address = signal_data.get('contract_address', '')
        
        # Create comprehensive token data (in real implementation, this would fetch from APIs)
        token_data = ComprehensiveTokenData(
            contract_address=token_address,
            symbol=signal_data.get('symbol', 'UNKNOWN'),
            name=signal_data.get('name', 'Unknown Token'),
            price_usd=signal_data.get('price', 0.0),
            price_change_5m=np.random.normal(0, 10),  # Simulated
            price_change_1h=np.random.normal(0, 15),  # Simulated
            price_change_24h=np.random.normal(0, 25), # Simulated
            volume_24h=np.random.uniform(10000, 500000),
            market_cap=np.random.uniform(100000, 5000000),
            liquidity_usd=np.random.uniform(10000, 200000),
            holder_count=np.random.randint(50, 2000),
            top_10_holders_percent=np.random.uniform(15, 70),
            whale_count=np.random.randint(1, 10),
            rug_risk_score=np.random.uniform(0.1, 0.8),
            honeypot_risk=np.random.uniform(0.0, 0.5),
            mint_disabled=np.random.choice([True, False]),
            freeze_disabled=np.random.choice([True, False]),
            data_sources=['telegram', 'dexscreener']
        )
        
        # Run top 3 strategies on the token
        strategy_results = self.run_top_strategies([token_data])
        
        # Calculate combined score
        strategy_scores = {}
        for strategy_name, signals in strategy_results.items():
            if signals:
                strategy_scores[strategy_name] = signals[0]['score']
            else:
                strategy_scores[strategy_name] = 0.0
        
        # Combined scoring logic
        combined_score = self.calculate_combined_score(strategy_scores, signal_data)
        
        # Generate recommendation
        recommendation, reasoning = self.generate_recommendation(combined_score, strategy_scores, token_data)
        
        return SniperSignal(
            token_data=token_data,
            strategy_scores=strategy_scores,
            combined_score=combined_score,
            recommendation=recommendation,
            entry_price=token_data.price_usd,
            profit_target=token_data.price_usd * self.profit_target_multiplier,
            stop_loss=token_data.price_usd * self.stop_loss_multiplier,
            confidence=combined_score,
            reasoning=reasoning,
            telegram_signal=signal_data
        )
    
    def run_top_strategies(self, tokens: List[ComprehensiveTokenData]) -> Dict[str, List[Dict]]:
        """Run top 3 TrenchCoat strategies on tokens"""
        results = {}
        
        # Run specific strategies
        enabled_strategies = st.session_state.sniper_config['strategies_enabled']
        
        if 'momentum_breakout' in enabled_strategies:
            results['momentum_breakout'] = self.strategies.momentum_breakout_strategy(tokens)
        
        if 'volume_surge' in enabled_strategies:
            results['volume_surge'] = self.strategies.volume_surge_strategy(tokens)
        
        if 'social_sentiment' in enabled_strategies:
            results['social_sentiment'] = self.strategies.social_sentiment_strategy(tokens)
        
        return results
    
    def calculate_combined_score(self, strategy_scores: Dict[str, float], signal_data: Dict) -> float:
        """Calculate combined score from multiple strategies"""
        if not strategy_scores:
            return 0.0
        
        # Base score from strategies
        base_score = np.mean(list(strategy_scores.values()))
        
        # Telegram signal confidence boost
        telegram_confidence = signal_data.get('confidence', 0.5)
        telegram_boost = telegram_confidence * 0.2
        
        # Whale activity boost
        whale_activity = signal_data.get('whale_activity', 0)
        whale_boost = min(whale_activity * 0.1, 0.15)
        
        # Social buzz boost
        social_buzz = signal_data.get('social_mentions', 0)
        social_boost = min(social_buzz * 0.05, 0.1)
        
        combined = base_score + telegram_boost + whale_boost + social_boost
        return min(combined, 1.0)  # Cap at 1.0
    
    def generate_recommendation(self, combined_score: float, strategy_scores: Dict[str, float], 
                              token_data: ComprehensiveTokenData) -> Tuple[str, List[str]]:
        """Generate buy/hold/avoid recommendation with reasoning"""
        reasoning = []
        
        # Score-based recommendation
        if combined_score >= 0.8:
            recommendation = "BUY"
            reasoning.append(f"High combined score: {combined_score:.2f}")
        elif combined_score >= 0.6:
            recommendation = "HOLD"
            reasoning.append(f"Moderate score: {combined_score:.2f}")
        else:
            recommendation = "AVOID"
            reasoning.append(f"Low score: {combined_score:.2f}")
        
        # Strategy-specific reasoning
        for strategy, score in strategy_scores.items():
            if score > 0.7:
                reasoning.append(f"{strategy}: Strong signal ({score:.2f})")
            elif score > 0.5:
                reasoning.append(f"{strategy}: Moderate signal ({score:.2f})")
        
        # Risk factors
        if token_data.rug_risk_score > 0.7:
            reasoning.append(f"⚠️ High rug risk: {token_data.rug_risk_score:.2f}")
            if recommendation == "BUY":
                recommendation = "HOLD"
        
        if token_data.honeypot_risk > 0.5:
            reasoning.append(f"⚠️ Honeypot risk: {token_data.honeypot_risk:.2f}")
        
        if token_data.top_10_holders_percent > 80:
            reasoning.append(f"⚠️ High whale concentration: {token_data.top_10_holders_percent:.1f}%")
        
        # Positive factors
        if token_data.liquidity_usd > 100000:
            reasoning.append(f"✅ Good liquidity: ${token_data.liquidity_usd:,.0f}")
        
        if token_data.mint_disabled and token_data.freeze_disabled:
            reasoning.append("✅ Mint/freeze disabled - safer token")
        
        return recommendation, reasoning
    
    def execute_sniper_trade(self, signal: SniperSignal) -> SniperTrade:
        """Execute a sniper trade based on signal"""
        
        trade = SniperTrade(
            token_address=signal.token_data.contract_address,
            symbol=signal.token_data.symbol,
            entry_price=signal.entry_price,
            entry_time=datetime.now(),
            amount_sol=self.test_trade_amount,
            strategy_used=max(signal.strategy_scores, key=signal.strategy_scores.get),
            confidence_score=signal.confidence
        )
        
        # In simulation mode, track the trade
        if st.session_state.simulation_mode:
            st.session_state.sniper_trades.append(trade)
            st.session_state.portfolio_balance -= self.test_trade_amount
            
            st.success(f"🎯 Test trade executed: {trade.symbol} @ ${trade.entry_price:.6f}")
        
        return trade
    
    def simulate_trade_outcomes(self):
        """Simulate outcomes for active trades"""
        current_time = datetime.now()
        
        for trade in st.session_state.sniper_trades:
            if trade.status == "active":
                # Simulate price movement
                time_elapsed = (current_time - trade.entry_time).total_seconds() / 60  # minutes
                trade.hold_time_minutes = int(time_elapsed)
                
                # Random walk with bias based on confidence
                confidence_bias = (trade.confidence_score - 0.5) * 0.1
                price_change = np.random.normal(confidence_bias, 0.02)
                current_price = trade.entry_price * (1 + price_change)
                
                # Update max price
                trade.max_price_reached = max(trade.max_price_reached, current_price)
                
                # Calculate unrealized P&L
                trade.profit_loss = (current_price - trade.entry_price) * (trade.amount_sol / trade.entry_price)
                trade.profit_loss_percent = ((current_price - trade.entry_price) / trade.entry_price) * 100
                
                # Check exit conditions
                should_exit = False
                
                # Profit target hit
                if current_price >= trade.entry_price * self.profit_target_multiplier:
                    trade.exit_price = current_price
                    trade.exit_time = current_time
                    trade.status = "closed"
                    should_exit = True
                
                # Stop loss hit
                elif current_price <= trade.entry_price * self.stop_loss_multiplier:
                    trade.exit_price = current_price
                    trade.exit_time = current_time
                    trade.status = "stopped"
                    should_exit = True
                
                # Max hold time reached
                elif time_elapsed >= self.max_hold_time_hours * 60:
                    trade.exit_price = current_price
                    trade.exit_time = current_time
                    trade.status = "closed"
                    should_exit = True
                
                # Rug detection (random for simulation)
                elif np.random.random() < 0.01:  # 1% chance per update
                    trade.rug_detected = True
                    trade.exit_price = current_price * 0.1  # 90% loss on rug
                    trade.exit_time = current_time
                    trade.status = "rugged"
                    should_exit = True
                
                if should_exit:
                    # Return SOL to portfolio
                    exit_value = (trade.exit_price / trade.entry_price) * trade.amount_sol
                    st.session_state.portfolio_balance += exit_value
    
    def generate_sample_signals(self, count: int = 5) -> List[SniperSignal]:
        """Generate sample signals for demonstration"""
        signals = []
        
        for i in range(count):
            # Create random signal data
            signal_data = {
                'contract_address': f'sample_token_{i}_{int(time.time())}',
                'symbol': f'MEME{i+1}',
                'name': f'Sample Memecoin {i+1}',
                'price': np.random.uniform(0.00001, 0.01),
                'confidence': np.random.uniform(0.4, 0.9),
                'whale_activity': np.random.randint(0, 5),
                'social_mentions': np.random.randint(0, 20),
                'source': 'telegram_simulation'
            }
            
            # Analyze the signal
            signal = self.analyze_telegram_signal(signal_data)
            signals.append(signal)
        
        return signals
    
    def render_sniper_dashboard(self):
        """Render the main sniper bot dashboard"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 2px solid #ef4444;">
            <h1 style="color: #ef4444; margin: 0;">🎯 Solana Memecoin Sniper Bot</h1>
            <p style="color: #d1d5db; margin: 0.5rem 0 0 0;">
                Advanced AI-powered sniping with TrenchCoat strategy integration
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Bot status and configuration
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Portfolio Balance", f"{st.session_state.portfolio_balance:.2f} SOL")
        
        with col2:
            active_trades = sum(1 for trade in st.session_state.sniper_trades if trade.status == "active")
            st.metric("Active Trades", active_trades)
        
        with col3:
            total_trades = len(st.session_state.sniper_trades)
            profitable_trades = sum(1 for trade in st.session_state.sniper_trades if trade.is_profitable)
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
        
        with col4:
            total_pnl = sum(trade.profit_loss or 0 for trade in st.session_state.sniper_trades)
            st.metric("Total P&L", f"{total_pnl:+.3f} SOL")
        
        # Configuration panel
        st.subheader("⚙️ Bot Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.simulation_mode = st.checkbox("Simulation Mode", st.session_state.simulation_mode)
            auto_snipe = st.checkbox("Auto-Snipe Enabled", st.session_state.sniper_config['auto_snipe'])
            st.session_state.sniper_config['auto_snipe'] = auto_snipe
            
            min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 
                                     st.session_state.sniper_config['min_confidence'], 0.1)
            st.session_state.sniper_config['min_confidence'] = min_confidence
        
        with col2:
            st.markdown("**Enabled Strategies:**")
            strategies = ['momentum_breakout', 'volume_surge', 'social_sentiment', 'whale_following']
            enabled = []
            for strategy in strategies:
                if st.checkbox(strategy.replace('_', ' ').title(), 
                             value=strategy in st.session_state.sniper_config['strategies_enabled']):
                    enabled.append(strategy)
            st.session_state.sniper_config['strategies_enabled'] = enabled
        
        # Signal generation and analysis
        st.subheader("📡 Signal Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🎯 Generate Test Signals", type="primary"):
                new_signals = self.generate_sample_signals(5)
                st.session_state.sniper_signals.extend(new_signals)
                st.success(f"Generated {len(new_signals)} new signals!")
        
        with col2:
            if st.button("🔄 Update Trade Status"):
                self.simulate_trade_outcomes()
                st.success("Trade status updated!")
        
        # Display current signals
        if st.session_state.sniper_signals:
            self.render_signals_table()
        
        # Display active trades
        if st.session_state.sniper_trades:
            self.render_trades_dashboard()
    
    def render_signals_table(self):
        """Render table of current signals"""
        st.subheader("🎯 Current Signals")
        
        signals_data = []
        for i, signal in enumerate(st.session_state.sniper_signals[-10:]):  # Show last 10
            signals_data.append({
                'Symbol': signal.token_data.symbol,
                'Price': f"${signal.entry_price:.6f}",
                'Combined Score': f"{signal.combined_score:.2f}",
                'Recommendation': signal.recommendation,
                'Confidence': f"{signal.confidence:.1%}",
                'Profit Target': f"${signal.profit_target:.6f}",
                'Stop Loss': f"${signal.stop_loss:.6f}",
                'Action': i  # For button indexing
            })
        
        df = pd.DataFrame(signals_data)
        
        for idx, row in df.iterrows():
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
            
            with col1:
                st.write(row['Symbol'])
            with col2:
                st.write(row['Price'])
            with col3:
                score_color = "#10b981" if float(row['Combined Score']) > 0.7 else "#f59e0b" if float(row['Combined Score']) > 0.5 else "#ef4444"
                st.markdown(f"<span style='color: {score_color}'>{row['Combined Score']}</span>", unsafe_allow_html=True)
            with col4:
                rec_color = "#10b981" if row['Recommendation'] == "BUY" else "#f59e0b" if row['Recommendation'] == "HOLD" else "#ef4444"
                st.markdown(f"<span style='color: {rec_color}'>{row['Recommendation']}</span>", unsafe_allow_html=True)
            with col5:
                st.write(row['Confidence'])
            with col6:
                st.write(row['Profit Target'])
            with col7:
                st.write(row['Stop Loss'])
            with col8:
                if row['Recommendation'] == "BUY" and st.button(f"🎯 Snipe", key=f"snipe_{idx}"):
                    signal = st.session_state.sniper_signals[-(10-idx)]
                    trade = self.execute_sniper_trade(signal)
                    st.rerun()
    
    def render_trades_dashboard(self):
        """Render active and historical trades dashboard"""
        st.subheader("📊 Trading Dashboard")
        
        # Simulate trade updates
        self.simulate_trade_outcomes()
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📈 Active Trades", "📊 Performance", "📋 History"])
        
        with tab1:
            self.render_active_trades()
        
        with tab2:
            self.render_performance_analysis()
        
        with tab3:
            self.render_trade_history()
    
    def render_active_trades(self):
        """Render active trades table"""
        active_trades = [trade for trade in st.session_state.sniper_trades if trade.status == "active"]
        
        if not active_trades:
            st.info("No active trades currently")
            return
        
        for trade in active_trades:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                profit_color = "#10b981" if trade.profit_loss_percent and trade.profit_loss_percent > 0 else "#ef4444"
                st.markdown(f"""
                **{trade.symbol}** | {trade.strategy_used}<br>
                Entry: ${trade.entry_price:.6f} | Hold: {trade.hold_time_minutes}m<br>
                <span style="color: {profit_color}">P&L: {trade.profit_loss_percent:+.1f}%</span>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("Amount", f"{trade.amount_sol} SOL")
            
            with col3:
                st.metric("Confidence", f"{trade.confidence_score:.1%}")
            
            with col4:
                if st.button(f"🛑 Close", key=f"close_{trade.token_address}"):
                    trade.status = "manually_closed"
                    trade.exit_time = datetime.now()
                    # Simulate current price for exit
                    current_price = trade.entry_price * (1 + (trade.profit_loss_percent or 0) / 100)
                    trade.exit_price = current_price
                    exit_value = (trade.exit_price / trade.entry_price) * trade.amount_sol
                    st.session_state.portfolio_balance += exit_value
                    st.rerun()
    
    def render_performance_analysis(self):
        """Render performance analysis charts"""
        if not st.session_state.sniper_trades:
            st.info("No trades to analyze yet")
            return
        
        trades = st.session_state.sniper_trades
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_trades = len(trades)
        profitable_trades = sum(1 for trade in trades if trade.is_profitable)
        total_pnl = sum(trade.profit_loss or 0 for trade in trades)
        avg_hold_time = np.mean([trade.hold_time_minutes for trade in trades if trade.hold_time_minutes > 0])
        
        with col1:
            st.metric("Total Trades", total_trades)
        
        with col2:
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
        
        with col3:
            st.metric("Total P&L", f"{total_pnl:+.3f} SOL")
        
        with col4:
            st.metric("Avg Hold Time", f"{avg_hold_time:.0f}m")
        
        # P&L distribution chart
        if trades:
            pnl_data = [trade.profit_loss_percent or 0 for trade in trades if trade.profit_loss_percent is not None]
            
            if pnl_data:
                fig = go.Figure(data=[go.Histogram(x=pnl_data, nbinsx=20, name="P&L Distribution")])
                fig.update_layout(
                    title="Trade P&L Distribution",
                    xaxis_title="P&L (%)",
                    yaxis_title="Number of Trades",
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Strategy performance comparison
        strategy_performance = {}
        for trade in trades:
            if trade.strategy_used not in strategy_performance:
                strategy_performance[trade.strategy_used] = []
            strategy_performance[trade.strategy_used].append(trade.profit_loss_percent or 0)
        
        if strategy_performance:
            strategy_names = list(strategy_performance.keys())
            strategy_avg_returns = [np.mean(returns) for returns in strategy_performance.values()]
            
            fig = go.Figure(data=[go.Bar(x=strategy_names, y=strategy_avg_returns)])
            fig.update_layout(
                title="Strategy Performance Comparison",
                xaxis_title="Strategy",
                yaxis_title="Average Return (%)",
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_trade_history(self):
        """Render complete trade history"""
        if not st.session_state.sniper_trades:
            st.info("No trade history yet")
            return
        
        history_data = []
        for trade in st.session_state.sniper_trades:
            history_data.append({
                'Symbol': trade.symbol,
                'Entry Time': trade.entry_time.strftime("%Y-%m-%d %H:%M"),
                'Entry Price': f"${trade.entry_price:.6f}",
                'Exit Price': f"${trade.exit_price:.6f}" if trade.exit_price else "N/A",
                'P&L (%)': f"{trade.profit_loss_percent:+.1f}%" if trade.profit_loss_percent else "N/A",
                'P&L (SOL)': f"{trade.profit_loss:+.3f}" if trade.profit_loss else "N/A", 
                'Hold Time': f"{trade.hold_time_minutes}m",
                'Strategy': trade.strategy_used,
                'Status': trade.status,
                'Rug Detected': "Yes" if trade.rug_detected else "No"
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)

def render_sniper_bot_interface():
    """Main function to render the sniper bot interface"""
    bot = SolanaSniperBot()
    bot.render_sniper_dashboard()

if __name__ == "__main__":
    render_sniper_bot_interface()