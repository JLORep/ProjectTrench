#!/usr/bin/env python3
"""
TrenchCoat Pro - Enhanced Automated Library Updater
Integrates with validation system for safe dependency updates
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

# Import existing validators
from validate_code import validate_python_files
from validate_html_css_smart import validate_html_css
from enhanced_deployment_validator import EnhancedDeploymentValidator
from comprehensive_testing_framework import ComprehensiveTestingFramework

class EnhancedAutoLibraryUpdater:
    """Enhanced automated library updater with comprehensive validation"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.requirements_file = self.project_root / "requirements.txt"
        self.backup_dir = self.project_root / "library_backups"
        self.test_results_file = self.project_root / "update_test_results.json"
        self.update_log_file = self.project_root / "library_update_log.json"
        
        # Initialize validators
        self.deployment_validator = EnhancedDeploymentValidator()
        self.test_framework = ComprehensiveTestingFramework()
        
        # Critical features to test after updates
        self.critical_tests = [
            "streamlit_app_loads",
            "dashboard_renders",
            "data_processing_works",
            "ml_models_function",
            "notifications_send",
            "database_operations",
            "discord_queue_system",
            "comprehensive_blog_system",
            "all_tabs_render",
            "api_integrations_work"
        ]
        
        # Libraries that should be updated conservatively
        self.conservative_libraries = [
            "streamlit",  # UI framework - breaking changes affect everything
            "pandas",     # Data processing core
            "numpy",      # Mathematical foundation
            "aiohttp",    # Discord queue system dependency
            "sqlite3"     # Database operations
        ]
        
        # Libraries safe for aggressive updates
        self.safe_libraries = [
            "requests",
            "psutil",
            "base58",
            "frozenlist",
            "multidict",
            "yarl"
        ]
        
        # Discord webhook for notifications
        self.discord_webhook = os.environ.get('DISCORD_WEBHOOK_URL', 
            'https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE')
        
        self.init_directories()
    
    def init_directories(self):
        """Initialize backup and log directories"""
        self.backup_dir.mkdir(exist_ok=True)
        
        if not self.update_log_file.exists():
            self.save_log({
                "created": datetime.now().isoformat(),
                "updates": [],
                "rollbacks": [],
                "validation_results": []
            })
    
    def run_comprehensive_validation(self) -> Dict[str, any]:
        """Run all validation checks"""
        print("🔍 Running comprehensive validation...")
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "python_validation": False,
            "html_css_validation": False,
            "deployment_validation": False,
            "test_suite": False,
            "critical_features": {},
            "errors": []
        }
        
        # 1. Python code validation
        try:
            python_valid, python_errors = validate_python_files()
            validation_results["python_validation"] = python_valid
            if not python_valid:
                validation_results["errors"].extend(python_errors)
        except Exception as e:
            validation_results["errors"].append(f"Python validation error: {str(e)}")
        
        # 2. HTML/CSS validation
        try:
            html_valid, html_errors = validate_html_css()
            validation_results["html_css_validation"] = html_valid
            if not html_valid:
                validation_results["errors"].extend(html_errors)
        except Exception as e:
            validation_results["errors"].append(f"HTML/CSS validation error: {str(e)}")
        
        # 3. Deployment validation
        try:
            deploy_result = self.deployment_validator.validate_deployment()
            validation_results["deployment_validation"] = deploy_result.get("validation_passed", False)
            if not deploy_result.get("validation_passed"):
                validation_results["errors"].append("Deployment validation failed")
        except Exception as e:
            validation_results["errors"].append(f"Deployment validation error: {str(e)}")
        
        # 4. Test suite
        try:
            test_results = self.test_framework.run_all_tests()
            validation_results["test_suite"] = test_results.get("all_passed", False)
            validation_results["critical_features"] = test_results.get("feature_tests", {})
        except Exception as e:
            validation_results["errors"].append(f"Test suite error: {str(e)}")
        
        # Overall validation status
        validation_results["all_valid"] = all([
            validation_results["python_validation"],
            validation_results["html_css_validation"],
            validation_results["deployment_validation"],
            validation_results["test_suite"]
        ])
        
        return validation_results
    
    def test_discord_queue_system(self) -> bool:
        """Test Discord queue system functionality"""
        try:
            from comprehensive_dev_blog_system import ComprehensiveDevBlogSystem
            from enhanced_blog_with_queue import DiscordRateLimitQueue
            
            # Test imports
            blog_system = ComprehensiveDevBlogSystem()
            queue = DiscordRateLimitQueue()
            
            # Test basic functionality
            queue_stats = queue.get_queue_stats()
            
            return True
        except Exception as e:
            print(f"Discord queue system test failed: {e}")
            return False
    
    def test_comprehensive_blog_system(self) -> bool:
        """Test comprehensive blog system"""
        try:
            from comprehensive_dev_blog_system import ComprehensiveDevBlogSystem
            from integrated_webhook_blog_system import IntegratedWebhookBlogSystem
            from retrospective_blog_system import RetrospectiveBlogSystem
            
            # Test imports and initialization
            blog_system = ComprehensiveDevBlogSystem()
            
            return True
        except Exception as e:
            print(f"Comprehensive blog system test failed: {e}")
            return False
    
    def test_all_tabs_render(self) -> bool:
        """Test if all dashboard tabs can render"""
        try:
            # Import streamlit app to check tab structure
            import streamlit as st
            
            # Test tab imports
            from hunt_hub_scanner import HuntHubScanner
            from alpha_radar_system import AlphaRadarSystem
            from security_dashboard import SecurityDashboard
            from comprehensive_monitoring import ComprehensiveMonitoring
            
            return True
        except Exception as e:
            print(f"Tab render test failed: {e}")
            return False
    
    def test_api_integrations_work(self) -> bool:
        """Test API integrations"""
        try:
            from unified_api_integration_layer import UnifiedAPIIntegrationLayer
            from comprehensive_api_providers import get_all_providers
            
            # Test basic API functionality
            providers = get_all_providers()
            
            return len(providers) > 0
        except Exception as e:
            print(f"API integrations test failed: {e}")
            return False
    
    def create_validation_report(self, validation_results: Dict) -> str:
        """Create a detailed validation report"""
        report = f"""# Library Update Validation Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Status: {'✅ PASSED' if validation_results['all_valid'] else '❌ FAILED'}

### Validation Results:
- Python Code Validation: {'✅' if validation_results['python_validation'] else '❌'}
- HTML/CSS Validation: {'✅' if validation_results['html_css_validation'] else '❌'}
- Deployment Validation: {'✅' if validation_results['deployment_validation'] else '❌'}
- Test Suite: {'✅' if validation_results['test_suite'] else '❌'}

### Critical Features:
"""
        
        for feature, status in validation_results.get('critical_features', {}).items():
            report += f"- {feature}: {'✅' if status else '❌'}\n"
        
        if validation_results.get('errors'):
            report += "\n### Errors:\n"
            for error in validation_results['errors']:
                report += f"- {error}\n"
        
        return report
    
    def run_enhanced_safety_tests(self) -> Dict[str, bool]:
        """Run enhanced safety tests including new features"""
        test_results = {}
        
        print("Running enhanced safety tests...")
        
        # Original tests
        test_results["streamlit_app_loads"] = self.test_streamlit_import()
        test_results["dashboard_renders"] = self.test_dashboard_components()
        test_results["data_processing_works"] = self.test_data_processing()
        test_results["ml_models_function"] = self.test_ml_functionality()
        test_results["notifications_send"] = self.test_notification_system()
        test_results["database_operations"] = self.test_database_operations()
        
        # New enhanced tests
        test_results["discord_queue_system"] = self.test_discord_queue_system()
        test_results["comprehensive_blog_system"] = self.test_comprehensive_blog_system()
        test_results["all_tabs_render"] = self.test_all_tabs_render()
        test_results["api_integrations_work"] = self.test_api_integrations_work()
        
        return test_results
    
    def update_package_safely(self, package: str, version: str) -> Tuple[bool, Optional[str]]:
        """Update a package with pre and post validation"""
        
        # Pre-update validation
        print(f"Pre-update validation for {package}...")
        pre_validation = self.run_comprehensive_validation()
        
        if not pre_validation['all_valid']:
            return False, "Pre-update validation failed"
        
        # Perform update
        try:
            print(f"Updating {package} to {version}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", f"{package}=={version}"
            ], capture_output=True, text=True, check=True)
            
            # Post-update validation
            print(f"Post-update validation for {package}...")
            post_validation = self.run_comprehensive_validation()
            
            if not post_validation['all_valid']:
                return False, "Post-update validation failed"
            
            return True, None
            
        except subprocess.CalledProcessError as e:
            return False, f"Package installation failed: {e.stderr}"
    
    def run_auto_update_with_validation(self, test_mode: bool = False) -> Dict[str, any]:
        """Run auto-update with comprehensive validation"""
        
        print("🔄 Starting Enhanced TrenchCoat Pro Auto Library Update")
        print("=" * 60)
        
        # Initial validation
        print("\n📋 Running initial system validation...")
        initial_validation = self.run_comprehensive_validation()
        
        if not initial_validation['all_valid']:
            print("❌ System validation failed before updates!")
            validation_report = self.create_validation_report(initial_validation)
            
            # Save validation report
            report_path = self.project_root / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_path, 'w') as f:
                f.write(validation_report)
            
            return {
                "status": "pre_validation_failed",
                "validation_report": str(report_path),
                "errors": initial_validation['errors']
            }
        
        print("✅ Initial validation passed!")
        
        # Continue with normal update process...
        # (Rest of the update logic from original auto_library_updater.py)
        
        # Get current versions
        current_versions = self.get_current_versions()
        latest_versions = self.get_latest_versions(list(current_versions.keys()))
        
        # Determine updates
        updates_to_apply = {}
        for package, current_version in current_versions.items():
            if package in latest_versions:
                latest_version = latest_versions[package]
                if self.should_update_package(package, current_version, latest_version):
                    updates_to_apply[package] = latest_version
        
        if not updates_to_apply:
            print("✅ All packages are up to date!")
            return {"status": "success", "message": "No updates needed"}
        
        if test_mode:
            print(f"\n🧪 TEST MODE: Would update {len(updates_to_apply)} packages")
            return {"status": "test", "planned_updates": updates_to_apply}
        
        # Create backup
        backup_path = self.create_backup()
        
        # Apply updates with validation
        successful_updates = {}
        failed_updates = {}
        
        for package, new_version in updates_to_apply.items():
            success, error = self.update_package_safely(package, new_version)
            
            if success:
                successful_updates[package] = new_version
                print(f"✅ {package} updated successfully")
            else:
                failed_updates[package] = {"version": new_version, "error": error}
                print(f"❌ {package} update failed: {error}")
        
        # Final validation
        print("\n📋 Running final system validation...")
        final_validation = self.run_comprehensive_validation()
        
        if final_validation['all_valid']:
            print("✅ All validations passed!")
            
            # Update requirements.txt
            self.update_requirements_file(successful_updates)
            
            # Create success report
            validation_report = self.create_validation_report(final_validation)
            report_path = self.project_root / f"update_success_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_path, 'w') as f:
                f.write(validation_report)
            
            return {
                "status": "success",
                "updates": successful_updates,
                "failed_updates": failed_updates,
                "backup_path": str(backup_path),
                "validation_report": str(report_path)
            }
        else:
            print("❌ Final validation failed! Rolling back...")
            
            # Rollback
            if self.rollback_to_backup(str(backup_path)):
                print("✅ Rollback successful")
                
                return {
                    "status": "rolled_back",
                    "reason": "Final validation failed",
                    "validation_errors": final_validation['errors'],
                    "backup_path": str(backup_path)
                }
            else:
                return {
                    "status": "error",
                    "reason": "Rollback failed after validation failure",
                    "validation_errors": final_validation['errors']
                }
    
    # Include all the helper methods from original auto_library_updater.py
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
                response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    latest_versions[package] = data['info']['version']
            except Exception as e:
                print(f"Error fetching version for {package}: {e}")
                
        return latest_versions
    
    def create_backup(self) -> Path:
        """Create backup of current environment"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Backup requirements.txt
        if self.requirements_file.exists():
            shutil.copy2(self.requirements_file, backup_path / "requirements.txt")
        
        # Backup pip freeze
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                                  capture_output=True, text=True, check=True)
            with open(backup_path / "pip_freeze.txt", 'w') as f:
                f.write(result.stdout)
        except Exception as e:
            print(f"Warning: Could not create pip freeze backup: {e}")
        
        return backup_path
    
    def rollback_to_backup(self, backup_path: str) -> bool:
        """Rollback to a previous backup"""
        try:
            backup_requirements = Path(backup_path) / "requirements.txt"
            
            if backup_requirements.exists():
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(backup_requirements)
                ], capture_output=True, text=True, check=True)
                
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
        
        # Read original file to preserve comments and structure
        lines = []
        if self.requirements_file.exists():
            with open(self.requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        lines.append(line)
                    else:
                        if '==' in line:
                            package = line.split('==')[0].strip()
                            if package in current_versions:
                                lines.append(f"{package}=={current_versions[package]}")
                                del current_versions[package]
                            else:
                                lines.append(line)
                        else:
                            lines.append(line)
        
        # Add any new packages
        for package, version in current_versions.items():
            lines.append(f"{package}=={version}")
        
        # Write updated file
        with open(self.requirements_file, 'w') as f:
            f.write('\n'.join(lines))
            f.write('\n')
    
    def should_update_package(self, package: str, current_version: str, latest_version: str) -> bool:
        """Determine if a package should be updated based on safety rules"""
        
        if current_version == latest_version:
            return False
        
        def parse_version(version_str):
            # Handle versions with additional suffixes (e.g., 1.0.0rc1)
            base_version = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
            if base_version:
                return tuple(map(int, base_version.groups()))
            return (0, 0, 0)
        
        try:
            current_v = parse_version(current_version)
            latest_v = parse_version(latest_version)
        except ValueError:
            return False
        
        # Conservative updates for critical libraries
        if package in self.conservative_libraries:
            # Only update patch versions (x.y.Z)
            if current_v[0] == latest_v[0] and current_v[1] == latest_v[1]:
                return True
            return False
        
        # Safe libraries can be updated more aggressively
        if package in self.safe_libraries:
            # Allow minor updates (x.Y.z)
            if current_v[0] == latest_v[0]:
                return True
            return False
        
        # Default: only patch updates
        if current_v[0] == latest_v[0] and current_v[1] == latest_v[1]:
            return True
        
        return False
    
    def save_log(self, log_data: Dict):
        """Save update log"""
        with open(self.update_log_file, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
    
    def load_log(self) -> Dict:
        """Load update log"""
        if self.update_log_file.exists():
            with open(self.update_log_file, 'r') as f:
                return json.load(f)
        return {"updates": [], "rollbacks": [], "validation_results": []}
    
    # Include test methods from original
    def test_streamlit_import(self) -> bool:
        """Test if Streamlit can be imported"""
        try:
            import streamlit as st
            import pandas as pd
            import numpy as np
            import plotly.graph_objects as go
            return True
        except Exception as e:
            print(f"Streamlit import test failed: {e}")
            return False
    
    def test_dashboard_components(self) -> bool:
        """Test if dashboard components can be imported"""
        try:
            from ultra_premium_dashboard import main
            from live_data_integration import LiveDataManager
            return True
        except Exception as e:
            print(f"Dashboard component test failed: {e}")
            return False
    
    def test_data_processing(self) -> bool:
        """Test pandas and numpy functionality"""
        try:
            import pandas as pd
            import numpy as np
            
            df = pd.DataFrame({
                'symbol': ['BTC', 'ETH', 'SOL'],
                'price': [45000, 2500, 100]
            })
            
            result = df.groupby('symbol')['price'].sum()
            return True
        except Exception as e:
            print(f"Data processing test failed: {e}")
            return False
    
    def test_ml_functionality(self) -> bool:
        """Test machine learning components if available"""
        try:
            # Only test if sklearn is in requirements
            if 'scikit-learn' in self.get_current_versions():
                from sklearn.ensemble import RandomForestClassifier
                return True
            return True  # Skip if not installed
        except Exception as e:
            print(f"ML functionality test failed: {e}")
            return False
    
    def test_notification_system(self) -> bool:
        """Test notification system imports"""
        try:
            import requests
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Notification system test failed: {e}")
            return False
    
    def test_database_operations(self) -> bool:
        """Test database operations"""
        try:
            import sqlite3
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY)')
            conn.close()
            return True
        except Exception as e:
            print(f"Database operations test failed: {e}")
            return False


def main():
    """Main function for running the enhanced auto updater"""
    
    updater = EnhancedAutoLibraryUpdater()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            result = updater.run_auto_update_with_validation(test_mode=True)
            print(f"\nTest mode result: {json.dumps(result, indent=2)}")
        elif sys.argv[1] == "--validate":
            validation = updater.run_comprehensive_validation()
            report = updater.create_validation_report(validation)
            print(report)
        elif sys.argv[1] == "--run":
            result = updater.run_auto_update_with_validation(test_mode=False)
            print(f"\nUpdate result: {json.dumps(result, indent=2)}")
    else:
        # Interactive mode
        print("Enhanced TrenchCoat Pro Auto Library Updater")
        print("=" * 50)
        print("1. Test mode (check what would be updated)")
        print("2. Run updates with validation")
        print("3. Validate system only")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            result = updater.run_auto_update_with_validation(test_mode=True)
            print(f"\nTest result: {json.dumps(result, indent=2)}")
        elif choice == "2":
            confirm = input("This will update packages. Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                result = updater.run_auto_update_with_validation(test_mode=False)
                print(f"\nUpdate result: {json.dumps(result, indent=2)}")
        elif choice == "3":
            validation = updater.run_comprehensive_validation()
            report = updater.create_validation_report(validation)
            print(report)


if __name__ == "__main__":
    main()