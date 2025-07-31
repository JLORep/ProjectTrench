#!/usr/bin/env python3
"""
Debug deployment timeouts by testing each component individually
"""
import subprocess
import time
import sys
import os
from unicode_handler import safe_print

def test_git_operations(timeout=30):
    """Test git operations with timeout"""
    safe_print("Testing git operations...")
    
    operations = [
        ["git", "status", "--porcelain"],
        ["git", "log", "--oneline", "-1"],
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
    ]
    
    for cmd in operations:
        try:
            safe_print(f"Running: {' '.join(cmd)}")
            start = time.time()
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            elapsed = time.time() - start
            safe_print(f"✅ Completed in {elapsed:.2f}s")
            
        except subprocess.TimeoutExpired:
            safe_print(f"❌ TIMEOUT after {timeout}s")
            return False
        except Exception as e:
            safe_print(f"❌ ERROR: {e}")
            return False
    
    return True

def test_network_operations(timeout=10):
    """Test network operations"""
    safe_print("Testing network operations...")
    
    try:
        import requests
        
        urls = [
            "https://trenchdemo.streamlit.app",
            "https://api.github.com/repos/JLORep/ProjectTrench"
        ]
        
        for url in urls:
            safe_print(f"Testing: {url}")
            start = time.time()
            
            response = requests.get(url, timeout=timeout)
            elapsed = time.time() - start
            
            safe_print(f"✅ Status {response.status_code} in {elapsed:.2f}s")
            
    except Exception as e:
        safe_print(f"❌ Network error: {e}")
        return False
    
    return True

def test_deployment_validator(timeout=30):
    """Test deployment validator"""
    safe_print("Testing deployment validator...")
    
    try:
        from deployment_validator import DeploymentValidator
        
        start = time.time()
        validator = DeploymentValidator()
        
        # Test just health check, no waiting
        health = validator.check_streamlit_health()
        elapsed = time.time() - start
        
        safe_print(f"✅ Health check: {health['status']} in {elapsed:.2f}s")
        return True
        
    except Exception as e:
        safe_print(f"❌ Validator error: {e}")
        return False

def main():
    """Run all debugging tests"""
    safe_print("=== DEPLOYMENT DEBUG TESTS ===")
    
    tests = [
        ("Git Operations", test_git_operations),
        ("Network Operations", test_network_operations), 
        ("Deployment Validator", test_deployment_validator)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        safe_print(f"\n--- {test_name} ---")
        start = time.time()
        
        try:
            result = test_func()
            elapsed = time.time() - start
            results[test_name] = {'success': result, 'time': elapsed}
            
            if result:
                safe_print(f"✅ {test_name} PASSED ({elapsed:.2f}s)")
            else:
                safe_print(f"❌ {test_name} FAILED ({elapsed:.2f}s)")
                
        except Exception as e:
            elapsed = time.time() - start
            results[test_name] = {'success': False, 'time': elapsed, 'error': str(e)}
            safe_print(f"❌ {test_name} CRASHED ({elapsed:.2f}s): {e}")
    
    safe_print("\n=== SUMMARY ===")
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        safe_print(f"{status} {test_name}: {result['time']:.2f}s")
    
    # Check for likely timeout culprits  
    slow_tests = [name for name, result in results.items() if result['time'] > 10]
    if slow_tests:
        safe_print(f"\n⚠️ Slow components (>10s): {', '.join(slow_tests)}")
    
    return all(result['success'] for result in results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)