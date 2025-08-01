#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MINIMAL DEBUG - What's actually running on Streamlit Cloud?
"""
import streamlit as st
import sqlite3
import os
from datetime import datetime

st.set_page_config(page_title="DEBUG: What's Actually Running?", layout="wide")

st.title("🔍 STREAMLIT LIVE DEBUG")
st.markdown(f"**Test running at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Test 1: Basic file system
st.markdown("## 1. File System Check")
current_files = os.listdir('.')
st.write("Files in current directory:")
st.code('\n'.join(sorted(current_files)))

# Test 2: Database check
st.markdown("## 2. Database Check")
db_path = "data/trench.db"
db_exists = os.path.exists(db_path)
st.write(f"Database exists at {db_path}: {db_exists}")

if db_exists:
    db_size = os.path.getsize(db_path)
    st.success(f"✅ Database found: {db_size:,} bytes")
    
    # Test direct query
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM coins")
        count = cursor.fetchone()[0]
        st.success(f"✅ Database accessible: {count:,} coins found")
        
        cursor.execute("SELECT ticker FROM coins WHERE ticker IS NOT NULL LIMIT 10")
        sample_tickers = [row[0] for row in cursor.fetchall()]
        st.write("Sample tickers:", sample_tickers)
        conn.close()
        
    except Exception as e:
        st.error(f"❌ Database query failed: {e}")
else:
    st.error("❌ Database not found!")

# Test 3: Import test
st.markdown("## 3. Import Test")
try:
    from streamlit_safe_dashboard import StreamlitSafeDashboard
    st.success("✅ StreamlitSafeDashboard import successful")
    
    try:
        dashboard = StreamlitSafeDashboard()
        st.success("✅ Dashboard creation successful")
    except Exception as e:
        st.error(f"❌ Dashboard creation failed: {e}")
        
except Exception as e:
    st.error(f"❌ Import failed: {e}")

# Test 4: What would normally be shown
st.markdown("## 4. Normal streamlit_app.py Logic Test")
st.info("This is what users should see when streamlit_app.py runs")

# Simple coin display test
if db_exists:
    st.markdown("### Direct Coin Data (Should Work)")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ticker, smart_wallets, liquidity 
            FROM coins 
            WHERE ticker IS NOT NULL 
            LIMIT 5
        """)
        rows = cursor.fetchall()
        conn.close()
        
        for ticker, wallets, liquidity in rows:
            st.write(f"🪙 {ticker} - Wallets: {wallets or 'N/A'} - Liquidity: ${liquidity or 0:,.0f}")
            
    except Exception as e:
        st.error(f"Direct query error: {e}")

# Test 5: Environment info
st.markdown("## 5. Environment Info")
import sys
st.code(f"""
Python version: {sys.version}
Streamlit version: {st.__version__}
Current working directory: {os.getcwd()}
Python path: {sys.path[:3]}...
""")

st.markdown("---")
st.markdown("**If you can see this debug page, then Streamlit is working and we can fix the main app.**")