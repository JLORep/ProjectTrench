#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified API Integration Layer
Connects all API infrastructure components into a single interface
Created: 2025-08-02
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

# Import our custom components
from comprehensive_api_providers import APIProviderRegistry, APICategory
from intelligent_data_aggregator import IntelligentDataAggregator, DataPoint
from api_credential_manager import APICredentialManager
from api_health_monitoring import APIHealthMonitor
from adaptive_rate_limiter import GlobalRateLimitCoordinator, RateLimitCache

@dataclass
class EnrichmentRequest:
    """Request for coin data enrichment"""
    coin_address: str
    coin_symbol: Optional[str] = None
    coin_name: Optional[str] = None
    categories: List[str] = field(default_factory=lambda: ['all'])
    priority: float = 1.0
    max_sources: int = 50
    timeout: int = 30

@dataclass
class EnrichmentResult:
    """Result of coin enrichment"""
    coin_address: str
    success: bool
    data: Dict[str, Any]
    sources_used: List[str]
    sources_failed: List[str]
    processing_time: float
    confidence_score: float
    error_message: Optional[str] = None

class UnifiedAPIManager:
    """
    Main API management system that orchestrates all components
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        
        # Initialize core components
        self.provider_registry = APIProviderRegistry()
        self.data_aggregator = IntelligentDataAggregator()
        self.credential_manager = APICredentialManager()
        self.health_monitor = APIHealthMonitor()
        self.rate_coordinator = GlobalRateLimitCoordinator()
        self.cache = RateLimitCache(self.rate_coordinator)
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.active_providers: Set[str] = set()
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'average_response_time': 0.0,
            'uptime_start': datetime.utcnow()
        }
        
        # Logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'max_concurrent_requests': 50,
            'default_timeout': 30,
            'cache_ttl': 300,  # 5 minutes
            'health_check_interval': 300,  # 5 minutes
            'auto_retry_on_failure': True,
            'max_retries': 3,
            'preferred_providers': {
                'price': ['coingecko', 'coinmarketcap', 'dexscreener'],
                'volume': ['coingecko', 'dexscreener', 'birdeye'],
                'security': ['tokensniffer', 'goplus', 'rugdoc'],
                'social': ['lunarcrush', 'santiment']
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    async def initialize(self):
        """Initialize the API management system"""
        self.logger.info("Initializing Unified API Manager...")
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=self.config['default_timeout'])
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Initialize credentials from environment
        await self.credential_manager.initialize_from_env()
        
        # Get available providers
        available_providers = self.provider_registry.get_available_providers()
        self.active_providers = set(available_providers.keys())
        
        # Start health monitoring for active providers
        await self.health_monitor.start_monitoring(list(self.active_providers))
        
        self.logger.info(f"Initialized with {len(self.active_providers)} active providers")
        
        return True
    
    async def shutdown(self):
        """Gracefully shutdown the system"""
        self.logger.info("Shutting down Unified API Manager...")
        
        # Stop health monitoring
        await self.health_monitor.stop_monitoring()
        
        # Close HTTP session
        if self.session:
            await self.session.close()
            self.session = None
        
        self.logger.info("Shutdown complete")
    
    async def enrich_coin(self, request: EnrichmentRequest) -> EnrichmentResult:
        """Enrich a single coin with data from multiple sources"""
        start_time = datetime.utcnow()
        
        self.logger.info(f"Starting enrichment for {request.coin_address}")
        
        # Determine which providers to use
        providers_to_use = await self._select_providers(request)
        
        # Fetch data from all selected providers
        raw_data = await self._fetch_from_providers(request, providers_to_use)
        
        # Aggregate and resolve conflicts
        aggregated_data = self.data_aggregator.aggregate_coin_data({
            'coin_address': request.coin_address,
            'data_sources': raw_data
        })
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Create result
        result = EnrichmentResult(
            coin_address=request.coin_address,
            success=len([k for k, v in raw_data.items() if 'error' not in v]) > 0,
            data=aggregated_data,
            sources_used=[k for k, v in raw_data.items() if 'error' not in v],
            sources_failed=[k for k, v in raw_data.items() if 'error' in v],
            processing_time=processing_time,
            confidence_score=aggregated_data.get('metadata', {}).get('overall_confidence', 0.0)
        )
        
        # Update statistics
        self._update_stats(result)
        
        self.logger.info(f"Enrichment completed for {request.coin_address} in {processing_time:.2f}s")
        
        return result
    
    async def enrich_coins_batch(self, requests: List[EnrichmentRequest]) -> List[EnrichmentResult]:
        """Enrich multiple coins in batch with optimal concurrency"""
        self.logger.info(f"Starting batch enrichment for {len(requests)} coins")
        
        # Limit concurrency to prevent overwhelming APIs
        semaphore = asyncio.Semaphore(self.config['max_concurrent_requests'])
        
        async def enrich_with_semaphore(req: EnrichmentRequest) -> EnrichmentResult:
            async with semaphore:
                return await self.enrich_coin(req)
        
        # Execute all enrichment requests concurrently
        tasks = [enrich_with_semaphore(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error result
                error_result = EnrichmentResult(
                    coin_address=requests[i].coin_address,
                    success=False,
                    data={},
                    sources_used=[],
                    sources_failed=[],
                    processing_time=0.0,
                    confidence_score=0.0,
                    error_message=str(result)
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
        
        successful = sum(1 for r in final_results if r.success)
        self.logger.info(f"Batch enrichment completed: {successful}/{len(requests)} successful")
        
        return final_results
    
    async def _select_providers(self, request: EnrichmentRequest) -> List[str]:
        """Select optimal providers for a request"""
        # Start with all available providers
        candidates = list(self.active_providers)
        
        # Filter by category if specified
        if 'all' not in request.categories:
            category_providers = set()
            for category in request.categories:
                if category in self.config['preferred_providers']:
                    category_providers.update(self.config['preferred_providers'][category])
            candidates = [p for p in candidates if p in category_providers]
        
        # Filter by health status
        healthy_providers = []
        for provider in candidates:
            if provider in self.health_monitor.health_status:
                status = self.health_monitor.health_status[provider]
                if status.status.value in ['healthy', 'degraded']:
                    healthy_providers.append(provider)
            else:
                # Include unknown providers (they might work)
                healthy_providers.append(provider)
        
        # Sort by priority (rate limit availability, reliability)
        sorted_providers = await self._sort_providers_by_priority(healthy_providers)
        
        # Limit to max_sources
        selected = sorted_providers[:request.max_sources]
        
        self.logger.debug(f"Selected {len(selected)} providers: {selected}")
        
        return selected
    
    async def _sort_providers_by_priority(self, providers: List[str]) -> List[str]:
        """Sort providers by current priority (availability + reliability)"""
        provider_scores = []
        
        for provider in providers:
            score = 0.0
            
            # Base reliability score
            if provider in self.rate_coordinator.limiters:
                limiter = self.rate_coordinator.limiters[provider]
                score += limiter.config.priority_weight
                
                # Bonus for available tokens
                score += limiter.state.available_tokens * 0.1
                
                # Penalty for violations
                score -= limiter.state.violations * 0.2
            
            # Health bonus
            if provider in self.health_monitor.health_status:
                health = self.health_monitor.health_status[provider]
                if health.status.value == 'healthy':
                    score += 0.3
                elif health.status.value == 'degraded':
                    score += 0.1
            
            provider_scores.append((score, provider))
        
        # Sort by score (highest first)
        provider_scores.sort(reverse=True)
        
        return [provider for score, provider in provider_scores]
    
    async def _fetch_from_providers(self, request: EnrichmentRequest, providers: List[str]) -> Dict[str, Any]:
        """Fetch data from multiple providers concurrently"""
        results = {}
        
        # Create tasks for each provider
        tasks = []
        for provider in providers:
            task = asyncio.create_task(
                self._fetch_from_single_provider(provider, request)
            )
            tasks.append((provider, task))
        
        # Wait for all tasks to complete
        for provider, task in tasks:
            try:
                data = await task
                results[provider] = data
            except Exception as e:
                self.logger.warning(f"Failed to fetch from {provider}: {e}")
                results[provider] = {'error': str(e)}
        
        return results
    
    async def _fetch_from_single_provider(self, provider: str, request: EnrichmentRequest) -> Dict[str, Any]:
        """Fetch data from a single provider with rate limiting and caching"""
        # Check cache first
        cache_key = f"{provider}:{request.coin_address}"
        
        try:
            # Use cached fetch with rate limiting
            async def fetch_func():
                return await self._make_api_request(provider, request)
            
            data = await self.cache.get_or_fetch(
                provider=provider,
                key=request.coin_address,
                fetch_func=fetch_func,
                ttl=self.config['cache_ttl']
            )
            
            return data
            
        except Exception as e:
            # Report rate limit violations
            if '429' in str(e) or 'rate' in str(e).lower():
                self.rate_coordinator.report_violation(provider)
            raise
    
    async def _make_api_request(self, provider: str, request: EnrichmentRequest) -> Dict[str, Any]:
        """Make actual API request to a provider"""
        # Get provider configuration
        provider_config = self.provider_registry.get_provider(provider)
        if not provider_config:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Get authentication
        headers = await self.credential_manager.get_auth_headers(provider)
        params = await self.credential_manager.get_auth_params(provider)
        
        # Build request URL and parameters
        endpoint_data = self._build_request_params(provider_config, request)
        
        # Add auth params
        endpoint_data['params'].update(params)
        
        # Make request
        async with self.session.get(
            endpoint_data['url'],
            headers={**headers, **endpoint_data['headers']},
            params=endpoint_data['params']
        ) as response:
            
            if response.status == 429:
                # Report rate limit hit
                raise Exception(f"Rate limit hit for {provider}")
            
            response.raise_for_status()
            
            # Parse response
            data = await response.json()
            
            # Normalize data format
            normalized_data = self._normalize_provider_response(provider, data)
            
            return normalized_data
    
    def _build_request_params(self, provider_config: Any, request: EnrichmentRequest) -> Dict[str, Any]:
        """Build request parameters for a specific provider"""
        # This would contain provider-specific logic
        # For now, return basic structure
        
        base_url = provider_config.base_url
        
        # Default endpoint mapping (would be provider-specific)
        endpoint_mappings = {
            'coingecko': {
                'url': f"{base_url}/coins/{request.coin_address}",
                'params': {'vs_currencies': 'usd', 'include_24hr_change': 'true'},
                'headers': {}
            },
            'dexscreener': {
                'url': f"{base_url}/latest/dex/tokens/{request.coin_address}",
                'params': {},
                'headers': {}
            },
            'birdeye': {
                'url': f"{base_url}/public/price",
                'params': {'address': request.coin_address},
                'headers': {}
            }
        }
        
        return endpoint_mappings.get(provider_config.name, {
            'url': f"{base_url}/token/{request.coin_address}",
            'params': {},
            'headers': {}
        })
    
    def _normalize_provider_response(self, provider: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize provider response to standard format"""
        # Provider-specific normalization logic
        # This would contain mappings for each provider's response format
        
        normalized = {
            'timestamp': datetime.utcnow().isoformat(),
            'provider': provider,
            'raw_data': data
        }
        
        # Basic normalization (would be expanded for each provider)
        if provider == 'coingecko':
            if 'market_data' in data:
                market_data = data['market_data']
                normalized.update({
                    'price': market_data.get('current_price', {}).get('usd'),
                    'volume_24h': market_data.get('total_volume', {}).get('usd'),
                    'market_cap': market_data.get('market_cap', {}).get('usd'),
                    'price_change_24h': market_data.get('price_change_24h'),
                    'price_change_percentage_24h': market_data.get('price_change_percentage_24h')
                })
        
        elif provider == 'dexscreener':
            if 'pairs' in data and data['pairs']:
                pair = data['pairs'][0]  # Take first pair
                normalized.update({
                    'price': float(pair.get('priceUsd', 0)),
                    'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                    'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0))
                })
        
        elif provider == 'birdeye':
            if 'data' in data:
                bird_data = data['data']
                normalized.update({
                    'price': bird_data.get('value'),
                    'price_change_24h': bird_data.get('updateHumanTime')
                })
        
        return normalized
    
    def _update_stats(self, result: EnrichmentResult):
        """Update system statistics"""
        self.stats['total_requests'] += 1
        
        if result.success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        # Update average response time
        current_avg = self.stats['average_response_time']
        total_requests = self.stats['total_requests']
        
        self.stats['average_response_time'] = (
            (current_avg * (total_requests - 1) + result.processing_time) / total_requests
        )
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Get health data
        health_data = self.health_monitor.get_dashboard_data()
        
        # Get rate limit stats
        rate_limit_stats = self.rate_coordinator.get_dashboard_stats()
        
        # Get credential health
        credential_health = await self.credential_manager.get_health_dashboard()
        
        # Calculate uptime
        uptime = datetime.utcnow() - self.stats['uptime_start']
        
        return {
            'system': {
                'status': 'operational',
                'uptime_seconds': uptime.total_seconds(),
                'active_providers': len(self.active_providers),
                'total_requests': self.stats['total_requests'],
                'success_rate': (
                    self.stats['successful_requests'] / max(1, self.stats['total_requests'])
                ),
                'average_response_time': self.stats['average_response_time']
            },
            'providers': health_data,
            'rate_limits': rate_limit_stats,
            'credentials': credential_health,
            'configuration': {
                'max_concurrent': self.config['max_concurrent_requests'],
                'cache_ttl': self.config['cache_ttl'],
                'health_check_interval': self.config['health_check_interval']
            }
        }
    
    async def get_provider_recommendations(self, coin_address: str) -> Dict[str, Any]:
        """Get recommendations for best providers for a specific coin"""
        # Analyze historical performance for this coin type
        recommendations = {
            'primary': [],
            'secondary': [],
            'avoid': []
        }
        
        # Get current provider health
        for provider in self.active_providers:
            if provider in self.health_monitor.health_status:
                health = self.health_monitor.health_status[provider]
                
                if health.uptime_percentage > 0.95 and health.avg_response_time_ms < 1000:
                    recommendations['primary'].append(provider)
                elif health.uptime_percentage > 0.90:
                    recommendations['secondary'].append(provider)
                else:
                    recommendations['avoid'].append(provider)
        
        return recommendations

