#!/usr/bin/env python3
"""Debug the coin data loading issue"""
import sys
import os

# Fix Windows Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def debug_coin_data():
    """Debug coin data loading"""
    print("🔍 DEBUGGING COIN DATA LOADING")
    print("=" * 50)
    
    # Test 1: Check if trench.db exists
    db_path = "data/trench.db"
    print(f"1. Database file check: {db_path}")
    if os.path.exists(db_path):
        print(f"   ✅ File exists, size: {os.path.getsize(db_path):,} bytes")
    else:
        print(f"   ❌ File not found!")
        return
    
    # Test 2: Try streamlit_database import
    print("\n2. Testing streamlit_database import...")
    try:
        from streamlit_database import StreamlitDatabase
        print("   ✅ Import successful")
        
        db = StreamlitDatabase()
        print("   ✅ Database instance created")
        
        # Test get_live_coins
        coins = db.get_live_coins(limit=5)
        print(f"   📊 Retrieved {len(coins)} coins")
        
        if coins:
            print("   🎯 Sample coin data:")
            for i, coin in enumerate(coins[:3]):
                print(f"      {i+1}. {coin.get('ticker', 'NO_TICKER')} - "
                      f"Price: ${coin.get('axiom_price', 0):.8f} - "
                      f"Smart Wallets: {coin.get('smart_wallets', 0)}")
        else:
            print("   ❌ No coins returned")
            
    except Exception as e:
        print(f"   ❌ Import/execution error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test streamlit_safe_dashboard integration
    print("\n3. Testing dashboard integration...")
    try:
        # Simulate the dashboard's get_validated_coin_data logic
        database_available = True
        
        from streamlit_database import StreamlitDatabase
        streamlit_db = StreamlitDatabase()
        
        if database_available and streamlit_db:
            print("   ✅ Database available check passed")
            
            live_coins = streamlit_db.get_live_coins(limit=10)
            if live_coins:
                print(f"   ✅ Live coins retrieved: {len(live_coins)}")
                
                # Test data conversion logic
                coins = []
                for coin in live_coins:
                    price_gain_pct = 0
                    if coin.get('discovery_price', 0) > 0 and coin.get('axiom_price', 0) > 0:
                        price_gain_pct = ((coin['axiom_price'] - coin['discovery_price']) / coin['discovery_price']) * 100
                    
                    coin_data = {
                        'ticker': coin['ticker'],
                        'price_gain_pct': price_gain_pct,
                        'smart_wallets': coin.get('smart_wallets', 0),
                        'liquidity': coin.get('liquidity', 0),
                        'axiom_mc': coin.get('axiom_mc', 0),
                        'peak_volume': coin.get('peak_volume', coin.get('axiom_volume', 0)),
                        'ca': coin.get('ca', 'N/A'),
                        'data_source': 'live_trench_db',
                        'mode': 'live'
                    }
                    coins.append(coin_data)
                
                print(f"   ✅ Converted coins: {len(coins)}")
                print("   🎯 Sample converted data:")
                for coin in coins[:3]:
                    print(f"      - {coin['ticker']}: +{coin['price_gain_pct']:.1f}% gain, "
                          f"{coin['smart_wallets']} wallets, ${coin['liquidity']:,.0f} liquidity")
                    
            else:
                print("   ❌ No live coins returned from database")
        else:
            print("   ❌ Database availability check failed")
            
    except Exception as e:
        print(f"   ❌ Dashboard integration error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Direct SQL query
    print("\n4. Direct database query test...")
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM coins")
        count = cursor.fetchone()[0]
        print(f"   📊 Total coins in database: {count:,}")
        
        cursor.execute("""
            SELECT ticker, discovery_price, axiom_price, smart_wallets, liquidity 
            FROM coins 
            WHERE ticker IS NOT NULL AND ticker != '' 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        print(f"   🎯 Sample direct query results:")
        for row in rows:
            ticker, disc_price, axiom_price, wallets, liquidity = row
            gain = 0
            if disc_price and axiom_price and disc_price > 0:
                gain = ((axiom_price - disc_price) / disc_price) * 100
            print(f"      - {ticker}: +{gain:.1f}% gain, {wallets or 0} wallets, ${liquidity or 0:,.0f} liquidity")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Direct query error: {e}")

if __name__ == "__main__":
    debug_coin_data()