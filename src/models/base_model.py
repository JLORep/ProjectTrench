from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    NEUTRAL = "NEUTRAL"

@dataclass
class TradingSignal:
    timestamp: datetime
    symbol: str
    signal_type: SignalType
    confidence: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: List[float] = field(default_factory=list)
    reasoning: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Position:
    symbol: str
    entry_price: float
    entry_time: datetime
    quantity: float
    position_type: str  # LONG or SHORT
    stop_loss: Optional[float] = None
    take_profit: List[float] = field(default_factory=list)
    current_price: Optional[float] = None
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    status: str = "OPEN"  # OPEN, CLOSED, PARTIAL
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    
    def update_pnl(self, current_price: float):
        """Update unrealized P&L"""
        self.current_price = current_price
        if self.position_type == "LONG":
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        else:  # SHORT
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity
    
    def close(self, exit_price: float, exit_time: datetime):
        """Close the position"""
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.status = "CLOSED"
        if self.position_type == "LONG":
            self.realized_pnl = (exit_price - self.entry_price) * self.quantity
        else:  # SHORT
            self.realized_pnl = (self.entry_price - exit_price) * self.quantity
        self.unrealized_pnl = 0.0

@dataclass
class ModelPerformance:
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    
    def update(self, trade_pnl: float):
        """Update performance metrics with a new trade"""
        self.total_trades += 1
        self.total_pnl += trade_pnl
        
        if trade_pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        self.win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0

class BaseTradingModel(ABC):
    """Base class for all trading models"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.is_fitted = False
        self.performance = ModelPerformance()
        self.positions: Dict[str, Position] = {}
        self.signal_history: List[TradingSignal] = []
        
    @abstractmethod
    def fit(self, data: pd.DataFrame, **kwargs):
        """Train the model on historical data"""
        pass
    
    @abstractmethod
    def predict(self, data: pd.DataFrame) -> TradingSignal:
        """Generate trading signal for current data"""
        pass
    
    @abstractmethod
    def validate_signal(self, signal: TradingSignal, market_data: Dict[str, Any]) -> bool:
        """Validate signal against current market conditions"""
        pass
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 10000) -> Dict[str, Any]:
        """Run backtest on historical data"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before backtesting")
        
        capital = initial_capital
        equity_curve = []
        trades = []
        
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            signal = self.predict(current_data)
            
            # Skip if no signal
            if signal.signal_type == SignalType.NEUTRAL:
                equity_curve.append(capital)
                continue
            
            # Validate signal
            market_data = {
                'volume': current_data.iloc[-1]['volume'],
                'volatility': current_data['close'].pct_change().std(),
                'trend': self._calculate_trend(current_data)
            }
            
            if not self.validate_signal(signal, market_data):
                equity_curve.append(capital)
                continue
            
            # Execute trade logic
            if signal.signal_type == SignalType.BUY and signal.symbol not in self.positions:
                # Open long position
                position_size = capital * self.config.get('position_size', 0.1)
                quantity = position_size / signal.entry_price
                
                position = Position(
                    symbol=signal.symbol,
                    entry_price=signal.entry_price,
                    entry_time=signal.timestamp,
                    quantity=quantity,
                    position_type="LONG",
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit
                )
                
                self.positions[signal.symbol] = position
                capital -= position_size
                
            elif signal.signal_type == SignalType.SELL and signal.symbol in self.positions:
                # Close position
                position = self.positions[signal.symbol]
                position.close(signal.entry_price, signal.timestamp)
                
                capital += position.quantity * signal.entry_price
                self.performance.update(position.realized_pnl)
                
                trades.append({
                    'symbol': position.symbol,
                    'entry_time': position.entry_time,
                    'exit_time': position.exit_time,
                    'entry_price': position.entry_price,
                    'exit_price': position.exit_price,
                    'pnl': position.realized_pnl,
                    'return': position.realized_pnl / (position.entry_price * position.quantity)
                })
                
                del self.positions[signal.symbol]
            
            equity_curve.append(capital + sum(p.unrealized_pnl for p in self.positions.values()))
        
        # Calculate final metrics
        equity_curve = np.array(equity_curve)
        returns = np.diff(equity_curve) / equity_curve[:-1]
        
        results = {
            'initial_capital': initial_capital,
            'final_capital': equity_curve[-1],
            'total_return': (equity_curve[-1] - initial_capital) / initial_capital,
            'performance': self.performance.__dict__,
            'equity_curve': equity_curve.tolist(),
            'trades': trades,
            'max_drawdown': self._calculate_max_drawdown(equity_curve),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns)
        }
        
        return results
    
    def _calculate_trend(self, data: pd.DataFrame) -> str:
        """Calculate market trend"""
        if len(data) < 20:
            return "NEUTRAL"
        
        sma_short = data['close'].rolling(10).mean().iloc[-1]
        sma_long = data['close'].rolling(20).mean().iloc[-1]
        
        if sma_short > sma_long * 1.02:
            return "BULLISH"
        elif sma_short < sma_long * 0.98:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _calculate_max_drawdown(self, equity_curve: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / peak
        return np.min(drawdown)
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        if np.std(excess_returns) == 0:
            return 0.0
        
        return np.sqrt(252) * np.mean(excess_returns) / np.std(excess_returns)
    
    def save_model(self, filepath: str):
        """Save model configuration and state"""
        model_data = {
            'name': self.name,
            'config': self.config,
            'is_fitted': self.is_fitted,
            'performance': self.performance.__dict__,
            'signal_history': [
                {
                    'timestamp': s.timestamp.isoformat(),
                    'symbol': s.symbol,
                    'signal_type': s.signal_type.value,
                    'confidence': s.confidence,
                    'entry_price': s.entry_price,
                    'stop_loss': s.stop_loss,
                    'take_profit': s.take_profit,
                    'reasoning': s.reasoning
                }
                for s in self.signal_history[-100:]  # Keep last 100 signals
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
    
    def load_model(self, filepath: str):
        """Load model configuration and state"""
        with open(filepath, 'r') as f:
            model_data = json.load(f)
        
        self.name = model_data['name']
        self.config = model_data['config']
        self.is_fitted = model_data['is_fitted']
        self.performance = ModelPerformance(**model_data['performance'])
        
        # Reconstruct signal history
        self.signal_history = []
        for signal_data in model_data.get('signal_history', []):
            signal = TradingSignal(
                timestamp=datetime.fromisoformat(signal_data['timestamp']),
                symbol=signal_data['symbol'],
                signal_type=SignalType(signal_data['signal_type']),
                confidence=signal_data['confidence'],
                entry_price=signal_data.get('entry_price'),
                stop_loss=signal_data.get('stop_loss'),
                take_profit=signal_data.get('take_profit', []),
                reasoning=signal_data.get('reasoning', {})
            )
            self.signal_history.append(signal)