#!/usr/bin/env python3
"""
TRENCHCOAT RUG INTELLIGENCE ANALYZER
Analyzes historical patterns and identifies profitable rug opportunities
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.analysis.rug_intelligence import RugIntelligenceEngine
from src.data.database import CoinDatabase
from src.trading.automated_trader import AutomatedTrader

async def analyze_historical_rugs():
    """Analyze historical data to find profitable rug patterns"""
    print("RUG INTELLIGENCE ANALYZER")
    print("=" * 50)
    
    db = CoinDatabase()
    rug_engine = RugIntelligenceEngine(db)
    
    print("Analyzing historical data for rug patterns...")
    
    try:
        # Analyze historical rugs
        profitable_rugs = await rug_engine.analyze_historical_rugs()
        
        print(f"\nFOUND {len(profitable_rugs)} TOKENS THAT HIT 50%+ BEFORE RUGGING!")
        print("=" * 60)
        
        # Show top performers
        if profitable_rugs:
            print("\nTOP PROFIT OPPORTUNITIES:")
            print("-" * 40)
            
            # Sort by profit potential
            sorted_rugs = sorted(profitable_rugs, 
                               key=lambda x: x.discovery_to_peak_multiplier, 
                               reverse=True)
            
            for i, rug in enumerate(sorted_rugs[:5], 1):
                print(f"\n{i}. {rug.symbol}")
                print(f"   Peak Multiplier: {rug.discovery_to_peak_multiplier:.2f}x")
                print(f"   Market Cap: ${rug.launch_price * 1000000:,.0f}")
                print(f"   Volume: ${rug.discovery_volume:,.0f}")
                if rug.rug_timestamp:
                    time_to_rug = (rug.rug_timestamp - rug.discovery_timestamp).total_seconds() / 3600
                    print(f"   Time to Peak: {time_to_rug:.1f} hours")
        
        # Show pattern analysis
        if hasattr(rug_engine, 'rug_patterns') and rug_engine.rug_patterns:
            patterns = rug_engine.rug_patterns
            print("\n" + "=" * 40)
            print("PROFITABLE RUG PATTERNS IDENTIFIED:")
            print("=" * 40)
            print(f"Average peak multiplier: {patterns['avg_discovery_to_peak']:.2f}x")
            print(f"Average time to peak: {patterns['avg_time_to_peak']:.1f} hours")
            print(f"Optimal exit strategy: -{patterns['success_indicators']['optimal_exit_drop']*100:.0f}% from peak")
            print(f"Max hold time: {patterns['success_indicators']['max_hold_time_hours']} hours")
            
            print("\nSTRATEGY READY FOR DEPLOYMENT!")
            print("🎯 Target: 50%+ gains before exit")
            print("🚨 Exit trigger: 15% drop from peak OR rug detection")
            print("⏰ Max hold time: 12 hours")
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

async def test_new_token_analysis():
    """Test the analysis of a new token"""
    print("\n" + "=" * 50)
    print("TESTING NEW TOKEN ANALYSIS")
    print("=" * 50)
    
    db = CoinDatabase()
    rug_engine = RugIntelligenceEngine(db)
    
    # Test with USDC (should be low risk)
    test_signal = {
        'contract_address': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        'symbol': 'USDC',
        'signal_type': 'BUY',
        'confidence': 0.8
    }
    
    try:
        analysis = await rug_engine.analyze_new_token(
            test_signal['contract_address'], 
            test_signal
        )
        
        print(f"\nANALYSIS RESULTS FOR {analysis.get('symbol', 'UNKNOWN')}:")
        print("-" * 30)
        print(f"Action: {analysis['action']}")
        print(f"Confidence: {analysis['confidence']:.2f}")
        print(f"Risk Level: {analysis['risk_level']}")
        print(f"Expected Return: {analysis.get('expected_return', 0):.1f}x")
        print(f"Reasoning: {analysis['reasoning']}")
        
        scores = analysis.get('scores', {})
        print(f"\nDETAILED SCORES:")
        for metric, score in scores.items():
            print(f"  {metric.title()}: {score:.2f}")
        
        if 'exit_strategy' in analysis:
            exit_strat = analysis['exit_strategy']
            print(f"\nEXIT STRATEGY:")
            print(f"  Profit Target: ${exit_strat.get('profit_target', 0):.6f}")
            print(f"  Stop Loss: ${exit_strat.get('stop_loss', 0):.6f}")
            print(f"  Time Limit: {exit_strat.get('time_limit_hours', 0)} hours")
    
    except Exception as e:
        print(f"Error testing token: {e}")
        import traceback
        traceback.print_exc()

async def simulate_automated_trading():
    """Simulate the automated trading system"""
    print("\n" + "=" * 50)
    print("AUTOMATED TRADING SIMULATION")
    print("=" * 50)
    
    try:
        trader = AutomatedTrader(initial_balance=10000)
        
        # Test signal processing
        test_signal = {
            'contract_address': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'symbol': 'USDC',
            'signal_type': 'BUY',
            'confidence': 0.8
        }
        
        print("Processing test signal...")
        trade = await trader._evaluate_new_signal(test_signal)
        
        if trade:
            print(f"\nTRADE EXECUTED:")
            print(f"Symbol: {trade.symbol}")
            print(f"Entry Price: ${trade.entry_price:.6f}")
            print(f"Position Size: {trade.position_size:.1%}")
            print(f"Position Value: ${trade.position_value:.2f}")
            print(f"Profit Target: ${trade.profit_target:.6f}")
            print(f"Stop Loss: ${trade.stop_loss:.6f}")
        else:
            print("No trade executed (signal filtered out)")
        
        # Generate report
        report = trader.generate_daily_report()
        print(f"\nDAILY PERFORMANCE:")
        perf = report['trading_performance']
        print(f"Starting Balance: ${perf['starting_balance']:,.2f}")
        print(f"Current Balance: ${perf['ending_balance']:,.2f}")
        print(f"Total Return: {perf['total_return_pct']:+.2f}%")
        print(f"Total Trades: {perf['total_trades']}")
        
    except Exception as e:
        print(f"Error in trading simulation: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main analysis runner"""
    print("TRENCHCOAT RUG INTELLIGENCE SYSTEM")
    print("The Ultimate Profit Extraction Engine")
    print("=" * 60)
    
    # Run all analyses
    await analyze_historical_rugs()
    await test_new_token_analysis() 
    await simulate_automated_trading()
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Deploy with real Telegram monitoring")
    print("2. Connect to actual trading APIs")
    print("3. Start making disgusting amounts of money!")
    print("4. Scale to Azure for 24/7 operation")

if __name__ == "__main__":
    asyncio.run(main())