#!/usr/bin/env python3
"""
Inspect database structure to understand the schema
"""
import sqlite3
from pathlib import Path
from unicode_handler import safe_print

def inspect_database(db_path: Path):
    """Inspect database structure"""
    safe_print(f"\n=== Inspecting {db_path} ===")
    
    if not db_path.exists():
        safe_print(f"Database {db_path} does not exist")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            safe_print(f"Tables found: {tables}")
            
            # Inspect each table
            for table in tables:
                safe_print(f"\n--- Table: {table} ---")
                
                # Get column info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                safe_print("Columns:")
                for col in columns:
                    safe_print(f"  {col[1]} ({col[2]})")
                
                # Count records
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                safe_print(f"Records: {count}")
                
                # Show sample data if exists
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    rows = cursor.fetchall()
                    safe_print("Sample data:")
                    for row in rows:
                        safe_print(f"  {row}")
                        
    except Exception as e:
        safe_print(f"Error inspecting {db_path}: {e}")

def main():
    """Main inspection"""
    project_dir = Path.cwd()
    db_files = [
        project_dir / "data/trench.db",
        project_dir / "data/coins.db"
    ]
    
    for db_path in db_files:
        inspect_database(db_path)

if __name__ == "__main__":
    main()