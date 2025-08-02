#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launch Mass Enrichment - Unicode Safe Version
Enriches ALL 1,733+ coins in database
"""

import sqlite3
import asyncio
import aiohttp
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import random

class MassEnrichmentSystem:
    """Mass enrichment of all coins in TrenchCoat Pro database"""
    
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
            'current_batch': 0,
            'estimated_completion': None,
            'errors': []
        }
        
        print("MASS ENRICHMENT SYSTEM - TrenchCoat Pro")
        print("=" * 70)
    
    async def initialize(self):
        """Initialize the mass enrichment system"""
        print("Initializing mass enrichment system...")
        
        # Create session with longer timeout for mass processing
        timeout = aiohttp.ClientTimeout(total=20)
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        
        self.stats['start_time'] = time.time()
        
        # Get total coin count
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM coins WHERE ca IS NOT NULL AND LENGTH(ca) > 20")
        self.stats['total_coins'] = cursor.fetchone()[0]
        conn.close()
        
        print(f"System initialized")
        print(f"Total coins to enrich: {self.stats['total_coins']:,}")
        print(f"Estimated time: {self.stats['total_coins'] * 1.5 / 60:.1f} minutes")
        
    async def shutdown(self):
        """Gracefully shutdown the system"""
        if self.session:
            await self.session.close()
    
    async def enrich_coin_with_dexscreener(self, ca: str, ticker: str = None) -> Dict[str, Any]:
        """Enrich single coin with DexScreener API"""
        result = {
            'ca': ca,
            'ticker': ticker,
            'success': False,
            'api_used': 'dexscreener',
            'data': {},
            'response_time': 0,
            'error': None
        }
        
        if not ca or len(ca) < 20:
            result['error'] = 'Invalid contract address'
            return result
        
        start_time = time.time()
        
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
            
            async with self.session.get(url) as response:
                result['response_time'] = (time.time() - start_time) * 1000  # ms
                self.stats['api_calls'] += 1
                
                if response.status == 200:
                    data = await response.json()
                    
                    if 'pairs' in data and data['pairs']:
                        pair = data['pairs'][0]  # Best liquidity pair
                        
                        # Extract comprehensive data
                        extracted_data = {}
                        
                        # Price data
                        if 'priceUsd' in pair and pair['priceUsd']:
                            try:
                                extracted_data['current_price_usd'] = float(pair['priceUsd'])
                            except (ValueError, TypeError):
                                pass
                        
                        # Volume data
                        if 'volume' in pair and pair['volume']:
                            if 'h24' in pair['volume']:
                                try:
                                    extracted_data['current_volume_24h'] = float(pair['volume']['h24'])
                                except (ValueError, TypeError):
                                    pass
                        
                        # Price change
                        if 'priceChange' in pair and pair['priceChange']:
                            if 'h24' in pair['priceChange']:
                                try:
                                    extracted_data['price_change_24h'] = float(pair['priceChange']['h24'])
                                except (ValueError, TypeError):
                                    pass
                        
                        # Market cap
                        if 'marketCap' in pair and pair['marketCap']:
                            try:
                                extracted_data['market_cap_usd'] = float(pair['marketCap'])
                            except (ValueError, TypeError):
                                pass
                        
                        # FDV (Fully Diluted Valuation)
                        if 'fdv' in pair and pair['fdv']:
                            try:
                                extracted_data['fdv_usd'] = float(pair['fdv'])
                            except (ValueError, TypeError):
                                pass
                        
                        # Liquidity
                        if 'liquidity' in pair and pair['liquidity']:
                            if 'usd' in pair['liquidity']:
                                try:
                                    extracted_data['liquidity_usd'] = float(pair['liquidity']['usd'])
                                except (ValueError, TypeError):
                                    pass
                        
                        # Update ticker if available
                        if not result['ticker']:
                            base_token = pair.get('baseToken', {})
                            if 'symbol' in base_token:
                                result['ticker'] = base_token['symbol']
                        
                        if extracted_data:
                            result['data'] = extracted_data
                            result['success'] = True
                            self.stats['data_points_added'] += len(extracted_data)
                        
                elif response.status == 429:
                    result['error'] = 'Rate limited'
                    # Exponential backoff for rate limits
                    await asyncio.sleep(min(5 + random.uniform(0, 3), 10))
                else:
                    result['error'] = f'HTTP {response.status}'
                    
        except asyncio.TimeoutError:
            result['error'] = 'Timeout'
        except Exception as e:
            result['error'] = f'Exception: {str(e)}'
        
        return result
    
    async def enrich_batch(self, coins: List[Tuple[str, str]], batch_size: int = 8) -> List[Dict[str, Any]]:
        """Enrich a batch of coins with intelligent rate limiting"""
        results = []
        
        # Process coins in smaller sub-batches for better rate limiting
        for i in range(0, len(coins), batch_size):
            sub_batch = coins[i:i + batch_size]
            
            # Create tasks for concurrent processing
            tasks = []
            for ca, ticker in sub_batch:
                # Add jitter to prevent thundering herd
                jitter = random.uniform(0, 0.2)
                await asyncio.sleep(jitter)
                
                task = asyncio.create_task(self.enrich_coin_with_dexscreener(ca, ticker))
                tasks.append(task)
            
            # Wait for sub-batch completion
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
                    self.stats['errors'].append(str(result))
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
                # Adaptive delay based on API response times
                avg_response_time = sum(r.get('response_time', 0) for r in sub_results if not isinstance(r, Exception)) / len(sub_results)
                delay = max(0.8, min(2.0, avg_response_time / 200))  # 0.8-2.0 seconds based on response time
                await asyncio.sleep(delay)
        
        return results
    
    def update_database_batch(self, results: List[Dict[str, Any]]) -> int:
        """Update database with batch results"""
        if not results:
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updated_count = 0
            
            for result in results:
                if result['success'] and result['data']:
                    ca = result['ca']
                    data = result['data']
                    
                    # Build dynamic update query
                    update_fields = []
                    update_values = []
                    
                    # Add all data fields
                    for field, value in data.items():
                        if value is not None:
                            update_fields.append(f"{field} = ?")
                            update_values.append(value)
                    
                    # Add metadata
                    metadata_fields = [
                        ("enrichment_timestamp", datetime.now().isoformat()),
                        ("last_enrichment_success", 1),
                        ("data_quality_score", min(1.0, len(data) * 0.15)),
                        ("last_api_update", datetime.now().isoformat()),
                        ("api_response_time_ms", int(result.get('response_time', 0)))
                    ]
                    
                    for field, value in metadata_fields:
                        update_fields.append(f"{field} = ?")
                        update_values.append(value)
                    
                    # Update ticker if we have a better one
                    if result['ticker'] and result['ticker'] != result.get('ticker'):
                        update_fields.append("ticker = ?")
                        update_values.append(result['ticker'])
                    
                    update_values.append(ca)  # WHERE clause
                    
                    if update_fields:
                        query = f"UPDATE coins SET {', '.join(update_fields)} WHERE ca = ?"
                        cursor.execute(query, update_values)
                        
                        if cursor.rowcount > 0:
                            updated_count += 1
                
                # Track failed attempts too
                elif not result['success']:
                    cursor.execute("""
                        UPDATE coins 
                        SET last_enrichment_success = 0,
                            enrichment_timestamp = ?,
                            last_api_update = ?
                        WHERE ca = ?
                    """, [datetime.now().isoformat(), datetime.now().isoformat(), result['ca']])
            
            conn.commit()
            conn.close()
            
            return updated_count
            
        except Exception as e:
            print(f"Database batch update error: {e}")
            return 0
    
    def print_progress_update(self, batch_num: int, total_batches: int):
        """Print detailed progress update"""
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            
            # Calculate rates and estimates
            if self.stats['processed'] > 0:
                rate = self.stats['processed'] / elapsed
                remaining = self.stats['total_coins'] - self.stats['processed']
                eta_seconds = remaining / rate if rate > 0 else 0
                eta_time = datetime.now() + timedelta(seconds=eta_seconds)
                
                success_rate = (self.stats['successful'] / self.stats['processed']) * 100
            else:
                rate = 0
                eta_time = None
                success_rate = 0
            
            # Progress bar
            progress = (self.stats['processed'] / self.stats['total_coins']) * 100
            bar_length = 40
            filled_length = int(bar_length * progress / 100)
            bar = '#' * filled_length + '-' * (bar_length - filled_length)
            
            print(f"\nMASS ENRICHMENT PROGRESS - Batch {batch_num}/{total_batches}")
            print(f"[{bar}] {progress:.1f}%")
            print(f"Processed: {self.stats['processed']:,}/{self.stats['total_coins']:,}")
            print(f"Successful: {self.stats['successful']:,} ({success_rate:.1f}%)")
            print(f"Failed: {self.stats['failed']:,}")
            print(f"API Calls: {self.stats['api_calls']:,}")
            print(f"Data Points: {self.stats['data_points_added']:,}")
            print(f"Rate: {rate:.1f} coins/sec")
            print(f"Elapsed: {elapsed/60:.1f} min")
            if eta_time:
                print(f"ETA: {eta_time.strftime('%H:%M:%S')} ({eta_seconds/60:.1f} min remaining)")
    
    def print_final_summary(self):
        """Print comprehensive final summary"""
        duration = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        
        print("\n" + "=" * 70)
        print("MASS ENRICHMENT COMPLETE!")
        print("=" * 70)
        
        print(f"Total Duration: {duration/60:.1f} minutes ({duration:.1f} seconds)")
        print(f"Total Processed: {self.stats['processed']:,} coins")
        print(f"Successful: {self.stats['successful']:,}")
        print(f"Failed: {self.stats['failed']:,}")
        print(f"Success Rate: {(self.stats['successful']/self.stats['processed']*100):.1f}%")
        print(f"API Calls Made: {self.stats['api_calls']:,}")
        print(f"Data Points Added: {self.stats['data_points_added']:,}")
        print(f"Average Rate: {self.stats['processed']/duration:.1f} coins/second")
        
        # Database stats
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM coins WHERE current_price_usd IS NOT NULL")
            enriched_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM coins")
            total_count = cursor.fetchone()[0]
            
            coverage = (enriched_count / total_count) * 100
            
            print(f"\nDATABASE STATISTICS:")
            print(f"Coins with Price Data: {enriched_count:,}/{total_count:,} ({coverage:.1f}%)")
            
            # Get top performing coins
            cursor.execute("""
                SELECT ticker, current_price_usd, market_cap_usd, current_volume_24h
                FROM coins 
                WHERE current_price_usd IS NOT NULL 
                ORDER BY market_cap_usd DESC NULLS LAST
                LIMIT 5
            """)
            top_coins = cursor.fetchall()
            
            if top_coins:
                print(f"\nTOP 5 COINS BY MARKET CAP:")
                for i, (ticker, price, mcap, volume) in enumerate(top_coins, 1):
                    mcap_str = f"${float(mcap):,.0f}" if mcap else "N/A"
                    price_str = f"${float(price):.8f}" if price else "N/A"
                    print(f"  {i}. {ticker}: {price_str} (MCap: {mcap_str})")
            
            conn.close()
            
        except Exception as e:
            print(f"Database stats error: {e}")
        
        print(f"\nTrenchCoat Pro database is now SUPERCHARGED with live market data!")
        print(f"Ready for advanced trading intelligence and analytics!")
    
    async def run_mass_enrichment(self, batch_size: int = 50, max_batches: Optional[int] = None):
        """Run the complete mass enrichment process"""
        print(f"Starting mass enrichment of {self.stats['total_coins']:,} coins...")
        print(f"Batch size: {batch_size} coins")
        print(f"Rate limiting: 0.8-2.0 seconds between requests")
        print(f"Estimated completion: {self.stats['total_coins'] * 1.5 / 60:.1f} minutes")
        
        # Get all coins that need enrichment
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Prioritize coins without data, then older data
        cursor.execute("""
            SELECT ca, ticker 
            FROM coins 
            WHERE ca IS NOT NULL 
            AND LENGTH(ca) > 20
            ORDER BY 
                CASE WHEN current_price_usd IS NULL THEN 0 ELSE 1 END,
                CASE WHEN enrichment_timestamp IS NULL THEN 0 ELSE 1 END,
                enrichment_timestamp ASC,
                RANDOM()
        """)
        
        all_coins = cursor.fetchall()
        conn.close()
        
        if max_batches:
            all_coins = all_coins[:max_batches * batch_size]
            print(f"LIMITED RUN: Processing {len(all_coins)} coins ({max_batches} batches)")
        
        # Process in batches
        total_batches = (len(all_coins) + batch_size - 1) // batch_size
        
        try:
            for batch_num in range(1, total_batches + 1):
                start_idx = (batch_num - 1) * batch_size
                end_idx = min(start_idx + batch_size, len(all_coins))
                batch_coins = all_coins[start_idx:end_idx]
                
                # Process batch
                results = await self.enrich_batch(batch_coins, batch_size=8)
                
                # Update database
                updated = self.update_database_batch(results)
                
                # Progress update
                self.print_progress_update(batch_num, total_batches)
                print(f"Database updated: {updated} coins")
                
                # Batch completion delay
                if batch_num < total_batches:
                    await asyncio.sleep(2)  # 2 second rest between batches
                    
        except KeyboardInterrupt:
            print(f"\nMass enrichment interrupted by user at batch {batch_num}")
        
        # Final summary
        self.print_final_summary()

async def main():
    """Main execution function"""
    system = MassEnrichmentSystem()
    
    try:
        await system.initialize()
        
        print(f"\nReady to enrich {system.stats['total_coins']:,} coins!")
        print(f"This will take approximately {system.stats['total_coins'] * 1.5 / 60:.1f} minutes")
        print(f"You can interrupt anytime with Ctrl+C")
        
        # Run mass enrichment - remove max_batches to process ALL coins
        await system.run_mass_enrichment(batch_size=50)  # Remove max_batches parameter for full run
        
        return 0
        
    except Exception as e:
        print(f"Mass enrichment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        await system.shutdown()

if __name__ == "__main__":
    import sys
    print("MASS ENRICHMENT SYSTEM STARTING...")
    print("Preparing to enrich ALL coins in TrenchCoat Pro database!")
    print("Hold on... this is going to be EPIC!")
    
    sys.exit(asyncio.run(main()))