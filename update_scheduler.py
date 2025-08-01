#!/usr/bin/env python3
"""
TrenchCoat Pro - Update Scheduler
Automated scheduling and monitoring of library updates
"""

import schedule
import time
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from auto_library_updater import AutoLibraryUpdater

class UpdateScheduler:
    """Handles scheduled library updates"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.schedule_file = self.project_root / "update_schedule.json"
        self.updater = AutoLibraryUpdater()
        self.is_running = False
    
    def load_schedule_config(self) -> dict:
        """Load schedule configuration"""
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "frequency": "weekly",
            "auto_update": True,
            "notification_webhook": "https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61Dg2-WgSwrpIb110UiG4Z1f7",
            "next_check": (datetime.now() + timedelta(weeks=1)).isoformat(),
            "safe_hours": [2, 3, 4, 5],  # 2-5 AM UTC for updates
            "skip_on_failure": True
        }
    
    def save_schedule_config(self, config: dict):
        """Save schedule configuration"""
        with open(self.schedule_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def should_run_update(self) -> bool:
        """Check if update should run based on schedule"""
        config = self.load_schedule_config()
        
        if not config.get("auto_update", True):
            return False
        
        next_check = datetime.fromisoformat(config["next_check"])
        current_time = datetime.now()
        
        # Check if it's time for an update
        if current_time < next_check:
            return False
        
        # Check if we're in safe hours (optional)
        safe_hours = config.get("safe_hours", [])
        if safe_hours and current_time.hour not in safe_hours:
            print(f"Skipping update - not in safe hours ({safe_hours})")
            return False
        
        return True
    
    def run_scheduled_update(self):
        """Run scheduled update with proper error handling"""
        print(f"[{datetime.now()}] Running scheduled library update...")
        
        try:
            # Run the update
            result = self.updater.run_auto_update(test_mode=False)
            
            # Send notification
            self.updater.send_update_notification(result)
            
            # Update next check time
            config = self.load_schedule_config()
            frequency_map = {
                "daily": timedelta(days=1),
                "weekly": timedelta(weeks=1),
                "monthly": timedelta(days=30)
            }
            
            next_interval = frequency_map.get(config["frequency"], timedelta(weeks=1))
            config["next_check"] = (datetime.now() + next_interval).isoformat()
            config["last_update"] = datetime.now().isoformat()
            config["last_result"] = result["status"]
            
            self.save_schedule_config(config)
            
            print(f"[{datetime.now()}] Scheduled update completed: {result['status']}")
            
        except Exception as e:
            print(f"[{datetime.now()}] Scheduled update failed: {e}")
            
            # Update config with failure info
            config = self.load_schedule_config()
            config["last_error"] = str(e)
            config["last_error_time"] = datetime.now().isoformat()
            
            if config.get("skip_on_failure", True):
                # Skip to next scheduled time
                frequency_map = {
                    "daily": timedelta(days=1),
                    "weekly": timedelta(weeks=1), 
                    "monthly": timedelta(days=30)
                }
                next_interval = frequency_map.get(config["frequency"], timedelta(weeks=1))
                config["next_check"] = (datetime.now() + next_interval).isoformat()
            
            self.save_schedule_config(config)
    
    def setup_schedule(self):
        """Set up the update schedule"""
        config = self.load_schedule_config()
        frequency = config.get("frequency", "weekly")
        
        # Clear existing schedules
        schedule.clear()
        
        # Set up new schedule
        if frequency == "daily":
            schedule.every().day.at("03:00").do(self.check_and_update)
        elif frequency == "weekly":
            schedule.every().monday.at("03:00").do(self.check_and_update)
        elif frequency == "monthly":
            schedule.every().month.do(self.check_and_update)
        
        print(f"Update schedule set to: {frequency} at 03:00 UTC")
    
    def check_and_update(self):
        """Check if update should run and execute if needed"""
        if self.should_run_update():
            self.run_scheduled_update()
        else:
            print(f"[{datetime.now()}] Skipping scheduled update (not due yet)")
    
    def start_scheduler(self):
        """Start the scheduler daemon"""
        self.setup_schedule()
        self.is_running = True
        
        print("TrenchCoat Pro Update Scheduler started")
        print("Press Ctrl+C to stop")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")
            self.is_running = False
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
    
    def get_status(self) -> dict:
        """Get current scheduler status"""
        config = self.load_schedule_config()
        
        return {
            "is_running": self.is_running,
            "frequency": config.get("frequency", "weekly"),
            "auto_update": config.get("auto_update", True),
            "next_check": config.get("next_check"),
            "last_update": config.get("last_update"),
            "last_result": config.get("last_result"),
            "last_error": config.get("last_error"),
            "safe_hours": config.get("safe_hours", [2, 3, 4, 5])
        }

def main():
    """Main function for the scheduler"""
    scheduler = UpdateScheduler()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            scheduler.start_scheduler()
        elif command == "status":
            status = scheduler.get_status()
            print(f"Scheduler Status: {json.dumps(status, indent=2)}")
        elif command == "run-now":
            scheduler.run_scheduled_update()
        elif command == "setup":
            frequency = sys.argv[2] if len(sys.argv) > 2 else "weekly"
            config = scheduler.load_schedule_config()
            config["frequency"] = frequency
            config["auto_update"] = True
            
            # Set next check time
            frequency_map = {
                "daily": timedelta(days=1),
                "weekly": timedelta(weeks=1),
                "monthly": timedelta(days=30)
            }
            next_interval = frequency_map.get(frequency, timedelta(weeks=1))
            config["next_check"] = (datetime.now() + next_interval).isoformat()
            
            scheduler.save_schedule_config(config)
            print(f"Update schedule configured for {frequency} updates")
        else:
            print("Unknown command")
    else:
        print("TrenchCoat Pro Update Scheduler")
        print("Commands:")
        print("  start          - Start the scheduler daemon")
        print("  status         - Show scheduler status")
        print("  run-now        - Run update immediately")
        print("  setup [freq]   - Configure update frequency (daily/weekly/monthly)")

if __name__ == "__main__":
    main()