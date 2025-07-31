import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
from loguru import logger

from src.analysis.rug_intelligence import RugIntelligenceEngine, RugStatus
from src.data.database import CoinDatabase
from src.telegram.telegram_monitor import TelegramSignalMonitor

class TradeStatus(Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED" 
    MONITORING = "MONITORING"
    EXITED = "EXITED"
    STOPPED_OUT = "STOPPED_OUT"
    RUGGED = "RUGGED"

@dataclass
class Trade:
    """Individual trade tracking"""
    id: str
    contract_address: str
    symbol: str
    entry_timestamp: datetime
    entry_price: float
    position_size: float
    position_value: float
    
    # Targets
    profit_target: float
    stop_loss: float
    time_limit: datetime
    
    # Current status
    status: TradeStatus = TradeStatus.PENDING
    current_price: float = 0
    peak_price: float = 0
    unrealized_pnl: float = 0
    
    # Exit details
    exit_timestamp: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: str = ""
    realized_pnl: float = 0
    
    # Risk management
    rug_detection_alerts: List[str] = field(default_factory=list)
    risk_level: str = "MEDIUM"
    
    # Performance tracking
    max_gain_percent: float = 0
    max_drawdown_percent: float = 0

@dataclass
class TradingSession:
    """Daily trading session tracking"""
    date: datetime
    starting_balance: float
    current_balance: float
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    rugged_trades: int = 0
    
    total_profit: float = 0
    best_trade_profit: float = 0
    worst_trade_loss: float = 0
    
    active_trades: List[Trade] = field(default_factory=list)
    completed_trades: List[Trade] = field(default_factory=list)

class AutomatedTrader:
    """
    WEAPONIZED AUTOMATED TRADING ENGINE
    Executes microsecond trades based on Telegram signals and rug intelligence
    """
    
    def __init__(self, initial_balance: float = 10000):
        self.db = CoinDatabase()
        self.rug_engine = RugIntelligenceEngine(self.db)
        self.telegram_monitor = TelegramSignalMonitor(self.db)
        
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.max_position_size = 0.05  # 5% max per trade
        self.max_concurrent_trades = 10
        
        self.current_session = TradingSession(
            date=datetime.now(),
            starting_balance=initial_balance,
            current_balance=initial_balance
        )
        
        self.trade_history: List[Trade] = []
        self.performance_metrics = {}
        
        # Trading parameters
        self.trading_active = False
        self.risk_management_active = True
        self.rug_detection_active = True
        
    async def start_trading_engine(self):
        """Start the automated trading engine"""
        logger.info("🚀 STARTING AUTOMATED TRADING ENGINE")
        logger.info(f"💰 Initial balance: ${self.initial_balance:,.2f}")
        logger.info(f"🎯 Max position size: {self.max_position_size:.1%}")
        
        self.trading_active = True
        
        # Start monitoring systems
        await asyncio.gather(
            self._telegram_signal_processor(),
            self._position_monitor(),
            self._rug_detection_monitor(),
            self._performance_tracker()
        )
    
    async def _telegram_signal_processor(self):
        """Process incoming Telegram signals in real-time"""
        logger.info("📡 Starting Telegram signal processor...")
        
        # Set up signal callback
        async def process_signal(signal):
            await self._evaluate_new_signal(signal)
        
        # This would connect to the actual Telegram monitor
        # For now, simulate with test signals
        while self.trading_active:
            await asyncio.sleep(5)  # Check every 5 seconds
            # In production, this would process real signals
    
    async def _evaluate_new_signal(self, signal_data: Dict) -> Optional[Trade]:
        """Evaluate new Telegram signal for trading opportunity"""
        contract_address = signal_data.get('contract_address')
        if not contract_address:
            return None
        
        logger.info(f"🔍 Evaluating signal: {signal_data.get('symbol')} ({contract_address[:10]}...)")
        
        # Run rug intelligence analysis
        analysis = await self.rug_engine.analyze_new_token(contract_address, signal_data)
        
        action = analysis.get('action')
        confidence = analysis.get('confidence', 0)
        
        logger.info(f"📊 Analysis result: {action} (confidence: {confidence:.2f})")
        
        if action in ['BUY_AGGRESSIVE', 'BUY_MODERATE']:
            trade = await self._execute_trade(analysis)
            if trade:
                logger.info(f"✅ Trade executed: {trade.symbol} @ ${trade.entry_price:.6f}")
                return trade
        else:
            logger.info(f"⏭️ Skipping trade: {analysis.get('reasoning')}")
        
        return None
    
    async def _execute_trade(self, analysis: Dict) -> Optional[Trade]:
        """Execute a trade based on analysis"""
        if len(self.current_session.active_trades) >= self.max_concurrent_trades:
            logger.warning("🚫 Max concurrent trades reached")
            return None
        
        contract_address = analysis['contract_address']
        symbol = analysis['symbol']
        token_data = analysis['token_data']
        exit_strategy = analysis.get('exit_strategy', {})
        
        # Calculate position size
        recommended_size = analysis.get('position_size', self.max_position_size)
        position_size = min(recommended_size, self.max_position_size)
        position_value = self.current_balance * position_size
        
        # Current price
        entry_price = token_data.get('price', 0)
        if entry_price <= 0:
            logger.error("Invalid entry price")
            return None
        
        # Create trade
        trade = Trade(
            id=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            contract_address=contract_address,
            symbol=symbol,
            entry_timestamp=datetime.now(),
            entry_price=entry_price,
            position_size=position_size,
            position_value=position_value,
            
            profit_target=exit_strategy.get('profit_target', entry_price * 1.5),
            stop_loss=exit_strategy.get('stop_loss', entry_price * 0.85),
            time_limit=datetime.now() + timedelta(hours=exit_strategy.get('time_limit_hours', 8)),
            
            status=TradeStatus.EXECUTED,
            current_price=entry_price,
            peak_price=entry_price,
            risk_level=analysis.get('risk_level', 'MEDIUM')
        )
        
        # Add to active trades
        self.current_session.active_trades.append(trade)
        self.current_session.total_trades += 1
        
        # Update balance (simulated)
        self.current_balance -= position_value
        
        # Store in database
        await self._store_trade(trade)
        
        logger.info(f"🎯 Trade Details:")
        logger.info(f"   Entry: ${trade.entry_price:.6f}")
        logger.info(f"   Target: ${trade.profit_target:.6f} (+{((trade.profit_target/trade.entry_price)-1)*100:.1f}%)")
        logger.info(f"   Stop: ${trade.stop_loss:.6f} ({((trade.stop_loss/trade.entry_price)-1)*100:.1f}%)")
        logger.info(f"   Size: ${trade.position_value:.2f} ({trade.position_size:.1%})")
        
        return trade
    
    async def _position_monitor(self):
        """Monitor all active positions"""
        logger.info("👀 Starting position monitor...")
        
        while self.trading_active:
            if not self.current_session.active_trades:
                await asyncio.sleep(10)
                continue
            
            # Check each active trade
            for trade in self.current_session.active_trades.copy():
                await self._update_trade_status(trade)
            
            await asyncio.sleep(2)  # Check every 2 seconds
    
    async def _update_trade_status(self, trade: Trade):
        """Update individual trade status"""
        try:
            # Get current price
            from src.data.free_api_providers import FreeAPIProviders
            
            async with FreeAPIProviders() as api:
                current_data = await api.get_comprehensive_data(trade.contract_address)
            
            if not current_data:
                return
            
            current_price = current_data.get('price', 0)
            if current_price <= 0:
                return
            
            # Update trade data
            trade.current_price = current_price
            trade.peak_price = max(trade.peak_price, current_price)
            
            # Calculate P&L
            price_change = (current_price - trade.entry_price) / trade.entry_price
            trade.unrealized_pnl = trade.position_value * price_change
            trade.max_gain_percent = max(trade.max_gain_percent, price_change * 100)
            
            if price_change < 0:
                trade.max_drawdown_percent = min(trade.max_drawdown_percent, price_change * 100)
            
            # Check exit conditions
            exit_reason = None
            
            # Profit target hit
            if current_price >= trade.profit_target:
                exit_reason = "PROFIT_TARGET"
            
            # Stop loss hit
            elif current_price <= trade.stop_loss:
                exit_reason = "STOP_LOSS"
            
            # Time limit reached
            elif datetime.now() >= trade.time_limit:
                exit_reason = "TIME_LIMIT"
            
            # Rug detection (checked separately)
            
            if exit_reason:
                await self._exit_trade(trade, exit_reason)
        
        except Exception as e:
            logger.error(f"Error updating trade {trade.id}: {e}")
    
    async def _rug_detection_monitor(self):
        """Monitor for rug pulls in active positions"""
        logger.info("🚨 Starting rug detection monitor...")
        
        while self.trading_active and self.rug_detection_active:
            if not self.current_session.active_trades:
                await asyncio.sleep(5)
                continue
            
            # Check each position for rug signals
            for trade in self.current_session.active_trades.copy():
                rug_analysis = await self.rug_engine.real_time_rug_detection(trade.contract_address)
                
                if rug_analysis.get('rug_detected'):
                    confidence = rug_analysis.get('confidence', 0)
                    signals = rug_analysis.get('signals', [])
                    
                    logger.warning(f"🚨 RUG DETECTED: {trade.symbol}")
                    logger.warning(f"   Confidence: {confidence:.2f}")
                    logger.warning(f"   Signals: {', '.join(signals)}")
                    
                    # EMERGENCY EXIT
                    await self._exit_trade(trade, "RUG_DETECTED", emergency=True)
            
            await asyncio.sleep(1)  # Check every second for rugs
    
    async def _exit_trade(self, trade: Trade, reason: str, emergency: bool = False):
        """Exit a trade"""
        trade.exit_timestamp = datetime.now()
        trade.exit_price = trade.current_price
        trade.exit_reason = reason
        
        # Calculate final P&L
        price_change = (trade.exit_price - trade.entry_price) / trade.entry_price
        trade.realized_pnl = trade.position_value * price_change
        
        # Update status
        if reason == "RUG_DETECTED":
            trade.status = TradeStatus.RUGGED
            self.current_session.rugged_trades += 1
        elif reason == "STOP_LOSS":
            trade.status = TradeStatus.STOPPED_OUT
        else:
            trade.status = TradeStatus.EXITED
        
        # Update session stats
        if trade.realized_pnl > 0:
            self.current_session.winning_trades += 1
            self.current_session.best_trade_profit = max(
                self.current_session.best_trade_profit, 
                trade.realized_pnl
            )
        else:
            self.current_session.losing_trades += 1
            self.current_session.worst_trade_loss = min(
                self.current_session.worst_trade_loss,
                trade.realized_pnl
            )
        
        self.current_session.total_profit += trade.realized_pnl
        self.current_balance += (trade.position_value + trade.realized_pnl)
        
        # Move to completed trades
        self.current_session.active_trades.remove(trade)
        self.current_session.completed_trades.append(trade)
        
        # Log exit
        pnl_percent = price_change * 100
        emoji = "🟢" if trade.realized_pnl > 0 else "🔴"
        
        logger.info(f"{emoji} TRADE EXITED: {trade.symbol}")
        logger.info(f"   Reason: {reason}")
        logger.info(f"   Entry: ${trade.entry_price:.6f}")
        logger.info(f"   Exit: ${trade.exit_price:.6f}")
        logger.info(f"   P&L: ${trade.realized_pnl:.2f} ({pnl_percent:+.1f}%)")
        logger.info(f"   Duration: {trade.exit_timestamp - trade.entry_timestamp}")
        
        if emergency:
            logger.warning("🚨 EMERGENCY EXIT EXECUTED")
    
    async def _performance_tracker(self):
        """Track and log performance metrics"""
        logger.info("📈 Starting performance tracker...")
        
        while self.trading_active:
            await asyncio.sleep(60)  # Update every minute
            
            # Calculate current performance
            win_rate = (self.current_session.winning_trades / 
                       max(self.current_session.total_trades, 1)) * 100
            
            total_return = ((self.current_balance / self.initial_balance) - 1) * 100
            
            # Log performance every 10 minutes
            if datetime.now().minute % 10 == 0:
                logger.info("📊 PERFORMANCE UPDATE:")
                logger.info(f"   Balance: ${self.current_balance:,.2f}")
                logger.info(f"   Total Return: {total_return:+.2f}%")
                logger.info(f"   Active Trades: {len(self.current_session.active_trades)}")
                logger.info(f"   Win Rate: {win_rate:.1f}%")
                logger.info(f"   Daily P&L: ${self.current_session.total_profit:+,.2f}")
    
    async def _store_trade(self, trade: Trade):
        """Store trade in database"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            
            # Create trades table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    contract_address TEXT,
                    symbol TEXT,
                    entry_timestamp TIMESTAMP,
                    entry_price REAL,
                    position_size REAL,
                    position_value REAL,
                    profit_target REAL,
                    stop_loss REAL,
                    time_limit TIMESTAMP,
                    status TEXT,
                    exit_timestamp TIMESTAMP,
                    exit_price REAL,
                    exit_reason TEXT,
                    realized_pnl REAL,
                    max_gain_percent REAL,
                    max_drawdown_percent REAL,
                    risk_level TEXT
                )
            """)
            
            # Insert trade
            cursor.execute("""
                INSERT OR REPLACE INTO trades VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.id, trade.contract_address, trade.symbol,
                trade.entry_timestamp, trade.entry_price, trade.position_size,
                trade.position_value, trade.profit_target, trade.stop_loss,
                trade.time_limit, trade.status.value, trade.exit_timestamp,
                trade.exit_price, trade.exit_reason, trade.realized_pnl,
                trade.max_gain_percent, trade.max_drawdown_percent, trade.risk_level
            ))
            
            conn.commit()
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate comprehensive daily trading report"""
        session = self.current_session
        
        win_rate = (session.winning_trades / max(session.total_trades, 1)) * 100
        total_return = ((self.current_balance / self.initial_balance) - 1) * 100
        
        # Calculate Sharpe ratio (simplified)
        if session.completed_trades:
            returns = [t.realized_pnl / t.position_value for t in session.completed_trades]
            avg_return = np.mean(returns) if returns else 0
            return_volatility = np.std(returns) if len(returns) > 1 else 0
            sharpe_ratio = avg_return / return_volatility if return_volatility > 0 else 0
        else:
            sharpe_ratio = 0
        
        report = {
            'date': session.date.date().isoformat(),
            'trading_performance': {
                'starting_balance': session.starting_balance,
                'ending_balance': self.current_balance,
                'total_return_pct': total_return,
                'total_profit': session.total_profit,
                'total_trades': session.total_trades,
                'winning_trades': session.winning_trades,
                'losing_trades': session.losing_trades,
                'rugged_trades': session.rugged_trades,
                'win_rate_pct': win_rate,
                'best_trade': session.best_trade_profit,
                'worst_trade': session.worst_trade_loss,
                'sharpe_ratio': sharpe_ratio
            },
            'active_positions': [
                {
                    'symbol': t.symbol,
                    'entry_price': t.entry_price,
                    'current_price': t.current_price,
                    'unrealized_pnl': t.unrealized_pnl,
                    'max_gain_pct': t.max_gain_percent
                } for t in session.active_trades
            ],
            'rug_detection_stats': {
                'rugs_avoided': 0,  # Would track successful rug detections
                'false_positives': 0,
                'detection_accuracy': 0
            }
        }
        
        return report

# Test function to simulate trading
async def simulate_trading_day():
    """Simulate a day of automated trading"""
    trader = AutomatedTrader(initial_balance=10000)
    
    # Simulate some signals
    test_signals = [
        {
            'contract_address': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'symbol': 'USDC',
            'signal_type': 'BUY',
            'confidence': 0.8
        }
    ]
    
    logger.info("🎮 STARTING TRADING SIMULATION")
    
    for signal in test_signals:
        await trader._evaluate_new_signal(signal)
    
    # Generate report
    report = trader.generate_daily_report()
    logger.info("📊 Daily Report Generated")
    
    return report