#!/usr/bin/env python3
"""
Streamlit Rate Limit Handler
Detects and manages Streamlit Cloud deployment rate limiting
"""
import subprocess
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from unicode_handler import safe_print

class StreamlitRateLimitHandler:
    """Handles Streamlit Cloud rate limiting detection and management"""
    
    def __init__(self):
        self.rate_limit_file = Path("streamlit_rate_limits.json")
        self.max_deploys_per_hour = 5  # Conservative limit
        self.cooldown_minutes = 30
        
    def load_deployment_history(self) -> list:
        """Load recent deployment history"""
        try:
            if self.rate_limit_file.exists():
                with open(self.rate_limit_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def save_deployment_history(self, history: list):
        """Save deployment history"""
        try:
            with open(self.rate_limit_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            safe_print(f"Warning: Could not save deployment history: {e}")
    
    def record_deployment(self, commit_hash: str):
        """Record a new deployment"""
        history = self.load_deployment_history()
        
        # Add new deployment
        deployment = {
            'commit_hash': commit_hash,
            'timestamp': datetime.now().isoformat(),
            'deployed': True
        }
        
        history.append(deployment)
        
        # Keep only last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        history = [
            d for d in history 
            if datetime.fromisoformat(d['timestamp']) > cutoff
        ]
        
        self.save_deployment_history(history)
    
    def get_recent_deployments(self, hours: int = 1) -> list:
        """Get deployments from the last N hours"""
        history = self.load_deployment_history()
        cutoff = datetime.now() - timedelta(hours=hours)
        
        return [
            d for d in history 
            if datetime.fromisoformat(d['timestamp']) > cutoff
        ]
    
    def is_rate_limited(self) -> dict:
        """Check if we're likely rate limited"""
        recent_deploys = self.get_recent_deployments(1)  # Last hour
        
        rate_limited = len(recent_deploys) >= self.max_deploys_per_hour
        
        if rate_limited:
            oldest_deploy = min(recent_deploys, key=lambda d: d['timestamp'])
            cooldown_end = datetime.fromisoformat(oldest_deploy['timestamp']) + timedelta(minutes=60)
            minutes_remaining = max(0, (cooldown_end - datetime.now()).total_seconds() / 60)
        else:
            minutes_remaining = 0
        
        return {
            'is_rate_limited': rate_limited,
            'recent_deployments': len(recent_deploys),
            'max_per_hour': self.max_deploys_per_hour,
            'minutes_until_reset': int(minutes_remaining),
            'can_deploy': not rate_limited
        }
    
    def should_skip_deployment(self, commit_msg: str) -> dict:
        """Determine if deployment should be skipped due to rate limiting"""
        rate_status = self.is_rate_limited()
        
        # Always allow critical deployments
        is_critical = any(word in commit_msg.lower() for word in ['critical:', 'urgent:', 'security:'])
        
        if rate_status['is_rate_limited'] and not is_critical:
            return {
                'should_skip': True,
                'reason': 'rate_limited',
                'message': f"Skipping deployment - rate limited. {rate_status['minutes_until_reset']} minutes remaining.",
                'rate_status': rate_status
            }
        
        return {
            'should_skip': False,
            'reason': 'approved',
            'message': 'Deployment approved',
            'rate_status': rate_status
        }
    
    def wait_for_rate_limit_reset(self) -> bool:
        """Wait for rate limit to reset if needed"""
        rate_status = self.is_rate_limited()
        
        if not rate_status['is_rate_limited']:
            return True
        
        wait_minutes = rate_status['minutes_until_reset']
        if wait_minutes > 30:  # Don't wait more than 30 minutes
            safe_print(f"⏰ Rate limit reset in {wait_minutes} minutes - too long to wait")
            return False
        
        safe_print(f"⏳ Waiting {wait_minutes} minutes for Streamlit rate limit reset...")
        time.sleep(wait_minutes * 60)
        
        # Check again
        new_status = self.is_rate_limited()
        return not new_status['is_rate_limited']

def main():
    """CLI tool for checking rate limit status"""
    handler = StreamlitRateLimitHandler()
    status = handler.is_rate_limited()
    
    if status['is_rate_limited']:
        safe_print(f"🚫 RATE LIMITED: {status['recent_deployments']}/{status['max_per_hour']} deployments in last hour")
        safe_print(f"⏰ Reset in: {status['minutes_until_reset']} minutes")
        return 1
    else:
        safe_print(f"✅ OK: {status['recent_deployments']}/{status['max_per_hour']} deployments in last hour")
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())