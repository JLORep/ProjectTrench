#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test if basic Streamlit functionality works"""
import streamlit as st

st.set_page_config(page_title="TrenchCoat Pro Test", layout="wide")

st.title("🚀 TrenchCoat Pro - Test Version")
st.success("✅ App is running!")
st.info("Testing basic functionality before loading full features")

# Test database connection
import os
if os.path.exists("data/trench.db"):
    st.success("✅ Database file exists")
    try:
        import sqlite3
        conn = sqlite3.connect("data/trench.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM coins")
        count = cursor.fetchone()[0]
        st.metric("Total Coins in Database", f"{count:,}")
        conn.close()
    except Exception as e:
        st.error(f"Database error: {e}")
else:
    st.error("❌ Database file not found")

# Test Plotly availability
try:
    import plotly.graph_objects as go
    st.success("✅ Plotly is available")
except ImportError:
    st.warning("⚠️ Plotly not available")

st.info("If you see this, the basic app structure is working. The full app may be taking time to build.")