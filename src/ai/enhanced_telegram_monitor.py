#!/usr/bin/env python3
"""
ENHANCED TELEGRAM MONITOR WITH AI INTEGRATION
Real-time signal detection with instant AI optimization
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
import re

from src.telegram.telegram_monitor import TelegramSignalMonitor
from src.ai.claude_optimizer import ClaudeOptimizer

class EnhancedTelegramMonitor(TelegramSignalMonitor):
    """
    Enhanced Telegram monitor with real-time AI optimization
    """
    
    def __init__(self, db, webhook_url: str = "http://localhost:8000/webhook/telegram-signal"):
        super().__init__(db)
        self.webhook_url = webhook_url
        self.optimizer = ClaudeOptimizer()
        self.session = None
        self.processed_messages = set()
        
    async def start_enhanced_monitoring(self):
        """Start enhanced monitoring with AI pipeline"""
        logger.info("🤖 Starting enhanced Telegram monitoring with AI optimization")
        
        self.session = aiohttp.ClientSession()
        
        # Simulate monitoring channels (in production, would use Telethon)
        await self._simulate_channel_monitoring()
    
    async def _simulate_channel_monitoring(self):
        """Simulate monitoring Telegram channels"""
        # Test signals for demonstration
        test_signals = [
            {
                "raw_message": "🚀 PEPE is pumping! Contract: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\nTarget: $0.000020\nSL: $0.000008",
                "channel": "atm.day",
                "timestamp": datetime.now().isoformat()
            },
            {
                "raw_message": "New gem found 💎 BONK\nCA: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263\nMC: $500K\nLiq: $50K locked",
                "channel": "crypto_gems",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        for test_msg in test_signals:
            await self._process_message(test_msg)
            await asyncio.sleep(5)  # Wait between signals
    
    async def _process_message(self, message_data: Dict):
        """Process incoming Telegram message with AI enhancement"""
        try:
            raw_message = message_data.get('raw_message', '')
            message_id = hash(raw_message + str(message_data.get('timestamp')))
            
            # Skip if already processed
            if message_id in self.processed_messages:
                return
            
            self.processed_messages.add(message_id)
            
            logger.info(f"📱 Processing message from {message_data.get('channel')}")
            
            # Parse signal using existing logic
            parsed_signal = await self.parse_signal(raw_message)
            
            if not parsed_signal:
                logger.info("⏭️ No valid signal found in message")
                return
            
            # Enhance with AI preprocessing
            enhanced_signal = await self._enhance_signal_with_ai(
                parsed_signal, 
                message_data
            )
            
            # Send to webhook for processing
            await self._send_to_webhook(enhanced_signal)
            
        except Exception as e:
            logger.error(f"Message processing error: {e}")
    
    async def _enhance_signal_with_ai(self, signal: Dict, message_data: Dict) -> Dict:
        """Enhance signal with AI preprocessing"""
        
        # Extract additional context
        enhanced = {
            **signal,
            'source_channel': message_data.get('channel'),
            'raw_message': message_data.get('raw_message'),
            'message_timestamp': message_data.get('timestamp'),
            'preprocessing': {
                'sentiment': self._analyze_sentiment(message_data.get('raw_message', '')),
                'urgency': self._detect_urgency(message_data.get('raw_message', '')),
                'credibility': self._assess_credibility(message_data.get('channel', '')),
                'signal_strength': self._calculate_signal_strength(signal)
            }
        }
        
        return enhanced
    
    def _analyze_sentiment(self, message: str) -> str:
        """Analyze message sentiment"""
        bullish_words = ['🚀', 'moon', 'pump', 'gem', '💎', 'rocket', 'x100', 'breakout']
        bearish_words = ['dump', 'crash', 'rug', 'scam', 'warning', '📉']
        
        message_lower = message.lower()
        
        bullish_count = sum(1 for word in bullish_words if word in message_lower)
        bearish_count = sum(1 for word in bearish_words if word in message_lower)
        
        if bullish_count > bearish_count:
            return 'bullish'
        elif bearish_count > bullish_count:
            return 'bearish'
        else:
            return 'neutral'
    
    def _detect_urgency(self, message: str) -> str:
        """Detect urgency level"""
        urgent_indicators = ['NOW', 'URGENT', 'FAST', 'QUICK', '⚡', 'ASAP', '!!!']
        
        message_upper = message.upper()
        urgent_count = sum(1 for indicator in urgent_indicators if indicator in message_upper)
        
        if urgent_count >= 2:
            return 'high'
        elif urgent_count == 1:
            return 'medium'
        else:
            return 'low'
    
    def _assess_credibility(self, channel: str) -> float:
        """Assess channel credibility"""
        credibility_scores = {
            'atm.day': 0.9,
            'crypto_gems': 0.7,
            'moonshots': 0.5,
            'unknown': 0.3
        }
        
        return credibility_scores.get(channel, 0.3)
    
    def _calculate_signal_strength(self, signal: Dict) -> float:
        """Calculate overall signal strength"""
        strength = 0.5  # Base strength
        
        # Has targets
        if signal.get('targets'):
            strength += 0.2
        
        # Has stop loss
        if signal.get('stop_loss'):
            strength += 0.1
        
        # Has contract address
        if signal.get('contract_address'):
            strength += 0.2
        
        return min(strength, 1.0)
    
    async def _send_to_webhook(self, signal: Dict):
        """Send enhanced signal to webhook for AI processing"""
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
                    logger.info(f"✅ Signal processed: {result.get('message')}")
                else:
                    logger.error(f"❌ Webhook error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Webhook send error: {e}")
    
    async def parse_signal(self, message: str) -> Optional[Dict]:
        """Enhanced signal parsing with more patterns"""
        
        # Extract contract address
        contract_patterns = [
            r'(?i)(?:contract|ca|address)[:=\s]*([A-Za-z0-9]{32,44})',
            r'([A-Za-z0-9]{32,44})',  # Standalone addresses
        ]
        
        contract_address = None
        for pattern in contract_patterns:
            match = re.search(pattern, message)
            if match:
                potential_address = match.group(1)
                if len(potential_address) >= 32:  # Likely a valid address
                    contract_address = potential_address
                    break
        
        # Extract symbol
        symbol_patterns = [
            r'\\$([A-Z]{2,10})',  # $SYMBOL
            r'([A-Z]{2,10})\\s+(?:is|contract|ca)',  # SYMBOL is/contract/ca
            r'(?:^|\\s)([A-Z]{2,10})(?:\\s|$)',  # Standalone symbols
        ]
        
        symbol = None
        for pattern in symbol_patterns:
            match = re.search(pattern, message)
            if match:
                symbol = match.group(1)
                break
        
        # Extract targets
        target_patterns = [
            r'(?i)target[:=\\s]*(\\$?[0-9.]+)',
            r'(?i)tp[:=\\s]*(\\$?[0-9.]+)',
            r'(?i)take\\s*profit[:=\\s]*(\\$?[0-9.]+)'
        ]
        
        targets = []
        for pattern in target_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                try:
                    price = float(match.replace('$', ''))
                    targets.append(price)
                except ValueError:
                    continue
        
        # Extract stop loss
        sl_patterns = [
            r'(?i)(?:stop\\s*loss|sl)[:=\\s]*(\\$?[0-9.]+)',
            r'(?i)stoploss[:=\\s]*(\\$?[0-9.]+)'
        ]
        
        stop_loss = None
        for pattern in sl_patterns:
            match = re.search(pattern, message)
            if match:
                try:
                    stop_loss = float(match.group(1).replace('$', ''))
                    break
                except ValueError:
                    continue
        
        # Must have at least contract or symbol
        if not contract_address and not symbol:
            return None
        
        return {
            'symbol': symbol,
            'contract_address': contract_address,
            'targets': targets,
            'stop_loss': stop_loss,
            'confidence': self._calculate_parse_confidence(symbol, contract_address, targets, stop_loss),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_parse_confidence(self, symbol, contract, targets, stop_loss) -> float:
        """Calculate parsing confidence"""
        confidence = 0.0
        
        if symbol:
            confidence += 0.3
        if contract:
            confidence += 0.4
        if targets:
            confidence += 0.2
        if stop_loss:
            confidence += 0.1
        
        return confidence
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

# Standalone function to run enhanced monitoring
async def run_enhanced_monitoring():
    """Run the enhanced monitoring system"""
    from src.data.database import CoinDatabase
    
    db = CoinDatabase()
    monitor = EnhancedTelegramMonitor(db)
    
    try:
        await monitor.start_enhanced_monitoring()
    except KeyboardInterrupt:
        logger.info("Stopping enhanced monitoring...")
    finally:
        await monitor.close()

if __name__ == "__main__":
    asyncio.run(run_enhanced_monitoring())