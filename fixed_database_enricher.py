#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed Database Enricher for TrenchCoat Pro
Works with actual database schema (ca, ticker columns)
Created: 2025-08-02
"""

import sqlite3
import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CoinData:
    """Represents a coin in the actual database"""
    ca: str  # Contract address
    ticker: Optional[str] = None
    discovery_price: Optional[float] = None
    liquidity: Optional[float] = None
    peak_volume: Optional[float] = None
    smart_wallets: Optional[int] = None

class DatabaseOptimizer:
    """Optimizes database structure and performance"""
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        print("TrenchCoat Pro Database Optimizer & Enricher")
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
            cursor.execute("SELECT * FROM coins LIMIT 3")
            sample_data = cursor.fetchall()
            
            # Check for NULL values in key columns
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(ticker) as has_ticker,
                    COUNT(ca) as has_ca,
                    COUNT(discovery_price) as has_price,
                    COUNT(liquidity) as has_liquidity,
                    COUNT(peak_volume) as has_volume
                FROM coins
            """)
            data_completeness = cursor.fetchone()
            
            # Check for recently updated data (if column exists)
            try:
                cursor.execute("SELECT COUNT(*) FROM coins WHERE last_api_update > datetime('now', '-24 hours')")
                recent_updates = cursor.fetchone()[0]
            except:
                recent_updates = 0
            
            conn.close()
            
            analysis = {
                'total_coins': total_coins,
                'columns': [col[1] for col in columns],
                'column_count': len(columns),
                'data_completeness': {
                    'total': data_completeness[0],
                    'has_ticker': data_completeness[1],
                    'has_ca': data_completeness[2],
                    'has_price': data_completeness[3],
                    'has_liquidity': data_completeness[4],
                    'has_volume': data_completeness[5]
                },
                'recent_updates': recent_updates,
                'sample_data': sample_data[:3] if sample_data else []
            }
            
            print(f"Database Analysis Complete:")
            print(f"   Total coins: {analysis['total_coins']:,}")
            print(f"   Columns: {analysis['column_count']}")
            print(f"   Column names: {', '.join(analysis['columns'][:10])}...")
            print(f"   Data completeness:")
            print(f"     - Tickers: {analysis['data_completeness']['has_ticker']:,} ({analysis['data_completeness']['has_ticker']/analysis['total_coins']*100:.1f}%)")
            print(f"     - Contract Addresses: {analysis['data_completeness']['has_ca']:,} ({analysis['data_completeness']['has_ca']/analysis['total_coins']*100:.1f}%)")
            print(f"     - Prices: {analysis['data_completeness']['has_price']:,} ({analysis['data_completeness']['has_price']/analysis['total_coins']*100:.1f}%)")
            print(f"   Recent API updates (24h): {analysis['recent_updates']:,}")
            
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
            
            # Create performance indexes on existing columns
            indexes_to_create = [
                "CREATE INDEX IF NOT EXISTS idx_ticker ON coins(ticker)",
                "CREATE INDEX IF NOT EXISTS idx_ca ON coins(ca)", 
                "CREATE INDEX IF NOT EXISTS idx_discovery_price ON coins(discovery_price)",
                "CREATE INDEX IF NOT EXISTS idx_liquidity ON coins(liquidity)",
                "CREATE INDEX IF NOT EXISTS idx_peak_volume ON coins(peak_volume)",
                "CREATE INDEX IF NOT EXISTS idx_smart_wallets ON coins(smart_wallets)",
                "CREATE INDEX IF NOT EXISTS idx_last_api_update ON coins(last_api_update)"
            ]
            
            for index_sql in indexes_to_create:
                try:
                    cursor.execute(index_sql)
                    index_name = index_sql.split()[5]  # Extract index name
                    print(f"   Created index: {index_name}")
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"   Index creation warning: {e}")
            
            # Add enrichment tracking columns if they don't exist
            enrichment_columns = [
                "current_price_usd REAL",
                "current_volume_24h REAL",
                "price_change_24h REAL",
                "market_cap_usd REAL",
                "fdv_usd REAL",
                "enrichment_timestamp TEXT",
                "api_response_time_ms INTEGER",
                "data_quality_score REAL DEFAULT 0.0",
                "last_enrichment_success INTEGER DEFAULT 0"
            ]
            
            for column_def in enrichment_columns:
                column_name = column_def.split()[0]
                try:
                    cursor.execute(f"ALTER TABLE coins ADD COLUMN {column_def}")
                    print(f"   Added enrichment column: {column_name}")
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

