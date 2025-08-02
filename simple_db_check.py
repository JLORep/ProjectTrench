#!/usr/bin/env python3
"""
Simple Database Check - No Unicode Issues
"""

import sqlite3
from datetime import datetime

def check_database():
    try:
        conn = sqlite3.connect("data/trench.db")
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM coins")
        total_coins = cursor.fetchone()[0]
        print(f"Total coins: {total_coins}")
        
        # Recent updates
        cursor.execute("SELECT COUNT(*) FROM coins WHERE enrichment_timestamp > datetime('now', '-24 hours')")
        recent_updates = cursor.fetchone()[0]
        print(f"Recent updates (24h): {recent_updates}")
        
        # Valid prices
        cursor.execute("SELECT COUNT(*) FROM coins WHERE current_price_usd IS NOT NULL AND current_price_usd > 0")
        valid_prices = cursor.fetchone()[0]
        print(f"Valid prices: {valid_prices}")
        
        # Data quality percentage
        quality_pct = (valid_prices / total_coins * 100) if total_coins > 0 else 0
        print(f"Data quality: {quality_pct:.1f}%")
        
        # Latest update
        cursor.execute("SELECT MAX(enrichment_timestamp) FROM coins WHERE enrichment_timestamp IS NOT NULL")
        latest = cursor.fetchone()[0]
        if latest:
            try:
                latest_dt = datetime.fromisoformat(latest)
                hours_ago = (datetime.now() - latest_dt).total_seconds() / 3600
                print(f"Latest update: {hours_ago:.1f} hours ago")
            except:
                print(f"Latest update: {latest}")
        
        conn.close()
        
        # Identify issues
        issues = []
        if recent_updates == 0:
            issues.append("No recent updates")
        if quality_pct < 50:
            issues.append("Low data quality")
        if total_coins == 0:
            issues.append("Empty database")
        
        print(f"Issues: {', '.join(issues) if issues else 'None detected'}")
        
        return {
            'total_coins': total_coins,
            'recent_updates': recent_updates,
            'valid_prices': valid_prices,
            'quality_pct': quality_pct,
            'issues': issues
        }
        
    except Exception as e:
        print(f"Database check failed: {e}")
        return None

if __name__ == "__main__":
    check_database()