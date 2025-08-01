#!/usr/bin/env python3
"""
Data Validation System - Ensures proper separation between demo and live data
"""
import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime

class DataValidationSystem:
    """Centralized system for validating and managing demo vs live data"""
    
    def __init__(self):
        self.live_data_available = False
        self.live_data_sources = {}
        self.validation_status = {}
        
    def validate_database_connection(self) -> Dict[str, Any]:
        """Validate if we have a real database connection with actual data"""
        try:
            # Try importing database modules
            from streamlit_database import streamlit_db
            database_available = True
            
            # Test actual data retrieval
            test_coins = streamlit_db.get_all_coins()
            coin_count = streamlit_db.get_coin_count()
            
            # Validate we have real data (not just empty responses)
            has_real_data = (
                test_coins and 
                len(test_coins) > 10 and  # More than just a few test records
                coin_count > 100  # Substantial dataset
            )
            
            return {
                'status': 'connected' if has_real_data else 'demo_mode',
                'database_available': database_available,
                'has_real_data': has_real_data,
                'coin_count': coin_count,
                'sample_data_count': len(test_coins) if test_coins else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except ImportError:
            return {
                'status': 'demo_mode',
                'database_available': False,
                'has_real_data': False,
                'coin_count': 0,
                'error': 'Database module not available',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'demo_mode',
                'database_available': False,
                'has_real_data': False,
                'coin_count': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_data_mode(self) -> str:
        """Determine current data mode: 'live' or 'demo'"""
        validation = self.validate_database_connection()
        return 'live' if validation['has_real_data'] else 'demo'
    
    def show_data_status_banner(self):
        """Show a clear banner indicating current data mode"""
        mode = self.get_data_mode()
        validation = self.validate_database_connection()
        
        if mode == 'live':
            st.success(f"🟢 **LIVE DATA MODE** - Connected to trench.db with {validation['coin_count']:,} real coins")
        else:
            st.warning(f"🟡 **DEMO DATA MODE** - Using sample data for demonstration. {validation.get('error', 'Database not available')}")
    
    def get_validated_portfolio_data(self) -> Dict[str, Any]:
        """Get portfolio data with proper live/demo separation"""
        mode = self.get_data_mode()
        
        if mode == 'live':
            try:
                from streamlit_database import streamlit_db
                portfolio = streamlit_db.get_portfolio_data()
                portfolio['data_source'] = 'live'
                portfolio['mode'] = 'live'
                return portfolio
            except Exception as e:
                # Fall through to demo data
                pass
        
        # Demo portfolio data
        return {
            'total_value': 127845,
            'profit': 12845,
            'profit_pct': 11.2,
            'active_positions': 23,
            'win_rate': 78.3,
            'avg_smart_wallets': 156,
            'total_liquidity': 2847500,
            'data_source': 'demo',
            'mode': 'demo'
        }
    
    def get_validated_coin_data(self) -> List[Dict[str, Any]]:
        """Get coin data with proper live/demo separation"""
        mode = self.get_data_mode()
        
        if mode == 'live':
            try:
                from streamlit_database import streamlit_db
                coins = streamlit_db.get_all_coins()
                if coins and len(coins) > 10:
                    # Add data source indicator
                    for coin in coins:
                        coin['data_source'] = 'live'
                        coin['mode'] = 'live'
                    return coins
            except Exception as e:
                # Fall through to demo data
                pass
        
        # Demo coin data
        demo_coins = [
            {"ticker": "PEPE", "price_gain_pct": 270.1, "smart_wallets": 1250, "liquidity": 2100000.0, "axiom_mc": 8200000000.0, "peak_volume": 67800000.0, "ca": "6GCwwBywXgSqUJVNxvL4XJbdMGPsafgX7bqDCKQw45dV"},
            {"ticker": "SHIB", "price_gain_pct": 152.3, "smart_wallets": 890, "liquidity": 5600000.0, "axiom_mc": 15100000000.0, "peak_volume": 89200000.0, "ca": "CiKu9eHPBf2PyJ8EQCR8xJ4KnF2KVg7e6B3vW1234567"},
            {"ticker": "DOGE", "price_gain_pct": 90.5, "smart_wallets": 2100, "liquidity": 12300000.0, "axiom_mc": 28700000000.0, "peak_volume": 234500000.0, "ca": "DKxYz8vMJKLNOPQRSTUVWXYZ123456789abcdefghij"},
            {"ticker": "FLOKI", "price_gain_pct": 180.1, "smart_wallets": 670, "liquidity": 1800000.0, "axiom_mc": 3400000000.0, "peak_volume": 45600000.0, "ca": "FLKxYz8vMJKLNOPQRSTUVWXYZ123456789abcdef123"},
            {"ticker": "BONK", "price_gain_pct": 57.0, "smart_wallets": 450, "liquidity": 890000.0, "axiom_mc": 1200000000.0, "peak_volume": 23400000.0, "ca": "BNKxYz8vMJKLNOPQRSTUVWXYZ123456789abcdef456"},
            {"ticker": "SOLANA", "price_gain_pct": 45.8, "smart_wallets": 5670, "liquidity": 45600000.0, "axiom_mc": 89700000000.0, "peak_volume": 567800000.0, "ca": "So11111111111111111111111111111111111111112"},
            {"ticker": "MATIC", "price_gain_pct": 123.7, "smart_wallets": 1890, "liquidity": 8900000.0, "axiom_mc": 12300000000.0, "peak_volume": 123400000.0, "ca": "MATxYz8vMJKLNOPQRSTUVWXYZ123456789abcdef789"},
            {"ticker": "AVAX", "price_gain_pct": 78.9, "smart_wallets": 2340, "liquidity": 15400000.0, "axiom_mc": 23400000000.0, "peak_volume": 189000000.0, "ca": "AVXxYz8vMJKLNOPQRSTUVWXYZ123456789abcdef321"},
            {"ticker": "LINK", "price_gain_pct": 89.2, "smart_wallets": 3450, "liquidity": 23400000.0, "axiom_mc": 34500000000.0, "peak_volume": 267800000.0, "ca": "LNKxYz8vMJKLNOPQRSTUVWXYZ123456789abcdef654"},
            {"ticker": "UNI", "price_gain_pct": 65.4, "smart_wallets": 2780, "liquidity": 18900000.0, "axiom_mc": 27800000000.0, "peak_volume": 178900000.0, "ca": "UNIxYz8vMJKLNOPQRSTUVWXYZ123456789abcdef987"}
        ]
        
        # Add data source indicator
        for coin in demo_coins:
            coin['data_source'] = 'demo'
            coin['mode'] = 'demo'
            
        return demo_coins
    
    def get_validated_telegram_signals(self) -> List[Dict[str, Any]]:
        """Get telegram signals with proper live/demo separation"""
        mode = self.get_data_mode()
        
        if mode == 'live':
            try:
                from streamlit_database import streamlit_db
                signals = streamlit_db.get_telegram_signals(limit=8, min_confidence=0.6)
                if signals and len(signals) > 0:
                    # Add data source indicator
                    for signal in signals:
                        signal['data_source'] = 'live'
                        signal['mode'] = 'live'
                    return signals
            except Exception as e:
                # Fall through to demo data
                pass
        
        # Demo telegram signals
        demo_signals = [
            {'coin_symbol': 'SOL', 'signal_type': 'BUY', 'confidence': 0.85, 'entry_price': 119.50, 'timestamp': '2025-08-01 10:30:00', 'channel_name': 'CryptoGems', 'data_source': 'demo', 'mode': 'demo'},
            {'coin_symbol': 'AVAX', 'signal_type': 'SELL', 'confidence': 0.75, 'entry_price': 35.20, 'timestamp': '2025-08-01 09:45:00', 'channel_name': 'MoonShots', 'data_source': 'demo', 'mode': 'demo'},
            {'coin_symbol': 'NEAR', 'signal_type': 'BUY', 'confidence': 0.92, 'entry_price': 8.45, 'timestamp': '2025-08-01 08:15:00', 'channel_name': 'ATM.Day', 'data_source': 'demo', 'mode': 'demo'}
        ]
        
        return demo_signals

# Global validator instance
data_validator = DataValidationSystem()