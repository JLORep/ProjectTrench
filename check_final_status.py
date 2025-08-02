import sqlite3

conn = sqlite3.connect('data/trench.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM coins WHERE current_price_usd IS NOT NULL')
enriched = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM coins')
total = cursor.fetchone()[0]

print(f'DATABASE STATUS: {enriched:,} coins enriched of {total:,} total ({enriched/total*100:.1f}% coverage)')

cursor.execute('SELECT ticker, current_price_usd, market_cap_usd FROM coins WHERE current_price_usd IS NOT NULL AND market_cap_usd IS NOT NULL ORDER BY market_cap_usd DESC LIMIT 3')
top = cursor.fetchall()

print('TOP COINS BY MARKET CAP:')
for ticker, price, mcap in top:
    print(f'  {ticker}: ${float(price):.8f} (MCap: ${float(mcap):,.0f})')

conn.close()