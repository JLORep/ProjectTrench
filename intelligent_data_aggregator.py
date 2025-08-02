#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent Data Aggregation System
Handles conflict resolution, confidence scoring, and multi-source data fusion
Created: 2025-08-02
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics
from collections import defaultdict
import json
import hashlib

@dataclass
class DataPoint:
    """Represents a single data point from a source"""
    source: str
    value: Any
    timestamp: datetime
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregatedResult:
    """Result of data aggregation with metadata"""
    value: Any
    confidence: float
    sources: List[str]
    variance: Optional[float]
    conflicts: List[Dict[str, Any]]
    resolution_method: str
    metadata: Dict[str, Any]

class ConflictResolver:
    """Resolves conflicts between different data sources"""
    
    def __init__(self):
        self.source_weights = self._initialize_source_weights()
        self.resolution_strategies = {
            'weighted_average': self._weighted_average,
            'majority_vote': self._majority_vote,
            'highest_confidence': self._highest_confidence,
            'most_recent': self._most_recent,
            'median': self._median_value,
            'outlier_removal': self._outlier_removal,
            'source_priority': self._source_priority
        }
    
    def _initialize_source_weights(self) -> Dict[str, float]:
        """Initialize reliability weights for each source"""
        return {
            # Tier 1 - Most Reliable (0.9-1.0)
            'chainlink': 1.0,  # Decentralized oracle
            'coingecko': 0.95,
            'binance': 0.95,
            'coinbase': 0.95,
            'etherscan': 0.95,
            'moralis': 0.92,
            'coinmarketcap': 0.90,
            
            # Tier 2 - Very Reliable (0.8-0.9)
            'messari': 0.88,
            'defillama': 0.88,
            'dexscreener': 0.85,
            'jupiter': 0.85,
            'birdeye': 0.85,
            'geckoterminal': 0.85,
            '1inch': 0.85,
            '0x': 0.85,
            
            # Tier 3 - Reliable (0.7-0.8)
            'raydium': 0.78,
            'orca': 0.78,
            'solscan': 0.78,
            'helius': 0.78,
            'cryptocompare': 0.75,
            'coinpaprika': 0.75,
            'taapi': 0.75,
            
            # Tier 4 - Moderate (0.6-0.7)
            'pump_fun': 0.65,
            'gmgn': 0.68,
            'tradingview': 0.70,
            'alternative_me': 0.68,
            
            # Tier 5 - Lower Priority (0.5-0.6)
            'reddit': 0.55,
            'cryptopanic': 0.58,
            'lunarcrush': 0.58,
            
            # Default for unknown sources
            'default': 0.50
        }
    
    def resolve(self, data_points: List[DataPoint], strategy: str = 'weighted_average') -> AggregatedResult:
        """Resolve conflicts between multiple data points"""
        if not data_points:
            return AggregatedResult(
                value=None,
                confidence=0.0,
                sources=[],
                variance=None,
                conflicts=[],
                resolution_method='no_data',
                metadata={}
            )
        
        if len(data_points) == 1:
            dp = data_points[0]
            return AggregatedResult(
                value=dp.value,
                confidence=dp.confidence,
                sources=[dp.source],
                variance=0.0,
                conflicts=[],
                resolution_method='single_source',
                metadata=dp.metadata
            )
        
        # Detect conflicts
        conflicts = self._detect_conflicts(data_points)
        
        # Apply resolution strategy
        if strategy not in self.resolution_strategies:
            strategy = 'weighted_average'
        
        resolver_func = self.resolution_strategies[strategy]
        result = resolver_func(data_points)
        
        # Add conflict information
        result.conflicts = conflicts
        result.resolution_method = strategy
        
        return result
    
    def _detect_conflicts(self, data_points: List[DataPoint]) -> List[Dict[str, Any]]:
        """Detect significant conflicts between data points"""
        conflicts = []
        
        if not data_points or len(data_points) < 2:
            return conflicts
        
        # For numeric values, check variance
        if all(isinstance(dp.value, (int, float)) for dp in data_points):
            values = [dp.value for dp in data_points]
            mean = statistics.mean(values)
            
            for dp in data_points:
                deviation = abs(dp.value - mean) / mean if mean != 0 else 0
                if deviation > 0.1:  # More than 10% deviation
                    conflicts.append({
                        'source': dp.source,
                        'value': dp.value,
                        'deviation': deviation,
                        'type': 'numeric_deviation'
                    })
        
        # For categorical values, check disagreement
        elif all(isinstance(dp.value, str) for dp in data_points):
            value_counts = defaultdict(list)
            for dp in data_points:
                value_counts[dp.value].append(dp.source)
            
            if len(value_counts) > 1:
                for value, sources in value_counts.items():
                    conflicts.append({
                        'value': value,
                        'sources': sources,
                        'type': 'categorical_disagreement'
                    })
        
        return conflicts
    
    def _weighted_average(self, data_points: List[DataPoint]) -> AggregatedResult:
        """Calculate weighted average based on source reliability"""
        numeric_points = [dp for dp in data_points if isinstance(dp.value, (int, float))]
        
        if not numeric_points:
            return self._highest_confidence(data_points)
        
        weights = []
        values = []
        
        for dp in numeric_points:
            weight = self.source_weights.get(dp.source, self.source_weights['default'])
            weight *= dp.confidence  # Combine source weight with point confidence
            weights.append(weight)
            values.append(dp.value)
        
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        total_weight = sum(weights)
        
        if total_weight == 0:
            return self._median_value(data_points)
        
        weighted_avg = weighted_sum / total_weight
        
        # Calculate variance
        variance = statistics.variance(values) if len(values) > 1 else 0.0
        
        # Calculate confidence
        confidence = min(1.0, total_weight / len(numeric_points))
        
        return AggregatedResult(
            value=weighted_avg,
            confidence=confidence,
            sources=[dp.source for dp in numeric_points],
            variance=variance,
            conflicts=[],
            resolution_method='weighted_average',
            metadata={
                'weights': dict(zip([dp.source for dp in numeric_points], weights)),
                'raw_values': dict(zip([dp.source for dp in numeric_points], values))
            }
        )
    
    def _majority_vote(self, data_points: List[DataPoint]) -> AggregatedResult:
        """Use majority voting for categorical data"""
        vote_counts = defaultdict(lambda: {'count': 0, 'sources': [], 'total_confidence': 0})
        
        for dp in data_points:
            vote_counts[dp.value]['count'] += 1
            vote_counts[dp.value]['sources'].append(dp.source)
            vote_counts[dp.value]['total_confidence'] += dp.confidence
        
        # Find the value with most votes
        winner = max(vote_counts.items(), key=lambda x: (x[1]['count'], x[1]['total_confidence']))
        
        total_votes = len(data_points)
        confidence = winner[1]['count'] / total_votes
        
        return AggregatedResult(
            value=winner[0],
            confidence=confidence,
            sources=winner[1]['sources'],
            variance=None,
            conflicts=[],
            resolution_method='majority_vote',
            metadata={'vote_distribution': dict(vote_counts)}
        )
    
    def _highest_confidence(self, data_points: List[DataPoint]) -> AggregatedResult:
        """Select value from source with highest confidence"""
        best_point = max(data_points, key=lambda dp: dp.confidence * self.source_weights.get(dp.source, 0.5))
        
        return AggregatedResult(
            value=best_point.value,
            confidence=best_point.confidence,
            sources=[best_point.source],
            variance=None,
            conflicts=[],
            resolution_method='highest_confidence',
            metadata={'selected_source': best_point.source}
        )
    
    def _most_recent(self, data_points: List[DataPoint]) -> AggregatedResult:
        """Select the most recent data point"""
        latest_point = max(data_points, key=lambda dp: dp.timestamp)
        
        # Reduce confidence based on age
        age = datetime.utcnow() - latest_point.timestamp
        time_penalty = min(1.0, age.total_seconds() / 3600)  # Penalty for data older than 1 hour
        adjusted_confidence = latest_point.confidence * (1 - time_penalty * 0.5)
        
        return AggregatedResult(
            value=latest_point.value,
            confidence=adjusted_confidence,
            sources=[latest_point.source],
            variance=None,
            conflicts=[],
            resolution_method='most_recent',
            metadata={
                'timestamp': latest_point.timestamp.isoformat(),
                'age_seconds': age.total_seconds()
            }
        )
    
    def _median_value(self, data_points: List[DataPoint]) -> AggregatedResult:
        """Calculate median value for numeric data"""
        numeric_points = [dp for dp in data_points if isinstance(dp.value, (int, float))]
        
        if not numeric_points:
            return self._highest_confidence(data_points)
        
        values = [dp.value for dp in numeric_points]
        median = statistics.median(values)
        
        # Find closest actual value to median
        closest_point = min(numeric_points, key=lambda dp: abs(dp.value - median))
        
        return AggregatedResult(
            value=median,
            confidence=0.8,  # Median is generally reliable
            sources=[dp.source for dp in numeric_points],
            variance=statistics.variance(values) if len(values) > 1 else 0.0,
            conflicts=[],
            resolution_method='median',
            metadata={'closest_source': closest_point.source}
        )
    
    def _outlier_removal(self, data_points: List[DataPoint]) -> AggregatedResult:
        """Remove outliers using IQR method and average remaining"""
        numeric_points = [dp for dp in data_points if isinstance(dp.value, (int, float))]
        
        if len(numeric_points) < 4:
            return self._weighted_average(data_points)
        
        values = sorted([dp.value for dp in numeric_points])
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Filter out outliers
        filtered_points = [dp for dp in numeric_points if lower_bound <= dp.value <= upper_bound]
        
        if not filtered_points:
            return self._median_value(data_points)
        
        # Apply weighted average to remaining points
        result = self._weighted_average(filtered_points)
        result.resolution_method = 'outlier_removal'
        result.metadata['removed_count'] = len(numeric_points) - len(filtered_points)
        
        return result
    
    def _source_priority(self, data_points: List[DataPoint]) -> AggregatedResult:
        """Use predefined source priority order"""
        priority_order = [
            'chainlink', 'coingecko', 'binance', 'coinbase', 
            'etherscan', 'moralis', 'coinmarketcap', 'messari'
        ]
        
        # Sort data points by priority
        sorted_points = sorted(
            data_points,
            key=lambda dp: priority_order.index(dp.source) if dp.source in priority_order else 999
        )
        
        if sorted_points:
            return self._highest_confidence([sorted_points[0]])
        
        return self._highest_confidence(data_points)


