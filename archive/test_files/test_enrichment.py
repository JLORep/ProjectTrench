#!/usr/bin/env python3
"""
Quick test script to verify the enrichment system works
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_api_providers():
    """Test the free API providers"""
    print("Testing Free API Providers...")
    
    try:
        from src.data.free_api_providers import FreeAPIProviders
        
        async with FreeAPIProviders() as api:
            # Test DexScreener with a popular Solana token (USDC)
            print("Testing DexScreener API...")
            usdc_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            dex_data = await api.get_dexscreener_data(usdc_address)
            
            if dex_data:
                print(f"SUCCESS DexScreener: Got data for USDC - Price: ${dex_data.get('price', 'N/A')}")
            else:
                print("FAILED DexScreener: No data received")
            
            # Test Jupiter API
            print("Testing Jupiter API...")
            jupiter_data = await api.get_jupiter_price([usdc_address])
            
            if jupiter_data:
                print(f"SUCCESS Jupiter: Got data for USDC")
            else:
                print("FAILED Jupiter: No data received")
            
            # Test Solscan API
            print("Testing Solscan API...")
            solscan_data = await api.get_solscan_token_info(usdc_address)
            
            if solscan_data:
                print(f"SUCCESS Solscan: Got token info - Name: {solscan_data.get('name', 'N/A')}")
            else:
                print("FAILED Solscan: No data received")
            
            # Test comprehensive data
            print("Testing comprehensive data aggregation...")
            comprehensive = await api.get_comprehensive_data(usdc_address, "USDC")
            
            if comprehensive:
                sources = comprehensive.get('data_sources', [])
                score = comprehensive.get('enrichment_score', 0)
                print(f"SUCCESS Comprehensive: Score {score:.2f}, Sources: {', '.join(sources)}")
            else:
                print("FAILED Comprehensive: No data aggregated")
        
        print("API Provider tests completed!")
        
    except Exception as e:
        print(f"ERROR testing API providers: {e}")
        import traceback
        traceback.print_exc()

async def test_database():
    """Test database operations"""
    print("\nTesting Database Operations...")
    
    try:
        from src.data.database import CoinDatabase
        
        db = CoinDatabase()
        
        # Test adding a coin
        coin_id = db.add_coin("USDC", "USD Coin", market_cap=50000000000)
        print(f"SUCCESS Database: Added coin with ID {coin_id}")
        
        # Test adding price data
        from datetime import datetime
        db.add_price_data(
            coin_id=coin_id,
            timestamp=datetime.now(),
            timeframe="1h",
            open_price=1.0001,
            high=1.0002,
            low=1.0000,
            close=1.0001,
            volume=1000000
        )
        print("SUCCESS Database: Added price data")
        
        # Test retrieving data
        price_df = db.get_price_data("USDC", "1h")
        print(f"SUCCESS Database: Retrieved {len(price_df)} price records")
        
        print("Database tests completed!")
        
    except Exception as e:
        print(f"ERROR testing database: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    print("TrenchCoat Enrichment System Test Suite")
    print("=" * 50)
    
    await test_api_providers()
    await test_database()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("\nTo start enriching your coins.db, run:")
    print("   python scripts/enrich_coins.py --help")

if __name__ == "__main__":
    asyncio.run(main())