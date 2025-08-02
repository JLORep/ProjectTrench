#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Database Enricher
Optimizes the database and enriches coins with free APIs
Created: 2025-08-02
"""

import sqlite3
import asyncio
import aiohttp
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics

@dataclass
class CoinData:
    """Represents a coin in the database"""
    address: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    price_usd: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    price_change_24h: Optional[float] = None
    last_updated: Optional[str] = None

class DatabaseOptimizer:
    """Optimizes database structure and performance"""
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        print("Database Optimizer & Mass Enrichment System")
        print("=" * 60)
    
    def analyze_current_database(self) -> Dict[str, Any]:
        """Analyze current database structure and content"""
        print("Analyzing current database...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("PRAGMA table_info(coins)")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute("SELECT COUNT(*) FROM coins")
            total_coins = cursor.fetchone()[0]
            
            # Get sample data
            cursor.execute("SELECT * FROM coins LIMIT 5")
            sample_data = cursor.fetchall()
            
            # Check for NULL values in key columns
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(symbol) as has_symbol,
                    COUNT(name) as has_name,
                    COUNT(price_usd) as has_price,
                    COUNT(volume_24h) as has_volume,
                    COUNT(market_cap) as has_market_cap
                FROM coins
            """)
            data_completeness = cursor.fetchone()
            
            # Check for recently updated data
            cursor.execute("SELECT COUNT(*) FROM coins WHERE last_updated > datetime('now', '-24 hours')")
            recent_updates = cursor.fetchone()[0]
            
            conn.close()
            
            analysis = {
                'total_coins': total_coins,
                'columns': [col[1] for col in columns],
                'column_count': len(columns),
                'data_completeness': {
                    'total': data_completeness[0],
                    'has_symbol': data_completeness[1],
                    'has_name': data_completeness[2],
                    'has_price': data_completeness[3],
                    'has_volume': data_completeness[4],
                    'has_market_cap': data_completeness[5]
                },
                'recent_updates': recent_updates,
                'sample_data': sample_data[:3] if sample_data else []
            }
            
            print(f"Database Analysis Complete:")
            print(f"   • Total coins: {analysis['total_coins']:,}")
            print(f"   • Columns: {analysis['column_count']}")
            print(f"   • Data completeness:")
            print(f"     - Symbols: {analysis['data_completeness']['has_symbol']:,} ({analysis['data_completeness']['has_symbol']/analysis['total_coins']*100:.1f}%)")
            print(f"     - Names: {analysis['data_completeness']['has_name']:,} ({analysis['data_completeness']['has_name']/analysis['total_coins']*100:.1f}%)")
            print(f"     - Prices: {analysis['data_completeness']['has_price']:,} ({analysis['data_completeness']['has_price']/analysis['total_coins']*100:.1f}%)")
            print(f"   • Recent updates (24h): {analysis['recent_updates']:,}")
            
            return analysis
            
        except Exception as e:
            print(f"Database analysis failed: {e}")
            return {}
    
    def optimize_database_structure(self) -> bool:
        """Optimize database structure for better performance"""
        print("\nOptimizing database structure...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create performance indexes
            indexes_to_create = [
                "CREATE INDEX IF NOT EXISTS idx_symbol ON coins(symbol)",
                "CREATE INDEX IF NOT EXISTS idx_price ON coins(price_usd)",
                "CREATE INDEX IF NOT EXISTS idx_volume ON coins(volume_24h)",
                "CREATE INDEX IF NOT EXISTS idx_market_cap ON coins(market_cap)",
                "CREATE INDEX IF NOT EXISTS idx_last_updated ON coins(last_updated)",
                "CREATE INDEX IF NOT EXISTS idx_api_confidence ON coins(api_confidence_score)",
                "CREATE INDEX IF NOT EXISTS idx_price_change ON coins(price_change_24h)"
            ]
            
            for index_sql in indexes_to_create:
                try:
                    cursor.execute(index_sql)
                    index_name = index_sql.split()[5]  # Extract index name
                    print(f"   Created index: {index_name}")
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"   Index creation warning: {e}")
            
            # Add additional useful columns if they don't exist
            additional_columns = [
                "price_change_7d REAL",
                "price_change_30d REAL", 
                "all_time_high REAL",
                "all_time_low REAL",
                "circulating_supply REAL",
                "total_supply REAL",
                "max_supply REAL",
                "market_cap_rank INTEGER",
                "fully_diluted_valuation REAL",
                "social_score REAL",
                "security_score REAL",
                "whale_activity_score REAL",
                "technical_analysis_score REAL",
                "developer_activity_score REAL",
                "data_quality_score REAL",
                "enrichment_timestamp TEXT",
                "api_response_time_ms INTEGER",
                "data_source_count INTEGER DEFAULT 0"
            ]
            
            for column_def in additional_columns:
                column_name = column_def.split()[0]
                try:
                    cursor.execute(f"ALTER TABLE coins ADD COLUMN {column_def}")
                    print(f"   Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"   Column warning: {e}")
            
            # Optimize database file
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            
            conn.commit()
            conn.close()
            
            print("Database optimization complete!")
            return True
            
        except Exception as e:
            print(f"Database optimization failed: {e}")
            return False
    
    def backup_database(self) -> str:
        """Create backup of current database"""
        print("\nCreating database backup...")
        
        try:
            import shutil
            backup_name = f"trench_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = f"data/{backup_name}"
            
            shutil.copy2(self.db_path, backup_path)
            print(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"Backup failed: {e}")
            return ""

class SimpleEnricher:
    """Simple enrichment system using free APIs"""
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.session = None
        self.enrichment_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'api_calls_made': 0,
            'data_points_added': 0,
            'start_time': None,
            'errors': []
        }
        
        # Simple free APIs we can use
        self.free_apis = {
            'dexscreener': {
                'url': 'https://api.dexscreener.com/latest/dex/tokens/{address}',
                'rate_limit': 1,
                'max_per_minute': 300
            }
        }
    
    async def initialize(self):
        """Initialize the enrichment system"""
        print("\nInitializing Simple Enrichment System...")
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        self.enrichment_stats['start_time'] = time.time()
        
        print("Enrichment system ready!")
    
    async def shutdown(self):
        """Shutdown the enrichment system"""
        if self.session:
            await self.session.close()
    
    async def enrich_single_coin(self, coin_address: str, coin_symbol: str = None) -> Dict[str, Any]:
        """Enrich a single coin with data from DexScreener"""
        enriched_data = {
            'address': coin_address,
            'symbol': coin_symbol,
            'success': False,
            'apis_used': [],
            'data_points': {},
            'errors': []
        }
        
        # Try DexScreener (good for Solana tokens)
        if coin_address and len(coin_address) > 20:  # Looks like Solana address
            try:
                await asyncio.sleep(self.free_apis['dexscreener']['rate_limit'])
                
                url = self.free_apis['dexscreener']['url'].format(address=coin_address)
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.enrichment_stats['api_calls_made'] += 1
                        
                        if 'pairs' in data and data['pairs']:
                            pair = data['pairs'][0]
                            base_token = pair.get('baseToken', {})
                            
                            # Extract data
                            if 'priceUsd' in pair:
                                enriched_data['data_points']['price_usd'] = float(pair['priceUsd'])
                            if 'volume' in pair and 'h24' in pair['volume']:
                                enriched_data['data_points']['volume_24h'] = float(pair['volume']['h24'])
                            if 'priceChange' in pair and 'h24' in pair['priceChange']:
                                enriched_data['data_points']['price_change_24h'] = float(pair['priceChange']['h24'])
                            if 'liquidity' in pair and 'usd' in pair['liquidity']:
                                enriched_data['data_points']['liquidity_usd'] = float(pair['liquidity']['usd'])
                            
                            # Token info
                            if not enriched_data['symbol'] and 'symbol' in base_token:
                                enriched_data['symbol'] = base_token['symbol']
                            if 'name' in base_token:
                                enriched_data['data_points']['name'] = base_token['name']
                            
                            enriched_data['apis_used'].append('dexscreener')
                            enriched_data['success'] = True
                            
                            print(f"   DexScreener: {enriched_data['symbol']} = ${enriched_data['data_points'].get('price_usd', 'N/A')}")
                            
            except Exception as e:
                enriched_data['errors'].append(f"DexScreener: {str(e)}")
        
        # Calculate data quality score
        data_points_count = len(enriched_data['data_points'])
        api_count = len(enriched_data['apis_used'])
        enriched_data['data_quality_score'] = min(1.0, (data_points_count * 0.1) + (api_count * 0.2))
        
        self.enrichment_stats['data_points_added'] += data_points_count
        
        return enriched_data
    
    async def enrich_batch(self, coins: List[Tuple[str, str]], batch_size: int = 5) -> List[Dict[str, Any]]:
        """Enrich a batch of coins with rate limiting"""
        print(f"\nEnriching batch of {len(coins)} coins...")
        
        results = []
        
        # Process in smaller batches to respect rate limits
        for i in range(0, len(coins), batch_size):
            batch = coins[i:i + batch_size]
            
            # Create tasks for concurrent processing
            tasks = []
            for address, symbol in batch:
                task = asyncio.create_task(self.enrich_single_coin(address, symbol))
                tasks.append(task)
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    print(f"   Error processing {batch[j][0]}: {result}")
                    self.enrichment_stats['failed'] += 1
                    self.enrichment_stats['errors'].append(str(result))
                else:
                    results.append(result)
                    if result['success']:
                        self.enrichment_stats['successful'] += 1
                    else:
                        self.enrichment_stats['failed'] += 1
                
                self.enrichment_stats['total_processed'] += 1
            
            # Progress update
            progress = (i + len(batch)) / len(coins) * 100
            print(f"   Progress: {progress:.1f}% ({i + len(batch)}/{len(coins)})")
            
            # Rate limiting pause between batches
            if i + batch_size < len(coins):
                await asyncio.sleep(2)  # 2 second pause between batches
        
        return results
    
    def update_database_with_enriched_data(self, enriched_results: List[Dict[str, Any]]) -> int:
        """Update database with enriched data"""
        print(f"\nUpdating database with {len(enriched_results)} enriched records...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updated_count = 0
            
            for result in enriched_results:
                if result['success'] and result['data_points']:
                    address = result['address']
                    data_points = result['data_points']
                    
                    # Build update query dynamically
                    update_fields = []
                    update_values = []
                    
                    # Map API data to database columns
                    field_mapping = {
                        'price_usd': 'price_usd',
                        'volume_24h': 'volume_24h',
                        'price_change_24h': 'price_change_24h',
                        'name': 'name',
                        'liquidity_usd': 'liquidity_usd'
                    }
                    
                    for api_field, db_field in field_mapping.items():
                        if api_field in data_points:
                            update_fields.append(f"{db_field} = ?")
                            update_values.append(data_points[api_field])
                    
                    # Add metadata
                    update_fields.extend([
                        "api_sources_count = ?",
                        "last_api_update = ?",
                        "api_confidence_score = ?",
                        "data_source_count = ?",
                        "enrichment_timestamp = ?"
                    ])
                    
                    update_values.extend([
                        len(result['apis_used']),
                        datetime.now().isoformat(),
                        result.get('data_quality_score', 0.0),
                        len(result['data_points']),
                        datetime.now().isoformat()
                    ])
                    
                    # Add symbol if we got it and it's missing
                    if result['symbol'] and result['symbol'] != 'None':
                        update_fields.append("symbol = ?")
                        update_values.append(result['symbol'])
                    
                    update_values.append(address)  # For WHERE clause
                    
                    if update_fields:
                        query = f"UPDATE coins SET {', '.join(update_fields)} WHERE address = ?"
                        cursor.execute(query, update_values)
                        
                        if cursor.rowcount > 0:
                            updated_count += 1
            
            conn.commit()
            conn.close()
            
            print(f"Database updated: {updated_count} coins enriched")
            return updated_count
            
        except Exception as e:
            print(f"Database update failed: {e}")
            return 0
    
    def print_enrichment_summary(self):
        """Print comprehensive enrichment summary"""
        if self.enrichment_stats['start_time']:
            duration = time.time() - self.enrichment_stats['start_time']
        else:
            duration = 0
        
        print("\n" + "=" * 60)
        print("SIMPLE ENRICHMENT SUMMARY")
        print("=" * 60)
        
        print(f"Duration: {duration:.1f} seconds")
        print(f"Total Processed: {self.enrichment_stats['total_processed']:,}")
        print(f"Successful: {self.enrichment_stats['successful']:,}")
        print(f"Failed: {self.enrichment_stats['failed']:,}")
        print(f"API Calls Made: {self.enrichment_stats['api_calls_made']:,}")
        print(f"Data Points Added: {self.enrichment_stats['data_points_added']:,}")
        
        if self.enrichment_stats['total_processed'] > 0:
            success_rate = (self.enrichment_stats['successful'] / self.enrichment_stats['total_processed']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        if duration > 0:
            rate = self.enrichment_stats['total_processed'] / duration
            print(f"Processing Rate: {rate:.1f} coins/second")

async def main():
    """Main function to optimize and enrich database"""
    
    # Step 1: Initialize systems
    optimizer = DatabaseOptimizer()
    enricher = SimpleEnricher()
    
    # Step 2: Analyze current database
    analysis = optimizer.analyze_current_database()
    if not analysis:
        print("Cannot proceed without database analysis")
        return 1
    
    # Step 3: Create backup
    backup_path = optimizer.backup_database()
    if not backup_path:
        print("Continuing without backup...")
    
    # Step 4: Optimize database structure
    if not optimizer.optimize_database_structure():
        print("Database optimization failed")
        return 1
    
    # Step 5: Initialize enrichment system
    await enricher.initialize()
    
    try:
        # Step 6: Get coins to enrich
        print(f"\nPreparing to enrich up to 100 coins from {analysis['total_coins']:,} total...")
        
        conn = sqlite3.connect(enricher.db_path)
        cursor = conn.cursor()
        
        # Get coins that need enrichment (limit to 100 for this test)
        cursor.execute("""
            SELECT address, symbol 
            FROM coins 
            WHERE last_api_update IS NULL 
               OR last_api_update < datetime('now', '-7 days')
               OR price_usd IS NULL
            ORDER BY 
                CASE WHEN price_usd IS NULL THEN 0 ELSE 1 END,
                CASE WHEN last_api_update IS NULL THEN 0 ELSE 1 END,
                RANDOM()
            LIMIT 100
        """)
        
        coins_to_enrich = cursor.fetchall()
        conn.close()
        
        if not coins_to_enrich:
            print("All coins are already up to date!")
            return 0
        
        print(f"Found {len(coins_to_enrich)} coins that need enrichment")
        
        # Step 7: Perform enrichment
        print("\nStarting enrichment process...")
        print("   This will take several minutes due to API rate limits...")
        
        enriched_results = await enricher.enrich_batch(coins_to_enrich, batch_size=3)
        
        # Step 8: Update database
        updated_count = enricher.update_database_with_enriched_data(enriched_results)
        
        # Step 9: Print summary
        enricher.print_enrichment_summary()
        
        print(f"\nENRICHMENT COMPLETE!")
        print(f"Database optimized and {updated_count:,} coins enriched with fresh data!")
        print(f"Your TrenchCoat Pro database is now enhanced!")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nEnrichment interrupted by user")
        enricher.print_enrichment_summary()
        return 1
        
    except Exception as e:
        print(f"\nEnrichment failed: {e}")
        return 1
        
    finally:
        await enricher.shutdown()

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))