#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Normalization Schemas
Standardizes data formats across 100+ API providers
Created: 2025-08-02
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from decimal import Decimal
from enum import Enum

class DataType(Enum):
    """Supported data types for normalization"""
    NUMERIC = "numeric"
    STRING = "string"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    ADDRESS = "address"
    URL = "url"
    ENUM = "enum"

@dataclass
class FieldMapping:
    """Maps provider field to normalized field"""
    provider_field: str
    normalized_field: str
    data_type: DataType
    transform_func: Optional[Callable] = None
    required: bool = False
    default_value: Any = None

@dataclass
class NormalizedCoinData:
    """Standardized coin data structure"""
    # Core identifiers
    address: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    
    # Price metrics
    price_usd: Optional[Decimal] = None
    price_change_1h: Optional[Decimal] = None
    price_change_24h: Optional[Decimal] = None
    price_change_7d: Optional[Decimal] = None
    price_change_30d: Optional[Decimal] = None
    
    # Volume metrics
    volume_24h_usd: Optional[Decimal] = None
    volume_change_24h: Optional[Decimal] = None
    
    # Market metrics
    market_cap_usd: Optional[Decimal] = None
    market_cap_rank: Optional[int] = None
    fully_diluted_valuation: Optional[Decimal] = None
    circulating_supply: Optional[Decimal] = None
    total_supply: Optional[Decimal] = None
    max_supply: Optional[Decimal] = None
    
    # Technical indicators
    rsi_14: Optional[Decimal] = None
    macd: Optional[Decimal] = None
    bollinger_upper: Optional[Decimal] = None
    bollinger_lower: Optional[Decimal] = None
    ema_20: Optional[Decimal] = None
    sma_50: Optional[Decimal] = None
    sma_200: Optional[Decimal] = None
    
    # Social metrics
    twitter_followers: Optional[int] = None
    reddit_subscribers: Optional[int] = None
    telegram_members: Optional[int] = None
    social_score: Optional[Decimal] = None
    sentiment_score: Optional[Decimal] = None
    
    # Security metrics
    security_score: Optional[Decimal] = None
    is_honeypot: Optional[bool] = None
    rugpull_risk: Optional[str] = None
    contract_verified: Optional[bool] = None
    audit_status: Optional[str] = None
    
    # DeFi metrics
    tvl_usd: Optional[Decimal] = None
    liquidity_usd: Optional[Decimal] = None
    apy: Optional[Decimal] = None
    pool_count: Optional[int] = None
    
    # Whale activity
    whale_transactions_24h: Optional[int] = None
    whale_holdings_percentage: Optional[Decimal] = None
    smart_money_flow_24h: Optional[Decimal] = None
    
    # Developer metrics
    github_commits_30d: Optional[int] = None
    github_contributors: Optional[int] = None
    code_quality_score: Optional[Decimal] = None
    
    # Trading metrics
    all_time_high: Optional[Decimal] = None
    all_time_low: Optional[Decimal] = None
    ath_change_percentage: Optional[Decimal] = None
    atl_change_percentage: Optional[Decimal] = None
    
    # Metadata
    last_updated: Optional[datetime] = None
    data_provider: Optional[str] = None
    confidence_score: Optional[Decimal] = None

