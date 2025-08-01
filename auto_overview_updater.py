#!/usr/bin/env python3
"""
TrenchCoat Pro - Automatic Overview Updater
Keeps Discord overview channel updated when features change
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class AutoOverviewUpdater:
    """Automatically updates Discord overview when features change"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.overview_webhook = "https://discord.com/api/webhooks/1400497302241677383/Im9oyVehkH6zhsc5w4mt4KHQvgSR2qfMPD-k6lTR-X0XQWT3eLV_IJM2-MqQNM6dPAzM"
        self.feature_state_file = self.project_root / "feature_state.json"
        
        # Initialize feature tracking
        self.init_feature_tracking()
    
    def init_feature_tracking(self):
        """Initialize feature state tracking"""
        if not self.feature_state_file.exists():
            initial_state = {
                "last_updated": datetime.now().isoformat(),
                "version": "2.1.0",
                "features": {
                    "Live Trading Intelligence": "active",
                    "Ultra-Premium Dashboard": "active",
                    "Machine Learning Engine": "active",
                    "Multi-Platform Notifications": "active",
                    "Advanced Signal Processing": "active",
                    "Automated Trading Engine": "active",
                    "Data Management System": "active",
                    "Auto Library Updates": "new",
                    "Automated Dev Blog": "active",
                    "Professional Branding": "active"
                }
            }
            
            with open(self.feature_state_file, 'w') as f:
                json.dump(initial_state, f, indent=2)
    
    def load_feature_state(self) -> Dict:
        """Load current feature state"""
        with open(self.feature_state_file, 'r') as f:
            return json.load(f)
    
    def save_feature_state(self, state: Dict):
        """Save feature state"""
        with open(self.feature_state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def add_new_feature(self, feature_name: str, status: str = "new", description: str = ""):
        """Add a new feature and update Discord"""
        
        state = self.load_feature_state()
        
        # Add the new feature
        state["features"][feature_name] = status
        state["last_updated"] = datetime.now().isoformat()
        
        # Save updated state
        self.save_feature_state(state)
        
        # Send Discord notification about new feature
        self.send_new_feature_notification(feature_name, status, description)
        
        # Update overview channel with new feature list
        self.send_feature_update()
    
    def update_feature_status(self, feature_name: str, new_status: str):
        """Update existing feature status"""
        
        state = self.load_feature_state()
        
        if feature_name in state["features"]:
            old_status = state["features"][feature_name]
            state["features"][feature_name] = new_status
            state["last_updated"] = datetime.now().isoformat()
            
            self.save_feature_state(state)
            
            # Send status change notification
            self.send_status_change_notification(feature_name, old_status, new_status)
    
    def send_new_feature_notification(self, feature_name: str, status: str, description: str):
        """Send notification about new feature"""
        
        status_emoji = {
            "new": "🆕",
            "active": "✅",
            "beta": "🧪",
            "coming_soon": "🚧",
            "deprecated": "⚠️"
        }
        
        emoji = status_emoji.get(status, "🔧")
        
        message = f"""🚀 **TrenchCoat Pro - New Feature Added!**

{emoji} **{feature_name}** - **{status.title()}**

{description}

📊 **Updated Overview:**
All project documentation and feature lists have been automatically updated.

⏰ Added: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

#NewFeature #TrenchCoatPro #Update"""

        try:
            payload = {
                "content": message,
                "username": "TrenchCoat Pro - Feature Update"
            }
            
            response = requests.post(self.overview_webhook, json=payload, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error sending new feature notification: {e}")
            return False
    
    def send_status_change_notification(self, feature_name: str, old_status: str, new_status: str):
        """Send notification about feature status change"""
        
        status_emoji = {
            "new": "🆕",
            "active": "✅", 
            "beta": "🧪",
            "coming_soon": "🚧",
            "deprecated": "⚠️"
        }
        
        old_emoji = status_emoji.get(old_status, "🔧")
        new_emoji = status_emoji.get(new_status, "🔧")
        
        message = f"""🔄 **TrenchCoat Pro - Feature Status Update**

**{feature_name}**
{old_emoji} {old_status.title()} → {new_emoji} {new_status.title()}

📊 **Overview Updated:** Feature status has been automatically updated across all channels.

⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

#StatusUpdate #TrenchCoatPro"""

        try:
            payload = {
                "content": message,
                "username": "TrenchCoat Pro - Status Update"
            }
            
            response = requests.post(self.overview_webhook, json=payload, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error sending status change notification: {e}")
            return False
    
    def send_feature_update(self):
        """Send updated feature list to overview channel"""
        
        state = self.load_feature_state()
        
        feature_list = ""
        for feature, status in state["features"].items():
            status_emoji = {
                "new": "🆕",
                "active": "✅",
                "beta": "🧪", 
                "coming_soon": "🚧",
                "deprecated": "⚠️"
            }
            
            emoji = status_emoji.get(status, "🔧")
            feature_list += f"• {emoji} **{feature}** - {status.title()}\n"
        
        message = f"""📋 **TrenchCoat Pro - Current Feature Status**

🚀 **All Features ({len(state['features'])}):**
{feature_list}

📈 **Version:** {state.get('version', '2.1.0')}
⏰ **Last Updated:** {datetime.fromisoformat(state['last_updated']).strftime('%Y-%m-%d %H:%M UTC')}

#FeatureList #TrenchCoatPro #Overview"""

        try:
            payload = {
                "content": message,
                "username": "TrenchCoat Pro - Feature List"
            }
            
            response = requests.post(self.overview_webhook, json=payload, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error sending feature update: {e}")
            return False
    
    def increment_version(self, version_type: str = "patch"):
        """Increment version number and update Discord"""
        
        state = self.load_feature_state()
        current_version = state.get("version", "2.1.0")
        
        # Parse version
        major, minor, patch = map(int, current_version.split('.'))
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        state["version"] = new_version
        state["last_updated"] = datetime.now().isoformat()
        
        self.save_feature_state(state)
        
        # Send version update notification
        self.send_version_update_notification(current_version, new_version, version_type)
        
        return new_version
    
    def send_version_update_notification(self, old_version: str, new_version: str, version_type: str):
        """Send version update notification"""
        
        version_emoji = {
            "major": "🚀",
            "minor": "✨", 
            "patch": "🔧"
        }
        
        emoji = version_emoji.get(version_type, "🔧")
        
        message = f"""{emoji} **TrenchCoat Pro - Version Update**

📈 **Version:** {old_version} → **{new_version}**
🏷️ **Type:** {version_type.title()} Release

🎯 **What's New:**
This {version_type} update includes improvements and new features to enhance your trading experience.

📊 **Live Demo:** https://trenchdemo.streamlit.app
📂 **GitHub:** https://github.com/JLORep/ProjectTrench

⏰ Released: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

#VersionUpdate #Release #TrenchCoatPro"""

        try:
            payload = {
                "content": message,
                "username": "TrenchCoat Pro - Version Update"
            }
            
            response = requests.post(self.overview_webhook, json=payload, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error sending version update: {e}")
            return False

def main():
    """Main function for testing the auto updater"""
    
    updater = AutoOverviewUpdater()
    
    print("TrenchCoat Pro Auto Overview Updater")
    print("1. Add new feature")
    print("2. Update feature status")
    print("3. Send current feature list")
    print("4. Increment version")
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == "1":
        feature_name = input("Feature name: ").strip()
        status = input("Status (new/active/beta/coming_soon): ").strip()
        description = input("Description: ").strip()
        updater.add_new_feature(feature_name, status, description)
        print("New feature added and Discord updated!")
        
    elif choice == "2":
        feature_name = input("Feature name: ").strip()
        new_status = input("New status (active/beta/deprecated): ").strip()
        updater.update_feature_status(feature_name, new_status)
        print("Feature status updated!")
        
    elif choice == "3":
        updater.send_feature_update()
        print("Feature list sent to Discord!")
        
    elif choice == "4":
        version_type = input("Version type (major/minor/patch): ").strip()
        new_version = updater.increment_version(version_type)
        print(f"Version updated to {new_version}!")

if __name__ == "__main__":
    main()