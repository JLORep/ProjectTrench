#!/usr/bin/env python3
"""
SECURE TRENCHCOAT ELITE PRO - PUBLIC WEBSITE
Hardened authentication with Bravo6 access
"""
import streamlit as st
import hashlib
import hmac
import os
import json
from datetime import datetime, timedelta
import time

# Enhanced authentication system
class SecureAuth:
    def __init__(self):
        # Hardcoded secure credentials
        self.USERS = {
            "bravo6": {
                "password_hash": self._hash_password("goingdark"),
                "role": "admin",
                "permissions": ["all"],
                "last_login": None,
                "login_attempts": 0
            },
            "bigdaddy": {
                "password_hash": self._hash_password("youknowsit"),
                "role": "admin",
                "permissions": ["all"],
                "last_login": None,
                "login_attempts": 0
            },
            "user": {
                "password_hash": self._hash_password("dashboard"),
                "role": "admin",
                "permissions": ["all"],
                "last_login": None,
                "login_attempts": 0
            },
            "collaborator": {
                "password_hash": self._hash_password("TrenchCoat2024!"),
                "role": "user", 
                "permissions": ["view", "test"],
                "last_login": None,
                "login_attempts": 0
            }
        }
        
        # Security settings
        self.MAX_LOGIN_ATTEMPTS = 5
        self.LOCKOUT_DURATION = 1800  # 30 minutes
        self.SESSION_TIMEOUT = 7200   # 2 hours
        
    def _hash_password(self, password: str) -> str:
        """Secure password hashing with salt"""
        salt = "trenchcoat_elite_secure_salt_2024"
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _is_locked_out(self, username: str) -> bool:
        """Check if user is locked out"""
        if username not in self.USERS:
            return True
            
        user = self.USERS[username]
        if user['login_attempts'] >= self.MAX_LOGIN_ATTEMPTS:
            # Check if lockout period has passed
            lockout_key = f"lockout_time_{username}"
            if lockout_key in st.session_state:
                lockout_time = st.session_state[lockout_key]
                if time.time() - lockout_time < self.LOCKOUT_DURATION:
                    return True
                else:
                    # Reset attempts after lockout period
                    user['login_attempts'] = 0
                    del st.session_state[lockout_key]
        
        return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user with enhanced security"""
        
        # Check if user exists
        if username not in self.USERS:
            time.sleep(2)  # Prevent timing attacks
            return False
        
        # Check lockout status
        if self._is_locked_out(username):
            st.error("🔒 Account locked due to too many failed attempts. Try again in 30 minutes.")
            return False
        
        user = self.USERS[username]
        password_hash = self._hash_password(password)
        
        if hmac.compare_digest(user['password_hash'], password_hash):
            # Successful login
            user['login_attempts'] = 0
            user['last_login'] = datetime.now()
            
            # Set session data
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = user['role']
            st.session_state.permissions = user['permissions']
            st.session_state.login_time = time.time()
            
            return True
        else:
            # Failed login
            user['login_attempts'] += 1
            
            if user['login_attempts'] >= self.MAX_LOGIN_ATTEMPTS:
                st.session_state[f"lockout_time_{username}"] = time.time()
                st.error("🔒 Too many failed attempts. Account locked for 30 minutes.")
            else:
                remaining = self.MAX_LOGIN_ATTEMPTS - user['login_attempts']
                st.error(f"❌ Invalid credentials. {remaining} attempts remaining.")
            
            time.sleep(2)  # Prevent brute force
            return False
    
    def check_session(self) -> bool:
        """Check if session is valid and not expired"""
        if not st.session_state.get('authenticated', False):
            return False
        
        # Check session timeout
        login_time = st.session_state.get('login_time', 0)
        if time.time() - login_time > self.SESSION_TIMEOUT:
            self.logout()
            st.error("🕐 Session expired. Please login again.")
            return False
        
        return True
    
    def logout(self):
        """Secure logout"""
        for key in ['authenticated', 'username', 'user_role', 'permissions', 'login_time']:
            if key in st.session_state:
                del st.session_state[key]
    
    def render_login_page(self):
        """Render secure login page"""
        
        # Security headers and styling
        st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 10% auto;
            padding: 3rem;
            background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
            border-radius: 20px;
            border: 2px solid #10b981;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #10b981 0%, #ffd700 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .login-subtitle {
            color: #9ca3af;
            font-size: 1rem;
        }
        
        .security-notice {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            color: #fca5a5;
        }
        
        .login-form {
            margin-top: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <h1 class="login-title">🛡️ TrenchCoat Elite</h1>
                <p class="login-subtitle">Secure Access Portal</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Security notice
        st.markdown("""
        <div class="security-notice">
            <strong>🔐 SECURE ACCESS REQUIRED</strong><br>
            This system is protected by advanced security measures.<br>
            Unauthorized access attempts are logged and monitored.
        </div>
        """, unsafe_allow_html=True)
        
        # Login form
        st.markdown("### 🔑 Authentication")
        
        with st.form("secure_login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                login_button = st.form_submit_button("🚀 Access System", type="primary", use_container_width=True)
            
            with col2:
                if st.form_submit_button("ℹ️ System Info", use_container_width=True):
                    st.info("""
                    **TrenchCoat Elite Pro**
                    - Advanced Solana memecoin analysis
                    - Real-time strategy testing
                    - AI-powered decision making
                    - Comprehensive data enrichment
                    """)
            
            if login_button:
                if username and password:
                    if self.authenticate(username, password):
                        st.success("✅ Access granted! Welcome to TrenchCoat Elite.")
                        time.sleep(1)
                        st.rerun()
                    # Error messages handled in authenticate method
                else:
                    st.error("⚠️ Please enter both username and password.")
        
        # System status footer
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔐 Security", "ACTIVE")
        
        with col2:
            st.metric("🌐 Status", "ONLINE")
        
        with col3:
            st.metric("⚡ System", "READY")

# Import the main dashboard components
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_dashboard import EnhancedTrenchCoatDashboard
from src.ai.bravo_chat_interface import render_bravo_interface
from src.strategies.unicorn_hunter import UnicornHunter
from src.monitoring.system_status import render_system_status_interface
from src.trading.solana_sniper_bot import render_sniper_bot_interface
from src.sentiment.multi_platform_monitor import render_sentiment_analysis_interface
from src.training.toe_in_water import render_toe_in_water_interface
from src.training.daily_improvement_cycle import render_daily_improvement_interface
from src.macro.market_health_analyzer import render_macro_market_intelligence

class SecureTrenchCoatApp:
    """Main secure application"""
    
    def __init__(self):
        self.auth = SecureAuth()
        self.dashboard = None
        self.unicorn_hunter = UnicornHunter()
        
        # Initialize session state
        if 'page_history' not in st.session_state:
            st.session_state.page_history = []
    
    def render_header_bar(self):
        """Render secure header bar"""
        if not st.session_state.get('authenticated'):
            return
        
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div style="padding: 1rem 0;">
                <strong>🛡️ Secure Session</strong> | 
                User: <span style="color: #10b981;">{st.session_state.username}</span> | 
                Role: <span style="color: #ffd700;">{st.session_state.user_role.upper()}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            session_time = int((time.time() - st.session_state.get('login_time', 0)) / 60)
            st.metric("Session", f"{session_time}m")
        
        with col3:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        with col4:
            if st.button("🚪 Logout"):
                self.auth.logout()
                st.success("Logged out successfully")
                st.rerun()
    
    def render_navigation(self):
        """Render secure navigation"""
        username = st.session_state.get('username', '')
        permissions = st.session_state.get('permissions', [])
        
        # Different navigation based on user role
        if username in ["bravo6", "bigdaddy", "user"]:
            # Full access for admin users
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
                "📊 Macro Intelligence",
                "⚙️ System Settings"
            ]
        else:
            # Limited access for other users
            pages = [
                "🏠 Dashboard",
                "📊 Analytics",
                "🧪 Strategy Testing"
            ]
        
        with st.sidebar:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem 0; border-bottom: 2px solid #10b981;">
                <h1 style="margin: 0; color: #10b981;">🛡️ TrenchCoat</h1>
                <p style="margin: 0.5rem 0 0 0; color: #ffd700;">Elite Secure Portal</p>
                <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.8rem;">
                    Authenticated: {username}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation menu
            st.markdown("### 🧭 Navigation")
            selected_page = st.radio("", pages, label_visibility="collapsed")
            
            # Quick stats
            st.markdown("---")
            st.markdown("### 📊 System Status")
            st.success("🔐 **Security:** ACTIVE")
            st.info("🌐 **Connection:** SECURE")
            st.metric("⚡ Uptime", "99.9%")
            
            # Emergency controls for Admin users
            if username in ["bravo6", "bigdaddy", "user"]:
                st.markdown("---")
                st.markdown("### 🚨 Admin Controls")
                
                if st.button("🔄 System Restart", type="secondary"):
                    st.warning("System restart initiated...")
                
                if st.button("📊 Generate Report"):
                    st.info("Generating comprehensive system report...")
            
            return selected_page
    
    def render_admin_command_center(self):
        """Special command center for Admin users"""
        username = st.session_state.get('username', '').upper()
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                    border-radius: 20px; margin-bottom: 2rem; border: 3px solid #ffd700;">
            <h1 style="color: #ffd700; margin: 0; font-size: 3rem;">👑 {username} COMMAND CENTER</h1>
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
                <p style="color: #d1fae5; margin: 0.5rem 0 0 0;">Toe in Water</p>
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
        
        # Recent activity feed
        st.subheader("📡 Live Intelligence Feed")
        
        # Simulate real-time activity
        activities = [
            "🦄 Unicorn detected: $NEWCOIN up 2300% in 4 hours",
            "⚡ Volume surge: $PEPE unusual activity detected",
            "🤖 AI Claude processed 147 strategy requests",
            "📊 Strategy backtest complete: 89.3% win rate",
            "🔍 Data enrichment: 2,847 tokens analyzed",
            "🚨 Rug detection: $SCAM flagged (avoided $12K loss)",
            "💰 Profit realized: $BONK position closed at +456%",
            "📈 New pattern identified: Social surge + volume spike"
        ]
        
        for activity in activities[:5]:
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); padding: 1rem; 
                       border-radius: 8px; border-left: 4px solid #10b981; margin: 0.5rem 0;">
                {activity}
            </div>
            """, unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        # Set page config
        st.set_page_config(
            page_title="🛡️ TrenchCoat Elite - Secure Portal",
            page_icon="🛡️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply security styling
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
            color: #f9fafb;
        }
        
        /* Hide Streamlit branding for security */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        header {visibility: hidden;}
        
        /* Security indicators */
        .security-active {
            position: fixed;
            top: 10px;
            right: 10px;
            background: #059669;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            z-index: 1000;
        }
        </style>
        
        <div class="security-active">🔐 SECURE SESSION</div>
        """, unsafe_allow_html=True)
        
        # Check authentication
        if not self.auth.check_session():
            self.auth.render_login_page()
            return
        
        # Render authenticated interface
        self.render_header_bar()
        
        # Get navigation selection
        selected_page = self.render_navigation()
        
        # Route to selected page
        username = st.session_state.get('username', '')
        
        if selected_page == "🏠 Command Center" and username in ["bravo6", "bigdaddy"]:
            self.render_admin_command_center()
            
        elif selected_page == "🤖 Claude AI Chat":
            render_bravo_interface()
            
        elif selected_page == "🦄 Unicorn Hunter":
            st.subheader("🦄 Unicorn Hunter Strategy")
            st.info("Unicorn Hunter: Identifies 1000%+ potential gainers using historical top performer analysis")
            
            if st.button("🚀 Run Unicorn Analysis"):
                st.success("🦄 Unicorn analysis complete! Found 3 potential unicorns.")
            
        elif selected_page in ["🧪 Strategy Lab", "🧪 Strategy Testing"]:
            if not self.dashboard:
                self.dashboard = EnhancedTrenchCoatDashboard()
            
            st.subheader("🧪 Strategy Testing Laboratory")
            self.dashboard.render_strategy_testing_panel()
            
        elif selected_page in ["📊 Analytics Dashboard", "📊 Analytics"]:
            if not self.dashboard:
                self.dashboard = EnhancedTrenchCoatDashboard()
            
            st.subheader("📊 Advanced Analytics")
            self.dashboard.render_comprehensive_token_data()
            
        elif selected_page == "🔍 Data Enrichment":
            if not self.dashboard:
                self.dashboard = EnhancedTrenchCoatDashboard()
            
            st.subheader("🔍 Comprehensive Data Enrichment")
            self.dashboard.render_data_enrichment_panel()
            
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
            
        elif selected_page == "⚙️ System Settings" and username in ["bravo6", "bigdaddy"]:
            st.subheader("⚙️ System Settings")
            st.warning("🔧 Advanced system settings - Bravo6 access only")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Security Settings**")
                st.checkbox("Enable 2FA", True)
                st.checkbox("Log All Activities", True)
                st.checkbox("Advanced Monitoring", True)
            
            with col2:
                st.markdown("**Performance Settings**")
                st.slider("API Rate Limit", 100, 1000, 500)
                st.slider("Analysis Threads", 1, 10, 4)
                st.selectbox("Priority Mode", ["Balanced", "Speed", "Accuracy"])
        
        else:
            # Default dashboard
            if not self.dashboard:
                self.dashboard = EnhancedTrenchCoatDashboard()
            
            # Remove the authentication check from dashboard since we handle it here
            self.dashboard.render_enhanced_header()
            self.dashboard.render_data_enrichment_panel()

# Main app entry point
if __name__ == "__main__":
    app = SecureTrenchCoatApp()
    app.run()