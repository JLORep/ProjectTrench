#!/usr/bin/env python3
"""
UNICORN HUNTER STRATEGY
Identifies coins with potential for 1000%+ gains using top performer message analysis
"""
import asyncio
import sqlite3
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from loguru import logger
import pandas as pd
import numpy as np

from src.data.comprehensive_enricher import ComprehensiveTokenData

@dataclass
class TopPerformerMessage:
    """Structure for top performer Telegram messages"""
    message_id: int
    timestamp: datetime
    raw_message: str
    coin_symbol: str
    contract_address: str
    initial_price: float
    peak_price: float
    max_gain_percent: float
    time_to_peak_hours: float
    volume_at_discovery: float
    market_cap_at_discovery: float
    
    # Extracted features
    urgency_indicators: List[str] = field(default_factory=list)
    social_proof_signals: List[str] = field(default_factory=list)
    technical_signals: List[str] = field(default_factory=list)
    risk_warnings: List[str] = field(default_factory=list)
    
    # Performance validation
    verified_gain: bool = False
    actual_peak_reached: bool = False

@dataclass
class UnicornSignal:
    """Signal for potential unicorn (1000%+ gainer)"""
    token: ComprehensiveTokenData
    unicorn_score: float
    confidence_level: str
    predicted_gain_range: Tuple[float, float]  # Min, Max expected gain
    time_horizon_hours: int
    aggressive_position_size: float
    reasoning: List[str]
    similar_historical_patterns: List[str]

