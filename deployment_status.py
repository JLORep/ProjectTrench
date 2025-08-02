#!/usr/bin/env python3
"""
🚀 TrenchCoat Pro - Deployment Status Dashboard
Simple monitoring for deployment health
"""

import streamlit as st
import requests
import json
import subprocess
from datetime import datetime
import pandas as pd

def check_app_status():
    """Check if the app is accessible"""
    try:
        response = requests.get("https://trenchdemo.streamlit.app", timeout=10)
        return response.status_code == 200, response.elapsed.total_seconds()
    except:
        return False, 0

def get_git_info():
    """Get current git information"""
    try:
        # Current branch
        branch = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True).stdout.strip()
        
        # Last commit
        commit = subprocess.run(['git', 'log', '-1', '--pretty=%H'], 
                              capture_output=True, text=True).stdout.strip()[:8]
        
        # Last commit message
        message = subprocess.run(['git', 'log', '-1', '--pretty=%s'], 
                               capture_output=True, text=True).stdout.strip()
        
        # Last commit time
        commit_time = subprocess.run(['git', 'log', '-1', '--pretty=%cd', '--date=relative'], 
                                   capture_output=True, text=True).stdout.strip()
        
        return {
            'branch': branch,
            'commit': commit,
            'message': message,
            'time': commit_time
        }
    except:
        return None

def main():
    st.set_page_config(page_title="Deployment Status", page_icon="🚀", layout="wide")
    
    st.title("🚀 TrenchCoat Pro - Deployment Status")
    
    # Check app status
    is_healthy, response_time = check_app_status()
    
    # Status display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if is_healthy:
            st.metric("App Status", "✅ Online", delta=f"{response_time:.2f}s")
        else:
            st.metric("App Status", "❌ Offline", delta="Check required")
    
    with col2:
        st.metric("Environment", "Production", delta="Streamlit Cloud")
    
    with col3:
        st.metric("URL", "trenchdemo.streamlit.app")
    
    with col4:
        st.metric("Last Check", datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")
    
    # Git information
    git_info = get_git_info()
    if git_info:
        st.subheader("📊 Repository Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Branch:** `{git_info['branch']}`")
            st.markdown(f"**Last Commit:** `{git_info['commit']}`")
        
        with col2:
            st.markdown(f"**Commit Message:** {git_info['message']}")
            st.markdown(f"**Committed:** {git_info['time']}")
    
    st.markdown("---")
    
    # Deployment checklist
    st.subheader("✅ Deployment Checklist")
    
    checks = {
        "Main file exists": os.path.exists("streamlit_app.py"),
        "Database exists": os.path.exists("data/trench.db"),
        "Requirements file exists": os.path.exists("requirements.txt"),
        "GitHub workflow exists": os.path.exists(".github/workflows/deploy.yml"),
        "Deployment script exists": os.path.exists("deploy.py")
    }
    
    for check, status in checks.items():
        if status:
            st.success(f"✅ {check}")
        else:
            st.error(f"❌ {check}")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Deploy Now", type="primary"):
            st.info("Run `python deploy.py` in terminal")
    
    with col2:
        if st.button("🔍 Check Logs"):
            st.info("Visit https://share.streamlit.io")
    
    with col3:
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    # Auto-refresh
    st.caption("Auto-refreshes every 30 seconds")
    time.sleep(30)
    st.rerun()

if __name__ == "__main__":
    import os
    import time
    main()