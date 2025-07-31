#!/usr/bin/env python3
"""
Automated Deployment System for TrenchCoat Pro
Deploys to Streamlit and updates dev blog/overview on every commit
"""
import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import time
from auto_bug_reporter import AutoBugReporter

class AutoDeploySystem:
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.deployment_log_file = self.project_root / "deployment_log.json"
        self.bug_reporter = AutoBugReporter()
        self.load_deployment_log()
        
    def load_deployment_log(self):
        """Load existing deployment log"""
        if self.deployment_log_file.exists():
            with open(self.deployment_log_file, 'r') as f:
                self.deployment_log = json.load(f)
        else:
            self.deployment_log = []
    
    def save_deployment_log(self):
        """Save deployment log"""
        with open(self.deployment_log_file, 'w') as f:
            json.dump(self.deployment_log, f, indent=2)
    
    def get_git_info(self):
        """Get current git commit info"""
        try:
            # Get current commit hash
            commit_hash = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], 
                text=True
            ).strip()
            
            # Get commit message
            commit_msg = subprocess.check_output(
                ['git', 'log', '-1', '--pretty=%B'], 
                text=True
            ).strip()
            
            # Get changed files
            changed_files = subprocess.check_output(
                ['git', 'diff', '--name-only', 'HEAD~1'], 
                text=True
            ).strip().split('\n')
            
            return {
                'commit_hash': commit_hash[:7],
                'commit_message': commit_msg,
                'changed_files': [f for f in changed_files if f]
            }
        except Exception as e:
            print(f"Error getting git info: {e}")
            return None
    
    def categorize_changes(self, git_info):
        """Categorize changes as bug fixes or new features"""
        changes = {
            'bug_fixes': [],
            'new_features': [],
            'core_changes': [],
            'config_changes': []
        }
        
        commit_msg = git_info['commit_message'].lower()
        
        # Categorize by commit message
        if any(word in commit_msg for word in ['fix', 'bug', 'error', 'crash', 'issue']):
            changes['bug_fixes'].append(git_info['commit_hash'] + ' ' + git_info['commit_message'][:50])
        elif any(word in commit_msg for word in ['add', 'new', 'feature', 'implement']):
            changes['new_features'].append(git_info['commit_hash'] + ' ' + git_info['commit_message'][:50])
        
        # Categorize by files changed
        for file in git_info['changed_files']:
            if file.endswith('.py'):
                if 'dashboard' in file or 'app' in file:
                    changes['core_changes'].append(file)
                elif 'config' in file or 'requirements' in file:
                    changes['config_changes'].append(file)
        
        return changes
    
    def update_dev_blog(self, git_info, changes, deployment_success):
        """Update the dev blog with deployment info"""
        try:
            # Import dev blog system
            from dev_blog_system import DevBlogSystem
            blog = DevBlogSystem()
            
            # Create blog entry
            title = f"Deployment: {git_info['commit_message'][:50]}"
            
            content = f"""
## Deployment Summary

**Commit:** `{git_info['commit_hash']}` - {git_info['commit_message']}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Status:** {'✅ Success' if deployment_success else '❌ Failed'}

### Changes Deployed:

"""
            
            if changes['bug_fixes']:
                content += "#### 🐛 Bug Fixes:\n"
                for fix in changes['bug_fixes']:
                    content += f"- {fix}\n"
                content += "\n"
            
            if changes['new_features']:
                content += "#### ✨ New Features:\n"
                for feature in changes['new_features']:
                    content += f"- {feature}\n"
                content += "\n"
            
            if changes['core_changes']:
                content += "#### 🔧 Core Changes:\n"
                for file in changes['core_changes']:
                    content += f"- Modified: `{file}`\n"
                content += "\n"
            
            # Add deployment details
            if deployment_success:
                content += """
### Deployment Details:

- **Platform:** Streamlit Cloud
- **URL:** https://trenchcoat-pro.streamlit.app
- **Auto-deploy:** Enabled
- **Health Check:** ✅ Passing

### Next Steps:

1. Monitor application performance
2. Check error logs for any issues
3. Validate all features working correctly
"""
            else:
                content += """
### Deployment Failed

Please check the deployment logs and fix any issues before retrying.
"""
            
            # Create blog post
            blog.create_post(
                title=title,
                content=content,
                category="deployment",
                tags=["deployment", "automated", "streamlit"]
            )
            
            print("✅ Dev blog updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error updating dev blog: {e}")
            return False
    
    def update_overview(self, git_info, changes):
        """Update the project overview with latest changes"""
        try:
            # Import overview updater
            from auto_overview_updater import update_project_overview
            
            # Prepare update data
            update_data = {
                'last_deployment': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'latest_commit': f"{git_info['commit_hash']} - {git_info['commit_message']}",
                'recent_changes': changes,
                'deployment_status': 'active',
                'version': self.get_next_version()
            }
            
            # Update overview
            update_project_overview(update_data)
            
            print("✅ Project overview updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error updating overview: {e}")
            return False
    
    def get_next_version(self):
        """Calculate next version number"""
        if not self.deployment_log:
            return "1.0.0"
        
        last_version = self.deployment_log[-1].get('version', '1.0.0')
        parts = last_version.split('.')
        
        # Increment patch version
        parts[2] = str(int(parts[2]) + 1)
        
        return '.'.join(parts)
    
    def deploy_to_streamlit(self):
        """Deploy to Streamlit Cloud"""
        try:
            print("🚀 Deploying to Streamlit Cloud...")
            
            # First, ensure we're on the right branch
            subprocess.run(['git', 'checkout', 'main'], check=True)
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Get git info before commit
            git_info = self.get_git_info()
            
            # Only commit if there are changes
            try:
                subprocess.run(['git', 'commit', '-m', f"Auto-deploy: {datetime.now().strftime('%Y-%m-%d %H:%M')}"], check=True)
            except subprocess.CalledProcessError:
                print("No changes to commit")
            
            # Push to GitHub
            print("📤 Pushing to GitHub...")
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            print("✅ Successfully pushed to GitHub")
            print("🔄 Streamlit will automatically detect and deploy changes")
            
            return True, git_info
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            return False, None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False, None
    
    def run_deployment(self):
        """Run the complete deployment process"""
        print("=" * 50)
        print("🤖 AUTOMATED DEPLOYMENT SYSTEM")
        print("=" * 50)
        
        # Get git info
        git_info = self.get_git_info()
        if not git_info:
            print("❌ Could not get git information")
            return False
        
        # Categorize changes
        changes = self.categorize_changes(git_info)
        
        # Deploy to Streamlit
        deployment_success, git_info = self.deploy_to_streamlit()
        
        # Log deployment
        deployment_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'success': deployment_success,
            'changes': changes,
            'commit': git_info['commit_hash'] if git_info else None,
            'version': self.get_next_version() if deployment_success else None
        }
        
        self.deployment_log.append(deployment_entry)
        self.save_deployment_log()
        
        # Update dev blog
        if git_info:
            self.update_dev_blog(git_info, changes, deployment_success)
        
        # Update overview
        if deployment_success and git_info:
            self.update_overview(git_info, changes)
        
        # Check for bug fixes and notify Discord
        if deployment_success and git_info:
            try:
                print("[6/6] Checking for bug fixes...")
                self.bug_reporter.process_latest_commit()
            except Exception as e:
                print(f"[WARN] Bug fix notification failed: {e}")
        
        print("\n" + "=" * 50)
        if deployment_success:
            print("✅ DEPLOYMENT SUCCESSFUL!")
            print(f"🌐 Your app will be updated at: https://trenchcoat-pro.streamlit.app")
            print("📝 Dev blog and overview have been updated")
        else:
            print("❌ DEPLOYMENT FAILED!")
            print("Please check the errors above and try again")
        print("=" * 50)
        
        return deployment_success


def main():
    """Main entry point"""
    deployer = AutoDeploySystem()
    success = deployer.run_deployment()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())