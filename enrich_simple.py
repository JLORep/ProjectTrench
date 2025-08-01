#!/usr/bin/env python3
"""
Simple TrenchCoat Coin Enrichment Script (Windows compatible)
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data.master_enricher import MasterEnricher

async def main():
    """Simple enrichment without fancy formatting"""
    print("TrenchCoat Coin Enrichment Engine")
    print("=" * 40)
    
    # Test with USDC address
    usdc_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    enricher = MasterEnricher()
    
    print(f"\nEnriching USDC token: {usdc_address[:20]}...")
    
    def progress_callback(stats):
        print(f"Progress: {stats.processed}/{stats.total_coins} "
              f"({stats.success_rate:.1%} success rate)")
    
    try:
        stats = await enricher.enrich_specific_coins([usdc_address])
        
        print("\n" + "=" * 40)
        print("ENRICHMENT COMPLETE!")
        print("=" * 40)
        print(f"Total coins: {stats.total_coins}")
        print(f"Processed: {stats.processed}")
        print(f"Successful: {stats.successful}")
        print(f"Failed: {stats.failed}")
        print(f"Success rate: {stats.success_rate:.1%}")
        print(f"Duration: {stats.elapsed_time}")
        
        if stats.successful > 0:
            print("\nSUCCESS! Your coins.db has been enriched with real crypto data!")
            print("Next steps:")
            print("1. Run: python -c \"from src.data.database import CoinDatabase; db=CoinDatabase(); print('Database has', len(db.get_price_data('USDC', '1h')), 'USDC records')\"")
            print("2. Check data/coins.db with SQLite browser")
            print("3. Run more enrichments with different tokens")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())