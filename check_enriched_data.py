import sqlite3

conn = sqlite3.connect('data/trench.db')
cursor = conn.cursor()

# Get counts
cursor.execute('SELECT COUNT(*) FROM coins WHERE axiom_price > 0')
price_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM coins WHERE liquidity > 0')
liquidity_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM coins')
total_count = cursor.fetchone()[0]

print("Database Enrichment Results:")
print("=" * 40)
print(f"Total coins: {total_count:,}")
print(f"Coins with price data: {price_count:,} ({price_count/total_count*100:.1f}%)")
print(f"Coins with liquidity: {liquidity_count:,} ({liquidity_count/total_count*100:.1f}%)")

# Show sample data
print("\nSample Enriched Coins:")
print("-" * 40)
cursor.execute('''
    SELECT ticker, axiom_price, liquidity, axiom_mc, axiom_volume 
    FROM coins 
    WHERE axiom_price > 0 
    ORDER BY axiom_mc DESC 
    LIMIT 10
''')

for row in cursor.fetchall():
    ticker, price, liquidity, mc, volume = row
    print(f"\n{ticker}:")
    print(f"  Price: ${price:.8f}")
    print(f"  Liquidity: ${liquidity:,.0f}")
    print(f"  Market Cap: ${mc:,.0f}")
    print(f"  Volume: ${volume:,.0f}")

conn.close()