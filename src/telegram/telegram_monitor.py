import asyncio
import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityBold, MessageEntityItalic, MessageEntityCode
import aiohttp
from loguru import logger
import pandas as pd
from src.data.database import CoinDatabase
from config.config import settings

@dataclass
class CoinSignal:
    ticker: str
    contract_address: str
    signal_type: str  # BUY, SELL, HOLD, ALERT
    entry_price: Optional[float] = None
    target_prices: List[float] = field(default_factory=list)
    stop_loss: Optional[float] = None
    confidence: float = 0.5
    reasoning: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    channel_name: str = ""
    channel_id: int = 0
    message_id: int = 0
    raw_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class SignalPattern:
    """Advanced pattern matching for crypto signals"""
    
    # Sophisticated regex patterns for signal detection
    BUY_PATTERNS = [
        r"(?i)(?:🚀|💎|🔥|⚡)?\s*(?:buy|long|accumulate|entry|dip\s*buy|ape)\s*(?:signal|alert|zone|now)?",
        r"(?i)(?:strong\s*)?buy\s*(?:recommendation|signal|alert)",
        r"(?i)entry\s*(?:point|zone|price)?\s*[:=]?\s*\$?(\d+\.?\d*)",
        r"(?i)(?:gem|moonshot|100x|rocket|pump)\s*(?:alert|incoming|potential)?",
    ]
    
    SELL_PATTERNS = [
        r"(?i)(?:🔴|⚠️|📉)?\s*(?:sell|short|exit|take\s*profit|tp\s*hit)",
        r"(?i)(?:exit|close)\s*(?:position|trade|signal)",
        r"(?i)target\s*(?:reached|hit|achieved)",
    ]
    
    CONTRACT_PATTERNS = [
        r"(?:CA|Contract|Address|Token)[\s:]*([A-Za-z0-9]{32,44})",
        r"pump\.fun/([A-Za-z0-9]{32,44})",
        r"dexscreener\.com/solana/([A-Za-z0-9]{32,44})",
        r"birdeye\.so/token/([A-Za-z0-9]{32,44})",
    ]
    
    PRICE_PATTERNS = [
        r"(?i)(?:price|current|now|@)\s*[:=]?\s*\$?(\d+\.?\d*)",
        r"(?i)(?:entry|buy)\s*(?:zone|price|@)?\s*[:=]?\s*\$?(\d+\.?\d*)",
    ]
    
    TARGET_PATTERNS = [
        r"(?i)(?:target|tp|take\s*profit)\s*\d?\s*[:=]?\s*\$?(\d+\.?\d*)",
        r"(?i)(?:🎯|🔴)\s*\$?(\d+\.?\d*)",
    ]
    
    STOP_LOSS_PATTERNS = [
        r"(?i)(?:stop\s*loss|sl|stop)\s*[:=]?\s*\$?(\d+\.?\d*)",
        r"(?i)(?:risk|invalidation)\s*[:=]?\s*\$?(\d+\.?\d*)",
    ]

