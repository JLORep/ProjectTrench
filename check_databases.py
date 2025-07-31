#!/usr/bin/env python3
"""Check all database files and their content"""
import sqlite3
import os
from pathlib import Path

def check_database(db_path):
    """Check database tables and record counts"""
    try:
        print(f"\n=== {db_path} ===")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        # Get record counts
        for table in tables:
            if table != 'sqlite_sequence':
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f"{table}: {count} records")
        
        conn.close()
        return tables
    except Exception as e:
        print(f"Error checking {db_path}: {e}")
        return []

def main():
    """Check all database files"""
    db_files = [
        "data/coins.db",
        "data/trench.db", 
        "trenchcoat_devblog.db",
        "trenchcoat_historic.db",
        "trenchcoat_money.db"
    ]
    
    all_databases = {}
    
    for db_file in db_files:
        if os.path.exists(db_file):
            tables = check_database(db_file)
            all_databases[db_file] = tables
        else:
            print(f"\n=== {db_file} === (NOT FOUND)")
    
    print(f"\n=== SUMMARY ===")
    for db_file, tables in all_databases.items():
        print(f"{db_file}: {len(tables)} tables")
    
    return all_databases

if __name__ == "__main__":
    main()