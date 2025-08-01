"""
Enhanced Multi-API Enricher for TrenchCoat Pro
Uses multiple APIs with fallback strategy for maximum data coverage
"""
import asyncio
import aiohttp
import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnrichedCoinData:
    """Standardized coin data structure"""
    ticker: str
    contract_address: str
    price_usd: float = 0
    liquidity_usd: float = 0
    market_cap: float = 0
    volume_24h: float = 0
    holders: int = 0
    price_change_24h: float = 0
    last_updated: str = ""
    data_source: str = ""
    
class MultiAPIEnricher:
    """Enhanced enricher using multiple API sources"""
    
    def __init__(self):
        self.db_path = "data/trench.db"
        self.session = None
        self.stats = {
            'dexscreener': {'success': 0, 'failed': 0},
            'jupiter': {'success': 0, 'failed': 0},
            'coingecko': {'success': 0, 'failed': 0},
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
    
    async def fetch_dexscreener(self, contract_address: str) -> Optional[Dict]:
        """Primary source - DexScreener API"""
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
    
    async def fetch_jupiter(self, contract_address: str) -> Optional[Dict]:
        """Secondary source - Jupiter Price API"""
        try:
            url = f"https://price.jup.ag/v4/price?ids={contract_address}"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data') and contract_address in data['data']:
                        self.stats['jupiter']['success'] += 1
                        return data['data'][contract_address]
            self.stats['jupiter']['failed'] += 1
            return None
        except Exception as e:
            logger.debug(f"Jupiter error for {contract_address}: {e}")
            self.stats['jupiter']['failed'] += 1
            return None
    
    async def fetch_birdeye(self, contract_address: str) -> Optional[Dict]:
        """Tertiary source - Birdeye API (if available)"""
        try:
            # Birdeye requires API key, but we can try public endpoints
            url = f"https://public-api.birdeye.so/public/token_overview?address={contract_address}"
            headers = {"User-Agent": "TrenchCoat-Pro/1.0"}
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        self.stats['birdeye']['success'] += 1
                        return data.get('data')
            self.stats['birdeye']['failed'] += 1
            return None
        except Exception as e:
            logger.debug(f"Birdeye error for {contract_address}: {e}")
            self.stats['birdeye']['failed'] += 1
            return None
    
    async def fetch_coingecko_solana(self, contract_address: str) -> Optional[Dict]:
        """Fallback source - CoinGecko for Solana tokens"""
        try:
            # CoinGecko requires finding the coin ID first
            url = f"https://api.coingecko.com/api/v3/coins/solana/contract/{contract_address}"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    self.stats['coingecko']['success'] += 1
                    return data
            self.stats['coingecko']['failed'] += 1
            return None
        except Exception as e:
            logger.debug(f"CoinGecko error for {contract_address}: {e}")
            self.stats['coingecko']['failed'] += 1
            return None
    
    def parse_dexscreener_data(self, data: Dict) -> EnrichedCoinData:
        """Parse DexScreener response into standard format"""
        return EnrichedCoinData(
            ticker="",  # Will be filled from DB
            contract_address=data.get('baseToken', {}).get('address', ''),
            price_usd=float(data.get('priceUsd', 0)),
            liquidity_usd=float(data.get('liquidity', {}).get('usd', 0)),
            market_cap=float(data.get('marketCap', 0)),
            volume_24h=float(data.get('volume', {}).get('h24', 0)),
            price_change_24h=float(data.get('priceChange', {}).get('h24', 0)),
            data_source="DexScreener",
            last_updated=datetime.now().isoformat()
        )
    
    def parse_jupiter_data(self, data: Dict) -> EnrichedCoinData:
        """Parse Jupiter response into standard format"""
        return EnrichedCoinData(
            ticker="",
            contract_address=data.get('id', ''),
            price_usd=float(data.get('price', 0)),
            data_source="Jupiter",
            last_updated=datetime.now().isoformat()
        )
    
    def parse_birdeye_data(self, data: Dict) -> EnrichedCoinData:
        """Parse Birdeye response into standard format"""
        return EnrichedCoinData(
            ticker="",
            contract_address=data.get('address', ''),
            price_usd=float(data.get('price', 0)),
            liquidity_usd=float(data.get('liquidity', 0)),
            market_cap=float(data.get('mc', 0)),
            volume_24h=float(data.get('v24hUSD', 0)),
            holders=int(data.get('holder', 0)),
            price_change_24h=float(data.get('v24hChangePercent', 0)),
            data_source="Birdeye",
            last_updated=datetime.now().isoformat()
        )
    
    def parse_coingecko_data(self, data: Dict) -> EnrichedCoinData:
        """Parse CoinGecko response into standard format"""
        market_data = data.get('market_data', {})
        return EnrichedCoinData(
            ticker=data.get('symbol', '').upper(),
            contract_address=data.get('contract_address', ''),
            price_usd=float(market_data.get('current_price', {}).get('usd', 0)),
            market_cap=float(market_data.get('market_cap', {}).get('usd', 0)),
            volume_24h=float(market_data.get('total_volume', {}).get('usd', 0)),
            price_change_24h=float(market_data.get('price_change_percentage_24h', 0)),
            data_source="CoinGecko",
            last_updated=datetime.now().isoformat()
        )
    
    async def enrich_coin_multi_source(self, ticker: str, contract_address: str) -> Optional[EnrichedCoinData]:
        """Use comprehensive API system for maximum data coverage"""
        # Skip if no contract address
        if not contract_address or contract_address == 'N/A':
            return None
        
        try:
            # Import the comprehensive API system
            from src.data.free_api_providers import FreeAPIProviders
            
            async with FreeAPIProviders() as api:
                # Get comprehensive data from all sources
                comprehensive_data = await api.get_comprehensive_data(contract_address, ticker)
                
                if comprehensive_data and comprehensive_data.get('price'):
                    # Convert to EnrichedCoinData format
                    enriched_data = EnrichedCoinData(
                        ticker=ticker,
                        contract_address=contract_address,
                        price_usd=float(comprehensive_data.get('price', 0)),
                        liquidity_usd=float(comprehensive_data.get('liquidity', 0)),
                        market_cap=float(comprehensive_data.get('market_cap', 0)),
                        volume_24h=float(comprehensive_data.get('volume_24h', 0)),
                        holders=int(comprehensive_data.get('total_holders', 0)),
                        price_change_24h=float(comprehensive_data.get('price_change_24h', 0)),
                        data_source=f"Comprehensive ({len(comprehensive_data.get('data_sources', []))} sources)",
                        last_updated=datetime.now().isoformat()
                    )
                    
                    sources = comprehensive_data.get('data_sources', [])
                    logger.info(f"[Comprehensive] Enriched {ticker}: ${enriched_data.price_usd:.8f} from {len(sources)} sources")
                    return enriched_data
                
        except Exception as e:
            logger.warning(f"Comprehensive API failed for {ticker}, falling back to legacy: {e}")
        
        # Fallback to original logic if comprehensive system fails
        # Try DexScreener first (most comprehensive for DEX tokens)
        dex_data = await self.fetch_dexscreener(contract_address)
        if dex_data:
            enriched_data = self.parse_dexscreener_data(dex_data)
            enriched_data.ticker = ticker
            logger.info(f"[DexScreener] Enriched {ticker}: ${enriched_data.price_usd:.8f}")
            return enriched_data
        
        # Try Birdeye (good for Solana tokens)
        birdeye_data = await self.fetch_birdeye(contract_address)
        if birdeye_data:
            enriched_data = self.parse_birdeye_data(birdeye_data)
            enriched_data.ticker = ticker
            logger.info(f"[Birdeye] Enriched {ticker}: ${enriched_data.price_usd:.8f}")
            return enriched_data
        
        # Try Jupiter for price at least
        jupiter_data = await self.fetch_jupiter(contract_address)
        if jupiter_data:
            enriched_data = self.parse_jupiter_data(jupiter_data)
            enriched_data.ticker = ticker
            logger.info(f"[Jupiter] Got price for {ticker}: ${enriched_data.price_usd:.8f}")
            return enriched_data
        
        # Last resort - CoinGecko (limited for new tokens)
        coingecko_data = await self.fetch_coingecko_solana(contract_address)
        if coingecko_data:
            enriched_data = self.parse_coingecko_data(coingecko_data)
            enriched_data.ticker = ticker
            logger.info(f"[CoinGecko] Enriched {ticker}: ${enriched_data.price_usd:.8f}")
            return enriched_data
        
        logger.warning(f"Failed to enrich {ticker} from any API")
        return None
    
    async def update_database(self, data: EnrichedCoinData):
        """Update database with enriched data"""
        if not data or data.price_usd == 0:
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
                    smart_wallets = CASE WHEN ? > 0 THEN ? ELSE smart_wallets END
                WHERE ca = ?
            """
            
            params = (
                data.price_usd,
                data.liquidity_usd,
                data.market_cap,
                data.volume_24h,
                data.holders,  # Only update if we have holder data
                data.holders,
                data.contract_address
            )
            
            cursor.execute(query, params)
            conn.commit()
            self.stats['total_enriched'] += 1
            
        except Exception as e:
            logger.error(f"Database update error: {e}")
            self.stats['total_failed'] += 1
        finally:
            conn.close()
    
    async def enrich_batch(self, coins: List[Tuple[str, str]], batch_size: int = 5):
        """Process coins in batches with rate limiting"""
        total = len(coins)
        
        for i in range(0, total, batch_size):
            batch = coins[i:i + batch_size]
            tasks = []
            
            for ticker, ca in batch:
                tasks.append(self.enrich_coin_multi_source(ticker, ca))
            
            # Process batch concurrently
            results = await asyncio.gather(*tasks)
            
            # Update database
            for result in results:
                if result:
                    await self.update_database(result)
            
            # Rate limiting between batches
            await asyncio.sleep(1)
            
            # Progress update
            processed = min(i + batch_size, total)
            logger.info(f"Progress: {processed}/{total} ({processed/total*100:.1f}%)")
    
    async def run_enrichment(self, limit: Optional[int] = None):
        """Run the multi-API enrichment process"""
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
            
            # Print statistics
            print(f"""
=====================================
Multi-API Enrichment Complete!
=====================================
Time taken: {elapsed:.2f} seconds
Total enriched: {self.stats['total_enriched']}
Total failed: {self.stats['total_failed']}

API Statistics:
- DexScreener: {self.stats['dexscreener']['success']} success, {self.stats['dexscreener']['failed']} failed
- Birdeye: {self.stats['birdeye']['success']} success, {self.stats['birdeye']['failed']} failed  
- Jupiter: {self.stats['jupiter']['success']} success, {self.stats['jupiter']['failed']} failed
- CoinGecko: {self.stats['coingecko']['success']} success, {self.stats['coingecko']['failed']} failed

Success Rate: {self.stats['total_enriched'] / len(coins_to_enrich) * 100:.1f}%
Rate: {self.stats['total_enriched'] / elapsed:.2f} coins/second
""")

async def main():
    """Main execution"""
    print("TrenchCoat Pro - Multi-API Database Enricher")
    print("=" * 50)
    print("APIs: DexScreener, Birdeye, Jupiter, CoinGecko")
    print("=" * 50)
    
    # Ask for batch size
    try:
        limit = input("How many coins to enrich? (Enter for all, or number): ").strip()
        limit = int(limit) if limit else None
    except:
        limit = 100
    
    async with MultiAPIEnricher() as enricher:
        await enricher.run_enrichment(limit)
    
    # Show updated database stats
    conn = sqlite3.connect("data/trench.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM coins WHERE axiom_price > 0")
    with_price = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM coins WHERE liquidity > 0")
    with_liquidity = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM coins WHERE smart_wallets > 0")
    with_holders = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM coins")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"""
Database Statistics:
-------------------
Total coins: {total:,}
With price data: {with_price:,} ({with_price/total*100:.1f}%)
With liquidity: {with_liquidity:,} ({with_liquidity/total*100:.1f}%)
With holder data: {with_holders:,} ({with_holders/total*100:.1f}%)
""")

if __name__ == "__main__":
    asyncio.run(main())