#!/usr/bin/env python3
"""
Send development update for latest commits
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import subprocess
import requests
import json
from datetime import datetime
from auto_overview_updater import AutoOverviewUpdater

def get_recent_commits():
    """Get recent commits for summary"""
    result = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, text=True)
    return result.stdout.strip().split('\n')

def send_dev_update():
    """Send development update to Discord"""
    
    # Get recent commits
    commits = get_recent_commits()
    
    # Latest features and fixes
    latest_features = [
        "✅ **Solana Wallet Integration** - Real-time portfolio tracking",
        "✅ **Live Price Feeds** - Jupiter & CoinGecko API integration", 
        "✅ **USD Portfolio Values** - Accurate SOL/USD conversion",
        "✅ **Multi-RPC Support** - Fallback endpoints for reliability",
        "✅ **SPL Token Detection** - Complete token balance tracking"
    ]
    
    latest_fixes = [
        "🔧 Added base58 dependency for wallet validation",
        "🔧 Fixed Streamlit 303 redirect (auth required)",
        "🔧 Updated CLAUDE.md with comprehensive infrastructure docs",
        "🔧 Documented existing wallet/portfolio systems to avoid duplication"
    ]
    
    # Technical message
    tech_message = f"""🚀 **TrenchCoat Pro Dev Update - {datetime.now().strftime('%Y-%m-%d')}**

**🎯 Major Achievement: Solana Wallet Integration Complete!**

**New Features:**
{chr(10).join(latest_features)}

**Bug Fixes & Improvements:**
{chr(10).join(latest_fixes)}

**Recent Commits:**
```
{chr(10).join(commits[:3])}
```

**Technical Details:**
- Integrated `SolanaWalletTracker` class with multi-RPC endpoints
- Real-time balance fetching via Solana JSON-RPC
- Jupiter Price API for live SOL/USD rates (CoinGecko fallback)
- Complete SPL token enumeration with metadata enrichment
- Dashboard integration via `render_solana_wallet_section()`

**Infrastructure Note:** All wallet/portfolio logic builds on existing production systems - no wheels reinvented! 🎯
"""

    # Non-technical message
    non_tech_message = f"""💎 **TrenchCoat Pro Update - Wallet Tracking Now Live!**

**What's New:**
🔗 **Connect Your Solana Wallet** - Track your real portfolio in the dashboard!
💰 **Live USD Values** - See your SOL worth in real-time
🪙 **All Tokens Visible** - Every SPL token in your wallet displayed
📊 **Portfolio Metrics** - Total value, token counts, and more

**Why This Matters:**
Users can now connect their actual Solana wallets to TrenchCoat Pro and see their real portfolio alongside our trading signals and analytics. No more demo data - this is YOUR real crypto!

**Try It Now:** Head to the dashboard and look for the "💎 Solana Wallet" section!

*Making crypto trading smarter, one feature at a time.* 🚀
"""

    # Discord webhook - fixed URL from webhook_config.json
    webhook_url = "https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61Dg2-WgSwrpIb110UiG4Z1f7"
    
    # Send technical update
    tech_payload = {
        "content": tech_message,
        "username": "TrenchCoat Dev Team",
        "avatar_url": "https://via.placeholder.com/64x64/10b981/ffffff?text=DEV"
    }
    
    response = requests.post(webhook_url, json=tech_payload)
    print(f"Tech message sent: {response.status_code}")
    
    # Wait a moment
    import time
    time.sleep(2)
    
    # Send non-technical update
    non_tech_payload = {
        "content": non_tech_message,
        "username": "TrenchCoat Updates", 
        "avatar_url": "https://via.placeholder.com/64x64/3b82f6/ffffff?text=TC"
    }
    
    response = requests.post(webhook_url, json=non_tech_payload)
    print(f"Non-tech message sent: {response.status_code}")
    
    # Update overview
    print("\nUpdating project overview...")
    updater = AutoOverviewUpdater()
    # Add the Solana wallet feature
    updater.add_new_feature(
        "Solana Wallet Integration",
        "Real-time portfolio tracking with live USD values",
        "wallet"
    )
    updater.send_feature_update()
    print("✅ Overview updated!")
    
    # Update CLAUDE.md
    print("\nUpdating CLAUDE.md with latest session info...")
    update_claude_md()
    print("✅ CLAUDE.md updated!")

def update_claude_md():
    """Update CLAUDE.md with latest session achievements"""
    from datetime import datetime
    
    # Read current CLAUDE.md
    with open('CLAUDE.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the last updated line
    if '*Last updated:' in content:
        # Update the timestamp
        import re
        content = re.sub(
            r'\*Last updated: .+\*',
            f'*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")} - Solana wallet integration complete, dev blog triggered*',
            content
        )
    
    # Write back
    with open('CLAUDE.md', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    send_dev_update()