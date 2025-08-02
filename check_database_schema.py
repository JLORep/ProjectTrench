#!/usr/bin/env python3
import sqlite3

def check_database():
    conn = sqlite3.connect('data/trench.db')
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute('PRAGMA table_info(coins)')
    columns = [row[1] for row in cursor.fetchall()]
    print('Columns:', columns)
    
    # Get total count
    cursor.execute('SELECT COUNT(*) FROM coins')
    total = cursor.fetchone()[0]
    print('Total coins:', total)
    
    # Get sample data
    cursor.execute('SELECT ticker, ca, discovery_price, axiom_price FROM coins WHERE ticker IS NOT NULL LIMIT 10')
    print('\nSample data:')
    for row in cursor.fetchall():
        ticker, ca, disc_price, axiom_price = row
        ca_short = ca[:20] + '...' if ca and len(ca) > 20 else ca
        print(f'Ticker: {ticker}, CA: {ca_short}, Discovery: {disc_price}, Axiom: {axiom_price}')
    
    # Check enrichment status
    cursor.execute('SELECT COUNT(*) FROM coins WHERE discovery_price > 0 OR axiom_price > 0')
    enriched = cursor.fetchone()[0]
    print(f'\nEnrichment status: {enriched}/{total} coins have price data ({enriched/total*100:.1f}%)')
    
    conn.close()

if __name__ == '__main__':
    check_database()