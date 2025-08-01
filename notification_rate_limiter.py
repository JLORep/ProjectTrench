#!/usr/bin/env python3
"""
Notification Rate Limiter - Prevent Discord spam
"""
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

class NotificationRateLimiter:
    def __init__(self, max_notifications_per_hour=5):
        self.max_notifications_per_hour = max_notifications_per_hour
        self.log_file = Path("notification_history.json")
        
    def load_history(self):
        """Load notification history"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def save_history(self, history):
        """Save notification history"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(history, f)
        except Exception:
            pass
    
    def clean_old_history(self, history):
        """Remove notifications older than 1 hour"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        return [
            entry for entry in history 
            if datetime.fromisoformat(entry['timestamp']) > one_hour_ago
        ]
    
    def can_send_notification(self, commit_hash: str, notification_type: str):
        """Check if we can send a notification"""
        history = self.load_history()
        history = self.clean_old_history(history)
        
        # Check if we've already sent this exact notification
        for entry in history:
            if entry['commit_hash'] == commit_hash and entry['type'] == notification_type:
                return False
        
        # Check rate limit
        if len(history) >= self.max_notifications_per_hour:
            return False
        
        return True
    
    def record_notification(self, commit_hash: str, notification_type: str):
        """Record that we sent a notification"""
        history = self.load_history()
        history = self.clean_old_history(history)
        
        history.append({
            'commit_hash': commit_hash,
            'type': notification_type,
            'timestamp': datetime.now().isoformat()
        })
        
        self.save_history(history)

# Global rate limiter instance
rate_limiter = NotificationRateLimiter(max_notifications_per_hour=3)  # Very restrictive