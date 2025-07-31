#!/usr/bin/env python3
"""
Simple Streamlit App Test
Minimal test to verify Streamlit deployment
"""
import streamlit as st
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="TrenchCoat Test",
    page_icon="🧪",
    layout="wide"
)

# Simple test content
st.title("🧪 TrenchCoat Streamlit Test")
st.success(f"✅ App is working! Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Test database connection
st.header("🔍 Database Test")
try:
    from streamlit_database import streamlit_db
    if streamlit_db:
        coins = streamlit_db.get_all_coins()
        if coins:
            st.success(f"✅ Database connected! Found {len(coins)} coins")
            
            # Show sample data
            import pandas as pd
            df = pd.DataFrame(coins[:10])  # First 10 coins
            st.dataframe(df)
        else:
            st.warning("⚠️ Database connected but no coins found")
    else:
        st.error("❌ Database not available")
except Exception as e:
    st.error(f"❌ Database error: {e}")

# Test imports
st.header("📦 Import Test")
imports_to_test = [
    "streamlit_safe_dashboard",
    "streamlit_database", 
    "unicode_handler"
]

for module in imports_to_test:
    try:
        __import__(module)
        st.success(f"✅ {module} imported successfully")
    except Exception as e:
        st.error(f"❌ {module} failed: {e}")

st.info("🚀 If you see this, the basic Streamlit app is working!")

# Add deployment timestamp
st.text(f"Deployment timestamp: {datetime.now().isoformat()}")