class DataNormalizer:
    """Normalizes data from different providers to standard format"""
    
    def __init__(self):
        self.provider_mappings = self._initialize_provider_mappings()
        self.transformers = self._initialize_transformers()
    
    def _initialize_provider_mappings(self) -> Dict[str, List[FieldMapping]]:
        """Initialize field mappings for each provider"""
        return {
            'coingecko': [
                # Price data
                FieldMapping('market_data.current_price.usd', 'price_usd', DataType.CURRENCY),
                FieldMapping('market_data.price_change_percentage_1h_in_currency.usd', 'price_change_1h', DataType.PERCENTAGE),
                FieldMapping('market_data.price_change_percentage_24h_in_currency.usd', 'price_change_24h', DataType.PERCENTAGE),
                FieldMapping('market_data.price_change_percentage_7d_in_currency.usd', 'price_change_7d', DataType.PERCENTAGE),
                FieldMapping('market_data.price_change_percentage_30d_in_currency.usd', 'price_change_30d', DataType.PERCENTAGE),
                
                # Volume and market cap
                FieldMapping('market_data.total_volume.usd', 'volume_24h_usd', DataType.CURRENCY),
                FieldMapping('market_data.market_cap.usd', 'market_cap_usd', DataType.CURRENCY),
                FieldMapping('market_cap_rank', 'market_cap_rank', DataType.NUMERIC),
                FieldMapping('market_data.fully_diluted_valuation.usd', 'fully_diluted_valuation', DataType.CURRENCY),
                
                # Supply metrics
                FieldMapping('market_data.circulating_supply', 'circulating_supply', DataType.NUMERIC),
                FieldMapping('market_data.total_supply', 'total_supply', DataType.NUMERIC),
                FieldMapping('market_data.max_supply', 'max_supply', DataType.NUMERIC),
                
                # Social data
                FieldMapping('community_data.twitter_followers', 'twitter_followers', DataType.NUMERIC),
                FieldMapping('community_data.reddit_subscribers', 'reddit_subscribers', DataType.NUMERIC),
                FieldMapping('community_data.telegram_channel_user_count', 'telegram_members', DataType.NUMERIC),
                
                # ATH/ATL
                FieldMapping('market_data.ath.usd', 'all_time_high', DataType.CURRENCY),
                FieldMapping('market_data.atl.usd', 'all_time_low', DataType.CURRENCY),
                FieldMapping('market_data.ath_change_percentage.usd', 'ath_change_percentage', DataType.PERCENTAGE),
                FieldMapping('market_data.atl_change_percentage.usd', 'atl_change_percentage', DataType.PERCENTAGE),
                
                # Basic info
                FieldMapping('symbol', 'symbol', DataType.STRING, transform_func=str.upper),
                FieldMapping('name', 'name', DataType.STRING),
                FieldMapping('last_updated', 'last_updated', DataType.DATETIME),
            ],
            
            'coinmarketcap': [
                # Price data
                FieldMapping('data.0.quote.USD.price', 'price_usd', DataType.CURRENCY),
                FieldMapping('data.0.quote.USD.percent_change_1h', 'price_change_1h', DataType.PERCENTAGE),
                FieldMapping('data.0.quote.USD.percent_change_24h', 'price_change_24h', DataType.PERCENTAGE),
                FieldMapping('data.0.quote.USD.percent_change_7d', 'price_change_7d', DataType.PERCENTAGE),
                FieldMapping('data.0.quote.USD.percent_change_30d', 'price_change_30d', DataType.PERCENTAGE),
                
                # Volume and market cap
                FieldMapping('data.0.quote.USD.volume_24h', 'volume_24h_usd', DataType.CURRENCY),
                FieldMapping('data.0.quote.USD.market_cap', 'market_cap_usd', DataType.CURRENCY),
                FieldMapping('data.0.cmc_rank', 'market_cap_rank', DataType.NUMERIC),
                FieldMapping('data.0.quote.USD.fully_diluted_market_cap', 'fully_diluted_valuation', DataType.CURRENCY),
                
                # Supply
                FieldMapping('data.0.circulating_supply', 'circulating_supply', DataType.NUMERIC),
                FieldMapping('data.0.total_supply', 'total_supply', DataType.NUMERIC),
                FieldMapping('data.0.max_supply', 'max_supply', DataType.NUMERIC),
                
                # Basic info
                FieldMapping('data.0.symbol', 'symbol', DataType.STRING, transform_func=str.upper),
                FieldMapping('data.0.name', 'name', DataType.STRING),
                FieldMapping('data.0.last_updated', 'last_updated', DataType.DATETIME),
            ],
            
            'dexscreener': [
                # Price data from first pair
                FieldMapping('pairs.0.priceUsd', 'price_usd', DataType.CURRENCY),
                FieldMapping('pairs.0.priceChange.h1', 'price_change_1h', DataType.PERCENTAGE),
                FieldMapping('pairs.0.priceChange.h24', 'price_change_24h', DataType.PERCENTAGE),
                
                # Volume
                FieldMapping('pairs.0.volume.h24', 'volume_24h_usd', DataType.CURRENCY),
                FieldMapping('pairs.0.volume.h6', 'volume_6h_usd', DataType.CURRENCY),
                
                # Liquidity
                FieldMapping('pairs.0.liquidity.usd', 'liquidity_usd', DataType.CURRENCY),
                
                # Basic info
                FieldMapping('pairs.0.baseToken.symbol', 'symbol', DataType.STRING, transform_func=str.upper),
                FieldMapping('pairs.0.baseToken.name', 'name', DataType.STRING),
                FieldMapping('pairs.0.baseToken.address', 'address', DataType.ADDRESS),
            ],
            
            'birdeye': [
                # Price data
                FieldMapping('data.value', 'price_usd', DataType.CURRENCY),
                FieldMapping('data.updateUnixTime', 'last_updated', DataType.DATETIME, transform_func=lambda x: datetime.fromtimestamp(x, tz=timezone.utc)),
                
                # Volume (if available)
                FieldMapping('data.volume24h', 'volume_24h_usd', DataType.CURRENCY),
                FieldMapping('data.liquidity', 'liquidity_usd', DataType.CURRENCY),
            ],
            
            'jupiter': [
                # Basic token info
                FieldMapping('symbol', 'symbol', DataType.STRING, transform_func=str.upper),
                FieldMapping('name', 'name', DataType.STRING),
                FieldMapping('address', 'address', DataType.ADDRESS),
                FieldMapping('decimals', 'decimals', DataType.NUMERIC),
            ],
            
            'moralis': [
                # Price and volume from token stats
                FieldMapping('usdPrice', 'price_usd', DataType.CURRENCY),
                FieldMapping('24hrPercentChange', 'price_change_24h', DataType.PERCENTAGE),
                FieldMapping('24hrUsdVolume', 'volume_24h_usd', DataType.CURRENCY),
            ],
            
            'tokensniffer': [
                # Security metrics
                FieldMapping('score', 'security_score', DataType.NUMERIC, transform_func=lambda x: Decimal(str(x)) / 100),
                FieldMapping('is_honeypot', 'is_honeypot', DataType.BOOLEAN),
                FieldMapping('rugpull_risk', 'rugpull_risk', DataType.STRING),
                FieldMapping('contract_verified', 'contract_verified', DataType.BOOLEAN),
            ],
            
            'goplus': [
                # Security analysis
                FieldMapping('result.is_honeypot', 'is_honeypot', DataType.BOOLEAN, transform_func=lambda x: x == '1'),
                FieldMapping('result.trust_list', 'contract_verified', DataType.BOOLEAN, transform_func=lambda x: x == '1'),
                FieldMapping('result.is_open_source', 'open_source', DataType.BOOLEAN, transform_func=lambda x: x == '1'),
            ],
            
            'lunarcrush': [
                # Social metrics
                FieldMapping('data.twitter_followers', 'twitter_followers', DataType.NUMERIC),
                FieldMapping('data.reddit_subscribers', 'reddit_subscribers', DataType.NUMERIC),
                FieldMapping('data.social_score', 'social_score', DataType.NUMERIC),
                FieldMapping('data.sentiment_score', 'sentiment_score', DataType.NUMERIC),
            ],
            
            'defillama': [
                # DeFi metrics
                FieldMapping('tvl', 'tvl_usd', DataType.CURRENCY),
                FieldMapping('apy', 'apy', DataType.PERCENTAGE),
                FieldMapping('pool_count', 'pool_count', DataType.NUMERIC),
            ]
        }
    
    def _initialize_transformers(self) -> Dict[DataType, Callable]:
        """Initialize data type transformers"""
        return {
            DataType.NUMERIC: self._to_decimal,
            DataType.STRING: self._to_string,
            DataType.BOOLEAN: self._to_boolean,
            DataType.DATETIME: self._to_datetime,
            DataType.PERCENTAGE: self._to_percentage,
            DataType.CURRENCY: self._to_currency,
            DataType.ADDRESS: self._to_address,
            DataType.URL: self._to_url,
        }
    
    def normalize_provider_data(self, provider: str, raw_data: Dict[str, Any]) -> NormalizedCoinData:
        """Normalize data from a specific provider"""
        if provider not in self.provider_mappings:
            # Return minimal normalized data for unknown providers
            return NormalizedCoinData(
                address="unknown",
                data_provider=provider,
                last_updated=datetime.utcnow()
            )
        
        mappings = self.provider_mappings[provider]
        normalized_data = {}
        
        # Process each field mapping
        for mapping in mappings:
            try:
                # Extract value using dot notation
                value = self._extract_nested_value(raw_data, mapping.provider_field)
                
                if value is not None:
                    # Apply custom transform function if provided
                    if mapping.transform_func:
                        value = mapping.transform_func(value)
                    else:
                        # Apply data type transformation
                        transformer = self.transformers.get(mapping.data_type)
                        if transformer:
                            value = transformer(value)
                    
                    normalized_data[mapping.normalized_field] = value
                
                elif mapping.required and mapping.default_value is not None:
                    normalized_data[mapping.normalized_field] = mapping.default_value
                    
            except Exception as e:
                # Log error but continue processing
                print(f"Error normalizing {mapping.provider_field} from {provider}: {e}")
                
                if mapping.required and mapping.default_value is not None:
                    normalized_data[mapping.normalized_field] = mapping.default_value
        
        # Add metadata
        normalized_data['data_provider'] = provider
        normalized_data['last_updated'] = datetime.utcnow()
        
        # Create NormalizedCoinData instance
        return NormalizedCoinData(**{k: v for k, v in normalized_data.items() if hasattr(NormalizedCoinData, k)})
    
    def _extract_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from nested dictionary using dot notation"""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                current = current[index] if index < len(current) else None
            else:
                return None
            
            if current is None:
                return None
        
        return current
    
    def _to_decimal(self, value: Any) -> Optional[Decimal]:
        """Convert value to Decimal"""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except:
            return None
    
    def _to_string(self, value: Any) -> Optional[str]:
        """Convert value to string"""
        if value is None:
            return None
        return str(value)
    
    def _to_boolean(self, value: Any) -> Optional[bool]:
        """Convert value to boolean"""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        if isinstance(value, (int, float)):
            return bool(value)
        return None
    
    def _to_datetime(self, value: Any) -> Optional[datetime]:
        """Convert value to datetime"""
        if value is None:
            return None
        
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, str):
            # Try different datetime formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
        
        if isinstance(value, (int, float)):
            # Assume Unix timestamp
            try:
                return datetime.fromtimestamp(value, tz=timezone.utc)
            except:
                pass
        
        return None
    
    def _to_percentage(self, value: Any) -> Optional[Decimal]:
        """Convert value to percentage (as decimal)"""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except:
            return None
    
    def _to_currency(self, value: Any) -> Optional[Decimal]:
        """Convert value to currency (as decimal)"""
        if value is None:
            return None
        try:
            # Remove currency symbols and commas
            if isinstance(value, str):
                # Remove common currency symbols and formatting
                clean_value = re.sub(r'[$,€£¥₹]', '', value)
                return Decimal(clean_value)
            return Decimal(str(value))
        except:
            return None
    
    def _to_address(self, value: Any) -> Optional[str]:
        """Convert and validate blockchain address"""
        if value is None:
            return None
        
        address = str(value)
        
        # Basic validation (could be expanded for specific chains)
        if len(address) >= 26:  # Minimum reasonable address length
            return address
        
        return None
    
    def _to_url(self, value: Any) -> Optional[str]:
        """Convert and validate URL"""
        if value is None:
            return None
        
        url = str(value)
        
        # Basic URL validation
        if url.startswith(('http://', 'https://')):
            return url
        
        return None

class DataQualityValidator:
    """Validates normalized data quality"""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[str, Callable]:
        """Initialize validation rules for different fields"""
        return {
            'price_usd': lambda x: x is not None and x > 0,
            'market_cap_usd': lambda x: x is None or x > 0,
            'volume_24h_usd': lambda x: x is None or x >= 0,
            'circulating_supply': lambda x: x is None or x > 0,
            'price_change_24h': lambda x: x is None or abs(x) < 1000,  # Sanity check
            'security_score': lambda x: x is None or (0 <= x <= 1),
            'social_score': lambda x: x is None or (0 <= x <= 100),
        }
    
    def validate_data(self, data: NormalizedCoinData) -> Dict[str, Any]:
        """Validate normalized data and return quality report"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'completeness_score': 0.0,
            'quality_score': 0.0
        }
        
        # Check required fields
        if not data.address or data.address == "unknown":
            validation_results['errors'].append("Missing or invalid address")
            validation_results['is_valid'] = False
        
        # Validate individual fields
        for field_name, validation_func in self.validation_rules.items():
            field_value = getattr(data, field_name, None)
            
            if field_value is not None:
                try:
                    if not validation_func(field_value):
                        validation_results['warnings'].append(f"Invalid {field_name}: {field_value}")
                except Exception as e:
                    validation_results['warnings'].append(f"Validation error for {field_name}: {e}")
        
        # Calculate completeness score
        total_fields = len([f for f in dir(data) if not f.startswith('_')])
        filled_fields = len([f for f in dir(data) if not f.startswith('_') and getattr(data, f) is not None])
        validation_results['completeness_score'] = filled_fields / total_fields if total_fields > 0 else 0
        
        # Calculate overall quality score
        error_penalty = len(validation_results['errors']) * 0.2
        warning_penalty = len(validation_results['warnings']) * 0.1
        validation_results['quality_score'] = max(0, validation_results['completeness_score'] - error_penalty - warning_penalty)
        
        return validation_results

