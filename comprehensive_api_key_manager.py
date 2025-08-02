#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrenchCoat Pro Comprehensive API Key Management System
Secure API key lifecycle management with automatic renewal monitoring
"""

import json
import base64
import hashlib
import os
import sys
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass

class APIKeyManager:
    """Comprehensive API key management system"""
    
    def __init__(self, config_file: str = "api_keys_config.json"):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load API key configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration structure"""
        return {
            "api_keys": {},
            "monitoring": {
                "enabled": True,
                "check_interval_hours": 12,
                "notification_days": [30, 14, 7, 3, 1]
            },
            "notifications": {
                "email_enabled": False,
                "discord_enabled": True,
                "telegram_enabled": True,
                "file_enabled": True
            },
            "auto_renewal": {
                "enabled": False,
                "providers": []
            },
            "last_check": None
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def encrypt_key(self, api_key: str) -> str:
        """Encrypt API key using base64 encoding"""
        try:
            encoded = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
            return encoded
        except Exception as e:
            print(f"Error encrypting key: {e}")
            return api_key
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt API key from base64 encoding"""
        try:
            decoded = base64.b64decode(encrypted_key.encode('utf-8')).decode('utf-8')
            return decoded
        except Exception as e:
            print(f"Error decrypting key: {e}")
            return encrypted_key
    
    def add_api_key(self, provider: str, api_key: str, name: str, 
                   expiry_days: int = 90) -> str:
        """Add a new API key to the management system"""
        # Generate unique ID
        key_id = hashlib.md5(f"{provider}_{name}_{datetime.now()}".encode()).hexdigest()[:8]
        
        # Calculate expiry date
        created_date = datetime.now()
        expires_date = created_date + timedelta(days=expiry_days)
        
        # Encrypt the key
        encrypted_key = self.encrypt_key(api_key)
        
        # Store key information
        self.config["api_keys"][key_id] = {
            "provider": provider,
            "key": encrypted_key,
            "name": name,
            "created_date": created_date.isoformat(),
            "expires_date": expires_date.isoformat(),
            "expiry_days": expiry_days,
            "active": True,
            "last_used": created_date.isoformat(),
            "usage_count": 0,
            "last_test_result": None,
            "renewal_notifications_sent": []
        }
        
        self.save_config()
        return key_id
    
    def get_api_key(self, key_id: str) -> Optional[str]:
        """Get decrypted API key by ID"""
        if key_id in self.config["api_keys"]:
            encrypted_key = self.config["api_keys"][key_id]["key"]
            return self.decrypt_key(encrypted_key)
        return None
    
    def validate_api_key(self, key_id: str) -> Dict[str, Any]:
        """Validate an API key by testing it"""
        if key_id not in self.config["api_keys"]:
            return {"valid": False, "error": "Key not found"}
        
        key_info = self.config["api_keys"][key_id]
        provider = key_info["provider"]
        api_key = self.get_api_key(key_id)
        
        validation_result = {"valid": False, "timestamp": datetime.now().isoformat()}
        
        try:
            if provider == "github":
                # Test GitHub API
                headers = {"Authorization": f"token {api_key}"}
                response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
                
                validation_result.update({
                    "valid": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining"),
                    "rate_limit_reset": response.headers.get("X-RateLimit-Reset")
                })
                
                if response.status_code == 200:
                    user_data = response.json()
                    validation_result["user"] = user_data.get("login")
                    validation_result["scopes"] = response.headers.get("X-OAuth-Scopes", "").split(", ")
                    
            elif provider == "telegram":
                # Test Telegram Bot API
                response = requests.get(f"https://api.telegram.org/bot{api_key}/getMe", timeout=10)
                
                validation_result.update({
                    "valid": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "rate_limit_remaining": None,
                    "rate_limit_reset": None
                })
                
            elif provider == "discord":
                # Test Discord Webhook
                test_payload = {"content": "TrenchCoat Pro API Key Test (ignore this message)"}
                response = requests.post(api_key, json=test_payload, timeout=10)
                
                validation_result.update({
                    "valid": response.status_code == 204,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining"),
                    "rate_limit_reset": response.headers.get("X-RateLimit-Reset")
                })
                
            else:
                validation_result = {"valid": False, "error": f"Unknown provider: {provider}"}
                
        except Exception as e:
            validation_result = {"valid": False, "error": str(e)}
        
        # Update key with test result
        self.config["api_keys"][key_id]["last_test_result"] = validation_result
        self.config["api_keys"][key_id]["last_used"] = datetime.now().isoformat()
        self.config["api_keys"][key_id]["usage_count"] += 1
        
        self.save_config()
        return validation_result
    
    def validate_all_keys(self) -> Dict[str, Dict[str, Any]]:
        """Validate all API keys"""
        results = {}
        for key_id in self.config["api_keys"]:
            results[key_id] = self.validate_api_key(key_id)
        return results
    
    def check_expiring_keys(self) -> List[Dict[str, Any]]:
        """Check for keys that are expiring soon"""
        notifications = []
        now = datetime.now()
        notification_days = self.config["monitoring"]["notification_days"]
        
        for key_id, key_info in self.config["api_keys"].items():
            try:
                expires_date = datetime.fromisoformat(key_info["expires_date"])
                days_until_expiry = (expires_date - now).days
                
                if days_until_expiry in notification_days:
                    # Check if we already sent notification for this timeframe
                    if days_until_expiry not in key_info.get("renewal_notifications_sent", []):
                        notifications.append({
                            "key_id": key_id,
                            "provider": key_info["provider"],
                            "name": key_info["name"],
                            "days_until_expiry": days_until_expiry,
                            "expires_date": key_info["expires_date"],
                            "urgency": "critical" if days_until_expiry <= 3 else "warning"
                        })
                        
                        # Mark notification as sent
                        key_info["renewal_notifications_sent"].append(days_until_expiry)
                        
            except Exception as e:
                print(f"Error checking expiry for key {key_id}: {e}")
        
        if notifications:
            self.save_config()
        
        return notifications
    
    def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        report = f"""# 🔑 TrenchCoat Pro API Key Status Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Summary

- **Total Keys**: {len(self.config["api_keys"])}
- **Active Keys**: {sum(1 for key in self.config["api_keys"].values() if key.get('active', False))}
- **Monitoring**: {'✅ Enabled' if self.config["monitoring"]["enabled"] else '❌ Disabled'}

## 🔑 Key Details

"""
        
        for key_id, key_info in self.config["api_keys"].items():
            provider = key_info.get("provider", "Unknown")
            name = key_info.get("name", "Unnamed")
            active = "✅ Active" if key_info.get("active", False) else "❌ Inactive"
            
            # Calculate days until expiry
            try:
                expires_date = datetime.fromisoformat(key_info["expires_date"])
                days_until_expiry = (expires_date - datetime.now()).days
                expiry_str = f"{days_until_expiry} days" if days_until_expiry > 0 else "⚠️ EXPIRED"
            except:
                expiry_str = "Unknown"
            
            # Get last test result
            last_test = key_info.get("last_test_result", {})
            test_status = "✅ Valid" if last_test.get("valid") else "❌ Invalid"
            
            report += f"""### {provider.title()} - {name}
- **ID**: `{key_id}`
- **Status**: {active}
- **Expires**: {expiry_str}
- **Last Test**: {test_status}
- **Usage Count**: {key_info.get("usage_count", 0)}

"""
        
        # Add expiring keys section
        expiring_keys = self.check_expiring_keys()
        if expiring_keys:
            report += "## ⚠️ Keys Requiring Attention\n\n"
            for key in expiring_keys:
                urgency_icon = "🚨" if key["urgency"] == "critical" else "⚠️"
                report += f"- {urgency_icon} **{key['provider']}** expires in {key['days_until_expiry']} days\n"
            report += "\n"
        
        report += f"""## 🔧 Configuration

- **Check Interval**: {self.config["monitoring"]["check_interval_hours"]} hours
- **Notification Days**: {self.config["monitoring"]["notification_days"]}
- **Discord Notifications**: {'✅' if self.config["notifications"]["discord_enabled"] else '❌'}
- **Telegram Notifications**: {'✅' if self.config["notifications"]["telegram_enabled"] else '❌'}
- **File Notifications**: {'✅' if self.config["notifications"]["file_enabled"] else '❌'}

---

*Generated by TrenchCoat Pro API Key Management System*
"""
        
        return report

def main():
    """Main CLI interface for API key management"""
    print("🔑 TrenchCoat Pro API Key Management System")
    print("=" * 60)
    
    manager = APIKeyManager()
    
    # Show status
    print(f"📊 Status: {len(manager.config['api_keys'])} keys managed")
    
    # Check for expiring keys
    expiring_keys = manager.check_expiring_keys()
    if expiring_keys:
        print(f"⚠️  Warning: {len(expiring_keys)} keys need attention")
        for key in expiring_keys:
            print(f"   - {key['provider']}: {key['days_until_expiry']} days remaining")
    
    # Validate all keys
    print("\n🔍 Testing all API keys...")
    results = manager.validate_all_keys()
    
    valid_count = sum(1 for result in results.values() if result.get('valid', False))
    print(f"✅ {valid_count}/{len(results)} keys are valid")
    
    # Generate report
    report = manager.generate_status_report()
    report_file = f"API_KEY_STATUS_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Status report saved: {report_file}")

if __name__ == "__main__":
    main()