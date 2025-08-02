#!/usr/bin/env python3
"""Test script to find the actual deployment error"""

import sys
import traceback

def test_imports():
    """Test all imports to find which one is failing"""
    
    modules_to_test = [
        "streamlit",
        "pandas", 
        "numpy",
        "plotly.graph_objects",
        "enhanced_security_dashboard",
        "security_dashboard",
        "comprehensive_monitoring",
        "super_claude_system",
        "super_claude_commands",
        "super_claude_personas",
        "mcp_server_integration",
        "coin_image_system",
        "premium_chart_system",
        "solana_strategy_engine",
        "enhanced_caching_system",
        "health_check_system",
        "event_system",
        "database_connection_pool",
        "memecoin_hunt_hub_ui",
        "alpha_radar_system",
        "live_signals_dashboard",
        "mathematical_runners_dashboard",
        "comprehensive_dev_blog_system",
        "enhanced_blog_integration"
    ]
    
    failed = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed.append((module, str(e)))
        except Exception as e:
            print(f"⚠️  {module}: {type(e).__name__}: {e}")
            
    if failed:
        print("\n❌ FAILED IMPORTS:")
        for module, error in failed:
            print(f"  - {module}: {error}")
    else:
        print("\n✅ All imports successful!")

if __name__ == "__main__":
    test_imports()