#!/usr/bin/env python3
"""
Quick deployment verification script
Checks that code changes are live on Streamlit
"""
import requests
import time
import subprocess
import sys

def verify_deployment():
    """Verify deployment is successful and changes are live"""
    
    print("🔍 Verifying deployment...")
    
    # 1. Get current commit hash
    result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                          capture_output=True, text=True)
    current_hash = result.stdout.strip()
    print(f"✅ Current commit: {current_hash}")
    
    # 2. Check Streamlit is responding
    try:
        start = time.time()
        response = requests.get("https://trenchdemo.streamlit.app", timeout=30)
        elapsed = time.time() - start
        
        if response.status_code in [200, 303]:
            print(f"✅ Streamlit responding (HTTP {response.status_code}) in {elapsed:.1f}s")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False
    
    # 3. Wait for deployment to propagate
    print("⏳ Waiting 30s for deployment to propagate...")
    time.sleep(30)
    
    # 4. Check specific features
    print("\n📊 Checking features:")
    
    # Try to fetch the page content
    try:
        response = requests.get("https://trenchdemo.streamlit.app", timeout=30)
        content = response.text.lower()
        
        # Check for key elements
        checks = {
            "TrenchCoat Pro title": "trenchcoat pro" in content,
            "Dashboard tab": "dashboard" in content,
            "Coins tab": "coins" in content or "💎" in content,
            "Multiple tabs": content.count("tab") > 5,
            "No error messages": "error" not in content[:1000]
        }
        
        all_passed = True
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✅ Deployment verified successfully!")
            return True
        else:
            print("\n⚠️ Some checks failed - deployment may need more time")
            return False
            
    except Exception as e:
        print(f"❌ Error checking features: {e}")
        return False

if __name__ == "__main__":
    success = verify_deployment()
    sys.exit(0 if success else 1)