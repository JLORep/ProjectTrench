import sqlite3

# Check sample contract addresses
conn = sqlite3.connect('data/trench.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT ticker, ca 
    FROM coins 
    WHERE ca IS NOT NULL 
    AND ca != 'N/A'
    AND (axiom_price IS NULL OR axiom_price = 0)
    LIMIT 10
''')

print("Sample coins needing enrichment:")
print("-" * 60)
for row in cursor.fetchall():
    ticker, ca = row
    print(f"{ticker:<20} | {ca}")

# Check a few with existing data
cursor.execute('''
    SELECT ticker, ca, axiom_price, liquidity
    FROM coins 
    WHERE axiom_price > 0
    LIMIT 5
''')

print("\nSample coins with data:")
print("-" * 60)
for row in cursor.fetchall():
    ticker, ca, price, liq = row
    print(f"{ticker:<20} | ${price:.8f} | Liq: ${liq:,.0f}")

conn.close()