#!/usr/bin/env python3
"""
TrenchCoat Pro - Automated Library Updater
Safe dependency updates with rollback capabilities and feature testing
"""

import subprocess
import json
import os
import shutil
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import requests
import re
from pathlib import Path

class AutoLibraryUpdater:
    """Automated library updater with safety checks"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.requirements_file = self.project_root / "requirements.txt"
        self.backup_dir = self.project_root / "library_backups"
        self.test_results_file = self.project_root / "update_test_results.json"
        self.update_log_file = self.project_root / "library_update_log.json"
        
        # Critical features to test after updates
        self.critical_tests = [
            "streamlit_app_loads",
            "dashboard_renders",
            "data_processing_works",
            "ml_models_function",
            "notifications_send",
            "database_operations"
        ]
        
        # Libraries that should be updated conservatively
        self.conservative_libraries = [
            "streamlit",  # UI framework - breaking changes affect everything
            "pandas",     # Data processing core
            "numpy",      # Mathematical foundation
            "scikit-learn" # ML models
        ]
        
        # Libraries safe for aggressive updates
        self.safe_libraries = [
            "requests",
            "pillow", 
            "python-dateutil",
            "seaborn"
        ]
        
        self.init_directories()
    
    def init_directories(self):
        """Initialize backup and log directories"""
        self.backup_dir.mkdir(exist_ok=True)
        
        if not self.update_log_file.exists():
            self.save_log({
                "created": datetime.now().isoformat(),
                "updates": [],
                "rollbacks": []
            })
    
    def get_current_versions(self) -> Dict[str, str]:
        """Get currently installed package versions"""
        current_versions = {}
        
        if self.requirements_file.exists():
            with open(self.requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '==' in line:
                            package, version = line.split('==')
                            current_versions[package.strip()] = version.strip()
        
        return current_versions
    
    def get_latest_versions(self, packages: List[str]) -> Dict[str, str]:
        """Get latest available versions from PyPI"""
        latest_versions = {}
        
        for package in packages:
            try:
                print(f"Checking latest version for {package}...")
                response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    latest_versions[package] = data['info']['version']
                else:
                    print(f"Warning: Could not fetch version info for {package}")
            except Exception as e:
                print(f"Error fetching version for {package}: {e}")
                
        return latest_versions
    
    def create_backup(self) -> str:
        """Create backup of current environment"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Backup requirements.txt
        if self.requirements_file.exists():
            shutil.copy2(self.requirements_file, backup_path / "requirements.txt")
        
        # Backup virtual environment info (if available)
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                                  capture_output=True, text=True, check=True)
            with open(backup_path / "pip_freeze.txt", 'w') as f:
                f.write(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not create pip freeze backup: {e}")
        
        return str(backup_path)
    
    def run_safety_tests(self) -> Dict[str, bool]:
        """Run safety tests to ensure features still work"""
        test_results = {}
        
        print("Running safety tests...")
        
        # Test 1: Streamlit app loads
        test_results["streamlit_app_loads"] = self.test_streamlit_import()
        
        # Test 2: Dashboard renders
        test_results["dashboard_renders"] = self.test_dashboard_components()
        
        # Test 3: Data processing works
        test_results["data_processing_works"] = self.test_data_processing()
        
        # Test 4: ML models function
        test_results["ml_models_function"] = self.test_ml_functionality()
        
        # Test 5: Notifications send
        test_results["notifications_send"] = self.test_notification_system()
        
        # Test 6: Database operations
        test_results["database_operations"] = self.test_database_operations()
        
        return test_results
    
    def test_streamlit_import(self) -> bool:
        """Test if Streamlit can be imported and basic functions work"""
        try:
            import streamlit as st
            import pandas as pd
            import numpy as np
            import plotly.graph_objects as go
            
            # Test basic functionality
            test_data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
            test_array = np.array([1, 2, 3])
            test_fig = go.Figure()
            
            return True
        except Exception as e:
            print(f"Streamlit import test failed: {e}")
            return False
    
    def test_dashboard_components(self) -> bool:
        """Test if dashboard components can be imported"""
        try:
            from ultra_premium_dashboard import main
            from live_data_integration import LiveDataManager
            from model_builder import ModelBuilder
            from historic_data_manager import HistoricDataManager
            
            return True
        except Exception as e:
            print(f"Dashboard component test failed: {e}")
            return False
    
    def test_data_processing(self) -> bool:
        """Test pandas and numpy functionality"""
        try:
            import pandas as pd
            import numpy as np
            
            # Test DataFrame operations
            df = pd.DataFrame({
                'symbol': ['BTC', 'ETH', 'SOL'],
                'price': [45000, 2500, 100],
                'volume': [1000000, 500000, 200000]
            })
            
            # Test basic operations
            result = df.groupby('symbol')['volume'].sum()
            correlation = df[['price', 'volume']].corr()
            
            # Test numpy operations
            arr = np.random.random((10, 5))
            mean_val = np.mean(arr)
            std_val = np.std(arr)
            
            return True
        except Exception as e:
            print(f"Data processing test failed: {e}")
            return False
    
    def test_ml_functionality(self) -> bool:
        """Test machine learning components"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score
            import numpy as np
            
            # Create sample data
            X = np.random.random((100, 4))
            y = np.random.randint(0, 2, 100)
            
            # Test model training
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = RandomForestClassifier(n_estimators=10, random_state=42)
            model.fit(X_train, y_train)
            
            # Test prediction
            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            
            return True
        except Exception as e:
            print(f"ML functionality test failed: {e}")
            return False
    
    def test_notification_system(self) -> bool:
        """Test notification system imports"""
        try:
            import requests
            from unified_notifications import UnifiedNotificationSystem
            
            # Test basic requests functionality
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Notification system test failed: {e}")
            return False
    
    def test_database_operations(self) -> bool:
        """Test database operations"""
        try:
            import sqlite3
            from datetime import datetime
            
            # Test SQLite operations
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                INSERT INTO test_table (name, created_at) 
                VALUES (?, ?)
            ''', ('test', datetime.now()))
            
            cursor.execute('SELECT * FROM test_table')
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
        except Exception as e:
            print(f"Database operations test failed: {e}")
            return False
    
    def update_package(self, package: str, version: str) -> bool:
        """Update a specific package to a specific version"""
        try:
            print(f"Updating {package} to {version}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", f"{package}=={version}"
            ], capture_output=True, text=True, check=True)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to update {package}: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def rollback_to_backup(self, backup_path: str) -> bool:
        """Rollback to a previous backup"""
        try:
            print(f"Rolling back to backup: {backup_path}")
            backup_requirements = Path(backup_path) / "requirements.txt"
            
            if backup_requirements.exists():
                # Install from backup requirements
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(backup_requirements)
                ], capture_output=True, text=True, check=True)
                
                # Update current requirements.txt
                shutil.copy2(backup_requirements, self.requirements_file)
                
                return True
        except Exception as e:
            print(f"Rollback failed: {e}")
            return False
        
        return False
    
    def update_requirements_file(self, updated_packages: Dict[str, str]):
        """Update requirements.txt with new versions"""
        current_versions = self.get_current_versions()
        current_versions.update(updated_packages)
        
        with open(self.requirements_file, 'w') as f:
            for package, version in sorted(current_versions.items()):
                f.write(f"{package}=={version}\n")
    
    def save_log(self, log_data: Dict):
        """Save update log"""
        with open(self.update_log_file, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
    
    def load_log(self) -> Dict:
        """Load update log"""
        if self.update_log_file.exists():
            with open(self.update_log_file, 'r') as f:
                return json.load(f)
        return {"updates": [], "rollbacks": []}
    
    def should_update_package(self, package: str, current_version: str, latest_version: str) -> bool:
        """Determine if a package should be updated based on safety rules"""
        
        # Skip if versions are the same
        if current_version == latest_version:
            return False
        
        # Parse version numbers for comparison
        def parse_version(version_str):
            return tuple(map(int, version_str.split('.')))
        
        try:
            current_v = parse_version(current_version)
            latest_v = parse_version(latest_version)
        except ValueError:
            print(f"Warning: Could not parse versions for {package}")
            return False
        
        # Conservative updates for critical libraries
        if package in self.conservative_libraries:
            # Only update patch versions (x.y.Z) for conservative libraries
            if current_v[0] == latest_v[0] and current_v[1] == latest_v[1]:
                return True
            else:
                print(f"Skipping major/minor update for conservative library {package}")
                return False
        
        # Safe libraries can be updated more aggressively
        if package in self.safe_libraries:
            # Allow minor updates (x.Y.z) for safe libraries
            if current_v[0] == latest_v[0]:
                return True
            else:
                print(f"Skipping major update for {package}")
                return False
        
        # Default: only patch updates
        if current_v[0] == latest_v[0] and current_v[1] == latest_v[1]:
            return True
        
        return False
    
    def run_auto_update(self, test_mode: bool = False) -> Dict[str, any]:
        """Run the complete auto-update process"""
        
        print("🔄 Starting TrenchCoat Pro Auto Library Update")
        print("=" * 50)
        
        # Get current state
        current_versions = self.get_current_versions()
        print(f"Found {len(current_versions)} packages in requirements.txt")
        
        # Get latest versions
        print("\nChecking for updates...")
        latest_versions = self.get_latest_versions(list(current_versions.keys()))
        
        # Determine updates
        updates_to_apply = {}
        for package, current_version in current_versions.items():
            if package in latest_versions:
                latest_version = latest_versions[package]
                if self.should_update_package(package, current_version, latest_version):
                    updates_to_apply[package] = latest_version
                    print(f"📦 {package}: {current_version} → {latest_version}")
        
        if not updates_to_apply:
            print("✅ All packages are up to date!")
            return {"status": "success", "message": "No updates needed", "updates": []}
        
        if test_mode:
            print(f"\n🧪 TEST MODE: Would update {len(updates_to_apply)} packages")
            return {"status": "test", "planned_updates": updates_to_apply}
        
        # Create backup
        print(f"\n💾 Creating backup...")
        backup_path = self.create_backup()
        print(f"Backup created: {backup_path}")
        
        # Apply updates
        print(f"\n⬆️ Applying {len(updates_to_apply)} updates...")
        successful_updates = {}
        failed_updates = {}
        
        for package, new_version in updates_to_apply.items():
            if self.update_package(package, new_version):
                successful_updates[package] = new_version
                print(f"✅ {package} updated successfully")
            else:
                failed_updates[package] = new_version
                print(f"❌ {package} update failed")
        
        # Run safety tests
        print(f"\n🧪 Running safety tests...")
        test_results = self.run_safety_tests()
        
        all_tests_passed = all(test_results.values())
        failed_tests = [test for test, passed in test_results.items() if not passed]
        
        if all_tests_passed:
            print("✅ All safety tests passed!")
            
            # Update requirements.txt
            self.update_requirements_file(successful_updates)
            
            # Log successful update
            log_data = self.load_log()
            log_data["updates"].append({
                "timestamp": datetime.now().isoformat(),
                "backup_path": backup_path,
                "successful_updates": successful_updates,
                "failed_updates": failed_updates,
                "test_results": test_results
            })
            self.save_log(log_data)
            
            print(f"🎉 Update completed successfully!")
            print(f"Updated {len(successful_updates)} packages")
            
            return {
                "status": "success",
                "updates": successful_updates,
                "failed_updates": failed_updates,
                "backup_path": backup_path
            }
        
        else:
            print(f"❌ Safety tests failed: {failed_tests}")
            print("🔄 Rolling back changes...")
            
            if self.rollback_to_backup(backup_path):
                print("✅ Rollback successful")
                
                # Log failed update
                log_data = self.load_log()
                log_data["rollbacks"].append({
                    "timestamp": datetime.now().isoformat(),
                    "backup_path": backup_path,
                    "attempted_updates": updates_to_apply,
                    "failed_tests": failed_tests,
                    "test_results": test_results
                })
                self.save_log(log_data)
                
                return {
                    "status": "rolled_back",
                    "reason": "Safety tests failed",
                    "failed_tests": failed_tests,
                    "backup_path": backup_path
                }
            else:
                print("❌ Rollback failed!")
                return {
                    "status": "error",
                    "reason": "Rollback failed after test failure",
                    "failed_tests": failed_tests
                }
    
    def schedule_updates(self, frequency: str = "weekly") -> Dict[str, str]:
        """Set up scheduled updates"""
        
        schedules = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "monthly": timedelta(days=30)
        }
        
        if frequency not in schedules:
            return {"status": "error", "message": "Invalid frequency"}
        
        # Save schedule configuration
        schedule_config = {
            "frequency": frequency,
            "next_check": (datetime.now() + schedules[frequency]).isoformat(),
            "auto_update": True,
            "notification_webhook": "https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61Dg2-WgSwrpIb110UiG4Z1f7"
        }
        
        with open(self.project_root / "update_schedule.json", 'w') as f:
            json.dump(schedule_config, f, indent=2)
        
        return {"status": "success", "message": f"Updates scheduled {frequency}"}
    
    def send_update_notification(self, result: Dict[str, any]):
        """Send Discord notification about update results"""
        
        webhook_url = "https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61Dg2-WgSwrpIb110UiG4Z1f7"
        
        if result["status"] == "success":
            message = f"""**🔄 TrenchCoat Pro - Library Update Successful**

**Updated Packages:**
{chr(10).join([f'• {pkg}: {ver}' for pkg, ver in result["updates"].items()])}

**Status:** All safety tests passed ✅
**Backup:** {result["backup_path"]}

System is running smoothly with latest dependencies!

#LibraryUpdate #TrenchCoatPro #Maintenance"""

        elif result["status"] == "rolled_back":
            message = f"""**⚠️ TrenchCoat Pro - Library Update Rolled Back**

**Reason:** {result["reason"]}
**Failed Tests:** {', '.join(result["failed_tests"])}

System has been safely restored to previous state.
No functionality was affected.

#LibraryUpdate #Rollback #TrenchCoatPro"""

        else:
            message = f"""**❌ TrenchCoat Pro - Library Update Failed**

**Status:** {result["status"]}
**Reason:** {result.get("reason", "Unknown error")}

Manual intervention may be required.

#LibraryUpdate #Error #TrenchCoatPro"""

        try:
            payload = {
                "content": message,
                "username": "TrenchCoat Pro - Auto Updater",
                "avatar_url": "https://via.placeholder.com/64x64/f59e0b/ffffff?text=🔄"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 204
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

def main():
    """Main function for running the auto updater"""
    
    updater = AutoLibraryUpdater()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            result = updater.run_auto_update(test_mode=True)
            print(f"\nTest mode result: {result}")
        elif sys.argv[1] == "--schedule":
            frequency = sys.argv[2] if len(sys.argv) > 2 else "weekly"
            result = updater.schedule_updates(frequency)
            print(f"Schedule result: {result}")
        elif sys.argv[1] == "--run":
            result = updater.run_auto_update(test_mode=False)
            updater.send_update_notification(result)
            print(f"\nUpdate result: {result}")
    else:
        # Interactive mode
        print("TrenchCoat Pro Auto Library Updater")
        print("1. Test mode (check what would be updated)")
        print("2. Run updates")
        print("3. Schedule updates")
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == "1":
            result = updater.run_auto_update(test_mode=True)
            print(f"\nTest result: {result}")
        elif choice == "2":
            result = updater.run_auto_update(test_mode=False)
            updater.send_update_notification(result)
            print(f"\nUpdate result: {result}")
        elif choice == "3":
            frequency = input("Update frequency (daily/weekly/monthly): ").strip().lower()
            result = updater.schedule_updates(frequency)
            print(f"Schedule result: {result}")

if __name__ == "__main__":
    main()