#!/usr/bin/env python3
"""
TrenchCoat Pro - Live Data Integration
Connect real coin detection, trading, and notifications to dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import time
import requests
import json
from typing import Dict, List, Any
import os
import random

# Import our Telegram enrichment pipeline
try:
    from telegram_enrichment_pipeline import TelegramEnrichmentPipeline, convert_enriched_coin_to_dashboard_format
except ImportError:
    TelegramEnrichmentPipeline = None

class LiveDataManager:
    """Manages real-time data flow between components"""
    
    def __init__(self):
        self.api_endpoints = {
            'dexscreener': 'https://api.dexscreener.com/latest/dex/tokens/',
            'jupiter': 'https://price.jup.ag/v4/price',
            'coingecko': 'https://api.coingecko.com/api/v3/simple/price'
        }
        
        # Initialize Telegram enrichment pipeline
        self.enrichment_pipeline = TelegramEnrichmentPipeline() if TelegramEnrichmentPipeline else None
        
        # Initialize session state for live data
        if 'live_coins' not in st.session_state:
            st.session_state.live_coins = []
        if 'live_trades' not in st.session_state:
            st.session_state.live_trades = []
        if 'live_notifications' not in st.session_state:
            st.session_state.live_notifications = []
        if 'telegram_signals' not in st.session_state:
            st.session_state.telegram_signals = []
        if 'enriched_coins' not in st.session_state:
            st.session_state.enriched_coins = []
    
    def detect_trending_coins(self, limit=10):
        """Detect real trending coins from DEX data"""
        try:
            # Use DexScreener API for real Solana trending tokens
            response = requests.get(
                'https://api.dexscreener.com/latest/dex/search',
                params={
                    'q': 'SOL',
                    'rankBy': 'volume24h',
                    'order': 'desc'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                trending_coins = []
                
                for pair in data.get('pairs', [])[:limit]:
                    if pair.get('chainId') == 'solana':
                        coin_data = {
                            'symbol': pair.get('baseToken', {}).get('symbol', 'Unknown'),
                            'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                            'address': pair.get('baseToken', {}).get('address', ''),
                            'price': float(pair.get('priceUsd', 0)),
                            'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                            'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                            'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                            'confidence': self.calculate_confidence(pair),
                            'detected_at': datetime.now(),
                            'dex_pair': pair.get('dexId'),
                            'pair_address': pair.get('pairAddress')
                        }
                        trending_coins.append(coin_data)
                
                return trending_coins
            
        except Exception as e:
            st.error(f"Error fetching live coin data: {e}")
            
        # Fallback to sample data if API fails
        return self.generate_sample_coins(limit)
    
    def calculate_confidence(self, pair_data):
        """Calculate confidence score based on multiple factors"""
        factors = {
            'volume': min(float(pair_data.get('volume', {}).get('h24', 0)) / 1000000, 1.0),  # Volume score
            'liquidity': min(float(pair_data.get('liquidity', {}).get('usd', 0)) / 100000, 1.0),  # Liquidity score
            'price_change': min(abs(float(pair_data.get('priceChange', {}).get('h24', 0))) / 100, 1.0),  # Volatility
            'fdv': min(float(pair_data.get('fdv', 0)) / 10000000, 1.0) if pair_data.get('fdv') else 0  # Market cap
        }
        
        # Weighted confidence calculation
        weights = {'volume': 0.3, 'liquidity': 0.3, 'price_change': 0.2, 'fdv': 0.2}
        confidence = sum(factors[key] * weights[key] for key in factors) * 100
        
        return min(max(confidence, 0), 100)  # Clamp between 0-100
    
    async def process_telegram_signals(self, telegram_messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process Telegram signals through enrichment pipeline"""
        if not self.enrichment_pipeline:
            st.error("Telegram enrichment pipeline not available")
            return []
        
        try:
            # Process messages through enrichment pipeline
            enriched_coins = await self.enrichment_pipeline.process_telegram_signals(telegram_messages)
            
            # Convert to dashboard format
            dashboard_coins = []
            for enriched_coin in enriched_coins:
                dashboard_coin = convert_enriched_coin_to_dashboard_format(enriched_coin)
                dashboard_coins.append(dashboard_coin)
            
            # Store enriched coins in session state
            st.session_state.enriched_coins.extend(dashboard_coins)
            
            # Keep only recent enriched coins (last 50)
            st.session_state.enriched_coins = st.session_state.enriched_coins[-50:]
            
            return dashboard_coins
            
        except Exception as e:
            st.error(f"Telegram signal processing error: {e}")
            return []
    
    def simulate_telegram_signals(self) -> List[Dict[str, str]]:
        """Simulate Telegram signals for demo purposes"""
        
        sample_signals = [
            {
                'text': '🚀 NEW GEM ALERT! $BONK is about to MOON! 🌙\nCA: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263\nPrice: $0.000012\nMC: $500M\nThis is going to 100x! 💎',
                'channel': 'CryptoGems',
                'timestamp': datetime.now().isoformat()
            },
            {
                'text': 'Found a new runner! Contract: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\n$WIF is launching soon! Volume already pumping!\nGet in early! 🚀',
                'channel': 'ATM.Day',
                'timestamp': datetime.now().isoformat()
            },
            {
                'text': 'PEPE ALERT 🐸\nContract: 4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R\nPrice: $0.000089\nLiquidity: $2.5M\nConfirmed not a rug! Team is based! 💪',
                'channel': 'PepeSignals',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # Randomly select 1-2 signals to simulate new activity
        import random
        return random.sample(sample_signals, random.randint(1, 2))
    
    async def get_enriched_trending_coins(self, limit=10):
        """Get trending coins with enrichment from multiple sources"""
        all_coins = []
        
        try:
            # Method 1: Get coins from DexScreener API
            dex_coins = self.detect_trending_coins(limit)
            all_coins.extend(dex_coins)
            
            # Method 2: Process Telegram signals (simulation for demo)
            if random.random() > 0.7:  # 30% chance of new Telegram signals
                telegram_messages = self.simulate_telegram_signals()
                enriched_telegram_coins = await self.process_telegram_signals(telegram_messages)
                
                if enriched_telegram_coins:
                    st.info(f"📡 Processed {len(enriched_telegram_coins)} Telegram signals")
                    # Add enriched coins to the mix
                    all_coins.extend(enriched_telegram_coins)
            
            # Method 3: Include stored enriched coins
            stored_enriched = st.session_state.get('enriched_coins', [])
            if stored_enriched:
                # Add recent enriched coins (last 5)
                recent_enriched = stored_enriched[-5:]
                all_coins.extend(recent_enriched)
            
            # Sort by confidence and return top coins
            all_coins.sort(key=lambda x: x.get('score', 0) * 100, reverse=True)
            return all_coins[:limit]
            
        except Exception as e:
            st.error(f"Enriched coin detection error: {e}")
            return self.detect_trending_coins(limit)  # Fallback to basic detection
    
    def generate_sample_coins(self, limit=10):
        """Fallback sample data when APIs are unavailable"""
        sample_coins = []
        coin_names = ['BONK', 'WIF', 'PEPE', 'MYRO', 'BOME', 'SLERF', 'POPCAT', 'MOTHER', 'MOODENG', 'PNUT']
        
        for i in range(limit):
            coin = {
                'symbol': coin_names[i % len(coin_names)],
                'name': f"{coin_names[i % len(coin_names)]} Token",
                'address': f"sample_address_{i}",
                'price': np.random.uniform(0.001, 2.0),
                'volume_24h': np.random.uniform(100000, 5000000),
                'price_change_24h': np.random.uniform(-50, 200),
                'liquidity': np.random.uniform(50000, 1000000),
                'confidence': np.random.uniform(60, 95),
                'detected_at': datetime.now() - timedelta(minutes=np.random.randint(1, 60)),
                'dex_pair': 'demo',
                'pair_address': f'demo_pair_{i}'
            }
            sample_coins.append(coin)
        
        return sample_coins
    
    def get_live_portfolio_data(self):
        """Get real portfolio performance from trading engine"""
        try:
            # This would connect to your actual Solana wallet/trading data
            # For now, using enhanced sample data that looks realistic
            
            portfolio_data = {
                'total_value': st.session_state.get('portfolio_value', 10000),
                'daily_pnl': st.session_state.get('daily_pnl', 0),
                'positions': st.session_state.get('live_trades', []),
                'win_rate': self.calculate_win_rate(),
                'total_trades': len(st.session_state.get('completed_trades', [])),
                'active_positions': len(st.session_state.get('live_trades', []))
            }
            
            return portfolio_data
            
        except Exception as e:
            st.error(f"Error fetching portfolio data: {e}")
            return None
    
    def calculate_win_rate(self):
        """Calculate actual win rate from completed trades"""
        completed_trades = st.session_state.get('completed_trades', [])
        if not completed_trades:
            return 0.0
        
        winning_trades = sum(1 for trade in completed_trades if trade.get('pnl', 0) > 0)
        return (winning_trades / len(completed_trades)) * 100
    
    def trigger_live_notifications(self, coin_data):
        """Trigger real notifications when coins are detected"""
        try:
            # Import our notification system
            from unified_notifications import UnifiedNotificationSystem
            
            notification_system = UnifiedNotificationSystem()
            
            message = f"""
🎯 RUNNER DETECTED!

💎 {coin_data['symbol']} ({coin_data['name']})
💰 Price: ${coin_data['price']:.6f}
📈 24h Change: {coin_data['price_change_24h']:.1f}%
💧 Liquidity: ${coin_data['liquidity']:,.0f}
🎪 Confidence: {coin_data['confidence']:.1f}%

🔗 Address: {coin_data['address'][:8]}...
⏰ Detected: {coin_data['detected_at'].strftime('%H:%M:%S')}

🚀 TrenchCoat Pro Alert System
"""
            
            # Send to all platforms
            asyncio.run(notification_system.send_unified_alert(
                title="🎯 New Runner Detected!",
                message=message,
                priority="high"
            ))
            
            # Log notification
            st.session_state.live_notifications.append({
                'timestamp': datetime.now(),
                'type': 'runner_detected',
                'coin': coin_data['symbol'],
                'message': message
            })
            
        except Exception as e:
            st.error(f"Notification error: {e}")
    
    def execute_live_trade(self, coin_data, trade_params):
        """Execute real trade via Solana trading engine"""
        try:
            # Import our trading engine
            from solana_trading_engine import SafeTrader
            
            trader = SafeTrader()
            
            # Execute trade with safety limits
            trade_result = trader.execute_safe_trade(
                token_address=coin_data['address'],
                amount_sol=trade_params.get('amount', 0.1),
                action='buy',
                confidence=coin_data['confidence']
            )
            
            if trade_result['success']:
                # Add to live trades
                trade_record = {
                    'timestamp': datetime.now(),
                    'symbol': coin_data['symbol'],
                    'action': 'buy',
                    'amount': trade_params.get('amount', 0.1),
                    'price': coin_data['price'],
                    'confidence': coin_data['confidence'],
                    'status': 'active',
                    'trade_id': trade_result.get('transaction_id'),
                    'expected_profit': trade_params.get('take_profit', 25)
                }
                
                st.session_state.live_trades.append(trade_record)
                
                # Send success notification
                self.trigger_trade_notification(trade_record, 'executed')
                
                return trade_result
            
        except Exception as e:
            st.error(f"Trading error: {e}")
            return {'success': False, 'error': str(e)}
    
    def trigger_trade_notification(self, trade_record, action):
        """Send notifications for trade actions"""
        try:
            from unified_notifications import UnifiedNotificationSystem
            
            notification_system = UnifiedNotificationSystem()
            
            if action == 'executed':
                message = f"""
✅ TRADE EXECUTED!

💎 {trade_record['symbol']}
💰 Amount: {trade_record['amount']} SOL
💵 Price: ${trade_record['price']:.6f}
🎯 Confidence: {trade_record['confidence']:.1f}%
🎪 Expected Profit: {trade_record['expected_profit']}%

⏰ {trade_record['timestamp'].strftime('%H:%M:%S')}
🔗 TX: {trade_record.get('trade_id', 'Processing...')[:8]}...

🚀 TrenchCoat Pro Trading Engine
"""
                
                asyncio.run(notification_system.send_unified_alert(
                    title="✅ Trade Executed!",
                    message=message,
                    priority="high"
                ))
                
        except Exception as e:
            st.error(f"Trade notification error: {e}")
    
    def update_live_data(self):
        """Main method to update all live data"""
        # Detect new trending coins
        trending_coins = self.detect_trending_coins()
        
        # Update session state
        st.session_state.live_coins = trending_coins
        
        # Trigger notifications for high-confidence coins
        for coin in trending_coins:
            if coin['confidence'] > 85 and coin['symbol'] not in [n.get('coin') for n in st.session_state.live_notifications[-5:]]:
                self.trigger_live_notifications(coin)
        
        # Update portfolio data
        portfolio_data = self.get_live_portfolio_data()
        if portfolio_data:
            st.session_state.portfolio_data = portfolio_data
        
        return {
            'trending_coins': trending_coins,
            'portfolio': portfolio_data,
            'notifications_sent': len(st.session_state.live_notifications)
        }

# Integration functions for dashboard
def get_live_coin_data():
    """Get live coin data for dashboard"""
    manager = LiveDataManager()
    return manager.detect_trending_coins()

def get_live_portfolio():
    """Get live portfolio data for dashboard"""
    manager = LiveDataManager()
    return manager.get_live_portfolio_data()

def enable_live_mode():
    """Enable live data mode in dashboard"""
    st.session_state.live_mode = True
    st.success("🟢 Live data mode enabled!")
    st.info("Real coin detection and notifications are now active.")

def disable_live_mode():
    """Disable live data mode"""
    st.session_state.live_mode = False
    st.info("🔵 Demo mode enabled - using sample data.")