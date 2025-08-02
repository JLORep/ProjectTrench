#!/usr/bin/env python3
"""
Fix streamlit_safe_dashboard.py to use cloud_database
"""

def create_fixed_methods():
    """Create the fixed methods for coin data"""
    
    methods = '''
    def render_top_coins_analysis(self):
        """Render top coins focusing on percentage gains and actual DB columns"""
        st.subheader("🏆 Top Performing Coins")
        
        metric_choice = st.selectbox(
            "Sort by:",
            ["💰 Price Gain %", "🧠 Smart Wallets", "💧 Liquidity", "📊 Peak Volume", "📈 Market Cap"],
            key="coin_metric_sort"
        )
        
        # Try cloud database first
        coins = []
        if cloud_database_available and cloud_db:
            coins = cloud_db.get_all_coins()
        elif database_available and streamlit_db:
            coins = streamlit_db.get_all_coins()
        
        if not coins:
            st.warning("No coin data available - using demo data")
            # Demo data
            coins = [
                {"ticker": "PEPE", "price_gain_pct": 270.1, "smart_wallets": 1250, "liquidity": 2100000, "axiom_mc": 8200000000, "peak_volume": 67800000},
                {"ticker": "SHIB", "price_gain_pct": 152.3, "smart_wallets": 890, "liquidity": 5600000, "axiom_mc": 15100000000, "peak_volume": 89200000},
                {"ticker": "DOGE", "price_gain_pct": 90.5, "smart_wallets": 2100, "liquidity": 12300000, "axiom_mc": 28700000000, "peak_volume": 234500000},
                {"ticker": "FLOKI", "price_gain_pct": 180.1, "smart_wallets": 670, "liquidity": 1800000, "axiom_mc": 3400000000, "peak_volume": 45600000},
                {"ticker": "BONK", "price_gain_pct": 57.0, "smart_wallets": 450, "liquidity": 890000, "axiom_mc": 1200000000, "peak_volume": 23400000}
            ]
        
        try:
            df = pd.DataFrame(coins)
            
            # Sort based on selection
            if metric_choice == "💰 Price Gain %":
                sort_col = 'price_gain_pct'
                df = df.sort_values(sort_col, ascending=False, na_position='last')
            elif metric_choice == "🧠 Smart Wallets":
                sort_col = 'smart_wallets'
                df = df.sort_values(sort_col, ascending=False, na_position='last')
            elif metric_choice == "💧 Liquidity":
                sort_col = 'liquidity'
                df = df.sort_values(sort_col, ascending=False, na_position='last')
            elif metric_choice == "📊 Peak Volume":
                sort_col = 'peak_volume'
                df = df.sort_values(sort_col, ascending=False, na_position='last')
            elif metric_choice == "📈 Market Cap":
                sort_col = 'axiom_mc'
                df = df.sort_values(sort_col, ascending=False, na_position='last')
            
            # Display top 10
            top_coins = df.head(10).copy()
            
            # Format for display
            display_df = pd.DataFrame()
            display_df['🪙 Ticker'] = top_coins['ticker']
            
            if 'price_gain_pct' in top_coins.columns:
                display_df['💰 Gain %'] = top_coins['price_gain_pct'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")
            
            if 'smart_wallets' in top_coins.columns:
                display_df['🧠 Smart Wallets'] = top_coins['smart_wallets'].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else "N/A")
            
            if 'liquidity' in top_coins.columns:
                display_df['💧 Liquidity'] = top_coins['liquidity'].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) and x > 0 else "N/A")
            
            if 'axiom_mc' in top_coins.columns:
                display_df['📈 Market Cap'] = top_coins['axiom_mc'].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) and x > 0 else "N/A")
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
        except Exception as e:
            st.error(f"Error displaying coin data: {e}")
    
    def render_coin_distributions(self):
        """Render distribution charts"""
        st.subheader("📊 Distribution Analysis")
        
        # Get coins data
        coins = []
        if cloud_database_available and cloud_db:
            coins = cloud_db.get_all_coins()
        elif database_available and streamlit_db:
            coins = streamlit_db.get_all_coins()
        
        if not coins:
            st.info("📊 Distribution charts will show when data is available")
            return
        
        try:
            df = pd.DataFrame(coins)
            
            # Price gain distribution
            if 'price_gain_pct' in df.columns:
                st.write("**💰 Price Gain Distribution**")
                fig = px.histogram(df, x='price_gain_pct', nbins=20, 
                                 title="Distribution of Price Gains (%)")
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Smart wallets distribution
            if 'smart_wallets' in df.columns:
                st.write("**🧠 Smart Wallets Distribution**")
                fig = px.histogram(df, x='smart_wallets', nbins=15,
                                 title="Distribution of Smart Wallets")
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error creating distributions: {e}")
    
    def render_searchable_coin_table(self):
        """Render searchable coin table"""
        st.subheader("🔍 Searchable Coin Database")
        
        # Get coins data
        coins = []
        if cloud_database_available and cloud_db:
            coins = cloud_db.get_all_coins()
        elif database_available and streamlit_db:
            coins = streamlit_db.get_all_coins()
        
        if not coins:
            st.info("🔍 Searchable table will populate when data is available")
            return
        
        try:
            df = pd.DataFrame(coins)
            
            # Search filter
            search_term = st.text_input("🔍 Search coins by ticker:", key="coin_search")
            
            if search_term:
                df = df[df['ticker'].str.contains(search_term.upper(), na=False)]
            
            # Show filtered results
            if len(df) > 0:
                st.write(f"**Found {len(df)} coins:**")
                
                # Create display DataFrame
                display_df = pd.DataFrame()
                display_df['🪙 Ticker'] = df['ticker']
                
                if 'price_gain_pct' in df.columns:
                    display_df['💰 Gain %'] = df['price_gain_pct'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")
                
                if 'smart_wallets' in df.columns:
                    display_df['🧠 Smart Wallets'] = df['smart_wallets'].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else "N/A")
                
                if 'liquidity' in df.columns:
                    display_df['💧 Liquidity'] = df['liquidity'].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) and x > 0 else "N/A")
                
                # Limit display to 50 rows for performance
                display_df = display_df.head(50)
                st.dataframe(display_df, use_container_width=True, height=600)
                
                if len(df) > 50:
                    st.info(f"Showing first 50 results out of {len(df)} matches")
            else:
                st.warning("No coins found matching your search")
                
        except Exception as e:
            st.error(f"Error in searchable table: {e}")
    '''
    
    return methods

if __name__ == "__main__":
    print("Fixed methods created. Apply these to streamlit_safe_dashboard.py")
    print(create_fixed_methods())