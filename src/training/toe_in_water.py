#!/usr/bin/env python3
"""
TOE IN THE WATER - 24 HOUR TRAINING EXERCISE
Simulate betting on every new Telegram coin to test prediction accuracy
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
import random

from src.data.comprehensive_enricher import ComprehensiveTokenData
from src.strategies.top10_strategies import Top10Strategies
from src.sentiment.multi_platform_monitor import MultiPlatformSentimentMonitor

@dataclass
class TelegramCoinSignal:
    """New coin detected in Telegram"""
    coin_symbol: str
    contract_address: str
    entry_time: datetime
    entry_price: float
    signal_source: str
    signal_confidence: float
    initial_market_cap: float
    liquidity: float
    social_buzz: int
    whale_activity: int
    dev_holds: bool
    
@dataclass
class PredictionRecord:
    """Our prediction before investing"""
    coin_symbol: str
    prediction_type: str  # "UNICORN", "SMALL_EARNER", "AVOID"
    confidence_score: float
    predicted_max_gain: float  # Expected peak %
    predicted_timeframe: int   # Hours to peak
    risk_assessment: str       # "LOW", "MEDIUM", "HIGH"
    reasoning: List[str]
    strategy_scores: Dict[str, float]
    sentiment_score: float
    prediction_time: datetime = field(default_factory=datetime.now)

@dataclass
class TrainingTrade:
    """Simulated trade for training"""
    coin_symbol: str
    contract_address: str
    entry_time: datetime
    entry_price: float
    current_price: float
    peak_price: float
    prediction: PredictionRecord
    investment_amount: float = 0.1  # SOL
    current_gain_percent: float = 0.0
    peak_gain_percent: float = 0.0
    hours_elapsed: float = 0.0
    status: str = "ACTIVE"  # ACTIVE, PEAKED, RUGGED, CLOSED
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    final_gain_percent: Optional[float] = None
    was_prediction_correct: Optional[bool] = None
    
    @property
    def current_value_sol(self) -> float:
        return self.investment_amount * (1 + self.current_gain_percent / 100)
    
    @property
    def peak_value_sol(self) -> float:
        return self.investment_amount * (1 + self.peak_gain_percent / 100)

class ToeInWaterTrainer:
    """
    24-hour training exercise for prediction accuracy
    """
    
    def __init__(self):
        self.strategies = Top10Strategies()
        self.sentiment_monitor = MultiPlatformSentimentMonitor()
        
        # Training parameters
        self.training_duration_hours = 24
        self.investment_per_coin = 0.1  # SOL
        self.starting_balance = 10.0    # SOL
        
        # Initialize session state
        if 'training_active' not in st.session_state:
            st.session_state.training_active = False
        if 'training_start_time' not in st.session_state:
            st.session_state.training_start_time = None
        if 'training_trades' not in st.session_state:
            st.session_state.training_trades = []
        if 'training_balance' not in st.session_state:
            st.session_state.training_balance = self.starting_balance
        if 'telegram_signals' not in st.session_state:
            st.session_state.telegram_signals = []
        if 'training_stats' not in st.session_state:
            st.session_state.training_stats = {
                'total_predictions': 0,
                'correct_predictions': 0,
                'unicorn_predictions': 0,
                'unicorns_found': 0,
                'small_earner_predictions': 0,
                'small_earners_found': 0,
                'avoided_rugs': 0,
                'total_rugs': 0
            }
    
    def generate_telegram_signal(self) -> TelegramCoinSignal:
        """Simulate a new coin appearing in Telegram"""
        
        # Realistic memecoin symbols
        symbols = [
            'PEPE2', 'WOJAK', 'CHAD', 'DOGE2', 'SHIB2', 'FLOKI2', 'BONK2', 'WIF2',
            'MEME', 'BOBO', 'AIRY', 'PUMP', 'MOON', 'GEM', 'ROCKET', 'DIAMOND',
            'HODL', 'APE', 'FROG', 'CAT', 'DOG', 'BIRD', 'FISH', 'LION'
        ]
        
        symbol = random.choice(symbols) + str(random.randint(1, 999))
        
        # Generate realistic signal data
        signal = TelegramCoinSignal(
            coin_symbol=symbol,
            contract_address=f"contract_{random.randint(100000, 999999)}",
            entry_time=datetime.now(),
            entry_price=random.uniform(0.00001, 0.001),
            signal_source=random.choice(['ATM.Day', 'CryptoGems', 'MoonShots', 'SolanaAlpha']),
            signal_confidence=random.uniform(0.3, 0.9),
            initial_market_cap=random.uniform(50000, 2000000),
            liquidity=random.uniform(10000, 500000),
            social_buzz=random.randint(1, 100),
            whale_activity=random.randint(0, 10),
            dev_holds=random.choice([True, False])
        )
        
        return signal
    
    def analyze_and_predict(self, signal: TelegramCoinSignal) -> PredictionRecord:
        """Analyze new signal and make prediction"""
        
        # Create token data for analysis
        token_data = ComprehensiveTokenData(
            contract_address=signal.contract_address,
            symbol=signal.coin_symbol,
            name=f"{signal.coin_symbol} Token",
            price_usd=signal.entry_price,
            price_change_5m=random.normal(0, 10),
            price_change_1h=random.normal(0, 15),
            price_change_24h=random.normal(0, 25),
            volume_24h=random.uniform(10000, 500000),
            market_cap=signal.initial_market_cap,
            liquidity_usd=signal.liquidity,
            holder_count=random.randint(100, 5000),
            top_10_holders_percent=random.uniform(15, 80),
            whale_count=signal.whale_activity,
            rug_risk_score=random.uniform(0.1, 0.9),
            honeypot_risk=random.uniform(0.0, 0.7),
            mint_disabled=random.choice([True, False]),
            freeze_disabled=random.choice([True, False]),
            data_sources=['telegram', 'dexscreener']
        )
        
        # Run strategy analysis
        strategy_results = self.run_strategy_analysis([token_data])
        
        # Calculate strategy scores
        strategy_scores = {}
        for strategy_name, signals in strategy_results.items():
            if signals:
                strategy_scores[strategy_name] = signals[0]['score']
            else:
                strategy_scores[strategy_name] = 0.0
        
        # Combined analysis score
        base_score = np.mean(list(strategy_scores.values()))
        
        # Adjust for signal factors
        signal_boost = signal.signal_confidence * 0.2
        liquidity_boost = min(signal.liquidity / 100000, 0.1)
        whale_boost = min(signal.whale_activity * 0.05, 0.15)
        
        combined_score = base_score + signal_boost + liquidity_boost + whale_boost
        
        # Get sentiment score (simulated)
        sentiment_score = random.uniform(-0.5, 0.8)
        
        # Make prediction
        prediction_type, predicted_gain, timeframe, risk, reasoning = self.make_prediction(
            combined_score, strategy_scores, token_data, signal, sentiment_score
        )
        
        return PredictionRecord(
            coin_symbol=signal.coin_symbol,
            prediction_type=prediction_type,
            confidence_score=combined_score,
            predicted_max_gain=predicted_gain,
            predicted_timeframe=timeframe,
            risk_assessment=risk,
            reasoning=reasoning,
            strategy_scores=strategy_scores,
            sentiment_score=sentiment_score
        )
    
    def make_prediction(self, combined_score: float, strategy_scores: Dict[str, float], 
                       token_data: ComprehensiveTokenData, signal: TelegramCoinSignal,
                       sentiment_score: float) -> Tuple[str, float, int, str, List[str]]:
        """Make prediction: UNICORN, SMALL_EARNER, or AVOID"""
        
        reasoning = []
        
        # Base prediction logic
        if combined_score >= 0.8:
            prediction_type = "UNICORN"
            predicted_gain = random.uniform(500, 2000)  # 500-2000%
            timeframe = random.randint(2, 12)  # 2-12 hours
            risk = "HIGH"
            reasoning.append(f"🦄 HIGH SCORE: {combined_score:.2f} indicates massive potential")
        elif combined_score >= 0.6:
            prediction_type = "SMALL_EARNER"
            predicted_gain = random.uniform(50, 300)   # 50-300%
            timeframe = random.randint(1, 8)   # 1-8 hours
            risk = "MEDIUM"
            reasoning.append(f"💰 MODERATE SCORE: {combined_score:.2f} suggests decent gains")
        else:
            prediction_type = "AVOID"
            predicted_gain = random.uniform(-50, 20)   # Likely loss or small gain
            timeframe = random.randint(1, 4)   # Quick dump
            risk = "HIGH"
            reasoning.append(f"⚠️ LOW SCORE: {combined_score:.2f} suggests high risk")
        
        # Add specific reasoning
        if sentiment_score > 0.5:
            reasoning.append(f"✅ BULLISH SENTIMENT: {sentiment_score:.2f}")
        elif sentiment_score < -0.2:
            reasoning.append(f"❌ BEARISH SENTIMENT: {sentiment_score:.2f}")
        
        if signal.whale_activity > 5:
            reasoning.append(f"🐋 HIGH WHALE ACTIVITY: {signal.whale_activity} whales")
        
        if signal.liquidity > 200000:
            reasoning.append(f"💧 GOOD LIQUIDITY: ${signal.liquidity:,.0f}")
        
        if token_data.rug_risk_score > 0.7:
            reasoning.append(f"🚨 HIGH RUG RISK: {token_data.rug_risk_score:.2f}")
            if prediction_type == "UNICORN":
                prediction_type = "SMALL_EARNER"  # Downgrade due to rug risk
        
        return prediction_type, predicted_gain, timeframe, risk, reasoning
    
    def run_strategy_analysis(self, tokens: List[ComprehensiveTokenData]) -> Dict[str, List[Dict]]:
        """Run top strategies on tokens"""
        results = {}
        
        # Simulate strategy results
        strategies = ['momentum_breakout', 'volume_surge', 'social_sentiment', 'whale_following']
        
        for strategy in strategies:
            signals = []
            for token in tokens:
                score = random.uniform(0.2, 0.9)
                if score > 0.5:  # Only add if decent score
                    signals.append({
                        'token': token,
                        'score': score,
                        'action': 'BUY',
                        'strategy': strategy
                    })
            results[strategy] = signals
        
        return results
    
    def simulate_price_movement(self, trade: TrainingTrade) -> TrainingTrade:
        """Simulate realistic price movement over time"""
        hours_elapsed = (datetime.now() - trade.entry_time).total_seconds() / 3600
        trade.hours_elapsed = hours_elapsed
        
        # Base price movement based on prediction
        if trade.prediction.prediction_type == "UNICORN":
            # Unicorns: explosive growth then potential crash
            if hours_elapsed < trade.prediction.predicted_timeframe:
                # Growth phase
                progress = hours_elapsed / trade.prediction.predicted_timeframe
                target_gain = trade.prediction.predicted_max_gain
                current_gain = target_gain * progress * random.uniform(0.8, 1.2)
            else:
                # Post-peak phase - might hold or crash
                if random.random() < 0.3:  # 30% chance of rug pull
                    current_gain = trade.peak_gain_percent * random.uniform(0.1, 0.3)
                    trade.status = "RUGGED"
                else:
                    current_gain = trade.peak_gain_percent * random.uniform(0.6, 1.0)
        
        elif trade.prediction.prediction_type == "SMALL_EARNER":
            # Small earners: steady growth to modest peak
            if hours_elapsed < trade.prediction.predicted_timeframe:
                progress = hours_elapsed / trade.prediction.predicted_timeframe
                target_gain = trade.prediction.predicted_max_gain
                current_gain = target_gain * progress * random.uniform(0.9, 1.1)
            else:
                current_gain = trade.prediction.predicted_max_gain * random.uniform(0.8, 1.0)
        
        else:  # AVOID
            # Should dump or stay flat
            current_gain = random.uniform(-30, 10) * (hours_elapsed / 24)
        
        # Add random volatility
        volatility = random.uniform(-5, 5)
        current_gain += volatility
        
        # Update trade
        trade.current_gain_percent = current_gain
        trade.peak_gain_percent = max(trade.peak_gain_percent, current_gain)
        trade.current_price = trade.entry_price * (1 + current_gain / 100)
        trade.peak_price = max(trade.peak_price, trade.current_price)
        
        return trade
    
    def evaluate_prediction_accuracy(self, trade: TrainingTrade) -> bool:
        """Check if our prediction was correct"""
        actual_peak = trade.peak_gain_percent
        predicted_type = trade.prediction.prediction_type
        
        if predicted_type == "UNICORN":
            # Correct if achieved 500%+ gain
            return actual_peak >= 500
        elif predicted_type == "SMALL_EARNER":
            # Correct if achieved 50-500% gain
            return 50 <= actual_peak < 500
        else:  # AVOID
            # Correct if stayed below 50% or went negative
            return actual_peak < 50
    
    def start_training_exercise(self):
        """Start the 24-hour training exercise"""
        st.session_state.training_active = True
        st.session_state.training_start_time = datetime.now()
        st.session_state.training_trades = []
        st.session_state.training_balance = self.starting_balance
        st.session_state.telegram_signals = []
        st.session_state.training_stats = {
            'total_predictions': 0,
            'correct_predictions': 0,
            'unicorn_predictions': 0,
            'unicorns_found': 0,
            'small_earner_predictions': 0,
            'small_earners_found': 0,
            'avoided_rugs': 0,
            'total_rugs': 0
        }
        
        st.success("🌊 Toe in the Water training exercise started!")
        st.info("📡 Now monitoring for new Telegram signals...")
    
    def process_new_telegram_signal(self):
        """Process a new signal from Telegram"""
        # Generate new signal
        signal = self.generate_telegram_signal()
        st.session_state.telegram_signals.append(signal)
        
        # Make prediction
        prediction = self.analyze_and_predict(signal)
        
        # Create training trade
        trade = TrainingTrade(
            coin_symbol=signal.coin_symbol,
            contract_address=signal.contract_address,
            entry_time=signal.entry_time,
            entry_price=signal.entry_price,
            current_price=signal.entry_price,
            peak_price=signal.entry_price,
            prediction=prediction
        )
        
        st.session_state.training_trades.append(trade)
        st.session_state.training_balance -= self.investment_per_coin
        st.session_state.training_stats['total_predictions'] += 1
        
        if prediction.prediction_type == "UNICORN":
            st.session_state.training_stats['unicorn_predictions'] += 1
        elif prediction.prediction_type == "SMALL_EARNER":
            st.session_state.training_stats['small_earner_predictions'] += 1
        
        return signal, prediction, trade
    
    def update_all_trades(self):
        """Update all active trades with new price movements"""
        for i, trade in enumerate(st.session_state.training_trades):
            if trade.status == "ACTIVE":
                updated_trade = self.simulate_price_movement(trade)
                st.session_state.training_trades[i] = updated_trade
                
                # Check if prediction accuracy can be evaluated
                if updated_trade.hours_elapsed >= 6:  # Evaluate after 6 hours minimum
                    is_correct = self.evaluate_prediction_accuracy(updated_trade)
                    updated_trade.was_prediction_correct = is_correct
                    
                    if is_correct:
                        st.session_state.training_stats['correct_predictions'] += 1
    
    def render_training_dashboard(self):
        """Render the main training dashboard"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 2px solid #06d6a0;">
            <h1 style="color: #06d6a0; margin: 0;">🌊 Toe in the Water - Training Exercise</h1>
            <p style="color: #d1d5db; margin: 0.5rem 0 0 0;">
                24-hour simulation: Bet on every Telegram coin, test prediction accuracy
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Training controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if not st.session_state.training_active:
                if st.button("🚀 Start Training Exercise", type="primary"):
                    self.start_training_exercise()
                    st.rerun()
            else:
                time_elapsed = datetime.now() - st.session_state.training_start_time
                hours_remaining = 24 - (time_elapsed.total_seconds() / 3600)
                
                if hours_remaining > 0:
                    st.success(f"📡 Training Active | ⏱️ {hours_remaining:.1f} hours remaining")
                else:
                    st.info("🏁 Training Complete! Review results below.")
        
        with col2:
            if st.session_state.training_active:
                if st.button("📡 New Telegram Signal"):
                    signal, prediction, trade = self.process_new_telegram_signal()
                    st.success(f"📱 New signal: ${signal.coin_symbol}")
                    st.info(f"🔮 Prediction: {prediction.prediction_type}")
                    st.rerun()
        
        with col3:
            if st.session_state.training_active:
                if st.button("🔄 Update Prices"):
                    self.update_all_trades()
                    st.success("📈 Prices updated!")
                    st.rerun()
        
        # Display training results if active
        if st.session_state.training_active or st.session_state.training_trades:
            self.render_training_results()
    
    def render_training_results(self):
        """Render comprehensive training results"""
        
        # Performance overview
        st.subheader("📊 Training Performance Overview")
        
        stats = st.session_state.training_stats
        total_trades = len(st.session_state.training_trades)
        current_balance = st.session_state.training_balance
        
        # Calculate portfolio value
        portfolio_value = current_balance
        for trade in st.session_state.training_trades:
            portfolio_value += trade.current_value_sol
        
        total_return = ((portfolio_value - self.starting_balance) / self.starting_balance) * 100
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Portfolio Value", f"{portfolio_value:.2f} SOL", 
                     delta=f"{total_return:+.1f}%")
        
        with col2:
            st.metric("Total Trades", total_trades)
        
        with col3:
            accuracy = (stats['correct_predictions'] / max(stats['total_predictions'], 1)) * 100
            st.metric("Prediction Accuracy", f"{accuracy:.1f}%")
        
        with col4:
            active_trades = sum(1 for trade in st.session_state.training_trades if trade.status == "ACTIVE")
            st.metric("Active Trades", active_trades)
        
        with col5:
            avg_gain = np.mean([trade.current_gain_percent for trade in st.session_state.training_trades])
            st.metric("Avg Gain", f"{avg_gain:+.1f}%")
        
        # Recent signals and predictions
        if st.session_state.training_trades:
            st.subheader("📱 Recent Telegram Signals & Predictions")
            
            for trade in st.session_state.training_trades[-5:]:  # Show last 5
                prediction = trade.prediction
                
                # Color coding
                pred_color = {
                    "UNICORN": "#8b5cf6",
                    "SMALL_EARNER": "#10b981", 
                    "AVOID": "#ef4444"
                }.get(prediction.prediction_type, "#9ca3af")
                
                status_emoji = {
                    "ACTIVE": "🔄",
                    "PEAKED": "📈",
                    "RUGGED": "💥",
                    "CLOSED": "✅"
                }.get(trade.status, "🔄")
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                           padding: 1.5rem; border-radius: 12px; margin: 1rem 0; 
                           border-left: 4px solid {pred_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: {pred_color};">
                                ${trade.coin_symbol} | {prediction.prediction_type}
                            </h4>
                            <p style="margin: 0.5rem 0 0 0; color: #d1d5db;">
                                💰 Current: {trade.current_gain_percent:+.1f}% | 
                                📈 Peak: {trade.peak_gain_percent:+.1f}% | 
                                ⏱️ {trade.hours_elapsed:.1f}h
                            </p>
                            <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.9rem;">
                                🎯 Predicted: {prediction.predicted_max_gain:.0f}% in {prediction.predicted_timeframe}h
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 2rem;">{status_emoji}</div>
                            <div style="color: #9ca3af; font-size: 0.8rem;">{trade.status}</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 1rem;">
                        <strong>Reasoning:</strong><br>
                        {'<br>'.join(prediction.reasoning)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed performance analysis
        if len(st.session_state.training_trades) > 0:
            st.subheader("📈 Detailed Performance Analysis")
            
            # Create performance DataFrame
            trade_data = []
            for trade in st.session_state.training_trades:
                trade_data.append({
                    'Symbol': trade.coin_symbol,
                    'Prediction': trade.prediction.prediction_type,
                    'Confidence': f"{trade.prediction.confidence_score:.2f}",
                    'Current Gain': f"{trade.current_gain_percent:+.1f}%",
                    'Peak Gain': f"{trade.peak_gain_percent:+.1f}%",
                    'Hours Elapsed': f"{trade.hours_elapsed:.1f}",
                    'Status': trade.status,
                    'Correct?': "✅" if trade.was_prediction_correct else "❌" if trade.was_prediction_correct is False else "⏳"
                })
            
            df = pd.DataFrame(trade_data)
            st.dataframe(df, use_container_width=True)
            
            # Performance visualization
            self.render_performance_charts()
    
    def render_performance_charts(self):
        """Render performance visualization charts"""
        
        trades = st.session_state.training_trades
        if not trades:
            return
        
        # Portfolio value over time
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Portfolio Value Over Time', 'Prediction Accuracy by Type',
                          'Gain Distribution', 'Best vs Worst Performers'),
            specs=[[{"secondary_y": False}, {"type": "bar"}],
                   [{"type": "histogram"}, {"type": "bar"}]]
        )
        
        # Portfolio timeline
        timeline_hours = []
        portfolio_values = []
        current_value = self.starting_balance
        
        for i in range(0, 25):  # 24 hours + current
            hour_value = st.session_state.training_balance
            for trade in trades:
                if trade.hours_elapsed >= i:
                    # Simulate historical value
                    historical_gain = (trade.current_gain_percent * i / max(trade.hours_elapsed, 1))
                    hour_value += trade.investment_amount * (1 + historical_gain / 100)
                else:
                    hour_value += trade.investment_amount
            
            timeline_hours.append(i)
            portfolio_values.append(hour_value)
        
        fig.add_trace(
            go.Scatter(x=timeline_hours, y=portfolio_values, 
                      mode='lines+markers', name='Portfolio Value',
                      line=dict(color='#06d6a0', width=3)),
            row=1, col=1
        )
        
        # Prediction accuracy by type
        pred_types = ['UNICORN', 'SMALL_EARNER', 'AVOID']
        accuracies = []
        
        for pred_type in pred_types:
            type_trades = [t for t in trades if t.prediction.prediction_type == pred_type]
            if type_trades:
                correct = sum(1 for t in type_trades if t.was_prediction_correct)
                total = len([t for t in type_trades if t.was_prediction_correct is not None])
                accuracy = (correct / max(total, 1)) * 100
            else:
                accuracy = 0
            accuracies.append(accuracy)
        
        colors = ['#8b5cf6', '#10b981', '#ef4444']
        fig.add_trace(
            go.Bar(x=pred_types, y=accuracies, name='Accuracy %',
                  marker_color=colors),
            row=1, col=2
        )
        
        # Gain distribution
        gains = [t.current_gain_percent for t in trades]
        fig.add_trace(
            go.Histogram(x=gains, nbinsx=20, name='Gain Distribution',
                        marker_color='#06d6a0', opacity=0.7),
            row=2, col=1
        )
        
        # Best vs worst performers
        sorted_trades = sorted(trades, key=lambda x: x.current_gain_percent, reverse=True)
        top_5 = sorted_trades[:5]
        bottom_5 = sorted_trades[-5:]
        
        symbols = [t.coin_symbol for t in top_5] + [t.coin_symbol for t in bottom_5]
        gains = [t.current_gain_percent for t in top_5] + [t.current_gain_percent for t in bottom_5]
        colors_bars = ['#10b981'] * 5 + ['#ef4444'] * 5
        
        fig.add_trace(
            go.Bar(x=symbols, y=gains, name='Performance',
                  marker_color=colors_bars),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            showlegend=False,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            title_text="Toe in the Water - Training Performance"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_toe_in_water_interface():
    """Main function to render the Toe in the Water interface"""
    trainer = ToeInWaterTrainer()
    trainer.render_training_dashboard()

if __name__ == "__main__":
    render_toe_in_water_interface()