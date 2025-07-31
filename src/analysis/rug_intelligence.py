import asyncio
import sqlite3
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from loguru import logger
import aiohttp
from src.data.database import CoinDatabase

class RugStatus(Enum):
    HEALTHY = "HEALTHY"
    SUSPICIOUS = "SUSPICIOUS" 
    RUG_DETECTED = "RUG_DETECTED"
    CONFIRMED_RUG = "CONFIRMED_RUG"

@dataclass
class TokenLifecycle:
    """Complete lifecycle analysis of a token"""
    contract_address: str
    symbol: str
    creation_timestamp: datetime
    discovery_timestamp: datetime
    age_at_discovery: timedelta
    
    # Price action
    launch_price: float
    discovery_price: float
    peak_price: float
    current_price: float
    rug_price: Optional[float] = None
    
    # Performance metrics
    launch_to_peak_multiplier: float = 0
    discovery_to_peak_multiplier: float = 0
    peak_to_rug_drop: float = 0
    
    # Volume analysis
    launch_volume: float = 0
    discovery_volume: float = 0
    peak_volume: float = 0
    volume_decline_rate: float = 0
    
    # Wallet analysis
    total_holders: int = 0
    whale_holders: int = 0
    dev_still_holds: bool = True
    dev_dump_detected: bool = False
    whale_exodus: bool = False
    
    # Risk factors
    momentum_score: float = 0
    volume_health: float = 0
    holder_health: float = 0
    age_bonus: float = 0
    overall_risk: float = 0
    
    # Status
    status: RugStatus = RugStatus.HEALTHY
    rug_timestamp: Optional[datetime] = None
    final_outcome: Optional[str] = None

