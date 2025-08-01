#!/usr/bin/env python3
"""Quick deployment status check"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import time
from datetime import datetime

def check_streamlit_app():
    """Quick check of Streamlit app status"""
    url = "https://trenchdemo.streamlit.app"
    
    try:
        print(f"🔍 Checking {url}...")
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Check for key features
            features = {
                'TrenchCoat Pro': 'trenchcoat pro' in content,
                'Incoming Coins': 'incoming coins' in content,
                'Live Data': 'live data' in content,
                'Solana Wallet': 'solana wallet' in content,
                'Demo Mode': 'demo data mode' in content or 'demo mode' in content
            }
            
            print("\n📊 Feature Detection:")
            for feature, present in features.items():
                status = "✅" if present else "❌"
                print(f"   {status} {feature}")
            
            if features['Demo Mode']:
                print("\n🟡 WARNING: App is still in demo mode - database connection issue")
            else:
                print("\n🟢 SUCCESS: Live data mode detected")
                
            return features
        else:
            print(f"❌ App not accessible: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking app: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Quick Deployment Check")
    print("=" * 40)
    features = check_streamlit_app()
    
    if features and not features.get('Demo Mode', True):
        print("\n✅ DEPLOYMENT SUCCESSFUL")
    else:
        print("\n⚠️ DEPLOYMENT NEEDS ATTENTION")
        print("💡 Try waiting 2-3 minutes for Streamlit to rebuild")