#!/usr/bin/env python3
"""Quick database checker"""
import sqlite3
import os

db_path = "data/trench.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    # Check coins count
    try:
        cursor.execute("SELECT COUNT(*) FROM coins;")
        count = cursor.fetchone()[0]
        print(f"Coins count: {count}")
        
        # Sample data
        cursor.execute("SELECT ticker, smart_wallets, liquidity FROM coins LIMIT 5;")
        sample = cursor.fetchall()
        print("Sample data:", sample)
    except Exception as e:
        print(f"Error: {e}")
    
    conn.close()
else:
    print("Database not found!")