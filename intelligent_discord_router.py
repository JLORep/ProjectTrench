#!/usr/bin/env python3
"""
Intelligent Discord Channel Router
Routes blog posts and updates to appropriate Discord channels based on content analysis
"""

import re
import json
import sqlite3
import requests
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

class IntelligentDiscordRouter:
    def __init__(self):
        self.webhook_base = "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"
        
        # Channel purposes and keywords for intelligent routing
        self.channel_config = {
            "dev-blog": {
                "purpose": "Development progress, feature development, and technical updates",
                "keywords": ["feature", "implement", "add", "create", "develop", "build", "code", 
                           "function", "method", "class", "module", "refactor", "optimize"],
                "priority": 2
            },
            "announcements": {
                "purpose": "Major releases, important updates, and official communications",
                "keywords": ["release", "launch", "announce", "major", "milestone", "complete",
                           "v1", "v2", "version", "production", "live"],
                "priority": 1
            },
            "documentation": {
                "purpose": "Documentation updates, guides, and tutorials",
                "keywords": ["docs", "documentation", "readme", "guide", "tutorial", "help",
                           "instructions", "usage", "api", "reference"],
                "priority": 3
            },
            "bug-reports": {
                "purpose": "Bug fixes and issue resolutions",
                "keywords": ["fix", "bug", "error", "issue", "crash", "failed", "broken",
                           "repair", "patch", "resolve", "solution"],
                "priority": 1
            },
            "system-updates": {
                "purpose": "System maintenance and infrastructure changes",
                "keywords": ["update", "upgrade", "maintain", "infrastructure", "system",
                           "dependency", "library", "package", "config", "setup"],
                "priority": 2
            },
            "testing": {
                "purpose": "Test results and quality assurance",
                "keywords": ["test", "testing", "qa", "quality", "validation", "verify",
                           "check", "assert", "spec", "unit", "integration"],
                "priority": 3
            },
            "deployments": {
                "purpose": "Deployment notifications and status",
                "keywords": ["deploy", "deployment", "push", "release", "production",
                           "staging", "rollout", "publish", "ship"],
                "priority": 1
            },
            "signals": {
                "purpose": "Trading signals and opportunities",
                "keywords": ["signal", "trade", "buy", "sell", "alert", "opportunity",
                           "coin", "token", "pump", "dump", "volume", "price"],
                "priority": 1
            },
            "analytics": {
                "purpose": "Market analysis and insights",
                "keywords": ["analysis", "analyze", "analytics", "insight", "report",
                           "metric", "data", "trend", "pattern", "statistics"],
                "priority": 2
            },
            "performance": {
                "purpose": "Performance metrics and optimization",
                "keywords": ["performance", "speed", "optimize", "efficiency", "benchmark",
                           "profile", "memory", "cpu", "latency", "throughput"],
                "priority": 3
            }
        }
        
        # Initialize duplicate prevention
        self.init_duplicate_tracking()
        
    def init_duplicate_tracking(self):
        """Initialize tracking for sent messages to prevent duplicates"""
        conn = sqlite3.connect('comprehensive_dev_blog.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discord_channel_messages (
                message_id TEXT PRIMARY KEY,
                channel TEXT NOT NULL,
                title TEXT,
                content_hash TEXT,
                sent_timestamp TIMESTAMP,
                commit_sha TEXT,
                UNIQUE(channel, content_hash)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_content(self, title: str, content: str, post_type: str = None) -> List[str]:
        """
        Analyze content to determine appropriate channels
        Returns list of channel names ordered by relevance
        """
        # Combine title and content for analysis
        full_text = f"{title} {content}".lower()
        
        # Score each channel based on keyword matches
        channel_scores = {}
        
        for channel, config in self.channel_config.items():
            score = 0
            keyword_matches = 0
            
            # Check for keyword matches
            for keyword in config['keywords']:
                if keyword in full_text:
                    # Weight title matches higher
                    if keyword in title.lower():
                        score += 3
                    else:
                        score += 1
                    keyword_matches += 1
            
            # Bonus for multiple keyword matches
            if keyword_matches > 2:
                score += 2
            
            # Consider post type if provided
            if post_type:
                if post_type == 'bug_fix' and channel == 'bug-reports':
                    score += 5
                elif post_type == 'feature' and channel == 'dev-blog':
                    score += 5
                elif post_type == 'deployment' and channel == 'deployments':
                    score += 5
                elif post_type == 'documentation' and channel == 'documentation':
                    score += 5
            
            # Apply priority weighting
            score = score * (4 - config['priority'])
            
            if score > 0:
                channel_scores[channel] = score
        
        # Sort channels by score
        sorted_channels = sorted(channel_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top channels (max 3)
        selected_channels = [ch[0] for ch in sorted_channels[:3]]
        
        # Default to dev-blog if no matches
        if not selected_channels:
            selected_channels = ['dev-blog']
        
        return selected_channels
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict]:
        """Get recent git commits for context"""
        try:
            import subprocess
            
            # Get recent commits with full message
            result = subprocess.run([
                'git', 'log', '--oneline', f'-{limit}', '--format=%H|%s|%b'
            ], capture_output=True, text=True, encoding='utf-8')
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|', 2)
                    if len(parts) >= 2:
                        commits.append({
                            'sha': parts[0][:7],
                            'title': parts[1],
                            'body': parts[2] if len(parts) > 2 else ''
                        })
            
            return commits
        except Exception as e:
            print(f"Error getting commits: {e}")
            return []
    
    def generate_commit_based_update(self, commit: Dict) -> Dict:
        """Generate a blog update based on a git commit"""
        title = commit['title']
        
        # Analyze commit message for type
        post_type = 'update'
        if any(word in title.lower() for word in ['fix', 'bug', 'error']):
            post_type = 'bug_fix'
        elif any(word in title.lower() for word in ['feature', 'add', 'implement']):
            post_type = 'feature'
        elif any(word in title.lower() for word in ['deploy', 'release']):
            post_type = 'deployment'
        elif any(word in title.lower() for word in ['docs', 'readme']):
            post_type = 'documentation'
        
        # Create content
        content = f"Commit {commit['sha']}: {title}"
        if commit.get('body'):
            content += f"\n\n{commit['body']}"
        
        return {
            'title': title,
            'content': content,
            'post_type': post_type,
            'commit_sha': commit['sha']
        }
    
    def route_to_channels(self, title: str, content: str, post_type: str = None, 
                         commit_sha: str = None, force_channels: List[str] = None):
        """
        Route a message to appropriate Discord channels
        """
        # Determine channels
        if force_channels:
            channels = force_channels
        else:
            channels = self.analyze_content(title, content, post_type)
        
        print(f"\n📡 Routing '{title}' to channels: {', '.join(channels)}")
        
        # Check for duplicates and send to each channel
        results = {}
        
        for channel in channels:
            # Generate unique message ID
            import hashlib
            message_id = hashlib.sha256(f"{channel}:{title}:{content[:100]}".encode()).hexdigest()[:16]
            
            # Check if already sent
            if self.is_duplicate(message_id, channel):
                print(f"  ⏭️  Skipping {channel} (already sent)")
                results[channel] = {"status": "skipped", "reason": "duplicate"}
                continue
            
            # Send message
            result = self.send_to_channel(channel, title, content, post_type)
            results[channel] = result
            
            if result['status'] == 'success':
                # Mark as sent
                self.mark_as_sent(message_id, channel, title, commit_sha)
            
            # Rate limit protection
            time.sleep(2)
        
        return results
    
    def send_to_channel(self, channel: str, title: str, content: str, 
                       post_type: str = None) -> Dict:
        """Send a message to a specific Discord channel"""
        
        # Determine embed color based on type/channel
        color_map = {
            'bug_fix': 0xFF6B6B,        # Red
            'feature': 0x4ECDC4,        # Teal
            'deployment': 0x45B7D1,     # Blue
            'documentation': 0xF7DC6F,   # Yellow
            'signals': 0x52C41A,        # Green
            'performance': 0x9B59B6,    # Purple
            'update': 0x95A5A6          # Gray
        }
        
        color = color_map.get(post_type, 0x10b981)  # Default TrenchCoat green
        
        # Create message
        message = {
            "embeds": [{
                "title": f"📌 {title}",
                "description": content[:2000],  # Discord limit
                "color": color,
                "fields": [
                    {"name": "Channel", "value": f"#{channel}", "inline": True},
                    {"name": "Type", "value": (post_type or 'update').replace('_', ' ').title(), "inline": True}
                ],
                "footer": {
                    "text": f"TrenchCoat Pro • Intelligent Routing • #{channel}"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        }
        
        try:
            # For now, all webhooks go to same URL (would be different per channel in production)
            response = requests.post(self.webhook_base, json=message)
            
            if response.status_code == 204:
                print(f"  ✅ Sent to #{channel}")
                return {"status": "success", "channel": channel}
            else:
                print(f"  ❌ Failed to send to #{channel}: {response.status_code}")
                return {"status": "failed", "channel": channel, "error": response.status_code}
                
        except Exception as e:
            print(f"  ❌ Error sending to #{channel}: {e}")
            return {"status": "error", "channel": channel, "error": str(e)}
    
    def is_duplicate(self, message_id: str, channel: str) -> bool:
        """Check if message was already sent to channel"""
        conn = sqlite3.connect('comprehensive_dev_blog.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sent_timestamp FROM discord_channel_messages 
            WHERE message_id = ? AND channel = ?
        ''', (message_id, channel))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def mark_as_sent(self, message_id: str, channel: str, title: str, commit_sha: str = None):
        """Mark message as sent to prevent duplicates"""
        conn = sqlite3.connect('comprehensive_dev_blog.db')
        cursor = conn.cursor()
        
        import hashlib
        content_hash = hashlib.sha256(f"{title}:{channel}".encode()).hexdigest()[:32]
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO discord_channel_messages 
                (message_id, channel, title, content_hash, sent_timestamp, commit_sha)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                message_id,
                channel,
                title,
                content_hash,
                datetime.now().isoformat(),
                commit_sha
            ))
            
            conn.commit()
        except Exception as e:
            print(f"Error marking as sent: {e}")
        
        conn.close()
    
    def route_recent_commits(self, limit: int = 5):
        """Analyze recent commits and route to appropriate channels"""
        print("\n🔍 Analyzing recent commits for intelligent routing...")
        
        commits = self.get_recent_commits(limit)
        
        for commit in commits:
            print(f"\n📝 Processing commit: {commit['sha']} - {commit['title']}")
            
            # Generate update from commit
            update = self.generate_commit_based_update(commit)
            
            # Route to appropriate channels
            self.route_to_channels(
                title=update['title'],
                content=update['content'],
                post_type=update['post_type'],
                commit_sha=update['commit_sha']
            )
    
    def get_routing_stats(self) -> Dict:
        """Get statistics on channel routing"""
        conn = sqlite3.connect('comprehensive_dev_blog.db')
        cursor = conn.cursor()
        
        # Messages per channel
        cursor.execute('''
            SELECT channel, COUNT(*) as count 
            FROM discord_channel_messages 
            GROUP BY channel
            ORDER BY count DESC
        ''')
        
        channel_stats = dict(cursor.fetchall())
        
        # Recent activity
        cursor.execute('''
            SELECT COUNT(*) FROM discord_channel_messages 
            WHERE sent_timestamp > datetime('now', '-24 hours')
        ''')
        
        recent_24h = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'by_channel': channel_stats,
            'recent_24h': recent_24h,
            'total': sum(channel_stats.values())
        }

def demonstrate_intelligent_routing():
    """Demonstrate the intelligent routing system"""
    router = IntelligentDiscordRouter()
    
    print("🤖 Intelligent Discord Router Demonstration")
    print("=" * 50)
    
    # Test examples
    test_cases = [
        {
            'title': 'Fixed critical Unicode encoding error in git hooks',
            'content': 'Resolved UnicodeDecodeError by adding UTF-8 encoding to all subprocess calls',
            'post_type': 'bug_fix'
        },
        {
            'title': 'Implemented Discord rate limit queue system',
            'content': 'Added comprehensive queue management with priority handling and retry logic',
            'post_type': 'feature'
        },
        {
            'title': 'Updated project documentation with API reference',
            'content': 'Added complete API documentation and usage examples to README',
            'post_type': 'documentation'
        },
        {
            'title': 'Deployed v2.1.0 to production',
            'content': 'Successfully deployed latest version with all features enabled',
            'post_type': 'deployment'
        },
        {
            'title': 'Performance optimization: Reduced dashboard load time by 60%',
            'content': 'Implemented caching and lazy loading for improved performance',
            'post_type': 'update'
        }
    ]
    
    print("\n📋 Test Cases:")
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['title']}")
        channels = router.analyze_content(test['title'], test['content'], test['post_type'])
        print(f"   → Routes to: {', '.join(f'#{ch}' for ch in channels)}")
    
    # Show stats
    stats = router.get_routing_stats()
    print(f"\n📊 Routing Statistics:")
    print(f"   • Total messages routed: {stats['total']}")
    print(f"   • Last 24 hours: {stats['recent_24h']}")
    print(f"   • By channel: {stats['by_channel']}")

if __name__ == "__main__":
    # Run demonstration
    demonstrate_intelligent_routing()
    
    # Option to route recent commits
    if input("\n🚀 Route recent commits to Discord? (y/n): ").lower() == 'y':
        router = IntelligentDiscordRouter()
        router.route_recent_commits(limit=5)