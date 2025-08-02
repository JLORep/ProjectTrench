#!/usr/bin/env python3
"""
Git Hygiene Manager - Safe periodic garbage collection and repository maintenance
"""

import subprocess
import os
import sys
import shutil
import time
from datetime import datetime, timedelta
import json

class GitHygieneManager:
    def __init__(self):
        self.log_file = "git_hygiene.log"
        self.state_file = ".git_hygiene_state.json"
        self.backup_dir = ".git_backups"
        
    def log(self, message, level="INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def load_state(self):
        """Load hygiene state"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "last_gc": None,
            "gc_count": 0,
            "last_backup": None,
            "errors_fixed": 0
        }
    
    def save_state(self, state):
        """Save hygiene state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def run_command(self, cmd, timeout=300):
        """Run command with timeout"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def backup_git_dir(self):
        """Create backup of .git directory"""
        self.log("📦 Creating backup of .git directory...")
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        backup_name = f"git_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Use robocopy on Windows for better performance
            if sys.platform == 'win32':
                cmd = f'robocopy .git "{backup_path}" /E /MT:8 /R:1 /W:1 /NFL /NDL /NJH /NJS'
                success, _, _ = self.run_command(cmd)
                if success or "ERROR" not in _:  # robocopy returns non-zero for success
                    self.log(f"✅ Backup created: {backup_path}")
                    return True
            else:
                shutil.copytree('.git', backup_path)
                self.log(f"✅ Backup created: {backup_path}")
                return True
        except Exception as e:
            self.log(f"⚠️  Backup failed: {e}", "WARNING")
            return False
        
        return False
    
    def check_repository_health(self):
        """Check repository health"""
        self.log("🏥 Checking repository health...")
        
        issues = []
        
        # Check for corrupted objects
        success, stdout, stderr = self.run_command("git fsck --no-reflogs")
        if not success:
            if "unable to read" in stderr or "missing blob" in stderr:
                issues.append("corrupted_objects")
                self.log("❌ Found corrupted objects", "ERROR")
        else:
            self.log("✅ No corrupted objects found")
        
        # Check repository size
        success, stdout, _ = self.run_command("git count-objects -v")
        if success:
            for line in stdout.split('\n'):
                if "size-pack:" in line:
                    size_kb = int(line.split(':')[1].strip())
                    size_mb = size_kb / 1024
                    self.log(f"📊 Repository size: {size_mb:.2f} MB")
                    if size_mb > 500:  # If repo > 500MB
                        issues.append("large_repo")
        
        # Check for too many loose objects
        success, stdout, _ = self.run_command("git count-objects")
        if success:
            loose_count = int(stdout.split()[0])
            self.log(f"📊 Loose objects: {loose_count}")
            if loose_count > 1000:
                issues.append("too_many_loose")
        
        return issues
    
    def fix_corrupted_objects(self):
        """Fix corrupted objects"""
        self.log("🔧 Attempting to fix corrupted objects...")
        
        # Get list of corrupted objects
        success, stdout, stderr = self.run_command("git fsck --no-reflogs")
        
        fixed_count = 0
        if not success:
            # Extract corrupted object IDs
            import re
            pattern = r'unable to read ([0-9a-f]{40})'
            corrupted_ids = re.findall(pattern, stderr)
            
            for obj_id in corrupted_ids:
                # Try to remove corrupted object
                obj_path = os.path.join('.git', 'objects', obj_id[:2], obj_id[2:])
                if os.path.exists(obj_path):
                    try:
                        os.remove(obj_path)
                        self.log(f"✅ Removed corrupted object: {obj_id}")
                        fixed_count += 1
                    except Exception as e:
                        self.log(f"⚠️  Could not remove {obj_id}: {e}", "WARNING")
        
        return fixed_count
    
    def perform_safe_gc(self):
        """Perform safe garbage collection"""
        self.log("♻️  Starting safe garbage collection...")
        
        # Step 1: Prune unreachable objects older than 2 weeks
        self.log("🗑️  Pruning old objects...")
        success, _, _ = self.run_command("git prune --expire=2.weeks.ago")
        if success:
            self.log("✅ Pruned old objects")
        
        # Step 2: Repack with safe options
        self.log("📦 Repacking repository...")
        success, _, _ = self.run_command("git repack -a -d -f --depth=20 --window=100")
        if success:
            self.log("✅ Repository repacked")
        
        # Step 3: Clean reflog
        self.log("📋 Cleaning reflog...")
        success, _, _ = self.run_command("git reflog expire --expire=30.days --all")
        if success:
            self.log("✅ Reflog cleaned")
        
        # Step 4: Final gc with safe options
        self.log("🧹 Running final cleanup...")
        success, _, _ = self.run_command("git gc --aggressive --prune=now")
        if success:
            self.log("✅ Garbage collection complete")
            return True
        
        return False
    
    def clean_old_backups(self, keep_days=7):
        """Clean old backups"""
        if not os.path.exists(self.backup_dir):
            return
        
        self.log(f"🗑️  Cleaning backups older than {keep_days} days...")
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        cleaned = 0
        
        for backup in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup)
            if os.path.isdir(backup_path):
                # Extract date from backup name
                try:
                    date_str = backup.split('_')[2] + backup.split('_')[3]
                    backup_date = datetime.strptime(date_str, '%Y%m%d%H%M%S')
                    
                    if backup_date < cutoff_date:
                        shutil.rmtree(backup_path)
                        cleaned += 1
                except:
                    pass
        
        if cleaned > 0:
            self.log(f"✅ Cleaned {cleaned} old backups")
    
    def run_hygiene(self, force=False):
        """Run complete hygiene routine"""
        self.log("🚀 Starting Git Hygiene Manager")
        
        state = self.load_state()
        
        # Check if it's time for maintenance (every 3 days)
        if not force and state["last_gc"]:
            last_gc = datetime.fromisoformat(state["last_gc"])
            if datetime.now() - last_gc < timedelta(days=3):
                self.log("ℹ️  Skipping - last GC was less than 3 days ago")
                return
        
        # Check repository health
        issues = self.check_repository_health()
        
        if issues or force:
            # Create backup first
            if self.backup_git_dir():
                state["last_backup"] = datetime.now().isoformat()
                
                # Fix corrupted objects if needed
                if "corrupted_objects" in issues:
                    fixed = self.fix_corrupted_objects()
                    state["errors_fixed"] += fixed
                
                # Perform safe GC
                if self.perform_safe_gc():
                    state["last_gc"] = datetime.now().isoformat()
                    state["gc_count"] += 1
                    
                    # Clean old backups
                    self.clean_old_backups()
                    
                    self.log("✨ Git hygiene complete!")
                else:
                    self.log("⚠️  Some cleanup operations failed", "WARNING")
            else:
                self.log("❌ Backup failed - skipping maintenance", "ERROR")
        else:
            self.log("✅ Repository is healthy - no maintenance needed")
        
        # Save state
        self.save_state(state)
        
        # Show summary
        self.log("\n📊 Hygiene Summary:")
        self.log(f"   Total GC runs: {state['gc_count']}")
        self.log(f"   Errors fixed: {state['errors_fixed']}")
        if state['last_gc']:
            self.log(f"   Last GC: {state['last_gc']}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Git Hygiene Manager')
    parser.add_argument('--force', action='store_true', help='Force hygiene even if recent')
    parser.add_argument('--check-only', action='store_true', help='Only check health')
    parser.add_argument('--schedule', action='store_true', help='Show scheduling options')
    
    args = parser.parse_args()
    
    manager = GitHygieneManager()
    
    if args.schedule:
        print("\n📅 Scheduling Options:")
        print("\n1. Windows Task Scheduler:")
        print("   schtasks /create /tn 'GitHygiene' /tr 'python git_hygiene_manager.py' /sc weekly /d SUN /st 02:00")
        print("\n2. Cron (Linux/Mac):")
        print("   0 2 * * 0 cd /path/to/project && python git_hygiene_manager.py")
        print("\n3. Manual run:")
        print("   python git_hygiene_manager.py [--force]")
        return
    
    if args.check_only:
        issues = manager.check_repository_health()
        if issues:
            print(f"\n⚠️  Found issues: {', '.join(issues)}")
        else:
            print("\n✅ Repository is healthy!")
        return
    
    manager.run_hygiene(force=args.force)

if __name__ == "__main__":
    main()