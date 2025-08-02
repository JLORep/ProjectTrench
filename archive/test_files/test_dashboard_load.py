#!/usr/bin/env python3
"""
Test dashboard loading to isolate the issue
"""
import streamlit as st

st.set_page_config(
    page_title="TrenchCoat Pro | Live Trading Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("# Dashboard Load Test")

try:
    st.write("Testing branding system import...")
    from branding_system import BrandingSystem
    branding = BrandingSystem()
    st.success("✅ Branding system imported successfully")
    
    st.write("Testing ultra premium dashboard import...")
    from ultra_premium_dashboard import UltraPremiumDashboard
    st.success("✅ Dashboard class imported successfully")
    
    st.write("Testing dashboard initialization...")
    dashboard = UltraPremiumDashboard()
    st.success("✅ Dashboard initialized successfully")
    
    st.write("Dashboard should be rendered above this message")
    
except Exception as e:
    st.error(f"❌ Error: {e}")
    import traceback
    st.code(traceback.format_exc())