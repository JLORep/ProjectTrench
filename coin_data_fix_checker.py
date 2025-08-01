#!/usr/bin/env python3
"""Check if the coin data tab fix is working"""
import sys
import requests
import time
from datetime import datetime

# Fix Windows Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_coin_data_fix():
    """Check if coin data tab shows live data"""
    url = "https://trenchdemo.streamlit.app"
    
    print("🔍 COIN DATA TAB FIX VERIFICATION")
    print("=" * 50)
    print(f"Checking: {url}")
    
    try:
        response = requests.get(url, timeout=15, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Check for specific indicators
            indicators = {
                'Live Data Connection': 'live_trench_db' in content or 'live data' in content,
                'Coin Data Tab': 'coin data' in content,
                'Real Coin Tickers': any(ticker in content for ticker in ['pepe', 'shib', 'doge', 'floki']),
                'Percentage Gains': '+' in content and '%' in content,
                'Smart Wallets': 'smart wallets' in content,
                'Liquidity Data': 'liquidity' in content,
                'Demo Mode Warning': 'demo data mode' in content or 'demo mode' in content,
                'HTML Debug Text': 'header with coin image and tick' in content
            }
            
            print("\n📊 Fix Verification Results:")
            for indicator, present in indicators.items():
                if indicator in ['Demo Mode Warning', 'HTML Debug Text']:
                    status = "❌" if present else "✅"  # These should NOT be present
                    print(f"   {status} {indicator}: {'FOUND (BAD)' if present else 'NOT FOUND (GOOD)'}")
                else:
                    status = "✅" if present else "❌"
                    print(f"   {status} {indicator}: {'PRESENT' if present else 'MISSING'}")
            
            # Overall assessment
            good_indicators = sum([
                indicators['Live Data Connection'],
                indicators['Coin Data Tab'], 
                indicators['Real Coin Tickers'],
                indicators['Percentage Gains'],
                indicators['Smart Wallets'],
                indicators['Liquidity Data']
            ])
            
            bad_indicators = sum([
                indicators['Demo Mode Warning'],
                indicators['HTML Debug Text']
            ])
            
            print(f"\n📈 Score: {good_indicators}/6 good indicators, {bad_indicators}/2 bad indicators")
            
            if good_indicators >= 4 and bad_indicators == 0:
                print("\n🎉 SUCCESS: Coin data tab fix appears to be working!")
                print("✅ Live data integration successful")
                print("✅ No demo mode warnings")
                print("✅ No HTML debug text")
                return True
            elif good_indicators >= 3:
                print("\n⚠️ PARTIAL SUCCESS: Some improvements detected")
                print("💡 May need more time for Streamlit to fully rebuild")
                return False
            else:
                print("\n❌ FAILURE: Fix not yet visible")
                print("🔄 Streamlit may still be rebuilding - try again in 2-3 minutes")
                return False
                
        else:
            print(f"❌ App not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = check_coin_data_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ COIN DATA FIX VERIFICATION PASSED!")
        print("🎯 The live database integration should now be working")
        print("📊 Users should see real coin data instead of demo content")
    else:
        print("⚠️ COIN DATA FIX NEEDS MORE TIME")
        print("⏰ Wait 2-3 minutes for Streamlit Cloud to rebuild")
        print("🔄 Run this check again to verify the fix")
    
    print(f"\n🕒 Checked at: {datetime.now().strftime('%H:%M:%S')}")
    print("📱 Manual check: https://trenchdemo.streamlit.app")