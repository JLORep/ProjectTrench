#!/usr/bin/env python3
"""
Incoming Coins Monitor - Real-time Telegram coin detection and processing
Integrates with existing telegram_monitor infrastructure for seamless processing
"""
import asyncio
import time
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
import sqlite3
from pathlib import Path
import streamlit as st

# Safe imports for existing infrastructure
try:
    from src.telegram.telegram_monitor import TelegramSignalMonitor, CoinSignal, SignalPattern
    telegram_monitor_available = True
except ImportError:
    telegram_monitor_available = False
    TelegramSignalMonitor = None
    CoinSignal = None
    SignalPattern = None

try:
    from telegram_enrichment_pipeline import EnrichedCoin
    enrichment_available = True
except ImportError:
    enrichment_available = False
    EnrichedCoin = None

try:
    from unified_notifications import unified_notifier
    notifications_available = True
except ImportError:
    notifications_available = False
    unified_notifier = None

try:
    from database_manager import DatabaseManager
    db_manager_available = True
except ImportError:
    db_manager_available = False
    DatabaseManager = None

try:
    from coin_image_system import CoinImageSystem
    image_system_available = True
except ImportError:
    image_system_available = False
    CoinImageSystem = None

try:
    from src.data.database import CoinDatabase
    database_available = True
except ImportError:
    database_available = False
    CoinDatabase = None

@dataclass
class IncomingCoin:
    """Represents a newly detected coin from Telegram"""
    ticker: str
    contract_address: Optional[str]
    detected_time: datetime
    channel_name: str
    message_content: str
    confidence: float
    signal_type: str
    processing_status: str = "pending"
    image_url: Optional[str] = None
    enrichment_data: Optional[Dict] = None
    notification_sent: bool = False

class IncomingCoinsIntegrator:
    """Integrates with existing Telegram infrastructure for incoming coin processing"""
    
    def __init__(self):
        # Initialize with existing pattern matcher if available
        if telegram_monitor_available and SignalPattern:
            self.pattern_matcher = SignalPattern()
        else:
            self.pattern_matcher = None
            
        # Initialize database
        if database_available and CoinDatabase:
            self.coin_db = CoinDatabase()
        else:
            self.coin_db = None
            
        # Initialize monitor if available
        if telegram_monitor_available and TelegramSignalMonitor and self.coin_db:
            self.telegram_monitor = TelegramSignalMonitor(self.coin_db)
        else:
            self.telegram_monitor = None
    
    def extract_coins_from_telegram_signal(self, signal: 'CoinSignal') -> List[IncomingCoin]:
        """Convert telegram signal to incoming coin format"""
        if not signal:
            return []
            
        incoming_coin = IncomingCoin(
            ticker=signal.ticker,
            contract_address=signal.contract_address,
            detected_time=signal.timestamp.replace(tzinfo=None) if signal.timestamp.tzinfo else signal.timestamp,
            channel_name=signal.channel_name,
            message_content=signal.raw_message[:500],
            confidence=signal.confidence,
            signal_type=signal.signal_type.lower()
        )
        
        return [incoming_coin]
    
    def extract_coins_from_message_fallback(self, message: str, channel_name: str) -> List[IncomingCoin]:
        """Fallback method when telegram monitor is not available"""
        coins = []
        message_lower = message.lower()
        
        # Basic ticker extraction
        ticker_patterns = [
            r'\$([A-Z]{2,10})\b',  # $PEPE format
            r'(?:token|coin):\s*([A-Z]{2,10})',  # token: PEPE
        ]
        
        tickers = set()
        for pattern in ticker_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            tickers.update([match.upper() for match in matches])
        
        # Basic contract pattern
        contracts = re.findall(r'([1-9A-HJ-NP-Za-km-z]{32,44})', message)
        
        # Simple signal detection
        signal_type = 'watch'
        if any(word in message_lower for word in ['buy', 'gem', 'rocket', 'moon']):
            signal_type = 'buy'
        if any(word in message_lower for word in ['strong buy', 'buy now', '100x']):
            signal_type = 'strong_buy'
        
        # Basic confidence
        confidence = 0.6 if signal_type != 'watch' else 0.4
        
        for ticker in tickers:
            if ticker not in ['USD', 'BTC', 'ETH', 'THE', 'AND', 'OR']:
                coin = IncomingCoin(
                    ticker=ticker,
                    contract_address=contracts[0] if contracts else None,
                    detected_time=datetime.now(),
                    channel_name=channel_name,
                    message_content=message[:500],
                    confidence=confidence,
                    signal_type=signal_type
                )
                coins.append(coin)
        
        return coins

