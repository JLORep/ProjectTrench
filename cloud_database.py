#!/usr/bin/env python3
"""
Streamlit Cloud Compatible Database Module
Simplified version that works in cloud environment
"""
import sqlite3
import pandas as pd
import os
from typing import List, Dict, Any, Optional

class CloudDatabase:
    """Simplified database connector for Streamlit Cloud"""
    
    def __init__(self):
        self.db_path = self._find_database()
        self.connected = self._test_connection()
    
    def _find_database(self) -> Optional[str]:
        """Find database in cloud environment"""
        paths = ["data/trench.db", "trench.db", "./data/trench.db", "../data/trench.db"]
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def _test_connection(self) -> bool:
        """Test if database is accessible"""
        if not self.db_path:
            return False
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("SELECT 1 FROM coins LIMIT 1")
            conn.close()
            return True
        except:
            return False
    
    def get_all_coins(self) -> List[Dict[str, Any]]:
        """Get all coins with calculated metrics"""
        if not self.connected:
            return self._get_demo_coins()
        
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT 
                ticker,
                ca,
                discovery_price,
                axiom_price,
                ROUND(((axiom_price - discovery_price) / discovery_price * 100), 2) as price_gain_pct,
                smart_wallets,
                liquidity,
                axiom_mc,
                axiom_volume,
                peak_volume,
                discovery_time
            FROM coins 
            WHERE discovery_price > 0 AND axiom_price > 0
            ORDER BY price_gain_pct DESC
            LIMIT 100
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Database error: {e}")
            return self._get_demo_coins()
    
    def get_coin_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.connected:
            return {
                "total_coins": 1733,
                "avg_smart_wallets": 156.7,
                "total_liquidity": 2847500.0,
                "status": "demo_mode"
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get basic stats
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM coins")
            total_coins = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(smart_wallets) FROM coins WHERE smart_wallets > 0")
            avg_smart_wallets = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(liquidity) FROM coins WHERE liquidity > 0")
            total_liquidity = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total_coins": total_coins,
                "avg_smart_wallets": round(avg_smart_wallets, 1),
                "total_liquidity": total_liquidity,
                "status": "connected"
            }
            
        except Exception as e:
            return {
                "total_coins": 0,
                "status": f"error: {e}",
                "avg_smart_wallets": 0,
                "total_liquidity": 0
            }
    
    def _get_demo_coins(self) -> List[Dict[str, Any]]:
        """Fallback demo data when database is not available"""
        return [
            {
                "ticker": "PEPE",
                "ca": "6GCwwBywXgSqUJVNxvL4XJbdMGPsafgX7bqDCKQw45dV",
                "discovery_price": 0.000001234,
                "axiom_price": 0.000004567,
                "price_gain_pct": 270.1,
                "smart_wallets": 1250,
                "liquidity": 2100000.0,
                "axiom_mc": 8200000000.0,
                "axiom_volume": 45600000.0,
                "peak_volume": 67800000.0,
                "discovery_time": "2024-03-15 10:30:00"
            },
            {
                "ticker": "SHIB",
                "ca": "CiKu9eHPBf2PyJ8EQCR8xJ4KnF2KVg7e6B3vW1234567",
                "discovery_price": 0.000008901,
                "axiom_price": 0.000022456,
                "price_gain_pct": 152.3,
                "smart_wallets": 890,
                "liquidity": 5600000.0,
                "axiom_mc": 15100000000.0,
                "axiom_volume": 23400000.0,
                "peak_volume": 89200000.0,
                "discovery_time": "2024-02-20 14:20:00"
            },
            {
                "ticker": "DOGE",
                "ca": "DKxYz8vMJKLNOPQRSTUVWXYZ123456789abcdefghij",
                "discovery_price": 0.067123,
                "axiom_price": 0.127890,
                "price_gain_pct": 90.5,
                "smart_wallets": 2100,
                "liquidity": 12300000.0,
                "axiom_mc": 28700000000.0,
                "axiom_volume": 78900000.0,
                "peak_volume": 234500000.0,
                "discovery_time": "2024-01-10 09:15:00"
            },
            {
                "ticker": "FLOKI",
                "ca": "FLKxYz8vMJKLNOPQRSTUVWXYZ123456789abcdef123",
                "discovery_price": 0.000012345,
                "axiom_price": 0.000034567,
                "price_gain_pct": 180.1,
                "smart_wallets": 670,
                "liquidity": 1800000.0,
                "axiom_mc": 3400000000.0,
                "axiom_volume": 12300000.0,
                "peak_volume": 45600000.0,
                "discovery_time": "2024-04-05 16:45:00"
            },
            {
                "ticker": "BONK",
                "ca": "BNKxYz8vMJKLNOPQRSTUVWXYZ123456789abcdef456",
                "discovery_price": 0.000000567,
                "axiom_price": 0.000000890,
                "price_gain_pct": 57.0,
                "smart_wallets": 450,
                "liquidity": 890000.0,
                "axiom_mc": 1200000000.0,
                "axiom_volume": 5600000.0,
                "peak_volume": 23400000.0,
                "discovery_time": "2024-05-12 11:30:00"
            }
        ]

# Global instance for easy import
cloud_db = CloudDatabase()