# Factory function
def create_normalizer() -> DataNormalizer:
    """Create a configured data normalizer"""
    return DataNormalizer()

# Example usage
if __name__ == "__main__":
    normalizer = create_normalizer()
    validator = DataQualityValidator()
    
    # Example CoinGecko data
    coingecko_data = {
        'symbol': 'btc',
        'name': 'Bitcoin',
        'market_cap_rank': 1,
        'market_data': {
            'current_price': {'usd': 50000},
            'price_change_percentage_24h_in_currency': {'usd': 2.5},
            'total_volume': {'usd': 25000000000},
            'market_cap': {'usd': 1000000000000},
            'circulating_supply': 19000000,
            'max_supply': 21000000,
            'ath': {'usd': 69000},
            'atl': {'usd': 0.05}
        },
        'community_data': {
            'twitter_followers': 5000000,
            'reddit_subscribers': 4000000
        },
        'last_updated': '2025-08-02T10:30:00.000Z'
    }
    
    # Normalize the data
    normalized = normalizer.normalize_provider_data('coingecko', coingecko_data)
    print(f"Normalized BTC data: {normalized.symbol} - ${normalized.price_usd}")
    
    # Validate the data
    validation = validator.validate_data(normalized)
    print(f"Data quality score: {validation['quality_score']:.2f}")
    print(f"Completeness: {validation['completeness_score']:.2f}")
    
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")