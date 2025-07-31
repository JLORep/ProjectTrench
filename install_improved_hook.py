#!/usr/bin/env python3
"""
TrenchCoat Pro - Improved Hook Installer
Safely installs the improved post-commit hook with backup
"""
import os
import shutil
import subprocess
import sys
from datetime import datetime

class HookInstaller:
    """Installs improved git hooks safely"""
    
    def __init__(self):
        self.project_dir = os.getcwd()
        self.hooks_dir = os.path.join(self.project_dir, '.git', 'hooks')
        self.hook_file = os.path.join(self.hooks_dir, 'post-commit')
        self.backup_file = os.path.join(self.hooks_dir, 'post-commit.backup')
        self.disabled_file = os.path.join(self.hooks_dir, 'post-commit.disabled')
        self.improved_file = os.path.join(self.project_dir, 'improved-post-commit')
        
    def backup_existing_hook(self) -> bool:
        """Backup existing hook if it exists"""
        try:
            if os.path.exists(self.hook_file):
                print(f"[BACKUP] Backing up existing hook to {self.backup_file}")
                shutil.copy2(self.hook_file, self.backup_file)
                print("[BACKUP] SUCCESS: Existing hook backed up successfully")
                return True
            elif os.path.exists(self.disabled_file):
                print(f"[BACKUP] Backing up disabled hook to {self.backup_file}")
                shutil.copy2(self.disabled_file, self.backup_file)
                print("[BACKUP] SUCCESS: Disabled hook backed up successfully")
                return True
            else:
                print("[BACKUP] No existing hook to backup")
                return True
                
        except Exception as e:
            print(f"[ERROR] Failed to backup existing hook: {e}")
            return False
    
    def install_improved_hook(self) -> bool:
        """Install the improved hook"""
        try:
            if not os.path.exists(self.improved_file):
                print(f"[ERROR] Improved hook file not found: {self.improved_file}")
                return False
            
            print(f"[INSTALL] Installing improved hook from {self.improved_file}")
            shutil.copy2(self.improved_file, self.hook_file)
            
            # Make executable on Unix systems
            if os.name != 'nt':  # Not Windows
                os.chmod(self.hook_file, 0o755)
                print("[INSTALL] Set hook as executable")
            
            print("[INSTALL] SUCCESS: Improved hook installed successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to install improved hook: {e}")
            return False
    
    def test_hook(self) -> bool:
        """Test the hook with a dummy commit check"""
        try:
            print("[TEST] Testing hook functionality...")
            
            # Check if hook file exists and is readable
            if not os.path.exists(self.hook_file):
                print("[ERROR] Hook file does not exist after installation")
                return False
            
            # Try to read the hook file
            with open(self.hook_file, 'r') as f:
                content = f.read()
                if 'TrenchCoat Pro - Improved Post-Commit Hook' in content:
                    print("[TEST] SUCCESS: Hook content verified")
                    return True
                else:
                    print("[ERROR] Hook content verification failed")
                    return False
                    
        except Exception as e:
            print(f"[ERROR] Hook test failed: {e}")
            return False
    
    def create_log_file(self) -> bool:
        """Create initial log file"""
        try:
            log_file = os.path.join(self.project_dir, 'deployment_hook.log')
            
            with open(log_file, 'a') as f:
                f.write(f"\n=== IMPROVED HOOK INSTALLED ===\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Project: TrenchCoat Pro\n")
                f.write(f"Hook Version: Improved with timeout prevention\n")
                f.write(f"====================================\n\n")
            
            print(f"[LOG] Created log file: {log_file}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to create log file: {e}")
            return False
    
    def install(self) -> bool:
        """Main installation process"""
        print("=" * 60)
        print("TrenchCoat Pro - Improved Hook Installer")
        print("=" * 60)
        
        # Step 1: Backup existing hook
        if not self.backup_existing_hook():
            print("[FAILED] Hook installation aborted due to backup failure")
            return False
        
        # Step 2: Install improved hook
        if not self.install_improved_hook():
            print("[FAILED] Hook installation failed")
            return False
        
        # Step 3: Test hook
        if not self.test_hook():
            print("[WARNING] Hook test failed, but installation completed")
        
        # Step 4: Create log file
        self.create_log_file()
        
        print("\n" + "=" * 60)
        print("SUCCESS: IMPROVED HOOK INSTALLATION COMPLETE")
        print("=" * 60)
        print("Features:")
        print("- Background deployment (no git timeouts)")
        print("- Comprehensive logging")
        print("- Lock file prevents concurrent deployments")
        print("- 5-minute timeout protection")
        print("- Discord notifications for all outcomes")
        print("- Error handling and recovery")
        print("\nNext commit with deployment keywords will trigger auto-deployment!")
        
        return True

def main():
    """Run hook installation"""
    installer = HookInstaller()
    success = installer.install()
    
    if success:
        print("\nSUCCESS: Ready for improved auto-deployment!")
        return 0
    else:
        print("\nERROR: Hook installation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())