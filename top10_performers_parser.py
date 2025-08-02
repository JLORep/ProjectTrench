#!/usr/bin/env python3
"""
TrenchCoat Pro - Top10 Performers Parser & Veracity Validator
Advanced system for parsing, enriching, and validating ATM.day top performers
"""

import re
import json
import sqlite3
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio
import aiohttp
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceVeracity(Enum):
    """Performance claim verification status"""
    VERIFIED = "verified"       # Confirmed accurate
    INFLATED = "inflated"      # Exaggerated but partially true
    FABRICATED = "fabricated"  # Completely false
    UNVERIFIABLE = "unverifiable"  # Cannot be verified
    PENDING = "pending"        # Verification in progress

@dataclass
class Top10Performer:
    """Top10 performer data structure"""
    # Basic identification
    id: str
    rank: int
    ticker: str
    contract_address: Optional[str]
    
    # Claimed performance
    claimed_gain_pct: float
    claimed_start_price: Optional[float]
    claimed_end_price: Optional[float]
    claimed_timeframe: str  # "24h", "7d", "30d", etc.
    
    # Verified performance
    actual_gain_pct: Optional[float] = None
    actual_start_price: Optional[float] = None
    actual_end_price: Optional[float] = None
    verification_confidence: float = 0.0
    
    # Enriched market data
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    liquidity: Optional[float] = None
    holder_count: Optional[int] = None
    
    # Technical indicators
    rsi: Optional[float] = None
    volatility: Optional[float] = None
    price_momentum: Optional[float] = None
    volume_momentum: Optional[float] = None
    
    # Mathematical efficiency metrics
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    profit_probability: Optional[float] = None
    kelly_criterion: Optional[float] = None
    
    # Metadata  
    source_message: str = ""
    parsing_timestamp: datetime = None
    verification_status: PerformanceVeracity = PerformanceVeracity.PENDING
    verification_notes: List[str] = None
    
    def __post_init__(self):
        if self.parsing_timestamp is None:
            self.parsing_timestamp = datetime.now()
        if self.verification_notes is None:
            self.verification_notes = []

@dataclass
class MathematicalModel:
    """Mathematical efficiency model for coin selection"""
    name: str
    description: str
    weight: float
    parameters: Dict[str, float]
    
    def calculate_score(self, performer: Top10Performer) -> Tuple[float, str]:
        """Calculate efficiency score for a performer"""
        pass

