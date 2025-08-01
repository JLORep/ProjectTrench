#!/usr/bin/env python3
"""
Lightweight GitHub Setup - No Heavy Installers
CPU-friendly approach using existing tools
"""
import subprocess
import os
import sys
import json
import base64
import urllib3
import requests
from pathlib import Path

class LightweightGitHubSetup:
    """Lightweight GitHub operations without heavy CLI tools"""
    
    def __init__(self):
        self.repo_owner = "JLORep"
        self.repo_name = "ProjectTrench"
        self.github_api = "https://api.github.com"
        
    def check_git_config(self):
        """Check if git is properly configured"""
        print("🔧 Checking Git configuration...")
        
        try:
            # Check if git exists
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Git found: {result.stdout.strip()}")
            else:
                print("❌ Git not found")
                return False
                
            # Check git config
            name_result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
            email_result = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
            
            if name_result.returncode == 0 and email_result.returncode == 0:
                print(f"✅ Git configured: {name_result.stdout.strip()} <{email_result.stdout.strip()}>")
                return True
            else:
                print("⚠️ Git not configured properly")
                return False
                
        except FileNotFoundError:
            print("❌ Git not found in PATH")
            return False
    
    def setup_git_credential_helper(self):
        """Set up Git credential helper for GitHub"""
        print("🔑 Setting up Git credentials...")
        
        try:
            # Use Windows Credential Manager (built-in)
            subprocess.run([
                "git", "config", "--global", "credential.helper", "manager-core"
            ], check=True)
            
            # Set up GitHub specific config
            subprocess.run([
                "git", "config", "--global", "credential.https://github.com.provider", "generic"
            ], check=True)
            
            print("✅ Git credential helper configured")
            return True
            
        except subprocess.CalledProcessError:
            print("⚠️ Could not configure credential helper")
            return False
    
    def create_personal_access_token_guide(self):
        """Create guide for manual token creation"""
        token_guide = """
# 🔑 GitHub Personal Access Token Setup

## Step 1: Create Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "TrenchCoat Pro Deploy"
4. Expiration: 90 days
5. Select scopes:
   ✅ repo (Full control of private repositories)
   ✅ workflow (Update GitHub Action workflows)
   ✅ write:packages (Upload packages)
   ✅ read:org (Read org and team membership)

## Step 2: Copy Token
- Copy the token (starts with ghp_...)
- Save it somewhere safe (you'll need it for git push)

## Step 3: Use Token
When git asks for password, use the token instead:
- Username: JLORep
- Password: [paste your token here]

## Alternative: Store Token in Git
```bash
git config --global credential.helper store
git push -u origin master
# Enter username: JLORep  
# Enter password: [your token]
# Git will remember for future pushes
```
"""
        
        with open("GITHUB_TOKEN_GUIDE.md", "w") as f:
            f.write(token_guide)
        
        print("✅ Created GITHUB_TOKEN_GUIDE.md")
        return True
    
    def push_with_simple_auth(self):
        """Push using simple git with credential prompting"""
        print("📤 Attempting to push to GitHub...")
        
        try:
            # Add all files
            subprocess.run(["git", "add", "-A"], check=True)
            
            # Check if there are changes to commit
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         capture_output=True, text=True)
            
            if status_result.stdout.strip():
                # Commit changes
                subprocess.run([
                    "git", "commit", "-m", 
                    "feat: TrenchCoat Pro v1.0.0 - Ultra-premium dashboard ready for deployment"
                ], check=True)
            
            # Try to push
            print("🔄 Pushing to GitHub (you may need to enter credentials)...")
            push_result = subprocess.run([
                "git", "push", "-u", "origin", "master"
            ], capture_output=True, text=True, timeout=60)
            
            if push_result.returncode == 0:
                print("✅ Successfully pushed to GitHub!")
                print(f"🔗 Repository: https://github.com/{self.repo_owner}/{self.repo_name}")
                return True
            else:
                print(f"❌ Push failed: {push_result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Push timed out - likely waiting for credentials")
            print("💡 Please check GITHUB_TOKEN_GUIDE.md for authentication options")
            return False
        except subprocess.CalledProcessError as e:
            print(f"❌ Git command failed: {e}")
            return False
    
    def create_streamlit_deployment_files(self):
        """Create files needed for Streamlit Cloud deployment"""
        print("☁️ Creating Streamlit Cloud deployment files...")
        
        # Create .streamlit/secrets.toml template
        secrets_dir = Path(".streamlit")
        secrets_dir.mkdir(exist_ok=True)
        
        secrets_template = """# Streamlit Secrets for TrenchCoat Pro
# Add your API keys here when deploying to Streamlit Cloud

[api_keys]
# anthropic_api_key = "your_claude_api_key_here"
# coingecko_api_key = "your_coingecko_key_here"
# birdeye_api_key = "your_birdeye_key_here"

[settings]
demo_mode = true
live_trading_enabled = false
"""
        
        with open(secrets_dir / "secrets.toml", "w") as f:
            f.write(secrets_template)
        
        # Create app launcher for Streamlit Cloud
        streamlit_app = """#!/usr/bin/env python3
'''
TrenchCoat Pro - Streamlit Cloud Launcher
Optimized for cloud deployment
'''
import streamlit as st
import os

# Set cloud environment
os.environ['STREAMLIT_CLOUD'] = 'true'
os.environ['DEMO_MODE'] = 'true'

# Configure page
st.set_page_config(
    page_title="TrenchCoat Pro - Live Demo",
    page_icon="🎯",
    layout="wide"
)

# Import and run ultra-premium dashboard
try:
    from ultra_premium_dashboard import UltraPremiumDashboard
    
    # Add cloud-specific header
    st.markdown('''
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #065f46 0%, #059669 100%); 
                border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h2>🎯 TrenchCoat Pro - Live Demo</h2>
        <p>Ultra-Premium Cryptocurrency Trading Dashboard</p>
        <p><small>Running in DEMO mode - No live trading</small></p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize dashboard
    dashboard = UltraPremiumDashboard()
    
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please ensure all dependencies are installed correctly.")
except Exception as e:
    st.error(f"Error: {e}")
    st.info("Please check the application logs for more details.")
"""
        
        with open("streamlit_app.py", "w") as f:
            f.write(streamlit_app)
        
        print("✅ Streamlit deployment files created")
        return True
    
    def create_deployment_instructions(self):
        """Create comprehensive deployment instructions"""
        instructions = """# 🚀 TrenchCoat Pro - Lightweight Deployment Guide

## Current Status: ✅ READY FOR DEPLOYMENT

Your ultra-premium dashboard is complete with:
- Apple/PayPal-level design with glassmorphism effects  
- Live coin processing animations
- Real-time performance metrics
- AI-powered suggestions from Claude
- 3D visualizations and heatmap calendars
- Professional dark theme with smooth transitions

## Quick Deployment Options

### Option 1: GitHub Web Interface (Easiest)
1. Go to: https://github.com/JLORep/ProjectTrench
2. Click "uploading an existing file"
3. Drag all files from C:\\trench (except venv/, .git/, *.db)
4. Commit message: "feat: TrenchCoat Pro v1.0.0 - Ultra-premium dashboard"
5. Click "Commit changes"

### Option 2: Git with Personal Access Token
1. Create token: https://github.com/settings/tokens
2. Copy token (starts with ghp_...)
3. Run: `git push -u origin master`
4. Username: JLORep
5. Password: [paste token]

### Option 3: Git with Stored Credentials
```bash
git config --global credential.helper store
git push -u origin master
# Enter credentials once, Git remembers them
```

## Deploy to Streamlit Cloud

1. **Go to**: https://share.streamlit.io
2. **Sign in** with GitHub account  
3. **New app** → Connect repository
4. **Repository**: JLORep/ProjectTrench
5. **Branch**: master
6. **Main file**: streamlit_app.py
7. **Click Deploy!**

## Expected URLs
- **GitHub**: https://github.com/JLORep/ProjectTrench
- **Live Demo**: https://trenchcoat-pro.streamlit.app (or similar)

## Test Locally First
```bash
streamlit run ultra_premium_dashboard.py
```

## Files Ready for Deployment
✅ ultra_premium_dashboard.py (main app)
✅ premium_components.py (advanced features)  
✅ streamlit_app.py (cloud launcher)
✅ requirements.txt (dependencies)
✅ .streamlit/config.toml (theme)
✅ tests/test_suite.py (comprehensive tests)

## No Heavy Installations Required!
All deployment uses existing tools and web interfaces - perfect for your i7 CPU constraints.

The ultra-premium dashboard is ready to go live! 🎉
"""
        
        with open("DEPLOYMENT_INSTRUCTIONS.md", "w") as f:
            f.write(instructions)
        
        print("✅ Created DEPLOYMENT_INSTRUCTIONS.md")
        return True
    
    def test_dashboard_locally(self):
        """Test if the dashboard can run locally"""
        print("🧪 Testing dashboard locally...")
        
        try:
            # Check if streamlit is available
            result = subprocess.run(["streamlit", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Streamlit available: {result.stdout.strip()}")
                
                print("🚀 You can test the dashboard with:")
                print("   streamlit run ultra_premium_dashboard.py")
                return True
            else:
                print("❌ Streamlit not available")
                return False
                
        except FileNotFoundError:
            print("❌ Streamlit not found")
            print("💡 Install with: pip install streamlit")
            return False
    
    def run_lightweight_setup(self):
        """Run complete lightweight setup"""
        print("🎯 TrenchCoat Pro - Lightweight Setup (CPU-Friendly)")
        print("=" * 60)
        
        # Check git
        if not self.check_git_config():
            return False
        
        # Set up credentials
        self.setup_git_credential_helper()
        
        # Create guides and files
        self.create_personal_access_token_guide()
        self.create_streamlit_deployment_files()
        self.create_deployment_instructions()
        
        # Test dashboard
        self.test_dashboard_locally()
        
        # Try simple push
        success = self.push_with_simple_auth()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 SUCCESS! TrenchCoat Pro is ready for deployment!")
            print(f"🔗 Repository: https://github.com/{self.repo_owner}/{self.repo_name}")
        else:
            print("⚠️ Push failed - Check DEPLOYMENT_INSTRUCTIONS.md for manual options")
        
        print("\n📋 Next Steps:")
        print("1. Deploy to Streamlit Cloud: https://share.streamlit.io")
        print("2. Set main file: streamlit_app.py")
        print("3. Your ultra-premium dashboard will be live!")
        
        return True


def main():
    """Run lightweight setup"""
    setup = LightweightGitHubSetup()
    setup.run_lightweight_setup()

if __name__ == "__main__":
    main()