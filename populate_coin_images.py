#!/usr/bin/env python3
"""
Populate coin images for top coins to test the image system
"""
import asyncio
import sqlite3
from coin_image_system import coin_image_system

async def populate_top_coins_images():
    """Fetch images for top coins by market cap"""
    
    # Get top 20 coins from database
    conn = sqlite3.connect('data/trench.db')
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT ticker, ca FROM coins 
    WHERE ticker IS NOT NULL AND ca IS NOT NULL
    AND (current_price_usd IS NOT NULL OR discovery_mc IS NOT NULL)
    ORDER BY market_cap_usd DESC NULLS LAST, discovery_mc DESC NULLS LAST
    LIMIT 20
    """)
    
    coins = cursor.fetchall()
    conn.close()
    
    print(f"Fetching images for {len(coins)} top coins...")
    
    # Fetch images
    for ticker, ca in coins:
        try:
            print(f"Fetching image for {ticker}...")
            coin_image = await coin_image_system.fetch_coin_image(ticker, ca)
            
            # Update database
            conn = sqlite3.connect('data/trench.db')
            cursor = conn.cursor()
            
            cursor.execute("""
            UPDATE coins 
            SET image_url = ?, image_source = ?, image_verified = ?
            WHERE ticker = ? AND ca = ?
            """, (coin_image.image_url, coin_image.image_source, coin_image.verified, ticker, ca))
            
            conn.commit()
            conn.close()
            
            print(f"  -> {coin_image.image_url[:50]}... from {coin_image.image_source}")
            
        except Exception as e:
            print(f"  -> Error: {e}")
        
        # Rate limiting
        await asyncio.sleep(1)
    
    print("Image population complete!")

if __name__ == "__main__":
    asyncio.run(populate_top_coins_images())