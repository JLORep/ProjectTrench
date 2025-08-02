#!/usr/bin/env python3
"""
TrenchCoat Pro - Auto Deploy with Library Updates
Integrates library updates into the deployment pipeline
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path
from enhanced_auto_library_updater import EnhancedAutoLibraryUpdater

class AutoDeployWithLibraryUpdates:
    """Enhanced deployment system with automatic library updates"""
    
    def __init__(self):
        self.updater = EnhancedAutoLibraryUpdater()
        self.deployment_log = []
        
    def log(self, message: str):
        """Log deployment messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def check_for_library_updates(self) -> Dict[str, any]:
        """Check if any library updates are available"""
        self.log("🔍 Checking for library updates...")
        
        current_versions = self.updater.get_current_versions()
        latest_versions = self.updater.get_latest_versions(list(current_versions.keys()))
        
        updates_available = {}
        for package, current_version in current_versions.items():
            if package in latest_versions:
                latest_version = latest_versions[package]
                if self.updater.should_update_package(package, current_version, latest_version):
                    updates_available[package] = {
                        "current": current_version,
                        "latest": latest_version
                    }
        
        return updates_available
    
    def run_pre_deployment_updates(self) -> bool:
        """Run library updates before deployment"""
        self.log("📦 Running pre-deployment library update check...")
        
        # Check for updates
        updates = self.check_for_library_updates()
        
        if not updates:
            self.log("✅ All libraries are up to date")
            return True
        
        self.log(f"📋 Found {len(updates)} available updates:")
        for package, versions in updates.items():
            self.log(f"  - {package}: {versions['current']} → {versions['latest']}")
        
        # Run updates with validation
        self.log("🔄 Applying updates with validation...")
        result = self.updater.run_auto_update_with_validation(test_mode=False)
        
        if result["status"] == "success":
            self.log("✅ Library updates completed successfully")
            self.log(f"📄 Validation report: {result.get('validation_report', 'N/A')}")
            return True
        elif result["status"] == "rolled_back":
            self.log("⚠️ Updates rolled back due to validation failure")
            self.log(f"❌ Errors: {result.get('validation_errors', [])}")
            return False
        else:
            self.log(f"❌ Update failed: {result.get('reason', 'Unknown')}")
            return False
    
    def run_deployment_pipeline(self):
        """Run the complete deployment pipeline with library updates"""
        self.log("🚀 Starting Enhanced Deployment Pipeline")
        self.log("=" * 50)
        
        try:
            # Step 1: Run library updates
            if not self.run_pre_deployment_updates():
                self.log("❌ Deployment aborted due to library update failure")
                return False
            
            # Step 2: Run standard deployment
            self.log("\n📤 Running standard deployment...")
            
            # Git add and commit
            subprocess.run(["git", "add", "-A"], check=True)
            
            commit_result = subprocess.run([
                "git", "commit", "-m", 
                f"Auto-deploy with library updates - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ], capture_output=True, text=True)
            
            if commit_result.returncode == 0:
                self.log("✅ Changes committed")
            else:
                self.log("ℹ️ No changes to commit")
            
            # Git push
            push_result = subprocess.run(["git", "push"], capture_output=True, text=True, check=True)
            self.log("✅ Pushed to GitHub")
            
            # Step 3: Run deployment validation
            self.log("\n🔍 Running post-deployment validation...")
            
            from enhanced_deployment_validator import EnhancedDeploymentValidator
            validator = EnhancedDeploymentValidator()
            validation_result = validator.validate_deployment()
            
            if validation_result.get("validation_passed"):
                self.log("✅ Deployment validation passed")
                self.log("🎉 Deployment completed successfully!")
                return True
            else:
                self.log("❌ Deployment validation failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Deployment error: {str(e)}")
            return False
    
    def save_deployment_log(self):
        """Save deployment log to file"""
        log_file = Path("deployment_logs") / f"deploy_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.deployment_log))
        
        self.log(f"📝 Deployment log saved to: {log_file}")


def integrate_with_hooks():
    """Integrate library updates with git hooks"""
    
    # Create pre-push hook
    pre_push_hook = """#!/usr/bin/env python3
# TrenchCoat Pro - Pre-push library update check

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from enhanced_auto_library_updater import EnhancedAutoLibraryUpdater

def main():
    updater = EnhancedAutoLibraryUpdater()
    
    # Check for updates
    current = updater.get_current_versions()
    latest = updater.get_latest_versions(list(current.keys()))
    
    updates = {}
    for pkg, curr_ver in current.items():
        if pkg in latest and updater.should_update_package(pkg, curr_ver, latest[pkg]):
            updates[pkg] = {"current": curr_ver, "latest": latest[pkg]}
    
    if updates:
        print("⚠️  Library updates available:")
        for pkg, vers in updates.items():
            print(f"   {pkg}: {vers['current']} → {vers['latest']}")
        print("\\nRun 'python enhanced_auto_library_updater.py' to update before pushing")
        print("Or use --no-verify to skip this check")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    
    # Save pre-push hook
    hook_path = Path(".git/hooks/pre-push")
    hook_path.parent.mkdir(exist_ok=True)
    
    with open(hook_path, 'w') as f:
        f.write(pre_push_hook)
    
    # Make executable on Unix-like systems
    try:
        import os
        os.chmod(hook_path, 0o755)
    except:
        pass
    
    print("✅ Pre-push hook installed")


def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install-hooks":
            integrate_with_hooks()
        elif sys.argv[1] == "--check-updates":
            deployer = AutoDeployWithLibraryUpdates()
            updates = deployer.check_for_library_updates()
            if updates:
                print(f"Found {len(updates)} updates available")
                print(json.dumps(updates, indent=2))
            else:
                print("All libraries are up to date")
        elif sys.argv[1] == "--deploy":
            deployer = AutoDeployWithLibraryUpdates()
            success = deployer.run_deployment_pipeline()
            deployer.save_deployment_log()
            sys.exit(0 if success else 1)
    else:
        print("Auto Deploy with Library Updates")
        print("=" * 40)
        print("Usage:")
        print("  --check-updates   Check for library updates")
        print("  --deploy         Run full deployment with updates")
        print("  --install-hooks  Install git hooks")


if __name__ == "__main__":
    main()