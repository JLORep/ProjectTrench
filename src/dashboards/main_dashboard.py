import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Optional
from src.data.database import CoinDatabase
from src.data.enrichment_pipeline import DataEnrichmentPipeline
from src.telegram.telegram_monitor import TelegramSignalMonitor
from src.strategies.momentum_strategy import MomentumStrategy
from config.config import settings

# Page configuration
st.set_page_config(
    page_title="TrenchCoat Crypto Analytics",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
    }
    .signal-card {
        background: #2d2d2d;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .alert-card {
        background: rgba(255, 152, 0, 0.1);
        border: 1px solid #ff9800;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class CryptoDashboard:
    def __init__(self):
        self.db = CoinDatabase()
        self.init_session_state()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'selected_coin' not in st.session_state:
            st.session_state.selected_coin = None
        if 'refresh_counter' not in st.session_state:
            st.session_state.refresh_counter = 0
        if 'strategy' not in st.session_state:
            st.session_state.strategy = MomentumStrategy()
    
    def render_header(self):
        """Render dashboard header"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("🔮 TrenchCoat Crypto Analytics")
            st.markdown("*Advanced cryptocurrency analysis and signal generation*")
        
        with col2:
            if st.button("🔄 Refresh Data", key="refresh"):
                st.session_state.refresh_counter += 1
                st.experimental_rerun()
        
        with col3:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.metric("Last Update", current_time)
    
    def render_market_overview(self):
        """Render market overview section"""
        st.header("📊 Market Overview")
        
        # Fetch market metrics
        with st.spinner("Loading market data..."):
            metrics = self._get_market_metrics()
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Total Market Cap",
                f"${metrics['total_market_cap']:,.0f}",
                f"{metrics['market_cap_change_24h']:.2f}%"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.metric(
                "BTC Dominance",
                f"{metrics['btc_dominance']:.1f}%",
                f"{metrics['btc_dominance_change']:.2f}%"
            )
        
        with col3:
            st.metric(
                "24h Volume",
                f"${metrics['total_volume_24h']:,.0f}",
                f"{metrics['volume_change_24h']:.2f}%"
            )
        
        with col4:
            fear_greed = metrics.get('fear_greed_index', 50)
            color = "🔴" if fear_greed < 30 else "🟡" if fear_greed < 70 else "🟢"
            st.metric(
                "Fear & Greed Index",
                f"{color} {fear_greed}",
                self._get_fear_greed_label(fear_greed)
            )
    
    def render_portfolio_tracking(self):
        """Render portfolio tracking section"""
        st.header("💼 Portfolio Tracking")
        
        # Get tracked coins
        tracked_coins = self._get_tracked_coins()
        
        if not tracked_coins.empty:
            # Portfolio performance chart
            fig = self._create_portfolio_chart(tracked_coins)
            st.plotly_chart(fig, use_container_width=True)
            
            # Individual coin performance
            st.subheader("Individual Coin Performance")
            
            # Create sortable dataframe
            display_df = tracked_coins[[
                'symbol', 'current_price', 'price_change_24h', 
                'volume_24h', 'market_cap', 'rsi', 'signal'
            ]].copy()
            
            # Format columns
            display_df['price_change_24h'] = display_df['price_change_24h'].apply(
                lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
            )
            display_df['volume_24h'] = display_df['volume_24h'].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
            )
            display_df['market_cap'] = display_df['market_cap'].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
            )
            
            # Display with conditional formatting
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "symbol": st.column_config.TextColumn("Symbol", width="small"),
                    "current_price": st.column_config.NumberColumn(
                        "Price", format="$%.6f", width="medium"
                    ),
                    "signal": st.column_config.TextColumn(
                        "Signal", width="small",
                        help="Trading signal based on momentum strategy"
                    )
                }
            )
        else:
            st.info("No coins currently tracked. Add coins to start tracking.")
    
    def render_signal_monitor(self):
        """Render real-time signal monitoring"""
        st.header("📡 Signal Monitor")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Recent signals
            st.subheader("Recent Signals")
            signals = self._get_recent_signals()
            
            for signal in signals:
                signal_color = {
                    'BUY': '#4CAF50',
                    'SELL': '#f44336',
                    'HOLD': '#ff9800'
                }.get(signal['signal_type'], '#9e9e9e')
                
                st.markdown(f"""
                <div class="signal-card" style="border-left-color: {signal_color}">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <h4>{signal['symbol']} - {signal['signal_type']}</h4>
                            <p>Confidence: {signal['confidence']:.2%}</p>
                            <p>Entry: ${signal['entry_price']:.6f}</p>
                        </div>
                        <div style="text-align: right;">
                            <p>{signal['timestamp']}</p>
                            <p>Source: {signal['source']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Signal statistics
            st.subheader("Signal Statistics (24h)")
            stats = self._get_signal_stats()
            
            st.metric("Total Signals", stats['total'])
            st.metric("Buy Signals", stats['buy'], f"{stats['buy_pct']:.1f}%")
            st.metric("Sell Signals", stats['sell'], f"{stats['sell_pct']:.1f}%")
            st.metric("Avg Confidence", f"{stats['avg_confidence']:.2%}")
    
    def render_technical_analysis(self):
        """Render technical analysis section"""
        st.header("📈 Technical Analysis")
        
        # Coin selector
        coins = self._get_available_coins()
        selected_coin = st.selectbox(
            "Select Coin for Analysis",
            options=coins['symbol'].tolist(),
            index=0 if not coins.empty else None
        )
        
        if selected_coin:
            st.session_state.selected_coin = selected_coin
            
            # Get coin data
            coin_data = self._get_coin_analysis_data(selected_coin)
            
            if coin_data is not None:
                # Create technical analysis charts
                fig = make_subplots(
                    rows=4, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=[0.5, 0.2, 0.15, 0.15],
                    subplot_titles=('Price & Moving Averages', 'Volume', 'RSI', 'MACD')
                )
                
                # Price chart with MA
                fig.add_trace(
                    go.Candlestick(
                        x=coin_data.index,
                        open=coin_data['open'],
                        high=coin_data['high'],
                        low=coin_data['low'],
                        close=coin_data['close'],
                        name="Price"
                    ),
                    row=1, col=1
                )
                
                # Add moving averages
                if 'sma_20' in coin_data:
                    fig.add_trace(
                        go.Scatter(
                            x=coin_data.index,
                            y=coin_data['sma_20'],
                            name="SMA 20",
                            line=dict(color='orange', width=1)
                        ),
                        row=1, col=1
                    )
                
                if 'sma_50' in coin_data:
                    fig.add_trace(
                        go.Scatter(
                            x=coin_data.index,
                            y=coin_data['sma_50'],
                            name="SMA 50",
                            line=dict(color='blue', width=1)
                        ),
                        row=1, col=1
                    )
                
                # Volume
                colors = ['red' if close < open else 'green' 
                         for close, open in zip(coin_data['close'], coin_data['open'])]
                
                fig.add_trace(
                    go.Bar(
                        x=coin_data.index,
                        y=coin_data['volume'],
                        name="Volume",
                        marker_color=colors
                    ),
                    row=2, col=1
                )
                
                # RSI
                if 'rsi' in coin_data:
                    fig.add_trace(
                        go.Scatter(
                            x=coin_data.index,
                            y=coin_data['rsi'],
                            name="RSI",
                            line=dict(color='purple')
                        ),
                        row=3, col=1
                    )
                    
                    # Add RSI levels
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
                
                # MACD
                if all(col in coin_data for col in ['macd', 'macd_signal', 'macd_histogram']):
                    fig.add_trace(
                        go.Scatter(
                            x=coin_data.index,
                            y=coin_data['macd'],
                            name="MACD",
                            line=dict(color='blue')
                        ),
                        row=4, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=coin_data.index,
                            y=coin_data['macd_signal'],
                            name="Signal",
                            line=dict(color='red')
                        ),
                        row=4, col=1
                    )
                    
                    fig.add_trace(
                        go.Bar(
                            x=coin_data.index,
                            y=coin_data['macd_histogram'],
                            name="Histogram"
                        ),
                        row=4, col=1
                    )
                
                # Update layout
                fig.update_layout(
                    title=f"{selected_coin} Technical Analysis",
                    xaxis_title="Date",
                    height=1000,
                    showlegend=True,
                    template="plotly_dark"
                )
                
                fig.update_xaxes(rangeslider_visible=False)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display current indicators
                self._render_indicator_summary(coin_data)
    
    def render_strategy_backtesting(self):
        """Render strategy backtesting section"""
        st.header("🎯 Strategy Backtesting")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Strategy Configuration")
            
            # Strategy parameters
            rsi_period = st.slider("RSI Period", 5, 30, 14)
            rsi_oversold = st.slider("RSI Oversold", 20, 40, 30)
            rsi_overbought = st.slider("RSI Overbought", 60, 80, 70)
            position_size = st.slider("Position Size (%)", 5, 50, 10) / 100
            
            if st.button("Run Backtest"):
                # Update strategy config
                st.session_state.strategy.config.update({
                    'rsi_period': rsi_period,
                    'rsi_oversold': rsi_oversold,
                    'rsi_overbought': rsi_overbought,
                    'position_size': position_size
                })
                
                # Run backtest
                with st.spinner("Running backtest..."):
                    results = self._run_backtest()
                    st.session_state.backtest_results = results
        
        with col2:
            if 'backtest_results' in st.session_state:
                results = st.session_state.backtest_results
                
                # Performance metrics
                st.subheader("Performance Metrics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Return",
                        f"{results['total_return']:.2%}",
                        f"${results['final_capital'] - results['initial_capital']:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Win Rate",
                        f"{results['performance']['win_rate']:.2%}",
                        f"{results['performance']['winning_trades']}/{results['performance']['total_trades']}"
                    )
                
                with col3:
                    st.metric(
                        "Max Drawdown",
                        f"{results['max_drawdown']:.2%}"
                    )
                
                with col4:
                    st.metric(
                        "Sharpe Ratio",
                        f"{results['sharpe_ratio']:.2f}"
                    )
                
                # Equity curve
                st.subheader("Equity Curve")
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        y=results['equity_curve'],
                        mode='lines',
                        name='Portfolio Value',
                        line=dict(color='#4CAF50', width=2)
                    )
                )
                
                fig.update_layout(
                    title="Portfolio Value Over Time",
                    yaxis_title="Value ($)",
                    template="plotly_dark",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    def _get_market_metrics(self) -> Dict:
        """Fetch market metrics from database"""
        # This would fetch real data from your database
        # For now, returning mock data
        return {
            'total_market_cap': 2.1e12,
            'market_cap_change_24h': 2.5,
            'btc_dominance': 48.5,
            'btc_dominance_change': -0.3,
            'total_volume_24h': 89e9,
            'volume_change_24h': 5.2,
            'fear_greed_index': 65
        }
    
    def _get_fear_greed_label(self, value: int) -> str:
        """Get fear and greed index label"""
        if value < 25:
            return "Extreme Fear"
        elif value < 45:
            return "Fear"
        elif value < 55:
            return "Neutral"
        elif value < 75:
            return "Greed"
        else:
            return "Extreme Greed"
    
    def _get_tracked_coins(self) -> pd.DataFrame:
        """Get tracked coins with latest data"""
        # Fetch from database
        query = """
        SELECT 
            c.symbol,
            c.ticker,
            c.price as current_price,
            c.price_change_24h,
            c.volume_24h,
            c.market_cap,
            i.indicator_value as rsi
        FROM coins c
        LEFT JOIN (
            SELECT coin_id, indicator_value
            FROM indicators
            WHERE indicator_name = 'rsi'
            AND timestamp = (
                SELECT MAX(timestamp) 
                FROM indicators i2 
                WHERE i2.coin_id = indicators.coin_id
            )
        ) i ON c.id = i.coin_id
        WHERE c.price IS NOT NULL
        ORDER BY c.market_cap DESC
        LIMIT 20
        """
        
        # Mock data for demonstration
        data = pd.DataFrame({
            'symbol': ['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC'],
            'ticker': ['Bitcoin', 'Ethereum', 'Solana', 'Avalanche', 'Polygon'],
            'current_price': [65000, 3500, 120, 35, 0.8],
            'price_change_24h': [2.5, 3.2, -1.5, 4.0, 1.8],
            'volume_24h': [25e9, 15e9, 2e9, 500e6, 300e6],
            'market_cap': [1.2e12, 420e9, 50e9, 12e9, 7e9],
            'rsi': [55, 62, 35, 70, 48],
            'signal': ['HOLD', 'HOLD', 'BUY', 'SELL', 'HOLD']
        })
        
        return data
    
    def _create_portfolio_chart(self, tracked_coins: pd.DataFrame) -> go.Figure:
        """Create portfolio allocation chart"""
        fig = go.Figure(data=[
            go.Pie(
                labels=tracked_coins['symbol'],
                values=tracked_coins['market_cap'],
                hole=0.4,
                textinfo='label+percent',
                marker=dict(
                    colors=px.colors.sequential.Viridis,
                    line=dict(color='white', width=2)
                )
            )
        ])
        
        fig.update_layout(
            title="Portfolio Allocation by Market Cap",
            template="plotly_dark",
            height=400
        )
        
        return fig
    
    def _get_recent_signals(self) -> List[Dict]:
        """Get recent trading signals from live database"""
        try:
            from src.data.database import CoinDatabase
            db = CoinDatabase()
            signals = db.get_telegram_signals(limit=10, min_confidence=0.6)
            
            # Convert database signals to dashboard format
            formatted_signals = []
            for signal in signals:
                formatted_signal = {
                    'symbol': signal.get('coin_symbol', 'UNKNOWN'),
                    'signal_type': signal.get('signal_type', 'UNKNOWN').upper(),
                    'confidence': signal.get('confidence', 0),
                    'entry_price': signal.get('entry_price', 0),
                    'timestamp': signal.get('timestamp', 'Unknown'),
                    'source': f"Telegram: {signal.get('channel_name', 'Unknown')}"
                }
                formatted_signals.append(formatted_signal)
            
            if formatted_signals:
                return formatted_signals
            
        except Exception as e:
            # Log error but don't crash - fall back to demo data
            print(f"Warning: Could not load live signals: {e}")
        
        # Fallback to demo data if no live signals available
        return [
            {
                'symbol': 'SOL',
                'signal_type': 'BUY',
                'confidence': 0.75,
                'entry_price': 119.50,
                'timestamp': '2025-01-31 10:30:00',
                'source': 'Demo: Momentum Strategy'
            },
            {
                'symbol': 'AVAX',
                'signal_type': 'SELL',
                'confidence': 0.82,
                'entry_price': 35.20,
                'timestamp': '2025-01-31 09:45:00',
                'source': 'Demo: RSI Overbought'
            }
        ]
    
    def _get_signal_stats(self) -> Dict:
        """Get signal statistics from live database"""
        try:
            from src.data.database import CoinDatabase
            db = CoinDatabase()
            signals = db.get_telegram_signals(limit=100)  # Get more signals for stats
            
            if signals:
                total = len(signals)
                buy_signals = len([s for s in signals if s.get('signal_type', '').upper() == 'BUY'])
                sell_signals = len([s for s in signals if s.get('signal_type', '').upper() == 'SELL'])
                avg_confidence = sum(s.get('confidence', 0) for s in signals) / total if total > 0 else 0
                
                return {
                    'total': total,
                    'buy': buy_signals,
                    'sell': sell_signals,
                    'buy_pct': (buy_signals / total * 100) if total > 0 else 0,
                    'sell_pct': (sell_signals / total * 100) if total > 0 else 0,
                    'avg_confidence': avg_confidence
                }
                
        except Exception as e:
            # Log error but don't crash - fall back to demo data
            print(f"Warning: Could not load signal stats: {e}")
        
        # Fallback to demo data
        return {
            'total': 45,
            'buy': 28,
            'sell': 17,
            'buy_pct': 62.2,
            'sell_pct': 37.8,
            'avg_confidence': 0.68
        }
    
    def _get_available_coins(self) -> pd.DataFrame:
        """Get available coins for analysis"""
        # Mock data for demonstration
        return pd.DataFrame({
            'symbol': ['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC', 'LINK', 'DOT'],
            'name': ['Bitcoin', 'Ethereum', 'Solana', 'Avalanche', 'Polygon', 'Chainlink', 'Polkadot']
        })
    
    def _get_coin_analysis_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get analysis data for a specific coin"""
        # Generate mock OHLCV data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='1H')
        
        # Random walk for price
        returns = np.random.normal(0.001, 0.02, 100)
        price = 100 * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'open': price * (1 + np.random.uniform(-0.01, 0.01, 100)),
            'high': price * (1 + np.random.uniform(0, 0.02, 100)),
            'low': price * (1 + np.random.uniform(-0.02, 0, 100)),
            'close': price,
            'volume': np.random.uniform(1e6, 1e7, 100)
        }, index=dates)
        
        # Calculate indicators
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        return df
    
    def _render_indicator_summary(self, coin_data: pd.DataFrame):
        """Render indicator summary"""
        latest = coin_data.iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Price", f"${latest['close']:.6f}")
            st.metric("24h Volume", f"${latest['volume']:,.0f}")
        
        with col2:
            rsi_value = latest.get('rsi', 50)
            rsi_color = "🔴" if rsi_value > 70 else "🟢" if rsi_value < 30 else "🟡"
            st.metric("RSI", f"{rsi_color} {rsi_value:.2f}")
            
            macd_hist = latest.get('macd_histogram', 0)
            macd_signal = "📈 Bullish" if macd_hist > 0 else "📉 Bearish"
            st.metric("MACD Signal", macd_signal)
        
        with col3:
            # Price vs MA
            if 'sma_20' in latest and pd.notna(latest['sma_20']):
                price_vs_ma = ((latest['close'] - latest['sma_20']) / latest['sma_20']) * 100
                st.metric("Price vs SMA20", f"{price_vs_ma:+.2f}%")
    
    def _run_backtest(self) -> Dict:
        """Run strategy backtest"""
        # Get historical data
        symbol = st.session_state.selected_coin or 'BTC'
        data = self._get_coin_analysis_data(symbol)
        
        if data is not None:
            # Fit strategy
            st.session_state.strategy.fit(data)
            
            # Run backtest
            results = st.session_state.strategy.backtest(data, initial_capital=10000)
            
            return results
        
        return {}
    
    def render_sidebar(self):
        """Render sidebar with navigation and settings"""
        with st.sidebar:
            st.image("https://via.placeholder.com/150", caption="TrenchCoat Analytics")
            
            st.header("Navigation")
            page = st.radio(
                "Go to",
                ["Market Overview", "Portfolio", "Signals", "Technical Analysis", "Backtesting"]
            )
            
            st.header("Settings")
            
            # Refresh rate
            refresh_rate = st.selectbox(
                "Auto Refresh",
                ["Off", "30s", "1m", "5m"],
                index=0
            )
            
            # Theme
            theme = st.selectbox(
                "Theme",
                ["Dark", "Light"],
                index=0
            )
            
            # Data source priorities
            st.header("Data Sources")
            st.checkbox("BirdEye", value=True)
            st.checkbox("DexScreener", value=True)
            st.checkbox("Jupiter", value=True)
            st.checkbox("CoinGecko", value=False)
            
            return page
    
    def run(self):
        """Main dashboard entry point"""
        # Render header
        self.render_header()
        
        # Render sidebar and get selected page
        page = self.render_sidebar()
        
        # Render selected page
        if page == "Market Overview":
            self.render_market_overview()
        elif page == "Portfolio":
            self.render_portfolio_tracking()
        elif page == "Signals":
            self.render_signal_monitor()
        elif page == "Technical Analysis":
            self.render_technical_analysis()
        elif page == "Backtesting":
            self.render_strategy_backtesting()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "Built with ❤️ by TrenchCoat Analytics | "
            "[Documentation](https://docs.trenchcoat.io) | "
            "[API Status](https://status.trenchcoat.io)"
        )

# Run the dashboard
if __name__ == "__main__":
    dashboard = CryptoDashboard()
    dashboard.run()