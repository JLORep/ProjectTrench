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
    from ultra_premium_dashboard import UltraPremiumDashboard
    
    # Add cloud-specific header
    st.markdown('''
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #065f46 0%, #059669 100%); 
                border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h2>🎯 TrenchCoat Pro - Live Demo</h2>
        <p>Ultra-Premium Cryptocurrency Trading Dashboard</p>
        <p><small>Running in DEMO mode - No live trading</small></p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize dashboard
    dashboard = UltraPremiumDashboard()
    
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please ensure all dependencies are installed correctly.")
except Exception as e:
    st.error(f"Error: {e}")
    st.info("Please check the application logs for more details.")