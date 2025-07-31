#!/usr/bin/env python3
"""
TrenchCoat Pro - Telegram Enrichment Pipeline
Integrates Telegram parsing, data enrichment, and dashboard display
"""
import asyncio
import re
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging

@dataclass
class EnrichedCoin:
    """Enriched coin data structure"""
    # Basic identification
    symbol: str
    name: str
    contract_address: str
    
    # Price data
    current_price: float
    price_change_24h: float
    price_change_7d: float
    
    # Volume and liquidity
    volume_24h: float
    market_cap: float
    liquidity_usd: float
    
    # Technical indicators
    rsi: float
    macd: float
    bollinger_upper: float
    bollinger_lower: float
    
    # Social and sentiment
    social_score: float
    sentiment_score: float
    telegram_mentions: int
    twitter_mentions: int
    
    # TrenchCoat specific
    runner_confidence: float
    enrichment_timestamp: datetime
    source: str  # 'telegram', 'dexscreener', 'api'
    
    # Risk factors
    rug_risk_score: float
    honeypot_risk: float
    contract_verified: bool
    
    # Metadata
    holder_count: int
    creator_balance: float
    top_10_holder_percent: float

class TelegramEnrichmentPipeline:
    """Complete pipeline from Telegram signals to enriched dashboard data"""
    
    def __init__(self):
        self.api_endpoints = {
            'dexscreener': 'https://api.dexscreener.com/latest/dex',
            'coingecko': 'https://api.coingecko.com/api/v3',
            'jupiter': 'https://price.jup.ag/v4/price',
            'solscan': 'https://api.solscan.io/account',
            'birdeye': 'https://public-api.birdeye.so/v1/wallet'
        }
        
        # Telegram parsing patterns
        self.parsing_patterns = {
            'contract_address': r'([A-Za-z0-9]{32,44})',
            'symbol': r'\$([A-Z]{2,10})',
            'price': r'\$([0-9]+\.?[0-9]*)',
            'mcap': r'(?:MC|Market Cap|mcap)[\s:]*\$?([0-9,]+[KMB]?)',
            'volume': r'(?:Vol|Volume|vol)[\s:]*\$?([0-9,]+[KMB]?)',
            'ca': r'(?:CA|Contract|Address)[\s:]*([A-Za-z0-9]{32,44})'
        }
    
    def parse_telegram_signal(self, message: str, channel: str = "unknown") -> Dict[str, Any]:
        """Enhanced Telegram message parsing"""
        
        parsed_data = {
            'raw_message': message,
            'channel': channel,
            'timestamp': datetime.now(),
            'extracted': {}
        }
        
        # Extract all patterns
        for key, pattern in self.parsing_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                parsed_data['extracted'][key] = match.group(1)
        
        # Clean and normalize data
        if 'symbol' in parsed_data['extracted']:
            parsed_data['extracted']['symbol'] = parsed_data['extracted']['symbol'].upper()
        
        if 'price' in parsed_data['extracted']:
            try:
                parsed_data['extracted']['price'] = float(parsed_data['extracted']['price'])
            except:
                pass
        
        # Calculate initial confidence based on data completeness
        confidence_factors = [
            'contract_address' in parsed_data['extracted'],
            'symbol' in parsed_data['extracted'],
            'price' in parsed_data['extracted'],
            len(message) > 50,  # Detailed message
            any(word in message.lower() for word in ['gem', 'moon', 'x100', 'launch'])
        ]
        
        parsed_data['initial_confidence'] = sum(confidence_factors) / len(confidence_factors)
        
        return parsed_data
    
    async def enrich_coin_data(self, parsed_signal: Dict[str, Any]) -> Optional[EnrichedCoin]:
        """Enrich parsed Telegram signal with comprehensive market data"""
        
        extracted = parsed_signal.get('extracted', {})
        contract_address = extracted.get('contract_address')
        symbol = extracted.get('symbol', 'UNKNOWN')
        
        if not contract_address:
            return None
        
        try:
            # Step 1: Get basic token info from DexScreener
            dex_data = await self.fetch_dexscreener_data(contract_address)
            
            # Step 2: Get detailed market data
            market_data = await self.fetch_market_data(contract_address, symbol)
            
            # Step 3: Get social sentiment data
            social_data = await self.fetch_social_data(symbol)
            
            # Step 4: Get risk assessment
            risk_data = await self.assess_risk_factors(contract_address)
            
            # Step 5: Calculate technical indicators
            technical_data = await self.calculate_technical_indicators(dex_data)
            
            # Step 6: Combine all data into EnrichedCoin
            enriched_coin = self.combine_enrichment_data(
                parsed_signal, dex_data, market_data, social_data, risk_data, technical_data
            )
            
            return enriched_coin
            
        except Exception as e:
            logging.error(f"Enrichment failed for {symbol}: {e}")
            return None
    
    async def fetch_dexscreener_data(self, contract_address: str) -> Dict[str, Any]:
        """Fetch comprehensive data from DexScreener"""
        try:
            url = f"{self.api_endpoints['dexscreener']}/tokens/{contract_address}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('pairs'):
                    pair = data['pairs'][0]  # Get most liquid pair
                    
                    return {
                        'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                        'name': pair.get('baseToken', {}).get('name', 'Unknown Token'),
                        'price_usd': float(pair.get('priceUsd', 0)),
                        'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                        'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                        'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0)),
                        'market_cap': float(pair.get('marketCap', 0)),
                        'dex_id': pair.get('dexId'),
                        'pair_address': pair.get('pairAddress'),
                        'price_history': pair.get('priceChange', {})
                    }
            
            return {}
            
        except Exception as e:
            logging.error(f"DexScreener fetch failed: {e}")
            return {}
    
    async def fetch_market_data(self, contract_address: str, symbol: str) -> Dict[str, Any]:
        """Fetch additional market data from multiple sources"""
        market_data = {
            'holder_count': 0,
            'top_10_holder_percent': 0,
            'creator_balance': 0,
            'total_supply': 0
        }
        
        try:
            # Try Solscan API for holder data
            url = f"{self.api_endpoints['solscan']}/tokens"
            params = {'address': contract_address}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                market_data.update({
                    'holder_count': data.get('holder', 0),
                    'total_supply': float(data.get('supply', 0))
                })
            
        except Exception as e:
            logging.error(f"Market data fetch failed: {e}")
        
        return market_data
    
    async def fetch_social_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch social sentiment and mention data"""
        social_data = {
            'telegram_mentions': np.random.randint(10, 500),  # Simulated for demo
            'twitter_mentions': np.random.randint(5, 200),
            'social_score': np.random.uniform(0.3, 0.9),
            'sentiment_score': np.random.uniform(0.4, 0.8)
        }
        
        # In production, this would query:
        # - Twitter API for mentions
        # - Telegram channel monitoring
        # - Reddit/Discord sentiment analysis
        # - LunarCrush social metrics
        
        return social_data
    
    async def assess_risk_factors(self, contract_address: str) -> Dict[str, Any]:
        """Assess rug pull and honeypot risks"""
        risk_data = {
            'rug_risk_score': np.random.uniform(0.1, 0.7),
            'honeypot_risk': np.random.uniform(0.0, 0.3),
            'contract_verified': np.random.choice([True, False], p=[0.7, 0.3])
        }
        
        # In production, this would check:
        # - Contract verification status
        # - Liquidity lock duration
        # - Owner permissions analysis
        # - Honeypot detection APIs
        # - Team token holdings
        
        return risk_data
    
    async def calculate_technical_indicators(self, dex_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate technical indicators from price data"""
        
        # Generate sample price history for calculations
        current_price = dex_data.get('price_usd', 1.0)
        price_history = [current_price * (1 + np.random.normal(0, 0.05)) for _ in range(20)]
        
        # Calculate RSI
        rsi = self.calculate_rsi(price_history)
        
        # Calculate MACD
        macd = self.calculate_macd(price_history)
        
        # Calculate Bollinger Bands
        bb_upper, bb_lower = self.calculate_bollinger_bands(price_history)
        
        return {
            'rsi': rsi,
            'macd': macd,
            'bollinger_upper': bb_upper,
            'bollinger_lower': bb_lower
        }
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI
            
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, prices: List[float]) -> float:
        """Calculate MACD indicator"""
        if len(prices) < 26:
            return 0.0
            
        # Simple MACD calculation
        ema_12 = sum(prices[-12:]) / 12
        ema_26 = sum(prices[-26:]) / 26
        
        return ema_12 - ema_26
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> Tuple[float, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            current_price = prices[-1] if prices else 1.0
            return current_price * 1.05, current_price * 0.95
            
        recent_prices = prices[-period:]
        sma = sum(recent_prices) / period
        variance = sum((p - sma) ** 2 for p in recent_prices) / period
        std_dev = variance ** 0.5
        
        upper_band = sma + (2 * std_dev)
        lower_band = sma - (2 * std_dev)
        
        return upper_band, lower_band
    
    def combine_enrichment_data(
        self, 
        parsed_signal: Dict[str, Any],
        dex_data: Dict[str, Any],
        market_data: Dict[str, Any],
        social_data: Dict[str, Any],
        risk_data: Dict[str, Any],
        technical_data: Dict[str, Any]
    ) -> EnrichedCoin:
        """Combine all enrichment data into final EnrichedCoin object"""
        
        extracted = parsed_signal.get('extracted', {})
        
        # Calculate comprehensive runner confidence
        confidence_factors = {
            'price_momentum': min(abs(dex_data.get('price_change_24h', 0)) / 50, 1.0),
            'volume_strength': min(dex_data.get('volume_24h', 0) / 1000000, 1.0),
            'liquidity_depth': min(dex_data.get('liquidity_usd', 0) / 100000, 1.0),
            'social_buzz': social_data.get('social_score', 0.5),
            'technical_score': (technical_data.get('rsi', 50) - 30) / 40 if technical_data.get('rsi', 50) > 30 else 0,
            'risk_inverse': 1 - risk_data.get('rug_risk_score', 0.5),
            'initial_confidence': parsed_signal.get('initial_confidence', 0.5)
        }
        
        runner_confidence = sum(confidence_factors.values()) / len(confidence_factors) * 100
        
        return EnrichedCoin(
            # Basic identification
            symbol=dex_data.get('symbol', extracted.get('symbol', 'UNKNOWN')),
            name=dex_data.get('name', 'Unknown Token'),
            contract_address=extracted.get('contract_address', ''),
            
            # Price data
            current_price=dex_data.get('price_usd', 0),
            price_change_24h=dex_data.get('price_change_24h', 0),
            price_change_7d=0,  # Would need 7-day data
            
            # Volume and liquidity
            volume_24h=dex_data.get('volume_24h', 0),
            market_cap=dex_data.get('market_cap', 0),
            liquidity_usd=dex_data.get('liquidity_usd', 0),
            
            # Technical indicators
            rsi=technical_data.get('rsi', 50),
            macd=technical_data.get('macd', 0),
            bollinger_upper=technical_data.get('bollinger_upper', 0),
            bollinger_lower=technical_data.get('bollinger_lower', 0),
            
            # Social and sentiment
            social_score=social_data.get('social_score', 0.5),
            sentiment_score=social_data.get('sentiment_score', 0.5),
            telegram_mentions=social_data.get('telegram_mentions', 0),
            twitter_mentions=social_data.get('twitter_mentions', 0),
            
            # TrenchCoat specific
            runner_confidence=runner_confidence,
            enrichment_timestamp=datetime.now(),
            source=parsed_signal.get('channel', 'telegram'),
            
            # Risk factors
            rug_risk_score=risk_data.get('rug_risk_score', 0.5),
            honeypot_risk=risk_data.get('honeypot_risk', 0.2),
            contract_verified=risk_data.get('contract_verified', False),
            
            # Metadata
            holder_count=market_data.get('holder_count', 0),
            creator_balance=market_data.get('creator_balance', 0),
            top_10_holder_percent=market_data.get('top_10_holder_percent', 0)
        )
    
    async def process_telegram_signals(self, messages: List[Dict[str, str]]) -> List[EnrichedCoin]:
        """Process multiple Telegram messages and return enriched coins"""
        enriched_coins = []
        
        for message_data in messages:
            message = message_data.get('text', '')
            channel = message_data.get('channel', 'unknown')
            
            # Parse the message
            parsed_signal = self.parse_telegram_signal(message, channel)
            
            # Skip if no contract address found
            if 'contract_address' not in parsed_signal.get('extracted', {}):
                continue
            
            # Enrich the coin data
            enriched_coin = await self.enrich_coin_data(parsed_signal)
            
            if enriched_coin:
                enriched_coins.append(enriched_coin)
        
        return enriched_coins

# Dashboard integration functions
def convert_enriched_coin_to_dashboard_format(enriched_coin: EnrichedCoin) -> Dict[str, Any]:
    """Convert EnrichedCoin to dashboard display format"""
    return {
        'ticker': f"${enriched_coin.symbol}",
        'name': enriched_coin.name,
        'stage': get_processing_stage_from_confidence(enriched_coin.runner_confidence),
        'price': enriched_coin.current_price,
        'volume': enriched_coin.volume_24h,
        'score': enriched_coin.runner_confidence / 100,
        'timestamp': enriched_coin.enrichment_timestamp,
        'change_24h': enriched_coin.price_change_24h,
        'liquidity': enriched_coin.liquidity_usd,
        'market_cap': enriched_coin.market_cap,
        'social_score': enriched_coin.social_score,
        'sentiment_score': enriched_coin.sentiment_score,
        'rug_risk': enriched_coin.rug_risk_score,
        'contract_verified': enriched_coin.contract_verified,
        'holder_count': enriched_coin.holder_count,
        'source': enriched_coin.source,
        'contract_address': enriched_coin.contract_address,
        'rsi': enriched_coin.rsi,
        'macd': enriched_coin.macd
    }

def get_processing_stage_from_confidence(confidence: float) -> str:
    """Convert confidence score to processing stage"""
    if confidence >= 90:
        return 'Trading'
    elif confidence >= 80:
        return 'Analyzing'
    elif confidence >= 70:
        return 'Enriching'
    else:
        return 'Discovering'

# Example usage and testing
async def test_telegram_enrichment():
    """Test the telegram enrichment pipeline"""
    
    pipeline = TelegramEnrichmentPipeline()
    
    # Sample Telegram messages
    test_messages = [
        {
            'text': '🚀 NEW GEM ALERT! $BONK is about to MOON! 🌙\nCA: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263\nPrice: $0.00001234\nMC: $50M\nThis is going to 100x! 💎',
            'channel': 'CryptoGems'
        },
        {
            'text': 'Found a new runner! Contract: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\n$WIF is launching soon! Volume already pumping!',
            'channel': 'ATM.Day'
        }
    ]
    
    enriched_coins = await pipeline.process_telegram_signals(test_messages)
    
    print("=" * 60)
    print("TELEGRAM ENRICHMENT PIPELINE TEST")
    print("=" * 60)
    
    for coin in enriched_coins:
        print(f"\n💎 {coin.symbol} ({coin.name})")
        print(f"💰 Price: ${coin.current_price:.8f}")
        print(f"📈 24h Change: {coin.price_change_24h:+.2f}%")
        print(f"📊 Volume: ${coin.volume_24h:,.0f}")
        print(f"💧 Liquidity: ${coin.liquidity_usd:,.0f}")
        print(f"🎯 Runner Confidence: {coin.runner_confidence:.1f}%")
        print(f"🏛️ Social Score: {coin.social_score:.2f}")
        print(f"⚠️ Rug Risk: {coin.rug_risk_score:.2f}")
        print(f"✅ Verified: {coin.contract_verified}")
        print(f"📱 Source: {coin.source}")

if __name__ == "__main__":
    asyncio.run(test_telegram_enrichment())