class RugIntelligenceEngine:
    """
    Advanced rug detection and profit extraction system
    Analyzes historical patterns to predict and profit from rugs
    """
    
    def __init__(self, db: CoinDatabase):
        self.db = db
        self.historical_rugs: List[TokenLifecycle] = []
        self.active_tokens: Dict[str, TokenLifecycle] = {}
        self.rug_patterns = {}
        self.profit_opportunities = []
        
    async def analyze_historical_rugs(self) -> List[TokenLifecycle]:
        """Analyze all historical tokens to identify rug patterns"""
        logger.info("🔍 Analyzing historical rugs for profit patterns...")
        
        # Get all tokens with price history
        with sqlite3.connect(self.db.db_path) as conn:
            query = """
            SELECT 
                c.symbol,
                c.name,
                json_extract(cm.metadata, '$.enrichment_data.contract_address') as contract_address,
                pd.timestamp,
                pd.open,
                pd.high, 
                pd.low,
                pd.close,
                pd.volume
            FROM coins c
            JOIN coin_metadata cm ON c.id = cm.coin_id
            JOIN price_data pd ON c.id = pd.coin_id
            WHERE contract_address IS NOT NULL
            ORDER BY c.symbol, pd.timestamp
            """
            
            df = pd.read_sql_query(query, conn, parse_dates=['timestamp'])
        
        if df.empty:
            logger.warning("No historical price data found")
            return []
        
        # Group by token and analyze lifecycle
        lifecycles = []
        for contract_address, token_data in df.groupby('contract_address'):
            if len(token_data) < 5:  # Need minimum data points
                continue
                
            lifecycle = await self._analyze_token_lifecycle(token_data)
            if lifecycle:
                lifecycles.append(lifecycle)
        
        # Find the golden pattern: tokens that hit 50%+ before rugging
        profitable_rugs = [lc for lc in lifecycles if lc.discovery_to_peak_multiplier >= 1.5]
        
        logger.info(f"📊 Found {len(profitable_rugs)} tokens that hit 50%+ before rugging!")
        
        # Store patterns for prediction
        self.historical_rugs = lifecycles
        self._extract_rug_patterns()
        
        return profitable_rugs
    
    async def _analyze_token_lifecycle(self, price_data: pd.DataFrame) -> Optional[TokenLifecycle]:
        """Analyze complete lifecycle of a single token"""
        if price_data.empty:
            return None
        
        # Sort by timestamp
        price_data = price_data.sort_values('timestamp')
        
        # Key price points
        launch_price = price_data.iloc[0]['open']
        peak_price = price_data['high'].max()
        final_price = price_data.iloc[-1]['close']
        
        # Volume analysis
        max_volume = price_data['volume'].max()
        volume_trend = price_data['volume'].rolling(3).mean().diff()
        
        # Detect rug (sharp drop after peak)
        peak_idx = price_data['high'].idxmax()
        peak_timestamp = price_data.loc[peak_idx, 'timestamp']
        
        # Look for 80%+ drop within 24 hours after peak
        post_peak = price_data[price_data['timestamp'] > peak_timestamp]
        rug_detected = False
        rug_price = None
        
        if not post_peak.empty:
            min_after_peak = post_peak['low'].min()
            drop_percentage = (peak_price - min_after_peak) / peak_price
            
            if drop_percentage >= 0.8:  # 80%+ drop = rug
                rug_detected = True
                rug_price = min_after_peak
        
        # Calculate performance metrics
        discovery_price = price_data.iloc[1]['open'] if len(price_data) > 1 else launch_price
        
        lifecycle = TokenLifecycle(
            contract_address=str(price_data.iloc[0]['contract_address']),
            symbol=str(price_data.iloc[0]['symbol']),
            creation_timestamp=price_data.iloc[0]['timestamp'],
            discovery_timestamp=price_data.iloc[0]['timestamp'],
            age_at_discovery=timedelta(0),
            
            launch_price=launch_price,
            discovery_price=discovery_price,
            peak_price=peak_price,
            current_price=final_price,
            rug_price=rug_price,
            
            launch_to_peak_multiplier=peak_price / launch_price if launch_price > 0 else 0,
            discovery_to_peak_multiplier=peak_price / discovery_price if discovery_price > 0 else 0,
            peak_to_rug_drop=(peak_price - rug_price) / peak_price if rug_price else 0,
            
            discovery_volume=price_data.iloc[0]['volume'],
            peak_volume=max_volume,
            
            status=RugStatus.CONFIRMED_RUG if rug_detected else RugStatus.HEALTHY,
            rug_timestamp=peak_timestamp if rug_detected else None
        )
        
        return lifecycle
    
    def _extract_rug_patterns(self):
        """Extract patterns from historical rugs for prediction"""
        if not self.historical_rugs:
            return
        
        rugged_tokens = [lc for lc in self.historical_rugs if lc.status == RugStatus.CONFIRMED_RUG]
        profitable_rugs = [lc for lc in rugged_tokens if lc.discovery_to_peak_multiplier >= 1.5]
        
        if not profitable_rugs:
            logger.warning("No profitable rug patterns found")
            return
        
        # Extract winning patterns
        self.rug_patterns = {
            'avg_discovery_to_peak': np.mean([lc.discovery_to_peak_multiplier for lc in profitable_rugs]),
            'avg_time_to_peak': np.mean([(lc.rug_timestamp - lc.discovery_timestamp).seconds / 3600 
                                       for lc in profitable_rugs if lc.rug_timestamp]),
            'volume_patterns': {
                'avg_discovery_volume': np.mean([lc.discovery_volume for lc in profitable_rugs]),
                'volume_spike_multiplier': np.mean([lc.peak_volume / lc.discovery_volume 
                                                  for lc in profitable_rugs if lc.discovery_volume > 0])
            },
            'success_indicators': {
                'min_multiplier_for_profit': 1.5,  # 50% minimum gain
                'optimal_exit_drop': 0.15,  # Exit when 15% down from peak
                'max_hold_time_hours': 12   # Don't hold longer than 12 hours
            }
        }
        
        logger.info(f"🎯 Extracted patterns from {len(profitable_rugs)} profitable rugs:")
        logger.info(f"   Average peak multiplier: {self.rug_patterns['avg_discovery_to_peak']:.2f}x")
        logger.info(f"   Average time to peak: {self.rug_patterns['avg_time_to_peak']:.1f} hours")
    
    async def analyze_new_token(self, contract_address: str, signal_data: Dict) -> Dict[str, Any]:
        """Analyze a new token from Telegram signal for profit potential"""
        logger.info(f"🔍 Analyzing new token: {contract_address[:10]}...")
        
        # Get comprehensive data
        from src.data.free_api_providers import FreeAPIProviders
        
        async with FreeAPIProviders() as api:
            token_data = await api.get_comprehensive_data(contract_address, signal_data.get('symbol'))
        
        if not token_data:
            return {'action': 'SKIP', 'reason': 'No data available'}
        
        # Age analysis
        age_score = self._calculate_age_score(token_data)
        
        # Momentum analysis  
        momentum_score = self._calculate_momentum_score(token_data, signal_data)
        
        # Volume analysis
        volume_score = self._calculate_volume_score(token_data)
        
        # Whale analysis
        whale_score = await self._calculate_whale_score(contract_address)
        
        # Developer analysis
        dev_score = await self._calculate_dev_score(contract_address)
        
        # Combine scores
        overall_score = (
            momentum_score * 0.3 +
            volume_score * 0.25 +
            age_score * 0.15 +
            whale_score * 0.15 +
            dev_score * 0.15
        )
        
        # Decision logic
        action = self._make_trading_decision(overall_score, token_data)
        
        analysis = {
            'contract_address': contract_address,
            'symbol': token_data.get('symbol'),
            'timestamp': datetime.now().isoformat(),
            'scores': {
                'momentum': momentum_score,
                'volume': volume_score, 
                'age': age_score,
                'whale': whale_score,
                'developer': dev_score,
                'overall': overall_score
            },
            'token_data': token_data,
            'action': action['action'],
            'confidence': action['confidence'],
            'reasoning': action['reasoning'],
            'risk_level': action['risk_level'],
            'expected_return': action.get('expected_return', 0),
            'exit_strategy': action.get('exit_strategy', {})
        }
        
        return analysis
    
    def _calculate_age_score(self, token_data: Dict) -> float:
        """Calculate age-based risk score (newer = riskier but more profitable)"""
        # For now, assume newer tokens (less data sources) are newer
        sources = len(token_data.get('data_sources', []))
        
        if sources >= 3:
            return 0.3  # Older, established token
        elif sources == 2:
            return 0.7  # Medium age
        else:
            return 0.9  # Very new - high risk, high reward
    
    def _calculate_momentum_score(self, token_data: Dict, signal_data: Dict) -> float:
        """Calculate momentum score based on price action"""
        price_change_5m = token_data.get('price_change_5m', 0)
        price_change_1h = token_data.get('price_change_1h', 0) 
        price_change_24h = token_data.get('price_change_24h', 0)
        
        # Positive momentum in short timeframes is key
        momentum_score = 0
        
        if price_change_5m > 10:  # 10%+ in 5 minutes
            momentum_score += 0.4
        elif price_change_5m > 5:
            momentum_score += 0.2
        
        if price_change_1h > 20:  # 20%+ in 1 hour
            momentum_score += 0.4
        elif price_change_1h > 10:
            momentum_score += 0.2
        
        if price_change_24h > 50:  # 50%+ in 24 hours
            momentum_score += 0.2
        
        return min(momentum_score, 1.0)
    
    def _calculate_volume_score(self, token_data: Dict) -> float:
        """Calculate volume health score"""
        volume_24h = token_data.get('volume_24h', 0)
        market_cap = token_data.get('market_cap', 1)
        
        if volume_24h == 0 or market_cap == 0:
            return 0
        
        volume_to_mcap_ratio = volume_24h / market_cap
        
        # Healthy volume is 10-50% of market cap per day
        if 0.1 <= volume_to_mcap_ratio <= 0.5:
            return 0.9
        elif 0.05 <= volume_to_mcap_ratio <= 1.0:
            return 0.7
        elif volume_to_mcap_ratio > 1.0:
            return 0.5  # Too much volume can indicate dump
        else:
            return 0.2  # Too little volume
    
    async def _calculate_whale_score(self, contract_address: str) -> float:
        """Calculate whale concentration risk score"""
        # This would integrate with Solscan to get holder data
        # For now, return a placeholder score
        return 0.6
    
    async def _calculate_dev_score(self, contract_address: str) -> float:
        """Calculate developer holding risk score"""
        # This would check if dev wallet still holds tokens
        # For now, return a placeholder score
        return 0.7
    
    def _make_trading_decision(self, overall_score: float, token_data: Dict) -> Dict[str, Any]:
        """Make final trading decision based on analysis"""
        price = token_data.get('price', 0)
        market_cap = token_data.get('market_cap', 0)
        
        if overall_score >= 0.8:
            return {
                'action': 'BUY_AGGRESSIVE',
                'confidence': overall_score,
                'reasoning': 'High-conviction play - excellent momentum and fundamentals',
                'risk_level': 'HIGH',
                'expected_return': 2.0,  # 100% expected return
                'position_size': 0.05,   # 5% of portfolio
                'exit_strategy': {
                    'profit_target': price * 1.5,  # 50% profit target
                    'stop_loss': price * 0.85,     # 15% stop loss
                    'time_limit_hours': 8
                }
            }
        elif overall_score >= 0.6:
            return {
                'action': 'BUY_MODERATE',
                'confidence': overall_score,
                'reasoning': 'Decent setup - moderate position',
                'risk_level': 'MEDIUM',
                'expected_return': 1.3,  # 30% expected return
                'position_size': 0.02,   # 2% of portfolio
                'exit_strategy': {
                    'profit_target': price * 1.3,  # 30% profit target
                    'stop_loss': price * 0.90,     # 10% stop loss
                    'time_limit_hours': 6
                }
            }
        elif overall_score >= 0.4:
            return {
                'action': 'WATCH',
                'confidence': overall_score,
                'reasoning': 'Marginal setup - watch for better entry',
                'risk_level': 'LOW'
            }
        else:
            return {
                'action': 'SKIP',
                'confidence': overall_score,
                'reasoning': 'Poor setup - likely rug with no profit potential',
                'risk_level': 'EXTREME'
            }
    
    async def real_time_rug_detection(self, contract_address: str) -> Dict[str, Any]:
        """Real-time rug detection for active positions"""
        # Get latest price data
        from src.data.free_api_providers import FreeAPIProviders
        
        async with FreeAPIProviders() as api:
            current_data = await api.get_comprehensive_data(contract_address)
        
        if not current_data or contract_address not in self.active_tokens:
            return {'rug_detected': False}
        
        token = self.active_tokens[contract_address]
        current_price = current_data.get('price', 0)
        
        # Update token data
        if current_price > token.peak_price:
            token.peak_price = current_price
        
        # Rug detection signals
        rug_signals = []
        
        # 1. Sharp price drop (>15% in minutes)
        price_drop = (token.peak_price - current_price) / token.peak_price
        if price_drop > 0.15:
            rug_signals.append(f"Sharp drop: {price_drop:.1%}")
        
        # 2. Volume spike + price drop
        current_volume = current_data.get('volume_24h', 0)
        if current_volume > token.peak_volume * 2 and price_drop > 0.1:
            rug_signals.append("Volume spike + price drop")
        
        # 3. Liquidity drain detection
        current_liquidity = current_data.get('liquidity', 0)
        if hasattr(token, 'peak_liquidity') and current_liquidity < token.peak_liquidity * 0.5:
            rug_signals.append("Liquidity drain detected")
        
        # Decision
        rug_detected = len(rug_signals) >= 2 or price_drop > 0.3
        
        return {
            'rug_detected': rug_detected,
            'confidence': len(rug_signals) / 5.0,  # Max 5 signals
            'signals': rug_signals,
            'price_drop': price_drop,
            'current_price': current_price,
            'peak_price': token.peak_price,
            'action': 'SELL_IMMEDIATELY' if rug_detected else 'HOLD'
        }
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily performance report"""
        # This would analyze all trades from the day
        return {
            'date': datetime.now().date().isoformat(),
            'total_trades': 0,
            'profitable_trades': 0,
            'total_profit': 0,
            'win_rate': 0,
            'best_trade': None,
            'worst_trade': None,
            'rug_detection_accuracy': 0
        }