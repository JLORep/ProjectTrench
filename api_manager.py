"""
🌐 TrenchCoat Pro - Unified API Management System
Rate limiting, caching, and monitoring for 17+ API sources
"""

import asyncio
import aiohttp
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
import redis
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd

from config import config
from monitoring import logger, monitor, log_errors, monitor_performance

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    name: str
    base_url: str
    rate_limit: float  # requests per second
    priority: str  # high/medium/low
    requires_key: bool = False
    cache_ttl: int = 300  # seconds

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: float, burst: int = 10):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            # Calculate wait time
            wait_time = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
            self.tokens = 0
            return True

class CacheManager:
    """Unified caching system with Redis support"""
    
    def __init__(self):
        self.memory_cache = {}
        self.redis_client = None
        
        # Try to connect to Redis
        try:
            import redis
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True,
                socket_connect_timeout=1
            )
            self.redis_client.ping()
            logger.log_info("Redis cache connected")
        except:
            logger.log_warning("Redis not available, using memory cache only")
    
    def _get_key(self, api: str, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key"""
        param_str = json.dumps(params, sort_keys=True)
        key_data = f"{api}:{endpoint}:{param_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, api: str, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get from cache"""
        key = self._get_key(api, endpoint, params)
        
        # Check memory cache first
        if key in self.memory_cache:
            data, expiry = self.memory_cache[key]
            if time.time() < expiry:
                monitor.record_metric("cache_hit", 1, {"source": "memory", "api": api})
                return data
        
        # Check Redis if available
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    monitor.record_metric("cache_hit", 1, {"source": "redis", "api": api})
                    return json.loads(data)
            except:
                pass
        
        monitor.record_metric("cache_miss", 1, {"api": api})
        return None
    
    async def set(self, api: str, endpoint: str, params: Dict[str, Any], 
                  data: Any, ttl: int = 300):
        """Set cache value"""
        key = self._get_key(api, endpoint, params)
        
        # Memory cache
        self.memory_cache[key] = (data, time.time() + ttl)
        
        # Keep memory cache size limited
        if len(self.memory_cache) > 1000:
            # Remove oldest entries
            sorted_items = sorted(self.memory_cache.items(), 
                                key=lambda x: x[1][1])
            for old_key, _ in sorted_items[:100]:
                del self.memory_cache[old_key]
        
        # Redis cache
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(data))
            except:
                pass