# Factory function for easy initialization
async def create_api_manager(config_path: Optional[str] = None) -> UnifiedAPIManager:
    """Create and initialize a UnifiedAPIManager instance"""
    manager = UnifiedAPIManager(config_path)
    await manager.initialize()
    return manager

# Example usage
async def main():
    """Example usage of the Unified API Manager"""
    
    # Initialize the manager
    api_manager = await create_api_manager()
    
    try:
        # Single coin enrichment
        request = EnrichmentRequest(
            coin_address="So11111111111111111111111111111111111111112",  # SOL
            coin_symbol="SOL",
            categories=['price', 'volume', 'social'],
            priority=1.0
        )
        
        result = await api_manager.enrich_coin(request)
        print(f"Enrichment result: {result.success}")
        print(f"Sources used: {result.sources_used}")
        print(f"Confidence: {result.confidence_score:.2f}")
        
        # Batch enrichment
        batch_requests = [
            EnrichmentRequest("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "USDC"),  # USDC
            EnrichmentRequest("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "USDT"),  # USDT
        ]
        
        batch_results = await api_manager.enrich_coins_batch(batch_requests)
        print(f"Batch results: {len(batch_results)} coins processed")
        
        # Get system status
        status = await api_manager.get_system_status()
        print(f"System status: {status['system']['status']}")
        print(f"Active providers: {status['system']['active_providers']}")
        
    finally:
        # Cleanup
        await api_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())