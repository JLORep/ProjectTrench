"""
Fix Database Enrichment - Update trench.db with live data from APIs
Specifically designed to fill axiom_price, liquidity, market cap, and volume
"""
import asyncio
import aiohttp
import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrenchDatabaseEnricher:
    """Enrich trench.db with live data from free APIs"""
    
    def __init__(self):
        self.db_path = "data/trench.db"
        self.session = None
        self.enriched_count = 0
        self.failed_count = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_dexscreener_data(self, contract_address: str) -> Optional[Dict]:
        """Fetch data from DexScreener API"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('pairs'):
                        # Get the main pair (highest liquidity)
                        pairs = sorted(data['pairs'], 
                                     key=lambda x: float(x.get('liquidity', {}).get('usd', 0)), 
                                     reverse=True)
                        if pairs:
                            return pairs[0]
            return None
        except Exception as e:
            logger.error(f"DexScreener error for {contract_address}: {e}")
            return None
    
    async def fetch_jupiter_price(self, contract_address: str) -> Optional[float]:
        """Fetch price from Jupiter API"""
        try:
            url = f"https://price.jup.ag/v4/price?ids={contract_address}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data') and contract_address in data['data']:
                        return data['data'][contract_address].get('price', 0)
            return None
        except Exception as e:
            logger.error(f"Jupiter error for {contract_address}: {e}")
            return None
    
    async def enrich_coin(self, ticker: str, contract_address: str) -> Dict:
        """Enrich a single coin with data from multiple sources"""
        enriched_data = {
            'ticker': ticker,
            'ca': contract_address,
            'axiom_price': None,
            'liquidity': None,
            'axiom_mc': None,
            'axiom_volume': None,
            'updated': False
        }
        
        # Skip if no contract address
        if not contract_address or contract_address == 'N/A':
            return enriched_data
        
        # Fetch from DexScreener (primary source)
        dex_data = await self.fetch_dexscreener_data(contract_address)
        if dex_data:
            enriched_data['axiom_price'] = float(dex_data.get('priceUsd', 0))
            enriched_data['liquidity'] = float(dex_data.get('liquidity', {}).get('usd', 0))
            enriched_data['axiom_mc'] = float(dex_data.get('marketCap', 0))
            enriched_data['axiom_volume'] = float(dex_data.get('volume', {}).get('h24', 0))
            enriched_data['updated'] = True
            logger.info(f"[SUCCESS] Enriched {ticker} from DexScreener")
        else:
            # Try Jupiter as backup for price
            jupiter_price = await self.fetch_jupiter_price(contract_address)
            if jupiter_price:
                enriched_data['axiom_price'] = jupiter_price
                enriched_data['updated'] = True
                logger.info(f"[JUPITER] Got price for {ticker} from Jupiter")
        
        return enriched_data
    
    async def update_database(self, enriched_data: Dict):
        """Update the database with enriched data"""
        if not enriched_data['updated']:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update only if we have new data
            updates = []
            params = []
            
            if enriched_data['axiom_price'] is not None:
                updates.append("axiom_price = ?")
                params.append(enriched_data['axiom_price'])
            
            if enriched_data['liquidity'] is not None:
                updates.append("liquidity = ?")
                params.append(enriched_data['liquidity'])
            
            if enriched_data['axiom_mc'] is not None:
                updates.append("axiom_mc = ?")
                params.append(enriched_data['axiom_mc'])
            
            if enriched_data['axiom_volume'] is not None:
                updates.append("axiom_volume = ?")
                params.append(enriched_data['axiom_volume'])
            
            if updates:
                query = f"UPDATE coins SET {', '.join(updates)} WHERE ca = ?"
                params.append(enriched_data['ca'])
                cursor.execute(query, params)
                conn.commit()
                self.enriched_count += 1
                
        except Exception as e:
            logger.error(f"Database update error: {e}")
            self.failed_count += 1
        finally:
            conn.close()
    
    async def enrich_batch(self, coins: List[tuple], batch_size: int = 10):
        """Enrich a batch of coins"""
        for i in range(0, len(coins), batch_size):
            batch = coins[i:i + batch_size]
            tasks = []
            
            for ticker, ca in batch:
                tasks.append(self.enrich_coin(ticker, ca))
            
            # Process batch
            results = await asyncio.gather(*tasks)
            
            # Update database
            for result in results:
                await self.update_database(result)
            
            # Rate limiting
            await asyncio.sleep(2)  # Respect API limits
            
            logger.info(f"Progress: {i + len(batch)}/{len(coins)} coins processed")
    
    async def run_enrichment(self, limit: Optional[int] = None):
        """Run the enrichment process"""
        # Get coins that need enrichment
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT ticker, ca 
        FROM coins 
        WHERE ca IS NOT NULL 
        AND ca != 'N/A'
        AND (axiom_price IS NULL OR axiom_price = 0 
             OR liquidity IS NULL OR liquidity = 0)
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        coins_to_enrich = cursor.fetchall()
        conn.close()
        
        logger.info(f"Found {len(coins_to_enrich)} coins to enrich")
        
        if coins_to_enrich:
            start_time = time.time()
            await self.enrich_batch(coins_to_enrich)
            elapsed = time.time() - start_time
            
            logger.info(f"""
Enrichment Complete!
-------------------
Successfully enriched: {self.enriched_count} coins
Failed: {self.failed_count} coins
Time taken: {elapsed:.2f} seconds
Rate: {self.enriched_count / elapsed:.2f} coins/second
""")

async def main():
    """Main enrichment process"""
    print("TrenchCoat Pro - Database Enrichment Fix")
    print("=" * 50)
    
    # Ask user for batch size
    try:
        limit = input("How many coins to enrich? (Enter for all, or number): ").strip()
        limit = int(limit) if limit else None
    except:
        limit = 100  # Default to 100 for testing
    
    async with TrenchDatabaseEnricher() as enricher:
        await enricher.run_enrichment(limit)
    
    # Show updated stats
    conn = sqlite3.connect("data/trench.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM coins WHERE axiom_price > 0")
    with_price = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM coins WHERE liquidity > 0")
    with_liquidity = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM coins")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"""
Database Stats After Enrichment:
--------------------------------
Total coins: {total:,}
With price data: {with_price:,} ({with_price/total*100:.1f}%)
With liquidity: {with_liquidity:,} ({with_liquidity/total*100:.1f}%)
""")

if __name__ == "__main__":
    asyncio.run(main())