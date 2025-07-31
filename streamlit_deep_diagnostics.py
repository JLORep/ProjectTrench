#!/usr/bin/env python3
"""
Deep Streamlit App Diagnostics
Advanced analysis of Streamlit deployment status
"""
import requests
import json
import time
from unicode_handler import safe_print

def deep_streamlit_analysis():
    """Deep analysis of Streamlit app deployment"""
    safe_print("🔬 Deep Streamlit App Diagnostics")
    safe_print("=" * 50)
    
    # Primary URL
    base_url = "https://trenchcoat-pro.streamlit.app"
    
    safe_print(f"🎯 Analyzing: {base_url}")
    
    # Test 1: Basic connectivity
    safe_print("\n📡 Test 1: Basic Connectivity")
    try:
        response = requests.get(base_url, timeout=15, allow_redirects=True)
        safe_print(f"Final URL after redirects: {response.url}")
        safe_print(f"Status Code: {response.status_code}")
        safe_print(f"Response time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            # Check if it's actually our app
            content = response.text.lower()
            
            # Look for TrenchCoat indicators
            indicators = {
                'trenchcoat': 'TrenchCoat branding',
                'coin data': 'Coin Data tab',
                'telegram': 'Telegram features', 
                'solana': 'Solana integration',
                'dashboard': 'Dashboard interface',
                'streamlit': 'Streamlit framework',
                '1,733': 'Live coin count',
                'premium': 'Premium features'
            }
            
            found = []
            missing = []
            
            for keyword, description in indicators.items():
                if keyword in content:
                    found.append(f"✅ {description}")
                else:
                    missing.append(f"❌ {description}")
            
            safe_print(f"\n🔍 Content Analysis:")
            safe_print(f"Found indicators: {len(found)}")
            for item in found:
                safe_print(f"  {item}")
            
            if missing:
                safe_print(f"Missing indicators: {len(missing)}")
                for item in missing[:3]:  # Show first 3
                    safe_print(f"  {item}")
            
            # Check for specific content
            if 'coin data' in content:
                safe_print("🎉 COIN DATA TAB DETECTED!")
            else:
                safe_print("⚠️ Coin Data tab not found in content")
                
            # Preview first part of content
            safe_print(f"\n📄 Content Preview (first 300 chars):")
            safe_print(response.text[:300])
            
        else:
            safe_print(f"❌ Non-200 status code: {response.status_code}")
            
    except Exception as e:
        safe_print(f"💥 Connection error: {e}")
    
    # Test 2: Check for cache issues
    safe_print(f"\n🔄 Test 2: Cache-Busting Request")
    try:
        cache_buster = f"{base_url}?t={int(time.time())}"
        response = requests.get(cache_buster, timeout=15, allow_redirects=True,
                              headers={'Cache-Control': 'no-cache'})
        safe_print(f"Cache-busted status: {response.status_code}")
        
        if response.status_code == 200:
            if 'coin data' in response.text.lower():
                safe_print("✅ Coin Data tab found with cache-busting!")
            else:
                safe_print("❌ Still no Coin Data tab with cache-busting")
        
    except Exception as e:
        safe_print(f"💥 Cache-busting error: {e}")
    
    # Test 3: Check health endpoint
    safe_print(f"\n🏥 Test 3: Health Check Endpoint")
    try:
        health_url = f"{base_url}/healthz"
        response = requests.get(health_url, timeout=10)
        safe_print(f"Health endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            safe_print("✅ Health endpoint responding")
        
    except Exception as e:
        safe_print(f"Health check error: {e}")
    
    # Test 4: Check streamlit specific paths
    safe_print(f"\n🎛️ Test 4: Streamlit App Structure")
    test_paths = [
        "/",
        "/_stcore/health",
        "/_stcore/healthz"
    ]
    
    for path in test_paths:
        try:
            test_url = f"{base_url}{path}"
            response = requests.get(test_url, timeout=10, allow_redirects=False)
            safe_print(f"Path {path}: {response.status_code}")
            
        except Exception as e:
            safe_print(f"Path {path}: Error - {e}")
    
    safe_print("\n" + "=" * 50)
    safe_print("🎯 DIAGNOSIS SUMMARY")
    safe_print("- If app loads but missing features: Deployment successful, feature not visible")
    safe_print("- If 200 OK but wrong content: App exists but not updated")
    safe_print("- If redirects/auth: App privacy settings issue")
    safe_print("- If timeouts: Streamlit Cloud performance issue")

if __name__ == "__main__":
    deep_streamlit_analysis()