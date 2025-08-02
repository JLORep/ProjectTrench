#!/usr/bin/env python3
"""
Send the 24-hour retrospective blog posts to Discord
"""

import sqlite3
import json
import requests
import time
from datetime import datetime, timezone, timedelta

webhook_url = "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"

def send_retrospective_posts():
    """Send the last 24 hours of blog posts to Discord"""
    print("📊 Fetching retrospective blog posts...")
    
    try:
        conn = sqlite3.connect('comprehensive_dev_blog.db')
        cursor = conn.cursor()
        
        # Get posts from last 24 hours
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        
        cursor.execute('''
            SELECT id, title, content_json, created_timestamp, post_type
            FROM comprehensive_posts
            WHERE created_timestamp > ?
            ORDER BY created_timestamp ASC
            LIMIT 12
        ''', (cutoff,))
        
        posts = cursor.fetchall()
        conn.close()
        
        print(f"Found {len(posts)} retrospective posts to send")
        
        # Send each post with rate limiting
        for i, (post_id, title, content_json, timestamp, post_type) in enumerate(posts, 1):
            print(f"\n[{i}/{len(posts)}] Sending: {title}")
            
            # Parse content
            try:
                content_data = json.loads(content_json)
                content = content_data.get('content', '')
            except:
                content = content_json
            
            # Determine color based on post type
            color_map = {
                'critical_fix': 0xFF0000,  # Red
                'bug_fix': 0xFFA500,       # Orange
                'feature': 0x00FF00,       # Green
                'major_feature': 0x00FF00, # Green
                'ui_update': 0x1E90FF,     # Blue
                'infrastructure': 0x9400D3, # Purple
                'system_upgrade': 0xFFD700, # Gold
                'deployment': 0x00CED1,     # Dark Turquoise
                'security': 0xFF1493,       # Deep Pink
                'summary': 0x10b981         # TrenchCoat Green
            }
            color = color_map.get(post_type, 0x808080)  # Default gray
            
            # Create Discord message
            message = {
                "embeds": [{
                    "title": title,
                    "description": content[:2000],  # Discord limit
                    "color": color,
                    "fields": [
                        {"name": "Type", "value": post_type.replace('_', ' ').title(), "inline": True},
                        {"name": "Time", "value": timestamp[:16], "inline": True}
                    ],
                    "footer": {
                        "text": "TrenchCoat Pro • 24hr Retrospective"
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }]
            }
            
            # Send message
            response = requests.post(webhook_url, json=message)
            
            if response.status_code == 204:
                print(f"  ✅ Sent successfully")
            else:
                print(f"  ❌ Failed: {response.status_code}")
            
            # Rate limit protection (Discord allows 30 requests per 60 seconds per channel)
            time.sleep(2.5)  # ~24 messages per minute to be safe
        
        # Send summary message
        print("\n📊 Sending summary message...")
        summary_message = {
            "content": "**📊 24-Hour Development Retrospective Complete!**",
            "embeds": [{
                "title": "🎉 Mega Development Progress Summary",
                "description": f"Successfully sent {len(posts)} development updates covering the last 24 hours of intense progress on TrenchCoat Pro.",
                "color": 0x10b981,
                "fields": [
                    {"name": "📝 Total Updates", "value": str(len(posts)), "inline": True},
                    {"name": "⏰ Time Period", "value": "Last 24 hours", "inline": True},
                    {"name": "🚀 Status", "value": "All Delivered", "inline": True}
                ],
                "footer": {
                    "text": "TrenchCoat Pro • Blog → Discord Integration"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        }
        
        response = requests.post(webhook_url, json=summary_message)
        if response.status_code == 204:
            print("✅ Summary sent successfully!")
        
        print("\n✨ All retrospective posts sent to Discord!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_retrospective_posts()