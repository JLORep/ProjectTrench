#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Database Enricher - Fast version for testing
Enriches a small batch quickly to demonstrate the system
Created: 2025-08-02
"""

import sqlite3
import asyncio
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

class QuickEnricher:
    """Quick enrichment for demonstration"""
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.session = None
        self.stats = {'processed': 0, 'successful': 0, 'failed': 0}
    
    async def initialize(self):
        """Initialize session"""
        print("Quick Enricher - Initializing...")
        timeout = aiohttp.ClientTimeout(total=15)
        self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def shutdown(self):
        """Shutdown session"""
        if self.session:
            await self.session.close()
    
    async def enrich_coin(self, ca: str, ticker: str = None) -> Dict[str, Any]:
        """Enrich single coin quickly"""
        result = {'ca': ca, 'ticker': ticker, 'success': False, 'data': {}}
        
        if not ca or len(ca) < 20:
            return result
        
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'pairs' in data and data['pairs']:
                        pair = data['pairs'][0]
                        
                        # Extract essential data only
                        if 'priceUsd' in pair and pair['priceUsd']:
                            try:
                                result['data']['current_price_usd'] = float(pair['priceUsd'])
                            except:
                                pass
                        
                        if 'volume' in pair and 'h24' in pair['volume']:
                            try:
                                result['data']['current_volume_24h'] = float(pair['volume']['h24'])
                            except:
                                pass
                        
                        if 'marketCap' in pair and pair['marketCap']:
                            try:
                                result['data']['market_cap_usd'] = float(pair['marketCap'])
                            except:
                                pass
                        
                        if result['data']:
                            result['success'] = True
                            
        except Exception as e:
            pass  # Silent fail for speed
        
        return result
    
    async def enrich_batch_quick(self, coins: List[Tuple[str, str]], max_coins: int = 10):
        """Quick batch enrichment"""
        print(f"Quick enriching {min(len(coins), max_coins)} coins...")
        
        # Limit to first N coins for speed
        coins = coins[:max_coins]
        results = []
        
        for i, (ca, ticker) in enumerate(coins):
            result = await self.enrich_coin(ca, ticker)
            results.append(result)
            
            self.stats['processed'] += 1
            if result['success']:
                self.stats['successful'] += 1
                print(f"   {i+1}. {result['ticker'] or 'Unknown'}: ${result['data'].get('current_price_usd', 'N/A')}")
            else:
                self.stats['failed'] += 1
                print(f"   {i+1}. {result['ticker'] or 'Unknown'}: No data")
            
            # Minimal rate limiting
            if i < len(coins) - 1:
                await asyncio.sleep(0.5)  # Very short delay
        
        return results
    
    def update_database_quick(self, results: List[Dict[str, Any]]) -> int:
        """Quick database update"""
        print("Updating database...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updated = 0
            
            for result in results:
                if result['success'] and result['data']:
                    ca = result['ca']
                    data = result['data']
                    
                    # Simple update query
                    fields = []
                    values = []
                    
                    for field, value in data.items():
                        fields.append(f"{field} = ?")
                        values.append(value)
                    
                    # Add timestamp
                    fields.append("enrichment_timestamp = ?")
                    fields.append("last_enrichment_success = ?")
                    values.extend([datetime.now().isoformat(), 1])
                    
                    values.append(ca)  # WHERE clause
                    
                    query = f"UPDATE coins SET {', '.join(fields)} WHERE ca = ?"
                    cursor.execute(query, values)
                    
                    if cursor.rowcount > 0:
                        updated += 1
            
            conn.commit()
            conn.close()
            
            print(f"Updated {updated} coins in database")
            return updated
            
        except Exception as e:
            print(f"Database update error: {e}")
            return 0

async def main():
    """Quick enrichment demo"""
    print("TrenchCoat Pro - Quick Enrichment Demo")
    print("=" * 50)
    
    enricher = QuickEnricher()
    await enricher.initialize()
    
    try:
        # Get some coins to enrich
        conn = sqlite3.connect("data/trench.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ca, ticker 
            FROM coins 
            WHERE ca IS NOT NULL 
            AND LENGTH(ca) > 20
            LIMIT 10
        """)
        
        coins = cursor.fetchall()
        conn.close()
        
        if not coins:
            print("No coins found to enrich")
            return 1
        
        print(f"Found {len(coins)} coins to enrich")
        
        # Quick enrichment
        start_time = time.time()
        results = await enricher.enrich_batch_quick(coins, max_coins=10)
        duration = time.time() - start_time
        
        # Update database
        updated = enricher.update_database_quick(results)
        
        # Summary
        print("\n" + "=" * 50)
        print("QUICK ENRICHMENT SUMMARY")
        print("=" * 50)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Processed: {enricher.stats['processed']}")
        print(f"Successful: {enricher.stats['successful']}")
        print(f"Failed: {enricher.stats['failed']}")
        print(f"Database Updated: {updated}")
        print(f"Success Rate: {enricher.stats['successful']/enricher.stats['processed']*100:.1f}%")
        
        print("\nQUICK DEMO COMPLETE!")
        print("Database has been enhanced with fresh market data!")
        
        return 0
        
    except Exception as e:
        print(f"Quick enrichment failed: {e}")
        return 1
        
    finally:
        await enricher.shutdown()

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))