#!/usr/bin/env python3
"""
Test coin image integration for troubleshooting
"""
import sqlite3
import sys

def test_image_integration():
    """Test if images are properly integrated"""
    
    print("=== COIN IMAGE INTEGRATION TEST ===")
    
    # Test 1: Check database columns
    conn = sqlite3.connect('data/trench.db')
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA table_info(coins)')
    columns = [col[1] for col in cursor.fetchall()]
    
    required_cols = ['image_url', 'image_source', 'image_verified']
    for col in required_cols:
        if col in columns:
            print(f"✓ Database has {col} column")
        else:
            print(f"✗ Database missing {col} column")
    
    # Test 2: Check if we have image data
    cursor.execute('SELECT COUNT(*) FROM coins WHERE image_url IS NOT NULL')
    image_count = cursor.fetchone()[0]
    print(f"✓ {image_count} coins have image URLs")
    
    # Test 3: Show sample data
    cursor.execute('SELECT ticker, image_url, image_source FROM coins WHERE image_url IS NOT NULL LIMIT 3')
    samples = cursor.fetchall()
    
    print("\nSample coin images:")
    for ticker, url, source in samples:
        print(f"  {ticker}: {url[:40]}... ({source})")
    
    conn.close()
    
    # Test 4: Test coin image system import
    try:
        from coin_image_system import coin_image_system
        print("✓ Coin image system imports successfully")
        
        # Test getting a cached image
        test_url = coin_image_system.get_image_url("$NYLA", "3HeUeL8ru8DFfRRQGnE11vGrDdNUzqVwBW8hyYHBbonk")
        print(f"✓ Test image URL retrieved: {test_url[:40]}...")
        
    except Exception as e:
        print(f"✗ Coin image system import failed: {e}")
    
    # Test 5: Test streamlit app query
    try:
        query = """
        SELECT ca, ticker, current_price_usd, image_url, image_source
        FROM coins 
        WHERE image_url IS NOT NULL
        LIMIT 3
        """
        
        conn = sqlite3.connect('data/trench.db')
        import pandas as pd
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"✓ Streamlit query would return {len(df)} coins with images")
        print("Sample query results:")
        for _, row in df.iterrows():
            print(f"  {row['ticker']}: {row['image_url'][:40]}...")
            
    except Exception as e:
        print(f"✗ Streamlit query test failed: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_image_integration()