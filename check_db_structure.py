#!/usr/bin/env python3
"""
Check trench.db structure
"""
import sqlite3
import os

def check_database():
    db_path = "data/trench.db"
    
    if not os.path.exists(db_path):
        print("Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("PRAGMA table_info(coins)")
    columns = cursor.fetchall()
    
    print("Database columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Get sample data
    cursor.execute("SELECT * FROM coins LIMIT 3")
    rows = cursor.fetchall()
    
    print("\nSample data:")
    for i, row in enumerate(rows):
        print(f"Row {i+1}: {row}")
    
    conn.close()

if __name__ == "__main__":
    check_database()