"""
Data Enrichment Tracker - Analyze what data is missing and needs enrichment
"""
import sqlite3
import pandas as pd
from datetime import datetime
import json

def analyze_data_completeness():
    """Analyze database to identify missing data patterns"""
    conn = sqlite3.connect("data/trench.db")
    
    # Get all data into pandas for analysis
    query = """
    SELECT ticker, ca, discovery_time, discovery_price, discovery_mc,
           liquidity, peak_volume, smart_wallets, dex_paid, sol_price,
           history, axiom_price, axiom_mc, axiom_volume
    FROM coins
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    total_coins = len(df)
    
    # Analyze each field
    field_analysis = {}
    
    for column in df.columns:
        non_null = df[column].notna().sum()
        non_zero = (df[column] != 0).sum() if df[column].dtype in ['float64', 'int64'] else non_null
        
        field_analysis[column] = {
            'total': total_coins,
            'non_null': non_null,
            'non_zero': non_zero,
            'null_count': total_coins - non_null,
            'zero_count': non_null - non_zero if df[column].dtype in ['float64', 'int64'] else 0,
            'completeness_pct': (non_zero / total_coins) * 100,
            'data_type': str(df[column].dtype)
        }
    
    # Identify critical missing data
    critical_fields = ['axiom_price', 'liquidity', 'axiom_mc', 'axiom_volume', 'smart_wallets']
    
    # Find coins missing critical data
    missing_critical = df[
        (df['axiom_price'].isna() | (df['axiom_price'] == 0)) |
        (df['liquidity'].isna() | (df['liquidity'] == 0)) |
        (df['axiom_mc'].isna() | (df['axiom_mc'] == 0))
    ]
    
    # API requirements for enrichment
    enrichment_requirements = {
        'DexScreener': ['axiom_price', 'liquidity', 'axiom_volume', 'axiom_mc'],
        'Birdeye': ['smart_wallets', 'peak_volume', 'dex_paid'],
        'Jupiter': ['axiom_price', 'liquidity'],
        'CoinGecko': ['axiom_mc', 'axiom_volume'],
        'Solscan': ['smart_wallets', 'history']
    }
    
    return {
        'total_coins': total_coins,
        'field_analysis': field_analysis,
        'missing_critical_count': len(missing_critical),
        'missing_critical_tickers': missing_critical['ticker'].tolist()[:20],  # First 20
        'enrichment_requirements': enrichment_requirements,
        'recommendations': generate_recommendations(field_analysis)
    }

def generate_recommendations(field_analysis):
    """Generate specific recommendations for data enrichment"""
    recommendations = []
    
    # Check price data
    if field_analysis['axiom_price']['completeness_pct'] < 50:
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Missing current price data',
            'affected_pct': 100 - field_analysis['axiom_price']['completeness_pct'],
            'solution': 'Fetch from DexScreener or Jupiter API',
            'impact': 'Cannot calculate gains or trading signals'
        })
    
    # Check liquidity
    if field_analysis['liquidity']['completeness_pct'] < 50:
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Missing liquidity data',
            'affected_pct': 100 - field_analysis['liquidity']['completeness_pct'],
            'solution': 'Fetch from DexScreener API',
            'impact': 'Cannot assess trading safety'
        })
    
    # Check market cap
    if field_analysis['axiom_mc']['completeness_pct'] < 50:
        recommendations.append({
            'priority': 'MEDIUM',
            'issue': 'Missing market cap data',
            'affected_pct': 100 - field_analysis['axiom_mc']['completeness_pct'],
            'solution': 'Calculate from price * supply or fetch from APIs',
            'impact': 'Cannot properly categorize coins'
        })
    
    # Check wallet data
    if field_analysis['smart_wallets']['completeness_pct'] < 30:
        recommendations.append({
            'priority': 'MEDIUM',
            'issue': 'Missing smart wallet data',
            'affected_pct': 100 - field_analysis['smart_wallets']['completeness_pct'],
            'solution': 'Fetch from Birdeye or Solscan API',
            'impact': 'Cannot track whale activity'
        })
    
    return recommendations

def create_enrichment_plan():
    """Create a specific plan for enriching missing data"""
    analysis = analyze_data_completeness()
    
    plan = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_coins': analysis['total_coins'],
            'coins_needing_enrichment': analysis['missing_critical_count'],
            'priority_fields': ['axiom_price', 'liquidity', 'axiom_mc', 'axiom_volume']
        },
        'api_strategy': {
            'primary': 'DexScreener - for price, liquidity, volume',
            'secondary': 'Jupiter - for backup price data',
            'tertiary': 'Birdeye - for wallet and holder data'
        },
        'execution_steps': [
            {
                'step': 1,
                'action': 'Batch fetch all coins with missing axiom_price',
                'api': 'DexScreener',
                'batch_size': 50,
                'rate_limit': '300 requests/minute'
            },
            {
                'step': 2,
                'action': 'Update liquidity data for all coins',
                'api': 'DexScreener',
                'batch_size': 50,
                'rate_limit': '300 requests/minute'
            },
            {
                'step': 3,
                'action': 'Fetch holder/wallet data',
                'api': 'Birdeye',
                'batch_size': 20,
                'rate_limit': '100 requests/minute'
            }
        ],
        'estimated_time': 'Approximately 2-3 hours for full enrichment',
        'recommendations': analysis['recommendations']
    }
    
    return plan

def generate_enrichment_report():
    """Generate comprehensive enrichment report"""
    analysis = analyze_data_completeness()
    plan = create_enrichment_plan()
    
    report = f"""
