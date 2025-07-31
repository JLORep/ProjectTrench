import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from src.models.base_model import BaseTradingModel, TradingSignal, SignalType
from loguru import logger

class MomentumStrategy(BaseTradingModel):
    """
    Advanced momentum-based trading strategy combining multiple indicators
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        default_config = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'volume_ma_period': 20,
            'volume_threshold': 1.5,  # Volume must be 1.5x average
            'atr_period': 14,
            'atr_multiplier': 2.0,  # For stop loss
            'position_size': 0.1,  # 10% of capital per trade
            'max_positions': 5,
            'trend_ma_fast': 20,
            'trend_ma_slow': 50,
            'min_confidence': 0.6
        }
        
        if config:
            default_config.update(config)
        
        super().__init__("Momentum Strategy", default_config)
        self.indicators = {}
    
    def fit(self, data: pd.DataFrame, **kwargs):
        """Fit the model (calculate optimal parameters from historical data)"""
        logger.info(f"Fitting {self.name} on {len(data)} data points")
        
        # Optionally optimize parameters here
        # For now, we'll use the configured parameters
        self.is_fitted = True
        
        # Calculate historical success rates for different conditions
        self._analyze_historical_patterns(data)
    
    def _analyze_historical_patterns(self, data: pd.DataFrame):
        """Analyze historical patterns to improve signal generation"""
        # This could be expanded to include ML-based pattern recognition
        pass
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate all technical indicators"""
        indicators = {}
        
        # Price data
        close = data['close']
        high = data['high']
        low = data['low']
        volume = data['volume']
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.config['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.config['rsi_period']).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = close.ewm(span=self.config['macd_fast'], adjust=False).mean()
        exp2 = close.ewm(span=self.config['macd_slow'], adjust=False).mean()
        indicators['macd'] = exp1 - exp2
        indicators['macd_signal'] = indicators['macd'].ewm(
            span=self.config['macd_signal'], adjust=False
        ).mean()
        indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
        
        # Volume analysis
        indicators['volume_ma'] = volume.rolling(self.config['volume_ma_period']).mean()
        indicators['volume_ratio'] = volume / indicators['volume_ma']
        
        # ATR for volatility
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        indicators['atr'] = tr.rolling(self.config['atr_period']).mean()
        
        # Trend indicators
        indicators['sma_fast'] = close.rolling(self.config['trend_ma_fast']).mean()
        indicators['sma_slow'] = close.rolling(self.config['trend_ma_slow']).mean()
        
        # Price momentum
        indicators['momentum'] = close.pct_change(periods=10)
        
        # Bollinger Bands
        bb_period = 20
        bb_std = close.rolling(bb_period).std()
        indicators['bb_middle'] = close.rolling(bb_period).mean()
        indicators['bb_upper'] = indicators['bb_middle'] + (bb_std * 2)
        indicators['bb_lower'] = indicators['bb_middle'] - (bb_std * 2)
        indicators['bb_width'] = indicators['bb_upper'] - indicators['bb_lower']
        
        # Store for later use
        self.indicators = indicators
        
        return indicators
    
    def predict(self, data: pd.DataFrame) -> TradingSignal:
        """Generate trading signal based on momentum indicators"""
        if len(data) < max(self.config['trend_ma_slow'], self.config['macd_slow']):
            return TradingSignal(
                timestamp=datetime.now(),
                symbol=data.attrs.get('symbol', 'UNKNOWN'),
                signal_type=SignalType.NEUTRAL,
                confidence=0.0
            )
        
        # Calculate indicators
        indicators = self._calculate_indicators(data)
        
        # Get latest values
        latest = data.iloc[-1]
        latest_indicators = {k: v.iloc[-1] if len(v) > 0 else np.nan 
                           for k, v in indicators.items()}
        
        # Generate signal
        signal_type, confidence, reasoning = self._generate_signal(
            latest, latest_indicators, data
        )
        
        # Calculate entry, stop loss, and take profit
        entry_price = latest['close']
        stop_loss = None
        take_profit = []
        
        if signal_type == SignalType.BUY:
            # Stop loss based on ATR
            stop_loss = entry_price - (
                latest_indicators['atr'] * self.config['atr_multiplier']
            )
            
            # Multiple take profit levels
            take_profit = [
                entry_price * 1.02,  # 2% profit
                entry_price * 1.05,  # 5% profit
                entry_price * 1.10   # 10% profit
            ]
        
        signal = TradingSignal(
            timestamp=latest.name if hasattr(latest, 'name') else datetime.now(),
            symbol=data.attrs.get('symbol', 'UNKNOWN'),
            signal_type=signal_type,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reasoning=reasoning
        )
        
        # Store in history
        self.signal_history.append(signal)
        
        return signal
    
    def _generate_signal(self, latest: pd.Series, indicators: Dict[str, float], 
                        data: pd.DataFrame) -> Tuple[SignalType, float, Dict[str, Any]]:
        """Generate signal based on multiple conditions"""
        bullish_signals = 0
        bearish_signals = 0
        total_weight = 0
        reasoning = {}
        
        # RSI signals
        if not np.isnan(indicators['rsi']):
            if indicators['rsi'] < self.config['rsi_oversold']:
                bullish_signals += 2
                total_weight += 2
                reasoning['rsi'] = f"Oversold (RSI: {indicators['rsi']:.2f})"
            elif indicators['rsi'] > self.config['rsi_overbought']:
                bearish_signals += 2
                total_weight += 2
                reasoning['rsi'] = f"Overbought (RSI: {indicators['rsi']:.2f})"
        
        # MACD signals
        if not np.isnan(indicators['macd_histogram']):
            if indicators['macd_histogram'] > 0 and indicators['macd'] > indicators['macd_signal']:
                bullish_signals += 1.5
                total_weight += 1.5
                reasoning['macd'] = "Bullish crossover"
            elif indicators['macd_histogram'] < 0 and indicators['macd'] < indicators['macd_signal']:
                bearish_signals += 1.5
                total_weight += 1.5
                reasoning['macd'] = "Bearish crossover"
        
        # Trend alignment
        if not np.isnan(indicators['sma_fast']) and not np.isnan(indicators['sma_slow']):
            if indicators['sma_fast'] > indicators['sma_slow']:
                bullish_signals += 1
                total_weight += 1
                reasoning['trend'] = "Uptrend (fast MA > slow MA)"
            else:
                bearish_signals += 1
                total_weight += 1
                reasoning['trend'] = "Downtrend (fast MA < slow MA)"
        
        # Volume confirmation
        if not np.isnan(indicators['volume_ratio']):
            if indicators['volume_ratio'] > self.config['volume_threshold']:
                if bullish_signals > bearish_signals:
                    bullish_signals += 1
                    reasoning['volume'] = f"High volume confirmation ({indicators['volume_ratio']:.2f}x average)"
                else:
                    bearish_signals += 1
                    reasoning['volume'] = f"High volume on downside ({indicators['volume_ratio']:.2f}x average)"
                total_weight += 1
        
        # Bollinger Band signals
        if not np.isnan(indicators['bb_lower']) and not np.isnan(indicators['bb_upper']):
            if latest['close'] < indicators['bb_lower']:
                bullish_signals += 1
                total_weight += 1
                reasoning['bollinger'] = "Price below lower Bollinger Band"
            elif latest['close'] > indicators['bb_upper']:
                bearish_signals += 1
                total_weight += 1
                reasoning['bollinger'] = "Price above upper Bollinger Band"
        
        # Calculate confidence
        if total_weight > 0:
            bull_confidence = bullish_signals / total_weight
            bear_confidence = bearish_signals / total_weight
            
            if bull_confidence > bear_confidence and bull_confidence >= self.config['min_confidence']:
                return SignalType.BUY, bull_confidence, reasoning
            elif bear_confidence > bull_confidence and bear_confidence >= self.config['min_confidence']:
                return SignalType.SELL, bear_confidence, reasoning
        
        return SignalType.NEUTRAL, 0.0, {"reason": "No clear signal"}
    
    def validate_signal(self, signal: TradingSignal, market_data: Dict[str, Any]) -> bool:
        """Validate signal against market conditions"""
        # Check if we're at max positions
        if signal.signal_type == SignalType.BUY:
            if len(self.positions) >= self.config['max_positions']:
                logger.info("Max positions reached, skipping buy signal")
                return False
        
        # Check volume
        if market_data.get('volume', 0) < market_data.get('avg_volume', 1) * 0.5:
            logger.info("Volume too low, skipping signal")
            return False
        
        # Check volatility (avoid extremely volatile conditions)
        if market_data.get('volatility', 0) > 0.1:  # 10% daily volatility
            logger.info("Market too volatile, skipping signal")
            return False
        
        return True
    
    def get_risk_metrics(self, position: Dict[str, Any]) -> Dict[str, float]:
        """Calculate risk metrics for a position"""
        entry_price = position['entry_price']
        current_price = position['current_price']
        stop_loss = position.get('stop_loss', entry_price * 0.95)
        
        # Risk/Reward ratio
        risk = entry_price - stop_loss
        reward = position.get('take_profit', [entry_price * 1.05])[0] - entry_price
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # Position risk as percentage of entry
        position_risk_pct = risk / entry_price if entry_price > 0 else 0
        
        # Current P&L
        if position['type'] == 'LONG':
            unrealized_pnl_pct = (current_price - entry_price) / entry_price
        else:
            unrealized_pnl_pct = (entry_price - current_price) / entry_price
        
        return {
            'risk_reward_ratio': risk_reward_ratio,
            'position_risk_pct': position_risk_pct,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'distance_to_stop_pct': abs(current_price - stop_loss) / current_price
        }