class IncomingCoinsProcessor:
    """Processes incoming coins through enrichment pipeline"""
    
    def __init__(self):
        self.pattern_matcher = TelegramPatternMatcher()
        self.processing_queue = []
        self.processed_coins = []
        self.db_path = Path("data/trench.db")
        
        # Initialize components
        if image_system_available:
            self.image_system = CoinImageSystem()
        else:
            self.image_system = None
            
        if db_manager_available:
            self.db_manager = DatabaseManager()
        else:
            self.db_manager = None
    
    async def process_telegram_message(self, message: str, channel_name: str) -> List[IncomingCoin]:
        """Process a new Telegram message for coins"""
        # Extract coins from message
        detected_coins = self.pattern_matcher.extract_coins_from_message(message, channel_name)
        
        # Filter out already processed coins (within last 24 hours)
        new_coins = []
        for coin in detected_coins:
            if not self._is_recently_processed(coin.ticker):
                new_coins.append(coin)
                self.processing_queue.append(coin)
        
        # Process new coins
        for coin in new_coins:
            await self._process_single_coin(coin)
        
        return new_coins
    
    async def _process_single_coin(self, coin: IncomingCoin):
        """Process a single incoming coin through the full pipeline"""
        try:
            coin.processing_status = "processing"
            
            # Stage 1: Enrich basic data
            await self._enrich_coin_data(coin)
            
            # Stage 2: Fetch coin image
            if self.image_system:
                await self._fetch_coin_image(coin)
            
            # Stage 3: Store to database
            await self._store_coin_to_database(coin)
            
            # Stage 4: Send notification
            await self._send_coin_notification(coin)
            
            coin.processing_status = "completed"
            self.processed_coins.append(coin)
            
        except Exception as e:
            coin.processing_status = f"error: {str(e)}"
            print(f"Error processing coin {coin.ticker}: {e}")
    
    async def _enrich_coin_data(self, coin: IncomingCoin):
        """Enrich coin with market data"""
        # Simulate API calls - replace with real enrichment
        await asyncio.sleep(0.5)  # Simulate API delay
        
        coin.enrichment_data = {
            'market_cap': 1000000 + (hash(coin.ticker) % 10000000),
            'volume_24h': 50000 + (hash(coin.ticker) % 500000),
            'liquidity': 25000 + (hash(coin.ticker) % 250000),
            'smart_wallets': 10 + (hash(coin.ticker) % 100),
            'discovery_price': 0.0001 + (hash(coin.ticker) % 1000) * 0.0001,
            'enriched_time': datetime.now().isoformat()
        }
    
    async def _fetch_coin_image(self, coin: IncomingCoin):
        """Fetch coin image using the image system"""
        if not self.image_system:
            return
            
        try:
            # Use contract address if available, otherwise ticker
            identifier = coin.contract_address or coin.ticker
            image_url = await self.image_system.get_coin_image_async(identifier)
            coin.image_url = image_url
        except Exception as e:
            print(f"Error fetching image for {coin.ticker}: {e}")
    
    async def _store_coin_to_database(self, coin: IncomingCoin):
        """Store coin to database"""
        try:
            # Create database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create incoming_coins table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incoming_coins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    contract_address TEXT,
                    detected_time TEXT NOT NULL,
                    channel_name TEXT NOT NULL,
                    message_content TEXT,
                    confidence REAL,
                    signal_type TEXT,
                    processing_status TEXT,
                    image_url TEXT,
                    enrichment_data TEXT,
                    notification_sent BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert coin data
            cursor.execute("""
                INSERT INTO incoming_coins 
                (ticker, contract_address, detected_time, channel_name, message_content, 
                 confidence, signal_type, processing_status, image_url, enrichment_data, notification_sent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                coin.ticker,
                coin.contract_address,
                coin.detected_time.isoformat(),
                coin.channel_name,
                coin.message_content,
                coin.confidence,
                coin.signal_type,
                coin.processing_status,
                coin.image_url,
                json.dumps(coin.enrichment_data) if coin.enrichment_data else None,
                coin.notification_sent
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing coin {coin.ticker} to database: {e}")
    
    async def _send_coin_notification(self, coin: IncomingCoin):
        """Send notification about newly processed coin"""
        if not notifications_available or not unified_notifier:
            return
            
        try:
            # Prepare notification message
            message = f"""🚨 **NEW COIN DETECTED & PROCESSED**

🪙 **Coin:** ${coin.ticker}
📡 **Channel:** {coin.channel_name}
🎯 **Signal:** {coin.signal_type.upper()}
📊 **Confidence:** {coin.confidence:.1%}
⏰ **Detected:** {coin.detected_time.strftime('%H:%M:%S')}

📈 **Quick Stats:**
• Market Cap: ${coin.enrichment_data.get('market_cap', 0):,.0f}
• Volume 24h: ${coin.enrichment_data.get('volume_24h', 0):,.0f}
• Smart Wallets: {coin.enrichment_data.get('smart_wallets', 0)}

🔗 **Contract:** `{coin.contract_address or 'Not available'}`

✅ **Status:** Fully processed and added to database
"""
            
            # Send to Discord
            await unified_notifier.send_discord_notification(
                message=message,
                title="New Coin Alert",
                color=0x00ff00,  # Green
                channel_type="coin_data"
            )
            
            coin.notification_sent = True
            
        except Exception as e:
            print(f"Error sending notification for {coin.ticker}: {e}")
    
    def _is_recently_processed(self, ticker: str, hours: int = 24) -> bool:
        """Check if coin was processed recently"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Check in-memory processed coins
        for processed_coin in self.processed_coins:
            if (processed_coin.ticker == ticker and 
                processed_coin.detected_time > cutoff_time):
                return True
        
        # Check database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM incoming_coins 
                WHERE ticker = ? AND detected_time > ?
            """, (ticker, cutoff_time.isoformat()))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception:
            return False
    
    def get_recent_incoming_coins(self, hours: int = 24) -> List[Dict]:
        """Get recently processed incoming coins"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM incoming_coins 
                WHERE detected_time > ? 
                ORDER BY detected_time DESC
                LIMIT 50
            """, (cutoff_time,))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            
            coins = []
            for row in rows:
                coin_dict = dict(zip(columns, row))
                if coin_dict['enrichment_data']:
                    coin_dict['enrichment_data'] = json.loads(coin_dict['enrichment_data'])
                coins.append(coin_dict)
            
            return coins
            
        except Exception as e:
            print(f"Error fetching recent coins: {e}")
            return []
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get stats for last 24 hours
            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
            
            # Total processed today
            cursor.execute("""
                SELECT COUNT(*) FROM incoming_coins 
                WHERE detected_time > ?
            """, (cutoff_time,))
            total_today = cursor.fetchone()[0]
            
            # By status
            cursor.execute("""
                SELECT processing_status, COUNT(*) FROM incoming_coins 
                WHERE detected_time > ?
                GROUP BY processing_status
            """, (cutoff_time,))
            status_counts = dict(cursor.fetchall())
            
            # By signal type
            cursor.execute("""
                SELECT signal_type, COUNT(*) FROM incoming_coins 
                WHERE detected_time > ?
                GROUP BY signal_type
            """, (cutoff_time,))
            signal_counts = dict(cursor.fetchall())
            
            # Average confidence
            cursor.execute("""
                SELECT AVG(confidence) FROM incoming_coins 
                WHERE detected_time > ?
            """, (cutoff_time,))
            avg_confidence = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_today': total_today,
                'status_counts': status_counts,
                'signal_counts': signal_counts,
                'average_confidence': avg_confidence,
                'queue_size': len(self.processing_queue)
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_today': 0,
                'status_counts': {},
                'signal_counts': {},
                'average_confidence': 0,
                'queue_size': 0
            }

# Singleton instance
incoming_coins_processor = IncomingCoinsProcessor()

# Simulate Telegram monitoring (for demo)
async def simulate_telegram_activity():
    """Simulate incoming Telegram messages for demo purposes"""
    sample_messages = [
        ("🚀 NEW GEM ALERT: $ROCKET just launched! Buy now before moon! Contract: 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM", "Alpha Gems"),
        ("$MOON breaking out! Strong buy signal detected 📈", "Crypto Signals Pro"),
        ("Watch $STAR - potential 100x gem 💎", "Hidden Gems"),
        ("$FIRE token partnership announced! Official news! 🔥", "Official Announcements"),
        ("New token $WAVE launched on Solana. Early entry opportunity!", "Solana Gems")
    ]
    
    for message, channel in sample_messages:
        await incoming_coins_processor.process_telegram_message(message, channel)
        await asyncio.sleep(2)  # Simulate time between messages

if __name__ == "__main__":
    # Run simulation
    asyncio.run(simulate_telegram_activity())