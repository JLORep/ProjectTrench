#!/usr/bin/env python3
"""Properly fix Hunt Hub by rewriting the broken sections"""

# Read the current file
with open('memecoin_hunt_hub_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where the CSS ends and replace everything after with properly indented content
css_end = content.find('    """, unsafe_allow_html=True)')
if css_end == -1:
    print("❌ Could not find CSS end marker")
    exit(1)

# Keep everything up to and including the CSS end
before_css_end = content[:css_end + len('    """, unsafe_allow_html=True)')]

# Add the properly indented rest of the function
fixed_content = before_css_end + '''
        
        st.header("🎯 Hunt Hub - Memecoin Sniper Command Center")
        
        # Top metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🔍 Active Scans", "3,847", delta="+142/min", help="Tokens scanned per minute")
        
        with col2:
            st.metric("🎯 High Score", "12", delta="+3", help="Tokens with score >75")
        
        with col3:
            st.metric("⚡ Avg Latency", "0.3s", delta="-0.1s", help="Detection speed")
        
        with col4:
            st.metric("💰 24h Profits", "$8,342", delta="+42.3%", help="Total profits from snipes")
        
        with col5:
            st.metric("🏆 Win Rate", "73.2%", delta="+5.1%", help="Successful snipes")
        
        st.markdown("---")
        
        # Main content area with tabs
        hunt_tab1, hunt_tab2, hunt_tab3, hunt_tab4 = st.tabs([
            "🔍 Live Scanner", "📡 Alpha Radar", "📊 Performance", "⚙️ Settings"
        ])
        
        with hunt_tab1:
            render_live_scanner()
        
        with hunt_tab2:
            render_alpha_radar()
        
        with hunt_tab3:
            render_performance_tracker()
        
        with hunt_tab4:
            render_hunt_settings()
            
    except Exception as e:
        st.error(f"Hunt Hub Error: {e}")
        import traceback
        st.text(traceback.format_exc())
        
        # Fallback basic interface
        st.header("🎯 Hunt Hub - Memecoin Scanner")
        st.info("Hunt Hub is temporarily unavailable. Using fallback interface.")
        
        # Basic metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Scans", "1,234", delta="+56")
        with col2:
            st.metric("High Score Tokens", "8", delta="+2")
        with col3:
            st.metric("Avg Response", "0.4s", delta="-0.1s")

def render_live_scanner():
    """Render the live token scanner interface"""
    
    # Scanner controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        platforms = st.multiselect(
            "🌐 Platforms",
            ["Pump.fun", "Raydium", "Jupiter", "Meteora"],
            default=["Pump.fun", "Raydium"],
            help="Select platforms to scan"
        )
    
    with col2:
        filters = st.multiselect(
            "🔧 Filters",
            ["Score > 70", "Liquidity > $5k", "No Honeypot", "Burned LP", "KOL Mentions"],
            default=["Score > 70", "No Honeypot"],
            help="Apply smart filters"
        )
    
    with col3:
        auto_snipe = st.toggle("🎯 Auto-Snipe", help="Automatically buy high-score tokens")
    
    st.markdown('<div class="hunt-container">', unsafe_allow_html=True)
    st.markdown('<div class="scanner-line"></div>', unsafe_allow_html=True)
    
    st.subheader("🚀 Launch Queue")
    
    # Simulated token launches
    tokens = [
        {
            "symbol": "PEPE2.0",
            "name": "Pepe 2.0", 
            "address": "EPjF...3n2",
            "score": 87,
            "liquidity": "$12,450",
            "mcap": "$45,230",
            "volume": "$8,342",
            "holders": 142,
            "launch_time": "2 mins ago",
            "platform": "Pump.fun",
            "risk": "low",
            "rationale": "🔥 High social momentum | Strong liquidity foundation | KOL backing"
        },
        {
            "symbol": "MOONCAT",
            "name": "Moon Cat",
            "address": "MCT7...p4v", 
            "score": 92,
            "liquidity": "$25,000",
            "mcap": "$78,400",
            "volume": "$15,200", 
            "holders": 234,
            "launch_time": "30 secs ago",
            "platform": "Pump.fun",
            "risk": "low",
            "rationale": "🎯 All-around strong fundamentals | Undervalued with strong liquidity"
        }
    ]
    
    # Display token cards
    for token in tokens:
        render_token_card(token)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Launch heatmap
    st.subheader("🔥 Launch Heatmap")
    render_launch_heatmap()

def render_alpha_radar():
    """Render alpha radar signals"""
    st.info("📡 Alpha Radar signals coming soon...")

def render_performance_tracker():
    """Render performance tracking"""
    st.info("📊 Performance tracking coming soon...")

def render_hunt_settings():
    """Render hunt settings"""
    st.info("⚙️ Hunt settings coming soon...")
'''

# Find the existing render_token_card function and keep everything from there
token_card_start = content.find('def render_token_card(token: Dict):')
if token_card_start != -1:
    # Keep the token card function and everything after it
    remaining_content = content[token_card_start:]
    fixed_content += '\n' + remaining_content

# Write the fixed file
with open('memecoin_hunt_hub_ui.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✅ Fixed Hunt Hub properly")