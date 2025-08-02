#!/usr/bin/env python3
"""
Streamlit Troubleshooting and Optimization
Fix common deployment issues
"""
import streamlit as st
import sys
import os
from pathlib import Path

def check_streamlit_setup():
    """Check Streamlit configuration and dependencies"""
    st.title("🔧 TrenchCoat Pro - Streamlit Diagnostics")
    
    # System info
    st.subheader("📊 System Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Python Version**: {sys.version}")
        st.write(f"**Streamlit Version**: {st.__version__}")
        st.write(f"**Working Directory**: {os.getcwd()}")
    
    with col2:
        st.write(f"**Platform**: {sys.platform}")
        st.write(f"**Environment**: {os.environ.get('ENVIRONMENT', 'Not set')}")
        st.write(f"**Demo Mode**: {os.environ.get('DEMO_MODE', 'Not set')}")
    
    # File checks
    st.subheader("📁 File Verification")
    required_files = [
        "ultra_premium_dashboard.py",
        "premium_components.py",
        "requirements.txt",
        ".streamlit/config.toml"
    ]
    
    for file in required_files:
        if Path(file).exists():
            st.success(f"✅ {file}")
        else:
            st.error(f"❌ {file} - Missing")
    
    # Import checks
    st.subheader("🔗 Import Tests")
    imports_to_test = [
        ("streamlit", "st"),
        ("plotly.graph_objects", "go"),
        ("plotly.express", "px"),
        ("pandas", "pd"),
        ("numpy", "np"),
        ("datetime", "datetime"),
        ("json", "json"),
        ("requests", "requests")
    ]
    
    for module, alias in imports_to_test:
        try:
            __import__(module)
            st.success(f"✅ {module}")
        except ImportError as e:
            st.error(f"❌ {module} - {str(e)}")
    
    # Configuration display
    st.subheader("⚙️ Streamlit Configuration")
    
    # Show current config
    if Path(".streamlit/config.toml").exists():
        st.success("✅ Configuration file found")
        with open(".streamlit/config.toml", "r") as f:
            config_content = f.read()
        st.code(config_content, language="toml")
    else:
        st.error("❌ No configuration file found")
    
    # Memory usage
    st.subheader("💾 Memory Usage")
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        st.write(f"**Memory Usage**: {memory_info.rss / 1024 / 1024:.1f} MB")
        st.write(f"**CPU Usage**: {process.cpu_percent()}%")
    except ImportError:
        st.info("Install psutil for memory monitoring: pip install psutil")

def create_minimal_app():
    """Create minimal working Streamlit app"""
    minimal_app_content = '''import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import random

# Page config
st.set_page_config(
    page_title="TrenchCoat Pro - Minimal",
    page_icon="🎯",
    layout="wide"
)

# Title
st.title("🎯 TrenchCoat Pro - Minimal Version")
st.markdown("**Ultra-Premium Cryptocurrency Trading Dashboard**")

# Simple metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Profit", f"${random.uniform(1000, 5000):.2f}", f"{random.uniform(-50, 200):.2f}")

with col2:
    st.metric("Win Rate", f"{random.uniform(70, 85):.1f}%", f"{random.uniform(-2, 3):.1f}%")

with col3:
    st.metric("Active Trades", random.randint(5, 15), random.randint(-2, 5))

# Simple chart
st.subheader("📈 Performance Chart")
dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
values = np.cumsum(np.random.randn(30) * 10) + 1000

fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', name='Profit'))
fig.update_layout(
    title="Profit Over Time",
    xaxis_title="Date",
    yaxis_title="Profit ($)",
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)

st.success("✅ Minimal version working! This confirms Streamlit setup is correct.")
'''
    
    with open("streamlit_minimal.py", "w") as f:
        f.write(minimal_app_content)
    
    st.success("✅ Created streamlit_minimal.py for testing")

def create_fixed_requirements():
    """Create clean requirements.txt for Streamlit Cloud"""
    requirements_content = """streamlit>=1.47.0
plotly>=6.2.0
pandas>=2.2.1
numpy>=1.26.4
requests>=2.31.0
Pillow>=10.0.0
python-dateutil>=2.8.2
"""
    
    with open("requirements_minimal.txt", "w") as f:
        f.write(requirements_content)
    
    st.success("✅ Created requirements_minimal.txt")

def create_optimized_config():
    """Create optimized Streamlit config"""
    config_content = """[theme]
base = "dark"
primaryColor = "#10b981"
backgroundColor = "#111827"
secondaryBackgroundColor = "#1f2937"
textColor = "#f9fafb"

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
port = 8501

[browser]
gatherUsageStats = false

[client]
toolbarMode = "minimal"
showErrorDetails = true
"""
    
    # Ensure .streamlit directory exists
    Path(".streamlit").mkdir(exist_ok=True)
    
    with open(".streamlit/config.toml", "w") as f:
        f.write(config_content)
    
    st.success("✅ Created optimized .streamlit/config.toml")

def main():
    # Run all diagnostics
    check_streamlit_setup()
    
    st.markdown("---")
    st.subheader("🔧 Quick Fixes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Create Minimal App"):
            create_minimal_app()
    
    with col2:
        if st.button("Fix Requirements"):
            create_fixed_requirements()
    
    with col3:
        if st.button("Optimize Config"):
            create_optimized_config()
    
    st.markdown("---")
    st.subheader("📋 Common Streamlit Cloud Issues & Solutions")
    
    st.markdown("""
    **1. Import Errors:**
    - Check requirements.txt has all dependencies
    - Use exact version numbers: `streamlit>=1.47.0`
    
    **2. File Not Found:**
    - Ensure all files are in repository root
    - Check file paths are relative, not absolute
    
    **3. Memory Issues:**
    - Reduce data processing in @st.cache_data functions
    - Use st.session_state for large objects
    
    **4. Configuration Issues:**
    - Check .streamlit/config.toml is properly formatted
    - Ensure no conflicting settings
    
    **5. Runtime Errors:**
    - Test locally first: `streamlit run streamlit_app.py`
    - Check Streamlit Cloud logs for specific errors
    """)
    
    st.info("💡 **Tip**: Test with streamlit_minimal.py first to verify basic setup works!")

if __name__ == "__main__":
    main()