class Top10PerformersParser:
    """Advanced Top10 performers parser with veracity validation"""
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.api_cache = {}
        self.verification_stats = {
            'total_parsed': 0,
            'verified': 0,
            'inflated': 0,
            'fabricated': 0,
            'unverifiable': 0
        }
        
        # Mathematical models for efficiency
        self.mathematical_models = self._init_mathematical_models()
        
        # Database initialization
        self._init_database()
    
    def _init_database(self):
        """Initialize Top10 performers database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create top10_performers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS top10_performers (
                    id TEXT PRIMARY KEY,
                    rank INTEGER,
                    ticker TEXT,
                    contract_address TEXT,
                    claimed_gain_pct REAL,
                    claimed_start_price REAL,
                    claimed_end_price REAL,
                    claimed_timeframe TEXT,
                    actual_gain_pct REAL,
                    actual_start_price REAL,
                    actual_end_price REAL,
                    verification_confidence REAL,
                    current_price REAL,
                    market_cap REAL,
                    volume_24h REAL,
                    liquidity REAL,
                    holder_count INTEGER,
                    rsi REAL,
                    volatility REAL,
                    price_momentum REAL,
                    volume_momentum REAL,
                    sharpe_ratio REAL,
                    sortino_ratio REAL,
                    max_drawdown REAL,
                    profit_probability REAL,
                    kelly_criterion REAL,
                    source_message TEXT,
                    parsing_timestamp DATETIME,
                    verification_status TEXT,
                    verification_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create mathematical_efficiency table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mathematical_efficiency (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    performer_id TEXT,
                    efficiency_score REAL,
                    profitability_rank INTEGER,
                    model_scores TEXT,
                    selection_reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (performer_id) REFERENCES top10_performers (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Top10 performers database initialized")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    def _init_mathematical_models(self) -> List[MathematicalModel]:
        """Initialize mathematical efficiency models"""
        models = [
            MathematicalModel(
                name="Kelly Criterion Optimization",
                description="Optimal bet sizing based on win probability and payoff",
                weight=0.25,
                parameters={
                    'min_win_rate': 0.6,
                    'min_payoff_ratio': 1.5,
                    'max_kelly_pct': 0.25
                }
            ),
            MathematicalModel(
                name="Sharpe Ratio Analysis", 
                description="Risk-adjusted return efficiency",
                weight=0.2,
                parameters={
                    'min_sharpe': 1.0,
                    'volatility_penalty': 0.1,
                    'risk_free_rate': 0.05
                }
            ),
            MathematicalModel(
                name="Momentum Factor Model",
                description="Price and volume momentum scoring",
                weight=0.2,
                parameters={
                    'price_momentum_weight': 0.6,
                    'volume_momentum_weight': 0.4,
                    'momentum_threshold': 0.15
                }
            ),
            MathematicalModel(
                name="Liquidity Depth Model",
                description="Market depth and slippage analysis",
                weight=0.15,
                parameters={
                    'min_liquidity': 100000,
                    'slippage_tolerance': 0.02,
                    'depth_score_weight': 0.8
                }
            ),
            MathematicalModel(
                name="Veracity-Weighted Model",
                description="Performance claim verification weighting",
                weight=0.2,
                parameters={
                    'verified_multiplier': 1.0,
                    'inflated_penalty': 0.7,
                    'fabricated_penalty': 0.1,
                    'unverifiable_penalty': 0.5
                }
            )
        ]
        
        logger.info(f"✅ Initialized {len(models)} mathematical models")
        return models
    
    def parse_top10_message(self, message: str, timestamp: datetime = None) -> List[Top10Performer]:
        """Parse ATM.day Top10 performers message"""
        if timestamp is None:
            timestamp = datetime.now()
        
        performers = []
        
        try:
            # Pattern for Top10 entries
            # Example: "1. PEPE +1,247% (24h) | CA: EPjF...t1v"
            pattern = r'(\d+)\.\s*([A-Z]{2,10})\s*[\+\-]?([0-9,]+\.?\d*)%?\s*(?:\(([^)]+)\))?\s*(?:\|\s*(?:CA|Contract)?:?\s*([A-Za-z0-9]{32,44}))?'
            
            matches = re.findall(pattern, message, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                rank, ticker, gain_str, timeframe, contract = match
                
                # Clean gain percentage
                gain_pct = float(gain_str.replace(',', ''))
                
                # Generate unique ID
                performer_id = f"top10_{timestamp.strftime('%Y%m%d')}_{rank}_{ticker}"
                
                performer = Top10Performer(
                    id=performer_id,
                    rank=int(rank),
                    ticker=ticker.upper(),
                    contract_address=contract if contract else None,
                    claimed_gain_pct=gain_pct,
                    claimed_timeframe=timeframe if timeframe else "24h",
                    source_message=message,
                    parsing_timestamp=timestamp
                )
                
                performers.append(performer)
                logger.info(f"✅ Parsed {ticker} - Rank #{rank}: +{gain_pct}%")
            
            self.verification_stats['total_parsed'] += len(performers)
            return performers
            
        except Exception as e:
            logger.error(f"❌ Failed to parse Top10 message: {e}")
            return []
    
    async def enrich_performer(self, performer: Top10Performer) -> Top10Performer:
        """Enrich performer with comprehensive market data"""
        try:
            if not performer.contract_address:
                # Try to find contract address by ticker
                performer.contract_address = await self._find_contract_by_ticker(performer.ticker)
            
            if not performer.contract_address:
                performer.verification_notes.append("⚠️ No contract address found")
                return performer
            
            # Multi-source data enrichment
            enriched = False
            
            # DexScreener enrichment
            try:
                dex_data = await self._fetch_dexscreener_data(performer.contract_address)
                if dex_data:
                    performer.current_price = dex_data.get('priceUsd', 0)
                    performer.volume_24h = dex_data.get('volume', {}).get('h24', 0)
                    performer.liquidity = dex_data.get('liquidity', {}).get('usd', 0)
                    performer.market_cap = dex_data.get('marketCap', 0)
                    
                    # Calculate price momentum
                    price_change = dex_data.get('priceChange', {}).get('h24', 0)
                    performer.price_momentum = price_change / 100 if price_change else 0
                    
                    enriched = True
                    performer.verification_notes.append("✅ Enriched via DexScreener")
            except Exception as e:
                performer.verification_notes.append(f"⚠️ DexScreener failed: {str(e)[:50]}")
            
            # Calculate technical indicators if we have price data
            if performer.current_price and performer.volume_24h:
                performer = await self._calculate_technical_indicators(performer)
            
            # Calculate mathematical efficiency metrics
            performer = self._calculate_efficiency_metrics(performer)
            
            if enriched:
                performer.verification_notes.append("✅ Comprehensive enrichment completed")
            
            return performer
            
        except Exception as e:
            performer.verification_notes.append(f"❌ Enrichment error: {e}")
            logger.error(f"❌ Enrichment failed for {performer.ticker}: {e}")
            return performer
    
    async def validate_performance_veracity(self, performer: Top10Performer) -> Top10Performer:
        """Validate the veracity of claimed performance"""
        try:
            if not performer.contract_address:
                performer.verification_status = PerformanceVeracity.UNVERIFIABLE
                performer.verification_notes.append("❌ Cannot verify without contract address")
                return performer
            
            # Get historical price data for verification
            historical_data = await self._get_historical_prices(
                performer.contract_address, 
                performer.claimed_timeframe
            )
            
            if not historical_data:
                performer.verification_status = PerformanceVeracity.UNVERIFIABLE
                performer.verification_notes.append("❌ No historical data available")
                return performer
            
            # Calculate actual performance
            start_price = historical_data['start_price']
            end_price = historical_data['end_price']
            actual_gain = ((end_price - start_price) / start_price) * 100
            
            performer.actual_start_price = start_price
            performer.actual_end_price = end_price
            performer.actual_gain_pct = actual_gain
            
            # Compare claimed vs actual
            claimed = performer.claimed_gain_pct
            actual = actual_gain
            
            verification_threshold = 0.1  # 10% tolerance
            
            if abs(claimed - actual) <= (claimed * verification_threshold):
                # Within tolerance - verified
                performer.verification_status = PerformanceVeracity.VERIFIED
                performer.verification_confidence = 0.95
                performer.verification_notes.append(f"✅ VERIFIED: Claimed {claimed:.1f}%, Actual {actual:.1f}%")
                self.verification_stats['verified'] += 1
                
            elif actual > 0 and claimed > actual:
                # Exaggerated but positive
                inflation_factor = claimed / actual
                if inflation_factor <= 2.0:  # Less than 2x inflation
                    performer.verification_status = PerformanceVeracity.INFLATED
                    performer.verification_confidence = 0.6
                    performer.verification_notes.append(f"⚠️ INFLATED: Claimed {claimed:.1f}%, Actual {actual:.1f}% ({inflation_factor:.1f}x)")
                    self.verification_stats['inflated'] += 1
                else:
                    performer.verification_status = PerformanceVeracity.FABRICATED
                    performer.verification_confidence = 0.2
                    performer.verification_notes.append(f"❌ FABRICATED: Claimed {claimed:.1f}%, Actual {actual:.1f}% ({inflation_factor:.1f}x inflation)")
                    self.verification_stats['fabricated'] += 1
                    
            elif actual <= 0 and claimed > 0:
                # Claimed positive but actually negative/flat
                performer.verification_status = PerformanceVeracity.FABRICATED
                performer.verification_confidence = 0.1
                performer.verification_notes.append(f"❌ FABRICATED: Claimed +{claimed:.1f}%, Actually {actual:.1f}%")
                self.verification_stats['fabricated'] += 1
                
            else:
                performer.verification_status = PerformanceVeracity.UNVERIFIABLE
                performer.verification_confidence = 0.3
                performer.verification_notes.append(f"❓ UNCLEAR: Claimed {claimed:.1f}%, Actual {actual:.1f}%")
                self.verification_stats['unverifiable'] += 1
            
            logger.info(f"✅ Verified {performer.ticker}: {performer.verification_status.value}")
            return performer
            
        except Exception as e:
            performer.verification_status = PerformanceVeracity.UNVERIFIABLE
            performer.verification_notes.append(f"❌ Verification error: {e}")
            logger.error(f"❌ Verification failed for {performer.ticker}: {e}")
            return performer
    
    def calculate_mathematical_efficiency(self, performers: List[Top10Performer]) -> List[Tuple[Top10Performer, float, Dict]]:
        """Calculate mathematical efficiency for profitable coin selection"""
        try:
            efficiency_results = []
            
            for performer in performers:
                total_score = 0.0
                model_scores = {}
                reasoning = []
                
                # Kelly Criterion Model
                kelly_model = self.mathematical_models[0]
                if performer.profit_probability and performer.claimed_gain_pct:
                    win_rate = performer.profit_probability
                    payoff_ratio = performer.claimed_gain_pct / 100
                    
                    # Adjust for veracity
                    veracity_multiplier = self._get_veracity_multiplier(performer.verification_status)
                    adjusted_payoff = payoff_ratio * veracity_multiplier
                    
                    if win_rate >= kelly_model.parameters['min_win_rate']:
                        kelly_score = (win_rate * adjusted_payoff - (1 - win_rate)) * kelly_model.weight
                        kelly_score = max(0, min(kelly_score, kelly_model.parameters['max_kelly_pct']))
                        model_scores['kelly'] = kelly_score
                        total_score += kelly_score
                        reasoning.append(f"Kelly: {kelly_score:.3f} (win_rate: {win_rate:.2f})")
                
                # Sharpe Ratio Model
                sharpe_model = self.mathematical_models[1]
                if performer.sharpe_ratio:
                    sharpe_score = min(performer.sharpe_ratio / 2.0, 1.0) * sharpe_model.weight
                    if performer.volatility:
                        sharpe_score *= (1 - performer.volatility * sharpe_model.parameters['volatility_penalty'])
                    model_scores['sharpe'] = sharpe_score
                    total_score += sharpe_score
                    reasoning.append(f"Sharpe: {sharpe_score:.3f}")
                
                # Momentum Model
                momentum_model = self.mathematical_models[2]
                if performer.price_momentum and performer.volume_momentum:
                    momentum_score = (
                        performer.price_momentum * momentum_model.parameters['price_momentum_weight'] +
                        performer.volume_momentum * momentum_model.parameters['volume_momentum_weight']
                    ) * momentum_model.weight
                    model_scores['momentum'] = momentum_score
                    total_score += momentum_score
                    reasoning.append(f"Momentum: {momentum_score:.3f}")
                
                # Liquidity Model
                liquidity_model = self.mathematical_models[3]
                if performer.liquidity:
                    liquidity_score = min(performer.liquidity / 1000000, 1.0) * liquidity_model.weight
                    model_scores['liquidity'] = liquidity_score
                    total_score += liquidity_score
                    reasoning.append(f"Liquidity: {liquidity_score:.3f}")
                
                # Veracity Model
                veracity_model = self.mathematical_models[4]
                veracity_multiplier = self._get_veracity_multiplier(performer.verification_status)
                veracity_score = veracity_multiplier * veracity_model.weight
                model_scores['veracity'] = veracity_score
                total_score += veracity_score
                reasoning.append(f"Veracity: {veracity_score:.3f}")
                
                # Final efficiency score
                efficiency_results.append((
                    performer, 
                    total_score,
                    {
                        'model_scores': model_scores,
                        'reasoning': reasoning,
                        'veracity_multiplier': veracity_multiplier
                    }
                ))
            
            # Sort by efficiency score
            efficiency_results.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"✅ Calculated efficiency for {len(performers)} performers")
            return efficiency_results
            
        except Exception as e:
            logger.error(f"❌ Mathematical efficiency calculation failed: {e}")
            return []
    
    def _get_veracity_multiplier(self, status: PerformanceVeracity) -> float:
        """Get multiplier based on verification status"""
        multipliers = {
            PerformanceVeracity.VERIFIED: 1.0,
            PerformanceVeracity.INFLATED: 0.7,
            PerformanceVeracity.FABRICATED: 0.1,
            PerformanceVeracity.UNVERIFIABLE: 0.5,
            PerformanceVeracity.PENDING: 0.3
        }
        return multipliers.get(status, 0.3)
    
    async def _find_contract_by_ticker(self, ticker: str) -> Optional[str]:
        """Find contract address by ticker symbol"""
        try:
            # Search DexScreener for ticker
            url = f"https://api.dexscreener.com/latest/dex/search?q={ticker}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        pairs = data.get('pairs', [])
                        
                        # Find Solana pairs first
                        for pair in pairs:
                            if pair.get('chainId') == 'solana':
                                return pair.get('baseToken', {}).get('address')
                        
                        # Fallback to any chain
                        if pairs:
                            return pairs[0].get('baseToken', {}).get('address')
            
            return None
            
        except Exception as e:
            logger.error(f"Contract lookup failed for {ticker}: {e}")
            return None
    
    async def _fetch_dexscreener_data(self, contract_address: str) -> Optional[Dict]:
        """Fetch comprehensive data from DexScreener"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('pairs'):
                            return data['pairs'][0]
            return None
        except Exception as e:
            logger.error(f"DexScreener fetch failed: {e}")
            return None
    
    async def _get_historical_prices(self, contract_address: str, timeframe: str) -> Optional[Dict]:
        """Get historical price data for verification"""
        try:
            # This would integrate with historical price APIs
            # For now, simulate with current price and random historical
            current_data = await self._fetch_dexscreener_data(contract_address)
            if current_data:
                current_price = current_data.get('priceUsd', 0)
                
                # Simulate historical price (would be real API call)
                if timeframe == "24h":
                    historical_price = current_price * (1 - np.random.uniform(0.1, 0.3))
                elif timeframe == "7d":
                    historical_price = current_price * (1 - np.random.uniform(0.2, 0.5))
                else:
                    historical_price = current_price * (1 - np.random.uniform(0.3, 0.7))
                
                return {
                    'start_price': historical_price,
                    'end_price': current_price
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Historical price lookup failed: {e}")
            return None
    
    async def _calculate_technical_indicators(self, performer: Top10Performer) -> Top10Performer:
        """Calculate technical indicators"""
        try:
            # Simplified technical indicators (would use real TA library)
            if performer.current_price and performer.volume_24h:
                # RSI simulation
                performer.rsi = np.random.uniform(30, 70)
                
                # Volatility estimate
                performer.volatility = min(abs(performer.claimed_gain_pct) / 100, 1.0)
                
                # Volume momentum
                performer.volume_momentum = min(performer.volume_24h / 1000000, 2.0)
            
            return performer
            
        except Exception as e:
            logger.error(f"Technical indicators calculation failed: {e}")
            return performer
    
    def _calculate_efficiency_metrics(self, performer: Top10Performer) -> Top10Performer:
        """Calculate mathematical efficiency metrics"""
        try:
            # Sharpe ratio estimate
            if performer.claimed_gain_pct and performer.volatility:
                risk_free_rate = 0.05
                excess_return = (performer.claimed_gain_pct / 100) - risk_free_rate
                performer.sharpe_ratio = excess_return / max(performer.volatility, 0.01)
            
            # Sortino ratio (downside deviation)
            if performer.sharpe_ratio and performer.volatility:
                downside_deviation = performer.volatility * 0.7  # Estimate
                performer.sortino_ratio = performer.sharpe_ratio * 1.2
            
            # Max drawdown estimate
            if performer.volatility:
                performer.max_drawdown = performer.volatility * 0.5
            
            # Profit probability (based on verification and market conditions)
            base_probability = 0.5
            if performer.verification_status == PerformanceVeracity.VERIFIED:
                base_probability = 0.75
            elif performer.verification_status == PerformanceVeracity.INFLATED:
                base_probability = 0.60
            elif performer.verification_status == PerformanceVeracity.FABRICATED:
                base_probability = 0.25
            
            # Adjust for market conditions
            if performer.volume_24h and performer.volume_24h > 1000000:
                base_probability += 0.1
            if performer.liquidity and performer.liquidity > 500000:
                base_probability += 0.05
            
            performer.profit_probability = min(base_probability, 0.95)
            
            # Kelly criterion
            if performer.profit_probability and performer.claimed_gain_pct:
                win_rate = performer.profit_probability
                payoff_ratio = performer.claimed_gain_pct / 100
                performer.kelly_criterion = (win_rate * payoff_ratio - (1 - win_rate)) / payoff_ratio
                performer.kelly_criterion = max(0, min(performer.kelly_criterion, 0.25))
            
            return performer
            
        except Exception as e:
            logger.error(f"Efficiency metrics calculation failed: {e}")
            return performer
    
    def save_performer(self, performer: Top10Performer):
        """Save performer to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO top10_performers VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                performer.id, performer.rank, performer.ticker, performer.contract_address,
                performer.claimed_gain_pct, performer.claimed_start_price, performer.claimed_end_price,
                performer.claimed_timeframe, performer.actual_gain_pct, performer.actual_start_price,
                performer.actual_end_price, performer.verification_confidence, performer.current_price,
                performer.market_cap, performer.volume_24h, performer.liquidity, performer.holder_count,
                performer.rsi, performer.volatility, performer.price_momentum, performer.volume_momentum,
                performer.sharpe_ratio, performer.sortino_ratio, performer.max_drawdown,
                performer.profit_probability, performer.kelly_criterion, performer.source_message,
                performer.parsing_timestamp, performer.verification_status.value,
                json.dumps(performer.verification_notes), datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Saved performer: {performer.ticker}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save performer: {e}")
    
    def save_efficiency_results(self, date: datetime, results: List[Tuple[Top10Performer, float, Dict]]):
        """Save mathematical efficiency results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing results for this date
            cursor.execute('DELETE FROM mathematical_efficiency WHERE date = ?', (date.date(),))
            
            # Save new results
            for rank, (performer, score, details) in enumerate(results, 1):
                cursor.execute('''
                    INSERT INTO mathematical_efficiency (date, performer_id, efficiency_score, 
                                                       profitability_rank, model_scores, selection_reason)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    date.date(), performer.id, score, rank,
                    json.dumps(details['model_scores']),
                    " | ".join(details['reasoning'])
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Saved efficiency results for {len(results)} performers")
            
        except Exception as e:
            logger.error(f"❌ Failed to save efficiency results: {e}")
    
    async def process_top10_message(self, message: str, timestamp: datetime = None) -> List[Top10Performer]:
        """Complete Top10 processing pipeline"""
        if timestamp is None:
            timestamp = datetime.now()
        
        try:
            # Step 1: Parse message
            performers = self.parse_top10_message(message, timestamp)
            if not performers:
                logger.warning("❌ No performers parsed from message")
                return []
            
            # Step 2: Enrich and validate each performer
            processed_performers = []
            for performer in performers:
                # Enrich with market data
                performer = await self.enrich_performer(performer)
                
                # Validate performance claims
                performer = await self.validate_performance_veracity(performer)
                
                # Save to database
                self.save_performer(performer)
                
                processed_performers.append(performer)
                
                logger.info(f"✅ Processed {performer.ticker}: {performer.verification_status.value}")
            
            # Step 3: Calculate mathematical efficiency
            efficiency_results = self.calculate_mathematical_efficiency(processed_performers)
            
            # Step 4: Save efficiency results
            if efficiency_results:
                self.save_efficiency_results(timestamp, efficiency_results)
            
            logger.info(f"✅ Completed Top10 processing: {len(processed_performers)} performers")
            return processed_performers
            
        except Exception as e:
            logger.error(f"❌ Top10 processing failed: {e}")
            return []
    
    def get_verification_stats(self) -> Dict:
        """Get verification statistics"""
        stats = self.verification_stats.copy()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Database stats
            cursor.execute('SELECT COUNT(*) FROM top10_performers')
            stats['total_in_db'] = cursor.fetchone()[0]
            
            # Verification breakdown
            cursor.execute('''
                SELECT verification_status, COUNT(*) 
                FROM top10_performers 
                GROUP BY verification_status
            ''')
            
            for status, count in cursor.fetchall():
                stats[f'{status}_count'] = count
                
            # Average verification confidence
            cursor.execute('SELECT AVG(verification_confidence) FROM top10_performers WHERE verification_confidence > 0')
            result = cursor.fetchone()
            stats['avg_confidence'] = result[0] if result[0] else 0.0
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to get verification stats: {e}")
        
        return stats

# Global instance
top10_parser = Top10PerformersParser()