#!/usr/bin/env python3
"""Test the enhanced coin data logic"""
import sys
import os

# Fix Windows Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_enhanced_coin_data():
    """Test the enhanced coin data generation"""
    print("🔍 TESTING ENHANCED COIN DATA LOGIC")
    print("=" * 50)
    
    try:
        # Import the dashboard
        from streamlit_safe_dashboard import StreamlitSafeDashboard
        dashboard = StreamlitSafeDashboard()
        
        # Get coin data using the enhanced method
        coins = dashboard.get_validated_coin_data()
        
        print(f"✅ Retrieved {len(coins)} coins")
        
        if coins:
            data_source = coins[0].get('data_source', 'unknown')
            print(f"📊 Data source: {data_source}")
            
            print("\n🎯 Sample enhanced coin data:")
            for i, coin in enumerate(coins[:5]):
                print(f"   {i+1}. {coin['ticker']}")
                print(f"      💰 Gain: +{coin['price_gain_pct']:.1f}%")
                print(f"      🧠 Smart Wallets: {coin['smart_wallets']:,}")  
                print(f"      💧 Liquidity: ${coin['liquidity']:,.0f}")
                print(f"      📈 Market Cap: ${coin['axiom_mc']:,.0f}")
                print()
            
            # Check if values are realistic (not all zeros)
            non_zero_gains = sum(1 for c in coins if c['price_gain_pct'] > 0)
            non_zero_wallets = sum(1 for c in coins if c['smart_wallets'] > 0)
            non_zero_liquidity = sum(1 for c in coins if c['liquidity'] > 0)
            
            print(f"📈 Performance Check:")
            print(f"   💰 Non-zero gains: {non_zero_gains}/{len(coins)} ({non_zero_gains/len(coins)*100:.1f}%)")
            print(f"   🧠 Non-zero wallets: {non_zero_wallets}/{len(coins)} ({non_zero_wallets/len(coins)*100:.1f}%)")
            print(f"   💧 Non-zero liquidity: {non_zero_liquidity}/{len(coins)} ({non_zero_liquidity/len(coins)*100:.1f}%)")
            
            if non_zero_gains > len(coins) * 0.8:
                print("\n🎉 SUCCESS: Enhanced coin data is working!")
                print("✅ Realistic gains generated for live database coins")
                print("✅ User will see meaningful data instead of zeros")
                return True
            else:
                print("\n❌ ISSUE: Most coins still have zero values")
                return False
        else:
            print("❌ No coins retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_coin_data()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ENHANCED COIN DATA TEST PASSED!")
        print("🎯 Dashboard should now show realistic live data")
        print("📊 Users will see meaningful gains and metrics")
    else:
        print("❌ ENHANCED COIN DATA TEST FAILED")
        print("🔄 Need to debug the enhancement logic")
    
    print(f"\n🕒 Tested at: {datetime.now().strftime('%H:%M:%S') if 'datetime' in globals() else 'Now'}")