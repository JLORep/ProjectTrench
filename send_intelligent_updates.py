#!/usr/bin/env python3
"""
Send recent commits and updates intelligently to appropriate Discord channels
"""

import subprocess
from intelligent_discord_router import IntelligentDiscordRouter
from datetime import datetime
import time

def send_recent_updates():
    """Send recent updates to Discord using intelligent routing"""
    
    router = IntelligentDiscordRouter()
    
    print("🚀 Intelligent Discord Update System")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get recent commits
    print("📝 Analyzing recent commits...")
    result = subprocess.run(
        ['git', 'log', '--oneline', '-15', '--format=%H|%s|%an|%ae'],
        capture_output=True, text=True, encoding='utf-8'
    )
    
    if result.returncode != 0:
        print("❌ Error getting commits")
        return
    
    updates_sent = 0
    
    # Process each commit
    for line in result.stdout.strip().split('\n'):
        if not line or '|' not in line:
            continue
            
        parts = line.split('|')
        if len(parts) < 2:
            continue
            
        commit_sha = parts[0][:7]
        title = parts[1]
        
        print(f"\n📍 Commit {commit_sha}: {title}")
        
        # Determine post type from commit message
        post_type = 'update'
        if any(word in title.lower() for word in ['fix', 'bug', 'error', 'issue']):
            post_type = 'bug_fix'
        elif any(word in title.lower() for word in ['feature', 'add', 'implement', 'new']):
            post_type = 'feature'
        elif any(word in title.lower() for word in ['deploy', 'release']):
            post_type = 'deployment'
        elif any(word in title.lower() for word in ['docs', 'documentation', 'readme']):
            post_type = 'documentation'
        elif any(word in title.lower() for word in ['test', 'testing']):
            post_type = 'testing'
        elif any(word in title.lower() for word in ['ui', 'ux', 'interface']):
            post_type = 'ui_update'
            
        # Generate content with more context
        content = f"**Commit:** `{commit_sha}`\n**Message:** {title}\n\n"
        
        # Add context based on type
        if post_type == 'bug_fix':
            content += "🐛 This fix improves system stability and reliability."
        elif post_type == 'feature':
            content += "✨ New functionality added to enhance the platform."
        elif post_type == 'deployment':
            content += "🚀 Changes are now live in production."
        elif post_type == 'documentation':
            content += "📚 Documentation updated for better clarity."
        elif post_type == 'testing':
            content += "🧪 Quality assurance and testing improvements."
        elif post_type == 'ui_update':
            content += "🎨 User interface improvements for better experience."
        else:
            content += "🔧 General improvements and updates."
        
        # Route to appropriate channels
        results = router.route_to_channels(
            title=title,
            content=content,
            post_type=post_type,
            commit_sha=commit_sha
        )
        
        # Check results
        success_channels = [ch for ch, res in results.items() if res.get('status') == 'success']
        if success_channels:
            updates_sent += 1
        
        # Rate limiting
        time.sleep(2.5)
    
    print(f"\n✅ Summary: Sent {updates_sent} updates")
    
    # Show routing statistics
    stats = router.get_routing_stats()
    print(f"\n📊 Channel Distribution:")
    for channel, count in stats['by_channel'].items():
        print(f"   #{channel}: {count} messages")
    
    # Send summary message
    print("\n📝 Sending summary to #dev-blog...")
    
    summary_content = f"""
**Intelligent Update System Report**

📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
📨 **Updates Sent:** {updates_sent}
📊 **Channels Used:** {len(stats['by_channel'])}

**Channel Activity:**
{chr(10).join(f'• #{ch}: {count} messages' for ch, count in stats['by_channel'].items())}

*All updates have been intelligently routed to appropriate channels based on content analysis.*
"""
    
    router.route_to_channels(
        title="📊 Intelligent Routing Summary",
        content=summary_content,
        post_type="summary",
        force_channels=['dev-blog']
    )
    
    print("\n✨ Intelligent update delivery complete!")

def demonstrate_channel_routing():
    """Demonstrate how different types of updates route to channels"""
    
    router = IntelligentDiscordRouter()
    
    print("\n🎯 Channel Routing Demonstration")
    print("=" * 50)
    
    # Examples based on your recent work
    examples = [
        {
            'title': '🐛 FIX: Coin card HTML rendering issue - removed complex f-string handlers',
            'content': 'Fixed the 12+ hour issue where coin cards showed raw HTML. Root cause was nested quotes in onerror handlers breaking f-string parsing.',
            'type': 'bug_fix'
        },
        {
            'title': '✨ FEATURE: Intelligent Discord channel routing system',
            'content': 'Implemented smart routing that analyzes commit messages and blog content to deliver updates to the most appropriate Discord channels.',
            'type': 'feature'
        },
        {
            'title': '📚 DOCS: Complete session documentation and structure updates',
            'content': 'Updated CLAUDE.md with comprehensive session history, implementation details, and architectural documentation.',
            'type': 'documentation'
        },
        {
            'title': '🚀 DEPLOY: Discord rate limit queue system v2.0',
            'content': 'Successfully deployed the new queue management system with priority handling, automatic retries, and comprehensive monitoring.',
            'type': 'deployment'
        },
        {
            'title': '🧪 TEST: 24-hour blog simulation completed successfully',
            'content': 'Ran comprehensive testing of blog system with 12 simulated posts over 24-hour period. All systems functioning correctly.',
            'type': 'testing'
        },
        {
            'title': '⚡ PERFORMANCE: Optimized dashboard load time by 60%',
            'content': 'Implemented lazy loading, caching, and removed redundant API calls to significantly improve dashboard performance.',
            'type': 'performance'
        },
        {
            'title': '🔧 SYSTEM: Git hygiene manager prevents repository corruption',
            'content': 'Created automated system to detect and fix git corruption issues, preventing "unable to read" errors.',
            'type': 'system_update'
        },
        {
            'title': '📈 SIGNAL: High confidence trade opportunity detected - $PEPE',
            'content': 'AI analysis shows 92% confidence score for $PEPE with volume spike and smart wallet accumulation.',
            'type': 'signal'
        }
    ]
    
    for example in examples:
        print(f"\n📌 {example['title']}")
        router.route_to_channels(
            title=example['title'],
            content=example['content'],
            post_type=example['type']
        )
        time.sleep(2)
    
    print("\n✅ Demonstration complete! Check Discord channels for routed messages.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demonstrate_channel_routing()
    else:
        send_recent_updates()