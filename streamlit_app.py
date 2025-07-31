#!/usr/bin/env python3
"""
TrenchCoat Pro - Streamlit Cloud Launcher
Optimized for cloud deployment
"""
import streamlit as st
import os

# Set cloud environment
os.environ['STREAMLIT_CLOUD'] = 'true'
os.environ['DEMO_MODE'] = 'true'

# Configure page
st.set_page_config(
    page_title="TrenchCoat Pro - Live Demo",
    page_icon="🎯",
    layout="wide"
)

# Import and run ultra-premium dashboard
try:
    st.write("🔄 Loading TrenchCoat Pro Ultra-Premium Dashboard...")
    from ultra_premium_dashboard import UltraPremiumDashboard
    st.write("✅ Dashboard module imported successfully!")
    
    # Initialize dashboard
    dashboard = UltraPremiumDashboard()
    st.write("✅ Dashboard initialized successfully!")
    
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.info("📋 Falling back to simple demo version...")
    
    # Fallback to simple version
    exec(open('simple_app.py').read())
    
except Exception as e:
    st.error(f"❌ Dashboard error: {e}")
    st.error(f"Error type: {type(e).__name__}")
    import traceback
    st.code(traceback.format_exc())
    st.info("📋 Falling back to simple demo version...")
    
    # Fallback to simple version
    exec(open('simple_app.py').read())