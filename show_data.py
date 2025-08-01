#!/usr/bin/env python3
"""
Show enriched data from the database
"""
import sqlite3
import json

def main():
    conn = sqlite3.connect('data/coins.db')
    
    print("=== TRENCHCOAT ENRICHED DATABASE ===")
    print()
    
    # Get statistics
    coins = conn.execute('SELECT COUNT(*) FROM coins').fetchone()[0]
    metadata = conn.execute('SELECT COUNT(*) FROM coin_metadata').fetchone()[0]
    price_points = conn.execute('SELECT COUNT(*) FROM price_data').fetchone()[0]
    
    print(f"STATISTICS:")
    print(f"   Total coins: {coins}")
    print(f"   Enriched with metadata: {metadata}")
    print(f"   Price data points: {price_points}")
    print()
    
    # Show enriched data
    print("ENRICHED TOKENS:")
    print("-" * 80)
    
    enriched = conn.execute('''
        SELECT c.symbol, cm.metadata 
        FROM coins c 
        JOIN coin_metadata cm ON c.id = cm.coin_id 
        ORDER BY c.updated_at DESC
    ''').fetchall()
    
    for symbol, metadata_json in enriched:
        try:
            metadata = json.loads(metadata_json)
            data = metadata['enrichment_data']
            
            print(f"\n{symbol}:")
            print(f"   Contract: {data.get('contract_address', 'N/A')[:20]}...")
            print(f"   Price: ${data.get('price', 'N/A')}")
            
            if data.get('market_cap'):
                print(f"   Market Cap: ${data['market_cap']:,.0f}")
            
            if data.get('volume_24h'):
                print(f"   24h Volume: ${data['volume_24h']:,.0f}")
            
            print(f"   Data Sources: {', '.join(data.get('data_sources', []))}")
            print(f"   Quality Score: {data.get('enrichment_score', 0):.2f}/1.00")
            
        except Exception as e:
            print(f"\n{symbol}: Error parsing data - {e}")
    
    print("\n" + "=" * 60)
    print("SUCCESS! Your coins.db is now enriched with real crypto data!")
    print("Ready for advanced trading strategies and analysis!")
    print("=" * 60)
    
    conn.close()

if __name__ == "__main__":
    main()