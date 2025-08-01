#!/usr/bin/env python3
"""
Simple database test without Streamlit
"""
import sqlite3
import os
from unicode_handler import safe_print

def test_database():
    """Test database connection"""
    safe_print("🔍 Testing Database Connection")
    safe_print("=" * 40)
    
    # Check if database exists
    db_path = "data/trench.db"
    if os.path.exists(db_path):
        safe_print(f"✅ Database found: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            safe_print(f"📋 Tables: {[t[0] for t in tables]}")
            
            # Get coin count
            cursor.execute("SELECT COUNT(*) FROM coins")
            coin_count = cursor.fetchone()[0]
            safe_print(f"🪙 Total coins: {coin_count}")
            
            # Get sample data
            cursor.execute("""
                SELECT ticker, discovery_price, axiom_price, smart_wallets 
                FROM coins 
                WHERE discovery_price > 0 AND axiom_price > 0 
                LIMIT 5
            """)
            samples = cursor.fetchall()
            
            safe_print("📊 Sample data:")
            for sample in samples:
                ticker, disc_price, axiom_price, smart_wallets = sample
                gain_pct = ((axiom_price - disc_price) / disc_price * 100) if disc_price > 0 else 0
                safe_print(f"  {ticker}: {gain_pct:.1f}% gain, {smart_wallets} smart wallets")
            
            conn.close()
            return True
            
        except Exception as e:
            safe_print(f"❌ Database error: {e}")
            return False
    else:
        safe_print(f"❌ Database not found: {db_path}")
        
        # Check alternative paths
        alt_paths = ["trench.db", "./data/trench.db", "../data/trench.db"]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                safe_print(f"📍 Found alternative: {alt_path}")
                return False
        
        safe_print("❌ No database found in any location")
        return False

if __name__ == "__main__":
    test_database()