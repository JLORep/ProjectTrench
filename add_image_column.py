#!/usr/bin/env python3
"""
Add image_url column to coins table and populate with existing image data
"""
import sqlite3
import json
from pathlib import Path

def add_image_column():
    """Add image_url and image_source columns to coins table"""
    conn = sqlite3.connect('data/trench.db')
    cursor = conn.cursor()
    
    try:
        # Add image_url column
        cursor.execute('ALTER TABLE coins ADD COLUMN image_url TEXT')
        print("Added image_url column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("image_url column already exists")
        else:
            raise
    
    try:
        # Add image_source column
        cursor.execute('ALTER TABLE coins ADD COLUMN image_source TEXT')
        print("Added image_source column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("image_source column already exists")
        else:
            raise
    
    try:
        # Add image_verified column
        cursor.execute('ALTER TABLE coins ADD COLUMN image_verified INTEGER')
        print("Added image_verified column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("image_verified column already exists")
        else:
            raise
    
    # Load existing image metadata
    metadata_file = Path("data/coin_images/image_metadata.json")
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            image_metadata = json.load(f)
        
        print(f"Found {len(image_metadata)} cached images")
        
        # Update coins with image data
        updated = 0
        for cache_key, data in image_metadata.items():
            ticker = data.get('ticker')
            contract_address = data.get('contract_address')
            image_url = data.get('image_url')
            image_source = data.get('image_source')
            verified = data.get('verified', False)
            
            if ticker and contract_address and image_url:
                cursor.execute('''
                UPDATE coins 
                SET image_url = ?, image_source = ?, image_verified = ?
                WHERE ticker = ? AND ca = ?
                ''', (image_url, image_source, verified, ticker, contract_address))
                
                if cursor.rowcount > 0:
                    updated += 1
        
        print(f"Updated {updated} coins with image data")
    
    conn.commit()
    conn.close()
    
    print("Database schema updated successfully!")

if __name__ == "__main__":
    add_image_column()