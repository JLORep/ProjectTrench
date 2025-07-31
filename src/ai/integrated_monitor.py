#!/usr/bin/env python3
"""
INTEGRATED TELEGRAM MONITOR WITH AI OPTIMIZATION
Combines existing parser with real-time AI analysis
"""
import asyncio
import json
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from src.telegram.telegram_monitor import TelegramSignalMonitor, CoinSignal
from src.ai.claude_optimizer import ClaudeOptimizer
from src.data.database import CoinDatabase

class IntegratedTelegramMonitor(TelegramSignalMonitor):
    """
    Integrated monitor that combines existing Telegram parsing 
    with real-time AI optimization pipeline
    """
    
    def __init__(self, db: CoinDatabase, webhook_url: str = "http://localhost:8000/webhook/telegram-signal"):
        super().__init__(db)
        self.webhook_url = webhook_url
        self.optimizer = ClaudeOptimizer()
        self.session = None
        
    async def start_integrated_monitoring(self):
        """Start integrated monitoring with AI pipeline"""
        logger.info("🤖 Starting integrated Telegram monitoring with AI optimization")
        
        # Initialize HTTP session for webhook calls
        self.session = aiohttp.ClientSession()
        
        # Start the original Telegram monitoring
        await self.start()
    
    async def _process_high_confidence_signal(self, signal: CoinSignal):
        """Override to add AI optimization to high confidence signals"""
        
        # Call parent method for existing logic
        await super()._process_high_confidence_signal(signal)
        
        # Convert CoinSignal to webhook format and add AI analysis
        webhook_signal = await self._convert_signal_for_ai(signal)
        
        # Send to AI pipeline
        await self._send_to_webhook(webhook_signal)
    
    async def _convert_signal_for_ai(self, signal: CoinSignal) -> Dict[str, Any]:
        """Convert CoinSignal to format expected by AI pipeline"""
        
        # Extract market data from the parsed signal
        market_context = self._analyze_signal_context(signal)
        
        webhook_signal = {
            'symbol': signal.ticker.replace('$', '') if signal.ticker else 'UNKNOWN',
            'contract_address': signal.contract_address,
            'source': f"telegram_{signal.channel_name}",
            'signal_type': signal.signal_type,
            'raw_message': signal.raw_message,
            'timestamp': signal.timestamp.isoformat(),
            'confidence': signal.confidence,
            
            # Enhanced data from existing parser
            'entry_price': signal.entry_price,
            'targets': signal.target_prices,
            'stop_loss': signal.stop_loss,
            'channel_metadata': {
                'channel_id': signal.channel_id,
                'channel_name': signal.channel_name,
                'message_id': signal.message_id,
                'views': signal.metadata.get('views'),
                'has_media': signal.metadata.get('has_media'),
                'reactions': signal.metadata.get('reactions', [])
            },
            
            # Market context analysis
            'market_context': market_context,
            
            # AI preprocessing hints
            'preprocessing': {
                'sentiment': self._analyze_message_sentiment(signal.raw_message),
                'urgency': self._detect_urgency_level(signal.raw_message),
                'credibility': self._assess_channel_credibility(signal.channel_name),
                'signal_strength': self._calculate_signal_strength(signal)
            }
        }
        
        return webhook_signal
    
    def _analyze_signal_context(self, signal: CoinSignal) -> Dict[str, Any]:
        """Analyze the context around the signal for AI optimization"""
        
        context = {
            'has_contract': bool(signal.contract_address),
            'has_targets': len(signal.target_prices) > 0,
            'has_stop_loss': signal.stop_loss is not None,
            'has_entry_price': signal.entry_price is not None,
            'channel_engagement': {
                'views': signal.metadata.get('views', 0),
                'reactions_count': len(signal.metadata.get('reactions', [])),
                'has_media': signal.metadata.get('has_media', False)
            },
            'message_structure': {
                'length': len(signal.raw_message),
                'has_emojis': any(ord(c) > 127 for c in signal.raw_message),
                'has_formatting': any(marker in signal.raw_message for marker in ['**', '__', '`']),
                'urgency_indicators': sum(1 for indicator in ['NOW', 'URGENT', '!!!', '⚡'] 
                                       if indicator in signal.raw_message.upper())
            }
        }
        
        return context
    
    def _analyze_message_sentiment(self, message: str) -> str:
        """Analyze message sentiment"""
        message_lower = message.lower()
        
        bullish_indicators = ['🚀', 'moon', 'pump', 'gem', '💎', 'rocket', 'x100', 'breakout', 'bull']
        bearish_indicators = ['dump', 'crash', 'rug', 'scam', 'warning', '📉', 'bear']
        
        bullish_count = sum(1 for indicator in bullish_indicators if indicator in message_lower)
        bearish_count = sum(1 for indicator in bearish_indicators if indicator in message_lower)
        
        if bullish_count > bearish_count:
            return 'bullish'
        elif bearish_count > bullish_count:
            return 'bearish'
        else:
            return 'neutral'
    
    def _detect_urgency_level(self, message: str) -> str:
        """Detect urgency level in message"""
        message_upper = message.upper()
        
        high_urgency = ['NOW', 'URGENT', 'ASAP', 'IMMEDIATE', 'QUICK', 'FAST']
        medium_urgency = ['SOON', 'TODAY', 'ALERT', '!!!']
        
        high_count = sum(1 for indicator in high_urgency if indicator in message_upper)
        medium_count = sum(1 for indicator in medium_urgency if indicator in message_upper)
        
        if high_count >= 2 or any(indicator in message_upper for indicator in ['⚡', '🔥', '💥']):
            return 'high'
        elif high_count >= 1 or medium_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _assess_channel_credibility(self, channel_name: str) -> float:
        """Assess channel credibility based on name"""
        
        # High credibility channels
        premium_channels = ['atm.day', 'premium', 'vip', 'elite', 'pro']
        medium_channels = ['gems', 'signals', 'alerts', 'crypto']
        low_channels = ['pump', 'dump', 'moon', 'shill']
        
        channel_lower = channel_name.lower()
        
        if any(premium in channel_lower for premium in premium_channels):
            return 0.9
        elif any(medium in channel_lower for medium in medium_channels):
            return 0.6
        elif any(low in channel_lower for low in low_channels):
            return 0.3
        else:
            return 0.5  # Default credibility
    
    def _calculate_signal_strength(self, signal: CoinSignal) -> float:
        """Calculate overall signal strength"""
        strength = signal.confidence  # Start with existing confidence
        
        # Boost for complete signals
        if signal.contract_address:
            strength += 0.1
        if signal.target_prices:
            strength += 0.1
        if signal.stop_loss:
            strength += 0.05
        if signal.entry_price:
            strength += 0.05
        
        # Boost for engagement
        views = signal.metadata.get('views', 0)
        if views > 1000:
            strength += 0.05
        if views > 10000:
            strength += 0.1
        
        return min(strength, 1.0)
    
    async def _send_to_webhook(self, signal: Dict[str, Any]):
        """Send enhanced signal to AI webhook"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            logger.info(f"🔗 Sending signal to AI pipeline: {signal.get('symbol')}")
            
            async with self.session.post(
                self.webhook_url,
                json=signal,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ AI pipeline processed: {result.get('message')}")
                    
                    # Store AI result for tracking
                    await self._store_ai_result(signal, result)
                else:
                    logger.error(f"❌ AI webhook error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error sending to AI webhook: {e}")
    
    async def _store_ai_result(self, signal: Dict, ai_result: Dict):
        """Store AI processing results for analysis"""
        result_record = {
            'timestamp': datetime.now().isoformat(),
            'symbol': signal.get('symbol'),
            'contract_address': signal.get('contract_address'),
            'original_confidence': signal.get('confidence'),
            'ai_processing_status': ai_result.get('status'),
            'channel': signal.get('channel_metadata', {}).get('channel_name')
        }
        
        # Store in database or file for tracking
        with open('ai_processing_log.jsonl', 'a') as f:
            f.write(json.dumps(result_record) + '\n')
    
    async def get_ai_performance_stats(self) -> Dict[str, Any]:
        """Get AI processing performance statistics"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(
                "http://localhost:8000/ai/performance",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"API error: {response.status}"}
                    
        except Exception as e:
            return {"error": f"Connection error: {e}"}
    
    async def close(self):
        """Clean up resources"""
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        # Call parent cleanup
        await super().close()