class CoinEnricher:
    """Enriches coins using free APIs"""
    
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
    
    async def initialize(self):
        """Initialize the enrichment system"""
        print("\nInitializing Coin Enrichment System...")
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        self.enrichment_stats['start_time'] = time.time()
        
        print("Enrichment system ready!")
    
    async def shutdown(self):
        """Shutdown the enrichment system"""
        if self.session:
            await self.session.close()
    
    async def enrich_coin_with_dexscreener(self, contract_address: str, ticker: str = None) -> Dict[str, Any]:
        """Enrich a coin using DexScreener API"""
        enriched_data = {
            'ca': contract_address,
            'ticker': ticker,
            'success': False,
            'data_points': {},
            'errors': []
        }
        
        if not contract_address or len(contract_address) < 20:
            enriched_data['errors'].append("Invalid contract address")
            return enriched_data
        
        try:
            # Rate limiting
            await asyncio.sleep(1)
            
            url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self.enrichment_stats['api_calls_made'] += 1
                    
                    if 'pairs' in data and data['pairs']:
                        # Get the best pair (usually the first one)
                        pair = data['pairs'][0]
                        
                        # Extract price data
                        if 'priceUsd' in pair and pair['priceUsd']:
                            try:
                                enriched_data['data_points']['current_price_usd'] = float(pair['priceUsd'])
                            except (ValueError, TypeError):
                                pass
                        
                        # Extract volume data
                        if 'volume' in pair and pair['volume'] and 'h24' in pair['volume']:
                            try:
                                enriched_data['data_points']['current_volume_24h'] = float(pair['volume']['h24'])
                            except (ValueError, TypeError):
                                pass
                        
                        # Extract price change
                        if 'priceChange' in pair and pair['priceChange'] and 'h24' in pair['priceChange']:
                            try:
                                enriched_data['data_points']['price_change_24h'] = float(pair['priceChange']['h24'])
                            except (ValueError, TypeError):
                                pass
                        
                        # Extract market cap
                        if 'marketCap' in pair and pair['marketCap']:
                            try:
                                enriched_data['data_points']['market_cap_usd'] = float(pair['marketCap'])
                            except (ValueError, TypeError):
                                pass
                        
                        # Extract FDV
                        if 'fdv' in pair and pair['fdv']:
                            try:
                                enriched_data['data_points']['fdv_usd'] = float(pair['fdv'])
                            except (ValueError, TypeError):
                                pass
                                
                        # Get ticker if we don't have it
                        if not enriched_data['ticker']:
                            base_token = pair.get('baseToken', {})
                            if 'symbol' in base_token:
                                enriched_data['ticker'] = base_token['symbol']
                        
                        if enriched_data['data_points']:
                            enriched_data['success'] = True
                            price_str = f"${enriched_data['data_points'].get('current_price_usd', 'N/A')}"
                            print(f"   {enriched_data['ticker'] or 'Unknown'}: {price_str}")
                        
                elif response.status == 429:
                    enriched_data['errors'].append("Rate limited")
                    await asyncio.sleep(5)  # Wait longer on rate limit
                else:
                    enriched_data['errors'].append(f"HTTP {response.status}")
                    
        except asyncio.TimeoutError:
            enriched_data['errors'].append("Timeout")
        except Exception as e:
            enriched_data['errors'].append(f"Error: {str(e)}")
        
        return enriched_data
    
    async def enrich_batch(self, coins: List[Tuple[str, str]], batch_size: int = 3) -> List[Dict[str, Any]]:
        """Enrich a batch of coins with rate limiting"""
        print(f"\nEnriching batch of {len(coins)} coins...")
        
        results = []
        
        # Process in small batches to respect rate limits
        for i in range(0, len(coins), batch_size):
            batch = coins[i:i + batch_size]
            
            # Process each coin in the batch
            for ca, ticker in batch:
                try:
                    result = await self.enrich_coin_with_dexscreener(ca, ticker)
                    results.append(result)
                    
                    if result['success']:
                        self.enrichment_stats['successful'] += 1
                        self.enrichment_stats['data_points_added'] += len(result['data_points'])
                    else:
                        self.enrichment_stats['failed'] += 1
                        if result['errors']:
                            self.enrichment_stats['errors'].extend(result['errors'])
                    
                    self.enrichment_stats['total_processed'] += 1
                    
                except Exception as e:
                    print(f"   Error processing {ca}: {e}")
                    self.enrichment_stats['failed'] += 1
                    self.enrichment_stats['errors'].append(str(e))
                    self.enrichment_stats['total_processed'] += 1
            
            # Progress update
            progress = (i + len(batch)) / len(coins) * 100
            print(f"   Progress: {progress:.1f}% ({i + len(batch)}/{len(coins)})")
            
            # Rate limiting pause between batches
            if i + batch_size < len(coins):
                await asyncio.sleep(3)  # 3 second pause between batches
        
        return results
    
    def update_database_with_enriched_data(self, enriched_results: List[Dict[str, Any]]) -> int:
        """Update database with enriched data"""
        print(f"\nUpdating database with enriched data...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updated_count = 0
            
            for result in enriched_results:
                if result['success'] and result['data_points']:
                    ca = result['ca']
                    data_points = result['data_points']
                    
                    # Build update query dynamically
                    update_fields = []
                    update_values = []
                    
                    # Map enriched data to database columns
                    for field_name, value in data_points.items():
                        if value is not None:
                            update_fields.append(f"{field_name} = ?")
                            update_values.append(value)
                    
                    # Add metadata
                    update_fields.extend([
                        "enrichment_timestamp = ?",
                        "data_quality_score = ?",
                        "last_enrichment_success = ?",
                        "last_api_update = ?"
                    ])
                    
                    data_quality = min(1.0, len(data_points) * 0.2)  # 0.2 per data point
                    
                    update_values.extend([
                        datetime.now().isoformat(),
                        data_quality,
                        1,  # Success flag
                        datetime.now().isoformat()
                    ])
                    
                    # Update ticker if we got a better one
                    if result['ticker']:
                        update_fields.append("ticker = ?")
                        update_values.append(result['ticker'])
                    
                    update_values.append(ca)  # For WHERE clause
                    
                    if update_fields:
                        query = f"UPDATE coins SET {', '.join(update_fields)} WHERE ca = ?"
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
        print("COIN ENRICHMENT SUMMARY")
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
        
        # Show common errors
        if self.enrichment_stats['errors']:
            error_counts = {}
            for error in self.enrichment_stats['errors'][:20]:  # Show first 20 errors
                error_type = error.split(':')[0] if ':' in error else error[:30]
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            print(f"\nCommon Issues:")
            for error_type, count in list(error_counts.items())[:5]:
                print(f"   {error_type}: {count} occurrences")

async def main():
    """Main function to optimize and enrich database"""
    
    # Step 1: Initialize systems
    optimizer = DatabaseOptimizer()
    enricher = CoinEnricher()
    
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
        print(f"\nSelecting coins for enrichment from {analysis['total_coins']:,} total...")
        
        conn = sqlite3.connect(enricher.db_path)
        cursor = conn.cursor()
        
        # Get coins that need enrichment (limit to 50 for this run)
        cursor.execute("""
            SELECT ca, ticker 
            FROM coins 
            WHERE ca IS NOT NULL 
            AND LENGTH(ca) > 20
            AND (last_enrichment_success IS NULL OR last_enrichment_success = 0
                 OR enrichment_timestamp IS NULL 
                 OR enrichment_timestamp < datetime('now', '-7 days'))
            ORDER BY 
                CASE WHEN current_price_usd IS NULL THEN 0 ELSE 1 END,
                CASE WHEN enrichment_timestamp IS NULL THEN 0 ELSE 1 END,
                RANDOM()
            LIMIT 50
        """)
        
        coins_to_enrich = cursor.fetchall()
        conn.close()
        
        if not coins_to_enrich:
            print("No coins found that need enrichment!")
            return 0
        
        print(f"Found {len(coins_to_enrich)} coins that need enrichment")
        
        # Step 7: Perform enrichment
        print("\nStarting enrichment process...")
        print("   Using DexScreener API with rate limiting...")
        
        enriched_results = await enricher.enrich_batch(coins_to_enrich, batch_size=2)
        
        # Step 8: Update database
        updated_count = enricher.update_database_with_enriched_data(enriched_results)
        
        # Step 9: Print summary
        enricher.print_enrichment_summary()
        
        print(f"\nENRICHMENT COMPLETE!")
        print(f"Database optimized and {updated_count:,} coins enriched!")
        print(f"TrenchCoat Pro database enhanced with fresh market data!")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nEnrichment interrupted by user")
        enricher.print_enrichment_summary()
        return 1
        
    except Exception as e:
        print(f"\nEnrichment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        await enricher.shutdown()

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))