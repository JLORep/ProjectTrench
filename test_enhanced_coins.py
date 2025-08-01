#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test enhanced coin data functions"""

import sqlite3
import os

# Check database exists
if os.path.exists('data/trench.db'):
    print('SUCCESS: Database found')
    
    # Test connection and basic query
    conn = sqlite3.connect('data/trench.db')
    cursor = conn.cursor()
    
    # Test the enhanced query
    cursor.execute('''
        SELECT ticker, ca, discovery_price, axiom_price, smart_wallets, liquidity, axiom_mc, 
               peak_volume, discovery_mc, axiom_volume, discovery_time
        FROM coins 
        WHERE ticker IS NOT NULL AND ticker != ''
        ORDER BY ticker
        LIMIT 5
    ''')
    
    rows = cursor.fetchall()
    print(f'SUCCESS: Enhanced query successful: {len(rows)} rows')
    
    # Test sample data for completeness analysis
    for row in rows:
        ticker = row[0]
        fields_present = sum(1 for field in row if field is not None and field != '' and field != 0)
        completeness = fields_present / len(row) * 100
        print(f'DATA: {ticker}: {completeness:.0f}% complete ({fields_present}/{len(row)} fields)')
    
    conn.close()
    print('SUCCESS: Enhanced coin data system test successful!')
else:
    print('ERROR: Database not found')