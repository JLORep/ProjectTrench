#!/usr/bin/env python3
"""
TrenchCoat Pro - Advanced Data Modeling & Analytics
Ultra-premium charts with ML predictions and statistical analysis
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnalytics:
    def __init__(self):
        self.colors = {
            'primary': '#10b981',    # Emerald
            'secondary': '#059669',  # Dark emerald
            'accent': '#34d399',     # Light emerald
            'danger': '#ef4444',     # Red
            'warning': '#f59e0b',    # Amber
            'info': '#3b82f6',       # Blue
            'dark': '#1f2937',       # Dark gray
            'light': '#f9fafb'       # Light gray
        }
        
    def generate_market_data(self, days=90):
        """Generate realistic crypto market data"""
        np.random.seed(42)  # For consistent data
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='H')
        
        # Simulate realistic crypto price movements
        base_price = 1000
        volatility = 0.05
        trend = 0.001
        
        prices = []
        volume = []
        
        for i in range(len(dates)):
            # Price with trend and volatility
            if i == 0:
                price = base_price
            else:
                price_change = np.random.normal(trend, volatility) * prices[-1]
                price = max(prices[-1] + price_change, 0.01)
            
            prices.append(price)
            
            # Volume correlated with price volatility
            vol = np.random.lognormal(15, 1) * (1 + abs(price_change/prices[-1]) if i > 0 else 1)
            volume.append(vol)
        
        return pd.DataFrame({
            'timestamp': dates,
            'price': prices,
            'volume': volume,
            'market_cap': np.array(prices) * np.random.uniform(1e6, 1e9, len(prices)),
            'rsi': np.random.uniform(20, 80, len(dates)),
            'macd': np.random.normal(0, 5, len(dates)),
            'bollinger_upper': np.array(prices) * 1.05,
            'bollinger_lower': np.array(prices) * 0.95
        })
    
    def create_ml_prediction_chart(self, data):
        """Advanced ML price prediction with confidence intervals"""
        
        # Prepare features for ML model
        data['price_ma_7'] = data['price'].rolling(7).mean()
        data['price_ma_21'] = data['price'].rolling(21).mean()
        data['volume_ma'] = data['volume'].rolling(7).mean()
        data['price_change'] = data['price'].pct_change()
        data['volume_change'] = data['volume'].pct_change()
        
        # Create features
        features = ['price_ma_7', 'price_ma_21', 'volume_ma', 'rsi', 'macd', 'price_change', 'volume_change']
        data_clean = data.dropna()
        
        X = data_clean[features]
        y = data_clean['price']
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Future predictions
        future_periods = 24  # 24 hours ahead
        last_features = X.iloc[-1:].values
        last_features_scaled = scaler.transform(last_features)
        
        future_predictions = []
        confidence_upper = []
        confidence_lower = []
        
        for _ in range(future_periods):
            pred = model.predict(last_features_scaled)[0]
            
            # Simple confidence interval (in practice, you'd use more sophisticated methods)
            confidence = pred * 0.1  # 10% confidence interval
            
            future_predictions.append(pred)
            confidence_upper.append(pred + confidence)
            confidence_lower.append(pred - confidence)
        
        # Create future timestamps
        future_dates = pd.date_range(start=data['timestamp'].iloc[-1] + timedelta(hours=1), 
                                   periods=future_periods, freq='H')
        
        # Create the chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('🤖 AI Price Prediction', '📊 Feature Importance', 
                          '🎯 Model Performance', '📈 Prediction Confidence'),
            specs=[[{"secondary_y": True}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "scatter"}]],
            vertical_spacing=0.12
        )
        
        # Historical prices
        fig.add_trace(
            go.Scatter(
                x=data['timestamp'], 
                y=data['price'],
                name='Historical Price',
                line=dict(color=self.colors['primary'], width=2),
                hovertemplate='<b>Price:</b> $%{y:.2f}<br><b>Time:</b> %{x}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Future predictions
        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=future_predictions,
                name='AI Prediction',
                line=dict(color=self.colors['accent'], width=3, dash='dash'),
                hovertemplate='<b>Predicted:</b> $%{y:.2f}<br><b>Time:</b> %{x}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Confidence intervals
        fig.add_trace(
            go.Scatter(
                x=list(future_dates) + list(future_dates[::-1]),
                y=confidence_upper + confidence_lower[::-1],
                fill='toself',
                fillcolor=f'rgba(52, 211, 153, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Band',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=True)
        
        fig.add_trace(
            go.Bar(
                x=feature_importance['importance'],
                y=feature_importance['feature'],
                orientation='h',
                marker_color=self.colors['info'],
                name='Feature Importance'
            ),
            row=1, col=2
        )
        
        # Model performance scatter
        fig.add_trace(
            go.Scatter(
                x=y_test,
                y=y_pred,
                mode='markers',
                marker=dict(
                    color=self.colors['primary'],
                    size=8,
                    opacity=0.7
                ),
                name=f'R² = {r2:.3f}',
                hovertemplate='<b>Actual:</b> $%{x:.2f}<br><b>Predicted:</b> $%{y:.2f}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Perfect prediction line
        min_val, max_val = min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())
        fig.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                line=dict(color=self.colors['danger'], dash='dash'),
                name='Perfect Prediction',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Prediction confidence over time
        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=[(u-l)/p*100 for u, l, p in zip(confidence_upper, confidence_lower, future_predictions)],
                mode='lines+markers',
                line=dict(color=self.colors['warning'], width=3),
                marker=dict(size=8),
                name='Confidence %',
                hovertemplate='<b>Confidence:</b> ±%{y:.1f}%<br><b>Time:</b> %{x}<extra></extra>'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': '🧠 Advanced ML Price Prediction Model',
                'x': 0.5,
                'font': {'size': 24, 'color': 'white'}
            },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=800,
            showlegend=True,
            legend=dict(
                bgcolor='rgba(31, 41, 55, 0.8)',
                bordercolor='rgba(16, 185, 129, 0.5)',
                borderwidth=1
            )
        )
        
        # Update axes
        for i in range(1, 3):
            for j in range(1, 3):
                fig.update_xaxes(
                    gridcolor='rgba(16, 185, 129, 0.2)',
                    row=i, col=j
                )
                fig.update_yaxes(
                    gridcolor='rgba(16, 185, 129, 0.2)',
                    row=i, col=j
                )
        
        return fig, {
            'r2_score': r2,
            'mae': mae,
            'future_price': future_predictions[-1],
            'confidence': (confidence_upper[-1] - confidence_lower[-1]) / future_predictions[-1] * 100
        }
    
    def create_correlation_heatmap(self, data):
        """Beautiful correlation matrix heatmap"""
        
        # Calculate correlations
        numeric_cols = ['price', 'volume', 'market_cap', 'rsi', 'macd']
        corr_matrix = data[numeric_cols].corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale=[
                [0, '#ef4444'],      # Red for negative
                [0.5, '#1f2937'],    # Dark for zero
                [1, '#10b981']       # Emerald for positive
            ],
            zmid=0,
            text=corr_matrix.round(3).values,
            texttemplate="%{text}",
            textfont={"size": 12, "color": "white"},
            hoverongaps=False,
            hovertemplate='<b>%{x} vs %{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '🔗 Market Data Correlation Matrix',
                'x': 0.5,
                'font': {'size': 20, 'color': 'white'}
            },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        
        return fig
    
    def create_portfolio_optimization(self):
        """Modern Portfolio Theory visualization"""
        
        # Simulate multiple assets
        assets = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT']
        returns = np.random.multivariate_normal(
            [0.001, 0.002, 0.003, 0.0015, 0.0012],  # Expected returns
            [[0.01, 0.005, 0.003, 0.002, 0.001],    # Covariance matrix
             [0.005, 0.012, 0.004, 0.003, 0.002],
             [0.003, 0.004, 0.015, 0.002, 0.001],
             [0.002, 0.003, 0.002, 0.008, 0.001],
             [0.001, 0.002, 0.001, 0.001, 0.006]],
            1000  # 1000 simulations
        )
        
        # Calculate portfolio metrics
        num_portfolios = 10000
        results = np.zeros((3, num_portfolios))
        
        for i in range(num_portfolios):
            weights = np.random.random(5)
            weights /= np.sum(weights)
            
            portfolio_return = np.sum(returns.mean(axis=0) * weights) * 252
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(np.cov(returns.T), weights))) * np.sqrt(252)
            sharpe_ratio = portfolio_return / portfolio_std
            
            results[0, i] = portfolio_return
            results[1, i] = portfolio_std
            results[2, i] = sharpe_ratio
        
        # Create efficient frontier
        fig = go.Figure()
        
        # Portfolio scatter
        fig.add_trace(go.Scatter(
            x=results[1],
            y=results[0],
            mode='markers',
            marker=dict(
                color=results[2],
                colorscale='Viridis',
                size=4,
                opacity=0.6,
                colorbar=dict(
                    title="Sharpe Ratio",
                    titlefont=dict(color='white'),
                    tickfont=dict(color='white')
                )
            ),
            name='Portfolios',
            hovertemplate='<b>Risk:</b> %{x:.3f}<br><b>Return:</b> %{y:.3f}<br><b>Sharpe:</b> %{marker.color:.3f}<extra></extra>'
        ))
        
        # Optimal portfolio
        max_sharpe_idx = np.argmax(results[2])
        fig.add_trace(go.Scatter(
            x=[results[1, max_sharpe_idx]],
            y=[results[0, max_sharpe_idx]],
            mode='markers',
            marker=dict(
                color=self.colors['accent'],
                size=15,
                symbol='star',
                line=dict(color='white', width=2)
            ),
            name='Optimal Portfolio',
            hovertemplate='<b>Optimal Portfolio</b><br><b>Risk:</b> %{x:.3f}<br><b>Return:</b> %{y:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '🎯 Portfolio Optimization - Efficient Frontier',
                'x': 0.5,
                'font': {'size': 20, 'color': 'white'}
            },
            xaxis_title='Risk (Volatility)',
            yaxis_title='Expected Return',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=600,
            xaxis=dict(gridcolor='rgba(16, 185, 129, 0.2)'),
            yaxis=dict(gridcolor='rgba(16, 185, 129, 0.2)')
        )
        
        return fig, {
            'optimal_return': results[0, max_sharpe_idx],
            'optimal_risk': results[1, max_sharpe_idx],
            'optimal_sharpe': results[2, max_sharpe_idx]
        }
    
    def render_advanced_analytics(self):
        """Render all advanced analytics components"""
        
        st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
                    border-radius: 15px; border: 1px solid rgba(16, 185, 129, 0.3);'>
            <h1 style='color: #10b981; margin: 0; font-size: 2.5rem; font-weight: 700;'>
                🧠 Advanced Data Modeling
            </h1>
            <p style='color: #a3a3a3; margin-top: 0.5rem; font-size: 1.2rem;'>
                AI-Powered Analytics & Predictive Intelligence
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate market data
        market_data = self.generate_market_data()
        
        # ML Prediction Analysis
        st.markdown("### 🤖 Machine Learning Price Prediction")
        with st.spinner("Training AI model..."):
            ml_chart, ml_metrics = self.create_ml_prediction_chart(market_data)
            st.plotly_chart(ml_chart, use_container_width=True)
        
        # Display ML metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "🎯 Model Accuracy (R²)", 
                f"{ml_metrics['r2_score']:.3f}",
                delta=f"{(ml_metrics['r2_score']-0.8)*100:.1f}%" if ml_metrics['r2_score'] > 0.8 else None
            )
        with col2:
            st.metric(
                "📊 Mean Abs Error", 
                f"${ml_metrics['mae']:.2f}",
            )
        with col3:
            st.metric(
                "🔮 24h Prediction", 
                f"${ml_metrics['future_price']:.2f}",
                delta=f"±{ml_metrics['confidence']:.1f}%"
            )
        with col4:
            confidence_color = "normal" if ml_metrics['confidence'] < 15 else "inverse"
            st.metric(
                "🎪 Confidence Level", 
                f"{100-ml_metrics['confidence']:.1f}%",
                delta=f"±{ml_metrics['confidence']:.1f}%",
                delta_color=confidence_color
            )
        
        st.markdown("---")
        
        # Correlation Analysis
        st.markdown("### 🔗 Market Correlation Analysis")
        corr_chart = self.create_correlation_heatmap(market_data)
        st.plotly_chart(corr_chart, use_container_width=True)
        
        st.markdown("---")
        
        # Portfolio Optimization
        st.markdown("### 🎯 Portfolio Optimization")
        with st.spinner("Calculating efficient frontier..."):
            portfolio_chart, portfolio_metrics = self.create_portfolio_optimization()
            st.plotly_chart(portfolio_chart, use_container_width=True)
        
        # Portfolio metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "🎯 Optimal Return", 
                f"{portfolio_metrics['optimal_return']*100:.1f}%/year"
            )
        with col2:
            st.metric(
                "⚡ Risk Level", 
                f"{portfolio_metrics['optimal_risk']*100:.1f}%"
            )
        with col3:
            st.metric(
                "🏆 Sharpe Ratio", 
                f"{portfolio_metrics['optimal_sharpe']:.2f}",
                delta="Excellent" if portfolio_metrics['optimal_sharpe'] > 1.5 else "Good"
            )

if __name__ == "__main__":
    analytics = AdvancedAnalytics()
    analytics.render_advanced_analytics()