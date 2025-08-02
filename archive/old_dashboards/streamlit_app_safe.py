#!/usr/bin/env python3
# DEPLOYMENT_TIMESTAMP: 2025-08-01 21:30:00 - SAFE VERSION: Removing potential loops
# -*- coding: utf-8 -*-
"""
TrenchCoat Pro v2.3.0 - Safe Version
Removing potential infinite loops and circular dependencies
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import os
import sqlite3
import hashlib

# Set environment
os.environ['STREAMLIT_CLOUD'] = 'true'
os.environ['DEMO_MODE'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure page
st.set_page_config(
    page_title="TrenchCoat Pro | Premium Crypto Trading Intelligence",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simple header
st.markdown("### 🎯 TrenchCoat Pro v2.3.0 | Premium Crypto Intelligence")
st.success("✅ Safe Mode - Debugging spinning circle issue")

# Create tabs
tab1, tab2, tab3 = st.tabs(["🗄️ Coin Data", "📊 Live Dashboard", "🛠️ Debug Info"])

with tab1:
    st.header("🗄️ Coin Data")
    st.markdown("### 💎 Live Cryptocurrency Analytics")
    
    # Clear session button
    if st.button("🔄 Clear All Session State"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session cleared! Refreshing...")
        st.rerun()
    
    # Show session state
    st.write("Current session state keys:", list(st.session_state.keys()))
    
    # Simple database query
    try:
        db_path = "data/trench.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT ticker, ca, liquidity FROM coins LIMIT 10")
            rows = cursor.fetchall()
            conn.close()
            
            st.success(f"✅ Database connected - Found {len(rows)} coins")
            
            for row in rows:
                ticker, ca, liquidity = row
                st.write(f"- {ticker}: {ca[:20]}... | Liquidity: ${liquidity:,.0f}")
        else:
            st.error("Database not found")
            
    except Exception as e:
        st.error(f"Database error: {e}")

with tab2:
    st.header("📊 Live Dashboard")
    st.info("Dashboard content here...")

with tab3:
    st.header("🛠️ Debug Information")
    
    st.subheader("Environment")
    st.write("- Streamlit version:", st.__version__)
    st.write("- Python version:", os.sys.version)
    st.write("- Working directory:", os.getcwd())
    st.write("- CHARTS_AVAILABLE:", False)
    
    st.subheader("Session State")
    st.json(dict(st.session_state))
    
    st.subheader("Files Check")
    files_to_check = [
        "streamlit_app.py",
        "stunning_charts_system.py",
        "breadcrumb_navigation.py",
        "data/trench.db"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            st.success(f"✅ {file} exists")
        else:
            st.error(f"❌ {file} missing")

st.markdown("---")
st.caption("Safe mode - If this works, the issue is in the main app code")