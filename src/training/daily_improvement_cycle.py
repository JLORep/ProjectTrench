#!/usr/bin/env python3
"""
DAILY IMPROVEMENT CYCLE
Automated 24-hour training with top 10 performer validation and strategy adjustment
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
import pickle
import os

from src.training.toe_in_water import ToeInWaterTrainer, TrainingTrade, PredictionRecord
from src.telegram.signal_monitor import TelegramSignalMonitor

@dataclass
class Top10PerformerData:
    """Actual top 10 performer from Telegram"""
    symbol: str
    contract_address: str
    entry_price: float
    peak_price: float
    gain_percent: float
    time_to_peak_hours: float
    final_price: float
    final_gain_percent: float
    market_cap_at_entry: float
    volume_at_entry: float
    telegram_source: str
    date_detected: datetime
    
    @property
    def was_unicorn(self) -> bool:
        return self.gain_percent >= 1000  # 1000%+ = unicorn
    
    @property
    def performance_category(self) -> str:
        if self.gain_percent >= 1000:
            return "UNICORN"
        elif self.gain_percent >= 100:
            return "BIG_WINNER" 
        elif self.gain_percent >= 20:
            return "SMALL_WINNER"
        else:
            return "LOSER"

@dataclass 
class StrategyAdjustment:
    """Strategy parameter adjustment based on learning"""
    strategy_name: str
    parameter_name: str
    old_value: float
    new_value: float
    improvement_reason: str
    confidence_boost: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DailyTrainingResults:
    """Complete results from a 24-hour training cycle"""
    date: datetime
    total_predictions: int
    correct_predictions: int
    accuracy_percent: float
    unicorn_predictions: int
    unicorns_found_actual: int
    unicorn_accuracy: float
    portfolio_return_percent: float
    top_performers_analyzed: List[Top10PerformerData]
    strategy_adjustments: List[StrategyAdjustment]
    key_learnings: List[str]
    overall_grade: str  # A+, A, B+, B, C+, C, D, F

class DailyImprovementEngine:
    """
    Automated daily training and strategy improvement system
    """
    
    def __init__(self):
        self.trainer = ToeInWaterTrainer()
        self.telegram_monitor = TelegramSignalMonitor()
        
        # Learning parameters
        self.learning_rate = 0.1
        self.strategy_weights = {
            'momentum_breakout': 0.25,
            'volume_surge': 0.25, 
            'social_sentiment': 0.20,
            'whale_following': 0.15,
            'rug_detection': 0.15
        }
        
        # Performance tracking
        self.daily_results_history = []
        self.strategy_performance_history = {}
        
        # Initialize session state
        if 'daily_training_active' not in st.session_state:
            st.session_state.daily_training_active = False
        if 'current_cycle_day' not in st.session_state:
            st.session_state.current_cycle_day = 1
        if 'improvement_history' not in st.session_state:
            st.session_state.improvement_history = []
        if 'strategy_evolution' not in st.session_state:
            st.session_state.strategy_evolution = self.strategy_weights.copy()
        if 'learning_insights' not in st.session_state:
            st.session_state.learning_insights = []
    
    def fetch_top10_performers_actual(self, date: datetime) -> List[Top10PerformerData]:
        """Fetch actual top 10 performers from Telegram for validation"""
        
        # In real implementation, this would parse actual Telegram messages
        # For demo, we'll simulate realistic top 10 performer data
        
        performers = []
        for i in range(10):
            # Generate realistic top performer data
            gain = np.random.choice(
                [np.random.uniform(2000, 5000),  # 20% chance unicorn
                 np.random.uniform(100, 1000),   # 30% chance big winner  
                 np.random.uniform(20, 100),     # 40% chance small winner
                 np.random.uniform(-50, 20)],    # 10% chance loser
                p=[0.2, 0.3, 0.4, 0.1]
            )
            
            performer = Top10PerformerData(
                symbol=f"TOP{i+1}",
                contract_address=f"actual_contract_{i}_{int(time.time())}",
                entry_price=np.random.uniform(0.00001, 0.001),
                peak_price=0,  # Will calculate
                gain_percent=gain,
                time_to_peak_hours=np.random.uniform(0.5, 12),
                final_price=0,  # Will calculate
                final_gain_percent=gain * np.random.uniform(0.3, 0.8),  # Usually doesn't hold peak
                market_cap_at_entry=np.random.uniform(50000, 2000000),
                volume_at_entry=np.random.uniform(10000, 500000),
                telegram_source="ATM.Day Top 10",
                date_detected=date
            )
            
            # Calculate prices
            performer.peak_price = performer.entry_price * (1 + gain / 100)
            performer.final_price = performer.entry_price * (1 + performer.final_gain_percent / 100)
            
            performers.append(performer)
        
        return performers
    
    def analyze_prediction_vs_reality(self, predictions: List[TrainingTrade], 
                                    actual_performers: List[Top10PerformerData]) -> Dict[str, Any]:
        """Compare our predictions against actual top 10 performers"""
        
        analysis = {
            'total_comparisons': 0,
            'correct_unicorn_predictions': 0,
            'missed_unicorns': 0,
            'false_unicorn_predictions': 0,
            'strategy_accuracy': {},
            'learning_insights': []
        }
        
        # Find overlapping tokens (predictions that were also in top 10)
        predicted_symbols = {trade.coin_symbol for trade in predictions}
        actual_symbols = {perf.symbol for perf in actual_performers}
        overlapping_symbols = predicted_symbols.intersection(actual_symbols)
        
        analysis['total_comparisons'] = len(overlapping_symbols)
        
        for symbol in overlapping_symbols:
            # Find prediction and actual performance
            prediction = next(trade for trade in predictions if trade.coin_symbol == symbol)
            actual = next(perf for perf in actual_performers if perf.symbol == symbol)
            
            # Check unicorn prediction accuracy
            predicted_unicorn = prediction.prediction.prediction_type == "UNICORN"
            was_actual_unicorn = actual.was_unicorn
            
            if predicted_unicorn and was_actual_unicorn:
                analysis['correct_unicorn_predictions'] += 1
            elif not predicted_unicorn and was_actual_unicorn:
                analysis['missed_unicorns'] += 1
                analysis['learning_insights'].append(
                    f"MISSED UNICORN: {symbol} gained {actual.gain_percent:.0f}% but we predicted {prediction.prediction.prediction_type}"
                )
            elif predicted_unicorn and not was_actual_unicorn:
                analysis['false_unicorn_predictions'] += 1
                analysis['learning_insights'].append(
                    f"FALSE UNICORN: {symbol} only gained {actual.gain_percent:.0f}% but we predicted UNICORN"
                )
        
        # Analyze missed unicorns (actual unicorns we didn't even predict on)
        actual_unicorns = [p for p in actual_performers if p.was_unicorn]
        for unicorn in actual_unicorns:
            if unicorn.symbol not in predicted_symbols:
                analysis['missed_unicorns'] += 1
                analysis['learning_insights'].append(
                    f"COMPLETELY MISSED: {unicorn.symbol} gained {unicorn.gain_percent:.0f}% - not even detected"
                )
        
        return analysis
    
    def generate_strategy_adjustments(self, analysis: Dict[str, Any], 
                                    actual_performers: List[Top10PerformerData]) -> List[StrategyAdjustment]:
        """Generate strategy adjustments based on performance analysis"""
        
        adjustments = []
        
        # Analyze what made the actual unicorns special
        unicorns = [p for p in actual_performers if p.was_unicorn]
        
        if unicorns:
            # Analyze common patterns in unicorns
            avg_time_to_peak = np.mean([u.time_to_peak_hours for u in unicorns])
            avg_entry_mcap = np.mean([u.market_cap_at_entry for u in unicorns])
            avg_entry_volume = np.mean([u.volume_at_entry for u in unicorns])
            
            # Adjust momentum strategy if unicorns peaked quickly
            if avg_time_to_peak < 4:  # Fast movers
                adjustments.append(StrategyAdjustment(
                    strategy_name="momentum_breakout",
                    parameter_name="time_sensitivity_weight", 
                    old_value=self.strategy_weights['momentum_breakout'],
                    new_value=self.strategy_weights['momentum_breakout'] * 1.1,
                    improvement_reason=f"Unicorns peaked in avg {avg_time_to_peak:.1f}h - prioritize fast momentum",
                    confidence_boost=0.05
                ))
            
            # Adjust volume strategy if unicorns had high volume
            if avg_entry_volume > 200000:
                adjustments.append(StrategyAdjustment(
                    strategy_name="volume_surge",
                    parameter_name="volume_threshold",
                    old_value=self.strategy_weights['volume_surge'],
                    new_value=self.strategy_weights['volume_surge'] * 1.15,
                    improvement_reason=f"Unicorns had avg volume ${avg_entry_volume:,.0f} - increase volume weight",
                    confidence_boost=0.08
                ))
            
            # Adjust market cap preferences
            if avg_entry_mcap < 500000:  # Low cap unicorns
                adjustments.append(StrategyAdjustment(
                    strategy_name="market_cap_filter",
                    parameter_name="low_cap_bonus",
                    old_value=0.0,
                    new_value=0.1,
                    improvement_reason=f"Unicorns had avg mcap ${avg_entry_mcap:,.0f} - boost low cap scoring",
                    confidence_boost=0.06
                ))
        
        # Analyze missed opportunities
        if analysis['missed_unicorns'] > analysis['correct_unicorn_predictions']:
            adjustments.append(StrategyAdjustment(
                strategy_name="sensitivity_adjustment",
                parameter_name="unicorn_threshold",
                old_value=0.8,
                new_value=0.75,  # Lower threshold to catch more
                improvement_reason=f"Missed {analysis['missed_unicorns']} unicorns - lower detection threshold",
                confidence_boost=0.04
            ))
        
        # Reduce false positive rate if too many wrong unicorn predictions
        if analysis['false_unicorn_predictions'] > analysis['correct_unicorn_predictions']:
            adjustments.append(StrategyAdjustment(
                strategy_name="precision_adjustment", 
                parameter_name="unicorn_threshold",
                old_value=0.8,
                new_value=0.85,  # Higher threshold for more precision
                improvement_reason=f"{analysis['false_unicorn_predictions']} false unicorns - increase precision",
                confidence_boost=0.03
            ))
        
        return adjustments
    
    def apply_strategy_adjustments(self, adjustments: List[StrategyAdjustment]):
        """Apply the strategy adjustments to improve future performance"""
        
        for adjustment in adjustments:
            if adjustment.strategy_name in self.strategy_weights:
                # Apply the adjustment
                old_weight = self.strategy_weights[adjustment.strategy_name]
                new_weight = min(adjustment.new_value, 1.0)  # Cap at 1.0
                self.strategy_weights[adjustment.strategy_name] = new_weight
                
                # Log the change
                improvement_log = {
                    'timestamp': datetime.now(),
                    'adjustment': adjustment,
                    'performance_impact': adjustment.confidence_boost
                }
                st.session_state.improvement_history.append(improvement_log)
        
        # Update session state
        st.session_state.strategy_evolution = self.strategy_weights.copy()
    
    def calculate_daily_grade(self, results: DailyTrainingResults) -> str:
        """Calculate overall performance grade for the day"""
        
        score = 0
        
        # Accuracy component (40% of grade)
        accuracy_score = results.accuracy_percent / 100 * 40
        score += accuracy_score
        
        # Unicorn detection component (30% of grade)  
        if results.unicorn_predictions > 0:
            unicorn_score = results.unicorn_accuracy / 100 * 30
        else:
            unicorn_score = 0
        score += unicorn_score
        
        # Portfolio return component (30% of grade)
        return_score = min(results.portfolio_return_percent / 100 * 30, 30)  # Cap at 30
        score += return_score
        
        # Convert to letter grade
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 65:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def run_24hour_training_cycle(self) -> DailyTrainingResults:
        """Run complete 24-hour training cycle with validation and adjustment"""
        
        # Start training exercise
        if not st.session_state.training_active:
            self.trainer.start_training_exercise()
        
        # Simulate 24 hours of trading (accelerated for demo)
        training_trades = []
        
        # Generate signals throughout the day
        for hour in range(24):
            # Generate 1-3 signals per hour  
            signals_this_hour = np.random.randint(1, 4)
            
            for _ in range(signals_this_hour):
                signal, prediction, trade = self.trainer.process_new_telegram_signal()
                training_trades.append(trade)
                
                # Simulate time passing
                time.sleep(0.1)  # Small delay for demo
        
        # Update all trades with final prices
        for trade in training_trades:
            self.trainer.simulate_price_movement(trade)
        
        # Fetch actual top 10 performers for validation
        actual_performers = self.fetch_top10_performers_actual(datetime.now())
        
        # Analyze predictions vs reality
        analysis = self.analyze_prediction_vs_reality(training_trades, actual_performers)
        
        # Generate strategy adjustments
        adjustments = self.generate_strategy_adjustments(analysis, actual_performers)
        
        # Apply adjustments
        self.apply_strategy_adjustments(adjustments)
        
        # Calculate results
        total_predictions = len(training_trades)
        correct_predictions = sum(1 for trade in training_trades if trade.was_prediction_correct)
        accuracy = (correct_predictions / max(total_predictions, 1)) * 100
        
        unicorn_predictions = sum(1 for trade in training_trades if trade.prediction.prediction_type == "UNICORN")
        unicorns_found = len([p for p in actual_performers if p.was_unicorn])
        unicorn_accuracy = (analysis['correct_unicorn_predictions'] / max(unicorn_predictions, 1)) * 100
        
        # Portfolio return
        portfolio_value = st.session_state.training_balance
        for trade in training_trades:
            portfolio_value += trade.current_value_sol
        portfolio_return = ((portfolio_value - self.trainer.starting_balance) / self.trainer.starting_balance) * 100
        
        # Key learnings
        key_learnings = analysis['learning_insights'] + [
            f"Applied {len(adjustments)} strategy adjustments",
            f"Found {unicorns_found} actual unicorns vs {unicorn_predictions} predicted",
            f"Portfolio return: {portfolio_return:+.1f}%"
        ]
        
        results = DailyTrainingResults(
            date=datetime.now(),
            total_predictions=total_predictions,
            correct_predictions=correct_predictions,
            accuracy_percent=accuracy,
            unicorn_predictions=unicorn_predictions,
            unicorns_found_actual=unicorns_found,
            unicorn_accuracy=unicorn_accuracy,
            portfolio_return_percent=portfolio_return,
            top_performers_analyzed=actual_performers,
            strategy_adjustments=adjustments,
            key_learnings=key_learnings,
            overall_grade=self.calculate_daily_grade(results)
        )
        
        results.overall_grade = self.calculate_daily_grade(results)
        
        return results
    
    def render_daily_improvement_dashboard(self):
        """Render the daily improvement dashboard"""
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 2px solid #ffd700;">
            <h1 style="color: #ffd700; margin: 0;">📈 Daily Improvement Cycle</h1>
            <p style="color: #d1d5db; margin: 0.5rem 0 0 0;">
                24-hour training + Top 10 validation + Strategy adjustment = Continuous improvement
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Current cycle status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Day", st.session_state.current_cycle_day)
        
        with col2:
            if st.session_state.improvement_history:
                latest_grade = st.session_state.improvement_history[-1].get('grade', 'N/A')
                st.metric("Latest Grade", latest_grade)
            else:
                st.metric("Latest Grade", "Not Started")
        
        with col3:
            total_adjustments = len(st.session_state.improvement_history)
            st.metric("Total Adjustments", total_adjustments)
        
        with col4:
            if st.session_state.improvement_history:
                avg_impact = np.mean([h.get('performance_impact', 0) for h in st.session_state.improvement_history])
                st.metric("Avg Improvement", f"{avg_impact:+.2%}")
            else:
                st.metric("Avg Improvement", "0%")
        
        # Training controls
        st.subheader("🎮 Training Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Run 24-Hour Training Cycle", type="primary"):
                with st.spinner("Running 24-hour training cycle with validation..."):
                    results = self.run_24hour_training_cycle()
                    
                    # Store results
                    results_dict = {
                        'day': st.session_state.current_cycle_day,
                        'date': results.date,
                        'grade': results.overall_grade,
                        'accuracy': results.accuracy_percent,
                        'portfolio_return': results.portfolio_return_percent,
                        'adjustments': len(results.strategy_adjustments),
                        'key_learnings': results.key_learnings,
                        'performance_impact': sum(adj.confidence_boost for adj in results.strategy_adjustments)
                    }
                    st.session_state.improvement_history.append(results_dict)
                    st.session_state.current_cycle_day += 1
                    
                    st.success(f"✅ Day {results_dict['day']} Complete! Grade: {results.overall_grade}")
                    st.rerun()
        
        with col2:
            if st.button("📊 Analyze Current Strategies"):
                self.render_strategy_analysis()
        
        # Display improvement history
        if st.session_state.improvement_history:
            self.render_improvement_timeline()
        
        # Display current strategy weights
        self.render_current_strategy_weights()
        
        # Learning insights
        if st.session_state.learning_insights:
            st.subheader("🧠 Recent Learning Insights")
            for insight in st.session_state.learning_insights[-10:]:
                st.info(insight)
    
    def render_improvement_timeline(self):
        """Render timeline of daily improvements"""
        
        st.subheader("📈 Daily Performance Timeline")
        
        history = st.session_state.improvement_history
        
        # Create performance chart
        days = [h['day'] for h in history]
        grades = [h['grade'] for h in history]
        accuracy = [h['accuracy'] for h in history]
        returns = [h['portfolio_return'] for h in history]
        
        # Convert grades to numeric for plotting
        grade_map = {'A+': 97, 'A': 93, 'B+': 87, 'B': 83, 'C+': 77, 'C': 73, 'D': 67, 'F': 50}
        grade_numeric = [grade_map.get(g, 50) for g in grades]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily Grades', 'Prediction Accuracy', 'Portfolio Returns', 'Strategy Adjustments'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "bar"}]]
        )
        
        # Daily grades
        fig.add_trace(
            go.Scatter(x=days, y=grade_numeric, mode='lines+markers+text',
                      text=grades, textposition="top center",
                      name='Grade', line=dict(color='#ffd700', width=3)),
            row=1, col=1
        )
        
        # Accuracy trend
        fig.add_trace(
            go.Scatter(x=days, y=accuracy, mode='lines+markers',
                      name='Accuracy %', line=dict(color='#10b981', width=3)),
            row=1, col=2
        )
        
        # Returns
        fig.add_trace(
            go.Scatter(x=days, y=returns, mode='lines+markers',
                      name='Portfolio Return %', line=dict(color='#06d6a0', width=3)),
            row=2, col=1
        )
        
        # Adjustments per day
        adjustments = [h['adjustments'] for h in history]
        fig.add_trace(
            go.Bar(x=days, y=adjustments, name='Adjustments',
                  marker_color='#8b5cf6'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            title_text="Daily Improvement Progress"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance summary table
        st.subheader("📊 Performance Summary")
        
        summary_data = []
        for h in history:
            summary_data.append({
                'Day': h['day'],
                'Date': h['date'].strftime('%Y-%m-%d'),
                'Grade': h['grade'],
                'Accuracy': f"{h['accuracy']:.1f}%",
                'Portfolio Return': f"{h['portfolio_return']:+.1f}%",
                'Adjustments Made': h['adjustments'],
                'Performance Impact': f"{h['performance_impact']:+.2%}"
            })
        
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)
    
    def render_current_strategy_weights(self):
        """Render current strategy weights and evolution"""
        
        st.subheader("⚖️ Current Strategy Weights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Current weights pie chart
            weights = st.session_state.strategy_evolution
            
            fig = go.Figure(data=[go.Pie(
                labels=list(weights.keys()),
                values=list(weights.values()),
                hole=0.4,
                marker_colors=px.colors.qualitative.Set3
            )])
            
            fig.update_layout(
                title="Current Strategy Allocation",
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**📋 Strategy Details:**")
            
            for strategy, weight in weights.items():
                progress_color = "#10b981" if weight > 0.2 else "#f59e0b" if weight > 0.1 else "#ef4444"
                
                st.markdown(f"""
                <div style="margin: 0.5rem 0; padding: 1rem; background: rgba(31, 41, 55, 0.5); 
                           border-radius: 8px; border-left: 4px solid {progress_color};">
                    <strong>{strategy.replace('_', ' ').title()}</strong><br>
                    Weight: {weight:.1%} | 
                    Status: {'🟢 High' if weight > 0.2 else '🟡 Medium' if weight > 0.1 else '🔴 Low'}
                </div>
                """, unsafe_allow_html=True)
    
    def render_strategy_analysis(self):
        """Render detailed strategy analysis"""
        
        st.subheader("🔍 Strategy Performance Analysis")
        
        if not st.session_state.improvement_history:
            st.info("No training history available yet. Run a training cycle first!")
            return
        
        # Analyze which strategies are improving
        st.markdown("**📈 Strategy Evolution Analysis:**")
        
        original_weights = {
            'momentum_breakout': 0.25,
            'volume_surge': 0.25, 
            'social_sentiment': 0.20,
            'whale_following': 0.15,
            'rug_detection': 0.15
        }
        
        current_weights = st.session_state.strategy_evolution
        
        for strategy in original_weights:
            original = original_weights[strategy]
            current = current_weights.get(strategy, original)
            change = current - original
            
            change_color = "#10b981" if change > 0 else "#ef4444" if change < 0 else "#9ca3af"
            change_arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            
            st.markdown(f"""
            **{strategy.replace('_', ' ').title()}** {change_arrow}
            - Original: {original:.1%} → Current: {current:.1%} 
            - Change: <span style="color: {change_color}">{change:+.1%}</span>
            """, unsafe_allow_html=True)

def render_daily_improvement_interface():
    """Main function to render the daily improvement interface"""
    engine = DailyImprovementEngine()
    engine.render_daily_improvement_dashboard()

if __name__ == "__main__":
    render_daily_improvement_interface()