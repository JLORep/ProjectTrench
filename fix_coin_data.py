#!/usr/bin/env python3
"""
Fix Coin Data Access for Streamlit Cloud
Creates a simplified database connector that works in cloud environment
"""
import sqlite3
import pandas as pd
import os
from pathlib import Path
import streamlit as st

def get_database_path():
    """Find the correct database path in different environments"""
    possible_paths = [
        "data/trench.db",
        "./data/trench.db", 
        "../data/trench.db",
        "trench.db",
        "./trench.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def test_database_connection():
    """Test database connection and return status"""
    db_path = get_database_path()
    
    if not db_path:
        return False, "Database file not found", None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT COUNT(*) FROM coins")
        count = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Connected successfully - {count} coins found", db_path
        
    except Exception as e:
        return False, f"Connection error: {e}", db_path

def get_coin_data_sample(limit=10):
    """Get sample coin data for display"""
    db_path = get_database_path()
    
    if not db_path:
        return None, "Database not found"
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Get sample data with calculated percentage gains
        query = """
        SELECT 
            ticker,
            discovery_price,
            axiom_price,
            ROUND(((axiom_price - discovery_price) / discovery_price * 100), 2) as price_gain_pct,
            smart_wallets,
            liquidity,
            axiom_mc,
            axiom_volume
        FROM coins 
        WHERE discovery_price > 0 AND axiom_price > 0
        ORDER BY price_gain_pct DESC
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        
        return df, "Success"
        
    except Exception as e:
        return None, f"Query error: {e}"

def create_cloud_compatible_database_module():
    """Create a simplified database module for Streamlit Cloud"""
    
    code = '''#!/usr/bin/env python3
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
        paths = ["data/trench.db", "trench.db", "./data/trench.db"]
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
            return []
        
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
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Database error: {e}")
            return []
    
    def get_coin_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.connected:
            return {"total_coins": 0, "status": "disconnected"}
        
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
            return {"total_coins": 0, "status": f"error: {e}"}

# Global instance for easy import
cloud_db = CloudDatabase()
'''
    
    with open('cloud_database.py', 'w') as f:
        f.write(code)
    
    return True

if __name__ == "__main__":
    st.title("🔧 Database Connection Test")
    
    # Test current database connection
    connected, message, path = test_database_connection()
    
    if connected:
        st.success(f"✅ {message}")
        st.info(f"📍 Database path: {path}")
        
        # Show sample data
        df, status = get_coin_data_sample(10)
        if df is not None:
            st.success(f"✅ Sample data retrieved: {status}")
            st.dataframe(df)
        else:
            st.error(f"❌ Data retrieval failed: {status}")
            
    else:
        st.error(f"❌ {message}")
        if path:
            st.info(f"📍 Attempted path: {path}")
    
    # Create cloud-compatible module
    if st.button("🔧 Create Cloud Database Module"):
        if create_cloud_compatible_database_module():
            st.success("✅ Created cloud_database.py")
        else:
            st.error("❌ Failed to create module")