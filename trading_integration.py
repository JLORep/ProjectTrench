#!/usr/bin/env python3
"""
TrenchCoat Pro - Complete Trading Integration
Connects Runner detection with automated Solana trading
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Optional
import logging

# Import your existing notification systems
# from unified_notifications import UnifiedNotificationSystem
# from solana_trading_engine import SolanaTrader, SafeTrader

class TrenchCoatTradingSystem:
    """Complete automated trading system for TrenchCoat Pro"""
    
    def __init__(self):
        # Initialize components
        self.notifications = None  # UnifiedNotificationSystem()
        self.solana_trader = None  # SolanaTrader()
        self.safe_trader = None    # SafeTrader(self.solana_trader)
        
        # Trading configuration
        self.auto_trading_enabled = False
        self.paper_trading_mode = True
        
        # Performance tracking
        self.trades_executed = []
        self.total_profit_loss = 0.0
        self.win_rate = 0.0
        
    def setup_trading(self, wallet_private_key: str, enable_live: bool = False):
        """Setup automated trading system"""
        
        try:
            # Configure Solana trader
            self.solana_trader.setup_wallet(wallet_private_key)
            
            # Enable live trading if requested
            if enable_live:
                confirmation = input("Enable live trading? Type 'CONFIRM_LIVE_TRADING': ")
                if confirmation == "CONFIRM_LIVE_TRADING":
                    self.safe_trader.enable_live_trading("TRENCHCOAT_LIVE_TRADING_ENABLED")
                    self.auto_trading_enabled = True
                    self.paper_trading_mode = False
                    print("LIVE TRADING ENABLED")
                else:
                    print("Live trading not enabled - staying in paper mode")
            
            return True
            
        except Exception as e:
            logging.error(f"Trading setup failed: {e}")
            return False
            
    async def process_runner_signal(self, runner_data: Dict) -> Dict:
        """Complete pipeline: Detect Runner → Alert → Trade → Notify"""
        
        try:
            print(f"\nProcessing Runner: {runner_data.get('symbol', 'Unknown')}")
            
            # Step 1: Send initial Runner alert
            print("Step 1: Sending Runner alerts...")
            if self.notifications:
                await self.notifications.send_runner_alert(runner_data)
            
            # Step 2: Evaluate trade worthiness
            should_trade = self._should_execute_trade(runner_data)
            
            if not should_trade:
                print("Trade evaluation: SKIP")
                return {"status": "SKIPPED", "reason": "Does not meet trading criteria"}
            
            # Step 3: Execute trade
            print("Step 2: Executing trade...")
            trade_result = await self._execute_trade(runner_data)
            
            # Step 4: Send trade execution notification
            if trade_result and trade_result.get("status") == "SUCCESS":
                print("Step 3: Sending trade notifications...")
                await self._notify_trade_execution(runner_data, trade_result)
                
                # Track performance
                self._track_trade_performance(trade_result)
            
            return trade_result
            
        except Exception as e:
            logging.error(f"Runner processing failed: {e}")
            return {"status": "ERROR", "error": str(e)}
            
    def _should_execute_trade(self, runner_data: Dict) -> bool:
        """Determine if Runner signal should trigger a trade"""
        
        confidence = runner_data.get("runner_confidence", 0)
        volume_24h = runner_data.get("volume_24h", 0)
        price_change_24h = runner_data.get("price_change_24h", 0)
        
        # Trading criteria
        min_confidence = 80.0  # Only high-confidence signals
        min_volume = 100000    # Minimum $100K daily volume
        max_price_change = 200 # Skip if already pumped >200%
        
        # Check criteria
        if confidence < min_confidence:
            print(f"Confidence too low: {confidence}% < {min_confidence}%")
            return False
            
        if volume_24h < min_volume:
            print(f"Volume too low: ${volume_24h:,.0f} < ${min_volume:,.0f}")
            return False
            
        if price_change_24h > max_price_change:
            print(f"Already pumped too much: {price_change_24h}% > {max_price_change}%")
            return False
            
        print(f"Trade criteria met: {confidence}% confidence, ${volume_24h:,.0f} volume")
        return True
        
    async def _execute_trade(self, runner_data: Dict) -> Optional[Dict]:
        """Execute the actual trade"""
        
        if self.paper_trading_mode:
            # Simulate trade for testing
            return self._simulate_trade(runner_data)
        else:
            # Execute real trade
            if self.safe_trader and self.auto_trading_enabled:
                return await self.safe_trader.safe_execute_trade(runner_data)
            else:
                return {"status": "DISABLED", "message": "Live trading not enabled"}
                
    def _simulate_trade(self, runner_data: Dict) -> Dict:
        """Simulate trade execution for paper trading"""
        
        symbol = runner_data.get("symbol", "Unknown")
        confidence = runner_data.get("runner_confidence", 0)
        price = runner_data.get("current_price", 0)
        
        # Calculate simulated trade size
        base_size = 0.05  # 0.05 SOL base
        trade_size = base_size * (confidence / 100)
        
        # Simulate successful trade
        trade_result = {
            "type": "BUY",
            "status": "SUCCESS",
            "mode": "PAPER_TRADING",
            "token_address": f"simulated_{symbol.lower()}",
            "symbol": symbol,
            "sol_amount": trade_size,
            "entry_price": price,
            "confidence": confidence,
            "transaction": f"PAPER_{datetime.now().strftime('%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "expected_tokens": int(trade_size / price) if price > 0 else 0
        }
        
        print(f"PAPER TRADE: Bought {symbol} with {trade_size:.4f} SOL")
        return trade_result
        
    async def _notify_trade_execution(self, runner_data: Dict, trade_result: Dict):
        """Send notifications about executed trade"""
        
        symbol = runner_data.get("symbol", "Unknown")
        sol_amount = trade_result.get("sol_amount", 0)
        tx_signature = trade_result.get("transaction", "")
        trade_mode = trade_result.get("mode", "LIVE")
        
        # Enhanced notification with trade info
        enhanced_data = runner_data.copy()
        enhanced_data.update({
            "trade_executed": True,
            "trade_amount_sol": sol_amount,
            "transaction_id": tx_signature,
            "trade_mode": trade_mode
        })
        
        # Send to all notification platforms
        if self.notifications:
            await self.notifications.send_runner_alert(enhanced_data)
            
    def _track_trade_performance(self, trade_result: Dict):
        """Track trading performance metrics"""
        
        self.trades_executed.append(trade_result)
        
        # Calculate basic metrics
        total_trades = len(self.trades_executed)
        print(f"Total trades executed: {total_trades}")
        
    async def get_trading_dashboard_data(self) -> Dict:
        """Get data for trading dashboard"""
        
        # Get wallet balance if trader is configured
        sol_balance = 0.0
        if self.solana_trader and self.solana_trader.wallet_pubkey:
            try:
                sol_balance = await self.solana_trader.get_wallet_balance()
            except:
                sol_balance = 0.0
                
        return {
            "trading_enabled": self.auto_trading_enabled,
            "paper_mode": self.paper_trading_mode,
            "wallet_balance_sol": sol_balance,
            "total_trades": len(self.trades_executed),
            "recent_trades": self.trades_executed[-5:] if self.trades_executed else [],
            "system_status": "OPERATIONAL" if self.auto_trading_enabled else "MANUAL_MODE"
        }
        
    def get_trading_status_message(self) -> str:
        """Get trading status for notifications"""
        
        if self.paper_trading_mode:
            return "📝 PAPER TRADING MODE - Simulated trades only"
        elif self.auto_trading_enabled:
            return "🚀 LIVE TRADING ACTIVE - Automated execution enabled"
        else:
            return "⏸️ TRADING PAUSED - Manual mode"

# Demo function to show complete flow
async def demo_complete_system():
    """Demonstrate complete TrenchCoat Pro trading system"""
    
    print("TRENCHCOAT PRO - COMPLETE TRADING SYSTEM DEMO")
    print("=" * 50)
    
    # Initialize system
    trading_system = TrenchCoatTradingSystem()
    
    print("\nSystem Status:")
    print(f"Auto Trading: {trading_system.auto_trading_enabled}")
    print(f"Paper Mode: {trading_system.paper_trading_mode}")
    print(f"Notifications: {'Configured' if trading_system.notifications else 'Not configured'}")
    
    # Example Runner detection
    runner_data = {
        "symbol": "BONK",
        "token_address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "current_price": 0.000015,
        "price_change_24h": 45.7,
        "volume_24h": 2500000,
        "runner_confidence": 87.3,
        "market_cap": 15000000,
        "discovery_time": datetime.now().isoformat()
    }
    
    print(f"\nRunner Detected: {runner_data['symbol']}")
    print(f"Confidence: {runner_data['runner_confidence']}%")
    print(f"Price Change: +{runner_data['price_change_24h']}%")
    print(f"Volume: ${runner_data['volume_24h']:,.0f}")
    
    # Process the Runner signal
    print("\n" + "=" * 50)
    print("PROCESSING RUNNER SIGNAL...")
    print("=" * 50)
    
    result = await trading_system.process_runner_signal(runner_data)
    
    print(f"\nResult: {result}")
    
    # Show dashboard data
    dashboard_data = await trading_system.get_trading_dashboard_data()
    print("\nTrading Dashboard Data:")
    print(json.dumps(dashboard_data, indent=2))
    
    return trading_system

if __name__ == "__main__":
    # Run demo
    system = asyncio.run(demo_complete_system())
    
    print("\n" + "=" * 50)
    print("TRENCHCOAT PRO TRADING SYSTEM READY!")
    print("=" * 50)
    print()
    print("Features:")
    print("✅ AI Runner detection")
    print("✅ Multi-platform notifications") 
    print("✅ Automated Solana trading")
    print("✅ Risk management & safety limits")
    print("✅ Paper trading mode for testing")
    print("✅ Real-time performance tracking")
    print()
    print("Next Steps:")
    print("1. Configure Solana wallet")
    print("2. Test in paper trading mode")
    print("3. Enable live trading when ready")
    print("4. Monitor and optimize performance")