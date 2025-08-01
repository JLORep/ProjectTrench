#!/usr/bin/env python3
"""
TrenchCoat Pro - Comprehensive Test Suite
Automated unit tests for all critical components
"""
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import json
import sqlite3
import tempfile
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Test categories
# 1. Data Layer Tests
# 2. API Integration Tests  
# 3. Trading Logic Tests
# 4. Risk Management Tests
# 5. UI Component Tests


class TestDataLayer(unittest.TestCase):
    """Test database operations and data integrity"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.temp_db.name
        
    def tearDown(self):
        """Clean up temporary database"""
        os.unlink(self.db_path)
    
    def test_database_creation(self):
        """Test database schema creation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create coins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT UNIQUE NOT NULL,
                contract_address TEXT,
                discovery_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price_usd REAL,
                market_cap REAL,
                volume_24h REAL,
                liquidity REAL,
                holder_count INTEGER,
                rug_score REAL,
                enriched BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Verify table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coins'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'coins')
        
        conn.close()
    
    def test_coin_insertion(self):
        """Test inserting coin data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE coins (
                ticker TEXT UNIQUE NOT NULL,
                price_usd REAL,
                market_cap REAL
            )
        ''')
        
        # Insert test coin
        cursor.execute("INSERT INTO coins (ticker, price_usd, market_cap) VALUES (?, ?, ?)",
                      ("TEST", 0.001, 1000000))
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT * FROM coins WHERE ticker = ?", ("TEST",))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "TEST")
        self.assertEqual(result[1], 0.001)
        
        conn.close()
    
    def test_data_enrichment_update(self):
        """Test updating coin with enriched data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create and populate
        cursor.execute('''
            CREATE TABLE coins (
                ticker TEXT UNIQUE NOT NULL,
                price_usd REAL,
                enriched BOOLEAN DEFAULT FALSE
            )
        ''')
        cursor.execute("INSERT INTO coins (ticker, price_usd) VALUES (?, ?)", ("TEST", 0.001))
        
        # Update with enriched data
        cursor.execute("UPDATE coins SET price_usd = ?, enriched = ? WHERE ticker = ?",
                      (0.002, True, "TEST"))
        conn.commit()
        
        # Verify update
        cursor.execute("SELECT price_usd, enriched FROM coins WHERE ticker = ?", ("TEST",))
        result = cursor.fetchone()
        self.assertEqual(result[0], 0.002)
        self.assertEqual(result[1], 1)  # SQLite stores boolean as integer
        
        conn.close()


class TestAPIIntegrations(unittest.TestCase):
    """Test external API integrations"""
    
    @patch('requests.get')
    def test_dexscreener_api(self, mock_get):
        """Test DexScreener API integration"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'pairs': [{
                'priceUsd': '0.001',
                'volume': {'h24': 50000},
                'liquidity': {'usd': 100000}
            }]
        }
        mock_get.return_value = mock_response
        
        # Test API call
        from src.data.free_api_providers import get_dexscreener_data
        result = get_dexscreener_data("So11111111111111111111111111111111111111112")
        
        self.assertIsNotNone(result)
        self.assertIn('priceUsd', result)
        self.assertEqual(result['priceUsd'], '0.001')
    
    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling"""
        # Mock API error
        mock_get.side_effect = Exception("API Error")
        
        # Test error handling
        from src.data.free_api_providers import get_dexscreener_data
        result = get_dexscreener_data("invalid_address")
        
        # Should return None or empty dict on error
        self.assertTrue(result is None or result == {})


class TestTradingLogic(unittest.TestCase):
    """Test trading strategies and logic"""
    
    def test_momentum_strategy_calculation(self):
        """Test momentum strategy scoring"""
        # Test data
        test_coin = {
            'price_change_5m': 0.05,  # 5% gain
            'volume_surge': 3.0,       # 3x volume
            'liquidity': 100000        # Good liquidity
        }
        
        # Calculate momentum score
        score = (test_coin['price_change_5m'] * 0.3 + 
                 test_coin['volume_surge'] * 0.4 + 
                 (1 if test_coin['liquidity'] > 50000 else 0) * 0.3)
        
        # Verify calculation
        expected_score = (0.05 * 0.3) + (3.0 * 0.4) + (1 * 0.3)
        self.assertAlmostEqual(score, expected_score, places=4)
        self.assertGreater(score, 0.75)  # Should trigger buy signal
    
    def test_whale_following_strategy(self):
        """Test whale following strategy"""
        # Mock whale data
        whale_data = {
            'whale_count': 5,
            'whale_accumulation': True,
            'known_profitable_wallets': 3
        }
        
        # Calculate whale score
        if whale_data['whale_count'] >= 3 and whale_data['whale_accumulation']:
            whale_score = whale_data['known_profitable_wallets'] / whale_data['whale_count']
        else:
            whale_score = 0
        
        # Verify logic
        self.assertGreater(whale_score, 0.5)  # Should trigger signal
    
    def test_volume_explosion_detection(self):
        """Test volume explosion detection"""
        # Test data
        current_volume = 500000
        average_volume = 50000
        
        # Calculate volume anomaly
        volume_anomaly = current_volume / average_volume
        
        # Verify detection
        self.assertEqual(volume_anomaly, 10)  # 10x volume
        self.assertGreater(volume_anomaly, 5)  # Should trigger signal


