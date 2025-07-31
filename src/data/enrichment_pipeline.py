import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger
from dataclasses import dataclass, field
import json
from src.data.database import CoinDatabase
from config.config import settings

@dataclass
class APIProvider:
    name: str
    base_url: str
    headers: Dict[str, str] = field(default_factory=dict)
    rate_limit: float = 10.0  # requests per second
    priority: int = 1  # Higher priority = preferred source
    supported_chains: List[str] = field(default_factory=lambda: ["solana"])
    
class RateLimiter:
    def __init__(self, rate: float):
        self.rate = rate
        self.last_call = 0
        self.lock = asyncio.Lock()
        
    async def acquire(self):
        async with self.lock:
            current = asyncio.get_event_loop().time()
            time_since_last = current - self.last_call
            if time_since_last < 1.0 / self.rate:
                await asyncio.sleep(1.0 / self.rate - time_since_last)
            self.last_call = asyncio.get_event_loop().time()

class DataEnrichmentPipeline:
    def __init__(self, db: CoinDatabase):
        self.db = db
        self.session: Optional[aiohttp.ClientSession] = None
        self.providers = self._initialize_providers()
        self.rate_limiters = {
            provider.name: RateLimiter(provider.rate_limit) 
            for provider in self.providers
        }
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    def _initialize_providers(self) -> List[APIProvider]:
        """Initialize API providers with their configurations"""
        providers = [
            APIProvider(
                name="birdeye",
                base_url="https://public-api.birdeye.so",
                headers={"X-API-KEY": settings.birdeye_api_key} if settings.birdeye_api_key else {},
                rate_limit=5.0,
                priority=1
            ),
            APIProvider(
                name="dexscreener",
                base_url="https://api.dexscreener.com/latest/dex",
                rate_limit=10.0,
                priority=2
            ),
            APIProvider(
                name="jupiter",
                base_url="https://price.jup.ag/v4",
                rate_limit=20.0,
                priority=3
            ),
            APIProvider(
                name="coingecko",
                base_url="https://api.coingecko.com/api/v3",
                rate_limit=10.0,
                priority=4
            ),
            APIProvider(
                name="coinmarketcap",
                base_url="https://pro-api.coinmarketcap.com/v1",
                headers={"X-CMC_PRO_API_KEY": settings.cmc_api_key} if settings.cmc_api_key else {},
                rate_limit=3.0,
                priority=5
            )
        ]
        
        # Sort by priority
        return sorted(providers, key=lambda x: x.priority)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, provider: str, endpoint: str, params: Dict) -> str:
        """Generate cache key"""
        return f"{provider}:{endpoint}:{json.dumps(params, sort_keys=True)}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if 'timestamp' not in cache_entry:
            return False
        age = (datetime.now() - cache_entry['timestamp']).total_seconds()
        return age < self.cache_ttl
    
    async def _make_request(self, provider: APIProvider, endpoint: str, 
                          params: Optional[Dict] = None) -> Optional[Dict]:
        """Make rate-limited request to API provider"""
        cache_key = self._get_cache_key(provider.name, endpoint, params or {})
        
        # Check cache
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]['data']
        
        # Rate limit
        await self.rate_limiters[provider.name].acquire()
        
        try:
            url = f"{provider.base_url}/{endpoint}"
            async with self.session.get(
                url, 
                headers=provider.headers, 
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Cache the response
                    self.cache[cache_key] = {
                        'data': data,
                        'timestamp': datetime.now()
                    }
                    return data
                else:
                    logger.warning(f"{provider.name} returned {response.status} for {endpoint}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling {provider.name} {endpoint}")
        except Exception as e:
            logger.error(f"Error calling {provider.name}: {e}")
        
        return None
    
    async def enrich_birdeye(self, address: str) -> Dict[str, Any]:
        """Fetch data from BirdEye"""
        provider = next(p for p in self.providers if p.name == "birdeye")
        
        # Get token overview
        overview = await self._make_request(
            provider, 
            f"defi/token_overview",
            {"address": address}
        )
        
        # Get price history
        history = await self._make_request(
            provider,
            f"defi/history_price",
            {
                "address": address,
                "type": "1D",
                "time_from": int((datetime.now() - timedelta(days=30)).timestamp()),
                "time_to": int(datetime.now().timestamp())
            }
        )
        
        result = {}
        if overview and 'data' in overview:
            data = overview['data']
            result.update({
                'price': data.get('price'),
                'price_change_24h': data.get('priceChange24h'),
                'volume_24h': data.get('v24hUSD'),
                'market_cap': data.get('mc'),
                'liquidity': data.get('liquidity'),
                'holders': data.get('holder'),
                'decimals': data.get('decimals'),
                'supply': data.get('supply')
            })
        
        if history and 'data' in history:
            result['price_history'] = history['data']['items']
        
        return result
    
    async def enrich_dexscreener(self, address: str) -> Dict[str, Any]:
        """Fetch data from DexScreener"""
        provider = next(p for p in self.providers if p.name == "dexscreener")
        
        data = await self._make_request(
            provider,
            f"tokens/{address}"
        )
        
        result = {}
        if data and 'pairs' in data:
            # Aggregate data from all pairs
            pairs = data['pairs']
            if pairs:
                # Use the pair with highest liquidity
                best_pair = max(pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))
                
                result = {
                    'price': float(best_pair.get('priceUsd', 0)),
                    'price_change_24h': float(best_pair.get('priceChange', {}).get('h24', 0)),
                    'volume_24h': float(best_pair.get('volume', {}).get('h24', 0)),
                    'liquidity': float(best_pair.get('liquidity', {}).get('usd', 0)),
                    'market_cap': float(best_pair.get('marketCap', 0)),
                    'pair_address': best_pair.get('pairAddress'),
                    'dex_id': best_pair.get('dexId'),
                    'price_change_5m': float(best_pair.get('priceChange', {}).get('m5', 0)),
                    'price_change_1h': float(best_pair.get('priceChange', {}).get('h1', 0)),
                    'txns_24h': best_pair.get('txns', {}).get('h24', {})
                }
        
        return result
    
    async def enrich_jupiter(self, address: str) -> Dict[str, Any]:
        """Fetch data from Jupiter Aggregator"""
        provider = next(p for p in self.providers if p.name == "jupiter")
        
        data = await self._make_request(
            provider,
            "price",
            {"ids": address}
        )
        
        result = {}
        if data and 'data' in data and address in data['data']:
            token_data = data['data'][address]
            result = {
                'price': token_data.get('price'),
                'confidence': token_data.get('confidence'),
                'extra_info': token_data.get('extraInfo', {})
            }
        
        return result
    
    async def enrich_technical_indicators(self, address: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators from price data"""
        if df.empty or len(df) < 20:
            return {}
        
        # Ensure we have OHLCV data
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            return {}
        
        try:
            # Simple Moving Averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # Exponential Moving Averages
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Get latest values
            latest = df.iloc[-1]
            
            indicators = {
                'rsi': float(latest['rsi']) if pd.notna(latest['rsi']) else None,
                'macd': float(latest['macd']) if pd.notna(latest['macd']) else None,
                'macd_signal': float(latest['macd_signal']) if pd.notna(latest['macd_signal']) else None,
                'macd_histogram': float(latest['macd_histogram']) if pd.notna(latest['macd_histogram']) else None,
                'sma_20': float(latest['sma_20']) if pd.notna(latest['sma_20']) else None,
                'sma_50': float(latest['sma_50']) if pd.notna(latest['sma_50']) else None,
                'bb_upper': float(latest['bb_upper']) if pd.notna(latest['bb_upper']) else None,
                'bb_middle': float(latest['bb_middle']) if pd.notna(latest['bb_middle']) else None,
                'bb_lower': float(latest['bb_lower']) if pd.notna(latest['bb_lower']) else None,
                'volume_ratio': float(latest['volume_ratio']) if pd.notna(latest['volume_ratio']) else None,
            }
            
            # Add signals
            indicators['rsi_signal'] = 'oversold' if indicators['rsi'] and indicators['rsi'] < 30 else \
                                     'overbought' if indicators['rsi'] and indicators['rsi'] > 70 else 'neutral'
            
            indicators['macd_signal_type'] = 'bullish' if indicators['macd_histogram'] and indicators['macd_histogram'] > 0 else 'bearish'
            
            # Store indicators in database
            for name, value in indicators.items():
                if value is not None and not isinstance(value, str):
                    self.db.add_indicator(
                        coin_id=self.db.get_coin_id(address),
                        timestamp=latest.name,
                        timeframe='1h',
                        indicator_name=name,
                        indicator_value=value
                    )
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators for {address}: {e}")
            return {}
    
    async def enrich_coin(self, address: str, symbol: str) -> Dict[str, Any]:
        """Enrich a single coin with data from multiple sources"""
        logger.info(f"Enriching {symbol} ({address[:10]}...)")
        
        # Fetch from multiple sources concurrently
        tasks = [
            self.enrich_birdeye(address),
            self.enrich_dexscreener(address),
            self.enrich_jupiter(address),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results with priority
        merged_data = {
            'address': address,
            'symbol': symbol,
            'last_updated': datetime.now(),
            'sources': []
        }
        
        # Process results
        provider_names = ['birdeye', 'dexscreener', 'jupiter']
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error from {provider_names[i]}: {result}")
                continue
            
            if result:
                merged_data['sources'].append(provider_names[i])
                # Merge non-None values
                for key, value in result.items():
                    if value is not None and key not in merged_data:
                        merged_data[key] = value
        
        # Get historical data for technical analysis
        df = self.db.get_price_data(symbol, '1h', 
                                   start_date=datetime.now() - timedelta(days=30))
        
        if not df.empty:
            indicators = await self.enrich_technical_indicators(address, df)
            merged_data['technical_indicators'] = indicators
        
        # Calculate enrichment score
        required_fields = ['price', 'volume_24h', 'market_cap', 'liquidity']
        present_fields = sum(1 for field in required_fields if merged_data.get(field) is not None)
        merged_data['enrichment_score'] = present_fields / len(required_fields)
        
        return merged_data
    
    async def enrich_batch(self, coins: List[Tuple[str, str]], batch_size: int = 10) -> List[Dict[str, Any]]:
        """Enrich multiple coins in batches"""
        results = []
        
        for i in range(0, len(coins), batch_size):
            batch = coins[i:i + batch_size]
            batch_tasks = [
                self.enrich_coin(address, symbol) 
                for address, symbol in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to enrich {batch[j][1]}: {result}")
                    results.append({
                        'address': batch[j][0],
                        'symbol': batch[j][1],
                        'error': str(result)
                    })
                else:
                    results.append(result)
            
            # Progress update
            logger.info(f"Enriched {min(i + batch_size, len(coins))}/{len(coins)} coins")
            
            # Small delay between batches
            if i + batch_size < len(coins):
                await asyncio.sleep(1)
        
        return results
    
    def generate_enrichment_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary report of enrichment results"""
        total = len(results)
        successful = sum(1 for r in results if 'error' not in r)
        failed = total - successful
        
        # Source statistics
        source_stats = {}
        for result in results:
            if 'sources' in result:
                for source in result['sources']:
                    source_stats[source] = source_stats.get(source, 0) + 1
        
        # Enrichment scores
        scores = [r.get('enrichment_score', 0) for r in results if 'enrichment_score' in r]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Technical indicator coverage
        with_indicators = sum(1 for r in results if r.get('technical_indicators'))
        
        report = {
            'summary': {
                'total_coins': total,
                'successful': successful,
                'failed': failed,
                'success_rate': successful / total if total > 0 else 0,
                'average_enrichment_score': avg_score,
                'with_technical_indicators': with_indicators
            },
            'source_coverage': source_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        return report