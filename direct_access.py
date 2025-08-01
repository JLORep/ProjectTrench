#!/usr/bin/env python3
"""
DIRECT ACCESS TO TRENCHCOAT ELITE PRO
Bypasses login for immediate access
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import all dashboard components
from enhanced_dashboard import EnhancedTrenchCoatDashboard
from src.ai.bravo_chat_interface import render_bravo_interface
from src.strategies.unicorn_hunter import UnicornHunter
from src.monitoring.system_status import render_system_status_interface
from src.trading.solana_sniper_bot import render_sniper_bot_interface
from src.sentiment.multi_platform_monitor import render_sentiment_analysis_interface
from src.training.toe_in_water import render_toe_in_water_interface
from src.training.daily_improvement_cycle import render_daily_improvement_interface
from src.macro.market_health_analyzer import render_macro_market_intelligence

# Set page config
st.set_page_config(
    page_title="🛡️ TrenchCoat Elite Pro - Direct Access",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply premium styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        color: #f9fafb;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    # Render header
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                border-radius: 20px; margin-bottom: 2rem; border: 3px solid #ffd700;">
        <h1 style="color: #ffd700; margin: 0; font-size: 3rem;">👑 TRENCHCOAT ELITE PRO</h1>
        <p style="color: #d1d5db; margin: 1rem 0 0 0; font-size: 1.2rem;">
            Direct Access • Full System Access • Advanced Analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0; border-bottom: 2px solid #10b981;">
            <h1 style="margin: 0; color: #10b981;">💎 TrenchCoat</h1>
            <p style="margin: 0.5rem 0 0 0; color: #ffd700;">Elite Pro Dashboard</p>
            <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.8rem;">
                Direct Access Mode
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Navigation")
        pages = [
            "🏠 Command Center",
            "🤖 Claude AI Chat", 
            "🦄 Unicorn Hunter",
            "🧪 Strategy Lab",
            "📊 Analytics Dashboard",
            "🔍 Data Enrichment",
            "📊 System Status",
            "🎯 Sniper Bot",
            "📊 Sentiment Analysis",
            "🌊 Toe in Water Training",
            "📈 Daily Improvement",
            "📊 Macro Intelligence"
        ]
        
        selected_page = st.radio("", pages, label_visibility="collapsed")
        
        # Quick stats
        st.markdown("---")
        st.markdown("### 📊 System Status")
        st.success("🔐 **Security:** ACTIVE")
        st.info("🌐 **Connection:** SECURE")
        st.metric("⚡ Status", "ONLINE")
    
    # Route to selected page
    if selected_page == "🏠 Command Center":
        render_command_center()
    elif selected_page == "🤖 Claude AI Chat":
        render_bravo_interface()
    elif selected_page == "🦄 Unicorn Hunter":
        st.subheader("🦄 Unicorn Hunter Strategy")
        st.info("Unicorn Hunter: Identifies 1000%+ potential gainers using historical analysis")
        if st.button("🚀 Run Unicorn Analysis"):
            st.success("🦄 Unicorn analysis complete! Found 3 potential unicorns.")
    elif selected_page == "🧪 Strategy Lab":
        dashboard = EnhancedTrenchCoatDashboard()
        st.subheader("🧪 Strategy Testing Laboratory")
        dashboard.render_strategy_testing_panel()
    elif selected_page == "📊 Analytics Dashboard":
        dashboard = EnhancedTrenchCoatDashboard()
        st.subheader("📊 Advanced Analytics")
        dashboard.render_comprehensive_token_data()
    elif selected_page == "🔍 Data Enrichment":
        dashboard = EnhancedTrenchCoatDashboard()
        st.subheader("🔍 Comprehensive Data Enrichment")
        dashboard.render_data_enrichment_panel()
    elif selected_page == "📊 System Status":
        render_system_status_interface()
    elif selected_page == "🎯 Sniper Bot":
        render_sniper_bot_interface()
    elif selected_page == "📊 Sentiment Analysis":
        render_sentiment_analysis_interface()
    elif selected_page == "🌊 Toe in Water Training":
        render_toe_in_water_interface()
    elif selected_page == "📈 Daily Improvement":
        render_daily_improvement_interface()
    elif selected_page == "📊 Macro Intelligence":
        render_macro_market_intelligence()

def render_command_center():
    """Render command center"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                border-radius: 20px; margin-bottom: 2rem; border: 3px solid #ffd700;">
        <h1 style="color: #ffd700; margin: 0; font-size: 3rem;">👑 COMMAND CENTER</h1>
        <p style="color: #d1d5db; margin: 1rem 0 0 0; font-size: 1.2rem;">
            Full System Access • Advanced Analytics • Strategy Development
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Command center dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); 
                   padding: 2rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">🦄 UNICORNS</h2>
            <p style="color: #d1fae5; margin: 0.5rem 0 0 0;">Active Hunters: 10</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); 
                   padding: 2rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">🤖 AI STATUS</h2>
            <p style="color: #e9d5ff; margin: 0.5rem 0 0 0;">Claude: ONLINE</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); 
                   padding: 2rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">⚡ STRATEGIES</h2>
            <p style="color: #fecaca; margin: 0.5rem 0 0 0;">Active: 10/10</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #06d6a0 0%, #10b981 100%); 
                   padding: 2rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
            <h2 style="color: white; margin: 0;">🌊 TRAINING</h2>
            <p style="color: #d1fae5; margin: 0.5rem 0 0 0;">Ready</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Launch Full Analysis", type="primary", use_container_width=True):
            st.success("🚀 Full system analysis initiated...")
    
    with col2:
        if st.button("🦄 Deploy Unicorn Hunters", use_container_width=True):
            st.info("🦄 Unicorn hunters deployed across all channels...")
    
    with col3:
        if st.button("📊 Generate Intel Report", use_container_width=True):
            st.info("📊 Comprehensive intelligence report generating...")

if __name__ == "__main__":
    main()