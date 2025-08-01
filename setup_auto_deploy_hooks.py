#!/usr/bin/env python3
"""
Setup script for TrenchCoat Pro auto-deployment hooks
"""
import os
import sys
import stat
import shutil
from pathlib import Path

def setup_git_hooks():
    """Setup git hooks for automatic deployment"""
    project_root = Path(os.getcwd())
    git_hooks_dir = project_root / ".git" / "hooks"
    
    # Create hooks directory if it doesn't exist
    git_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # Post-commit hook content (Windows compatible)
    post_commit_content = '''#!/usr/bin/env python3
"""
Post-commit hook for TrenchCoat Pro
Automatically triggers deployment when commits contain feature/bug fix keywords
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get the commit message
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"], 
            capture_output=True, text=True, check=True
        )
        commit_msg = result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Could not get commit message")
        return
    
    # Convert to lowercase for checking
    commit_lower = commit_msg.lower()
    
    # Check if this commit should trigger a deployment
    should_deploy = False
    
    # Keywords that trigger deployment
    deploy_keywords = ['fix', 'bug', 'feature', 'add', 'implement', 'enhance', 'ship', 'deploy']
    skip_keywords = ['wip', 'temp', 'draft', 'test']
    
    # Check for deployment triggers
    if any(keyword in commit_lower for keyword in deploy_keywords):
        should_deploy = True
    
    # Skip deployment for certain patterns
    if any(keyword in commit_lower for keyword in skip_keywords):
        should_deploy = False
    
    if should_deploy:
        print(f"🚀 Commit detected that requires deployment: {commit_msg}")
        print("🤖 Triggering automated deployment...")
        
        # Change to project directory
        project_root = Path(__file__).parent.parent
        os.chdir(project_root)
        
        # Run the enhanced auto deployer
        try:
            result = subprocess.run([sys.executable, "enhanced_auto_deploy.py"], check=True)
            print("✅ Automated deployment completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Automated deployment failed: {e}")
            return 1
    else:
        print(f"ℹ️  Commit does not trigger deployment: {commit_msg}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    # Write the hook file
    hook_file = git_hooks_dir / "post-commit"
    with open(hook_file, 'w', encoding='utf-8') as f:
        f.write(post_commit_content)
    
    # Make it executable (Unix-style)
    try:
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
        print("✅ Git post-commit hook installed and made executable")
    except Exception as e:
        print(f"⚠️  Hook installed but couldn't make executable: {e}")
    
    return True

def create_manual_deploy_script():
    """Create a manual deployment script"""
    script_content = '''#!/usr/bin/env python3
"""
Manual deployment trigger for TrenchCoat Pro
"""
import subprocess
import sys

def main():
    print("🚀 Starting manual deployment...")
    
    try:
        # Run the enhanced auto deployer
        result = subprocess.run([sys.executable, "enhanced_auto_deploy.py"], check=True)
        print("✅ Manual deployment completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Manual deployment failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    # Write manual deploy script
    with open("manual_deploy.py", 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Manual deployment script created: manual_deploy.py")

def main():
    """Setup auto-deployment system"""
    print("=" * 50)
    print("🤖 TRENCHCOAT PRO AUTO-DEPLOYMENT SETUP")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Error: Not in a git repository")
        return 1
    
    # Setup git hooks
    print("1. Installing git hooks...")
    setup_git_hooks()
    
    # Create manual deployment script
    print("2. Creating manual deployment script...")
    create_manual_deploy_script()
    
    print("\n" + "=" * 50)
    print("✅ AUTO-DEPLOYMENT SETUP COMPLETE!")
    print("=" * 50)
    print("\n📋 What happens now:")
    print("• Every commit with keywords like 'fix', 'feature', 'add' will auto-deploy")
    print("• Streamlit app will be updated automatically")
    print("• Dev blog will be updated with deployment info")
    print("• Project overview will reflect latest changes")
    print("• Discord notifications will be sent")
    print("\n🔧 Manual deployment:")
    print("• Run: python manual_deploy.py")
    print("• Or: python enhanced_auto_deploy.py")
    print("\n🚀 Your next commit with 'fix' or 'feature' will trigger auto-deploy!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())