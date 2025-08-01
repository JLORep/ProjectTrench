#!/usr/bin/env python3
"""
TrenchCoat Pro - Coin Image System
Comprehensive logo/image fetching and caching for beautiful coin displays
"""
import asyncio
import aiohttp
import json
import os
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from dataclasses import dataclass
from unicode_handler import safe_print

@dataclass
class CoinImage:
    ticker: str
    contract_address: str
    image_url: str
    image_source: str
    cached_path: Optional[str] = None
    fetched_at: Optional[datetime] = None
    verified: bool = False

class CoinImageSystem:
    """Comprehensive coin image fetching and management system"""
    
    def __init__(self):
        self.cache_dir = Path("data/coin_images")
        self.cache_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.cache_dir / "image_metadata.json"
        self.metadata = self.load_metadata()
        
        # Image sources in priority order
        self.image_sources = [
            {
                'name': 'solscan',
                'url_template': 'https://public-api.solscan.io/token/meta?tokenAddress={address}',
                'data_path': 'icon',
                'rate_limit': 2.0  # requests per second
            },
            {
                'name': 'coingecko',
                'url_template': 'https://api.coingecko.com/api/v3/coins/{coin_id}',
                'data_path': 'image.large',
                'rate_limit': 1.0
            },
            {
                'name': 'dexscreener',
                'url_template': 'https://api.dexscreener.com/latest/dex/tokens/{address}',
                'data_path': 'pairs.0.info.imageUrl',
                'rate_limit': 3.0
            },
            {
                'name': 'cryptocompare',
                'url_template': 'https://min-api.cryptocompare.com/data/all/coinlist',
                'data_path': 'Data.{symbol}.ImageUrl',
                'rate_limit': 1.0
            },
            {
                'name': 'coinmarketcap',
                'url_template': 'https://s2.coinmarketcap.com/static/img/coins/64x64/{id}.png',
                'data_path': 'direct',
                'rate_limit': 5.0
            }
        ]
        
        # Fallback generic crypto icons
        self.fallback_icons = [
            "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
            "https://cryptologos.cc/logos/ethereum-eth-logo.png", 
            "https://cryptologos.cc/logos/solana-sol-logo.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/64px-Bitcoin.svg.png"
        ]
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load cached image metadata"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            safe_print(f"Warning: Could not load image metadata: {e}")
            return {}
    
    def save_metadata(self):
        """Save image metadata to cache"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            safe_print(f"Warning: Could not save image metadata: {e}")
    
    def get_cache_key(self, ticker: str, contract_address: str) -> str:
        """Generate cache key for coin"""
        data = f"{ticker}_{contract_address}".lower()
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def is_cached_valid(self, cache_key: str, max_age_days: int = 7) -> bool:
        """Check if cached image is still valid"""
        if cache_key not in self.metadata:
            return False
            
        entry = self.metadata[cache_key]
        
        # Check if image file exists
        if 'cached_path' in entry:
            cached_file = Path(entry['cached_path'])
            if not cached_file.exists():
                return False
        
        # Check age
        if 'fetched_at' in entry:
            try:
                fetched_date = datetime.fromisoformat(entry['fetched_at'])
                age = datetime.now() - fetched_date
                return age.days < max_age_days
            except:
                return False
        
        return False
    
    async def fetch_image_url_from_api(self, source: Dict[str, Any], ticker: str, contract_address: str) -> Optional[str]:
        """Fetch image URL from a specific API source"""
        try:
            url = source['url_template'].format(
                address=contract_address,
                coin_id=ticker.lower(),
                symbol=ticker.upper()
            )
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Navigate to image URL using data_path
                        image_url = self.extract_nested_value(data, source['data_path'])
                        
                        if image_url and self.is_valid_image_url(image_url):
                            return image_url
            
        except Exception as e:
            safe_print(f"Error fetching from {source['name']}: {e}")
        
        return None
    
    def extract_nested_value(self, data: Dict, path: str) -> Optional[str]:
        """Extract nested value from API response using dot notation"""
        try:
            keys = path.split('.')
            current = data
            
            for key in keys:
                if key.isdigit():
                    # Array index
                    current = current[int(key)]
                elif '{' in key and '}' in key:
                    # Template variable - skip for now
                    continue
                else:
                    current = current[key]
            
            return str(current) if current else None
            
        except (KeyError, IndexError, TypeError):
            return None
    
    def is_valid_image_url(self, url: str) -> bool:
        """Validate if URL looks like a valid image"""
        if not url:
            return False
            
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check for image file extensions
            path = parsed.path.lower()
            image_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif']
            
            # Either has image extension or contains image-related keywords
            has_extension = any(path.endswith(ext) for ext in image_extensions)
            has_keywords = any(keyword in url.lower() for keyword in ['logo', 'icon', 'image', 'avatar'])
            
            return has_extension or has_keywords
            
        except:
            return False
    
    async def fetch_coin_image(self, ticker: str, contract_address: str) -> CoinImage:
        """Fetch coin image from multiple sources"""
        cache_key = self.get_cache_key(ticker, contract_address)
        
        # Check cache first
        if self.is_cached_valid(cache_key):
            cached_entry = self.metadata[cache_key]
            return CoinImage(
                ticker=ticker,
                contract_address=contract_address,
                image_url=cached_entry['image_url'],
                image_source=cached_entry['image_source'],
                cached_path=cached_entry.get('cached_path'),
                fetched_at=datetime.fromisoformat(cached_entry['fetched_at']),
                verified=cached_entry.get('verified', False)
            )
        
        # Try each source in priority order
        for source in self.image_sources:
            try:
                image_url = await self.fetch_image_url_from_api(source, ticker, contract_address)
                
                if image_url:
                    coin_image = CoinImage(
                        ticker=ticker,
                        contract_address=contract_address,
                        image_url=image_url,
                        image_source=source['name'],
                        fetched_at=datetime.now(),
                        verified=True
                    )
                    
                    # Cache the result
                    self.metadata[cache_key] = {
                        'ticker': ticker,
                        'contract_address': contract_address,
                        'image_url': image_url,
                        'image_source': source['name'],
                        'fetched_at': datetime.now().isoformat(),
                        'verified': True
                    }
                    
                    self.save_metadata()
                    safe_print(f"✅ Found image for {ticker} from {source['name']}")
                    return coin_image
                
                # Rate limiting between sources
                await asyncio.sleep(1.0 / source['rate_limit'])
                
            except Exception as e:
                safe_print(f"Error with {source['name']} for {ticker}: {e}")
                continue
        
        # No image found - use fallback
        fallback_url = self.get_fallback_image(ticker)
        coin_image = CoinImage(
            ticker=ticker,
            contract_address=contract_address,
            image_url=fallback_url,
            image_source='fallback',
            fetched_at=datetime.now(),
            verified=False
        )
        
        # Cache fallback too
        self.metadata[cache_key] = {
            'ticker': ticker,
            'contract_address': contract_address,
            'image_url': fallback_url,
            'image_source': 'fallback',
            'fetched_at': datetime.now().isoformat(),
            'verified': False
        }
        
        self.save_metadata()
        safe_print(f"⚠️ Using fallback image for {ticker}")
        return coin_image
    
    def get_fallback_image(self, ticker: str) -> str:
        """Get fallback image based on ticker"""
        # Simple hash-based selection for consistency
        hash_val = sum(ord(c) for c in ticker.upper())
        return self.fallback_icons[hash_val % len(self.fallback_icons)]
    
    async def batch_fetch_images(self, coins: List[Dict[str, Any]]) -> Dict[str, CoinImage]:
        """Batch fetch images for multiple coins"""
        safe_print(f"🖼️ Fetching images for {len(coins)} coins...")
        
        # Create tasks for concurrent fetching
        tasks = []
        for coin in coins:
            ticker = coin.get('ticker', 'UNK')
            contract_address = coin.get('ca', coin.get('contract_address', ''))
            
            if ticker and contract_address:
                task = self.fetch_coin_image(ticker, contract_address)
                tasks.append((ticker, task))
        
        # Execute tasks with concurrency limit
        results = {}
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def fetch_with_semaphore(ticker, task):
            async with semaphore:
                return ticker, await task
        
        # Run all tasks
        for ticker, result in await asyncio.gather(*[
            fetch_with_semaphore(ticker, task) for ticker, task in tasks
        ], return_exceptions=True):
            if not isinstance(result, Exception):
                results[ticker] = result
        
        safe_print(f"✅ Fetched images for {len(results)} coins")
        return results
    
    def get_image_url(self, ticker: str, contract_address: str) -> str:
        """Get cached image URL or fallback"""
        cache_key = self.get_cache_key(ticker, contract_address)
        
        if cache_key in self.metadata:
            return self.metadata[cache_key]['image_url']
        
        return self.get_fallback_image(ticker)
    
    def get_coin_images_for_dashboard(self, coins: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get image URLs for dashboard display (sync version)"""
        images = {}
        
        for coin in coins:
            ticker = coin.get('ticker', 'UNK')
            contract_address = coin.get('ca', coin.get('contract_address', ''))
            
            if ticker:
                images[ticker] = self.get_image_url(ticker, contract_address)
        
        return images

# Global image system instance
coin_image_system = CoinImageSystem()

async def enrich_coins_with_images(coins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enrich coin data with image URLs"""
    images = await coin_image_system.batch_fetch_images(coins)
    
    # Add image URLs to coin data
    for coin in coins:
        ticker = coin.get('ticker', 'UNK')
        if ticker in images:
            coin_image = images[ticker]
            coin['image_url'] = coin_image.image_url
            coin['image_source'] = coin_image.image_source
            coin['image_verified'] = coin_image.verified
        else:
            coin['image_url'] = coin_image_system.get_fallback_image(ticker)
            coin['image_source'] = 'fallback'
            coin['image_verified'] = False
    
    return coins

def main():
    """CLI tool for testing image fetching"""
    import sys
    
    async def test_fetch():
        if len(sys.argv) > 2:
            ticker = sys.argv[1]
            address = sys.argv[2]
            image = await coin_image_system.fetch_coin_image(ticker, address)
            safe_print(f"Image for {ticker}: {image.image_url}")
        else:
            safe_print("Usage: python coin_image_system.py <TICKER> <CONTRACT_ADDRESS>")
    
    asyncio.run(test_fetch())

if __name__ == "__main__":
    main()