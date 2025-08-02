#!/usr/bin/env python3
"""
Simple deployment test - bypass validation to isolate timeout issue
"""
import subprocess
import sys
import os
import requests
from datetime import datetime
from unicode_handler import safe_print

def simple_deploy():
    """Minimal deployment without validation"""
    safe_print("Starting simple deployment test...")
    
    try:
        # Step 1: Check git status
        safe_print("Step 1: Git status check")
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        safe_print(f"Git status: {'clean' if not result.stdout.strip() else 'has changes'}")
        
        # Step 2: Get commit info
        safe_print("Step 2: Get last commit")
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        commit_info = result.stdout.strip()
        safe_print(f"Last commit: {commit_info}")
        
        # Step 3: Push to GitHub (if needed)
        safe_print("Step 3: Push to GitHub")
        try:
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True, text=True, timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0:
                safe_print("✅ Push successful")
            else:
                safe_print(f"Push result: {result.stderr}")
        except subprocess.TimeoutExpired:
            safe_print("❌ Git push timed out!")
            return False
        
        # Step 4: Quick Streamlit check (no waiting)
        safe_print("Step 4: Quick Streamlit check")
        try:
            response = requests.get("https://trenchdemo.streamlit.app", timeout=10)
            safe_print(f"Streamlit status: {response.status_code}")
        except:
            safe_print("Streamlit check failed (but continuing)")
        
        # Step 5: Send Discord notification
        safe_print("Step 5: Discord notification")
        webhook_url = "https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3"
        
        payload = {
            "embeds": [{
                "title": "🚀 Simple Deploy Test",
                "description": f"Testing deployment without validation\n\n**Commit:** {commit_info}",
                "color": 0x10b981,
                "timestamp": datetime.now().isoformat(),
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                safe_print("✅ Discord notification sent")
            else:
                safe_print(f"Discord notification failed: {response.status_code}")
        except:
            safe_print("Discord notification failed (but continuing)")
        
        safe_print("✅ Simple deployment completed successfully!")
        return True
        
    except Exception as e:
        safe_print(f"❌ Simple deployment failed: {e}")
        return False

def main():
    safe_print("=== SIMPLE DEPLOYMENT TEST ===")
    
    start_time = datetime.now()
    success = simple_deploy()
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    safe_print(f"\nTotal duration: {duration:.2f} seconds")
    
    if success:
        safe_print("🎉 Simple deployment test PASSED")
    else:
        safe_print("💥 Simple deployment test FAILED")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)