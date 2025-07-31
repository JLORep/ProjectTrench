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
    page_title="TrenchCoat Pro | Live Trading Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import and run ultra-premium dashboard
try:
    # Create loading placeholder
    loading_placeholder = st.empty()
    
    with loading_placeholder.container():
        st.markdown("""
        <div style='text-align: center; padding: 3rem; margin: 2rem 0;
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
                    border-radius: 15px; border: 1px solid rgba(16, 185, 129, 0.3);'>
            <h2 style='color: #10b981; margin: 0;'>🔄 Loading TrenchCoat Pro</h2>
            <p style='color: #a3a3a3; margin-top: 0.5rem;'>Ultra-Premium Trading Intelligence</p>
            <div style='margin-top: 1rem;'>
                <div style='display: inline-block; width: 8px; height: 8px; border-radius: 50%; 
                           background: #10b981; margin: 0 4px; animation: pulse 1.5s infinite;'></div>
                <div style='display: inline-block; width: 8px; height: 8px; border-radius: 50%; 
                           background: #10b981; margin: 0 4px; animation: pulse 1.5s infinite 0.2s;'></div>
                <div style='display: inline-block; width: 8px; height: 8px; border-radius: 50%; 
                           background: #10b981; margin: 0 4px; animation: pulse 1.5s infinite 0.4s;'></div>
            </div>
            <p style='color: #6b7280; font-size: 12px; margin-top: 1rem;'>
                Loading advanced analytics & ML models...
            </p>
        </div>
        <style>
            @keyframes pulse {
                0%, 80%, 100% { opacity: 0.3; }
                40% { opacity: 1; }
            }
        </style>
        """, unsafe_allow_html=True)
    
    # Import dashboard
    from ultra_premium_dashboard import UltraPremiumDashboard
    
    # Initialize dashboard
    dashboard = UltraPremiumDashboard()
    
    # Clear loading message once everything is ready
    loading_placeholder.empty()
    
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