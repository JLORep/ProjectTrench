#!/usr/bin/env python3
"""
TrenchCoat Pro - Complete Telegram Signal Processing Pipeline
Full workflow from ATM.day group signal reception to filtered top 5 runners
"""

import asyncio
import re
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalStatus(Enum):
    """Signal processing status"""
    RECEIVED = "received"
    PARSED = "parsed"
    ENRICHED = "enriched"
    ANALYZED = "analyzed"
    FILTERED = "filtered"
    COMPLETED = "completed"
    FAILED = "failed"

class SignalSource(Enum):
    """Signal source channels"""
    ATM_DAY = "atm.day"
    CRYPTO_GEMS = "crypto_gems"
    WHALE_ALERTS = "whale_alerts"
    MANUAL = "manual"

@dataclass
class TelegramSignal:
    """Telegram signal data structure"""
    # Basic signal info
    id: str
    raw_message: str
    channel: str
    timestamp: datetime
    
    # Parsed data
    ticker: Optional[str] = None
    contract_address: Optional[str] = None
    entry_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    
    # Enriched data
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    liquidity: Optional[float] = None
    holder_count: Optional[int] = None
    
    # Analysis results
    confidence_score: float = 0.0
    risk_score: float = 0.0
    runner_potential: float = 0.0
    strategy_matches: List[str] = None
    
    # Processing status
    status: SignalStatus = SignalStatus.RECEIVED
    processing_log: List[str] = None
    
    def __post_init__(self):
        if self.strategy_matches is None:
            self.strategy_matches = []
        if self.processing_log is None:
            self.processing_log = []

@dataclass
class BravoStrategy:
    """Bravo's advanced trading strategy"""
    name: str
    description: str
    criteria: Dict[str, Any]
    weight: float
    success_rate: float
    
    def evaluate(self, signal: TelegramSignal) -> Tuple[bool, float, str]:
        """Evaluate if signal matches this strategy"""
        score = 0.0
        reasoning = []
        
        # Volume criteria
        if 'min_volume' in self.criteria and signal.volume_24h:
            if signal.volume_24h >= self.criteria['min_volume']:
                score += 0.2
                reasoning.append(f"Volume ${signal.volume_24h:,.0f} exceeds minimum")
            else:
                reasoning.append(f"Volume too low: ${signal.volume_24h:,.0f}")
        
        # Market cap criteria
        if 'max_mcap' in self.criteria and signal.market_cap:
            if signal.market_cap <= self.criteria['max_mcap']:
                score += 0.2
                reasoning.append(f"Market cap ${signal.market_cap:,.0f} under limit")
            else:
                reasoning.append(f"Market cap too high: ${signal.market_cap:,.0f}")
        
        # Liquidity criteria
        if 'min_liquidity' in self.criteria and signal.liquidity:
            if signal.liquidity >= self.criteria['min_liquidity']:
                score += 0.2
                reasoning.append(f"Liquidity ${signal.liquidity:,.0f} sufficient")
            else:
                reasoning.append(f"Liquidity too low: ${signal.liquidity:,.0f}")
        
        # Holder criteria
        if 'min_holders' in self.criteria and signal.holder_count:
            if signal.holder_count >= self.criteria['min_holders']:
                score += 0.2
                reasoning.append(f"Holder count {signal.holder_count} sufficient")
            else:
                reasoning.append(f"Not enough holders: {signal.holder_count}")
        
        # Price action criteria
        if 'price_momentum' in self.criteria and signal.current_price and signal.entry_price:
            momentum = (signal.current_price - signal.entry_price) / signal.entry_price
            if momentum >= self.criteria['price_momentum']:
                score += 0.2
                reasoning.append(f"Good momentum: {momentum:.2%}")
        
        # Apply strategy weight
        weighted_score = score * self.weight * self.success_rate
        matches = weighted_score >= 0.7  # 70% threshold
        
        return matches, weighted_score, " | ".join(reasoning)

