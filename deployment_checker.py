#!/usr/bin/env python3
"""Quick deployment status checker"""
import sys
import requests
import time
from datetime import datetime

# Fix Windows Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_deployment():
    """Check Streamlit deployment status"""
    url = "https://trenchdemo.streamlit.app"
    
    print(f"🔍 Checking {url}...")
    
    try:
        response = requests.get(url, timeout=15, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Check for key features
            features = {
                'TrenchCoat Pro': 'trenchcoat pro' in content,
                'Incoming Coins': 'incoming coins' in content,
                'Live Dashboard': 'live dashboard' in content,
                'Solana Wallet': 'solana wallet' in content,
                'Telegram Signals': 'telegram signals' in content,
                'Demo Mode': 'demo data mode' in content or 'demo mode' in content
            }
            
            print("\n📊 Feature Detection:")
            for feature, present in features.items():
                status = "✅" if present else "❌"
                print(f"   {status} {feature}")
            
            # Check tab count
            tab_count = content.count('st.tabs')
            print(f"\n📋 Dashboard tabs detected: {tab_count}")
            
            if features['Demo Mode']:
                print("\n🟡 WARNING: Still in demo mode")
                return False
            elif features['Incoming Coins'] and features['Solana Wallet']:
                print("\n🎉 SUCCESS: All new features detected!")
                return True
            else:
                print("\n⚠️ PARTIAL: Some features missing")
                return False
                
        else:
            print(f"❌ App not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TrenchCoat Pro Deployment Checker")
    print("=" * 50)
    
    success = check_deployment()
    
    if success:
        print("\n✅ DEPLOYMENT SUCCESSFUL!")
        print("🔔 Incoming Coins tab should be visible")
        print("💎 Solana Wallet tab should be working")
        print("📡 Live data should be displaying")
    else:
        print("\n⚠️ DEPLOYMENT NEEDS ATTENTION")
        print("💡 Wait 2-3 minutes for Streamlit rebuild")
    
    print(f"\n🕒 Checked at: {datetime.now().strftime('%H:%M:%S')}")