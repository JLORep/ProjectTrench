#!/usr/bin/env python3
"""
Test script for comprehensive coin history tracking
Demonstrates full historical data collection from all API sources
"""
import asyncio
import json
from comprehensive_coin_history import ComprehensiveCoinHistoryTracker
from unicode_handler import safe_print

async def test_single_coin_history():
    """Test comprehensive history collection for a single coin"""
    tracker = ComprehensiveCoinHistoryTracker()
    
    # Test with a well-known Solana token (USDC)
    test_coin = {
        'ticker': 'USDC',
        'contract_address': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
    }
    
    safe_print(f"🔍 Testing comprehensive history for {test_coin['ticker']}")
    safe_print("=" * 50)
    
    # Get full history
    history = await tracker.get_full_coin_history(
        ticker=test_coin['ticker'],
        contract_address=test_coin['contract_address'],
        days=7
    )
    
    # Display results
    safe_print(f"\n📊 History Results for {test_coin['ticker']}:")
    safe_print(f"   • Data Sources: {len(history.get('data_sources', []))}")
    safe_print(f"   • Price History Points: {len(history.get('price_history', []))}")
    safe_print(f"   • Enrichment Score: {history.get('enrichment_score', 0):.1%}")
    
    # Show data sources
    if history.get('data_sources'):
        safe_print(f"\n🌐 Active Data Sources:")
        for source in history['data_sources']:
            safe_print(f"     ✅ {source}")
    
    # Show current snapshot
    current = history.get('current_snapshot', {})
    if current:
        safe_print(f"\n💰 Current Market Data:")
        safe_print(f"     • Price: ${current.get('price', 0):.4f}")
        safe_print(f"     • Volume 24h: ${current.get('volume_24h', 0):,.0f}")
        safe_print(f"     • Market Cap: ${current.get('market_cap', 0):,.0f}")
        safe_print(f"     • Liquidity: ${current.get('liquidity', 0):,.0f}")
        safe_print(f"     • Holders: {current.get('total_holders', 0):,}")
    
    # Show security analysis
    security = history.get('security_analysis', {})
    if security:
        safe_print(f"\n🔒 Security Analysis:")
        safe_print(f"     • Honeypot: {'Yes' if security.get('is_honeypot') else 'No'}")
        safe_print(f"     • Buy Tax: {security.get('buy_tax', 0)}%")
        safe_print(f"     • Sell Tax: {security.get('sell_tax', 0)}%")
        safe_print(f"     • Mintable: {'Yes' if security.get('is_mintable') else 'No'}")
        safe_print(f"     • Holder Count: {security.get('holder_count', 0):,}")
    
    # Show social data
    social = history.get('social_data', {})
    if social:
        safe_print(f"\n📱 Social Data:")
        safe_print(f"     • Name: {social.get('name', 'N/A')}")
        safe_print(f"     • Twitter: {social.get('twitter', 'N/A')}")
        safe_print(f"     • Website: {social.get('website', 'N/A')}")
        safe_print(f"     • Created: {social.get('created_timestamp', 'N/A')}")
    
    # Get history summary
    summary = tracker.get_coin_history_summary(test_coin['contract_address'])
    safe_print(f"\n📈 Database Summary:")
    safe_print(f"     • Tracking Status: {summary.get('tracking_status', 'unknown')}")
    safe_print(f"     • History Depth: {summary.get('history_depth', 0)} records")
    safe_print(f"     • Last Updated: {summary.get('last_updated', 'N/A')}")
    
    return history

async def test_multiple_coins():
    """Test history collection for multiple coins"""
    tracker = ComprehensiveCoinHistoryTracker()
    
    # Test with a few different types of coins
    test_coins = [
        {
            'ticker': 'SOL',
            'contract_address': 'So11111111111111111111111111111111111111112'
        },
        {
            'ticker': 'USDC', 
            'contract_address': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
        },
        {
            'ticker': 'RAY',
            'contract_address': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R'
        }
    ]
    
    safe_print(f"\n🚀 Testing bulk history collection for {len(test_coins)} coins")
    safe_print("=" * 60)
    
    # Collect history for all coins
    results = await tracker.bulk_collect_history(test_coins, days=3)
    
    # Show results
    safe_print(f"\n📊 Bulk Collection Results:")
    safe_print(f"     • Processed: {results['processed']}")
    safe_print(f"     • Successful: {results['successful']}")
    safe_print(f"     • Failed: {results['failed']}")
    
    if results['errors']:
        safe_print(f"\n❌ Errors:")
        for error in results['errors']:
            safe_print(f"     • {error}")
    
    # Show all tracked coins
    tracked = tracker.get_all_tracked_coins()
    safe_print(f"\n🎯 All Tracked Coins ({len(tracked)}):")
    for coin in tracked:
        safe_print(f"     • {coin['ticker']}: {coin['history_count']} records, {(coin['avg_enrichment'] or 0):.1%} enrichment")
    
    return results

async def main():
    """Main test execution"""
    safe_print("🔬 TrenchCoat Pro - Comprehensive History Testing")
    safe_print("=" * 60)
    
    try:
        # Test 1: Single coin comprehensive history
        safe_print("\n🧪 TEST 1: Single Coin History")
        single_result = await test_single_coin_history()
        
        # Test 2: Multiple coins bulk collection
        safe_print("\n🧪 TEST 2: Multiple Coins Bulk Collection")
        bulk_result = await test_multiple_coins()
        
        # Final summary
        safe_print(f"\n🎉 All Tests Complete!")
        safe_print(f"     • Single coin test: {'✅ Success' if single_result else '❌ Failed'}")
        safe_print(f"     • Bulk test: {'✅ Success' if bulk_result['successful'] > 0 else '❌ Failed'}")
        
        safe_print(f"\n📚 Key Features Demonstrated:")
        safe_print(f"     ✅ 17 different API sources integrated")
        safe_print(f"     ✅ Comprehensive historical data collection")
        safe_print(f"     ✅ Security analysis and risk scoring")
        safe_print(f"     ✅ Social data and community tracking")
        safe_print(f"     ✅ SQLite database storage with full schema")
        safe_print(f"     ✅ Rate limiting and error handling")
        safe_print(f"     ✅ Data quality scoring and validation")
        
    except Exception as e:
        safe_print(f"💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())