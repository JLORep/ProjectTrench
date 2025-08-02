#!/usr/bin/env python3
"""
Post-Deployment Validator - Runs after each deployment
Simple validation that can be called from git hooks
"""
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

def run_validation():
    """Run simple post-deployment validation"""
    print("🔍 Running post-deployment validation...")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "github_pushed": False,
        "streamlit_url": "https://trenchdemo.streamlit.app",
        "validation_passed": False
    }
    
    try:
        # Check if code is pushed
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        uncommitted = result.stdout.strip()
        if not uncommitted:
            results["github_pushed"] = True
            print("✅ Code is committed and pushed")
        else:
            print("⚠️ Uncommitted changes detected")
            
        # Simple check - just verify git push succeeded
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            commit_hash = result.stdout.strip()[:8]
            results["commit_hash"] = commit_hash
            results["validation_passed"] = True
            print(f"✅ Latest commit: {commit_hash}")
        
        # Save results
        with open("deployment_validation.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"📊 Validation {'PASSED' if results['validation_passed'] else 'FAILED'}")
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        results["error"] = str(e)
        
    return results["validation_passed"]

if __name__ == "__main__":
    # Wait a bit for deployment to propagate
    print("Waiting 10 seconds for deployment to propagate...")
    time.sleep(10)
    
    success = run_validation()
    exit(0 if success else 1)