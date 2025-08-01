#!/usr/bin/env python3
"""
Minimal Streamlit Test - Absolute simplest possible app
"""
import streamlit as st
from datetime import datetime

st.title("🎯 TrenchCoat Pro - LIVE TEST")
st.success(f"✅ App is working! Time: {datetime.now()}")
st.write("If you see this, the Streamlit app is deployed successfully!")

# Add timestamp for cache busting
st.text(f"Deployment: {datetime.now().isoformat()}")