#!/usr/bin/env python3
"""
Telegram Monitor Service - Real-time monitoring of Telegram channels
Integrates with incoming_coins_monitor for automatic processing
"""
import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
from pathlib import Path
import threading
import schedule
import requests
from dataclasses import dataclass

# Safe imports
try:
    from incoming_coins_monitor import incoming_coins_processor
    processor_available = True
except ImportError:
    processor_available = False
    incoming_coins_processor = None

try:
    from unified_notifications import unified_notifier
    notifications_available = True
except ImportError:
    notifications_available = False
    unified_notifier = None

@dataclass
class TelegramChannel:
    """Represents a monitored Telegram channel"""
    name: str
    channel_id: str
    priority: str  # high, medium, low
    keywords: List[str]
    active: bool = True
    last_message_id: Optional[int] = None
    message_count: int = 0
    coins_detected: int = 0

class TelegramMonitorService:
    """Service for monitoring Telegram channels for new coin mentions"""
    
    def __init__(self, config_file: str = "telegram_monitor_config.json"):
        self.config_file = config_file
        self.channels = []
        self.monitoring_active = False
        self.stats = {
            'total_messages': 0,
            'coins_detected': 0,
            'processing_errors': 0,
            'last_activity': None,
            'uptime_start': datetime.now()
        }
        self.db_path = Path("data/telegram_monitor.db")
        self.load_config()
        self.init_database()
        
    def load_config(self):
        """Load monitoring configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                # Load channels from config
                for channel_data in config.get('channels', []):
                    channel = TelegramChannel(**channel_data)
                    self.channels.append(channel)
            else:
                # Create default config
                self.create_default_config()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            # Use default channels
            self.create_default_channels()
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "channels": [
                {
                    "name": "Alpha Gems",
                    "channel_id": "@alphagems",
                    "priority": "high",
                    "keywords": ["gem", "buy", "moon", "rocket", "100x"],
                    "active": True
                },
                {
                    "name": "Crypto Signals Pro",
                    "channel_id": "@cryptosignalspro",
                    "priority": "medium",
                    "keywords": ["signal", "buy", "entry", "target"],
                    "active": True
                },
                {
                    "name": "Hidden Gems",
                    "channel_id": "@hiddengems",
                    "priority": "medium",
                    "keywords": ["hidden", "gem", "early", "potential"],
                    "active": True
                },
                {
                    "name": "Official Announcements",
                    "channel_id": "@announcements",
                    "priority": "high",
                    "keywords": ["official", "announcement", "partnership", "listing"],
                    "active": True
                },
                {
                    "name": "Solana Gems",
                    "channel_id": "@solanagems",
                    "priority": "medium",
                    "keywords": ["solana", "sol", "gem", "defi"],
                    "active": True
                }
            ],
            "monitoring": {
                "poll_interval": 30,  # seconds
                "max_messages_per_poll": 10,
                "enable_notifications": True,
                "confidence_threshold": 0.7
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        # Load the created config
        self.load_config()
    
    def create_default_channels(self):
        """Create default channels if config loading fails"""
        self.channels = [
            TelegramChannel(
                name="Alpha Gems",
                channel_id="@alphagems",
                priority="high",
                keywords=["gem", "buy", "moon", "rocket", "100x"]
            ),
            TelegramChannel(
                name="Crypto Signals Pro", 
                channel_id="@cryptosignalspro",
                priority="medium",
                keywords=["signal", "buy", "entry", "target"]
            ),
            TelegramChannel(
                name="Hidden Gems",
                channel_id="@hiddengems", 
                priority="medium",
                keywords=["hidden", "gem", "early", "potential"]
            )
        ]
    
    def init_database(self):
        """Initialize monitoring database"""
        try:
            self.db_path.parent.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitored_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_name TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    message_id INTEGER,
                    message_text TEXT,
                    timestamp TEXT NOT NULL,
                    coins_detected INTEGER DEFAULT 0,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    channel_name TEXT NOT NULL,
                    messages_processed INTEGER DEFAULT 0,
                    coins_detected INTEGER DEFAULT 0,
                    processing_errors INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    async def start_monitoring(self):
        """Start the monitoring service"""
        if not processor_available:
            print("❌ Cannot start monitoring - processor not available")
            return
            
        self.monitoring_active = True
        self.stats['uptime_start'] = datetime.now()
        
        print("🚀 Starting Telegram monitoring service...")
        print(f"📡 Monitoring {len([c for c in self.channels if c.active])} channels")
        
        # Send startup notification
        if notifications_available and unified_notifier:
            await unified_notifier.send_discord_notification(
                message="🚀 **Telegram Monitor Started**\n\n" + 
                       f"📡 Monitoring {len(self.channels)} channels\n" +
                       "🤖 Auto-processing enabled\n" +
                       "🔔 Notifications active",
                title="Monitor Service",
                color=0x00ff00,
                channel_type="coin_data"
            )
        
        # Start monitoring loop
        while self.monitoring_active:
            try:
                await self.monitor_channels()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                self.stats['processing_errors'] += 1
                await asyncio.sleep(60)  # Wait longer on error
    
    async def monitor_channels(self):
        """Monitor all active channels for new messages"""
        for channel in self.channels:
            if not channel.active:
                continue
                
            try:
                # Simulate message fetching (in real implementation, use Telegram API)
                new_messages = await self.fetch_channel_messages(channel)
                
                for message in new_messages:
                    await self.process_channel_message(channel, message)
                    
            except Exception as e:
                print(f"❌ Error monitoring channel {channel.name}: {e}")
                self.stats['processing_errors'] += 1
    
    async def fetch_channel_messages(self, channel: TelegramChannel) -> List[Dict]:
        """Fetch new messages from a channel (simulated for demo)"""
        # In real implementation, this would use Telegram Bot API or telethon
        # For now, simulate with random messages
        
        import random
        
        # Simulate random message generation
        if random.random() < 0.1:  # 10% chance of new message
            sample_messages = [
                "🚀 NEW GEM ALERT: $ROCKET just launched! Contract: 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                "$MOON breaking out! Strong buy signal detected 📈", 
                "Watch $STAR - potential 100x gem 💎",
                "$FIRE token partnership announced! Official news! 🔥",
                "New token $WAVE launched on Solana. Early entry opportunity!",
                "🔥 $BLAZE hitting new ATH! Take profits at $0.05",
                "Hidden gem alert: $MYSTERY just got listed on Jupiter 🎯",
                "⚡ Quick play: $FLASH showing massive volume spike",
                "$DIAMOND holders rewarded with airdrop announcement 💎",
                "🚨 $ALERT: Major partnership announcement coming tomorrow"
            ]
            
            message_text = random.choice(sample_messages)
            return [{
                'message_id': random.randint(1000, 9999),
                'text': message_text,
                'timestamp': datetime.now(),
                'channel': channel.name
            }]
        
        return []
    
    async def process_channel_message(self, channel: TelegramChannel, message: Dict):
        """Process a message from a channel"""
        try:
            message_text = message['text']
            message_id = message['message_id']
            
            # Store message in database
            await self.store_message(channel, message)
            
            # Check if message contains relevant keywords
            if not self.message_has_keywords(message_text, channel.keywords):
                return
            
            # Process with incoming coins processor
            if processor_available and incoming_coins_processor:
                detected_coins = await incoming_coins_processor.process_telegram_message(
                    message_text, 
                    channel.name
                )
                
                if detected_coins:
                    print(f"🪙 Detected {len(detected_coins)} coins from {channel.name}")
                    channel.coins_detected += len(detected_coins)
                    self.stats['coins_detected'] += len(detected_coins)
                    
                    # Send detection notification
                    if notifications_available and unified_notifier:
                        await self.send_detection_notification(channel, detected_coins, message_text)
            
            # Update stats
            channel.message_count += 1
            channel.last_message_id = message_id
            self.stats['total_messages'] += 1
            self.stats['last_activity'] = datetime.now()
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            self.stats['processing_errors'] += 1
    
    def message_has_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if message contains relevant keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)
    
    async def store_message(self, channel: TelegramChannel, message: Dict):
        """Store message in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO monitored_messages 
                (channel_name, channel_id, message_id, message_text, timestamp, processed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                channel.name,
                channel.channel_id,
                message['message_id'],
                message['text'],
                message['timestamp'].isoformat(),
                False
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing message: {e}")
    
    async def send_detection_notification(self, channel: TelegramChannel, coins: List, message: str):
        """Send notification about coin detection"""
        if not notifications_available or not unified_notifier:
            return
            
        try:
            coin_list = ", ".join([f"${coin.ticker}" for coin in coins])
            
            notification_message = f"""🔔 **New Coins Detected!**

📡 **Channel:** {channel.name}
🪙 **Coins:** {coin_list}
⏰ **Time:** {datetime.now().strftime('%H:%M:%S')}

📝 **Message:** {message[:200]}{'...' if len(message) > 200 else ''}

🤖 **Status:** Processing automatically...
"""
            
            await unified_notifier.send_discord_notification(
                message=notification_message,
                title="Live Coin Detection",
                color=0x3b82f6,
                channel_type="coin_data"
            )
            
        except Exception as e:
            print(f"❌ Error sending notification: {e}")
    
    def stop_monitoring(self):
        """Stop the monitoring service"""
        self.monitoring_active = False
        print("🛑 Telegram monitoring service stopped")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get current monitoring statistics"""
        uptime = datetime.now() - self.stats['uptime_start']
        
        return {
            'monitoring_active': self.monitoring_active,
            'uptime_seconds': uptime.total_seconds(),
            'uptime_formatted': str(uptime).split('.')[0],
            'total_channels': len(self.channels),
            'active_channels': len([c for c in self.channels if c.active]),
            'total_messages': self.stats['total_messages'],
            'coins_detected': self.stats['coins_detected'],
            'processing_errors': self.stats['processing_errors'],
            'last_activity': self.stats['last_activity'],
            'channels': [
                {
                    'name': c.name,
                    'active': c.active,
                    'priority': c.priority,
                    'message_count': c.message_count,
                    'coins_detected': c.coins_detected,
                    'last_message_id': c.last_message_id
                }
                for c in self.channels
            ]
        }
    
    def get_recent_messages(self, hours: int = 24) -> List[Dict]:
        """Get recent monitored messages"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM monitored_messages 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
                LIMIT 50
            """, (cutoff_time,))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            
            messages = []
            for row in rows:
                message_dict = dict(zip(columns, row))
                messages.append(message_dict)
            
            return messages
            
        except Exception as e:
            print(f"Error fetching recent messages: {e}")
            return []

# Global service instance
telegram_monitor = TelegramMonitorService()

# Background monitoring thread
def run_monitoring_background():
    """Run monitoring in background thread"""
    asyncio.run(telegram_monitor.start_monitoring())

# Auto-start function for production
def start_monitoring_service():
    """Start monitoring service in background"""
    if not telegram_monitor.monitoring_active:
        monitoring_thread = threading.Thread(target=run_monitoring_background, daemon=True)
        monitoring_thread.start()
        print("🚀 Telegram monitoring started in background")
    else:
        print("📡 Monitoring already active")

if __name__ == "__main__":
    # Run monitoring service directly
    asyncio.run(telegram_monitor.start_monitoring())