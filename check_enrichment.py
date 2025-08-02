import sqlite3

conn = sqlite3.connect('data/trench.db')
cursor = conn.cursor()

# Get total count
cursor.execute('SELECT COUNT(*) FROM coins WHERE current_price_usd IS NOT NULL')
enriched_count = cursor.fetchone()[0]

# Get sample enriched data
cursor.execute('''
    SELECT ca, ticker, current_price_usd, current_volume_24h, market_cap_usd, enrichment_timestamp 
    FROM coins 
    WHERE current_price_usd IS NOT NULL 
    ORDER BY current_price_usd DESC 
    LIMIT 5
''')
results = cursor.fetchall()

print(f"Total coins enriched with price data: {enriched_count}")
print("\nTop 5 enriched coins by price:")
print("-" * 60)

for r in results:
    ca, ticker, price, volume, mcap, timestamp = r
    price_str = f"${float(price):.8f}" if price else "N/A"
    volume_str = f", Vol: ${float(volume):,.0f}" if volume else ""
    mcap_str = f", MCap: ${float(mcap):,.0f}" if mcap else ""
    time_str = timestamp[:19] if timestamp else "N/A"
    
    print(f"  {ticker}: {price_str}{volume_str}{mcap_str}")
    print(f"    Updated: {time_str}")
    print()

conn.close()