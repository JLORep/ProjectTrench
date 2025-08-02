#!/usr/bin/env python3
"""
Blog Duplicate Prevention System
Prevents duplicate posts from being sent to Discord
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta

class DuplicatePreventionSystem:
    def __init__(self, db_path="comprehensive_dev_blog.db"):
        self.db_path = db_path
        self.init_duplicate_tracking()
    
    def init_duplicate_tracking(self):
        """Initialize duplicate tracking table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for tracking sent messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discord_sent_messages (
                message_hash TEXT PRIMARY KEY,
                post_id TEXT,
                title TEXT,
                channel TEXT,
                sent_timestamp TIMESTAMP,
                discord_message_id TEXT,
                UNIQUE(post_id, channel)
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sent_timestamp 
            ON discord_sent_messages(sent_timestamp)
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Duplicate tracking system initialized")
    
    def generate_message_hash(self, title, content, post_type):
        """Generate unique hash for a message"""
        # Create hash from title + content + type to identify duplicates
        hash_input = f"{title}:{content[:500]}:{post_type}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()
    
    def is_duplicate(self, title, content, post_type, channel="discord"):
        """Check if message is a duplicate"""
        message_hash = self.generate_message_hash(title, content, post_type)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if this exact message was already sent
        cursor.execute('''
            SELECT sent_timestamp FROM discord_sent_messages 
            WHERE message_hash = ? AND channel = ?
        ''', (message_hash, channel))
        
        result = cursor.fetchone()
        
        # Also check if same title was sent in last hour (prevent spam)
        cursor.execute('''
            SELECT COUNT(*) FROM discord_sent_messages 
            WHERE title = ? 
            AND channel = ? 
            AND sent_timestamp > datetime('now', '-1 hour')
        ''', (title, channel))
        
        recent_count = cursor.fetchone()[0]
        
        conn.close()
        
        if result:
            print(f"⚠️  Duplicate detected: {title} (already sent at {result[0]})")
            return True
        
        if recent_count > 0:
            print(f"⚠️  Similar message sent recently: {title} (within last hour)")
            return True
        
        return False
    
    def mark_as_sent(self, post_id, title, content, post_type, channel="discord", discord_message_id=None):
        """Mark a message as sent to prevent duplicates"""
        message_hash = self.generate_message_hash(title, content, post_type)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO discord_sent_messages 
                (message_hash, post_id, title, channel, sent_timestamp, discord_message_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                message_hash,
                post_id,
                title,
                channel,
                datetime.now().isoformat(),
                discord_message_id
            ))
            
            conn.commit()
            print(f"✅ Marked as sent: {title}")
            
        except Exception as e:
            print(f"❌ Error marking as sent: {e}")
        
        conn.close()
    
    def clean_old_records(self, days=30):
        """Clean old duplicate tracking records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            DELETE FROM discord_sent_messages 
            WHERE sent_timestamp < ?
        ''', (cutoff,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"🧹 Cleaned {deleted} old tracking records")
        return deleted
    
    def get_sent_stats(self, hours=24):
        """Get statistics on sent messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        # Total sent
        cursor.execute('''
            SELECT COUNT(*) FROM discord_sent_messages 
            WHERE sent_timestamp > ?
        ''', (cutoff,))
        total_sent = cursor.fetchone()[0]
        
        # By channel
        cursor.execute('''
            SELECT channel, COUNT(*) FROM discord_sent_messages 
            WHERE sent_timestamp > ?
            GROUP BY channel
        ''', (cutoff,))
        by_channel = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_sent': total_sent,
            'by_channel': dict(by_channel),
            'period_hours': hours
        }

def integrate_with_blog_system():
    """Integration code for the blog system"""
    integration_code = '''
# Add this to comprehensive_dev_blog_system.py in the publish method:

from blog_duplicate_prevention import DuplicatePreventionSystem

# Initialize duplicate prevention
if not hasattr(self, 'duplicate_prevention'):
    self.duplicate_prevention = DuplicatePreventionSystem()

# Before sending to Discord, check for duplicates:
if self.duplicate_prevention.is_duplicate(title, content, post_type, channel):
    st.warning(f"⚠️ Skipping duplicate: {title}")
    return {"status": "skipped", "reason": "duplicate"}

# After successful send, mark as sent:
self.duplicate_prevention.mark_as_sent(
    post_id=post_id,
    title=title,
    content=content,
    post_type=post_type,
    channel=channel
)
'''
    
    print("\n📋 Integration Instructions:")
    print(integration_code)
    
    # Save integration patch
    with open("duplicate_prevention_patch.py", 'w') as f:
        f.write(integration_code)
    
    print("\n✅ Integration code saved to duplicate_prevention_patch.py")

def test_duplicate_prevention():
    """Test the duplicate prevention system"""
    print("\n🧪 Testing Duplicate Prevention System...")
    
    dp = DuplicatePreventionSystem()
    
    # Test data
    test_posts = [
        ("Test Post 1", "This is test content 1", "feature"),
        ("Test Post 1", "This is test content 1", "feature"),  # Duplicate
        ("Test Post 2", "This is test content 2", "bug_fix"),
        ("Test Post 1", "Different content", "feature"),  # Same title, different content
    ]
    
    for title, content, post_type in test_posts:
        if dp.is_duplicate(title, content, post_type):
            print(f"  ⚠️  Duplicate: {title}")
        else:
            print(f"  ✅ New post: {title}")
            dp.mark_as_sent(f"test_{title}", title, content, post_type)
    
    # Show stats
    stats = dp.get_sent_stats(1)  # Last hour
    print(f"\n📊 Stats: {stats}")
    
    # Clean test data
    dp.clean_old_records(0)  # Clean all

if __name__ == "__main__":
    # Initialize system
    dp = DuplicatePreventionSystem()
    
    # Show current stats
    stats = dp.get_sent_stats(24)
    print(f"\n📊 Current Stats (last 24h):")
    print(f"  • Total sent: {stats['total_sent']}")
    print(f"  • By channel: {stats['by_channel']}")
    
    # Test the system
    test_duplicate_prevention()
    
    # Show integration instructions
    integrate_with_blog_system()