class IntelligentDataAggregator:
    """
    Main aggregator that orchestrates data fusion from 100+ sources
    """
    
    def __init__(self):
        self.conflict_resolver = ConflictResolver()
        self.cache = {}
        self.aggregation_history = []
    
    def aggregate_coin_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate all data for a single coin from multiple sources
        """
        aggregated = {
            'metadata': {
                'aggregation_timestamp': datetime.utcnow().isoformat(),
                'total_sources': len(raw_data.get('data_sources', {})),
                'successful_sources': 0,
                'failed_sources': 0,
                'overall_confidence': 0.0
            },
            'core_metrics': {},
            'technical_indicators': {},
            'social_metrics': {},
            'security_analysis': {},
            'defi_metrics': {},
            'market_sentiment': {},
            'whale_activity': {},
            'developer_metrics': {}
        }
        
        # Process each data source
        data_by_metric = self._organize_by_metric(raw_data.get('data_sources', {}))
        
        # Aggregate each metric type
        for metric_type, data_points in data_by_metric.items():
            if data_points:
                result = self._aggregate_metric(metric_type, data_points)
                category = self._get_metric_category(metric_type)
                aggregated[category][metric_type] = result
        
        # Calculate overall confidence
        aggregated['metadata']['overall_confidence'] = self._calculate_overall_confidence(aggregated)
        
        # Add data quality assessment
        aggregated['data_quality'] = self._assess_data_quality(aggregated)
        
        return aggregated
    
    def _organize_by_metric(self, data_sources: Dict[str, Any]) -> Dict[str, List[DataPoint]]:
        """Organize raw data by metric type"""
        metric_data = defaultdict(list)
        
        for source, source_data in data_sources.items():
            if isinstance(source_data, dict) and 'error' not in source_data:
                # Extract standard metrics
                self._extract_price_data(source, source_data, metric_data)
                self._extract_volume_data(source, source_data, metric_data)
                self._extract_market_cap_data(source, source_data, metric_data)
                self._extract_technical_data(source, source_data, metric_data)
                self._extract_social_data(source, source_data, metric_data)
                self._extract_security_data(source, source_data, metric_data)
                self._extract_defi_data(source, source_data, metric_data)
                self._extract_whale_data(source, source_data, metric_data)
        
        return metric_data
    
    def _extract_price_data(self, source: str, data: Dict[str, Any], metric_data: Dict[str, List[DataPoint]]):
        """Extract price-related metrics"""
        price_keys = ['price', 'current_price', 'usd_price', 'price_usd']
        
        for key in price_keys:
            if key in data:
                metric_data['price'].append(DataPoint(
                    source=source,
                    value=float(data[key]),
                    timestamp=datetime.utcnow(),
                    confidence=self._calculate_source_confidence(source, data)
                ))
                break
        
        # Extract price changes
        change_keys = [
            ('price_change_24h', 'price_change_24h'),
            ('price_change_percentage_24h', 'price_change_pct_24h'),
            ('price_change_7d', 'price_change_7d'),
            ('price_change_30d', 'price_change_30d')
        ]
        
        for data_key, metric_key in change_keys:
            if data_key in data:
                metric_data[metric_key].append(DataPoint(
                    source=source,
                    value=float(data[data_key]),
                    timestamp=datetime.utcnow(),
                    confidence=self._calculate_source_confidence(source, data)
                ))
    
    def _extract_volume_data(self, source: str, data: Dict[str, Any], metric_data: Dict[str, List[DataPoint]]):
        """Extract volume metrics"""
        volume_keys = ['volume', 'volume_24h', 'total_volume', 'usd_volume_24h']
        
        for key in volume_keys:
            if key in data:
                metric_data['volume_24h'].append(DataPoint(
                    source=source,
                    value=float(data[key]),
                    timestamp=datetime.utcnow(),
                    confidence=self._calculate_source_confidence(source, data)
                ))
                break
    
    def _extract_market_cap_data(self, source: str, data: Dict[str, Any], metric_data: Dict[str, List[DataPoint]]):
        """Extract market cap metrics"""
        mcap_keys = ['market_cap', 'marketcap', 'market_cap_usd', 'mcap']
        
        for key in mcap_keys:
            if key in data:
                metric_data['market_cap'].append(DataPoint(
                    source=source,
                    value=float(data[key]),
                    timestamp=datetime.utcnow(),
                    confidence=self._calculate_source_confidence(source, data)
                ))
                break
        
        # Fully diluted market cap
        fdv_keys = ['fully_diluted_valuation', 'fdv', 'fully_diluted_market_cap']
        for key in fdv_keys:
            if key in data:
                metric_data['fdv'].append(DataPoint(
                    source=source,
                    value=float(data[key]),
                    timestamp=datetime.utcnow(),
                    confidence=self._calculate_source_confidence(source, data)
                ))
                break
    
    def _extract_technical_data(self, source: str, data: Dict[str, Any], metric_data: Dict[str, List[DataPoint]]):
        """Extract technical indicators"""
        technical_indicators = {
            'rsi': ['rsi', 'rsi_14'],
            'macd': ['macd', 'macd_signal'],
            'bollinger_upper': ['bb_upper', 'bollinger_upper'],
            'bollinger_lower': ['bb_lower', 'bollinger_lower'],
            'ema_20': ['ema_20', 'ema20'],
            'sma_50': ['sma_50', 'sma50'],
            'sma_200': ['sma_200', 'sma200']
        }
        
        for metric, keys in technical_indicators.items():
            for key in keys:
                if key in data:
                    metric_data[metric].append(DataPoint(
                        source=source,
                        value=float(data[key]),
                        timestamp=datetime.utcnow(),
                        confidence=self._calculate_source_confidence(source, data)
                    ))
                    break
    
    def _extract_social_data(self, source: str, data: Dict[str, Any], metric_data: Dict[str, List[DataPoint]]):
        """Extract social metrics"""
        social_metrics = {
            'twitter_followers': ['twitter_followers', 'twitter_count'],
            'reddit_subscribers': ['reddit_subscribers', 'reddit_count'],
            'telegram_members': ['telegram_members', 'telegram_count'],
            'social_score': ['social_score', 'community_score'],
            'sentiment_score': ['sentiment', 'sentiment_score', 'social_sentiment']
        }
        
        for metric, keys in social_metrics.items():
            for key in keys:
                if key in data:
                    metric_data[metric].append(DataPoint(
                        source=source,
                        value=data[key],
                        timestamp=datetime.utcnow(),
                        confidence=self._calculate_source_confidence(source, data)
                    ))
                    break
    
    def _extract_security_data(self, source: str, data: Dict[str, Any], metric_data: Dict[str, List[DataPoint]]):
        """Extract security metrics"""
        security_metrics = {
            'security_score': ['security_score', 'safety_score', 'trust_score'],
            'honeypot': ['is_honeypot', 'honeypot_status'],
            'rugpull_risk': ['rugpull_risk', 'rug_risk', 'scam_risk'],
            'contract_verified': ['contract_verified', 'is_verified']
        }
        
        for metric, keys in security_metrics.items():
            for key in keys:
                if key in data:
                    metric_data[metric].append(DataPoint(
                        source=source,
                        value=data[key],
                        timestamp=datetime.utcnow(),
                        confidence=self._calculate_source_confidence(source, data)
                    ))
                    break
    
    def _extract_defi_data(self, source: str, data: Dict[str, Any], metric_data: Dict[str, List[DataPoint]]):
        """Extract DeFi metrics"""
        defi_metrics = {
            'tvl': ['tvl', 'total_value_locked'],
            'liquidity': ['liquidity', 'total_liquidity'],
            'apy': ['apy', 'annual_percentage_yield'],
            'pool_count': ['pool_count', 'liquidity_pools']
        }
        
        for metric, keys in defi_metrics.items():
            for key in keys:
                if key in data:
                    metric_data[metric].append(DataPoint(
                        source=source,
                        value=data[key],
                        timestamp=datetime.utcnow(),
                        confidence=self._calculate_source_confidence(source, data)
                    ))
                    break
    
    def _extract_whale_data(self, source: str, data: Dict[str, Any], metric_data: Dict[str, List[DataPoint]]):
        """Extract whale activity metrics"""
        whale_metrics = {
            'whale_transactions': ['whale_transactions', 'large_transactions'],
            'whale_holdings': ['whale_holdings', 'top_holders_percentage'],
            'smart_money_flow': ['smart_money', 'smart_money_flow']
        }
        
        for metric, keys in whale_metrics.items():
            for key in keys:
                if key in data:
                    metric_data[metric].append(DataPoint(
                        source=source,
                        value=data[key],
                        timestamp=datetime.utcnow(),
                        confidence=self._calculate_source_confidence(source, data)
                    ))
                    break
    
    def _aggregate_metric(self, metric_type: str, data_points: List[DataPoint]) -> Dict[str, Any]:
        """Aggregate a specific metric from multiple sources"""
        # Determine best aggregation strategy based on metric type
        strategy = self._get_aggregation_strategy(metric_type)
        
        # Resolve conflicts and aggregate
        result = self.conflict_resolver.resolve(data_points, strategy)
        
        # Convert to dictionary format
        return {
            'value': result.value,
            'confidence': result.confidence,
            'sources': result.sources,
            'source_count': len(result.sources),
            'variance': result.variance,
            'has_conflicts': len(result.conflicts) > 0,
            'conflicts': result.conflicts,
            'resolution_method': result.resolution_method,
            'metadata': result.metadata
        }
    
    def _get_aggregation_strategy(self, metric_type: str) -> str:
        """Determine best aggregation strategy for a metric"""
        strategies = {
            # Price metrics - use outlier removal
            'price': 'outlier_removal',
            'price_change_24h': 'weighted_average',
            'price_change_pct_24h': 'weighted_average',
            
            # Volume/Market cap - weighted average
            'volume_24h': 'weighted_average',
            'market_cap': 'weighted_average',
            'fdv': 'weighted_average',
            'tvl': 'weighted_average',
            
            # Technical indicators - median
            'rsi': 'median',
            'macd': 'median',
            
            # Security - highest confidence
            'security_score': 'highest_confidence',
            'honeypot': 'majority_vote',
            'rugpull_risk': 'highest_confidence',
            
            # Social - weighted average
            'twitter_followers': 'weighted_average',
            'sentiment_score': 'weighted_average',
            
            # Default
            'default': 'weighted_average'
        }
        
        return strategies.get(metric_type, strategies['default'])
    
    def _get_metric_category(self, metric_type: str) -> str:
        """Determine which category a metric belongs to"""
        categories = {
            'core_metrics': ['price', 'volume_24h', 'market_cap', 'fdv', 'price_change_24h', 'price_change_pct_24h'],
            'technical_indicators': ['rsi', 'macd', 'bollinger_upper', 'bollinger_lower', 'ema_20', 'sma_50', 'sma_200'],
            'social_metrics': ['twitter_followers', 'reddit_subscribers', 'telegram_members', 'social_score', 'sentiment_score'],
            'security_analysis': ['security_score', 'honeypot', 'rugpull_risk', 'contract_verified'],
            'defi_metrics': ['tvl', 'liquidity', 'apy', 'pool_count'],
            'whale_activity': ['whale_transactions', 'whale_holdings', 'smart_money_flow']
        }
        
        for category, metrics in categories.items():
            if metric_type in metrics:
                return category
        
        return 'other_metrics'
    
    def _calculate_source_confidence(self, source: str, data: Dict[str, Any]) -> float:
        """Calculate confidence for a data point from a source"""
        base_confidence = self.conflict_resolver.source_weights.get(
            source, 
            self.conflict_resolver.source_weights['default']
        )
        
        # Adjust based on data freshness if timestamp available
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'])
                age = (datetime.utcnow() - timestamp).total_seconds()
                freshness_factor = max(0.5, 1 - (age / 3600))  # Decay over 1 hour
                base_confidence *= freshness_factor
            except:
                pass
        
        # Adjust based on data completeness
        completeness = len([k for k in data.keys() if k not in ['error', 'warning']]) / 10
        completeness_factor = min(1.0, 0.7 + completeness * 0.3)
        
        return min(1.0, base_confidence * completeness_factor)
    
    def _calculate_overall_confidence(self, aggregated_data: Dict[str, Any]) -> float:
        """Calculate overall confidence score for aggregated data"""
        confidences = []
        weights = []
        
        # Weight different categories differently
        category_weights = {
            'core_metrics': 1.0,
            'technical_indicators': 0.7,
            'social_metrics': 0.5,
            'security_analysis': 0.8,
            'defi_metrics': 0.6,
            'whale_activity': 0.6
        }
        
        for category, weight in category_weights.items():
            if category in aggregated_data and aggregated_data[category]:
                category_confidences = [
                    metric_data.get('confidence', 0) 
                    for metric_data in aggregated_data[category].values()
                    if isinstance(metric_data, dict)
                ]
                
                if category_confidences:
                    avg_confidence = sum(category_confidences) / len(category_confidences)
                    confidences.append(avg_confidence)
                    weights.append(weight)
        
        if not confidences:
            return 0.0
        
        weighted_confidence = sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
        return round(weighted_confidence, 3)
    
    def _assess_data_quality(self, aggregated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall data quality"""
        quality_assessment = {
            'overall_score': 0.0,
            'completeness': 0.0,
            'consistency': 0.0,
            'timeliness': 0.0,
            'source_diversity': 0.0,
            'recommendations': []
        }
        
        # Completeness - how many expected metrics do we have?
        expected_metrics = 30  # Approximate number of key metrics
        actual_metrics = sum(
            len(category_data) 
            for category_data in aggregated_data.values() 
            if isinstance(category_data, dict)
        )
        quality_assessment['completeness'] = min(1.0, actual_metrics / expected_metrics)
        
        # Consistency - how many conflicts?
        total_conflicts = sum(
            len(metric_data.get('conflicts', [])) 
            for category_data in aggregated_data.values() 
            if isinstance(category_data, dict)
            for metric_data in category_data.values()
            if isinstance(metric_data, dict)
        )
        quality_assessment['consistency'] = max(0, 1 - (total_conflicts / max(actual_metrics, 1)) * 0.5)
        
        # Source diversity
        unique_sources = set()
        for category_data in aggregated_data.values():
            if isinstance(category_data, dict):
                for metric_data in category_data.values():
                    if isinstance(metric_data, dict) and 'sources' in metric_data:
                        unique_sources.update(metric_data['sources'])
        
        quality_assessment['source_diversity'] = min(1.0, len(unique_sources) / 10)  # 10+ sources is excellent
        
        # Overall score
        quality_assessment['overall_score'] = (
            quality_assessment['completeness'] * 0.3 +
            quality_assessment['consistency'] * 0.3 +
            quality_assessment['source_diversity'] * 0.4
        )
        
        # Recommendations
        if quality_assessment['completeness'] < 0.7:
            quality_assessment['recommendations'].append("Increase data source coverage")
        if quality_assessment['consistency'] < 0.7:
            quality_assessment['recommendations'].append("Investigate and resolve data conflicts")
        if quality_assessment['source_diversity'] < 0.5:
            quality_assessment['recommendations'].append("Add more diverse data sources")
        
        return quality_assessment


# Example usage
if __name__ == "__main__":
    aggregator = IntelligentDataAggregator()
    
    # Example raw data from multiple sources
    raw_data = {
        'data_sources': {
            'coingecko': {
                'price': 50000,
                'volume_24h': 1000000000,
                'market_cap': 1000000000000
            },
            'coinmarketcap': {
                'price': 50100,
                'volume_24h': 1050000000,
                'market_cap': 1001000000000
            },
            'dexscreener': {
                'price': 49800,
                'volume_24h': 980000000
            }
        }
    }
    
    result = aggregator.aggregate_coin_data(raw_data)
    print(json.dumps(result, indent=2, default=str))