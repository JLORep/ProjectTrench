#!/usr/bin/env python3
"""Test Hunt Hub UI for errors"""

import traceback

try:
    from memecoin_hunt_hub_ui import render_hunt_hub_dashboard
    print("✅ Hunt Hub UI imported successfully")
    
    # Test if it's a Streamlit-specific issue
    import streamlit as st
    print("✅ Streamlit imported")
    
    # Test the render function (this will fail outside streamlit but should show us any syntax errors)
    print("Testing render function...")
    render_hunt_hub_dashboard()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"❌ Render error: {e}")
    traceback.print_exc()