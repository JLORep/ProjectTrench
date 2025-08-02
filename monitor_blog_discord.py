#!/usr/bin/env python3
"""
Monitor blog to Discord integration
"""
import sqlite3
import time
from datetime import datetime, timedelta

def monitor_blog_discord_integration():
    """Monitor and report on blog → Discord integration"""
    print("📊 Blog → Discord Integration Monitor")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('comprehensive_dev_blog.db')
        cursor = conn.cursor()
        
        # Get stats for last 24 hours
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        
        # Total posts
        cursor.execute("""
            SELECT COUNT(*) FROM comprehensive_posts
            WHERE created_timestamp > ?
        """, (cutoff,))
        total_posts = cursor.fetchone()[0]
        
        # Posts sent to Discord
        cursor.execute("""
            SELECT COUNT(*) FROM comprehensive_posts
            WHERE created_timestamp > ? AND channels_posted LIKE '%discord%'
        """, (cutoff,))
        discord_posts = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute("""
            SELECT AVG(discord_success_rate) FROM comprehensive_posts
            WHERE created_timestamp > ? AND channels_posted LIKE '%discord%'
        """, (cutoff,))
        success_rate = cursor.fetchone()[0] or 0
        
        print(f"📈 Last 24 Hours:")
        print(f"  • Total blog posts: {total_posts}")
        print(f"  • Posts sent to Discord: {discord_posts}")
        print(f"  • Discord success rate: {success_rate:.1%}")
        print(f"  • Auto-integration rate: {discord_posts/total_posts:.1%}" if total_posts > 0 else "  • Auto-integration rate: N/A")
        
        # Recent posts
        cursor.execute("""
            SELECT title, created_timestamp, channels_posted
            FROM comprehensive_posts
            WHERE created_timestamp > ?
            ORDER BY created_timestamp DESC
            LIMIT 5
        """, (cutoff,))
        
        print("\n📝 Recent Posts:")
        for title, timestamp, channels in cursor.fetchall():
            discord_status = "✅" if "discord" in channels else "❌"
            print(f"  {discord_status} {title[:50]}... ({timestamp[:16]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error monitoring integration: {e}")

if __name__ == "__main__":
    monitor_blog_discord_integration()
