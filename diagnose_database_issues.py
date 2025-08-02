#!/usr/bin/env python3
"""
Database Diagnostic Script - Identify and Fix Database Issues
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json

def diagnose_database_issues(db_path="data/trench.db"):
    """Comprehensive database diagnosis"""
    
    print("🔍 DATABASE DIAGNOSTIC REPORT")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Basic counts
        print("\n📊 BASIC STATISTICS:")
        cursor.execute("SELECT COUNT(*) FROM coins")
        total_coins = cursor.fetchone()[0]
        print(f"Total coins: {total_coins:,}")
        
        # 2. Recent updates
        cursor.execute("""
            SELECT COUNT(*) FROM coins 
            WHERE enrichment_timestamp > datetime('now', '-24 hours')
        """)
        recent_updates = cursor.fetchone()[0]
        print(f"Updated in last 24h: {recent_updates:,}")
        
        # 3. Data quality
        cursor.execute("""
            SELECT COUNT(*) FROM coins 
            WHERE current_price_usd IS NOT NULL AND current_price_usd > 0
        """)
        valid_prices = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM coins 
            WHERE market_cap_usd IS NOT NULL AND market_cap_usd > 0
        """)
        valid_market_caps = cursor.fetchone()[0]
        
        print(f"Valid prices: {valid_prices:,} ({valid_prices/total_coins*100:.1f}%)")
        print(f"Valid market caps: {valid_market_caps:,} ({valid_market_caps/total_coins*100:.1f}%)")
        
        # 4. Enrichment status
        cursor.execute("""
            SELECT COUNT(*) FROM coins 
            WHERE enrichment_timestamp IS NOT NULL
        """)
        ever_enriched = cursor.fetchone()[0]
        print(f"Ever enriched: {ever_enriched:,} ({ever_enriched/total_coins*100:.1f}%)")
        
        # 5. Data freshness analysis
        print("\n⏰ DATA FRESHNESS:")
        cursor.execute("""
            SELECT 
                MAX(enrichment_timestamp) as latest,
                MIN(enrichment_timestamp) as earliest,
                COUNT(*) as count
            FROM coins 
            WHERE enrichment_timestamp IS NOT NULL
        """)
        freshness = cursor.fetchone()
        if freshness[0]:
            latest = datetime.fromisoformat(freshness[0])
            age_hours = (datetime.now() - latest).total_seconds() / 3600
            print(f"Latest update: {freshness[0]} ({age_hours:.1f} hours ago)")
            print(f"Earliest update: {freshness[1]}")
        
        # 6. Top coins by market cap
        print("\n🏆 TOP 10 COINS BY MARKET CAP:")
        cursor.execute("""
            SELECT ticker, market_cap_usd, current_price_usd, enrichment_timestamp
            FROM coins 
            WHERE market_cap_usd IS NOT NULL 
            ORDER BY market_cap_usd DESC 
            LIMIT 10
        """)
        top_coins = cursor.fetchall()
        for i, coin in enumerate(top_coins, 1):
            ticker, mcap, price, updated = coin
            age = ""
            if updated:
                try:
                    update_time = datetime.fromisoformat(updated)
                    hours_ago = (datetime.now() - update_time).total_seconds() / 3600
                    age = f" ({hours_ago:.1f}h ago)"
                except:
                    age = " (unknown age)"
            
            print(f"{i:2d}. {ticker:12} ${mcap:12,.0f} ${price:.8f}{age}")
        
        # 7. Problematic data
        print("\n⚠️  PROBLEMATIC DATA:")
        
        # Coins with no price but have market cap
        cursor.execute("""
            SELECT COUNT(*) FROM coins 
            WHERE market_cap_usd IS NOT NULL 
            AND (current_price_usd IS NULL OR current_price_usd = 0)
        """)
        no_price_with_mcap = cursor.fetchone()[0]
        if no_price_with_mcap > 0:
            print(f"❌ {no_price_with_mcap} coins have market cap but no price")
        
        # Very old data
        cursor.execute("""
            SELECT COUNT(*) FROM coins 
            WHERE enrichment_timestamp < datetime('now', '-7 days')
            AND enrichment_timestamp IS NOT NULL
        """)
        very_old = cursor.fetchone()[0]
        if very_old > 0:
            print(f"⚠️  {very_old} coins have data older than 7 days")
        
        # 8. Image data
        print("\n🖼️  IMAGE DATA:")
        cursor.execute("SELECT COUNT(*) FROM coins WHERE image_url IS NOT NULL")
        with_images = cursor.fetchone()[0]
        print(f"Coins with images: {with_images:,} ({with_images/total_coins*100:.1f}%)")
        
        # 9. Database file size
        import os
        db_size = os.path.getsize(db_path) / 1024  # KB
        print(f"\n💾 DATABASE SIZE: {db_size:.1f} KB")
        
        conn.close()
        
        # 10. Health assessment
        print("\n🏥 HEALTH ASSESSMENT:")
        
        issues = []
        
        if recent_updates == 0:
            issues.append("❌ CRITICAL: No updates in last 24 hours")
        elif recent_updates < total_coins * 0.01:  # Less than 1% updated
            issues.append("⚠️  WARNING: Very few recent updates")
        
        if valid_prices < total_coins * 0.1:  # Less than 10% have valid prices
            issues.append("❌ CRITICAL: Low data quality - few valid prices")
        elif valid_prices < total_coins * 0.5:  # Less than 50%
            issues.append("⚠️  WARNING: Moderate data quality issues")
        
        if ever_enriched < total_coins * 0.5:  # Less than 50% ever enriched
            issues.append("⚠️  WARNING: Many coins never enriched")
        
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("✅ Database appears healthy")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if recent_updates == 0:
            print("1. Run mass enrichment to update coin data")
        if valid_prices < total_coins * 0.5:
            print("2. Check API connectivity and enrichment pipeline")
        if ever_enriched < total_coins * 0.5:
            print("3. Consider running comprehensive data backfill")
        
        return {
            'total_coins': total_coins,
            'recent_updates': recent_updates,
            'valid_prices': valid_prices,
            'data_quality_pct': valid_prices / total_coins * 100,
            'issues': issues
        }
        
    except Exception as e:
        print(f"❌ Database diagnostic failed: {e}")
        return None

