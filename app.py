#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrenchCoat Pro - Ultra Premium Trading Platform
Apple/PayPal-level design with live updates and AI
"""
import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment for demo mode if not specified
if 'ENVIRONMENT' not in os.environ:
    os.environ['ENVIRONMENT'] = 'DEMO'
    os.environ['LIVE_TRADING_ENABLED'] = 'False'
    os.environ['DEMO_MODE'] = 'True'

def main():
    """Main application entry point"""
    print("🚀 Starting TrenchCoat Pro - Ultra Premium Dashboard")
    print("⚠️  Running in DEMO mode - No live trading")
    print("✨ Loading streamlit_app.py with all fixes")
    
    try:
        # Simply run our main streamlit app
        # It handles page config and everything else
        import streamlit_app
        
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()