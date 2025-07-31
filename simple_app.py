import streamlit as st
import pandas as pd
import numpy as np

# Configure page
st.set_page_config(
    page_title="TrenchCoat Pro Demo",
    page_icon="🎯",
    layout="wide"
)

# Title
st.title("🎯 TrenchCoat Pro")
st.subheader("AI-Powered Cryptocurrency Trading Platform")

# Status
st.success("✅ System Operational - Demo Mode")

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Runners Detected", "27", "+5")

with col2:
    st.metric("Win Rate", "87.3%", "+2.1%")

with col3:
    st.metric("Active Trades", "4", "+1")

with col4:
    st.metric("Total P&L", "$3,456", "+$567")

# Sample data
st.subheader("Recent Signals")

# Create sample data
data = {
    'Symbol': ['PEPE', 'BONK', 'WIF', 'MYRO', 'JUP'],
    'Price': ['$0.000012', '$0.000034', '$1.23', '$0.45', '$0.89'],
    'Change 24h': ['+67.5%', '+45.3%', '+38.9%', '+31.2%', '+28.7%'],
    'Confidence': ['92.3%', '87.5%', '85.1%', '81.2%', '79.8%'],
    'Status': ['🟢 Active', '🟢 Active', '🟡 Watch', '🟡 Watch', '🔴 Closed']
}

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

# Chart
st.subheader("Portfolio Performance")

# Generate sample data
dates = pd.date_range('2025-01-01', periods=30, freq='D')
values = np.random.randn(30).cumsum() + 10000

chart_data = pd.DataFrame({
    'Date': dates,
    'Portfolio Value': values
})

st.line_chart(chart_data.set_index('Date'))

# Footer
st.info("🚀 Live Demo: https://trenchdemo.streamlit.app | Full TrenchCoat Pro at trenchcoat.pro")

st.markdown("---")
st.markdown("© 2025 TrenchCoat Pro | Professional Trading Intelligence")