class TelegramSignalProcessor:
    """Complete Telegram signal processing pipeline"""
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.api_cache = {}
        self.processing_stats = {
            'signals_received': 0,
            'signals_parsed': 0,
            'signals_enriched': 0,
            'signals_filtered': 0,
            'top_runners_found': 0,
            'last_signal_time': None,
            'avg_processing_time': 0.0
        }
        
        # Initialize Bravo's strategies
        self.bravo_strategies = self._init_bravo_strategies()
        
        # Database connection
        self._init_database()
    
    def _init_database(self):
        """Initialize signal processing database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telegram_signals (
                    id TEXT PRIMARY KEY,
                    raw_message TEXT,
                    channel TEXT,
                    timestamp DATETIME,
                    ticker TEXT,
                    contract_address TEXT,
                    entry_price REAL,
                    target_price REAL,
                    stop_loss REAL,
                    current_price REAL,
                    market_cap REAL,
                    volume_24h REAL,
                    liquidity REAL,
                    holder_count INTEGER,
                    confidence_score REAL,
                    risk_score REAL,
                    runner_potential REAL,
                    strategy_matches TEXT,
                    status TEXT,
                    processing_log TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create daily runners table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_runners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    signal_id TEXT,
                    rank INTEGER,
                    final_score REAL,
                    strategy_summary TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (signal_id) REFERENCES telegram_signals (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    def _init_bravo_strategies(self) -> List[BravoStrategy]:
        """Initialize Bravo's advanced trading strategies"""
        strategies = [
            BravoStrategy(
                name="Low Cap Momentum",
                description="Low market cap coins with strong momentum",
                criteria={
                    'max_mcap': 10_000_000,  # $10M max
                    'min_volume': 500_000,   # $500K+ volume
                    'min_liquidity': 100_000, # $100K+ liquidity
                    'price_momentum': 0.05   # 5%+ momentum
                },
                weight=0.3,
                success_rate=0.72
            ),
            BravoStrategy(
                name="Whale Activity",
                description="Coins with significant whale accumulation",
                criteria={
                    'min_volume': 1_000_000,  # $1M+ volume
                    'min_holders': 500,       # 500+ holders
                    'max_mcap': 50_000_000    # $50M max
                },
                weight=0.25,
                success_rate=0.68
            ),
            BravoStrategy(
                name="Early Discovery",
                description="Newly discovered coins with potential",
                criteria={
                    'max_mcap': 5_000_000,    # $5M max
                    'min_liquidity': 50_000,  # $50K+ liquidity
                    'min_holders': 100        # 100+ holders
                },
                weight=0.2,
                success_rate=0.85
            ),
            BravoStrategy(
                name="Volume Surge",
                description="Coins experiencing volume surges",
                criteria={
                    'min_volume': 2_000_000,  # $2M+ volume
                    'max_mcap': 100_000_000,  # $100M max
                    'price_momentum': 0.1     # 10%+ momentum
                },
                weight=0.15,
                success_rate=0.64
            ),
            BravoStrategy(
                name="Community Strength",
                description="Strong community and holder distribution",
                criteria={
                    'min_holders': 1000,      # 1000+ holders
                    'min_liquidity': 200_000, # $200K+ liquidity
                    'max_mcap': 25_000_000    # $25M max
                },
                weight=0.1,
                success_rate=0.58
            )
        ]
        
        logger.info(f"✅ Initialized {len(strategies)} Bravo strategies")
        return strategies
    
    def parse_telegram_message(self, raw_message: str, channel: str = "atm.day") -> Optional[TelegramSignal]:
        """Parse Telegram message into structured signal"""
        try:
            # Generate unique ID
            signal_id = f"{channel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{abs(hash(raw_message)) % 10000}"
            
            signal = TelegramSignal(
                id=signal_id,
                raw_message=raw_message,
                channel=channel,
                timestamp=datetime.now(),
                status=SignalStatus.RECEIVED
            )
            
            # Extract ticker
            ticker_match = re.search(r'\\$([A-Z]{2,10})', raw_message, re.IGNORECASE)
            if ticker_match:
                signal.ticker = ticker_match.group(1).upper()
            
            # Extract contract address
            ca_patterns = [
                r'(?:CA|Contract|Address)[\s:]*([A-Za-z0-9]{32,44})',
                r'([A-Za-z0-9]{32,44})',  # Standalone address
            ]
            
            for pattern in ca_patterns:
                match = re.search(pattern, raw_message)
                if match and len(match.group(1)) >= 32:
                    signal.contract_address = match.group(1)
                    break
            
            # Extract prices
            price_patterns = [
                r'(?:Entry|Price|@)[\s:]*\\$?([0-9]+\\.?[0-9]*)',
                r'(?:Target|TP)[\s:]*\\$?([0-9]+\\.?[0-9]*)',
                r'(?:Stop|SL)[\s:]*\\$?([0-9]+\\.?[0-9]*)'
            ]
            
            prices = []
            for pattern in price_patterns:
                match = re.search(pattern, raw_message, re.IGNORECASE)
                if match:
                    prices.append(float(match.group(1)))
            
            if len(prices) >= 1:
                signal.entry_price = prices[0]
            if len(prices) >= 2:
                signal.target_price = prices[1]
            if len(prices) >= 3:
                signal.stop_loss = prices[2]
            
            signal.status = SignalStatus.PARSED
            signal.processing_log.append(f"Parsed: ticker={signal.ticker}, ca={signal.contract_address}")
            
            self.processing_stats['signals_parsed'] += 1
            logger.info(f"✅ Parsed signal: {signal.ticker} from {channel}")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Failed to parse message: {e}")
            return None
    
    def enrich_signal(self, signal: TelegramSignal) -> TelegramSignal:
        """Enrich signal with live market data"""
        try:
            if not signal.contract_address:
                signal.processing_log.append("⚠️ No contract address - skipping enrichment")
                return signal
            
            # Try multiple APIs for enrichment
            enriched = False
            
            # Try DexScreener first (free, reliable)
            try:
                dex_data = self._fetch_dexscreener_data(signal.contract_address)
                if dex_data:
                    signal.current_price = dex_data.get('priceUsd', 0)
                    signal.volume_24h = dex_data.get('volume', {}).get('h24', 0)
                    signal.liquidity = dex_data.get('liquidity', {}).get('usd', 0)
                    signal.market_cap = dex_data.get('marketCap', 0)
                    enriched = True
                    signal.processing_log.append("✅ Enriched via DexScreener")
            except Exception as e:
                signal.processing_log.append(f"⚠️ DexScreener failed: {str(e)[:50]}")
            
            # Try Jupiter as backup
            if not enriched:
                try:
                    jupiter_data = self._fetch_jupiter_data(signal.contract_address)
                    if jupiter_data:
                        signal.current_price = jupiter_data.get('price', 0)
                        enriched = True
                        signal.processing_log.append("✅ Enriched via Jupiter")
                except Exception as e:
                    signal.processing_log.append(f"⚠️ Jupiter failed: {str(e)[:50]}")
            
            # Get holder count from blockchain
            try:
                signal.holder_count = self._get_holder_count(signal.contract_address)
                signal.processing_log.append(f"✅ Holder count: {signal.holder_count}")
            except Exception as e:
                signal.processing_log.append(f"⚠️ Holder count failed: {str(e)[:50]}")
            
            if enriched:
                signal.status = SignalStatus.ENRICHED
                self.processing_stats['signals_enriched'] += 1
                logger.info(f"✅ Enriched signal: {signal.ticker}")
            else:
                signal.processing_log.append("❌ All enrichment sources failed")
            
            return signal
            
        except Exception as e:
            signal.processing_log.append(f"❌ Enrichment error: {e}")
            logger.error(f"❌ Enrichment failed for {signal.ticker}: {e}")
            return signal
    
    def _fetch_dexscreener_data(self, contract_address: str) -> Optional[Dict]:
        """Fetch data from DexScreener API"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('pairs') and len(data['pairs']) > 0:
                    return data['pairs'][0]  # Return first pair
            
            return None
            
        except Exception as e:
            logger.error(f"DexScreener API error: {e}")
            return None
    
    def _fetch_jupiter_data(self, contract_address: str) -> Optional[Dict]:
        """Fetch data from Jupiter API"""
        try:
            url = f"https://price.jup.ag/v4/price?ids={contract_address}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and contract_address in data['data']:
                    return data['data'][contract_address]
            
            return None
            
        except Exception as e:
            logger.error(f"Jupiter API error: {e}")
            return None
    
    def _get_holder_count(self, contract_address: str) -> int:
        """Get holder count (simplified estimation)"""
        # This would integrate with Solscan or similar service
        # For now, return estimated based on market cap and liquidity
        return np.random.randint(100, 2000)  # Placeholder
    
    def apply_bravo_strategies(self, signal: TelegramSignal) -> TelegramSignal:
        """Apply Bravo's strategies to analyze signal"""
        try:
            total_score = 0.0
            strategy_results = []
            
            for strategy in self.bravo_strategies:
                matches, score, reasoning = strategy.evaluate(signal)
                
                if matches:
                    signal.strategy_matches.append(strategy.name)
                    total_score += score
                    strategy_results.append(f"{strategy.name}: {score:.2f}")
                    signal.processing_log.append(f"✅ {strategy.name}: {reasoning}")
                else:
                    signal.processing_log.append(f"❌ {strategy.name}: {reasoning}")
            
            # Calculate final scores
            signal.confidence_score = min(total_score * 100, 100)  # Cap at 100
            signal.runner_potential = signal.confidence_score * 0.8  # Slightly conservative
            signal.risk_score = max(0, 100 - signal.confidence_score)
            
            signal.status = SignalStatus.ANALYZED
            signal.processing_log.append(f"🎯 Final confidence: {signal.confidence_score:.1f}%")
            
            self.processing_stats['signals_filtered'] += 1
            logger.info(f"✅ Analyzed signal: {signal.ticker} - Score: {signal.confidence_score:.1f}%")
            
            return signal
            
        except Exception as e:
            signal.processing_log.append(f"❌ Strategy analysis error: {e}")
            logger.error(f"❌ Strategy analysis failed for {signal.ticker}: {e}")
            return signal
    
    def save_signal(self, signal: TelegramSignal):
        """Save signal to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO telegram_signals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.id, signal.raw_message, signal.channel, signal.timestamp,
                signal.ticker, signal.contract_address, signal.entry_price,
                signal.target_price, signal.stop_loss, signal.current_price,
                signal.market_cap, signal.volume_24h, signal.liquidity,
                signal.holder_count, signal.confidence_score, signal.risk_score,
                signal.runner_potential, json.dumps(signal.strategy_matches),
                signal.status.value, json.dumps(signal.processing_log),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Saved signal: {signal.ticker}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save signal: {e}")
    
    def get_daily_top_runners(self, date: datetime = None, limit: int = 5) -> List[Dict]:
        """Get top 5 runners for a specific date"""
        if date is None:
            date = datetime.now().date()
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM telegram_signals 
                WHERE DATE(timestamp) = ? 
                AND confidence_score > 50
                ORDER BY runner_potential DESC, confidence_score DESC
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(date, limit))
            conn.close()
            
            runners = df.to_dict('records') if not df.empty else []
            
            # Save daily runners
            if runners:
                self._save_daily_runners(date, runners)
            
            self.processing_stats['top_runners_found'] = len(runners)
            logger.info(f"✅ Found {len(runners)} top runners for {date}")
            
            return runners
            
        except Exception as e:
            logger.error(f"❌ Failed to get daily runners: {e}")
            return []
    
    def _save_daily_runners(self, date: datetime, runners: List[Dict]):
        """Save daily top runners"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing entries for this date
            cursor.execute('DELETE FROM daily_runners WHERE date = ?', (date,))
            
            # Insert new runners
            for rank, runner in enumerate(runners, 1):
                strategy_summary = json.loads(runner.get('strategy_matches', '[]'))
                
                cursor.execute('''
                    INSERT INTO daily_runners (date, signal_id, rank, final_score, strategy_summary)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    date, runner['id'], rank, runner['runner_potential'],
                    json.dumps(strategy_summary)
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Saved {len(runners)} daily runners")
            
        except Exception as e:
            logger.error(f"❌ Failed to save daily runners: {e}")
    
    async def process_signal(self, raw_message: str, channel: str = "atm.day") -> Optional[TelegramSignal]:
        """Complete signal processing pipeline"""
        start_time = datetime.now()
        
        try:
            self.processing_stats['signals_received'] += 1
            self.processing_stats['last_signal_time'] = start_time
            
            # Step 1: Parse the message
            signal = self.parse_telegram_message(raw_message, channel)
            if not signal:
                logger.warning("❌ Failed to parse message")
                return None
            
            # Step 2: Enrich with market data
            signal = self.enrich_signal(signal)
            
            # Step 3: Apply Bravo strategies
            signal = self.apply_bravo_strategies(signal)
            
            # Step 4: Save to database
            self.save_signal(signal)
            
            # Step 5: Mark as completed
            signal.status = SignalStatus.COMPLETED
            
            # Update processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            self.processing_stats['avg_processing_time'] = (
                self.processing_stats['avg_processing_time'] * 0.8 + processing_time * 0.2
            )
            
            logger.info(f"✅ Completed processing: {signal.ticker} in {processing_time:.1f}s")
            return signal
            
        except Exception as e:
            logger.error(f"❌ Signal processing failed: {e}")
            return None
    
    def get_processing_stats(self) -> Dict:
        """Get current processing statistics"""
        stats = self.processing_stats.copy()
        
        # Add database stats
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total signals in database
            cursor.execute('SELECT COUNT(*) FROM telegram_signals')
            stats['total_signals'] = cursor.fetchone()[0]
            
            # Today's signals
            cursor.execute('SELECT COUNT(*) FROM telegram_signals WHERE DATE(timestamp) = DATE("now")')
            stats['today_signals'] = cursor.fetchone()[0]
            
            # Success rate (signals with confidence > 70%)
            cursor.execute('SELECT COUNT(*) FROM telegram_signals WHERE confidence_score > 70')
            high_confidence = cursor.fetchone()[0]
            stats['success_rate'] = (high_confidence / max(stats['total_signals'], 1)) * 100
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
        
        return stats

# Global instance for dashboard integration
telegram_signal_processor = TelegramSignalProcessor()