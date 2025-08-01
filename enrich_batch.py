#!/usr/bin/env python3
"""
Batch enrich popular Solana tokens
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data.master_enricher import MasterEnricher

async def main():
    """Enrich multiple popular tokens"""
    print("TrenchCoat Batch Enrichment")
    print("=" * 40)
    
    # Popular Solana tokens
    tokens = [
        ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "USDC"),  # USDC
        ("So11111111111111111111111111111111111111112", "SOL"),    # Wrapped SOL  
        ("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "USDT"),   # USDT
        ("4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", "RAY"),    # Raydium
        ("SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt", "SRM"),    # Serum
    ]
    
    enricher = MasterEnricher()
    
    print(f"\nEnriching {len(tokens)} popular Solana tokens...")
    print("This will demonstrate the power of our multi-API system!\n")
    
    addresses = [token[0] for token in tokens]
    
    def progress_callback(stats):
        if stats.processed > 0:
            print(f"Progress: {stats.processed}/{stats.total_coins} "
                  f"({stats.success_rate:.1%} success, "
                  f"{stats.coins_per_minute:.1f}/min)")
    
    try:
        stats = await enricher.enrich_specific_coins(addresses)
        
        print("\n" + "=" * 50)
        print("BATCH ENRICHMENT COMPLETE!")
        print("=" * 50)
        print(f"Total tokens: {stats.total_coins}")
        print(f"Successfully enriched: {stats.successful}")
        print(f"Failed: {stats.failed}")
        print(f"Success rate: {stats.success_rate:.1%}")
        print(f"Processing rate: {stats.coins_per_minute:.1f} tokens/minute")
        print(f"Total duration: {stats.elapsed_time}")
        
        if stats.successful > 0:
            print(f"\n🎉 SUCCESS! Enriched {stats.successful} tokens with real market data!")
            print("\nWhat you now have in your database:")
            print("✅ Real-time prices from DexScreener")
            print("✅ Market caps and volume data") 
            print("✅ Data quality validation")
            print("✅ Multi-source consistency checks")
            print("✅ Comprehensive metadata storage")
            
            print("\n🚀 Next steps:")
            print("1. Open data/coins.db in SQLite browser to explore")
            print("2. Run more enrichments with different tokens")
            print("3. Use the enriched data for trading strategies")
            print("4. Deploy the dashboard to visualize your data")
            
        # Show a sample of enriched data
        print("\n" + "=" * 30)
        print("SAMPLE ENRICHED DATA")
        print("=" * 30)
        
        import sqlite3, json
        conn = sqlite3.connect('data/coins.db')
        
        recent_coins = conn.execute("""
            SELECT c.symbol, cm.metadata 
            FROM coins c 
            JOIN coin_metadata cm ON c.id = cm.coin_id 
            ORDER BY c.updated_at DESC 
            LIMIT 3
        """).fetchall()
        
        for symbol, metadata_json in recent_coins:
            try:
                metadata = json.loads(metadata_json)
                data = metadata['enrichment_data']
                print(f"\n{symbol}:")
                print(f"  Price: ${data.get('price', 'N/A')}")
                print(f"  Market Cap: ${data.get('market_cap', 'N/A'):,.0f}" if data.get('market_cap') else "  Market Cap: N/A")
                print(f"  24h Volume: ${data.get('volume_24h', 'N/A'):,.0f}" if data.get('volume_24h') else "  24h Volume: N/A")
                print(f"  Sources: {', '.join(data.get('data_sources', []))}")
                print(f"  Quality Score: {data.get('enrichment_score', 0):.2f}/1.00")
            except:
                print(f"\n{symbol}: Data parsing error")
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())