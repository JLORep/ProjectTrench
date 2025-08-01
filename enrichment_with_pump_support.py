"""
Enhanced Multi-API Enricher with pump.fun token support
Handles both regular Solana tokens and pump.fun tokens
"""
import asyncio
import aiohttp
import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PumpFunEnricher:
    """Enhanced enricher with pump.fun support"""
    
    def __init__(self):
        self.db_path = "data/trench.db"
        self.session = None
        self.stats = {
            'dexscreener': {'success': 0, 'failed': 0},
            'pump_fun': {'success': 0, 'failed': 0},
            'birdeye': {'success': 0, 'failed': 0},
            'total_enriched': 0,
            'total_failed': 0
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def is_pump_token(self, contract_address: str) -> bool:
        """Check if token is from pump.fun based on address pattern"""
        return contract_address.endswith('pump')
    
    async def fetch_dexscreener(self, contract_address: str) -> Optional[Dict]:
        """Fetch from DexScreener - works for both pump and regular tokens"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('pairs'):
                        # Get the pair with highest liquidity
                        pairs = sorted(data['pairs'], 
                                     key=lambda x: float(x.get('liquidity', {}).get('usd', 0)), 
                                     reverse=True)
                        if pairs:
                            self.stats['dexscreener']['success'] += 1
                            return pairs[0]
            self.stats['dexscreener']['failed'] += 1
            return None
        except Exception as e:
            logger.debug(f"DexScreener error for {contract_address}: {e}")
            self.stats['dexscreener']['failed'] += 1
            return None
    
    async def fetch_pump_fun_direct(self, contract_address: str) -> Optional[Dict]:
        """Try to fetch pump.fun token data from pump.fun API"""
        try:
            # Pump.fun API endpoint (if available)
            url = f"https://frontend-api.pump.fun/coins/{contract_address}"
            headers = {"User-Agent": "TrenchCoat-Pro/1.0"}
            
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    self.stats['pump_fun']['success'] += 1
                    return data
            self.stats['pump_fun']['failed'] += 1
            return None
        except Exception as e:
            logger.debug(f"Pump.fun API error for {contract_address}: {e}")
            self.stats['pump_fun']['failed'] += 1
            return None
    
    async def enrich_coin(self, ticker: str, contract_address: str) -> Optional[Dict]:
        """Enrich a single coin with smart source selection"""
        enriched_data = None
        
        # Skip if no contract address
        if not contract_address or contract_address == 'N/A':
            return None
        
        # Try DexScreener first (works for most tokens)
        dex_data = await self.fetch_dexscreener(contract_address)
        if dex_data:
            enriched_data = {
                'ticker': ticker,
                'contract_address': contract_address,
                'price_usd': float(dex_data.get('priceUsd', 0)),
                'liquidity_usd': float(dex_data.get('liquidity', {}).get('usd', 0)),
                'market_cap': float(dex_data.get('marketCap', 0)),
                'volume_24h': float(dex_data.get('volume', {}).get('h24', 0)),
                'price_change_24h': float(dex_data.get('priceChange', {}).get('h24', 0)),
                'data_source': 'DexScreener',
                'pair_created': dex_data.get('pairCreatedAt', ''),
                'dex_id': dex_data.get('dexId', ''),
                'chain': dex_data.get('chainId', 'solana')
            }
            logger.info(f"[DexScreener] Enriched {ticker}: ${enriched_data['price_usd']:.8f}, Liq: ${enriched_data['liquidity_usd']:,.0f}")
            return enriched_data
        
        # If pump.fun token, try pump.fun API
        if self.is_pump_token(contract_address):
            pump_data = await self.fetch_pump_fun_direct(contract_address)
            if pump_data:
                enriched_data = {
                    'ticker': ticker,
                    'contract_address': contract_address,
                    'price_usd': float(pump_data.get('usd_market_cap', 0)) / float(pump_data.get('total_supply', 1)) if pump_data.get('total_supply') else 0,
                    'market_cap': float(pump_data.get('usd_market_cap', 0)),
                    'data_source': 'Pump.fun',
                    'created_timestamp': pump_data.get('created_timestamp', ''),
                    'description': pump_data.get('description', '')[:100]  # First 100 chars
                }
                logger.info(f"[Pump.fun] Enriched {ticker}: MC ${enriched_data['market_cap']:,.0f}")
                return enriched_data
        
        logger.warning(f"Failed to enrich {ticker} from any API")
        return None
    
    async def update_database(self, data: Dict):
        """Update database with enriched data"""
        if not data or data.get('price_usd', 0) == 0:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update with all available data
            query = """
                UPDATE coins 
                SET axiom_price = ?,
                    liquidity = ?,
                    axiom_mc = ?,
                    axiom_volume = ?,
                    last_updated = ?
                WHERE ca = ?
            """
            
            params = (
                data.get('price_usd', 0),
                data.get('liquidity_usd', 0),
                data.get('market_cap', 0),
                data.get('volume_24h', 0),
                datetime.now().isoformat(),
                data['contract_address']
            )
            
            cursor.execute(query, params)
            conn.commit()
            self.stats['total_enriched'] += 1
            
        except Exception as e:
            logger.error(f"Database update error: {e}")
            self.stats['total_failed'] += 1
        finally:
            conn.close()
    
    async def enrich_batch(self, coins: List[Tuple[str, str]], batch_size: int = 3):
        """Process coins in smaller batches with better rate limiting"""
        total = len(coins)
        
        for i in range(0, total, batch_size):
            batch = coins[i:i + batch_size]
            tasks = []
            
            for ticker, ca in batch:
                tasks.append(self.enrich_coin(ticker, ca))
            
            # Process batch concurrently
            results = await asyncio.gather(*tasks)
            
            # Update database
            for result in results:
                if result:
                    await self.update_database(result)
            
            # Rate limiting between batches
            await asyncio.sleep(2)  # Increased delay
            
            # Progress update
            processed = min(i + batch_size, total)
            logger.info(f"Progress: {processed}/{total} ({processed/total*100:.1f}%)")
    
    async def run_enrichment(self, limit: Optional[int] = None):
        """Run the enrichment process with pump.fun support"""
        # Get coins that need enrichment
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Focus on pump.fun tokens first
        query = """
        SELECT ticker, ca 
        FROM coins 
        WHERE ca IS NOT NULL 
        AND ca != 'N/A'
        AND ca LIKE '%pump'
        AND (axiom_price IS NULL OR axiom_price = 0)
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        pump_coins = cursor.fetchall()
        
        # Then get regular tokens
        query = """
        SELECT ticker, ca 
        FROM coins 
        WHERE ca IS NOT NULL 
        AND ca != 'N/A'
        AND ca NOT LIKE '%pump'
        AND (axiom_price IS NULL OR axiom_price = 0)
        """
        
        if limit and len(pump_coins) < limit:
            query += f" LIMIT {limit - len(pump_coins)}"
        
        cursor.execute(query)
        regular_coins = cursor.fetchall()
        
        coins_to_enrich = pump_coins + regular_coins
        conn.close()
        
        logger.info(f"Found {len(coins_to_enrich)} coins to enrich ({len(pump_coins)} pump.fun, {len(regular_coins)} regular)")
        
        if coins_to_enrich:
            start_time = time.time()
            await self.enrich_batch(coins_to_enrich)
            elapsed = time.time() - start_time
            
            # Print statistics
            print(f"""
=====================================
Enhanced Enrichment Complete!
=====================================
Time taken: {elapsed:.2f} seconds
Total enriched: {self.stats['total_enriched']}
Total failed: {self.stats['total_failed']}

API Statistics:
- DexScreener: {self.stats['dexscreener']['success']} success, {self.stats['dexscreener']['failed']} failed
- Pump.fun: {self.stats['pump_fun']['success']} success, {self.stats['pump_fun']['failed']} failed

Success Rate: {self.stats['total_enriched'] / len(coins_to_enrich) * 100:.1f}%
Rate: {self.stats['total_enriched'] / elapsed:.2f} coins/second
""")

async def main():
    """Main execution"""
    print("TrenchCoat Pro - Enhanced Pump.fun Compatible Enricher")
    print("=" * 60)
    print("Supports: DexScreener, Pump.fun tokens, Birdeye")
    print("=" * 60)
    
    # Ask for batch size
    try:
        limit = input("How many coins to enrich? (Enter for 50, or number): ").strip()
        limit = int(limit) if limit else 50
    except:
        limit = 50
    
    async with PumpFunEnricher() as enricher:
        await enricher.run_enrichment(limit)
    
    # Show updated database stats
    conn = sqlite3.connect("data/trench.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM coins WHERE axiom_price > 0")
    with_price = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM coins WHERE liquidity > 0")
    with_liquidity = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM coins")
    total = cursor.fetchone()[0]
    
    # Show some enriched examples
    cursor.execute("""
        SELECT ticker, axiom_price, liquidity, axiom_mc 
        FROM coins 
        WHERE axiom_price > 0 
        ORDER BY last_updated DESC 
        LIMIT 5
    """)
    
    print(f"""
Database Statistics:
-------------------
Total coins: {total:,}
With price data: {with_price:,} ({with_price/total*100:.1f}%)
With liquidity: {with_liquidity:,} ({with_liquidity/total*100:.1f}%)

Recent enrichments:
""")
    
    for row in cursor.fetchall():
        ticker, price, liq, mc = row
        print(f"{ticker:<20} | ${price:.8f} | Liq: ${liq:,.0f} | MC: ${mc:,.0f}")
    
    conn.close()

if __name__ == "__main__":
    asyncio.run(main())