import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger
from dataclasses import dataclass
import json
import time
from urllib.parse import urlencode

@dataclass
class APIEndpoint:
    name: str
    url: str
    rate_limit: float  # requests per second
    headers: Dict[str, str]
    params_template: Dict[str, Any]
    data_extractor: str  # JSON path to extract data
    requires_auth: bool = False

class RateLimiter:
    def __init__(self, rate: float):
        self.rate = rate
        self.last_call = 0
        self.lock = asyncio.Lock()
        
    async def acquire(self):
        async with self.lock:
            current = time.time()
            time_since_last = current - self.last_call
            if time_since_last < 1.0 / self.rate:
                await asyncio.sleep(1.0 / self.rate - time_since_last)
            self.last_call = time.time()

class FreeAPIProviders:
    """
    Comprehensive integration with free crypto APIs
    Handles rate limiting, error recovery, and data normalization
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiters = {}
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.endpoints = self._initialize_endpoints()
        
    def _initialize_endpoints(self) -> Dict[str, APIEndpoint]:
        """Initialize all free API endpoints"""
        return {
            # CoinGecko - 100 requests/minute
            "coingecko_price": APIEndpoint(
                name="CoinGecko Price",
                url="https://api.coingecko.com/api/v3/simple/price",
                rate_limit=1.5,  # Conservative: 90 requests/minute
                headers={"accept": "application/json"},
                params_template={"ids": "{coin_id}", "vs_currencies": "usd", "include_24hr_change": "true"},
                data_extractor="data"
            ),
            
            "coingecko_coins": APIEndpoint(
                name="CoinGecko Coins List",
                url="https://api.coingecko.com/api/v3/coins/list",
                rate_limit=0.5,  # Less frequent calls
                headers={"accept": "application/json"},
                params_template={"include_platform": "true"},
                data_extractor="data"
            ),
            
            "coingecko_market": APIEndpoint(
                name="CoinGecko Market Data",
                url="https://api.coingecko.com/api/v3/coins/markets",
                rate_limit=1.0,
                headers={"accept": "application/json"},
                params_template={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": "250",
                    "page": "1",
                    "sparkline": "false"
                },
                data_extractor="data"
            ),
            
            # DexScreener - No official rate limits, but be respectful
            "dexscreener_token": APIEndpoint(
                name="DexScreener Token",
                url="https://api.dexscreener.com/latest/dex/tokens/{address}",
                rate_limit=5.0,  # 5 requests/second max
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="pairs"
            ),
            
            "dexscreener_pairs": APIEndpoint(
                name="DexScreener Pairs",
                url="https://api.dexscreener.com/latest/dex/search",
                rate_limit=2.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"q": "{query}"},
                data_extractor="pairs"
            ),
            
            # Jupiter - Solana price aggregator
            "jupiter_price": APIEndpoint(
                name="Jupiter Price",
                url="https://price.jup.ag/v4/price",
                rate_limit=10.0,  # Generally very permissive
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"ids": "{token_address}"},
                data_extractor="data"
            ),
            
            # Solscan - Solana blockchain explorer
            "solscan_token": APIEndpoint(
                name="Solscan Token",  
                url="https://public-api.solscan.io/token/meta",
                rate_limit=5.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"tokenAddress": "{address}"},
                data_extractor="data"
            ),
            
            "solscan_holders": APIEndpoint(
                name="Solscan Holders",
                url="https://public-api.solscan.io/token/holders",
                rate_limit=3.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"tokenAddress": "{address}", "limit": "50"},
                data_extractor="data"
            ),
            
            # CoinMarketCap free tier - 333 calls per day
            "cmc_quotes": APIEndpoint(
                name="CoinMarketCap Quotes",
                url="https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
                rate_limit=0.001,  # Very conservative - ~100 calls per day
                headers={"X-CMC_PRO_API_KEY": "DEMO_KEY"},  # Will be replaced with real key
                params_template={"symbol": "{symbol}"},
                data_extractor="data",
                requires_auth=True
            ),
            
            # CryptoCompare - 100,000 requests/month free
            "cryptocompare_price": APIEndpoint(
                name="CryptoCompare Price",
                url="https://min-api.cryptocompare.com/data/price",
                rate_limit=5.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"fsym": "{symbol}", "tsyms": "USD"},
                data_extractor="data"
            ),
            
            "cryptocompare_multi": APIEndpoint(
                name="CryptoCompare Multi",
                url="https://min-api.cryptocompare.com/data/pricemultifull",
                rate_limit=2.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"fsyms": "{symbols}", "tsyms": "USD"},
                data_extractor="RAW"
            ),
            
            # Messari - 20 requests per minute
            "messari_asset": APIEndpoint(
                name="Messari Asset",
                url="https://data.messari.io/api/v1/assets/{asset}/metrics",
                rate_limit=0.3,  # Conservative: 18 requests/minute
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="data"
            ),
            
            # NEW COMPREHENSIVE API SOURCES
            
            # Birdeye - Solana DEX aggregator (Free tier: 100 requests/day)
            "birdeye_token": APIEndpoint(
                name="Birdeye Token Data",
                url="https://public-api.birdeye.so/public/token_overview",
                rate_limit=0.5,  # Conservative for free tier
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"address": "{address}"},
                data_extractor="data"
            ),
            
            "birdeye_price_history": APIEndpoint(
                name="Birdeye Price History", 
                url="https://public-api.birdeye.so/public/price_history",
                rate_limit=0.5,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"address": "{address}", "time_from": "{time_from}", "time_to": "{time_to}"},
                data_extractor="data"
            ),
            
            # Raydium API - Solana DEX
            "raydium_pairs": APIEndpoint(
                name="Raydium Pairs",
                url="https://api.raydium.io/v2/main/pairs",
                rate_limit=2.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="data"
            ),
            
            # Orca API - Solana DEX
            "orca_pools": APIEndpoint(
                name="Orca Pools",
                url="https://api.orca.so/v1/pools",
                rate_limit=5.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="data"
            ),
            
            # Pump.fun API - Solana meme coin tracker
            "pumpfun_token": APIEndpoint(
                name="Pump.fun Token",
                url="https://frontend-api.pump.fun/coins/{address}",
                rate_limit=2.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="data"
            ),
            
            # GMGN API - On-chain analytics
            "gmgn_token": APIEndpoint(
                name="GMGN Token Analytics",
                url="https://gmgn.ai/api/v1/token_security/solana/{address}",
                rate_limit=1.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="data"
            ),
            
            # Dune Analytics - On-chain data
            "dune_query": APIEndpoint(
                name="Dune Analytics",
                url="https://api.dune.com/api/v1/query/{query_id}/results",
                rate_limit=0.1,  # Very conservative for free tier
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="result.rows",
                requires_auth=True
            ),
            
            # CoinPaprika - Free crypto API
            "coinpaprika_ticker": APIEndpoint(
                name="CoinPaprika Ticker",
                url="https://api.coinpaprika.com/v1/tickers/{coin_id}",
                rate_limit=10.0,  # 10 req/sec for free
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="data"
            ),
            
            "coinpaprika_historical": APIEndpoint(
                name="CoinPaprika Historical",
                url="https://api.coinpaprika.com/v1/tickers/{coin_id}/historical",
                rate_limit=5.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"start": "{start_date}", "interval": "1d"},
                data_extractor="data"
            ),
            
            # Coinglass - Derivatives data
            "coinglass_funding": APIEndpoint(
                name="Coinglass Funding Rates",
                url="https://open-api.coinglass.com/public/v2/funding",
                rate_limit=1.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"symbol": "{symbol}"},
                data_extractor="data"
            ),
            
            # Defillama - TVL and DeFi data
            "defillama_protocol": APIEndpoint(
                name="DefiLlama Protocol",
                url="https://api.llama.fi/protocol/{protocol}",
                rate_limit=2.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="data"
            ),
            
            # CryptoPanic - News and sentiment
            "cryptopanic_news": APIEndpoint(
                name="CryptoPanic News",
                url="https://cryptopanic.com/api/v1/posts/",
                rate_limit=1.0,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={"auth_token": "free", "currencies": "{symbol}"},
                data_extractor="results"
            ),
            
            # Token Metrics - On-chain metrics
            "tokenmetrics_overview": APIEndpoint(
                name="Token Metrics Overview",
                url="https://api.tokenmetrics.com/v2/tokens/{address}/overview",
                rate_limit=0.5,
                headers={"User-Agent": "TrenchCoat-Analytics/1.0"},
                params_template={},
                data_extractor="data",
                requires_auth=True
            ),
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )
        
        # Initialize rate limiters
        for endpoint_name, endpoint in self.endpoints.items():
            self.rate_limiters[endpoint_name] = RateLimiter(endpoint.rate_limit)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key"""
        return f"{endpoint}:{json.dumps(params, sort_keys=True)}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is valid"""
        if 'timestamp' not in cache_entry:
            return False
        age = (datetime.now() - cache_entry['timestamp']).total_seconds()
        return age < self.cache_ttl
    
    async def _make_request(self, endpoint_name: str, **kwargs) -> Optional[Dict]:
        """Make rate-limited request to API endpoint"""
        endpoint = self.endpoints[endpoint_name]
        
        # Format URL and params
        url = endpoint.url.format(**kwargs)
        params = {}
        for key, value in endpoint.params_template.items():
            if isinstance(value, str) and "{" in value:
                params[key] = value.format(**kwargs)
            else:
                params[key] = value
        
        # Check cache
        cache_key = self._get_cache_key(endpoint_name, params)
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]['data']
        
        # Rate limit
        await self.rate_limiters[endpoint_name].acquire()
        
        try:
            async with self.session.get(url, headers=endpoint.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Cache the response
                    self.cache[cache_key] = {
                        'data': data,
                        'timestamp': datetime.now()
                    }
                    
                    return data
                elif response.status == 429:
                    logger.warning(f"Rate limited on {endpoint_name}, waiting...")
                    await asyncio.sleep(60)  # Wait 1 minute
                    return None
                else:
                    logger.error(f"{endpoint_name} returned {response.status}: {await response.text()}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling {endpoint_name}: {e}")
            return None
    
    async def get_coingecko_price(self, coin_ids: List[str]) -> Dict[str, Any]:
        """Get prices from CoinGecko"""
        # Batch up to 100 coins per request
        results = {}
        
        for i in range(0, len(coin_ids), 100):
            batch = coin_ids[i:i+100]
            coin_id_str = ",".join(batch)
            
            data = await self._make_request("coingecko_price", coin_id=coin_id_str)
            
            if data:
                results.update(data)
            
            # Small delay between batches
            if i + 100 < len(coin_ids):
                await asyncio.sleep(2)
        
        return results
    
    async def get_coingecko_market_data(self, page: int = 1) -> List[Dict]:
        """Get market data from CoinGecko"""
        data = await self._make_request("coingecko_market", page=page)
        return data if data else []
    
    async def get_dexscreener_data(self, address: str) -> Dict[str, Any]:
        """Get token data from DexScreener"""
        data = await self._make_request("dexscreener_token", address=address)
        
        if data and 'pairs' in data:
            # Find best Solana pair
            solana_pairs = [p for p in data['pairs'] if p.get('chainId') == 'solana']
            
            if solana_pairs:
                # Sort by liquidity and take the best
                best_pair = max(solana_pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))
                
                return {
                    'price': float(best_pair.get('priceUsd', 0)),
                    'price_change_24h': float(best_pair.get('priceChange', {}).get('h24', 0)),
                    'volume_24h': float(best_pair.get('volume', {}).get('h24', 0)),
                    'liquidity': float(best_pair.get('liquidity', {}).get('usd', 0)),
                    'market_cap': float(best_pair.get('marketCap', 0)),
                    'fdv': float(best_pair.get('fdv', 0)),
                    'pair_address': best_pair.get('pairAddress'),
                    'dex_id': best_pair.get('dexId'),
                    'price_change_5m': float(best_pair.get('priceChange', {}).get('m5', 0)),
                    'price_change_1h': float(best_pair.get('priceChange', {}).get('h1', 0)),
                    'price_change_6h': float(best_pair.get('priceChange', {}).get('h6', 0)),
                    'txns_24h': best_pair.get('txns', {}).get('h24', {}),
                    'buys_24h': best_pair.get('txns', {}).get('h24', {}).get('buys', 0),
                    'sells_24h': best_pair.get('txns', {}).get('h24', {}).get('sells', 0)
                }
        
        return {}
    
    async def get_jupiter_price(self, token_addresses: List[str]) -> Dict[str, Any]:
        """Get prices from Jupiter"""
        # Batch multiple addresses
        ids = ",".join(token_addresses)
        data = await self._make_request("jupiter_price", token_address=ids)
        
        results = {}
        if data and 'data' in data:
            for address, price_data in data['data'].items():
                if price_data:
                    results[address] = {
                        'price': price_data.get('price'),
                        'extraInfo': price_data.get('extraInfo', {})
                    }
        
        return results
    
    async def get_solscan_token_info(self, address: str) -> Dict[str, Any]:
        """Get token info from Solscan"""
        data = await self._make_request("solscan_token", address=address)
        
        if data:
            return {
                'name': data.get('name'),
                'symbol': data.get('symbol'),
                'decimals': data.get('decimals'),
                'supply': data.get('supply'),
                'icon': data.get('icon'),
                'website': data.get('website'),
                'twitter': data.get('twitter')
            }
        
        return {}
    
    async def get_solscan_holders(self, address: str) -> Dict[str, Any]:
        """Get holder data from Solscan"""
        data = await self._make_request("solscan_holders", address=address)
        
        if data:
            holders = data.get('data', [])
            
            # Calculate holder distribution
            total_holders = len(holders)
            top_10_percentage = 0
            
            if holders:
                total_supply = sum(float(h.get('amount', 0)) for h in holders)
                top_10_supply = sum(float(h.get('amount', 0)) for h in holders[:10])
                top_10_percentage = (top_10_supply / total_supply * 100) if total_supply > 0 else 0
            
            return {
                'total_holders': total_holders,
                'top_10_percentage': top_10_percentage,
                'holders_data': holders[:20]  # Top 20 holders
            }
        
        return {}
    
    async def get_cryptocompare_price(self, symbols: List[str]) -> Dict[str, Any]:
        """Get prices from CryptoCompare"""
        # Batch symbols
        symbol_str = ",".join(symbols)
        data = await self._make_request("cryptocompare_multi", symbols=symbol_str)
        
        results = {}
        if data:
            for symbol, price_data in data.items():
                if 'USD' in price_data:
                    usd_data = price_data['USD']
                    results[symbol] = {
                        'price': usd_data.get('PRICE'),
                        'change_24h': usd_data.get('CHANGEPCT24HOUR'),
                        'volume_24h': usd_data.get('VOLUME24HOURTO'),
                        'market_cap': usd_data.get('MKTCAP'),
                        'high_24h': usd_data.get('HIGH24HOUR'),
                        'low_24h': usd_data.get('LOW24HOUR')
                    }
        
        return results
    
    async def get_messari_data(self, asset_slug: str) -> Dict[str, Any]:
        """Get asset data from Messari"""
        data = await self._make_request("messari_asset", asset=asset_slug)
        
        if data and 'data' in data:
            metrics = data['data']
            
            return {
                'market_data': metrics.get('market_data', {}),
                'marketcap': metrics.get('marketcap', {}),
                'supply': metrics.get('supply', {}),
                'all_time_high': metrics.get('all_time_high', {}),
                'cycle_low': metrics.get('cycle_low', {}),
                'developer_activity': metrics.get('developer_activity', {}),
                'roi_data': metrics.get('roi_data', {})
            }
        
        return {}
    
    async def search_coingecko_coin_id(self, contract_address: str) -> Optional[str]:
        """Find CoinGecko coin ID by contract address"""
        # First try to get the coins list (cached)
        coins_data = await self._make_request("coingecko_coins")
        
        if coins_data:
            for coin in coins_data:
                platforms = coin.get('platforms', {})
                # Check Solana platform
                if 'solana' in platforms and platforms['solana'] == contract_address:
                    return coin['id']
                
                # Check other platforms
                for platform, addr in platforms.items():
                    if addr == contract_address:
                        return coin['id']
        
        return None
    
    async def get_comprehensive_data(self, contract_address: str, symbol: str = None) -> Dict[str, Any]:
        """Get comprehensive data from all available sources"""
        logger.info(f"Enriching {symbol or contract_address[:10]}... from all free APIs")
        
        # Prepare tasks for concurrent execution
        tasks = []
        
        # DexScreener (always available for Solana)
        tasks.append(("dexscreener", self.get_dexscreener_data(contract_address)))
        
        # Jupiter (Solana specific)
        tasks.append(("jupiter", self.get_jupiter_price([contract_address])))
        
        # Solscan (Solana specific)
        tasks.append(("solscan_token", self.get_solscan_token_info(contract_address)))
        tasks.append(("solscan_holders", self.get_solscan_holders(contract_address)))
        
        # CoinGecko (need to find coin ID first)
        if symbol:
            coin_id = await self.search_coingecko_coin_id(contract_address)
            if coin_id:
                tasks.append(("coingecko", self.get_coingecko_price([coin_id])))
        
        # CryptoCompare (if we have symbol)
        if symbol and symbol.startswith('$'):
            clean_symbol = symbol[1:].upper()
            tasks.append(("cryptocompare", self.get_cryptocompare_price([clean_symbol])))
        
        # Execute all tasks concurrently
        results = {}
        for source_name, task in tasks:
            try:
                result = await task
                if result:
                    results[source_name] = result
            except Exception as e:
                logger.error(f"Error fetching from {source_name}: {e}")
        
        # Merge and normalize data
        merged_data = self._merge_api_results(results, contract_address, symbol)
        
        logger.info(f"Enriched {symbol or contract_address[:10]}... with {len(results)} sources")
        
        return merged_data
    
    def _merge_api_results(self, results: Dict[str, Any], address: str, symbol: str) -> Dict[str, Any]:
        """Merge results from different APIs into normalized format"""
        merged = {
            'contract_address': address,
            'symbol': symbol,
            'enrichment_timestamp': datetime.now().isoformat(),
            'data_sources': list(results.keys()),
            'enrichment_score': 0
        }
        
        # Priority order for different metrics
        price_sources = ['dexscreener', 'jupiter', 'coingecko', 'cryptocompare']
        volume_sources = ['dexscreener', 'coingecko', 'cryptocompare']
        market_cap_sources = ['dexscreener', 'coingecko', 'cryptocompare']
        
        # Extract price (with source priority)
        for source in price_sources:
            if source in results:
                data = results[source]
                price = None
                
                if source == 'dexscreener':
                    price = data.get('price')
                elif source == 'jupiter':
                    price = data.get(address, {}).get('price')
                elif source == 'coingecko':
                    for coin_data in data.values():
                        price = coin_data.get('usd')
                        break
                elif source == 'cryptocompare':
                    for symbol_data in data.values():
                        price = symbol_data.get('price')
                        break
                
                if price and price > 0:
                    merged['price'] = float(price)
                    merged['price_source'] = source
                    break
        
        # Extract other metrics
        if 'dexscreener' in results:
            dex_data = results['dexscreener']
            merged.update({
                'price_change_24h': dex_data.get('price_change_24h'),
                'price_change_1h': dex_data.get('price_change_1h'),
                'price_change_5m': dex_data.get('price_change_5m'),
                'volume_24h': dex_data.get('volume_24h'),
                'liquidity': dex_data.get('liquidity'),
                'market_cap': dex_data.get('market_cap'),
                'fdv': dex_data.get('fdv'),
                'buys_24h': dex_data.get('buys_24h'),
                'sells_24h': dex_data.get('sells_24h'),
                'pair_address': dex_data.get('pair_address'),
                'dex_id': dex_data.get('dex_id')
            })
        
        if 'solscan_token' in results:
            token_data = results['solscan_token']
            merged.update({
                'name': token_data.get('name'),
                'decimals': token_data.get('decimals'),
                'total_supply': token_data.get('supply'),
                'icon_url': token_data.get('icon'),
                'website': token_data.get('website'),
                'twitter': token_data.get('twitter')
            })
        
        if 'solscan_holders' in results:
            holders_data = results['solscan_holders']
            merged.update({
                'total_holders': holders_data.get('total_holders'),
                'top_10_concentration': holders_data.get('top_10_percentage')
            })
        
        # Calculate enrichment score
        required_fields = ['price', 'volume_24h', 'market_cap', 'liquidity', 'total_holders']
        present_fields = sum(1 for field in required_fields if merged.get(field) is not None)
        merged['enrichment_score'] = present_fields / len(required_fields)
        
        # Data quality flags
        merged['data_quality'] = {
            'has_price': 'price' in merged,
            'has_volume': 'volume_24h' in merged,
            'has_liquidity': 'liquidity' in merged,
            'has_holders': 'total_holders' in merged,
            'price_consistency': self._check_price_consistency(results),
            'last_updated': datetime.now().isoformat()
        }
        
        return merged
    
    def _check_price_consistency(self, results: Dict[str, Any]) -> bool:
        """Check if prices from different sources are consistent"""
        prices = []
        
        # Extract prices from different sources
        if 'dexscreener' in results:
            price = results['dexscreener'].get('price')
            if price and price > 0:
                prices.append(price)
        
        if 'jupiter' in results:
            for addr_data in results['jupiter'].values():
                price = addr_data.get('price')
                if price and price > 0:
                    prices.append(price)
                    break
        
        if len(prices) < 2:
            return True  # Can't check consistency with less than 2 prices
        
        # Check if prices are within 5% of each other
        min_price = min(prices)
        max_price = max(prices)
        
        return (max_price - min_price) / min_price <= 0.05  # 5% tolerance
    
    async def get_birdeye_token_data(self, address: str) -> Dict[str, Any]:
        """Get comprehensive token data from Birdeye"""
        data = await self._make_request("birdeye_token", address=address)
        
        if data and data.get('success'):
            token_data = data.get('data', {})
            return {
                'price': token_data.get('price'),
                'price_change_24h': token_data.get('priceChange24h'),
                'volume_24h': token_data.get('volume24h'),
                'liquidity': token_data.get('liquidity'),
                'market_cap': token_data.get('mc'),
                'holders': token_data.get('holder'),
                'unique_wallet_24h': token_data.get('uniqueWallet24h'),
                'trade_24h': token_data.get('trade24h'),
                'buy_24h': token_data.get('buy24h'),
                'sell_24h': token_data.get('sell24h')
            }
        return {}
    
    async def get_birdeye_price_history(self, address: str, days: int = 30) -> List[Dict]:
        """Get historical price data from Birdeye"""
        import time
        time_to = int(time.time())
        time_from = time_to - (days * 24 * 60 * 60)
        
        data = await self._make_request("birdeye_price_history", 
                                      address=address, 
                                      time_from=time_from, 
                                      time_to=time_to)
        
        if data and data.get('success'):
            return data.get('data', {}).get('items', [])
        return []
    
    async def get_coinpaprika_historical(self, coin_id: str, days: int = 30) -> List[Dict]:
        """Get historical data from CoinPaprika"""
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        data = await self._make_request("coinpaprika_historical", 
                                      coin_id=coin_id, 
                                      start_date=start_date)
        
        return data if data else []
    
    async def get_pumpfun_data(self, address: str) -> Dict[str, Any]:
        """Get token data from Pump.fun"""
        data = await self._make_request("pumpfun_token", address=address)
        
        if data:
            return {
                'name': data.get('name'),
                'symbol': data.get('symbol'),
                'description': data.get('description'),
                'image_uri': data.get('image_uri'),
                'metadata_uri': data.get('metadata_uri'),
                'twitter': data.get('twitter'),
                'telegram': data.get('telegram'),
                'website': data.get('website'),
                'show_name': data.get('show_name'),
                'created_timestamp': data.get('created_timestamp'),
                'raydium_pool': data.get('raydium_pool'),
                'complete': data.get('complete'),
                'virtual_sol_reserves': data.get('virtual_sol_reserves'),
                'virtual_token_reserves': data.get('virtual_token_reserves'),
                'total_supply': data.get('total_supply'),
                'king_of_the_hill_timestamp': data.get('king_of_the_hill_timestamp'),
                'market_cap': data.get('usd_market_cap'),
                'reply_count': data.get('reply_count')
            }
        return {}
    
    async def get_gmgn_analytics(self, address: str) -> Dict[str, Any]:
        """Get on-chain analytics from GMGN"""
        data = await self._make_request("gmgn_token", address=address)
        
        if data and data.get('code') == 0:
            token_security = data.get('data', {})
            return {
                'is_honeypot': token_security.get('is_honeypot'),
                'buy_tax': token_security.get('buy_tax'),
                'sell_tax': token_security.get('sell_tax'),
                'is_mintable': token_security.get('is_mintable'),
                'is_proxy': token_security.get('is_proxy'),
                'slippage_modifiable': token_security.get('slippage_modifiable'),
                'is_blacklisted': token_security.get('is_blacklisted'),
                'is_whitelisted': token_security.get('is_whitelisted'),
                'is_in_dex': token_security.get('is_in_dex'),
                'transfer_pausable': token_security.get('transfer_pausable'),
                'creator_address': token_security.get('creator_address'),
                'creator_balance': token_security.get('creator_balance'),
                'creator_percent': token_security.get('creator_percent'),
                'lp_holder_count': token_security.get('lp_holder_count'),
                'lp_total_supply': token_security.get('lp_total_supply'),
                'holder_count': token_security.get('holder_count'),
                'total_supply': token_security.get('total_supply')
            }
        return {}
    
    async def get_comprehensive_historical_data(self, contract_address: str, symbol: str = None, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive historical data from all sources"""
        logger.info(f"Fetching comprehensive historical data for {symbol or contract_address[:10]}... ({days} days)")
        
        historical_data = {
            'contract_address': contract_address,
            'symbol': symbol,
            'timeframe_days': days,
            'data_sources': [],
            'price_history': [],
            'volume_history': [],
            'holder_history': [],
            'security_analysis': {},
            'social_data': {},
            'last_updated': datetime.now().isoformat()
        }
        
        # Birdeye historical data
        try:
            birdeye_history = await self.get_birdeye_price_history(contract_address, days)
            if birdeye_history:
                historical_data['data_sources'].append('birdeye_history')
                historical_data['price_history'].extend([
                    {
                        'timestamp': item.get('unixTime'),
                        'price': item.get('value'),
                        'source': 'birdeye'
                    } for item in birdeye_history
                ])
        except Exception as e:
            logger.warning(f"Birdeye historical data failed: {e}")
        
        # CoinPaprika historical data
        if symbol:
            try:
                paprika_history = await self.get_coinpaprika_historical(symbol.lower(), days)
                if paprika_history:
                    historical_data['data_sources'].append('coinpaprika_history')
                    historical_data['price_history'].extend([
                        {
                            'timestamp': item.get('timestamp'),
                            'price': item.get('price'),
                            'volume_24h': item.get('volume_24h'),
                            'market_cap': item.get('market_cap'),
                            'source': 'coinpaprika'
                        } for item in paprika_history
                    ])
            except Exception as e:
                logger.warning(f"CoinPaprika historical data failed: {e}")
        
        # Current comprehensive snapshot
        current_data = await self.get_comprehensive_data(contract_address, symbol)
        if current_data:
            historical_data['current_snapshot'] = current_data
            historical_data['data_sources'].extend(current_data.get('data_sources', []))
        
        # Security analysis from GMGN
        try:
            security_data = await self.get_gmgn_analytics(contract_address)
            if security_data:
                historical_data['security_analysis'] = security_data
                historical_data['data_sources'].append('gmgn_security')
        except Exception as e:
            logger.warning(f"GMGN security analysis failed: {e}")
        
        # Pump.fun social data
        try:
            pumpfun_data = await self.get_pumpfun_data(contract_address)
            if pumpfun_data:
                historical_data['social_data'] = pumpfun_data
                historical_data['data_sources'].append('pumpfun_social')
        except Exception as e:
            logger.warning(f"Pump.fun social data failed: {e}")
        
        # Calculate enrichment score
        total_possible_sources = 15  # Updated count
        actual_sources = len(set(historical_data['data_sources']))
        historical_data['enrichment_score'] = actual_sources / total_possible_sources
        
        logger.info(f"Historical enrichment complete: {actual_sources}/{total_possible_sources} sources ({historical_data['enrichment_score']:.1%})")
        
        return historical_data