#!/usr/bin/env python3
"""
TrenchCoat Pro - Poetry-Integrated Dependency Manager
Modern dependency management with Poetry integration and automated updates
"""

import subprocess
import json
import os
import shutil
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import requests
import re
from pathlib import Path
import toml
import tempfile

class PoetryIntegratedUpdater:
    """Modern dependency manager with Poetry integration"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.pyproject_file = self.project_root / "pyproject.toml"
        self.requirements_file = self.project_root / "requirements.txt"
        self.poetry_lock = self.project_root / "poetry.lock"
        self.backup_dir = self.project_root / "library_backups"
        self.test_results_file = self.project_root / "update_test_results.json"
        self.update_log_file = self.project_root / "library_update_log.json"
        
        # Check if Poetry is available
        self.poetry_available = self.check_poetry_installed()
        
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
            "plotly"      # Visualization core
        ]
        
        # Libraries safe for aggressive updates
        self.safe_libraries = [
            "requests",
            "aiohttp", 
            "psutil",
            "base58",
            "loguru"
        ]
        
        self.init_directories()
    
    def check_poetry_installed(self) -> bool:
        """Check if Poetry is installed and available"""
        try:
            result = subprocess.run(["poetry", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Poetry detected: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Poetry not installed. Using pip-based management.")
            return False
    
    def install_poetry(self) -> bool:
        """Install Poetry if not already installed"""
        if self.poetry_available:
            return True
            
        print("📦 Installing Poetry...")
        try:
            # Install using pip
            subprocess.run([sys.executable, "-m", "pip", "install", "poetry"],
                         check=True, capture_output=True)
            self.poetry_available = True
            print("✅ Poetry installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Poetry: {e}")
            return False
    
    def init_directories(self):
        """Initialize backup and log directories"""
        self.backup_dir.mkdir(exist_ok=True)
        
        if not self.update_log_file.exists():
            self.save_log({
                "created": datetime.now().isoformat(),
                "updates": [],
                "rollbacks": []
            })
    
    def migrate_to_poetry(self) -> bool:
        """Migrate from requirements.txt to Poetry if pyproject.toml doesn't exist"""
        if self.pyproject_file.exists():
            print("✅ pyproject.toml already exists")
            return True
            
        if not self.requirements_file.exists():
            print("❌ No requirements.txt found to migrate")
            return False
            
        print("🔄 Migrating to Poetry...")
        
        # Parse requirements.txt
        dependencies = {}
        with open(self.requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' in line:
                        package, version = line.split('==')
                        dependencies[package.strip()] = f"^{version.strip()}"
        
        # Create pyproject.toml
        pyproject_content = {
            "tool": {
                "poetry": {
                    "name": "trenchcoat-pro",
                    "version": "2.3.0",
                    "description": "Ultra-premium cryptocurrency trading intelligence platform",
                    "authors": ["TrenchCoat Pro Team <admin@trenchcoat.pro>"],
                    "readme": "README.md",
                    "homepage": "https://trenchcoat.pro",
                    "repository": "https://github.com/JLORep/ProjectTrench",
                    "keywords": ["cryptocurrency", "trading", "solana", "defi", "memecoin"],
                    "dependencies": {
                        "python": "^3.9",
                        **dependencies
                    },
                    "group": {
                        "dev": {
                            "dependencies": {
                                "pytest": "^7.4.0",
                                "black": "^23.7.0",
                                "flake8": "^6.1.0",
                                "mypy": "^1.5.0",
                                "pre-commit": "^3.3.3"
                            }
                        }
                    }
                },
                "build-system": {
                    "requires": ["poetry-core"],
                    "build-backend": "poetry.core.masonry.api"
                }
            }
        }
        
        with open(self.pyproject_file, 'w') as f:
            toml.dump(pyproject_content, f)
        
        print("✅ Created pyproject.toml")
        
        # Initialize Poetry environment
        if self.poetry_available:
            try:
                subprocess.run(["poetry", "install"], check=True)
                print("✅ Poetry environment initialized")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to initialize Poetry: {e}")
                return False
        
        return True
    
    def sync_requirements_with_poetry(self):
        """Keep requirements.txt in sync with Poetry for backward compatibility"""
        if not self.poetry_available or not self.pyproject_file.exists():
            return
            
        print("📝 Syncing requirements.txt with Poetry...")
        try:
            # Export from Poetry to requirements.txt
            result = subprocess.run(
                ["poetry", "export", "-f", "requirements.txt", "--without-hashes"],
                capture_output=True, text=True, check=True
            )
            
            # Clean up the output (remove extras and comments)
            lines = []
            for line in result.stdout.strip().split('\n'):
                if line and not line.startswith('#'):
                    # Remove any extras like package[extra]==version
                    line = re.sub(r'\[.*?\]', '', line)
                    lines.append(line)
            
            with open(self.requirements_file, 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ requirements.txt synced with Poetry")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to sync requirements.txt: {e}")
    
    def get_current_versions(self) -> Dict[str, str]:
        """Get currently installed package versions from Poetry or requirements.txt"""
        current_versions = {}
        
        if self.poetry_available and self.pyproject_file.exists():
            # Get from Poetry
            try:
                result = subprocess.run(
                    ["poetry", "show", "--no-dev"],
                    capture_output=True, text=True, check=True
                )
                
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 2:
                        package = parts[0]
                        version = parts[1]
                        current_versions[package] = version
                        
            except subprocess.CalledProcessError:
                pass
        
        # Fallback to requirements.txt
        if not current_versions and self.requirements_file.exists():
            with open(self.requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '==' in line:
                            package, version = line.split('==')
                            current_versions[package.strip()] = version.strip()
        
        return current_versions
    
    def get_outdated_packages(self) -> Dict[str, Dict[str, str]]:
        """Get outdated packages using Poetry or pip"""
        outdated = {}
        
        if self.poetry_available and self.pyproject_file.exists():
            try:
                # Use Poetry to check outdated packages
                result = subprocess.run(
                    ["poetry", "show", "--outdated"],
                    capture_output=True, text=True, check=True
                )
                
                for line in result.stdout.strip().split('\n'):
                    if '→' in line:  # Poetry uses → to show version updates
                        parts = line.split()
                        package = parts[0]
                        current = parts[1]
                        latest = parts[3]  # Skip the arrow
                        outdated[package] = {
                            "current": current,
                            "latest": latest
                        }
                        
            except subprocess.CalledProcessError:
                pass
        
        # Fallback to pip
        if not outdated:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                    capture_output=True, text=True, check=True
                )
                
                packages = json.loads(result.stdout)
                for pkg in packages:
                    outdated[pkg["name"]] = {
                        "current": pkg["version"],
                        "latest": pkg["latest_version"]
                    }
                    
            except subprocess.CalledProcessError:
                pass
        
        return outdated
    
    def create_backup(self) -> str:
        """Create backup of current environment"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Backup pyproject.toml if exists
        if self.pyproject_file.exists():
            shutil.copy2(self.pyproject_file, backup_path / "pyproject.toml")
        
        # Backup poetry.lock if exists
        if self.poetry_lock.exists():
            shutil.copy2(self.poetry_lock, backup_path / "poetry.lock")
        
        # Backup requirements.txt
        if self.requirements_file.exists():
            shutil.copy2(self.requirements_file, backup_path / "requirements.txt")
        
        # Backup pip freeze
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                                  capture_output=True, text=True, check=True)
            with open(backup_path / "pip_freeze.txt", 'w') as f:
                f.write(result.stdout)
        except subprocess.CalledProcessError:
            pass
        
        return str(backup_path)
    
    def update_package(self, package: str, version: str = None) -> bool:
        """Update a package using Poetry or pip"""
        try:
            if self.poetry_available and self.pyproject_file.exists():
                # Update using Poetry
                if version:
                    cmd = ["poetry", "add", f"{package}@{version}"]
                else:
                    cmd = ["poetry", "add", f"{package}@latest"]
                
                print(f"🔄 Updating {package} using Poetry...")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                # Sync requirements.txt
                self.sync_requirements_with_poetry()
                
            else:
                # Update using pip
                if version:
                    cmd = [sys.executable, "-m", "pip", "install", f"{package}=={version}"]
                else:
                    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package]
                
                print(f"🔄 Updating {package} using pip...")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to update {package}: {e}")
            return False
    
    def rollback_to_backup(self, backup_path: str) -> bool:
        """Rollback to a previous backup"""
        try:
            print(f"🔄 Rolling back to backup: {backup_path}")
            backup_path = Path(backup_path)
            
            # Restore files
            for file_name in ["pyproject.toml", "poetry.lock", "requirements.txt"]:
                backup_file = backup_path / file_name
                if backup_file.exists():
                    shutil.copy2(backup_file, self.project_root / file_name)
            
            # Reinstall dependencies
            if self.poetry_available and (backup_path / "pyproject.toml").exists():
                subprocess.run(["poetry", "install"], check=True)
            elif (backup_path / "requirements.txt").exists():
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", 
                    str(backup_path / "requirements.txt")
                ], check=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def run_safety_tests(self) -> Dict[str, bool]:
        """Run safety tests - reuse from original updater"""
        test_results = {}
        
        # Import tests from the original auto_library_updater
        try:
            from auto_library_updater import AutoLibraryUpdater
            original_updater = AutoLibraryUpdater()
            test_results = original_updater.run_safety_tests()
        except ImportError:
            # Run basic tests if original updater not available
            test_results["basic_imports"] = self.test_basic_imports()
        
        return test_results
    
    def test_basic_imports(self) -> bool:
        """Basic import test"""
        try:
            import streamlit
            import pandas
            import numpy
            import plotly
            import loguru
            return True
        except ImportError:
            return False
    
    def should_update_package(self, package: str, current_version: str, latest_version: str) -> bool:
        """Determine if a package should be updated based on safety rules"""
        
        # Skip if versions are the same
        if current_version == latest_version:
            return False
        
        # Parse semantic versions
        def parse_version(version_str):
            # Handle versions with pre-release tags
            version_str = re.split(r'[a-zA-Z]', version_str)[0]
            parts = version_str.split('.')
            return tuple(int(p) for p in parts if p.isdigit())
        
        try:
            current_v = parse_version(current_version)
            latest_v = parse_version(latest_version)
        except (ValueError, IndexError):
            print(f"⚠️  Could not parse versions for {package}")
            return False
        
        # Conservative updates for critical libraries
        if package in self.conservative_libraries:
            # Only update patch versions (x.y.Z)
            if len(current_v) >= 2 and len(latest_v) >= 2:
                if current_v[0] == latest_v[0] and current_v[1] == latest_v[1]:
                    return True
            return False
        
        # Safe libraries can be updated more aggressively
        if package in self.safe_libraries:
            # Allow minor updates (x.Y.z)
            if len(current_v) >= 1 and len(latest_v) >= 1:
                if current_v[0] == latest_v[0]:
                    return True
            return False
        
        # Default: only patch updates
        if len(current_v) >= 2 and len(latest_v) >= 2:
            if current_v[0] == latest_v[0] and current_v[1] == latest_v[1]:
                return True
        
        return False
    
    def run_auto_update(self, test_mode: bool = False) -> Dict[str, any]:
        """Run the complete auto-update process with Poetry integration"""
        
        print("🚀 TrenchCoat Pro Poetry-Integrated Dependency Update")
        print("=" * 60)
        
        # Ensure Poetry is available or migrate
        if not self.poetry_available:
            print("📦 Poetry not found. Would you like to install it? (recommended)")
            if input("Install Poetry? (y/n): ").lower() == 'y':
                if self.install_poetry():
                    self.migrate_to_poetry()
        
        # Get outdated packages
        print("\n🔍 Checking for outdated packages...")
        outdated_packages = self.get_outdated_packages()
        
        if not outdated_packages:
            print("✅ All packages are up to date!")
            return {"status": "success", "message": "No updates needed", "updates": []}
        
        # Determine safe updates
        updates_to_apply = {}
        for package, versions in outdated_packages.items():
            if self.should_update_package(package, versions["current"], versions["latest"]):
                updates_to_apply[package] = versions["latest"]
                print(f"📦 {package}: {versions['current']} → {versions['latest']}")
        
        if not updates_to_apply:
            print("✅ No safe updates available")
            return {"status": "success", "message": "No safe updates available", "updates": []}
        
        if test_mode:
            print(f"\n🧪 TEST MODE: Would update {len(updates_to_apply)} packages")
            return {"status": "test", "planned_updates": updates_to_apply}
        
        # Create backup
        print(f"\n💾 Creating backup...")
        backup_path = self.create_backup()
        print(f"✅ Backup created: {backup_path}")
        
        # Apply updates
        print(f"\n⬆️  Applying {len(updates_to_apply)} updates...")
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
        
        if all_tests_passed:
            print("✅ All safety tests passed!")
            
            # Log successful update
            log_data = self.load_log()
            log_data["updates"].append({
                "timestamp": datetime.now().isoformat(),
                "backup_path": backup_path,
                "successful_updates": successful_updates,
                "failed_updates": failed_updates,
                "test_results": test_results,
                "used_poetry": self.poetry_available
            })
            self.save_log(log_data)
            
            return {
                "status": "success",
                "updates": successful_updates,
                "failed_updates": failed_updates,
                "backup_path": backup_path,
                "used_poetry": self.poetry_available
            }
        
        else:
            print(f"❌ Safety tests failed!")
            print("🔄 Rolling back changes...")
            
            if self.rollback_to_backup(backup_path):
                print("✅ Rollback successful")
                
                return {
                    "status": "rolled_back",
                    "reason": "Safety tests failed",
                    "backup_path": backup_path
                }
            else:
                return {
                    "status": "error",
                    "reason": "Rollback failed after test failure"
                }
    
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
    
    def export_requirements(self, include_dev: bool = False) -> bool:
        """Export current dependencies to various formats"""
        print("📄 Exporting dependencies...")
        
        try:
            # Export to requirements.txt
            if self.poetry_available and self.pyproject_file.exists():
                cmd = ["poetry", "export", "-f", "requirements.txt", "--without-hashes"]
                if not include_dev:
                    cmd.append("--without-dev")
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                with open(self.requirements_file, 'w') as f:
                    f.write(result.stdout)
                
                print("✅ Exported to requirements.txt")
            
            # Export to requirements-dev.txt if including dev
            if include_dev and self.poetry_available:
                cmd = ["poetry", "export", "-f", "requirements.txt", "--without-hashes", "--dev"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                with open(self.project_root / "requirements-dev.txt", 'w') as f:
                    f.write(result.stdout)
                
                print("✅ Exported to requirements-dev.txt")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Export failed: {e}")
            return False


def main():
    """Main function for running the Poetry-integrated updater"""
    
    updater = PoetryIntegratedUpdater()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            result = updater.run_auto_update(test_mode=True)
            print(f"\nTest mode result: {result}")
        elif sys.argv[1] == "--migrate":
            updater.migrate_to_poetry()
        elif sys.argv[1] == "--export":
            include_dev = "--dev" in sys.argv
            updater.export_requirements(include_dev=include_dev)
        elif sys.argv[1] == "--run":
            result = updater.run_auto_update(test_mode=False)
            print(f"\nUpdate result: {result}")
    else:
        # Interactive mode
        print("TrenchCoat Pro Poetry-Integrated Dependency Manager")
        print("1. Test mode (check what would be updated)")
        print("2. Run updates")
        print("3. Migrate to Poetry")
        print("4. Export requirements")
        print("5. Sync requirements.txt with Poetry")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            result = updater.run_auto_update(test_mode=True)
            print(f"\nTest result: {result}")
        elif choice == "2":
            result = updater.run_auto_update(test_mode=False)
            print(f"\nUpdate result: {result}")
        elif choice == "3":
            updater.migrate_to_poetry()
        elif choice == "4":
            include_dev = input("Include dev dependencies? (y/n): ").lower() == 'y'
            updater.export_requirements(include_dev=include_dev)
        elif choice == "5":
            updater.sync_requirements_with_poetry()


if __name__ == "__main__":
    main()