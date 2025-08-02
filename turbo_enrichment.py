#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turbo Enrichment - Fast processing for demonstration
Enriches coins at maximum safe speed
"""

import sqlite3
import asyncio
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

class TurboEnrichment:
    """High-speed enrichment for demonstration"""
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.session = None
        self.stats = {'processed': 0, 'successful': 0, 'failed': 0, 'api_calls': 0, 'start_time': None}
    
    async def initialize(self):
        """Initialize turbo system"""
        print("TURBO ENRICHMENT SYSTEM - MAXIMUM SPEED")
        print("=" * 50)
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        self.stats['start_time'] = time.time()
    
    async def shutdown(self):
        if self.session:
            await self.session.close()
    
    async def enrich_coin_turbo(self, ca: str, ticker: str = None) -> Dict[str, Any]:
        """Turbo-speed coin enrichment"""
        result = {'ca': ca, 'ticker': ticker, 'success': False, 'data': {}}
        
        if not ca or len(ca) < 20:
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
                        
                        # Extract key data points
                        if 'priceUsd' in pair and pair['priceUsd']:
                            try:
                                extracted['current_price_usd'] = float(pair['priceUsd'])
                            except:
                                pass
                        
                        if 'volume' in pair and 'h24' in pair['volume']:
                            try:
                                extracted['current_volume_24h'] = float(pair['volume']['h24'])
                            except:
                                pass
                        
                        if 'marketCap' in pair and pair['marketCap']:
                            try:
                                extracted['market_cap_usd'] = float(pair['marketCap'])
                            except:
                                pass
                        
                        if 'liquidity' in pair and 'usd' in pair['liquidity']:
                            try:
                                extracted['liquidity_usd'] = float(pair['liquidity']['usd'])
                            except:
                                pass
                        
                        if 'priceChange' in pair and 'h24' in pair['priceChange']:
                            try:
                                extracted['price_change_24h'] = float(pair['priceChange']['h24'])
                            except:
                                pass
                        
                        if extracted:
                            result['data'] = extracted
                            result['success'] = True
                            
        except Exception as e:
            pass  # Silent fail for speed
        
        return result
    
    async def process_turbo_batch(self, coins: List[Tuple[str, str]], batch_size: int = 100):
        """Process coins at turbo speed"""
        print(f"TURBO PROCESSING: {len(coins)} coins at maximum speed!")
        
        results = []
        
        # Process in aggressive batches for speed
        for i in range(0, len(coins), batch_size):
            batch = coins[i:i + batch_size]
            batch_start = time.time()
            
            # Create all tasks at once for maximum concurrency
            tasks = [self.enrich_coin_turbo(ca, ticker) for ca, ticker in batch]
            
            # Execute all simultaneously
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_in_batch = 0
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    self.stats['failed'] += 1
                else:
                    results.append(result)
                    if result['success']:
                        self.stats['successful'] += 1
                        successful_in_batch += 1
                    else:
                        self.stats['failed'] += 1
                
                self.stats['processed'] += 1
            
            batch_time = time.time() - batch_start
            batch_rate = len(batch) / batch_time
            
            print(f"  Batch {i//batch_size + 1}: {successful_in_batch}/{len(batch)} successful")
            print(f"  Speed: {batch_rate:.1f} coins/sec, Time: {batch_time:.1f}s")
            
            # Minimal delay for API respect
            await asyncio.sleep(0.3)
        
        return results
    
    def update_database_turbo(self, results: List[Dict[str, Any]]) -> int:
        """Turbo database update"""
        if not results:
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updated = 0
            
            for result in results:
                if result['success'] and result['data']:
                    ca = result['ca']
                    data = result['data']
                    
                    # Build update query
                    fields = []
                    values = []
                    
                    for field, value in data.items():
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
                        min(1.0, len(data) * 0.2),
                        datetime.now().isoformat()
                    ])
                    
                    values.append(ca)
                    
                    query = f"UPDATE coins SET {', '.join(fields)} WHERE ca = ?"
                    cursor.execute(query, values)
                    
                    if cursor.rowcount > 0:
                        updated += 1
            
            conn.commit()
            conn.close()
            
            return updated
            
        except Exception as e:
            print(f"Database update error: {e}")
            return 0
    
    def print_turbo_summary(self):
        """Print turbo results"""
        duration = time.time() - self.stats['start_time']
        
        print("\n" + "=" * 50)
        print("TURBO ENRICHMENT COMPLETE!")
        print("=" * 50)
        
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"Processed: {self.stats['processed']:,} coins")
        print(f"Successful: {self.stats['successful']:,}")
        print(f"Failed: {self.stats['failed']:,}")
        print(f"Success Rate: {(self.stats['successful']/self.stats['processed']*100):.1f}%")
        print(f"Speed: {self.stats['processed']/duration:.1f} coins/second")
        print(f"API Calls: {self.stats['api_calls']:,}")
        
        # Show database totals
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM coins WHERE current_price_usd IS NOT NULL")
            total_enriched = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM coins")
            total_coins = cursor.fetchone()[0]
            
            print(f"\nDATABASE STATUS:")
            print(f"Total enriched coins: {total_enriched:,} / {total_coins:,}")
            print(f"Coverage: {(total_enriched/total_coins)*100:.1f}%")
            
            conn.close()
            
        except Exception as e:
            print(f"Database status error: {e}")

async def main():
    """Turbo enrichment main"""
    turbo = TurboEnrichment()
    
    try:
        await turbo.initialize()
        
        # Get coins that need enrichment
        conn = sqlite3.connect(turbo.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ca, ticker 
            FROM coins 
            WHERE ca IS NOT NULL 
            AND LENGTH(ca) > 20
            AND (current_price_usd IS NULL OR enrichment_timestamp IS NULL
                 OR enrichment_timestamp < datetime('now', '-1 day'))
            ORDER BY 
                CASE WHEN current_price_usd IS NULL THEN 0 ELSE 1 END,
                RANDOM()
            LIMIT 200
        """)
        
        coins_to_process = cursor.fetchall()
        conn.close()
        
        if not coins_to_process:
            print("No coins need enrichment!")
            return 0
        
        print(f"Found {len(coins_to_process)} coins to enrich")
        
        # TURBO PROCESSING
        results = await turbo.process_turbo_batch(coins_to_process, batch_size=20)
        
        # Update database
        updated = turbo.update_database_turbo(results)
        print(f"\nDatabase updated: {updated} coins")
        
        # Summary
        turbo.print_turbo_summary()
        
        print("\nTURBO ENRICHMENT SUCCESS!")
        print("Database supercharged with fresh market data!")
        
        return 0
        
    except Exception as e:
        print(f"Turbo enrichment failed: {e}")
        return 1
        
    finally:
        await turbo.shutdown()

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))