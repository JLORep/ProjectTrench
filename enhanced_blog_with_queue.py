#!/usr/bin/env python3
"""
TrenchCoat Pro - Enhanced Dev Blog System with Discord Rate Limit Queue
Implements intelligent queuing for Discord webhooks with rate limit handling
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import sqlite3
from enum import Enum
import threading
import functools

def run_async_safe(coro):
    """Safely run async code in potentially existing event loop"""
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        # If we're in an existing loop, create a new thread
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return asyncio.run(coro)
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(coro)

class MessagePriority(Enum):
    """Priority levels for queued messages"""
    CRITICAL = 1  # System alerts, critical updates
    HIGH = 2      # Feature releases, important updates
    NORMAL = 3    # Regular blog posts
    LOW = 4       # Documentation, minor updates

@dataclass
class QueuedMessage:
    """Represents a message in the Discord queue"""
    channel: str
    webhook_url: str
    embed: Dict[str, Any]
    priority: MessagePriority
    created_at: datetime
    retry_count: int = 0
    max_retries: int = 3
    post_id: Optional[str] = None

class DiscordRateLimitQueue:
    """
    Manages Discord webhook rate limits with intelligent queuing
    Inspired by comprehensive API integration patterns
    """
    
    def __init__(self):
        # Discord rate limits: 30 requests per channel per 60 seconds
        self.rate_limit_per_channel = 30
        self.rate_limit_window = 60  # seconds
        
        # Track requests per channel
        self.channel_requests: Dict[str, List[datetime]] = {}
        
        # Priority queue for each channel
        self.message_queues: Dict[str, deque] = {}
        
        # Failed message storage
        self.failed_messages: List[QueuedMessage] = []
        
        # Queue processing state
        self.processing = False
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Callback for notifications
        self.notification_webhook = None
        
    async def initialize(self):
        """Initialize the async session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    def add_to_queue(self, message: QueuedMessage):
        """Add a message to the appropriate channel queue"""
        channel = message.channel
        
        if channel not in self.message_queues:
            self.message_queues[channel] = deque()
        
        # Insert based on priority
        queue = self.message_queues[channel]
        
        # Find insertion point based on priority
        inserted = False
        for i, existing_msg in enumerate(queue):
            if message.priority.value < existing_msg.priority.value:
                queue.insert(i, message)
                inserted = True
                break
        
        if not inserted:
            queue.append(message)
        
        print(f"📥 Added message to {channel} queue (Priority: {message.priority.name}, Queue size: {len(queue)})")
    
    def can_send_to_channel(self, channel: str) -> Tuple[bool, Optional[float]]:
        """
        Check if we can send to a channel without hitting rate limits
        Returns (can_send, wait_time_seconds)
        """
        now = datetime.now()
        
        if channel not in self.channel_requests:
            self.channel_requests[channel] = []
            return True, None
        
        # Clean old requests outside the window
        cutoff_time = now - timedelta(seconds=self.rate_limit_window)
        self.channel_requests[channel] = [
            req_time for req_time in self.channel_requests[channel]
            if req_time > cutoff_time
        ]
        
        # Check if under limit
        if len(self.channel_requests[channel]) < self.rate_limit_per_channel:
            return True, None
        
        # Calculate wait time
        oldest_request = min(self.channel_requests[channel])
        wait_time = (oldest_request + timedelta(seconds=self.rate_limit_window) - now).total_seconds()
        
        return False, max(0, wait_time)
    
    async def send_webhook(self, message: QueuedMessage) -> bool:
        """Send a single webhook message"""
        if not self.session:
            await self.initialize()
        
        try:
            async with self.session.post(
                message.webhook_url,
                json={"embeds": [message.embed]},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 204:
                    # Success
                    self.channel_requests[message.channel].append(datetime.now())
                    return True
                
                elif response.status == 429:
                    # Rate limited
                    retry_after = response.headers.get('X-RateLimit-Reset-After', '60')
                    print(f"⚠️ Rate limited on {message.channel}. Retry after: {retry_after}s")
                    
                    # Re-queue with higher priority
                    message.retry_count += 1
                    if message.retry_count < message.max_retries:
                        self.add_to_queue(message)
                    else:
                        self.failed_messages.append(message)
                    
                    # Send notification about rate limit
                    await self.notify_rate_limit(message.channel, float(retry_after))
                    return False
                
                else:
                    # Other error
                    print(f"❌ Error sending to {message.channel}: {response.status}")
                    message.retry_count += 1
                    
                    if message.retry_count < message.max_retries:
                        self.add_to_queue(message)
                    else:
                        self.failed_messages.append(message)
                    
                    return False
                    
        except Exception as e:
            print(f"❌ Exception sending webhook: {str(e)}")
            message.retry_count += 1
            
            if message.retry_count < message.max_retries:
                self.add_to_queue(message)
            else:
                self.failed_messages.append(message)
            
            return False
    
    async def process_queues(self):
        """Process all channel queues respecting rate limits"""
        self.processing = True
        
        while self.processing:
            processed_any = False
            
            # Process each channel's queue
            for channel, queue in self.message_queues.items():
                if not queue:
                    continue
                
                # Check rate limit
                can_send, wait_time = self.can_send_to_channel(channel)
                
                if can_send:
                    # Send next message
                    message = queue.popleft()
                    success = await self.send_webhook(message)
                    
                    if success:
                        print(f"✅ Sent message to {channel} (Remaining in queue: {len(queue)})")
                        processed_any = True
                    
                    # Small delay between sends
                    await asyncio.sleep(0.5)
                
                elif wait_time and wait_time < 60:
                    # If wait time is reasonable, notify
                    await self.notify_queue_status(channel, len(queue), wait_time)
            
            # If nothing was processed, wait a bit
            if not processed_any:
                await asyncio.sleep(5)
    
    async def notify_rate_limit(self, channel: str, retry_after: float):
        """Send notification about rate limit hit"""
        if not self.notification_webhook:
            return
        
        notification = {
            "content": f"⚠️ **Rate Limit Alert**",
            "embeds": [{
                "title": "Discord Rate Limit Reached",
                "description": f"Channel `{channel}` has hit the rate limit.",
                "color": 0xFF9800,  # Orange
                "fields": [
                    {
                        "name": "Channel",
                        "value": f"#{channel}",
                        "inline": True
                    },
                    {
                        "name": "Retry After",
                        "value": f"{retry_after:.0f} seconds",
                        "inline": True
                    },
                    {
                        "name": "Queue Status",
                        "value": f"{len(self.message_queues.get(channel, []))} messages waiting",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Messages will be automatically retried"
                },
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
        
        try:
            if self.session:
                await self.session.post(self.notification_webhook, json=notification)
        except:
            pass  # Don't fail on notification errors
    
    async def notify_queue_status(self, channel: str, queue_size: int, wait_time: float):
        """Send periodic queue status update"""
        if not self.notification_webhook or queue_size < 5:
            return
        
        notification = {
            "embeds": [{
                "title": "📊 Queue Status Update",
                "description": f"Channel `{channel}` has messages queued",
                "color": 0x2196F3,  # Blue
                "fields": [
                    {
                        "name": "Messages Queued",
                        "value": str(queue_size),
                        "inline": True
                    },
                    {
                        "name": "Est. Wait Time",
                        "value": f"{wait_time:.0f}s",
                        "inline": True
                    },
                    {
                        "name": "Status",
                        "value": "Processing...",
                        "inline": True
                    }
                ],
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
        
        try:
            if self.session:
                await self.session.post(self.notification_webhook, json=notification)
        except:
            pass
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get current queue statistics"""
        stats = {
            "total_queued": sum(len(q) for q in self.message_queues.values()),
            "channels": {},
            "failed_count": len(self.failed_messages),
            "rate_limit_status": {}
        }
        
        for channel, queue in self.message_queues.items():
            stats["channels"][channel] = {
                "queued": len(queue),
                "priorities": {}
            }
            
            # Count by priority
            for msg in queue:
                priority = msg.priority.name
                stats["channels"][channel]["priorities"][priority] = \
                    stats["channels"][channel]["priorities"].get(priority, 0) + 1
            
            # Rate limit status
            can_send, wait_time = self.can_send_to_channel(channel)
            stats["rate_limit_status"][channel] = {
                "can_send": can_send,
                "wait_time": wait_time
            }
        
        return stats

class EnhancedComprehensiveDevBlogSystem:
    """
    Enhanced blog system with Discord rate limit queue management
    """
    
    def __init__(self):
        # Initialize queue system
        self.discord_queue = DiscordRateLimitQueue()
        
        # Database for queue persistence
        self.db_path = "enhanced_blog_queue.db"
        self.init_queue_database()
        
        # Track async tasks
        self.queue_processor_task = None
        
        # Webhook mapping (simplified for example)
        self.webhooks = {
            'dev-blog': 'https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE',
            'announcements': 'https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE',
            'system-updates': 'https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE'
        }
    
    def init_queue_database(self):
        """Initialize database for queue persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS queued_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT,
            channel TEXT NOT NULL,
            webhook_url TEXT NOT NULL,
            embed_json TEXT NOT NULL,
            priority INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            retry_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'queued'
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rate_limit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT NOT NULL,
            event_type TEXT NOT NULL,
            retry_after REAL,
            queue_size INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    async def start_queue_processor(self):
        """Start the background queue processor"""
        await self.discord_queue.initialize()
        
        # Set notification webhook for rate limit alerts
        self.discord_queue.notification_webhook = self.webhooks.get('system-updates')
        
        # Load any persisted messages
        self.load_persisted_messages()
        
        # Start processing
        self.queue_processor_task = asyncio.create_task(self.discord_queue.process_queues())
        print("🚀 Queue processor started")
    
    async def stop_queue_processor(self):
        """Stop the queue processor"""
        if self.queue_processor_task:
            self.discord_queue.processing = False
            await self.queue_processor_task
            await self.discord_queue.cleanup()
            print("🛑 Queue processor stopped")
    
    def load_persisted_messages(self):
        """Load any queued messages from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT post_id, channel, webhook_url, embed_json, priority, retry_count
        FROM queued_messages
        WHERE status = 'queued'
        ORDER BY priority, created_at
        ''')
        
        for row in cursor.fetchall():
            message = QueuedMessage(
                channel=row[1],
                webhook_url=row[2],
                embed=json.loads(row[3]),
                priority=MessagePriority(row[4]),
                created_at=datetime.now(),
                retry_count=row[5],
                post_id=row[0]
            )
            self.discord_queue.add_to_queue(message)
        
        conn.close()
    
    def create_blog_embed(self, title: str, content: str, category: str, 
                         priority: str = "normal") -> Dict[str, Any]:
        """Create a Discord embed for blog post"""
        
        # Color coding by category
        colors = {
            'feature': 0x00FF00,      # Green
            'bugfix': 0xFF9800,       # Orange
            'critical': 0xFF0000,     # Red
            'performance': 0x2196F3,  # Blue
            'security': 0x9C27B0,     # Purple
            'documentation': 0x607D8B # Blue Grey
        }
        
        embed = {
            "title": title,
            "description": content[:2000],  # Discord limit
            "color": colors.get(category, 0x000000),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": f"TrenchCoat Pro • {category.title()} Update"
            }
        }
        
        return embed
    
    async def publish_with_queue(self, title: str, content: str, category: str,
                                channels: List[str], priority: str = "normal"):
        """Publish blog post to Discord with queue management"""
        
        # Create embed
        embed = self.create_blog_embed(title, content, category, priority)
        
        # Map priority
        priority_map = {
            'critical': MessagePriority.CRITICAL,
            'high': MessagePriority.HIGH,
            'normal': MessagePriority.NORMAL,
            'low': MessagePriority.LOW
        }
        msg_priority = priority_map.get(priority, MessagePriority.NORMAL)
        
        # Queue for each channel
        for channel in channels:
            if channel not in self.webhooks:
                print(f"⚠️ No webhook configured for channel: {channel}")
                continue
            
            message = QueuedMessage(
                channel=channel,
                webhook_url=self.webhooks[channel],
                embed=embed,
                priority=msg_priority,
                created_at=datetime.now()
            )
            
            # Add to queue
            self.discord_queue.add_to_queue(message)
            
            # Persist to database
            self.persist_message(message)
        
        print(f"📬 Queued '{title}' for {len(channels)} channels")
    
    def persist_message(self, message: QueuedMessage):
        """Save message to database for recovery"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO queued_messages 
        (post_id, channel, webhook_url, embed_json, priority, retry_count)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            message.post_id,
            message.channel,
            message.webhook_url,
            json.dumps(message.embed),
            message.priority.value,
            message.retry_count
        ))
        
        conn.commit()
        conn.close()
    
    def get_queue_dashboard(self) -> str:
        """Get a formatted dashboard of queue status"""
        stats = self.discord_queue.get_queue_stats()
        
        dashboard = f"""
📊 **Discord Queue Dashboard**
═══════════════════════════════════════

**Overall Status:**
• Total Queued: {stats['total_queued']}
• Failed Messages: {stats['failed_count']}

**Channel Status:**
"""
        
        for channel, channel_stats in stats['channels'].items():
            rate_status = stats['rate_limit_status'].get(channel, {})
            
            status_icon = "🟢" if rate_status.get('can_send', True) else "🔴"
            wait_time = rate_status.get('wait_time', 0)
            
            dashboard += f"""
{status_icon} **#{channel}**
  • Queued: {channel_stats['queued']}
  • Priorities: {', '.join(f"{p}: {c}" for p, c in channel_stats['priorities'].items())}
  • Rate Limit: {"OK" if rate_status.get('can_send', True) else f"Wait {wait_time:.0f}s"}
"""
        
        return dashboard

# Example usage with async context
async def example_usage():
    """Example of using the enhanced blog system"""
    
    system = EnhancedComprehensiveDevBlogSystem()
    
    # Start queue processor
    await system.start_queue_processor()
    
    # Simulate publishing multiple updates
    updates = [
        {
            "title": "🚀 New Feature: Hunt Hub Launch",
            "content": "We're excited to announce the launch of Hunt Hub...",
            "category": "feature",
            "channels": ["announcements", "dev-blog"],
            "priority": "high"
        },
        {
            "title": "🐛 Critical Bug Fix",
            "content": "Fixed critical issue affecting trading engine...",
            "category": "bugfix",
            "channels": ["system-updates", "dev-blog"],
            "priority": "critical"
        },
        {
            "title": "📚 Documentation Update",
            "content": "Updated API documentation with new endpoints...",
            "category": "documentation",
            "channels": ["dev-blog"],
            "priority": "low"
        }
    ]
    
    # Queue all updates
    for update in updates:
        await system.publish_with_queue(**update)
    
    # Show dashboard
    print(system.get_queue_dashboard())
    
    # Let it process for a bit
    await asyncio.sleep(30)
    
    # Stop processor
    await system.stop_queue_processor()

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())