def fix_database_issues():
    """Attempt to fix common database issues"""
    print("\n🔧 ATTEMPTING DATABASE FIXES...")
    
    try:
        # Check if enrichment system is running
        import subprocess
        import os
        
        # Look for enrichment scripts
        enrichment_scripts = [
            'database_optimizer_and_enricher.py',
            'final_mass_enrichment.py',
            'launch_mass_enrichment.py'
        ]
        
        available_scripts = []
        for script in enrichment_scripts:
            if os.path.exists(script):
                available_scripts.append(script)
        
        if available_scripts:
            print(f"✅ Found enrichment scripts: {', '.join(available_scripts)}")
            print("💡 Consider running one of these to update data:")
            for script in available_scripts:
                print(f"   python {script}")
        else:
            print("⚠️  No enrichment scripts found")
        
        # Check API connectivity
        print("\n🌐 TESTING API CONNECTIVITY:")
        try:
            import requests
            
            test_apis = [
                ("DexScreener", "https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112"),
                ("Jupiter", "https://price.jup.ag/v4/price?ids=SOL")
            ]
            
            for name, url in test_apis:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {name}: OK")
                    else:
                        print(f"⚠️  {name}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"❌ {name}: {str(e)}")
                    
        except ImportError:
            print("⚠️  requests module not available for API testing")
        
    except Exception as e:
        print(f"❌ Fix attempt failed: {e}")

if __name__ == "__main__":
    result = diagnose_database_issues()
    if result:
        print(f"\n📋 SUMMARY:")
        print(f"Total coins: {result['total_coins']:,}")
        print(f"Data quality: {result['data_quality_pct']:.1f}%")
        print(f"Issues found: {len(result['issues'])}")
        
        if result['issues']:
            fix_database_issues()