class APIManager:
    """Unified API management for all sources"""
    
    # API configurations
    API_CONFIGS = {
        "dexscreener": APIEndpoint("DexScreener", "https://api.dexscreener.com/latest/dex", 5.0, "high"),
        "jupiter": APIEndpoint("Jupiter", "https://price.jup.ag/v4", 10.0, "high"),
        "coingecko": APIEndpoint("CoinGecko", "https://api.coingecko.com/api/v3", 1.5, "medium"),
        "cryptocompare": APIEndpoint("CryptoCompare", "https://min-api.cryptocompare.com/data", 5.0, "medium"),
        "coinpaprika": APIEndpoint("CoinPaprika", "https://api.coinpaprika.com/v1", 10.0, "medium"),
        "solscan": APIEndpoint("Solscan", "https://public-api.solscan.io", 5.0, "high"),
        "birdeye": APIEndpoint("Birdeye", "https://public-api.birdeye.so/public", 0.5, "high", True),
        "messari": APIEndpoint("Messari", "https://data.messari.io/api/v1", 0.3, "low"),
        "gmgn": APIEndpoint("GMGN", "https://gmgn.ai/api/v1", 1.0, "high"),
        "pumpfun": APIEndpoint("Pump.fun", "https://frontend-api.pump.fun", 2.0, "medium"),
        "raydium": APIEndpoint("Raydium", "https://api.raydium.io/v2", 2.0, "high"),
        "orca": APIEndpoint("Orca", "https://api.orca.so/v1", 5.0, "medium"),
        "cryptopanic": APIEndpoint("CryptoPanic", "https://cryptopanic.com/api/v1", 1.0, "low", True),
    }
    
    def __init__(self):
        self.session = None
        self.rate_limiters = {
            name: RateLimiter(cfg.rate_limit)
            for name, cfg in self.API_CONFIGS.items()
        }
        self.cache = CacheManager()
        self.error_counts = defaultdict(int)
        self.last_errors = {}
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'TrenchCoat Pro/2.2'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @monitor_performance("api_request")
    async def request(self, api_name: str, endpoint: str, 
                     params: Dict[str, Any] = None,
                     use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Make API request with rate limiting and caching"""
        
        if api_name not in self.API_CONFIGS:
            logger.log_error(f"Unknown API: {api_name}")
            return None
        
        api_config = self.API_CONFIGS[api_name]
        
        # Check cache first
        if use_cache:
            cached = await self.cache.get(api_name, endpoint, params or {})
            if cached:
                return cached
        
        # Rate limiting
        await self.rate_limiters[api_name].acquire()
        
        # Build URL
        url = f"{api_config.base_url}/{endpoint}"
        
        # Add API key if required
        headers = {}
        if api_config.requires_key:
            api_key = config.get_api_key(api_name)
            if not api_key:
                logger.log_warning(f"API key missing for {api_name}")
                return None
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Make request
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Cache successful response
                    if use_cache:
                        await self.cache.set(api_name, endpoint, params or {}, 
                                           data, api_config.cache_ttl)
                    
                    # Reset error count on success
                    self.error_counts[api_name] = 0
                    
                    monitor.record_metric("api_success", 1, {"api": api_name})
                    return data
                else:
                    error_msg = f"{api_name} returned {response.status}"
                    self._handle_error(api_name, error_msg)
                    return None
                    
        except Exception as e:
            self._handle_error(api_name, str(e))
            return None
    
    def _handle_error(self, api_name: str, error: str):
        """Handle API errors"""
        self.error_counts[api_name] += 1
        self.last_errors[api_name] = {
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'count': self.error_counts[api_name]
        }
        
        logger.log_error(f"API error for {api_name}: {error}")
        monitor.record_metric("api_error", 1, {"api": api_name})
        
        # Circuit breaker - disable API after too many errors
        if self.error_counts[api_name] >= 10:
            logger.log_warning(f"Circuit breaker activated for {api_name}")
    
    async def get_aggregated_price(self, contract_address: str, 
                                 symbol: str = None) -> Dict[str, Any]:
        """Get price from multiple sources and aggregate"""
        prices = []
        sources = []
        
        # Try multiple price sources in priority order
        price_apis = [
            ("dexscreener", f"tokens/{contract_address}"),
            ("jupiter", f"price?ids={contract_address}"),
            ("coingecko", f"simple/token_price/solana?contract_addresses={contract_address}"),
        ]
        
        tasks = []
        for api, endpoint in price_apis:
            if self.error_counts[api] < 10:  # Circuit breaker check
                tasks.append(self.request(api, endpoint))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, dict) and result:
                # Extract price based on API format
                api_name = price_apis[i][0]
                price = self._extract_price(result, api_name)
                if price:
                    prices.append(price)
                    sources.append(api_name)
        
        if prices:
            # Calculate aggregated metrics
            return {
                'price': sum(prices) / len(prices),  # Average price
                'min_price': min(prices),
                'max_price': max(prices),
                'sources': sources,
                'variance': max(prices) - min(prices),
                'confidence': len(sources) / len(price_apis)
            }
        
        return None
    
    def _extract_price(self, data: Dict[str, Any], api: str) -> Optional[float]:
        """Extract price from API response"""
        try:
            if api == "dexscreener":
                return float(data.get('pairs', [{}])[0].get('priceUsd', 0))
            elif api == "jupiter":
                return float(data.get('data', {}).get(list(data.get('data', {}).keys())[0], {}).get('price', 0))
            elif api == "coingecko":
                return float(list(data.values())[0].get('usd', 0))
        except:
            return None
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get current API status"""
        return {
            'apis': {
                name: {
                    'status': 'healthy' if self.error_counts[name] < 10 else 'circuit_breaker',
                    'error_count': self.error_counts[name],
                    'last_error': self.last_errors.get(name),
                    'rate_limit': cfg.rate_limit,
                    'priority': cfg.priority
                }
                for name, cfg in self.API_CONFIGS.items()
            },
            'total_errors': sum(self.error_counts.values()),
            'healthy_apis': sum(1 for c in self.error_counts.values() if c < 10),
            'total_apis': len(self.API_CONFIGS)
        }

# Global instance
api_manager = None

async def get_api_manager() -> APIManager:
    """Get or create global API manager"""
    global api_manager
    if api_manager is None:
        api_manager = APIManager()
    return api_manager

# Example usage
async def example_usage():
    """Example of using the API manager"""
    async with await get_api_manager() as api:
        # Get aggregated price
        price_data = await api.get_aggregated_price(
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "USDC"
        )
        
        if price_data:
            print(f"Price: ${price_data['price']:.6f}")
            print(f"Sources: {', '.join(price_data['sources'])}")
            print(f"Confidence: {price_data['confidence']:.1%}")
        
        # Get API status
        status = api.get_api_status()
        print(f"Healthy APIs: {status['healthy_apis']}/{status['total_apis']}")