#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Mass Enrichment System - TrenchCoat Pro
Optimized for existing database schema
Enriches ALL 1,733+ coins efficiently
"""

import sqlite3
import asyncio
import aiohttp
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import random

class FinalMassEnrichment:
    """Final optimized mass enrichment system"""
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.session = None
        self.stats = {
            'total_coins': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'api_calls': 0,
            'data_points_added': 0,
            'start_time': None,
            'errors': []
        }
        
        print("FINAL MASS ENRICHMENT SYSTEM")
        print("TrenchCoat Pro Database Enhancement")
        print("=" * 60)
    
    async def initialize(self):
        """Initialize the system"""
        print("Initializing mass enrichment system...")
        
        # Optimized session for mass processing
        timeout = aiohttp.ClientTimeout(total=15)
        connector = aiohttp.TCPConnector(limit=20, limit_per_host=10)
        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        
        self.stats['start_time'] = time.time()
        
        # Get total coins
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM coins WHERE ca IS NOT NULL AND LENGTH(ca) > 20")
        self.stats['total_coins'] = cursor.fetchone()[0]
        conn.close()
        
        print(f"System ready!")
        print(f"Total coins to process: {self.stats['total_coins']:,}")
        print(f"Expected duration: {self.stats['total_coins'] * 2.0 / 60:.1f} minutes")
        print(f"Processing speed: ~30 coins/minute with API limits")
    
    async def shutdown(self):
        """Shutdown system"""
        if self.session:
            await self.session.close()
    
    async def enrich_coin(self, ca: str, ticker: str = None) -> Dict[str, Any]:
        """Enrich single coin with DexScreener"""
        result = {
            'ca': ca,
            'ticker': ticker,
            'success': False,
            'data': {},
            'error': None
        }
        
        if not ca or len(ca) < 20:
            result['error'] = 'Invalid CA'
            return result
        
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
            
            async with self.session.get(url) as response:
                self.stats['api_calls'] += 1
                
                if response.status == 200:
                    data = await response.json()
                    
                    if 'pairs' in data and data['pairs']:
                        pair = data['pairs'][0]
                        extracted = {}
                        
                        # Price
                        if 'priceUsd' in pair and pair['priceUsd']:
                            try:
                                extracted['current_price_usd'] = float(pair['priceUsd'])
                            except:
                                pass
                        
                        # Volume
                        if 'volume' in pair and 'h24' in pair['volume']:
                            try:
                                extracted['current_volume_24h'] = float(pair['volume']['h24'])
                            except:
                                pass
                        
                        # Market Cap
                        if 'marketCap' in pair and pair['marketCap']:
                            try:
                                extracted['market_cap_usd'] = float(pair['marketCap'])
                            except:
                                pass
                        
                        # Price Change
                        if 'priceChange' in pair and 'h24' in pair['priceChange']:
                            try:
                                extracted['price_change_24h'] = float(pair['priceChange']['h24'])
                            except:
                                pass
                        
                        # FDV
                        if 'fdv' in pair and pair['fdv']:
                            try:
                                extracted['fdv_usd'] = float(pair['fdv'])
                            except:
                                pass
                        
                        # Update ticker
                        if not result['ticker']:
                            base_token = pair.get('baseToken', {})
                            if 'symbol' in base_token:
                                result['ticker'] = base_token['symbol']
                        
                        if extracted:
                            result['data'] = extracted
                            result['success'] = True
                            self.stats['data_points_added'] += len(extracted)
                        
                elif response.status == 429:
                    result['error'] = 'Rate limited'
                    await asyncio.sleep(3)  # Backoff on rate limit
                else:
                    result['error'] = f'HTTP {response.status}'
                    
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def ensure_columns_exist(self):
        """Ensure all needed columns exist in database"""
        print("Checking database schema...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Columns we need
            required_columns = [
                "current_price_usd REAL",
                "current_volume_24h REAL", 
                "market_cap_usd REAL",
                "price_change_24h REAL",
                "fdv_usd REAL",
                "enrichment_timestamp TEXT",
                "last_enrichment_success INTEGER DEFAULT 0",
                "data_quality_score REAL DEFAULT 0.0"
            ]
            
            for column_def in required_columns:
                column_name = column_def.split()[0]
                try:
                    cursor.execute(f"ALTER TABLE coins ADD COLUMN {column_def}")
                    print(f"  Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"  Column issue {column_name}: {e}")
            
            conn.commit()
            conn.close()
            print("Database schema ready!")
            return True
            
        except Exception as e:
            print(f"Schema check failed: {e}")
            return False
    
    def update_database(self, results: List[Dict[str, Any]]) -> int:
        """Update database with results"""
        if not results:
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updated = 0
            
            for result in results:
                ca = result['ca']
                
                if result['success'] and result['data']:
                    # Build update for successful enrichment
                    fields = []
                    values = []
                    
                    # Add data fields
                    for field, value in result['data'].items():
                        if value is not None:
                            fields.append(f"{field} = ?")
                            values.append(value)
                    
                    # Add metadata
                    fields.extend([
                        "enrichment_timestamp = ?",
                        "last_enrichment_success = ?",
                        "data_quality_score = ?",
                        "last_api_update = ?"
                    ])
                    
                    values.extend([
                        datetime.now().isoformat(),
                        1,
                        min(1.0, len(result['data']) * 0.2),
                        datetime.now().isoformat()
                    ])
                    
                    # Update ticker if we got one
                    if result['ticker']:
                        fields.append("ticker = ?")
                        values.append(result['ticker'])
                    
                    values.append(ca)
                    
                    if fields:
                        query = f"UPDATE coins SET {', '.join(fields)} WHERE ca = ?"
                        cursor.execute(query, values)
                        
                        if cursor.rowcount > 0:
                            updated += 1
                
                else:
                    # Mark failed attempt
                    cursor.execute("""
                        UPDATE coins 
                        SET last_enrichment_success = 0,
                            enrichment_timestamp = ?,
                            last_api_update = ?
                        WHERE ca = ?
                    """, [datetime.now().isoformat(), datetime.now().isoformat(), ca])
            
            conn.commit()
            conn.close()
            
            return updated
            
        except Exception as e:
            print(f"Database update error: {e}")
            return 0
    
    async def process_batch(self, coins: List[Tuple[str, str]], batch_size: int = 10) -> List[Dict[str, Any]]:
        """Process a batch of coins"""
        results = []
        
        # Process in small sub-batches for rate limiting
        for i in range(0, len(coins), batch_size):
            sub_batch = coins[i:i + batch_size]
            
            # Create tasks
            tasks = []
            for ca, ticker in sub_batch:
                # Stagger requests slightly
                if tasks:
                    await asyncio.sleep(0.1)
                task = asyncio.create_task(self.enrich_coin(ca, ticker))
                tasks.append(task)
            
            # Wait for completion
            sub_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for j, result in enumerate(sub_results):
                if isinstance(result, Exception):
                    error_result = {
                        'ca': sub_batch[j][0],
                        'ticker': sub_batch[j][1],
                        'success': False,
                        'error': str(result),
                        'data': {}
                    }
                    results.append(error_result)
                    self.stats['failed'] += 1
                else:
                    results.append(result)
                    if result['success']:
                        self.stats['successful'] += 1
                    else:
                        self.stats['failed'] += 1
                        if result['error']:
                            self.stats['errors'].append(result['error'])
                
                self.stats['processed'] += 1
            
            # Rate limiting between sub-batches
            if i + batch_size < len(coins):
                await asyncio.sleep(1.5)  # Conservative rate limiting
        
        return results
    
    def print_progress(self, batch_num: int, total_batches: int, updated: int):
        """Print progress update"""
        elapsed = time.time() - self.stats['start_time']
        progress = (self.stats['processed'] / self.stats['total_coins']) * 100
        
        if self.stats['processed'] > 0:
            rate = self.stats['processed'] / elapsed
            remaining = self.stats['total_coins'] - self.stats['processed']
            eta_minutes = (remaining / rate) / 60 if rate > 0 else 0
            success_rate = (self.stats['successful'] / self.stats['processed']) * 100
        else:
            rate = 0
            eta_minutes = 0
            success_rate = 0
        
        print(f"\nBATCH {batch_num}/{total_batches} COMPLETE")
        print(f"Progress: {progress:.1f}% ({self.stats['processed']:,}/{self.stats['total_coins']:,})")
        print(f"Successful: {self.stats['successful']:,} ({success_rate:.1f}%)")
        print(f"Database updated: {updated} coins")
        print(f"Rate: {rate:.1f} coins/sec")
        print(f"Elapsed: {elapsed/60:.1f} min, ETA: {eta_minutes:.1f} min")
    
    def print_final_summary(self):
        """Print final enrichment summary"""
        duration = time.time() - self.stats['start_time']
        
        print("\n" + "=" * 60)
        print("MASS ENRICHMENT COMPLETE!")
        print("=" * 60)
        
        print(f"Total Duration: {duration/60:.1f} minutes")
        print(f"Coins Processed: {self.stats['processed']:,}")
        print(f"Successful: {self.stats['successful']:,}")
        print(f"Failed: {self.stats['failed']:,}")
        print(f"Success Rate: {(self.stats['successful']/max(self.stats['processed'],1)*100):.1f}%")
        print(f"API Calls: {self.stats['api_calls']:,}")
        print(f"Data Points Added: {self.stats['data_points_added']:,}")
        print(f"Average Speed: {self.stats['processed']/duration:.1f} coins/second")
        
        # Database statistics
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM coins WHERE current_price_usd IS NOT NULL")
            enriched = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM coins")
            total = cursor.fetchone()[0]
            
            print(f"\nDATABASE STATUS:")
            print(f"Enriched Coins: {enriched:,} / {total:,} ({enriched/total*100:.1f}%)")
            
            # Top coins by market cap
            cursor.execute("""
                SELECT ticker, current_price_usd, market_cap_usd
                FROM coins 
                WHERE current_price_usd IS NOT NULL 
                AND market_cap_usd IS NOT NULL
                ORDER BY market_cap_usd DESC 
                LIMIT 3
            """)
            
            top_coins = cursor.fetchall()
            if top_coins:
                print(f"\nTOP COINS BY MARKET CAP:")
                for i, (ticker, price, mcap) in enumerate(top_coins, 1):
                    print(f"  {i}. {ticker}: ${float(price):.8f} (${float(mcap):,.0f})")
            
            conn.close()
            
        except Exception as e:
            print(f"Database stats error: {e}")
        
        print(f"\nTrenchCoat Pro database SUPERCHARGED!")
        print(f"Ready for professional trading intelligence!")
    
    async def run_mass_enrichment(self, batch_size: int = 25):
        """Run the complete mass enrichment"""
        print(f"Starting mass enrichment...")
        print(f"Processing {self.stats['total_coins']:,} coins in batches of {batch_size}")
        
        # Ensure database schema is ready
        if not self.ensure_columns_exist():
            print("Failed to prepare database schema")
            return False
        
        # Get all coins
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ca, ticker 
            FROM coins 
            WHERE ca IS NOT NULL 
            AND LENGTH(ca) > 20
            ORDER BY 
                CASE WHEN current_price_usd IS NULL THEN 0 ELSE 1 END,
                CASE WHEN enrichment_timestamp IS NULL THEN 0 ELSE 1 END,
                RANDOM()
        """)
        
        all_coins = cursor.fetchall()
        conn.close()
        
        total_batches = (len(all_coins) + batch_size - 1) // batch_size
        
        print(f"Processing {len(all_coins)} coins in {total_batches} batches")
        
        try:
            for batch_num in range(1, total_batches + 1):
                start_idx = (batch_num - 1) * batch_size
                end_idx = min(start_idx + batch_size, len(all_coins))
                batch_coins = all_coins[start_idx:end_idx]
                
                # Process batch
                results = await self.process_batch(batch_coins, batch_size=5)
                
                # Update database
                updated = self.update_database(results)
                
                # Progress update
                self.print_progress(batch_num, total_batches, updated)
                
                # Rest between batches
                if batch_num < total_batches:
                    await asyncio.sleep(3)  # 3 second rest
                    
        except KeyboardInterrupt:
            print(f"\nEnrichment interrupted at batch {batch_num}")
        
        # Final summary
        self.print_final_summary()
        return True

async def main():
    """Main execution"""
    enricher = FinalMassEnrichment()
    
    try:
        await enricher.initialize()
        
        print(f"\nREADY TO ENRICH {enricher.stats['total_coins']:,} COINS!")
        print(f"This will take approximately {enricher.stats['total_coins'] * 2.0 / 60:.1f} minutes")
        print(f"Processing with conservative rate limiting for reliability")
        print(f"Press Ctrl+C to stop at any time\n")
        
        success = await enricher.run_mass_enrichment(batch_size=25)
        
        if success:
            print("\n*** MASS ENRICHMENT SUCCESSFUL! ***")
            print("TrenchCoat Pro database enhanced with live market data!")
            return 0
        else:
            print("\n*** MASS ENRICHMENT FAILED ***")
            return 1
        
    except Exception as e:
        print(f"Mass enrichment error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        await enricher.shutdown()

if __name__ == "__main__":
    import sys
    print("FINAL MASS ENRICHMENT SYSTEM")
    print("Preparing to enrich ALL 1,733+ coins!")
    print("This is the BIG ONE - let's make it happen!")
    
    sys.exit(asyncio.run(main()))