class TelegramSignalMonitor:
    def __init__(self, db: CoinDatabase, session_name: str = "trench_monitor"):
        self.db = db
        self.client = None
        self.session_name = session_name
        self.monitored_channels: Set[int] = set()
        self.signal_cache: Dict[str, List[CoinSignal]] = {}
        self.pattern_matcher = SignalPattern()
        self.active_positions: Dict[str, CoinSignal] = {}
        
    async def start(self):
        """Initialize and start the Telegram client"""
        self.client = TelegramClient(
            self.session_name,
            settings.telegram_api_id,
            settings.telegram_api_hash
        )
        
        await self.client.start(bot_token=settings.telegram_bot_token)
        logger.info("Telegram monitor started successfully")
        
        # Set up event handlers
        self.client.add_event_handler(
            self._handle_new_message,
            events.NewMessage(chats=list(self.monitored_channels))
        )
        
    async def add_channel(self, channel_id: int):
        """Add a channel to monitor"""
        try:
            entity = await self.client.get_entity(channel_id)
            self.monitored_channels.add(channel_id)
            logger.info(f"Added channel to monitor: {entity.title} ({channel_id})")
            
            # Update event handler with new channel list
            self.client.remove_event_handler(self._handle_new_message)
            self.client.add_event_handler(
                self._handle_new_message,
                events.NewMessage(chats=list(self.monitored_channels))
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add channel {channel_id}: {e}")
            return False
    
    async def _handle_new_message(self, event):
        """Process new messages for signals"""
        try:
            message = event.message
            channel = await event.get_chat()
            
            # Parse the message for signals
            signals = await self._parse_message(message, channel)
            
            for signal in signals:
                # Store in database
                self.db.add_telegram_signal(
                    message_id=signal.message_id,
                    channel_id=signal.channel_id,
                    channel_name=signal.channel_name,
                    timestamp=signal.timestamp,
                    coin_symbol=signal.ticker,
                    signal_type=signal.signal_type,
                    entry_price=signal.entry_price,
                    target_prices=json.dumps(signal.target_prices),
                    stop_loss=signal.stop_loss,
                    confidence=signal.confidence,
                    raw_message=signal.raw_message,
                    metadata=json.dumps(signal.metadata)
                )
                
                # Cache the signal
                if signal.ticker not in self.signal_cache:
                    self.signal_cache[signal.ticker] = []
                self.signal_cache[signal.ticker].append(signal)
                
                # Log significant signals
                if signal.confidence > 0.7:
                    logger.info(f"High confidence signal: {signal.ticker} - {signal.signal_type} @ {signal.entry_price}")
                    await self._process_high_confidence_signal(signal)
                    
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _parse_message(self, message, channel) -> List[CoinSignal]:
        """Extract signals from a message using advanced pattern matching"""
        signals = []
        text = message.text or ""
        
        # Find contract addresses
        contracts = []
        for pattern in self.pattern_matcher.CONTRACT_PATTERNS:
            matches = re.findall(pattern, text)
            contracts.extend(matches)
        
        # Determine signal type
        signal_type = self._determine_signal_type(text)
        
        # Extract prices
        entry_price = self._extract_price(text, self.pattern_matcher.PRICE_PATTERNS)
        targets = self._extract_targets(text)
        stop_loss = self._extract_stop_loss(text)
        
        # Extract ticker
        ticker = self._extract_ticker(text)
        
        # Calculate confidence based on message structure and entities
        confidence = self._calculate_confidence(message, signal_type, bool(contracts))
        
        for contract in contracts:
            signal = CoinSignal(
                ticker=ticker or f"${contract[:5]}",
                contract_address=contract,
                signal_type=signal_type,
                entry_price=entry_price,
                target_prices=targets,
                stop_loss=stop_loss,
                confidence=confidence,
                channel_name=channel.title if hasattr(channel, 'title') else str(channel.id),
                channel_id=channel.id,
                message_id=message.id,
                raw_message=text[:500],  # Store first 500 chars
                metadata={
                    "has_media": bool(message.media),
                    "forward_from": message.forward.sender_id if message.forward else None,
                    "views": message.views,
                    "reactions": message.reactions.results if message.reactions else []
                }
            )
            signals.append(signal)
        
        return signals
    
    def _determine_signal_type(self, text: str) -> str:
        """Determine the type of signal from message text"""
        text_lower = text.lower()
        
        # Check for buy signals
        for pattern in self.pattern_matcher.BUY_PATTERNS:
            if re.search(pattern, text):
                return "BUY"
        
        # Check for sell signals
        for pattern in self.pattern_matcher.SELL_PATTERNS:
            if re.search(pattern, text):
                return "SELL"
        
        # Check for specific keywords
        if any(word in text_lower for word in ['hold', 'hodl', 'accumulate']):
            return "HOLD"
        
        return "ALERT"
    
    def _extract_price(self, text: str, patterns: List[str]) -> Optional[float]:
        """Extract price from text"""
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_targets(self, text: str) -> List[float]:
        """Extract target prices"""
        targets = []
        for pattern in self.pattern_matcher.TARGET_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    targets.append(float(match))
                except ValueError:
                    continue
        return sorted(targets)
    
    def _extract_stop_loss(self, text: str) -> Optional[float]:
        """Extract stop loss price"""
        for pattern in self.pattern_matcher.STOP_LOSS_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_ticker(self, text: str) -> Optional[str]:
        """Extract ticker symbol"""
        # Look for $SYMBOL pattern
        ticker_match = re.search(r'\$([A-Z]{2,10})', text)
        if ticker_match:
            return f"${ticker_match.group(1)}"
        
        # Look for common patterns
        patterns = [
            r"(?i)(?:ticker|symbol|token)[\s:]+([A-Z]{2,10})",
            r"([A-Z]{2,10})/(?:USD|USDT|SOL)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"${match.group(1)}"
        
        return None
    
    def _calculate_confidence(self, message, signal_type: str, has_contract: bool) -> float:
        """Calculate signal confidence based on multiple factors"""
        confidence = 0.5
        
        # Contract address increases confidence
        if has_contract:
            confidence += 0.2
        
        # Check for bold/italic emphasis
        if message.entities:
            for entity in message.entities:
                if isinstance(entity, (MessageEntityBold, MessageEntityItalic)):
                    confidence += 0.05
                elif isinstance(entity, MessageEntityCode):
                    confidence += 0.1
        
        # High engagement increases confidence
        if hasattr(message, 'views') and message.views:
            if message.views > 1000:
                confidence += 0.1
            if message.views > 10000:
                confidence += 0.1
        
        # Specific signal types have different base confidences
        if signal_type == "BUY":
            confidence += 0.1
        elif signal_type == "SELL":
            confidence += 0.15
        
        # Cap confidence at 0.95
        return min(confidence, 0.95)
    
    async def _process_high_confidence_signal(self, signal: CoinSignal):
        """Process high confidence signals for immediate action"""
        # Check if we already have a position
        if signal.contract_address in self.active_positions:
            existing = self.active_positions[signal.contract_address]
            if signal.signal_type == "SELL" and existing.signal_type == "BUY":
                logger.info(f"Exit signal received for {signal.ticker}")
                # Could trigger automated trading here
        else:
            if signal.signal_type == "BUY":
                self.active_positions[signal.contract_address] = signal
                logger.info(f"New position tracking: {signal.ticker}")
    
    async def get_channel_stats(self, channel_id: int, days: int = 7) -> Dict[str, Any]:
        """Get statistics for a specific channel"""
        cutoff_date = datetime.now(timezone.utc) - pd.Timedelta(days=days)
        
        # Query database for signals
        with self.db.db_path.open() as conn:
            df = pd.read_sql_query("""
                SELECT * FROM telegram_signals 
                WHERE channel_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """, conn, params=[channel_id, cutoff_date])
        
        if df.empty:
            return {"error": "No data found"}
        
        stats = {
            "total_signals": len(df),
            "signal_types": df['signal_type'].value_counts().to_dict(),
            "average_confidence": df['confidence'].mean(),
            "unique_coins": df['coin_symbol'].nunique(),
            "top_coins": df['coin_symbol'].value_counts().head(10).to_dict(),
            "daily_distribution": df.groupby(df['timestamp'].dt.date).size().to_dict()
        }
        
        return stats
    
    async def close(self):
        """Clean up resources"""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram monitor disconnected")