class UnicornHunter:
    """
    Advanced strategy to identify potential 1000%+ gainers
    Based on analysis of historical top performers
    """
    
    def __init__(self):
        self.top_performers_db = "data/top_performers.db"
        self.unicorn_patterns = {}
        self.volume_surge_indicators = {}
        self.social_momentum_signals = {}
        self.init_database()
    
    def init_database(self):
        """Initialize database for top performer messages"""
        with sqlite3.connect(self.top_performers_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS top_performers (
                message_id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP,
                raw_message TEXT,
                coin_symbol TEXT,
                contract_address TEXT,
                initial_price REAL,
                peak_price REAL,
                max_gain_percent REAL,
                time_to_peak_hours REAL,
                volume_at_discovery REAL,
                market_cap_at_discovery REAL,
                urgency_indicators TEXT,
                social_proof_signals TEXT,
                technical_signals TEXT,
                risk_warnings TEXT,
                verified_gain BOOLEAN,
                actual_peak_reached BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS unicorn_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT,
                pattern_data TEXT,
                success_rate REAL,
                avg_gain_percent REAL,
                samples_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()
    
    def import_top_performer_messages(self, messages: List[Dict[str, Any]]):
        """Import and analyze top performer messages from Telegram"""
        logger.info(f"🦄 Importing {len(messages)} top performer messages")
        
        processed_messages = []
        
        for msg_data in messages:
            try:
                processed_msg = self.process_top_performer_message(msg_data)
                if processed_msg:
                    processed_messages.append(processed_msg)
                    self.store_top_performer(processed_msg)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
        
        logger.info(f"✅ Processed {len(processed_messages)} top performer messages")
        
        # Analyze patterns
        self.analyze_unicorn_patterns()
        
        return processed_messages
    
    def process_top_performer_message(self, msg_data: Dict[str, Any]) -> Optional[TopPerformerMessage]:
        """Process individual top performer message"""
        
        raw_message = msg_data.get('text', '')
        if not raw_message:
            return None
        
        # Extract coin information
        coin_info = self.extract_coin_info(raw_message)
        if not coin_info:
            return None
        
        # Extract performance data
        performance_data = self.extract_performance_data(raw_message)
        
        # Extract signal features
        urgency_indicators = self.extract_urgency_indicators(raw_message)
        social_proof = self.extract_social_proof_signals(raw_message)
        technical_signals = self.extract_technical_signals(raw_message)
        risk_warnings = self.extract_risk_warnings(raw_message)
        
        top_performer = TopPerformerMessage(
            message_id=msg_data.get('id', 0),
            timestamp=datetime.fromisoformat(msg_data.get('date', datetime.now().isoformat())),
            raw_message=raw_message,
            coin_symbol=coin_info['symbol'],
            contract_address=coin_info['contract'],
            initial_price=performance_data.get('initial_price', 0),
            peak_price=performance_data.get('peak_price', 0),
            max_gain_percent=performance_data.get('max_gain', 0),
            time_to_peak_hours=performance_data.get('time_to_peak', 0),
            volume_at_discovery=performance_data.get('volume', 0),
            market_cap_at_discovery=performance_data.get('market_cap', 0),
            urgency_indicators=urgency_indicators,
            social_proof_signals=social_proof,
            technical_signals=technical_signals,
            risk_warnings=risk_warnings
        )
        
        return top_performer
    
    def extract_coin_info(self, message: str) -> Optional[Dict[str, str]]:
        """Extract coin symbol and contract from message"""
        
        # Look for coin symbols
        symbol_patterns = [
            r'\$([A-Z]{2,10})',  # $SYMBOL
            r'([A-Z]{2,10})\s+(?:is|was|up|gained)',  # SYMBOL is/was/up/gained
            r'(?:token|coin)\s+([A-Z]{2,10})',  # token SYMBOL
        ]
        
        symbol = None
        for pattern in symbol_patterns:
            match = re.search(pattern, message)
            if match:
                symbol = match.group(1)
                break
        
        # Look for contract addresses
        contract_patterns = [
            r'([A-Za-z0-9]{32,44})',  # Solana contract addresses
            r'(?:CA|Contract|Address)[:=\s]+([A-Za-z0-9]{32,44})',
        ]
        
        contract = None
        for pattern in contract_patterns:
            match = re.search(pattern, message)
            if match:
                potential_contract = match.group(1)
                if len(potential_contract) >= 32:  # Valid length
                    contract = potential_contract
                    break
        
        if symbol or contract:
            return {'symbol': symbol or 'UNKNOWN', 'contract': contract or ''}
        
        return None
    
    def extract_performance_data(self, message: str) -> Dict[str, float]:
        """Extract performance metrics from message"""
        
        performance = {}
        
        # Look for percentage gains
        gain_patterns = [
            r'(\d+(?:,\d{3})*\.?\d*)%\s*(?:up|gain|increase)',
            r'(?:up|gained|increased)\s+(\d+(?:,\d{3})*\.?\d*)%',
            r'(\d+(?:,\d{3})*\.?\d*)x\s*(?:gain|return)',
            r'(\d+(?:,\d{3})*\.?\d*)00%',  # e.g., 1000%, 2000%
        ]
        
        max_gain = 0
        for pattern in gain_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                try:
                    gain = float(match.replace(',', ''))
                    max_gain = max(max_gain, gain)
                except ValueError:
                    continue
        
        performance['max_gain'] = max_gain
        
        # Look for prices
        price_patterns = [
            r'\$(\d+\.?\d*(?:e-?\d+)?)',  # $0.0001, $1.5e-6
            r'(\d+\.?\d*(?:e-?\d+)?)\s*(?:USD|usd)',
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    prices.append(price)
                except ValueError:
                    continue
        
        if prices:
            performance['initial_price'] = min(prices)
            performance['peak_price'] = max(prices)
        
        # Look for volume data
        volume_patterns = [
            r'volume[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*([KMB]?)',
            r'\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*([KMB]?)\s+volume',
        ]
        
        for pattern in volume_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    volume = float(match.group(1).replace(',', ''))
                    unit = match.group(2).upper()
                    
                    multiplier = {'K': 1000, 'M': 1000000, 'B': 1000000000}.get(unit, 1)
                    performance['volume'] = volume * multiplier
                    break
                except ValueError:
                    continue
        
        # Look for market cap
        mcap_patterns = [
            r'(?:market cap|mcap|mc)[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*([KMB]?)',
            r'\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*([KMB]?)\s+(?:market cap|mcap|mc)',
        ]
        
        for pattern in mcap_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    mcap = float(match.group(1).replace(',', ''))
                    unit = match.group(2).upper()
                    
                    multiplier = {'K': 1000, 'M': 1000000, 'B': 1000000000}.get(unit, 1)
                    performance['market_cap'] = mcap * multiplier
                    break
                except ValueError:
                    continue
        
        return performance
    
    def extract_urgency_indicators(self, message: str) -> List[str]:
        """Extract urgency indicators from message"""
        
        urgency_signals = []
        
        urgency_patterns = {
            'immediate_action': [r'NOW', r'URGENT', r'ASAP', r'IMMEDIATELY', r'QUICK'],
            'time_pressure': [r'limited time', r'while you can', r'before it\'s too late', r'don\'t miss'],
            'scarcity': [r'only \d+ left', r'limited supply', r'running out'],
            'fomo': [r'FOMO', r'fear of missing out', r'last chance', r'final call'],
            'exclamation': [r'!!!', r'🚀🚀🚀', r'⚡⚡⚡'],
            'superlatives': [r'BEST', r'ULTIMATE', r'MASSIVE', r'HUGE', r'INSANE']
        }
        
        for category, patterns in urgency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    urgency_signals.append(category)
                    break
        
        return urgency_signals
    
    def extract_social_proof_signals(self, message: str) -> List[str]:
        """Extract social proof indicators"""
        
        social_signals = []
        
        social_patterns = {
            'community_size': [r'\d+k?\s+(?:members|holders|followers)', r'growing community'],
            'endorsements': [r'verified', r'audited', r'endorsed', r'recommended'],
            'media_mentions': [r'featured', r'mentioned', r'covered', r'interviewed'],
            'partnerships': [r'partnership', r'collaboration', r'team up', r'working with'],
            'achievements': [r'milestone', r'achievement', r'record', r'breakthrough'],
            'exclusivity': [r'exclusive', r'private', r'VIP', r'early access']
        }
        
        for category, patterns in social_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    social_signals.append(category)
                    break
        
        return social_signals
    
    def extract_technical_signals(self, message: str) -> List[str]:
        """Extract technical analysis signals"""
        
        technical_signals = []
        
        technical_patterns = {
            'breakout': [r'breakout', r'breaking out', r'broke resistance'],
            'volume_surge': [r'volume surge', r'volume spike', r'unusual volume'],
            'momentum': [r'momentum', r'strong move', r'accelerating'],
            'support_resistance': [r'support', r'resistance', r'key level'],
            'indicators': [r'RSI', r'MACD', r'moving average', r'oversold', r'overbought'],
            'patterns': [r'pattern', r'formation', r'setup', r'signal']
        }
        
        for category, patterns in technical_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    technical_signals.append(category)
                    break
        
        return technical_signals
    
    def extract_risk_warnings(self, message: str) -> List[str]:
        """Extract risk warning indicators"""
        
        risk_signals = []
        
        risk_patterns = {
            'high_risk': [r'high risk', r'risky', r'dangerous', r'volatile'],
            'dyor': [r'DYOR', r'do your own research', r'not financial advice'],
            'caution': [r'caution', r'careful', r'beware', r'warning'],
            'speculation': [r'speculative', r'gamble', r'bet', r'risky play'],
            'loss_potential': [r'could lose', r'might lose', r'total loss', r'100% loss']
        }
        
        for category, patterns in risk_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    risk_signals.append(category)
                    break
        
        return risk_signals
    
    def store_top_performer(self, top_performer: TopPerformerMessage):
        """Store top performer in database"""
        
        with sqlite3.connect(self.top_performers_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT OR REPLACE INTO top_performers VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                top_performer.message_id,
                top_performer.timestamp,
                top_performer.raw_message,
                top_performer.coin_symbol,
                top_performer.contract_address,
                top_performer.initial_price,
                top_performer.peak_price,
                top_performer.max_gain_percent,
                top_performer.time_to_peak_hours,
                top_performer.volume_at_discovery,
                top_performer.market_cap_at_discovery,
                json.dumps(top_performer.urgency_indicators),
                json.dumps(top_performer.social_proof_signals),
                json.dumps(top_performer.technical_signals),
                json.dumps(top_performer.risk_warnings),
                top_performer.verified_gain,
                top_performer.actual_peak_reached
            ))
            
            conn.commit()
    
    def analyze_unicorn_patterns(self):
        """Analyze patterns from historical top performers"""
        
        with sqlite3.connect(self.top_performers_db) as conn:
            df = pd.read_sql_query("""
                SELECT * FROM top_performers 
                WHERE max_gain_percent >= 1000
                ORDER BY max_gain_percent DESC
            """, conn)
        
        if df.empty:
            logger.warning("No unicorn patterns found (1000%+ gainers)")
            return
        
        logger.info(f"🦄 Analyzing {len(df)} unicorn patterns")
        
        # Analyze common characteristics
        patterns = {}
        
        # Volume surge pattern
        volume_surges = df[df['volume_at_discovery'] > 0]
        if not volume_surges.empty:
            patterns['volume_surge'] = {
                'avg_volume': volume_surges['volume_at_discovery'].mean(),
                'min_volume': volume_surges['volume_at_discovery'].min(),
                'success_rate': len(volume_surges) / len(df)
            }
        
        # Market cap sweet spot
        mcap_data = df[df['market_cap_at_discovery'] > 0]
        if not mcap_data.empty:
            patterns['market_cap_range'] = {
                'avg_mcap': mcap_data['market_cap_at_discovery'].mean(),
                'median_mcap': mcap_data['market_cap_at_discovery'].median(),
                'optimal_range': (
                    mcap_data['market_cap_at_discovery'].quantile(0.25),
                    mcap_data['market_cap_at_discovery'].quantile(0.75)
                )
            }
        
        # Time to peak analysis
        time_data = df[df['time_to_peak_hours'] > 0]
        if not time_data.empty:
            patterns['time_to_peak'] = {
                'avg_hours': time_data['time_to_peak_hours'].mean(),
                'median_hours': time_data['time_to_peak_hours'].median(),
                'optimal_window': (
                    time_data['time_to_peak_hours'].quantile(0.1),
                    time_data['time_to_peak_hours'].quantile(0.9)
                )
            }
        
        # Signal frequency analysis
        all_urgency = []
        all_social = []
        all_technical = []
        
        for _, row in df.iterrows():
            try:
                urgency = json.loads(row['urgency_indicators']) if row['urgency_indicators'] else []
                social = json.loads(row['social_proof_signals']) if row['social_proof_signals'] else []
                technical = json.loads(row['technical_signals']) if row['technical_signals'] else []
                
                all_urgency.extend(urgency)
                all_social.extend(social)
                all_technical.extend(technical)
            except:
                continue
        
        patterns['signal_frequency'] = {
            'urgency_signals': pd.Series(all_urgency).value_counts().to_dict(),
            'social_signals': pd.Series(all_social).value_counts().to_dict(),
            'technical_signals': pd.Series(all_technical).value_counts().to_dict()
        }
        
        self.unicorn_patterns = patterns
        
        # Store patterns in database
        with sqlite3.connect(self.top_performers_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT OR REPLACE INTO unicorn_patterns 
            (pattern_name, pattern_data, success_rate, avg_gain_percent, samples_count)
            VALUES (?, ?, ?, ?, ?)
            """, (
                'unicorn_patterns_v1',
                json.dumps(patterns),
                1.0,  # These are all confirmed unicorns
                df['max_gain_percent'].mean(),
                len(df)
            ))
            
            conn.commit()
        
        logger.info("✅ Unicorn patterns analyzed and stored")
    
    def unicorn_hunter_strategy(self, tokens: List[ComprehensiveTokenData]) -> List[UnicornSignal]:
        """
        Main unicorn hunting strategy
        Identifies potential 1000%+ gainers using learned patterns
        """
        logger.info(f"🦄 Hunting unicorns among {len(tokens)} tokens")
        
        unicorn_signals = []
        
        for token in tokens:
            unicorn_score = self.calculate_unicorn_score(token)
            
            if unicorn_score >= 0.7:  # High threshold for unicorn potential
                signal = self.create_unicorn_signal(token, unicorn_score)
                unicorn_signals.append(signal)
        
        # Sort by score and return top candidates
        unicorn_signals.sort(key=lambda x: x.unicorn_score, reverse=True)
        
        logger.info(f"🦄 Found {len(unicorn_signals)} potential unicorns")
        
        return unicorn_signals[:10]  # Top 10 unicorn candidates
    
    def calculate_unicorn_score(self, token: ComprehensiveTokenData) -> float:
        """Calculate unicorn potential score"""
        
        score = 0
        reasoning = []
        
        # Volume surge indicator (30% weight)
        volume_score = self.calculate_volume_surge_score(token)
        score += volume_score * 0.3
        if volume_score > 0.7:
            reasoning.append(f"Massive volume surge: {volume_score:.2f}")
        
        # Market cap sweet spot (20% weight)
        mcap_score = self.calculate_mcap_score(token)
        score += mcap_score * 0.2
        if mcap_score > 0.6:
            reasoning.append(f"Optimal market cap range: {mcap_score:.2f}")
        
        # Momentum explosion (25% weight)
        momentum_score = self.calculate_momentum_score(token)
        score += momentum_score * 0.25
        if momentum_score > 0.8:
            reasoning.append(f"Explosive momentum: {momentum_score:.2f}")
        
        # Social/community indicators (15% weight)
        social_score = self.calculate_social_score(token)
        score += social_score * 0.15
        if social_score > 0.5:
            reasoning.append(f"Strong social signals: {social_score:.2f}")
        
        # Risk/reward ratio (10% weight)
        risk_score = self.calculate_risk_reward_score(token)
        score += risk_score * 0.1
        if risk_score > 0.6:
            reasoning.append(f"Favorable risk/reward: {risk_score:.2f}")
        
        return min(score, 1.0)
    
    def calculate_volume_surge_score(self, token: ComprehensiveTokenData) -> float:
        """Calculate volume surge score based on unicorn patterns"""
        
        if not self.unicorn_patterns or token.volume_24h == 0:
            return 0
        
        # Compare to historical unicorn volumes
        volume_patterns = self.unicorn_patterns.get('volume_surge')
        if not volume_patterns:
            # Fallback logic
            if token.volume_24h > token.market_cap * 5:  # 5x market cap in volume
                return 1.0
            elif token.volume_24h > token.market_cap * 2:  # 2x market cap
                return 0.7
            elif token.volume_24h > token.market_cap * 0.5:  # 50% of market cap
                return 0.4
            return 0
        
        # Use learned patterns
        avg_unicorn_volume = volume_patterns['avg_volume']
        min_unicorn_volume = volume_patterns['min_volume']
        
        if token.volume_24h >= avg_unicorn_volume:
            return 1.0
        elif token.volume_24h >= min_unicorn_volume:
            return 0.8
        elif token.volume_24h >= min_unicorn_volume * 0.5:
            return 0.5
        else:
            return 0.2
    
    def calculate_mcap_score(self, token: ComprehensiveTokenData) -> float:
        """Calculate market cap score for unicorn potential"""
        
        if token.market_cap == 0:
            return 0
        
        # Unicorns typically come from smaller market caps
        if self.unicorn_patterns and 'market_cap_range' in self.unicorn_patterns:
            optimal_range = self.unicorn_patterns['market_cap_range']['optimal_range']
            min_mcap, max_mcap = optimal_range
            
            if min_mcap <= token.market_cap <= max_mcap:
                return 1.0
            elif token.market_cap < min_mcap:
                # Too small, might be too risky
                return max(0.3, min_mcap / token.market_cap * 0.6)
            else:
                # Too large, less unicorn potential
                return max(0.1, max_mcap / token.market_cap)
        
        # Fallback: optimal range for memecoins
        if 10000 <= token.market_cap <= 1000000:  # $10K - $1M sweet spot
            return 1.0
        elif 1000 <= token.market_cap <= 10000000:  # $1K - $10M acceptable
            return 0.6
        else:
            return 0.2
    
    def calculate_momentum_score(self, token: ComprehensiveTokenData) -> float:
        """Calculate momentum score for explosive growth potential"""
        
        score = 0
        
        # Short-term momentum (5m and 1h)
        if token.price_change_5m > 50:  # 50%+ in 5 minutes
            score += 0.4
        elif token.price_change_5m > 25:
            score += 0.25
        elif token.price_change_5m > 10:
            score += 0.1
        
        if token.price_change_1h > 100:  # 100%+ in 1 hour
            score += 0.4
        elif token.price_change_1h > 50:
            score += 0.25
        elif token.price_change_1h > 20:
            score += 0.1
        
        # Acceleration (5m momentum > 1h momentum indicates acceleration)
        if token.price_change_5m > 0 and token.price_change_1h > 0:
            if token.price_change_5m / 5 > token.price_change_1h / 60:  # Per minute comparison
                score += 0.2
        
        return min(score, 1.0)
    
    def calculate_social_score(self, token: ComprehensiveTokenData) -> float:
        """Calculate social momentum score"""
        
        score = 0
        
        # Twitter presence
        if token.twitter_followers > 10000:
            score += 0.3
        elif token.twitter_followers > 1000:
            score += 0.2
        elif token.twitter_followers > 100:
            score += 0.1
        
        # Telegram community
        if token.telegram_members > 5000:
            score += 0.3
        elif token.telegram_members > 1000:
            score += 0.2
        elif token.telegram_members > 100:
            score += 0.1
        
        # Website and legitimacy
        if token.website_url:
            score += 0.1
        
        # Holder growth (more holders = growing interest)
        if token.holder_count > 1000:
            score += 0.3
        elif token.holder_count > 500:
            score += 0.2
        elif token.holder_count > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def calculate_risk_reward_score(self, token: ComprehensiveTokenData) -> float:
        """Calculate risk/reward score"""
        
        score = 1.0  # Start with perfect score
        
        # Penalize high risk factors
        if token.rug_risk_score > 0.7:
            score -= 0.4
        elif token.rug_risk_score > 0.5:
            score -= 0.2
        elif token.rug_risk_score > 0.3:
            score -= 0.1
        
        if token.honeypot_risk > 0.5:
            score -= 0.3
        elif token.honeypot_risk > 0.2:
            score -= 0.1
        
        # Reward safety features
        if token.mint_disabled and token.freeze_disabled:
            score += 0.2
        elif token.mint_disabled or token.freeze_disabled:
            score += 0.1
        
        # Liquidity safety
        if token.liquidity_locked:
            score += 0.1
        
        return max(0, min(score, 1.0))
    
    def create_unicorn_signal(self, token: ComprehensiveTokenData, score: float) -> UnicornSignal:
        """Create unicorn signal with aggressive parameters"""
        
        # Determine confidence level
        if score >= 0.9:
            confidence = "EXTREMELY_HIGH"
            predicted_range = (500, 5000)  # 500% - 5000%
            position_size = 0.15  # 15% of portfolio (very aggressive)
            time_horizon = 6
        elif score >= 0.8:
            confidence = "HIGH"
            predicted_range = (200, 2000)  # 200% - 2000%
            position_size = 0.10  # 10% of portfolio
            time_horizon = 8
        elif score >= 0.7:
            confidence = "MODERATE_HIGH"
            predicted_range = (100, 1000)  # 100% - 1000%
            position_size = 0.08  # 8% of portfolio
            time_horizon = 12
        else:
            confidence = "MODERATE"
            predicted_range = (50, 500)   # 50% - 500%
            position_size = 0.05  # 5% of portfolio
            time_horizon = 24
        
        # Generate reasoning
        reasoning = [
            f"Unicorn score: {score:.2f}",
            f"Volume surge potential detected",
            f"Market cap in optimal range: ${token.market_cap:,.0f}",
            f"Strong momentum indicators",
            f"Predicted gain range: {predicted_range[0]}% - {predicted_range[1]}%"
        ]
        
        # Find similar historical patterns
        similar_patterns = self.find_similar_patterns(token)
        
        return UnicornSignal(
            token=token,
            unicorn_score=score,
            confidence_level=confidence,
            predicted_gain_range=predicted_range,
            time_horizon_hours=time_horizon,
            aggressive_position_size=position_size,
            reasoning=reasoning,
            similar_historical_patterns=similar_patterns
        )
    
    def find_similar_patterns(self, token: ComprehensiveTokenData) -> List[str]:
        """Find similar historical patterns"""
        
        patterns = []
        
        # This would query historical data for similar tokens
        # For now, return pattern descriptions
        
        if token.volume_24h > token.market_cap * 3:
            patterns.append("Similar to BONK Nov 2023 (3000% gain)")
        
        if token.price_change_5m > 30 and token.market_cap < 500000:
            patterns.append("Similar to PEPE May 2023 pattern (5000% gain)")
        
        if (token.holder_count > 500 and 
            token.twitter_followers > 1000 and 
            token.market_cap < 1000000):
            patterns.append("Similar to WIF early pattern (2000% gain)")
        
        return patterns

# Sample data for testing
def create_sample_top_performer_messages() -> List[Dict[str, Any]]:
    """Create sample top performer messages for testing"""
    
    sample_messages = [
        {
            'id': 1,
            'date': '2024-01-15T10:30:00',
            'text': '🚀🚀🚀 $BONK is EXPLODING!!! UP 2000% in 6 hours! Volume surge to $50M! Market cap only $500K! Contract: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 URGENT - before it hits $100M mcap! 🦄'
        },
        {
            'id': 2,
            'date': '2024-01-20T14:15:00',
            'text': 'PEPE 🐸 just did 5000% overnight! Started at $0.00000001, now $0.0000005! Massive volume spike detected! 100K+ holders in 24h! CA: 6GCwLaAcEqKZZa3dMnXZWwFoE7VG6JRaGRh5MQtxbhxU Don\'t miss this moonshot! ⚡⚡⚡'
        },
        {
            'id': 3,
            'date': '2024-02-05T09:45:00',
            'text': '🦄 UNICORN ALERT! WIF showing 3000% gains! Volume exploded from $10K to $75M in 4 hours! Market cap: $2M → $60M! Contract: EKpQGSJtjMFqKZ9ag7eaHF1HKu2qcjgqrtgdgLLPGGZQ FOMO kicking in! Limited time before major exchanges list!'
        },
        {
            'id': 4,
            'date': '2024-02-12T16:20:00',
            'text': 'MASSIVE BREAKOUT! $MYRO up 4500% in 8 hours! Community growing 1000+ members per hour! Twitter exploding! Volume: $125M! Started at $50K mcap, now $2.25M! CA: HhJpBhRRn4g56VsyLuT8DL5Bv31HkXqsrahTTUCZeZg4 🚀 This is the next 100x!'
        },
        {
            'id': 5,
            'date': '2024-02-18T11:10:00',
            'text': '⚡ VOLUME EXPLOSION ⚡ $POPCAT doing 1800% gains! Unusual volume detected: $200M in 6 hours! Whale accumulation confirmed! Market cap still under $5M! Contract: 7GCwLaAcEqKZZa3dMnXZWwFoE7VG6JRaGRh5MQtxbhxU Get in before the next leg up!'
        }
    ]
    
    return sample_messages

# Test the unicorn hunter
async def test_unicorn_hunter():
    """Test the unicorn hunter strategy"""
    
    hunter = UnicornHunter()
    
    # Import sample messages
    sample_messages = create_sample_top_performer_messages()
    hunter.import_top_performer_messages(sample_messages)
    
    # Create sample tokens for testing
    sample_tokens = []
    for i in range(20):
        token = ComprehensiveTokenData(
            contract_address=f"unicorn_test_{i}",
            symbol=f"UNI{i}",
            name=f"Unicorn Token {i}",
            price_usd=np.random.uniform(0.0001, 0.01),
            price_change_5m=np.random.normal(20, 40),  # Higher momentum for testing
            price_change_1h=np.random.normal(50, 80),
            price_change_24h=np.random.normal(100, 200),
            volume_24h=np.random.uniform(100000, 10000000),
            market_cap=np.random.uniform(10000, 2000000),  # Smaller caps for unicorn potential
            liquidity_usd=np.random.uniform(5000, 500000),
            holder_count=np.random.randint(100, 2000),
            twitter_followers=np.random.randint(100, 10000),
            telegram_members=np.random.randint(50, 5000),
            website_url="https://unicorn.example.com",
            rug_risk_score=np.random.uniform(0, 0.5),  # Lower risk
            honeypot_risk=np.random.uniform(0, 0.3),
            mint_disabled=True,
            freeze_disabled=True
        )
        sample_tokens.append(token)
    
    # Run unicorn hunter strategy
    unicorn_signals = hunter.unicorn_hunter_strategy(sample_tokens)
    
    print(f"\n🦄 UNICORN HUNTER RESULTS:")
    print(f"Analyzed {len(sample_tokens)} tokens")
    print(f"Found {len(unicorn_signals)} potential unicorns")
    
    for i, signal in enumerate(unicorn_signals, 1):
        print(f"\n#{i} {signal.token.symbol} (Score: {signal.unicorn_score:.3f})")
        print(f"   Confidence: {signal.confidence_level}")
        print(f"   Predicted Range: {signal.predicted_gain_range[0]}% - {signal.predicted_gain_range[1]}%")
        print(f"   Position Size: {signal.aggressive_position_size:.1%}")
        print(f"   Time Horizon: {signal.time_horizon_hours} hours")
        print(f"   Similar Patterns: {', '.join(signal.similar_historical_patterns)}")

if __name__ == "__main__":
    asyncio.run(test_unicorn_hunter())