# TrenchCoat Pro - Data Enrichment Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Database Overview
- Total Coins: {analysis['total_coins']:,}
- Coins Needing Critical Data: {analysis['missing_critical_count']:,}
- Overall Data Quality: {sum(f['completeness_pct'] for f in analysis['field_analysis'].values()) / len(analysis['field_analysis']):.1f}%

## Field-by-Field Analysis
"""
    
    for field, stats in analysis['field_analysis'].items():
        report += f"\n### {field}"
        report += f"\n- Completeness: {stats['completeness_pct']:.1f}%"
        report += f"\n- Non-null values: {stats['non_null']:,}/{stats['total']:,}"
        if stats['zero_count'] > 0:
            report += f"\n- Zero values: {stats['zero_count']:,}"
        report += "\n"
    
    report += "\n## Priority Recommendations\n"
    for rec in analysis['recommendations']:
        report += f"\n### [{rec['priority']}] {rec['issue']}"
        report += f"\n- Affected: {rec['affected_pct']:.1f}% of coins"
        report += f"\n- Solution: {rec['solution']}"
        report += f"\n- Impact: {rec['impact']}\n"
    
    report += "\n## Enrichment Execution Plan\n"
    for step in plan['execution_steps']:
        report += f"\n{step['step']}. {step['action']}"
        report += f"\n   - API: {step['api']}"
        report += f"\n   - Batch Size: {step['batch_size']}"
        report += f"\n   - Rate Limit: {step['rate_limit']}\n"
    
    return report

if __name__ == "__main__":
    # Generate and save report
    report = generate_enrichment_report()
    
    with open("data_enrichment_report.md", "w") as f:
        f.write(report)
    
    print("Data Enrichment Report Generated!")
    print("\nQuick Summary:")
    
    analysis = analyze_data_completeness()
    print(f"Total Coins: {analysis['total_coins']:,}")
    print(f"Missing Critical Data: {analysis['missing_critical_count']:,}")
    print("\nTop Missing Fields:")
    for field, stats in sorted(analysis['field_analysis'].items(), 
                              key=lambda x: x[1]['completeness_pct']):
        if stats['completeness_pct'] < 50:
            print(f"  - {field}: {stats['completeness_pct']:.1f}% complete")