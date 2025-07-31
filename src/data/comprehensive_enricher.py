#!/usr/bin/env python3
"""
COMPREHENSIVE SOLANA MEMECOIN DATA ENRICHER
Uses every possible free API to get maximum data coverage
"""
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from loguru import logger
import sqlite3
import pandas as pd

@dataclass
class ComprehensiveTokenData:
    """Complete token data from all sources"""
    # Basic info
    contract_address: str
    symbol: str
    name: str
    
    # Price data
    price_usd: float = 0
    price_sol: float = 0
    price_change_5m: float = 0
    price_change_1h: float = 0
    price_change_6h: float = 0
    price_change_24h: float = 0
    
    # Volume data
    volume_5m: float = 0
    volume_1h: float = 0
    volume_6h: float = 0
    volume_24h: float = 0
    volume_7d: float = 0
    
    # Market data
    market_cap: float = 0
    fully_diluted_valuation: float = 0
    circulating_supply: float = 0
    total_supply: float = 0
    max_supply: float = 0
    
    # Liquidity data
    liquidity_usd: float = 0
    liquidity_sol: float = 0
    liquidity_locked: bool = False
    liquidity_lock_duration: int = 0
    
    # Holder data
    holder_count: int = 0
    top_10_holders_percent: float = 0
    top_20_holders_percent: float = 0
    whale_count: int = 0
    
    # DEX data
    dex_pairs: List[Dict] = field(default_factory=list)
    main_dex: str = ""
    pair_count: int = 0
    
    # Social data
    twitter_followers: int = 0
    telegram_members: int = 0
    discord_members: int = 0
    website_url: str = ""
    
    # Technical indicators
    rsi_14: float = 0
    sma_20: float = 0
    ema_12: float = 0
    bollinger_upper: float = 0
    bollinger_lower: float = 0
    
    # On-chain data
    creation_time: datetime = None
    creator_address: str = ""
    creator_still_holds: bool = False
    creator_balance_percent: float = 0
    
    # Trading data
    buy_pressure: float = 0
    sell_pressure: float = 0
    trade_count_24h: int = 0
    unique_traders_24h: int = 0
    
    # Risk metrics
    rug_risk_score: float = 0
    honeypot_risk: float = 0
    mint_disabled: bool = False
    freeze_disabled: bool = False
    
    # Data sources used
    data_sources: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

