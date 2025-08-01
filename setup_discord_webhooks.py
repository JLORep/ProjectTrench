#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Webhook Setup Helper

This script helps configure Discord webhooks for the documentation update system.
Run this to easily set up your Discord integration.

Usage:
    python setup_discord_webhooks.py
"""

import json
import os

def setup_discord_webhooks():
    """Interactive setup for Discord webhooks"""
    
    print("=" * 60)
    print("DISCORD WEBHOOK SETUP - TrenchCoat Pro")
    print("=" * 60)
    print()
    print("This will help you configure Discord notifications for documentation updates.")
    print()
    print("To get Discord webhook URLs:")
    print("1. Go to your Discord server")
    print("2. Right-click on a channel > Edit Channel > Integrations > Webhooks")
    print("3. Create New Webhook, customize name/avatar, copy the URL")
    print()
    
    # Get webhook URLs
    webhooks = {}
    
    channels = {
        'development': 'Development updates and code changes',
        'documentation': 'Documentation updates and guides', 
        'general': 'General project updates',
        'alerts': 'Error alerts and urgent notifications'
    }
    
    for channel, description in channels.items():
        print(f"Channel: #{channel}")
        print(f"Purpose: {description}")
        
        webhook_url = input(f"Enter webhook URL for #{channel} (or press Enter to skip): ").strip()
        
        if webhook_url:
            # Basic validation
            if webhook_url.startswith('https://discord.com/api/webhooks/'):
                webhooks[channel] = webhook_url
                print(f"✅ #{channel} webhook configured")
            else:
                print(f"⚠️ Invalid webhook URL format for #{channel}")
        else:
            print(f"⏭️ Skipping #{channel}")
        
        print()
    
    if not webhooks:
        print("No webhooks configured. Exiting...")
        return False
    
    # Create configuration
    config = {
        "discord_webhooks": webhooks,
        "channel_mappings": {
            "development": {
                "name": "trench-development",
                "description": "Development updates and code changes",
                "color": 0x00ff00
            },
            "documentation": {
                "name": "trench-docs", 
                "description": "Documentation updates and guides",
                "color": 0x0099ff
            },
            "general": {
                "name": "trench-general",
                "description": "General project updates",
                "color": 0xffff00
            },
            "alerts": {
                "name": "trench-alerts",
                "description": "Error alerts and urgent notifications", 
                "color": 0xff0000
            }
        },
        "notification_settings": {
            "enable_discord": True,
            "max_files_in_embed": 10,
            "timeout_seconds": 10,
            "retry_attempts": 2
        }
    }
    
    # Save configuration
    config_file = 'webhook_config.json'
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, indent=2, fp=f)
        
        print("=" * 40)
        print("✅ CONFIGURATION SAVED")
        print(f"File: {config_file}")
        print(f"Webhooks configured: {len(webhooks)}")
        print()
        print("You can now use the documentation updater with Discord notifications:")
        print('python update_all_docs.py "Session Title" "Description"')
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def test_webhooks():
    """Test configured webhooks"""
    
    if not os.path.exists('webhook_config.json'):
        print("❌ No webhook configuration found. Run setup first.")
        return False
    
    try:
        with open('webhook_config.json') as f:
            config = json.load(f)
        
        webhooks = config.get('discord_webhooks', {})
        
        if not webhooks:
            print("❌ No webhooks configured.")
            return False
        
        print("🧪 TESTING DISCORD WEBHOOKS")
        print("=" * 30)
        
        # Import and test
        from update_all_docs import DocumentationUpdater
        
        updater = DocumentationUpdater()
        
        # Send test notification
        for channel, webhook_url in webhooks.items():
            print(f"Testing #{channel}...", end=" ")
            
            success = updater.send_discord_notification(
                webhook_url,
                "Test Notification",
                "This is a test of the Discord webhook integration for TrenchCoat Pro documentation updates.",
                0x0099ff
            )
            
            if success:
                print("✅ SUCCESS")
            else:
                print("❌ FAILED")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing webhooks: {e}")
        return False

def main():
    """Main function"""
    
    if len(os.sys.argv) > 1 and os.sys.argv[1] == 'test':
        test_webhooks()
    else:
        setup_discord_webhooks()

if __name__ == "__main__":
    main()