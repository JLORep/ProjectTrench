#!/usr/bin/env python3
"""
TrenchCoat Pro - Coin Image Enrichment Script
Bulk enrichment of coin database with beautiful logos and images
"""
import asyncio
import sqlite3
import os
from typing import List, Dict, Any
from datetime import datetime
from coin_image_system import coin_image_system, enrich_coins_with_images
from unicode_handler import safe_print

class CoinImageEnrichment:
    """Bulk coin image enrichment for the database"""
    
    def __init__(self):
        self.db_path = "data/trench.db"
        self.batch_size = 50  # Process in batches to avoid rate limits
        
    def get_coins_from_database(self) -> List[Dict[str, Any]]:
        """Get all coins from the database"""
        try:
            if not os.path.exists(self.db_path):
                safe_print(f"❌ Database not found: {self.db_path}")
                return []
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ticker, ca, discovery_price, axiom_price, axiom_mc, 
                       axiom_volume, liquidity, peak_volume, smart_wallets, discovery_time
                FROM coins
                WHERE ticker IS NOT NULL AND ticker != ''
                ORDER BY smart_wallets DESC, liquidity DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to dict format
            coins = []
            for row in rows:
                coin = {
                    'ticker': row['ticker'],
                    'ca': row['ca'] if row['ca'] else '',
                    'contract_address': row['ca'] if row['ca'] else '',
                    'discovery_price': float(row['discovery_price']) if row['discovery_price'] else 0,
                    'axiom_price': float(row['axiom_price']) if row['axiom_price'] else 0,
                    'axiom_mc': float(row['axiom_mc']) if row['axiom_mc'] else 0,
                    'axiom_volume': float(row['axiom_volume']) if row['axiom_volume'] else 0,
                    'liquidity': float(row['liquidity']) if row['liquidity'] else 0,
                    'peak_volume': float(row['peak_volume']) if row['peak_volume'] else 0,
                    'smart_wallets': int(row['smart_wallets']) if row['smart_wallets'] else 0,
                    'discovery_time': row['discovery_time'] if row['discovery_time'] else ''
                }
                coins.append(coin)
            
            safe_print(f"📊 Loaded {len(coins)} coins from database")
            return coins
            
        except Exception as e:
            safe_print(f"❌ Error loading coins: {e}")
            return []
    
    async def enrich_batch(self, coins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich a batch of coins with images"""
        safe_print(f"🖼️ Enriching batch of {len(coins)} coins with images...")
        
        try:
            enriched_coins = await enrich_coins_with_images(coins)
            
            # Count successful image fetches
            with_images = sum(1 for coin in enriched_coins if coin.get('image_verified', False))
            fallbacks = len(enriched_coins) - with_images
            
            safe_print(f"✅ Batch complete: {with_images} real images, {fallbacks} fallbacks")
            return enriched_coins
            
        except Exception as e:
            safe_print(f"❌ Error enriching batch: {e}") 
            return coins
    
    async def enrich_all_coins(self) -> Dict[str, Any]:
        """Enrich all coins with images in batches"""
        safe_print("🚀 Starting comprehensive coin image enrichment...")
        start_time = datetime.now()
        
        # Load all coins
        all_coins = self.get_coins_from_database()
        
        if not all_coins:
            return {
                'success': False,
                'error': 'No coins found in database',
                'stats': {'total': 0, 'enriched': 0, 'with_images': 0}
            }
        
        # Process in batches
        enriched_coins = []
        total_with_images = 0
        total_fallbacks = 0
        
        safe_print(f"📈 Processing {len(all_coins)} coins in batches of {self.batch_size}")
        
        for i in range(0, len(all_coins), self.batch_size):
            batch = all_coins[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(all_coins) + self.batch_size - 1) // self.batch_size
            
            safe_print(f"🔄 Processing batch {batch_num}/{total_batches}...")
            
            # Enrich this batch
            enriched_batch = await self.enrich_batch(batch)
            enriched_coins.extend(enriched_batch)
            
            # Count results
            batch_with_images = sum(1 for coin in enriched_batch if coin.get('image_verified', False))
            batch_fallbacks = len(enriched_batch) - batch_with_images
            
            total_with_images += batch_with_images
            total_fallbacks += batch_fallbacks
            
            # Progress update
            progress = ((i + len(batch)) / len(all_coins)) * 100
            safe_print(f"📊 Progress: {progress:.1f}% - Total images: {total_with_images}, Fallbacks: {total_fallbacks}")
            
            # Rate limiting between batches
            if i + self.batch_size < len(all_coins):
                safe_print("⏳ Rate limiting... waiting 5 seconds")
                await asyncio.sleep(5)
        
        # Final statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        stats = {
            'total_coins': len(all_coins),
            'enriched_coins': len(enriched_coins),
            'with_real_images': total_with_images,
            'with_fallbacks': total_fallbacks,
            'success_rate': (total_with_images / len(all_coins) * 100) if all_coins else 0,
            'duration_seconds': duration,
            'coins_per_minute': (len(all_coins) / duration * 60) if duration > 0 else 0
        }
        
        safe_print("🎉 Image enrichment complete!")
        safe_print(f"📈 Statistics:")
        safe_print(f"   • Total coins: {stats['total_coins']:,}")
        safe_print(f"   • Real images: {stats['with_real_images']:,} ({stats['success_rate']:.1f}%)")
        safe_print(f"   • Fallbacks: {stats['with_fallbacks']:,}")
        safe_print(f"   • Duration: {stats['duration_seconds']:.1f}s")
        safe_print(f"   • Speed: {stats['coins_per_minute']:.1f} coins/minute")
        
        return {
            'success': True,
            'stats': stats,
            'enriched_coins': enriched_coins
        }
    
    def generate_enrichment_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed enrichment report"""
        if not results['success']:
            return f"❌ Enrichment failed: {results.get('error', 'Unknown error')}"
        
        stats = results['stats']
        
        report = f"""
🖼️ **TrenchCoat Pro - Coin Image Enrichment Report**

📊 **Summary Statistics:**
   • Total Coins Processed: {stats['total_coins']:,}
   • Successfully Enriched: {stats['enriched_coins']:,}
   • Real Images Found: {stats['with_real_images']:,}
   • Fallback Images: {stats['with_fallbacks']:,}
   • Success Rate: {stats['success_rate']:.1f}%

⏱️ **Performance:**
   • Total Duration: {stats['duration_seconds']:.1f} seconds
   • Processing Speed: {stats['coins_per_minute']:.1f} coins/minute

🎯 **Quality Metrics:**
   • Image Coverage: {(stats['with_real_images'] / stats['total_coins'] * 100):.1f}%
   • API Success Rate: {stats['success_rate']:.1f}%

✅ **Status:** Image enrichment pipeline is fully operational and integrated with dashboard
"""
        return report

async def main():
    """Main enrichment execution"""
    enricher = CoinImageEnrichment()
    
    safe_print("🖼️ TrenchCoat Pro - Coin Image Enrichment System")
    safe_print("=" * 60)
    
    try:
        # Run the enrichment
        results = await enricher.enrich_all_coins()
        
        # Generate and display report
        report = enricher.generate_enrichment_report(results)
        safe_print(report)
        
        return 0 if results['success'] else 1
        
    except KeyboardInterrupt:
        safe_print("\n🛑 Enrichment interrupted by user")
        return 1
    except Exception as e:
        safe_print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))