class ComprehensiveEnricher:
    """
    Comprehensive data enricher using all available free APIs
    """
    
    def __init__(self):
        self.session = None
        self.rate_limits = {
            'coingecko': {'calls': 0, 'reset_time': 0, 'limit': 50},
            'dexscreener': {'calls': 0, 'reset_time': 0, 'limit': 300},
            'birdeye': {'calls': 0, 'reset_time': 0, 'limit': 100},
            'jupiter': {'calls': 0, 'reset_time': 0, 'limit': 600},
            'solscan': {'calls': 0, 'reset_time': 0, 'limit': 1000},
            'moralis': {'calls': 0, 'reset_time': 0, 'limit': 2500},
            'helius': {'calls': 0, 'reset_time': 0, 'limit': 100}
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def enrich_token_comprehensive(self, contract_address: str) -> ComprehensiveTokenData:
        """Get comprehensive data for a token from all sources"""
        logger.info(f"🔍 Comprehensive enrichment for {contract_address[:10]}...")
        
        token_data = ComprehensiveTokenData(contract_address=contract_address, symbol="", name="")
        
        # Fetch from all sources in parallel
        tasks = [
            self._fetch_dexscreener_data(contract_address, token_data),
            self._fetch_birdeye_data(contract_address, token_data),
            self._fetch_jupiter_data(contract_address, token_data),
            self._fetch_solscan_data(contract_address, token_data),
            self._fetch_coingecko_data(contract_address, token_data),
            self._fetch_moralis_data(contract_address, token_data),
            self._fetch_helius_data(contract_address, token_data),
            self._fetch_rugcheck_data(contract_address, token_data),
            self._fetch_honeypot_data(contract_address, token_data)
        ]
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful data sources
        successful_sources = sum(1 for result in results if not isinstance(result, Exception))
        logger.info(f"✅ Enriched from {successful_sources}/9 data sources")
        
        # Calculate derived metrics
        token_data = self._calculate_derived_metrics(token_data)
        
        return token_data
    
    async def _fetch_dexscreener_data(self, address: str, token_data: ComprehensiveTokenData):
        """Fetch comprehensive data from DexScreener"""
        try:
            await self._respect_rate_limit('dexscreener')
            
            url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('pairs'):
                        # Get the highest liquidity pair
                        best_pair = max(data['pairs'], key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))
                        
                        token_data.symbol = best_pair.get('baseToken', {}).get('symbol', '')
                        token_data.name = best_pair.get('baseToken', {}).get('name', '')
                        token_data.price_usd = float(best_pair.get('priceUsd', 0))
                        
                        # Price changes
                        price_change = best_pair.get('priceChange', {})
                        token_data.price_change_5m = float(price_change.get('m5', 0))
                        token_data.price_change_1h = float(price_change.get('h1', 0))
                        token_data.price_change_6h = float(price_change.get('h6', 0))
                        token_data.price_change_24h = float(price_change.get('h24', 0))
                        
                        # Volume data
                        token_data.volume_5m = float(best_pair.get('volume', {}).get('m5', 0))
                        token_data.volume_1h = float(best_pair.get('volume', {}).get('h1', 0))
                        token_data.volume_6h = float(best_pair.get('volume', {}).get('h6', 0))
                        token_data.volume_24h = float(best_pair.get('volume', {}).get('h24', 0))
                        
                        # Liquidity
                        liquidity = best_pair.get('liquidity', {})
                        token_data.liquidity_usd = float(liquidity.get('usd', 0))
                        
                        # Market cap
                        token_data.market_cap = float(best_pair.get('marketCap', 0))
                        token_data.fully_diluted_valuation = float(best_pair.get('fdv', 0))
                        
                        # DEX info
                        token_data.main_dex = best_pair.get('dexId', '')
                        token_data.pair_count = len(data['pairs'])
                        token_data.dex_pairs = data['pairs']
                        
                        token_data.data_sources.append('dexscreener')
                        
        except Exception as e:
            logger.error(f"DexScreener error: {e}")
    
    async def _fetch_birdeye_data(self, address: str, token_data: ComprehensiveTokenData):
        """Fetch data from Birdeye"""
        try:
            await self._respect_rate_limit('birdeye')
            
            # Token overview
            url = f"https://public-api.birdeye.so/defi/token_overview?address={address}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('data'):
                        token_info = data['data']
                        
                        if not token_data.symbol:
                            token_data.symbol = token_info.get('symbol', '')
                        if not token_data.name:
                            token_data.name = token_info.get('name', '')
                        
                        if not token_data.price_usd:
                            token_data.price_usd = float(token_info.get('price', 0))
                        
                        # Supply data
                        token_data.circulating_supply = float(token_info.get('supply', 0))
                        
                        # Social data
                        extensions = token_info.get('extensions', {})
                        token_data.website_url = extensions.get('website', '')
                        
                        token_data.data_sources.append('birdeye')
            
            # Get holder data
            url = f"https://public-api.birdeye.so/defi/token_holder?address={address}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('data'):
                        holders = data['data']
                        token_data.holder_count = len(holders.get('items', []))
                        
                        # Calculate top holder concentrations
                        if holders.get('items'):
                            total_supply = sum(float(h.get('uiAmount', 0)) for h in holders['items'])
                            if total_supply > 0:
                                top_10_amount = sum(float(h.get('uiAmount', 0)) for h in holders['items'][:10])
                                top_20_amount = sum(float(h.get('uiAmount', 0)) for h in holders['items'][:20])
                                
                                token_data.top_10_holders_percent = (top_10_amount / total_supply) * 100
                                token_data.top_20_holders_percent = (top_20_amount / total_supply) * 100
                                
                                # Count whales (>1% holders)
                                token_data.whale_count = sum(1 for h in holders['items'] 
                                                            if float(h.get('uiAmount', 0)) / total_supply > 0.01)
                        
        except Exception as e:
            logger.error(f"Birdeye error: {e}")
    
    async def _fetch_jupiter_data(self, address: str, token_data: ComprehensiveTokenData):
        """Fetch data from Jupiter"""
        try:
            await self._respect_rate_limit('jupiter')
            
            url = f"https://price.jup.ag/v4/price?ids={address}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('data') and address in data['data']:
                        price_data = data['data'][address]
                        
                        if not token_data.price_usd:
                            token_data.price_usd = float(price_data.get('price', 0))
                        
                        token_data.data_sources.append('jupiter')
                        
        except Exception as e:
            logger.error(f"Jupiter error: {e}")
    
    async def _fetch_solscan_data(self, address: str, token_data: ComprehensiveTokenData):
        """Fetch data from Solscan"""
        try:
            await self._respect_rate_limit('solscan')
            
            # Token meta
            url = f"https://public-api.solscan.io/token/meta?tokenAddress={address}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not token_data.symbol:
                        token_data.symbol = data.get('symbol', '')
                    if not token_data.name:
                        token_data.name = data.get('name', '')
                    
                    token_data.total_supply = float(data.get('supply', 0))
                    token_data.creator_address = data.get('creator', '')
                    
                    # Check if mint/freeze disabled
                    token_data.mint_disabled = data.get('mintAuthorityAddress') is None
                    token_data.freeze_disabled = data.get('freezeAuthorityAddress') is None
                    
                    token_data.data_sources.append('solscan')
                    
        except Exception as e:
            logger.error(f"Solscan error: {e}")
    
    async def _fetch_coingecko_data(self, address: str, token_data: ComprehensiveTokenData):
        """Fetch data from CoinGecko"""
        try:
            await self._respect_rate_limit('coingecko')
            
            # Try to find the token by contract address
            url = f"https://api.coingecko.com/api/v3/coins/solana/contract/{address}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    market_data = data.get('market_data', {})
                    
                    if not token_data.price_usd:
                        token_data.price_usd = float(market_data.get('current_price', {}).get('usd', 0))
                    
                    # More volume data
                    token_data.volume_24h = max(token_data.volume_24h, 
                                              float(market_data.get('total_volume', {}).get('usd', 0)))
                    
                    # Market cap
                    token_data.market_cap = max(token_data.market_cap,
                                              float(market_data.get('market_cap', {}).get('usd', 0)))
                    
                    # Social data
                    community_data = data.get('community_data', {})
                    token_data.twitter_followers = community_data.get('twitter_followers', 0)
                    token_data.telegram_members = community_data.get('telegram_channel_user_count', 0)
                    
                    token_data.data_sources.append('coingecko')
                    
        except Exception as e:
            logger.error(f"CoinGecko error: {e}")
    
    async def _fetch_moralis_data(self, address: str, token_data: ComprehensiveTokenData):
        """Fetch data from Moralis (if API key available)"""
        try:
            # This would require API key setup
            # For now, skip or use public endpoints if available
            pass
        except Exception as e:
            logger.error(f"Moralis error: {e}")
    
    async def _fetch_helius_data(self, address: str, token_data: ComprehensiveTokenData):
        """Fetch data from Helius (if API key available)"""
        try:
            # This would require API key setup
            # For now, skip or use public endpoints if available
            pass
        except Exception as e:
            logger.error(f"Helius error: {e}")
    
    async def _fetch_rugcheck_data(self, address: str, token_data: ComprehensiveTokenData):
        """Fetch rug risk data"""
        try:
            # Use rugcheck.xyz or similar services
            url = f"https://api.rugcheck.xyz/v1/tokens/{address}/report"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Calculate rug risk score based on various factors
                    risk_score = 0
                    
                    if data.get('risks'):
                        for risk in data['risks']:
                            severity = risk.get('level', 'info')
                            if severity == 'danger':
                                risk_score += 0.3
                            elif severity == 'warning':
                                risk_score += 0.1
                    
                    token_data.rug_risk_score = min(risk_score, 1.0)
                    token_data.data_sources.append('rugcheck')
                    
        except Exception as e:
            logger.error(f"Rugcheck error: {e}")
    
    async def _fetch_honeypot_data(self, address: str, token_data: ComprehensiveTokenData):
        """Check for honeypot risks"""
        try:
            # Use honeypot detection services
            url = f"https://api.honeypot.is/v2/IsHoneypot?address={address}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    token_data.honeypot_risk = float(data.get('honeypotResult', {}).get('isHoneypot', 0))
                    token_data.data_sources.append('honeypot_is')
                    
        except Exception as e:
            logger.error(f"Honeypot check error: {e}")
    
    def _calculate_derived_metrics(self, token_data: ComprehensiveTokenData) -> ComprehensiveTokenData:
        """Calculate derived metrics from collected data"""
        
        # Calculate buy/sell pressure from volume and price changes
        if token_data.volume_24h > 0 and token_data.price_change_24h != 0:
            if token_data.price_change_24h > 0:
                token_data.buy_pressure = min(token_data.price_change_24h / 100, 1.0)
                token_data.sell_pressure = max(0, 1 - token_data.buy_pressure)
            else:
                token_data.sell_pressure = min(abs(token_data.price_change_24h) / 100, 1.0)
                token_data.buy_pressure = max(0, 1 - token_data.sell_pressure)
        
        # Estimate unique traders (rough approximation)
        if token_data.volume_24h > 0 and token_data.price_usd > 0:
            avg_trade_size = token_data.volume_24h / max(token_data.trade_count_24h, 1)
            if avg_trade_size > 0:
                token_data.unique_traders_24h = int(token_data.volume_24h / (avg_trade_size * 3))  # Rough estimate
        
        # Calculate technical indicators (simplified)
        if token_data.price_usd > 0:
            # Simple RSI approximation based on price changes
            if token_data.price_change_24h > 0:
                token_data.rsi_14 = 50 + min(token_data.price_change_24h, 50)
            else:
                token_data.rsi_14 = 50 - min(abs(token_data.price_change_24h), 50)
        
        return token_data
    
    async def _respect_rate_limit(self, api_name: str):
        """Respect API rate limits"""
        current_time = time.time()
        rate_limit = self.rate_limits[api_name]
        
        # Reset counter every minute
        if current_time - rate_limit['reset_time'] > 60:
            rate_limit['calls'] = 0
            rate_limit['reset_time'] = current_time
        
        # Check if we need to wait
        if rate_limit['calls'] >= rate_limit['limit']:
            wait_time = 60 - (current_time - rate_limit['reset_time'])
            if wait_time > 0:
                logger.info(f"Rate limit hit for {api_name}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                rate_limit['calls'] = 0
                rate_limit['reset_time'] = time.time()
        
        rate_limit['calls'] += 1
    
    async def enrich_batch(self, contracts: List[str], progress_callback=None) -> List[ComprehensiveTokenData]:
        """Enrich multiple tokens in batch"""
        logger.info(f"📊 Starting batch enrichment of {len(contracts)} tokens")
        
        results = []
        for i, contract in enumerate(contracts):
            try:
                token_data = await self.enrich_token_comprehensive(contract)
                results.append(token_data)
                
                if progress_callback:
                    progress_callback(i + 1, len(contracts), token_data.symbol or contract[:10])
                
                # Small delay to be respectful to APIs
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error enriching {contract}: {e}")
                # Add empty data to maintain order
                results.append(ComprehensiveTokenData(contract_address=contract, symbol="ERROR", name="ERROR"))
        
        logger.info(f"✅ Batch enrichment complete: {len(results)} tokens processed")
        return results

# Database storage for enriched data
def store_comprehensive_data(token_data: ComprehensiveTokenData, db_path: str = "data/comprehensive_tokens.db"):
    """Store comprehensive token data in database"""
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create comprehensive table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comprehensive_tokens (
            contract_address TEXT PRIMARY KEY,
            symbol TEXT,
            name TEXT,
            price_usd REAL,
            price_sol REAL,
            price_change_5m REAL,
            price_change_1h REAL,
            price_change_6h REAL,
            price_change_24h REAL,
            volume_5m REAL,
            volume_1h REAL,
            volume_6h REAL,
            volume_24h REAL,
            volume_7d REAL,
            market_cap REAL,
            fully_diluted_valuation REAL,
            circulating_supply REAL,
            total_supply REAL,
            max_supply REAL,
            liquidity_usd REAL,
            liquidity_sol REAL,
            liquidity_locked BOOLEAN,
            liquidity_lock_duration INTEGER,
            holder_count INTEGER,
            top_10_holders_percent REAL,
            top_20_holders_percent REAL,
            whale_count INTEGER,
            main_dex TEXT,
            pair_count INTEGER,
            twitter_followers INTEGER,
            telegram_members INTEGER,
            discord_members INTEGER,
            website_url TEXT,
            rsi_14 REAL,
            sma_20 REAL,
            ema_12 REAL,
            bollinger_upper REAL,
            bollinger_lower REAL,
            creation_time TIMESTAMP,
            creator_address TEXT,
            creator_still_holds BOOLEAN,
            creator_balance_percent REAL,
            buy_pressure REAL,
            sell_pressure REAL,
            trade_count_24h INTEGER,
            unique_traders_24h INTEGER,
            rug_risk_score REAL,
            honeypot_risk REAL,
            mint_disabled BOOLEAN,
            freeze_disabled BOOLEAN,
            data_sources TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insert or update data
        cursor.execute("""
        INSERT OR REPLACE INTO comprehensive_tokens VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
        )
        """, (
            token_data.contract_address, token_data.symbol, token_data.name,
            token_data.price_usd, token_data.price_sol,
            token_data.price_change_5m, token_data.price_change_1h, token_data.price_change_6h, token_data.price_change_24h,
            token_data.volume_5m, token_data.volume_1h, token_data.volume_6h, token_data.volume_24h, token_data.volume_7d,
            token_data.market_cap, token_data.fully_diluted_valuation,
            token_data.circulating_supply, token_data.total_supply, token_data.max_supply,
            token_data.liquidity_usd, token_data.liquidity_sol, token_data.liquidity_locked, token_data.liquidity_lock_duration,
            token_data.holder_count, token_data.top_10_holders_percent, token_data.top_20_holders_percent, token_data.whale_count,
            token_data.main_dex, token_data.pair_count,
            token_data.twitter_followers, token_data.telegram_members, token_data.discord_members, token_data.website_url,
            token_data.rsi_14, token_data.sma_20, token_data.ema_12, token_data.bollinger_upper, token_data.bollinger_lower,
            token_data.creation_time, token_data.creator_address, token_data.creator_still_holds, token_data.creator_balance_percent,
            token_data.buy_pressure, token_data.sell_pressure, token_data.trade_count_24h, token_data.unique_traders_24h,
            token_data.rug_risk_score, token_data.honeypot_risk, token_data.mint_disabled, token_data.freeze_disabled,
            json.dumps(token_data.data_sources)
        ))
        
        conn.commit()

# Test the enricher
async def test_comprehensive_enrichment():
    """Test the comprehensive enricher"""
    test_contracts = [
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "So11111111111111111111111111111111111111112",     # SOL
    ]
    
    async with ComprehensiveEnricher() as enricher:
        for contract in test_contracts:
            data = await enricher.enrich_token_comprehensive(contract)
            print(f"\n{data.symbol} ({contract[:10]}...):")
            print(f"  Price: ${data.price_usd:.6f}")
            print(f"  Market Cap: ${data.market_cap:,.0f}")
            print(f"  Volume 24h: ${data.volume_24h:,.0f}")
            print(f"  Holders: {data.holder_count}")
            print(f"  Data Sources: {len(data.data_sources)}")
            
            # Store in database
            store_comprehensive_data(data)

if __name__ == "__main__":
    asyncio.run(test_comprehensive_enrichment())