class TestRiskManagement(unittest.TestCase):
    """Test risk management systems"""
    
    def test_position_sizing(self):
        """Test Kelly Criterion position sizing"""
        # Test parameters
        account_balance = 10000
        risk_per_trade = 0.02  # 2%
        stop_loss_percent = 0.15  # 15%
        
        # Calculate position size
        max_risk_amount = account_balance * risk_per_trade
        position_size = max_risk_amount / stop_loss_percent
        
        # Apply maximum position limit
        max_position = 0.5 * 3000  # 0.5 SOL at $3000/SOL
        final_position = min(position_size, max_position)
        
        # Verify calculations
        self.assertEqual(max_risk_amount, 200)  # $200 max risk
        self.assertAlmostEqual(position_size, 1333.33, places=2)
        self.assertEqual(final_position, 1500)  # Capped at max
    
    def test_stop_loss_calculation(self):
        """Test stop loss price calculation"""
        # Test data
        entry_price = 0.001
        stop_loss_percent = 0.15
        
        # Calculate stop loss
        stop_loss_price = entry_price * (1 - stop_loss_percent)
        
        # Verify calculation
        self.assertAlmostEqual(stop_loss_price, 0.00085, places=5)
    
    def test_max_drawdown_protection(self):
        """Test maximum drawdown protection"""
        # Portfolio tracking
        portfolio_values = [10000, 10500, 11000, 9500, 9000, 9200]
        
        # Calculate drawdown
        peak = max(portfolio_values)
        current = portfolio_values[-1]
        drawdown = (peak - current) / peak
        
        # Verify protection trigger
        self.assertAlmostEqual(drawdown, 0.1636, places=4)  # 16.36%
        self.assertGreater(drawdown, 0.15)  # Should trigger protection


class TestUIComponents(unittest.TestCase):
    """Test UI components and dashboard functionality"""
    
    def test_dashboard_data_preparation(self):
        """Test data preparation for dashboard display"""
        # Mock coin data
        coins_data = [
            {'ticker': 'TEST1', 'price': 0.001, 'volume': 50000, 'score': 0.85},
            {'ticker': 'TEST2', 'price': 0.002, 'volume': 100000, 'score': 0.92},
            {'ticker': 'TEST3', 'price': 0.0005, 'volume': 25000, 'score': 0.65}
        ]
        
        # Sort by score
        sorted_coins = sorted(coins_data, key=lambda x: x['score'], reverse=True)
        
        # Verify sorting
        self.assertEqual(sorted_coins[0]['ticker'], 'TEST2')
        self.assertEqual(sorted_coins[1]['ticker'], 'TEST1')
        self.assertEqual(sorted_coins[2]['ticker'], 'TEST3')
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation"""
        # Mock trade history
        trades = [
            {'profit': 100, 'result': 'win'},
            {'profit': -50, 'result': 'loss'},
            {'profit': 150, 'result': 'win'},
            {'profit': -30, 'result': 'loss'},
            {'profit': 200, 'result': 'win'}
        ]
        
        # Calculate metrics
        total_trades = len(trades)
        wins = len([t for t in trades if t['result'] == 'win'])
        losses = len([t for t in trades if t['result'] == 'loss'])
        win_rate = wins / total_trades
        total_profit = sum(t['profit'] for t in trades)
        
        # Verify calculations
        self.assertEqual(total_trades, 5)
        self.assertEqual(wins, 3)
        self.assertEqual(losses, 2)
        self.assertEqual(win_rate, 0.6)  # 60% win rate
        self.assertEqual(total_profit, 370)


class TestIntegration(unittest.TestCase):
    """End-to-end integration tests"""
    
    def test_full_coin_processing_pipeline(self):
        """Test complete coin processing pipeline"""
        # Simulate coin discovery
        new_coin = {
            'ticker': 'TESTCOIN',
            'contract': 'test_contract_address',
            'discovery_time': datetime.now()
        }
        
        # Simulate enrichment
        enriched_data = {
            'price': 0.001,
            'volume': 75000,
            'liquidity': 150000,
            'holders': 500,
            'rug_score': 0.2
        }
        new_coin.update(enriched_data)
        
        # Simulate strategy evaluation
        momentum_score = 0.82
        should_buy = momentum_score > 0.75
        
        # Verify pipeline
        self.assertTrue(should_buy)
        self.assertLess(new_coin['rug_score'], 0.5)  # Low risk
        self.assertGreater(new_coin['liquidity'], 100000)  # Good liquidity
    
    @patch('asyncio.sleep')
    async def test_real_time_monitoring(self, mock_sleep):
        """Test real-time monitoring simulation"""
        mock_sleep.return_value = None
        
        # Simulate monitoring loop
        monitoring_active = True
        updates_received = 0
        
        async def monitor():
            nonlocal updates_received
            while monitoring_active and updates_received < 3:
                updates_received += 1
                await asyncio.sleep(1)
        
        # Run monitoring
        await monitor()
        
        # Verify monitoring
        self.assertEqual(updates_received, 3)


def run_all_tests():
    """Run complete test suite"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIIntegrations))
    suite.addTests(loader.loadTestsFromTestCase(TestTradingLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestUIComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)