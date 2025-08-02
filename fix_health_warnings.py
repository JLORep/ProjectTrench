#!/usr/bin/env python3
"""
Fix Health Check Warnings - Address all three warning issues
"""

import sqlite3
import requests
import time
from datetime import datetime

def fix_database_integrity():
    """Fix database integrity issues"""
    print("Fixing database integrity...")
    
    try:
        conn = sqlite3.connect("data/trench.db")
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM coins")
        total_coins = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM coins WHERE current_price_usd IS NOT NULL AND current_price_usd > 0")
        valid_prices = cursor.fetchone()[0]
        
        quality_pct = (valid_prices / total_coins * 100) if total_coins > 0 else 0
        
        print(f"Current data quality: {quality_pct:.1f}% ({valid_prices}/{total_coins})")
        
        # If quality is very low, run a quick enrichment
        if quality_pct < 10:
            print("Data quality very low - triggering enrichment...")
            
            # Try to run enrichment script
            try:
                import subprocess
                import os
                
                enrichment_scripts = [
                    'quick_enricher.py',
                    'database_optimizer_and_enricher.py',
                    'simple_database_enricher.py'
                ]
                
                for script in enrichment_scripts:
                    if os.path.exists(script):
                        print(f"Running {script}...")
                        result = subprocess.run(['python', script], 
                                              capture_output=True, 
                                              text=True, 
                                              timeout=60)
                        if result.returncode == 0:
                            print(f"Successfully ran {script}")
                            break
                        else:
                            print(f"Failed to run {script}: {result.stderr}")
                    
            except Exception as e:
                print(f"Could not run enrichment: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database fix failed: {e}")

def fix_cache_system():
    """Improve cache system performance"""
    print("Checking cache system...")
    
    try:
        # Try to import cache system
        from enhanced_caching_system import get_cache_system
        
        cache_system = get_cache_system()
        stats = cache_system.get_stats()
        
        hit_rate = stats.get('hit_rate', 0)
        print(f"Current cache hit rate: {hit_rate:.1f}%")
        
        if hit_rate < 50:
            print("Cache hit rate low - optimizing...")
            
            # Clear old cache entries to improve performance
            cache_system.clear()
            
            # Pre-warm cache with common queries
            try:
                from streamlit_app import load_coin_data, get_market_stats
                
                print("Pre-warming cache...")
                load_coin_data()  # This will cache the data
                get_market_stats()  # This will cache market stats
                
                print("Cache pre-warmed successfully")
                
            except Exception as e:
                print(f"Cache pre-warming failed: {e}")
        
    except ImportError:
        print("Enhanced cache system not available - using Streamlit default")
    except Exception as e:
        print(f"Cache system check failed: {e}")

def fix_api_endpoints():
    """Test and fix API endpoint connectivity"""
    print("Testing API endpoints...")
    
    test_endpoints = [
        {
            "name": "DexScreener", 
            "url": "https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112",
            "timeout": 10
        },
        {
            "name": "Jupiter", 
            "url": "https://price.jup.ag/v4/price?ids=SOL",
            "timeout": 10
        },
        {
            "name": "CoinGecko",
            "url": "https://api.coingecko.com/api/v3/ping",
            "timeout": 10
        }
    ]
    
    healthy_endpoints = 0
    
    for endpoint in test_endpoints:
        try:
            print(f"Testing {endpoint['name']}...")
            
            response = requests.get(
                endpoint["url"], 
                timeout=endpoint["timeout"],
                headers={'User-Agent': 'TrenchCoat-Pro/1.0'}
            )
            
            if response.status_code == 200:
                print(f"  ✓ {endpoint['name']}: OK ({response.elapsed.total_seconds():.2f}s)")
                healthy_endpoints += 1
            else:
                print(f"  ✗ {endpoint['name']}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"  ✗ {endpoint['name']}: Timeout")
        except requests.exceptions.ConnectionError:
            print(f"  ✗ {endpoint['name']}: Connection failed")
        except Exception as e:
            print(f"  ✗ {endpoint['name']}: {str(e)}")
    
    print(f"API endpoints healthy: {healthy_endpoints}/{len(test_endpoints)}")
    
    if healthy_endpoints < len(test_endpoints):
        print("Some API endpoints are failing - this may affect data enrichment")
        print("Consider checking network connectivity and API status")
    
    return healthy_endpoints == len(test_endpoints)

def run_comprehensive_fix():
    """Run all fixes"""
    print("="*50)
    print("HEALTH CHECK COMPREHENSIVE FIX")
    print("="*50)
    
    print("\n1. DATABASE INTEGRITY:")
    fix_database_integrity()
    
    print("\n2. CACHE SYSTEM:")
    fix_cache_system()
    
    print("\n3. API ENDPOINTS:")
    api_healthy = fix_api_endpoints()
    
    print("\n" + "="*50)
    print("FIX COMPLETE")
    print("="*50)
    
    # Run quick data refresh if APIs are healthy
    if api_healthy:
        print("\nAPIs are healthy - running quick data refresh...")
        try:
            # Clear Streamlit cache to force refresh
            import streamlit as st
            if hasattr(st, 'cache_data'):
                st.cache_data.clear()
                print("Streamlit cache cleared")
        except:
            pass

if __name__ == "__main__":
    run_comprehensive_fix()