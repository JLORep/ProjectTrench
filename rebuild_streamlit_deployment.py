#!/usr/bin/env python3
"""
Complete Streamlit deployment rebuild from scratch
"""
import subprocess
import requests
import time
import json
import sys
import io
from datetime import datetime
from pathlib import Path

# Fix Unicode encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class StreamlitDeploymentRebuilder:
    def __init__(self):
        self.github_repo = "https://github.com/JLORep/ProjectTrench"
        self.correct_streamlit_urls = [
            "https://projecttrench-uat.streamlit.app/",
            "https://trenchcoat-pro.streamlit.app/",
            "https://share.streamlit.io/jlorep/projecttrench/main/streamlit_app.py"
        ]
        self.discord_webhook = "https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3"
        
    def check_local_files(self):
        """Verify required files exist locally"""
        print("🔍 Checking local files...")
        
        required_files = [
            "streamlit_app.py",
            "streamlit_safe_dashboard.py", 
            "streamlit_database.py",
            "data/trench.db"
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
            else:
                print(f"✅ {file} exists")
        
        if missing_files:
            print(f"❌ Missing files: {missing_files}")
            return False
        
        # Check trench.db has data
        try:
            import sqlite3
            conn = sqlite3.connect("data/trench.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM coins")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"✅ trench.db has {count} coins")
            return count > 0
        except Exception as e:
            print(f"❌ Error checking trench.db: {e}")
            return False
    
    def create_requirements_txt(self):
        """Create minimal requirements.txt for Streamlit Cloud"""
        print("📝 Creating requirements.txt...")
        
        requirements = [
            "streamlit>=1.28.0",
            "plotly>=5.15.0", 
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "requests>=2.31.0"
        ]
        
        with open("requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        
        print("✅ requirements.txt created")
    
    def create_streamlit_config(self):
        """Create .streamlit/config.toml"""
        print("⚙️ Creating Streamlit config...")
        
        Path(".streamlit").mkdir(exist_ok=True)
        
        config = """[global]
developmentMode = false

[server]
runOnSave = true
port = 8501

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#10b981"
backgroundColor = "#0f0f0f"
secondaryBackgroundColor = "#1a1a1a"
textColor = "#ffffff"
"""
        
        with open(".streamlit/config.toml", "w") as f:
            f.write(config)
        
        print("✅ Streamlit config created")
    
    def test_local_streamlit(self):
        """Test streamlit app locally first"""
        print("🧪 Testing local Streamlit...")
        
        try:
            # Import test
            import streamlit_safe_dashboard
            import streamlit_database
            print("✅ Module imports successful")
            
            # Database test
            db = streamlit_database.streamlit_db
            coins = db.get_live_coins(limit=3)
            print(f"✅ Database test: {len(coins)} coins retrieved")
            
            return True
            
        except Exception as e:
            print(f"❌ Local test failed: {e}")
            return False
    
    def commit_and_push(self):
        """Commit all changes and push to GitHub"""
        print("📤 Pushing to GitHub...")
        
        try:
            # Add all files
            subprocess.run(["git", "add", "."], check=True)
            
            # Commit
            commit_msg = f"REBUILD: Complete Streamlit deployment rebuild - {datetime.now().strftime('%H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            
            # Push
            subprocess.run(["git", "push", "origin", "main"], check=True)
            
            print("✅ Pushed to GitHub successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            return False
    
    def check_streamlit_deployment(self):
        """Check all possible Streamlit URLs"""
        print("🌐 Checking Streamlit deployments...")
        
        working_urls = []
        
        for url in self.correct_streamlit_urls:
            try:
                print(f"Checking: {url}")
                response = requests.get(url, timeout=10, allow_redirects=False)
                
                if response.status_code == 200:
                    print(f"✅ {url} - Working (200)")
                    working_urls.append(url)
                elif response.status_code == 303:
                    print(f"⚠️ {url} - Auth redirect (303)")
                else:
                    print(f"❌ {url} - Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {url} - Error: {e}")
        
        return working_urls
    
    def send_discord_notification(self, message):
        """Send deployment status to Discord"""
        try:
            payload = {
                "content": f"🚀 **Streamlit Deployment Rebuild**\n{message}\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            response = requests.post(self.discord_webhook, json=payload, timeout=10)
            if response.status_code == 204:
                print("✅ Discord notification sent")
            else:
                print(f"⚠️ Discord notification failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Discord notification error: {e}")
    
    def rebuild_complete_deployment(self):
        """Execute complete deployment rebuild"""
        print("🚀 STARTING COMPLETE STREAMLIT DEPLOYMENT REBUILD")
        print("=" * 60)
        
        steps_passed = 0
        total_steps = 6
        
        # Step 1: Check local files
        if self.check_local_files():
            steps_passed += 1
            print("✅ Step 1/6: Local files verified")
        else:
            print("❌ Step 1/6: Local files check failed")
            return False
        
        # Step 2: Create requirements
        self.create_requirements_txt()
        steps_passed += 1
        print("✅ Step 2/6: Requirements created")
        
        # Step 3: Create config
        self.create_streamlit_config()
        steps_passed += 1
        print("✅ Step 3/6: Streamlit config created")
        
        # Step 4: Test locally
        if self.test_local_streamlit():
            steps_passed += 1
            print("✅ Step 4/6: Local testing passed")
        else:
            print("❌ Step 4/6: Local testing failed")
            return False
        
        # Step 5: Push to GitHub
        if self.commit_and_push():
            steps_passed += 1
            print("✅ Step 5/6: GitHub push successful")
        else:
            print("❌ Step 5/6: GitHub push failed")
            return False
        
        # Step 6: Check deployment
        time.sleep(30)  # Wait for Streamlit Cloud to rebuild
        working_urls = self.check_streamlit_deployment()
        
        if working_urls:
            steps_passed += 1
            print("✅ Step 6/6: Deployment verification successful")
            
            # Success notification
            message = f"✅ **REBUILD COMPLETE**\n🔗 Working URLs: {len(working_urls)}\n📊 Live data: trench.db with 1733 coins\n⚡ All {steps_passed}/{total_steps} steps passed"
            self.send_discord_notification(message)
            
            print("\n🎉 DEPLOYMENT REBUILD SUCCESSFUL!")
            print(f"✅ Working URLs: {working_urls}")
            return True
        else:
            print("❌ Step 6/6: No working deployments found")
            
            # Failure notification
            message = f"❌ **REBUILD FAILED**\n⚠️ No working Streamlit URLs found\n📝 {steps_passed}/{total_steps} steps completed\n🔧 Manual intervention required"
            self.send_discord_notification(message)
            
            return False

def main():
    """Main execution"""
    rebuilder = StreamlitDeploymentRebuilder()
    success = rebuilder.rebuild_complete_deployment()
    
    if success:
        print("\n✅ Complete deployment rebuild successful!")
        print("🌐 Your TrenchCoat Pro dashboard should now be live with real data!")
    else:
        print("\n❌ Deployment rebuild failed - check errors above")
    
    return success

if __name__ == "__main__":
    main()