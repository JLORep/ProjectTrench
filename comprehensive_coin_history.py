#!/usr/bin/env python3
"""
TrenchCoat Pro - Comprehensive Coin History Tracker
Full historical data collection from all available API sources
"""
import asyncio
import sqlite3
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

from src.data.free_api_providers import FreeAPIProviders
from unicode_handler import safe_print

@dataclass
class CoinHistoryRecord:
    """Complete historical record for a coin"""
    ticker: str
    contract_address: str
    timestamp: datetime
    price_usd: float
    volume_24h: float
    market_cap: float
    liquidity: float
    holders: int
    price_change_24h: float
    data_sources: List[str]
    security_score: float
    social_metrics: Dict[str, Any]
    enrichment_score: float

class ComprehensiveCoinHistoryTracker:
    """Track complete history of any coin with all available data"""
    
    def __init__(self):
        self.db_path = "data/trench.db"
        self.history_db_path = "data/coin_history.db"
        self.api_providers = None
        self.init_history_database()
    
    def init_history_database(self):
        """Initialize comprehensive history database"""
        conn = sqlite3.connect(self.history_db_path)
        cursor = conn.cursor()
        
        # Main history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coin_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                contract_address TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                price_usd REAL,
                volume_24h REAL,
                market_cap REAL,
                liquidity REAL,
                holders INTEGER,
                price_change_24h REAL,
                price_change_1h REAL,
                price_change_5m REAL,
                data_sources TEXT,
                enrichment_score REAL,
                security_score REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(contract_address, timestamp)
            )
        """)
        
        # Price history table (high-frequency data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_address TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                price REAL NOT NULL,
                volume REAL,
                source TEXT NOT NULL,
                UNIQUE(contract_address, timestamp, source)
            )
        """)
        
        # Security analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_address TEXT NOT NULL,
                is_honeypot BOOLEAN,
                buy_tax REAL,
                sell_tax REAL,
                is_mintable BOOLEAN,
                is_proxy BOOLEAN,
                creator_address TEXT,
                creator_percent REAL,
                holder_count INTEGER,
                security_score REAL,
                analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(contract_address, analyzed_at)
            )
        """)
        
        # Social data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS social_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_address TEXT NOT NULL,
                name TEXT,
                description TEXT,
                twitter TEXT,
                telegram TEXT,
                website TEXT,
                created_timestamp INTEGER,
                reply_count INTEGER,
                social_score REAL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(contract_address)
            )
        """)
        
        # Trading activity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_address TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                unique_wallets_24h INTEGER,
                trades_24h INTEGER,
                buys_24h INTEGER,
                sells_24h INTEGER,
                buy_sell_ratio REAL,
                smart_wallet_activity INTEGER,
                UNIQUE(contract_address, timestamp)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_address_time ON coin_history(contract_address, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_address_time ON price_history(contract_address, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_address ON security_analysis(contract_address)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_social_address ON social_data(contract_address)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trading_address_time ON trading_activity(contract_address, timestamp)")
        
        conn.commit()
        conn.close()
        
        safe_print("✅ Comprehensive coin history database initialized")
    
    async def get_full_coin_history(self, ticker: str, contract_address: str, days: int = 30) -> Dict[str, Any]:
        """Get complete historical data for a coin"""
        safe_print(f"🔍 Collecting full history for {ticker} ({days} days)...")
        
        async with FreeAPIProviders() as api:
            # Get comprehensive historical data
            history_data = await api.get_comprehensive_historical_data(
                contract_address=contract_address,
                symbol=ticker,
                days=days
            )
            
            # Store in database
            await self.store_historical_data(ticker, contract_address, history_data)
            
            return history_data
    
    async def store_historical_data(self, ticker: str, contract_address: str, history_data: Dict[str, Any]):
        """Store comprehensive historical data in database"""
        conn = sqlite3.connect(self.history_db_path)
        cursor = conn.cursor()
        
        try:
            # Store main history record
            current_snapshot = history_data.get('current_snapshot', {})
            cursor.execute("""
                INSERT OR REPLACE INTO coin_history 
                (ticker, contract_address, timestamp, price_usd, volume_24h, market_cap, 
                 liquidity, holders, price_change_24h, data_sources, enrichment_score, security_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticker,
                contract_address,
                datetime.now(),
                current_snapshot.get('price', 0),
                current_snapshot.get('volume_24h', 0),
                current_snapshot.get('market_cap', 0),
                current_snapshot.get('liquidity', 0),
                current_snapshot.get('total_holders', 0),
                current_snapshot.get('price_change_24h', 0),
                json.dumps(history_data.get('data_sources', [])),
                history_data.get('enrichment_score', 0),
                self.calculate_security_score(history_data.get('security_analysis', {}))
            ))
            
            # Store price history points
            for price_point in history_data.get('price_history', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO price_history 
                    (contract_address, timestamp, price, volume, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    contract_address,
                    price_point.get('timestamp', 0),
                    price_point.get('price', 0),
                    price_point.get('volume_24h', 0),
                    price_point.get('source', 'unknown')
                ))
            
            # Store security analysis
            security_data = history_data.get('security_analysis', {})
            if security_data:
                cursor.execute("""
                    INSERT OR REPLACE INTO security_analysis
                    (contract_address, is_honeypot, buy_tax, sell_tax, is_mintable, 
                     is_proxy, creator_address, creator_percent, holder_count, security_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contract_address,
                    security_data.get('is_honeypot', False),
                    security_data.get('buy_tax', 0),
                    security_data.get('sell_tax', 0),
                    security_data.get('is_mintable', False),
                    security_data.get('is_proxy', False),
                    security_data.get('creator_address', ''),
                    security_data.get('creator_percent', 0),
                    security_data.get('holder_count', 0),
                    self.calculate_security_score(security_data)
                ))
            
            # Store social data
            social_data = history_data.get('social_data', {})
            if social_data:
                cursor.execute("""
                    INSERT OR REPLACE INTO social_data
                    (contract_address, name, description, twitter, telegram, website,
                     created_timestamp, reply_count, social_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contract_address,
                    social_data.get('name', ''),
                    social_data.get('description', ''),
                    social_data.get('twitter', ''),
                    social_data.get('telegram', ''),
                    social_data.get('website', ''),
                    social_data.get('created_timestamp', 0),
                    social_data.get('reply_count', 0),
                    self.calculate_social_score(social_data)
                ))
            
            conn.commit()
            safe_print(f"✅ Stored comprehensive history for {ticker}")
            
        except Exception as e:
            safe_print(f"❌ Error storing history for {ticker}: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def calculate_security_score(self, security_data: Dict[str, Any]) -> float:
        """Calculate security score from 0-100"""
        if not security_data:
            return 50.0  # Neutral score
        
        score = 100.0
        
        # Negative factors
        if security_data.get('is_honeypot'):
            score -= 40
        if security_data.get('buy_tax', 0) > 5:
            score -= 15
        if security_data.get('sell_tax', 0) > 5:
            score -= 15
        if security_data.get('is_mintable'):
            score -= 10
        if security_data.get('is_proxy'):
            score -= 10
        if security_data.get('creator_percent', 0) > 20:
            score -= 10
        
        return max(0, min(100, score))
    
    def calculate_social_score(self, social_data: Dict[str, Any]) -> float:
        """Calculate social engagement score from 0-100"""
        if not social_data:
            return 0
        
        score = 0
        
        # Positive factors
        if social_data.get('twitter'):
            score += 25
        if social_data.get('telegram'):
            score += 25
        if social_data.get('website'):
            score += 20
        if social_data.get('description'):
            score += 15
        if social_data.get('reply_count', 0) > 10:
            score += 15
        
        return min(100, score)
    
    def get_coin_history_summary(self, contract_address: str) -> Dict[str, Any]:
        """Get historical summary for a coin"""
        conn = sqlite3.connect(self.history_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get latest record
            cursor.execute("""
                SELECT * FROM coin_history 
                WHERE contract_address = ?
                ORDER BY timestamp DESC LIMIT 1
            """, (contract_address,))
            latest = cursor.fetchone()
            
            # Get price history count
            cursor.execute("""
                SELECT COUNT(*) as count, MIN(timestamp) as first_seen
                FROM price_history WHERE contract_address = ?
            """, (contract_address,))
            price_stats = cursor.fetchone()
            
            # Get security analysis
            cursor.execute("""
                SELECT * FROM security_analysis 
                WHERE contract_address = ?
                ORDER BY analyzed_at DESC LIMIT 1
            """, (contract_address,))
            security = cursor.fetchone()
            
            # Get social data
            cursor.execute("""
                SELECT * FROM social_data 
                WHERE contract_address = ?
            """, (contract_address,))
            social = cursor.fetchone()
            
            summary = {
                'contract_address': contract_address,
                'tracking_status': 'active' if latest else 'not_tracked',
                'history_depth': price_stats['count'] if price_stats else 0,
                'first_seen': price_stats['first_seen'] if price_stats else None,
                'latest_data': dict(latest) if latest else None,
                'security_analysis': dict(security) if security else None,
                'social_data': dict(social) if social else None,
                'last_updated': latest['timestamp'] if latest else None
            }
            
            return summary
            
        except Exception as e:
            safe_print(f"❌ Error getting history summary: {e}")
            return {'error': str(e)}
        finally:
            conn.close()
    
    def get_all_tracked_coins(self) -> List[Dict[str, Any]]:
        """Get list of all tracked coins with summary stats"""
        conn = sqlite3.connect(self.history_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    ticker,
                    contract_address,
                    COUNT(*) as history_count,
                    MAX(timestamp) as last_updated,
                    AVG(enrichment_score) as avg_enrichment,
                    AVG(security_score) as avg_security
                FROM coin_history
                GROUP BY contract_address
                ORDER BY last_updated DESC
            """)
            
            coins = []
            for row in cursor.fetchall():
                coins.append(dict(row))
            
            return coins
            
        except Exception as e:
            safe_print(f"❌ Error getting tracked coins: {e}")
            return []
        finally:
            conn.close()
    
    async def bulk_collect_history(self, coin_list: List[Dict[str, str]], days: int = 7):
        """Collect history for multiple coins"""
        safe_print(f"🚀 Starting bulk history collection for {len(coin_list)} coins ({days} days each)")
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        async with FreeAPIProviders() as api:
            for i, coin in enumerate(coin_list, 1):
                ticker = coin.get('ticker', 'UNKNOWN')
                contract_address = coin.get('ca', coin.get('contract_address', ''))
                
                if not contract_address or contract_address == 'N/A':
                    safe_print(f"⚠️ Skipping {ticker} - no contract address")
                    continue
                
                try:
                    safe_print(f"📊 Processing {i}/{len(coin_list)}: {ticker}")
                    
                    # Get comprehensive historical data
                    history_data = await api.get_comprehensive_historical_data(
                        contract_address=contract_address,
                        symbol=ticker,
                        days=days
                    )
                    
                    # Store in database
                    await self.store_historical_data(ticker, contract_address, history_data)
                    
                    results['successful'] += 1
                    safe_print(f"✅ {ticker}: {len(history_data.get('data_sources', []))} sources, {history_data.get('enrichment_score', 0):.1%} enrichment")
                    
                except Exception as e:
                    safe_print(f"❌ Failed to process {ticker}: {e}")
                    results['failed'] += 1
                    results['errors'].append(f"{ticker}: {e}")
                
                results['processed'] += 1
                
                # Rate limiting
                await asyncio.sleep(2)
        
        safe_print(f"🎉 Bulk collection complete: {results['successful']}/{results['processed']} successful")
        return results

async def main():
    """Main execution for comprehensive coin history tracking"""
    tracker = ComprehensiveCoinHistoryTracker()
    
    safe_print("🚀 TrenchCoat Pro - Comprehensive Coin History Tracker")
    safe_print("=" * 60)
    
    # Get coins from main database
    conn = sqlite3.connect("data/trench.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ticker, ca 
        FROM coins 
        WHERE ticker IS NOT NULL AND ca IS NOT NULL AND ca != 'N/A'
        ORDER BY smart_wallets DESC, liquidity DESC
        LIMIT 50
    """)
    
    coins = [{'ticker': row[0], 'ca': row[1]} for row in cursor.fetchall()]
    conn.close()
    
    if not coins:
        safe_print("❌ No coins found in database")
        return
    
    safe_print(f"📊 Found {len(coins)} coins to track")
    
    # Collect comprehensive history
    results = await tracker.bulk_collect_history(coins, days=30)
    
    # Show summary
    tracked_coins = tracker.get_all_tracked_coins()
    
    safe_print(f"\n📈 History Collection Summary:")
    safe_print(f"   • Coins processed: {results['processed']}")
    safe_print(f"   • Successfully tracked: {results['successful']}")
    safe_print(f"   • Failed: {results['failed']}")
    safe_print(f"   • Total coins in history DB: {len(tracked_coins)}")
    
    # Show top enriched coins
    if tracked_coins:
        safe_print(f"\n🏆 Top Enriched Coins:")
        for coin in sorted(tracked_coins, key=lambda x: x['avg_enrichment'] or 0, reverse=True)[:10]:
            safe_print(f"   • {coin['ticker']}: {(coin['avg_enrichment'] or 0):.1%} enrichment, {coin['history_count']} records")

if __name__ == "__main__":
    asyncio.run(main())