# Factory function to create integrated monitor
def create_integrated_monitor(db: CoinDatabase, webhook_url: str = None) -> IntegratedTelegramMonitor:
    """Factory function to create integrated monitor"""
    webhook_url = webhook_url or "http://localhost:8000/webhook/telegram-signal"
    return IntegratedTelegramMonitor(db, webhook_url)

# Standalone function to run integrated monitoring
async def run_integrated_monitoring():
    """Run the integrated monitoring system"""
    from src.data.database import CoinDatabase
    
    db = CoinDatabase()
    monitor = create_integrated_monitor(db)
    
    # Add some test channels (replace with real channel IDs)
    test_channels = [
        -1001234567890,  # Replace with actual channel ID
        -1001234567891,  # Replace with actual channel ID
    ]
    
    for channel_id in test_channels:
        success = await monitor.add_channel(channel_id)
        if success:
            logger.info(f"Added channel {channel_id} to monitoring")
        else:
            logger.warning(f"Failed to add channel {channel_id}")
    
    try:
        # Start integrated monitoring
        await monitor.start_integrated_monitoring()
        
        # Keep monitoring until interrupted
        while True:
            await asyncio.sleep(60)
            
            # Periodic stats
            stats = await monitor.get_ai_performance_stats()
            if 'error' not in stats:
                logger.info(f"AI Performance: {stats}")
                
    except KeyboardInterrupt:
        logger.info("Stopping integrated monitoring...")
    finally:
        await monitor.close()

if __name__ == "__main__":
    asyncio.run(run_integrated_monitoring())