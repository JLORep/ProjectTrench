"""
📡 Alpha Radar System - AI-Powered Signal Generation
Real-time alpha detection and emotionless trading signals for TrenchCoat Pro
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from collections import deque
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalType(Enum):
    VOLUME_SPIKE = "🚀 Volume Spike"
    WHALE_BUY = "🐋 Whale Buy"
    BREAKOUT = "📈 Breakout"
    SOCIAL_BUZZ = "🔥 Social Buzz"
    SMART_MONEY = "🧠 Smart Money"
    MOMENTUM = "⚡ Momentum"
    REVERSAL = "🔄 Reversal"
    ACCUMULATION = "📊 Accumulation"

class SignalAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    WATCH = "WATCH"
    AVOID = "AVOID"

@dataclass
class AlphaSignal:
    """Represents an alpha trading signal"""
    id: str
    timestamp: datetime
    type: SignalType
    token_symbol: str
    token_address: str
    confidence: float  # 0-100
    action: SignalAction
    message: str
    rationale: List[str]
    risk_factors: List[str] = field(default_factory=list)
    opportunity_factors: List[str] = field(default_factory=list)
    target_multiplier: float = 2.0
    time_horizon: str = "24h"
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Dict = field(default_factory=dict)

class AlphaDetector:
    """Detects alpha opportunities from market data"""
    
    def __init__(self):
        self.volume_baseline = {}
        self.price_history = {}
        self.social_sentiment = {}
        
    async def detect_volume_spike(self, token_data: Dict, 
                                 historical_data: List[Dict]) -> Optional[AlphaSignal]:
        """Detect unusual volume spikes"""
        try:
            current_volume = token_data.get('volume_24h', 0)
            symbol = token_data.get('symbol', 'UNKNOWN')
            
            # Calculate baseline from historical data
            if historical_data and len(historical_data) > 5:
                avg_volume = np.mean([d.get('volume', 0) for d in historical_data[-20:]])
                
                if avg_volume > 0:
                    volume_ratio = current_volume / avg_volume
                    
                    if volume_ratio > 3.0:  # 300% spike
                        confidence = min(95, 50 + (volume_ratio - 3) * 10)
                        
                        return AlphaSignal(
                            id=f"vol_{symbol}_{int(time.time())}",
                            timestamp=datetime.now(),
                            type=SignalType.VOLUME_SPIKE,
                            token_symbol=symbol,
                            token_address=token_data.get('address', ''),
                            confidence=confidence,
                            action=SignalAction.BUY if volume_ratio > 5 else SignalAction.WATCH,
                            message=f"Volume +{int(volume_ratio * 100)}% in last period",
                            rationale=[
                                f"Volume spike {volume_ratio:.1f}x above average",
                                "Increased market interest detected",
                                "Potential breakout or news catalyst"
                            ],
                            risk_factors=[
                                "Possible pump and dump" if volume_ratio > 10 else "Elevated volatility"
                            ],
                            opportunity_factors=[
                                "Early momentum detection",
                                "Institutional interest possible"
                            ],
                            target_multiplier=min(5.0, 1 + volume_ratio / 3),
                            time_horizon="4-24h"
                        )
                        
        except Exception as e:
            logger.error(f"Error detecting volume spike: {e}")
            
        return None
    
    async def detect_whale_activity(self, token_data: Dict, 
                                   transaction_data: List[Dict]) -> Optional[AlphaSignal]:
        """Detect whale buying activity"""
        try:
            symbol = token_data.get('symbol', 'UNKNOWN')
            
            # Analyze recent large transactions
            whale_txs = [tx for tx in transaction_data 
                        if tx.get('value_usd', 0) > 50000]  # $50k+ transactions
            
            if whale_txs:
                buy_txs = [tx for tx in whale_txs if tx.get('type') == 'buy']
                
                if len(buy_txs) >= 3:  # Multiple whale buys
                    total_whale_volume = sum(tx.get('value_usd', 0) for tx in buy_txs)
                    confidence = min(90, 60 + len(buy_txs) * 5)
                    
                    return AlphaSignal(
                        id=f"whale_{symbol}_{int(time.time())}",
                        timestamp=datetime.now(),
                        type=SignalType.WHALE_BUY,
                        token_symbol=symbol,
                        token_address=token_data.get('address', ''),
                        confidence=confidence,
                        action=SignalAction.BUY,
                        message=f"{len(buy_txs)} whales bought ${total_whale_volume/1000:.0f}k total",
                        rationale=[
                            f"Smart money accumulation detected",
                            f"{len(buy_txs)} whale wallets buying",
                            "Institutional confidence signal"
                        ],
                        risk_factors=[
                            "Possible coordinated pump" if len(buy_txs) > 10 else "Large holder concentration"
                        ],
                        opportunity_factors=[
                            "Follow smart money",
                            "Reduced downside risk with whale support"
                        ],
                        target_multiplier=3.0,
                        time_horizon="12-48h"
                    )
                    
        except Exception as e:
            logger.error(f"Error detecting whale activity: {e}")
            
        return None
    
    async def detect_breakout(self, token_data: Dict, 
                             price_data: List[Dict]) -> Optional[AlphaSignal]:
        """Detect technical breakouts"""
        try:
            symbol = token_data.get('symbol', 'UNKNOWN')
            current_price = token_data.get('price', 0)
            
            if price_data and len(price_data) > 20:
                prices = [p.get('price', 0) for p in price_data[-50:]]
                
                # Calculate resistance levels
                resistance = np.percentile(prices, 90)
                support = np.percentile(prices, 10)
                
                if current_price > resistance * 1.05:  # 5% above resistance
                    momentum = (current_price - prices[-20]) / prices[-20] * 100
                    confidence = min(85, 60 + abs(momentum))
                    
                    return AlphaSignal(
                        id=f"break_{symbol}_{int(time.time())}",
                        timestamp=datetime.now(),
                        type=SignalType.BREAKOUT,
                        token_symbol=symbol,
                        token_address=token_data.get('address', ''),
                        confidence=confidence,
                        action=SignalAction.BUY if momentum > 20 else SignalAction.WATCH,
                        message=f"Breaking resistance at ${resistance:.8f}",
                        rationale=[
                            "Technical breakout confirmed",
                            f"Momentum: {momentum:.1f}%",
                            "Clear skies above resistance"
                        ],
                        risk_factors=[
                            "False breakout possible" if momentum < 10 else "Overbought conditions"
                        ],
                        opportunity_factors=[
                            "Trend continuation likely",
                            "Stop loss can be tight at resistance"
                        ],
                        target_multiplier=2.5,
                        time_horizon="6-24h",
                        entry_price=current_price,
                        stop_loss=resistance * 0.98,
                        take_profit=current_price * 2.5
                    )
                    
        except Exception as e:
            logger.error(f"Error detecting breakout: {e}")
            
        return None
    
    async def detect_social_buzz(self, token_data: Dict, 
                                social_data: Dict) -> Optional[AlphaSignal]:
        """Detect social media momentum"""
        try:
            symbol = token_data.get('symbol', 'UNKNOWN')
            
            twitter_mentions = social_data.get('twitter_mentions_1h', 0)
            telegram_growth = social_data.get('telegram_member_growth_24h', 0)
            influencer_mentions = social_data.get('kol_mentions', 0)
            
            social_score = (
                twitter_mentions * 0.4 + 
                telegram_growth * 0.3 + 
                influencer_mentions * 30
            )
            
            if social_score > 100:
                confidence = min(80, 50 + social_score / 10)
                
                return AlphaSignal(
                    id=f"social_{symbol}_{int(time.time())}",
                    timestamp=datetime.now(),
                    type=SignalType.SOCIAL_BUZZ,
                    token_symbol=symbol,
                    token_address=token_data.get('address', ''),
                    confidence=confidence,
                    action=SignalAction.BUY if social_score > 200 else SignalAction.WATCH,
                    message=f"Social explosion: {int(social_score)} score",
                    rationale=[
                        f"{twitter_mentions} Twitter mentions in 1h",
                        f"{telegram_growth} new Telegram members",
                        "Viral momentum building"
                    ],
                    risk_factors=[
                        "FOMO-driven pump risk",
                        "Sentiment can reverse quickly"
                    ],
                    opportunity_factors=[
                        "Retail interest surge",
                        "Potential mainstream breakout"
                    ],
                    target_multiplier=4.0,
                    time_horizon="2-12h"
                )
                
        except Exception as e:
            logger.error(f"Error detecting social buzz: {e}")
            
        return None

class EmotionlessAI:
    """AI system for emotionless signal analysis"""
    
    def __init__(self):
        self.signal_history = deque(maxlen=1000)
        self.performance_tracker = {}
        
    def analyze_signal(self, signal: AlphaSignal, 
                      market_context: Dict) -> Dict:
        """Provide emotionless AI analysis of signal"""
        
        # Calculate objective metrics
        risk_score = self._calculate_risk_score(signal, market_context)
        opportunity_score = self._calculate_opportunity_score(signal, market_context)
        
        # Generate pros and cons
        pros = []
        cons = []
        
        # Objective pros
        if signal.confidence > 80:
            pros.append(f"High confidence signal ({signal.confidence}%)")
        if opportunity_score > 70:
            pros.append("Strong opportunity metrics")
        if len(signal.opportunity_factors) > 2:
            pros.append("Multiple positive catalysts")
            
        # Objective cons
        if risk_score > 60:
            cons.append(f"Elevated risk profile ({risk_score}%)")
        if market_context.get('btc_correlation', 0) > 0.8:
            cons.append("High BTC correlation risk")
        if len(signal.risk_factors) > 1:
            cons.append("Multiple risk factors present")
            
        # Decision logic
        if opportunity_score > risk_score * 1.5 and signal.confidence > 70:
            recommendation = "EXECUTE"
            position_size = min(0.1, 0.02 * (opportunity_score / risk_score))
        elif opportunity_score > risk_score:
            recommendation = "CONSIDER"
            position_size = 0.05
        else:
            recommendation = "PASS"
            position_size = 0
            
        return {
            "recommendation": recommendation,
            "position_size_sol": position_size,
            "risk_score": risk_score,
            "opportunity_score": opportunity_score,
            "pros": pros,
            "cons": cons,
            "objective_summary": self._generate_summary(signal, risk_score, opportunity_score),
            "suggested_params": {
                "entry": signal.entry_price,
                "stop_loss": signal.stop_loss or signal.entry_price * 0.9,
                "take_profit": signal.take_profit or signal.entry_price * signal.target_multiplier,
                "time_limit": signal.time_horizon
            }
        }
    
    def _calculate_risk_score(self, signal: AlphaSignal, context: Dict) -> float:
        """Calculate objective risk score 0-100"""
        risk = 0
        
        # Signal-specific risks
        risk += len(signal.risk_factors) * 10
        risk += max(0, 100 - signal.confidence) * 0.3
        
        # Market context risks
        if context.get('market_sentiment') == 'BEARISH':
            risk += 20
        if context.get('volatility_index', 0) > 80:
            risk += 15
            
        # Type-specific risks
        if signal.type == SignalType.SOCIAL_BUZZ:
            risk += 15  # Higher risk for social-driven
        elif signal.type == SignalType.WHALE_BUY:
            risk -= 10  # Lower risk with whale support
            
        return min(100, max(0, risk))
    
    def _calculate_opportunity_score(self, signal: AlphaSignal, context: Dict) -> float:
        """Calculate objective opportunity score 0-100"""
        score = signal.confidence * 0.5
        
        # Opportunity factors
        score += len(signal.opportunity_factors) * 10
        score += min(30, signal.target_multiplier * 10)
        
        # Market alignment
        if context.get('market_sentiment') == 'BULLISH':
            score += 15
        if context.get('sector_momentum', 0) > 50:
            score += 10
            
        # Historical performance of signal type
        historical_success = self.performance_tracker.get(signal.type, {}).get('win_rate', 0.5)
        score += historical_success * 20
        
        return min(100, max(0, score))
    
    def _generate_summary(self, signal: AlphaSignal, risk: float, opp: float) -> str:
        """Generate emotionless summary"""
        risk_level = "Low" if risk < 40 else "Medium" if risk < 70 else "High"
        opp_level = "Strong" if opp > 70 else "Moderate" if opp > 40 else "Weak"
        
        return (f"{signal.type.value} signal with {signal.confidence}% confidence. "
                f"Risk: {risk_level} ({risk:.0f}%). Opportunity: {opp_level} ({opp:.0f}%). "
                f"Target: {signal.target_multiplier}x in {signal.time_horizon}.")

class AlphaRadarSystem:
    """Main Alpha Radar system orchestrator"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.detector = AlphaDetector()
        self.ai = EmotionlessAI()
        self.signals = deque(maxlen=100)
        self.active_signals = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def start(self):
        """Start the Alpha Radar system"""
        self.session = aiohttp.ClientSession()
        
        # Start monitoring tasks
        tasks = [
            self._monitor_tokens(),
            self._process_signals(),
            self._track_performance()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _monitor_tokens(self):
        """Monitor tokens for alpha signals"""
        while True:
            try:
                # Get token data from various sources
                tokens = await self._fetch_trending_tokens()
                
                for token in tokens:
                    # Get additional data
                    historical = await self._fetch_historical_data(token['address'])
                    transactions = await self._fetch_transactions(token['address'])
                    social = await self._fetch_social_data(token['symbol'])
                    
                    # Run detectors
                    signals = await asyncio.gather(
                        self.detector.detect_volume_spike(token, historical),
                        self.detector.detect_whale_activity(token, transactions),
                        self.detector.detect_breakout(token, historical),
                        self.detector.detect_social_buzz(token, social)
                    )
                    
                    # Process valid signals
                    for signal in signals:
                        if signal and signal.confidence > self.config.get('min_confidence', 60):
                            await self._add_signal(signal)
                            
            except Exception as e:
                logger.error(f"Error in token monitoring: {e}")
                
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def _add_signal(self, signal: AlphaSignal):
        """Add a new signal to the system"""
        # Get market context
        market_context = await self._get_market_context()
        
        # AI analysis
        analysis = self.ai.analyze_signal(signal, market_context)
        signal.metadata['ai_analysis'] = analysis
        
        # Add to queue
        self.signals.append(signal)
        self.active_signals[signal.id] = signal
        
        # Log high-confidence signals
        if signal.confidence > 80:
            logger.info(f"🎯 HIGH CONFIDENCE: {signal.token_symbol} - "
                       f"{signal.type.value} - {analysis['recommendation']}")
    
    async def _process_signals(self):
        """Process and execute signals"""
        while True:
            try:
                # Process active signals
                for signal_id, signal in list(self.active_signals.items()):
                    # Check if signal expired
                    if datetime.now() - signal.timestamp > timedelta(hours=24):
                        del self.active_signals[signal_id]
                        continue
                        
                    # Update signal status
                    await self._update_signal_status(signal)
                    
            except Exception as e:
                logger.error(f"Error processing signals: {e}")
                
            await asyncio.sleep(60)  # Process every minute
    
    async def _track_performance(self):
        """Track signal performance for learning"""
        while True:
            try:
                # Track completed signals
                for signal in list(self.signals):
                    if signal.metadata.get('completed'):
                        # Update performance metrics
                        signal_type = signal.type
                        if signal_type not in self.ai.performance_tracker:
                            self.ai.performance_tracker[signal_type] = {
                                'total': 0,
                                'wins': 0,
                                'total_return': 0
                            }
                            
                        tracker = self.ai.performance_tracker[signal_type]
                        tracker['total'] += 1
                        
                        if signal.metadata.get('profit', 0) > 0:
                            tracker['wins'] += 1
                        tracker['total_return'] += signal.metadata.get('return', 0)
                        tracker['win_rate'] = tracker['wins'] / tracker['total']
                        
            except Exception as e:
                logger.error(f"Error tracking performance: {e}")
                
            await asyncio.sleep(300)  # Update every 5 minutes
    
    async def _fetch_trending_tokens(self) -> List[Dict]:
        """Fetch trending tokens from multiple sources"""
        # Implementation would fetch from DexScreener, etc.
        return []
    
    async def _fetch_historical_data(self, address: str) -> List[Dict]:
        """Fetch historical price data"""
        return []
    
    async def _fetch_transactions(self, address: str) -> List[Dict]:
        """Fetch recent transactions"""
        return []
    
    async def _fetch_social_data(self, symbol: str) -> Dict:
        """Fetch social media data"""
        return {}
    
    async def _get_market_context(self) -> Dict:
        """Get overall market context"""
        return {
            'market_sentiment': 'NEUTRAL',
            'volatility_index': 50,
            'btc_correlation': 0.7,
            'sector_momentum': 60
        }
    
    async def _update_signal_status(self, signal: AlphaSignal):
        """Update signal with current status"""
        # Would check current price vs entry/targets
        pass
    
    async def get_active_signals(self, 
                               min_confidence: Optional[float] = None,
                               signal_types: Optional[List[SignalType]] = None) -> List[AlphaSignal]:
        """Get filtered active signals"""
        signals = list(self.active_signals.values())
        
        if min_confidence:
            signals = [s for s in signals if s.confidence >= min_confidence]
            
        if signal_types:
            signals = [s for s in signals if s.type in signal_types]
            
        # Sort by confidence
        return sorted(signals, key=lambda s: s.confidence, reverse=True)
    
    async def stop(self):
        """Stop the Alpha Radar system"""
        if self.session:
            await self.session.close()

# Export main components
__all__ = ['AlphaRadarSystem', 'AlphaSignal', 'SignalType', 'SignalAction', 'EmotionlessAI']