#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MINIMAL TEST - Just database connection
"""
import streamlit as st
import sqlite3
import os

st.title("🔍 Database Test ONLY")

# Test database connection
db_path = "data/trench.db"
st.write(f"Testing database at: {db_path}")
st.write(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    st.success("✅ Database file found!")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get coin count
        cursor.execute("SELECT COUNT(*) FROM coins")
        count = cursor.fetchone()[0]
        st.success(f"✅ Database connected! Found {count:,} coins")
        
        # Get sample coins
        cursor.execute("SELECT ticker, smart_wallets, liquidity FROM coins WHERE ticker IS NOT NULL LIMIT 10")
        rows = cursor.fetchall()
        
        st.markdown("### Sample Coins:")
        for ticker, wallets, liquidity in rows:
            st.write(f"🪙 **{ticker}** - Wallets: {wallets or 0} - Liquidity: ${liquidity or 0:,.0f}")
        
        conn.close()
        st.success("🎉 SUCCESS! Database is working on Streamlit Cloud!")
        
    except Exception as e:
        st.error(f"❌ Database error: {e}")
else:
    st.error("❌ Database file not found!")

st.markdown("---")
st.markdown("**If you see coin data above, the database is working and we can build from here.**")