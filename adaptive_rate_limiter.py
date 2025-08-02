#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adaptive Rate Limiting System
Intelligent rate limiting for 100+ API providers with global coordination
Created: 2025-08-02
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import heapq
import json
from enum import Enum
import numpy as np

class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    provider: str
    requests_per_second: float
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    burst_size: int = 10
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    adaptive: bool = False
    priority_weight: float = 1.0

@dataclass
class RateLimitState:
    """Current state of rate limiter"""
    available_tokens: float
    last_refill: float
    request_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    violations: int = 0
    total_requests: int = 0
    total_wait_time: float = 0.0
    
class AdaptiveRateLimiter:
    """Adaptive rate limiter for a single provider"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.state = RateLimitState(
            available_tokens=config.burst_size,
            last_refill=time.time()
        )
        self.lock = asyncio.Lock()
        
        # Adaptive parameters
        self.base_rate = config.requests_per_second
        self.current_rate = config.requests_per_second
        self.rate_history = deque(maxlen=100)
        self.backoff_factor = 1.0
        
    async def acquire(self, priority: float = 1.0) -> float:
        """Acquire permission to make a request"""
        async with self.lock:
            now = time.time()
            
            # Refill tokens based on time passed
            self._refill_tokens(now)
            
            # Calculate wait time
            wait_time = 0.0
            if self.state.available_tokens < 1:
                wait_time = (1 - self.state.available_tokens) / self.current_rate
            
            # Wait if necessary
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                now = time.time()
                self._refill_tokens(now)
            
            # Consume token
            self.state.available_tokens -= 1
            self.state.request_times.append(now)
            self.state.total_requests += 1
            self.state.total_wait_time += wait_time
            
            # Adaptive rate adjustment
            if self.config.adaptive:
                self._adjust_rate()
            
            return wait_time
    
    def _refill_tokens(self, now: float):
        """Refill tokens based on time elapsed"""
        time_passed = now - self.state.last_refill
        tokens_to_add = time_passed * self.current_rate
        
        self.state.available_tokens = min(
            self.config.burst_size,
            self.state.available_tokens + tokens_to_add
        )
        self.state.last_refill = now
    
    def _adjust_rate(self):
        """Adjust rate based on recent performance"""
        if len(self.state.request_times) < 10:
            return
        
        # Calculate actual request rate
        recent_times = list(self.state.request_times)[-20:]
        if len(recent_times) > 1:
            time_span = recent_times[-1] - recent_times[0]
            actual_rate = len(recent_times) / time_span if time_span > 0 else 0
            
            # Store rate history
            self.rate_history.append(actual_rate)
            
            # Adjust based on violations
            if self.state.violations > 0:
                # Backoff on violations
                self.backoff_factor *= 0.9
                self.state.violations = 0
            else:
                # Gradually increase if no violations
                self.backoff_factor = min(1.0, self.backoff_factor * 1.01)
            
            # Update current rate
            self.current_rate = self.base_rate * self.backoff_factor
    
    def report_violation(self):
        """Report a rate limit violation (e.g., 429 response)"""
        self.state.violations += 1
        self.backoff_factor *= 0.7  # Aggressive backoff
        self.current_rate = self.base_rate * self.backoff_factor
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        avg_wait = self.state.total_wait_time / max(1, self.state.total_requests)
        
        return {
            'provider': self.config.provider,
            'current_rate': self.current_rate,
            'base_rate': self.base_rate,
            'backoff_factor': self.backoff_factor,
            'available_tokens': self.state.available_tokens,
            'total_requests': self.state.total_requests,
            'violations': self.state.violations,
            'avg_wait_time': avg_wait,
            'utilization': self.current_rate / self.base_rate
        }


class GlobalRateLimitCoordinator:
    """
    Coordinates rate limiting across all API providers
    Ensures global rate limits and fair resource allocation
    """
    
    def __init__(self):
        self.limiters: Dict[str, AdaptiveRateLimiter] = {}
        self.global_limiters: Dict[str, AdaptiveRateLimiter] = {}
        self.request_queue = asyncio.PriorityQueue()
        self.processing = False
        self.stats = defaultdict(lambda: {'requests': 0, 'wait_time': 0})
        
        # Global limits (across all providers)
        self.global_limits = {
            'total_rps': 100,  # Total requests per second across all APIs
            'total_rpm': 5000,  # Total requests per minute
        }
        
        # Provider configurations
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize rate limiters for all providers"""
        # Provider-specific configurations
        configs = {
            # Tier 1 - High rate limits
            'coingecko': RateLimitConfig('coingecko', 0.5, requests_per_minute=30, priority_weight=1.0),
            'coinmarketcap': RateLimitConfig('coinmarketcap', 0.33, requests_per_minute=20, priority_weight=1.0),
            'dexscreener': RateLimitConfig('dexscreener', 5.0, requests_per_minute=300, priority_weight=0.9),
            'jupiter': RateLimitConfig('jupiter', 10.0, requests_per_minute=600, priority_weight=0.9),
            'coinpaprika': RateLimitConfig('coinpaprika', 10.0, priority_weight=0.8),
            
            # Tier 2 - Medium rate limits
            'moralis': RateLimitConfig('moralis', 0.67, requests_per_minute=40, priority_weight=0.8),
            'etherscan': RateLimitConfig('etherscan', 5.0, requests_per_day=100000, priority_weight=0.8),
            'birdeye': RateLimitConfig('birdeye', 1.67, requests_per_minute=100, priority_weight=0.8),
            'messari': RateLimitConfig('messari', 0.33, requests_per_minute=20, priority_weight=0.7),
            
            # Tier 3 - Lower rate limits
            'whale_alert': RateLimitConfig('whale_alert', 0.17, requests_per_minute=10, priority_weight=0.6),
            'glassnode': RateLimitConfig('glassnode', 0.017, requests_per_minute=1, priority_weight=0.6),
            'santiment': RateLimitConfig('santiment', 0.5, priority_weight=0.6),
            
            # Default for unknown providers
            'default': RateLimitConfig('default', 1.0, priority_weight=0.5, adaptive=True)
        }
        
        # Create limiters
        for provider, config in configs.items():
            self.limiters[provider] = AdaptiveRateLimiter(config)
        
        # Global limiters
        self.global_limiters['total'] = AdaptiveRateLimiter(
            RateLimitConfig('global_total', self.global_limits['total_rps'])
        )
    
    async def acquire(self, provider: str, priority: float = 1.0) -> float:
        """Acquire permission to make a request to a provider"""
        # Get or create limiter for provider
        if provider not in self.limiters:
            self.limiters[provider] = AdaptiveRateLimiter(
                self.limiters['default'].config
            )
        
        limiter = self.limiters[provider]
        
        # Check global limit first
        global_wait = await self.global_limiters['total'].acquire(priority)
        
        # Then check provider limit
        provider_wait = await limiter.acquire(priority)
        
        # Track stats
        total_wait = global_wait + provider_wait
        self.stats[provider]['requests'] += 1
        self.stats[provider]['wait_time'] += total_wait
        
        return total_wait
    
    def report_violation(self, provider: str):
        """Report rate limit violation for a provider"""
        if provider in self.limiters:
            self.limiters[provider].report_violation()
            
            # Also slow down global rate if many violations
            total_violations = sum(
                l.state.violations for l in self.limiters.values()
            )
            if total_violations > 5:
                self.global_limiters['total'].report_violation()
    
    async def get_optimal_provider(self, providers: List[str]) -> str:
        """Get the optimal provider based on current rate limits"""
        best_provider = None
        min_wait = float('inf')
        
        for provider in providers:
            if provider not in self.limiters:
                continue
                
            limiter = self.limiters[provider]
            
            # Estimate wait time
            tokens = limiter.state.available_tokens
            rate = limiter.current_rate
            
            if tokens >= 1:
                wait_time = 0
            else:
                wait_time = (1 - tokens) / rate
            
            # Factor in priority
            adjusted_wait = wait_time / limiter.config.priority_weight
            
            if adjusted_wait < min_wait:
                min_wait = adjusted_wait
                best_provider = provider
        
        return best_provider or providers[0]
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive stats for dashboard"""
        provider_stats = {}
        
        for provider, limiter in self.limiters.items():
            stats = limiter.get_stats()
            stats.update({
                'total_requests': self.stats[provider]['requests'],
                'total_wait_time': self.stats[provider]['wait_time'],
                'avg_wait_time': (
                    self.stats[provider]['wait_time'] / 
                    max(1, self.stats[provider]['requests'])
                )
            })
            provider_stats[provider] = stats
        
        # Global stats
        total_requests = sum(s['requests'] for s in self.stats.values())
        total_wait = sum(s['wait_time'] for s in self.stats.values())
        
        return {
            'providers': provider_stats,
            'global': {
                'total_requests': total_requests,
                'total_wait_time': total_wait,
                'avg_wait_time': total_wait / max(1, total_requests),
                'active_providers': len([
                    p for p, s in provider_stats.items() 
                    if s['total_requests'] > 0
                ])
            }
        }
    
    async def optimize_batch_requests(
        self, 
        requests: List[Tuple[str, Any]], 
        max_concurrent: int = 10
    ) -> List[Any]:
        """
        Optimize and execute a batch of requests across providers
        requests: List of (provider, request_data) tuples
        """
        # Group by provider
        by_provider = defaultdict(list)
        for provider, data in requests:
            by_provider[provider].append(data)
        
        # Sort providers by current availability
        provider_order = []
        for provider, items in by_provider.items():
            if provider in self.limiters:
                limiter = self.limiters[provider]
                score = (
                    limiter.state.available_tokens * 
                    limiter.config.priority_weight /
                    len(items)
                )
                provider_order.append((score, provider))
        
        provider_order.sort(reverse=True)
        
        # Execute requests with rate limiting
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_request(provider: str, data: Any):
            async with semaphore:
                await self.acquire(provider)
                # Simulate request execution
                await asyncio.sleep(0.1)
                return f"Result for {provider}: {data}"
        
        # Create tasks
        tasks = []
        for _, provider in provider_order:
            for data in by_provider[provider]:
                task = asyncio.create_task(execute_request(provider, data))
                tasks.append(task)
        
        # Execute all tasks
        results = await asyncio.gather(*tasks)
        
        return results


class RateLimitCache:
    """
    Caching layer that respects rate limits
    """
    
    def __init__(self, coordinator: GlobalRateLimitCoordinator):
        self.coordinator = coordinator
        self.cache = {}
        self.cache_stats = defaultdict(lambda: {'hits': 0, 'misses': 0})
    
    async def get_or_fetch(
        self, 
        provider: str, 
        key: str, 
        fetch_func: Callable,
        ttl: int = 300
    ) -> Any:
        """Get from cache or fetch with rate limiting"""
        cache_key = f"{provider}:{key}"
        
        # Check cache
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry['timestamp'] < ttl:
                self.cache_stats[provider]['hits'] += 1
                return entry['data']
        
        # Cache miss - fetch with rate limiting
        self.cache_stats[provider]['misses'] += 1
        
        # Acquire rate limit token
        wait_time = await self.coordinator.acquire(provider)
        
        # Fetch data
        try:
            data = await fetch_func()
            
            # Store in cache
            self.cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            return data
            
        except Exception as e:
            # Report violation if it's a rate limit error
            if '429' in str(e) or 'rate' in str(e).lower():
                self.coordinator.report_violation(provider)
            raise


# Example usage
async def main():
    # Initialize coordinator
    coordinator = GlobalRateLimitCoordinator()
    
    # Simulate requests to multiple providers
    providers = ['coingecko', 'coinmarketcap', 'dexscreener', 'jupiter']
    
    async def make_requests():
        tasks = []
        for i in range(100):
            provider = providers[i % len(providers)]
            wait_time = await coordinator.acquire(provider)
            print(f"Request {i} to {provider} - waited {wait_time:.3f}s")
            await asyncio.sleep(0.01)  # Simulate request
    
    # Run requests
    await make_requests()
    
    # Get stats
    stats = coordinator.get_dashboard_stats()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    asyncio.run(main())