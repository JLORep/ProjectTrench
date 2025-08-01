import sqlite3
import os

db_path = "data/trench.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== TRENCH.DB SCHEMA ===")
    print("\nCOINS TABLE COLUMNS:")
    cursor.execute("PRAGMA table_info(coins)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Get sample data
    print("\nSAMPLE DATA (first row):")
    cursor.execute("SELECT * FROM coins LIMIT 1")
    row = cursor.fetchone()
    if row:
        for i, value in enumerate(row):
            print(f"  {columns[i][1]}: {value}")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM coins")
    count = cursor.fetchone()[0]
    print(f"\nTotal coins: {count}")
    
    conn.close()
else:
    print(f"Database not found at {db_path}")