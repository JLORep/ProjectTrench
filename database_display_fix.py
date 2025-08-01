"""
Database Display Fix - Show actual data from trench.db with proper handling
"""
import sqlite3
import streamlit as st
from datetime import datetime
import hashlib

def get_actual_db_columns():
    """Get the actual columns from trench.db"""
    return [
        'ticker', 'ca', 'discovery_time', 'discovery_price', 
        'discovery_mc', 'liquidity', 'peak_volume', 'smart_wallets',
        'dex_paid', 'sol_price', 'history', 'axiom_price', 
        'axiom_mc', 'axiom_volume'
    ]

def calculate_price_gain(discovery_price, current_price):
    """Calculate percentage gain from discovery to current price"""
    if discovery_price and current_price and discovery_price > 0:
        return ((current_price - discovery_price) / discovery_price) * 100
    return 0

def format_value(value, value_type="default"):
    """Format values for display based on type"""
    if value is None or value == 0:
        return "N/A"
    
    if value_type == "price":
        if value < 0.001:
            return f"${value:.8f}"
        elif value < 1:
            return f"${value:.6f}"
        else:
            return f"${value:,.2f}"
    elif value_type == "mc" or value_type == "volume" or value_type == "liquidity":
        if value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value/1_000:.1f}K"
        else:
            return f"${value:,.0f}"
    elif value_type == "wallets":
        return f"{int(value):,}"
    else:
        return str(value)

def get_coins_with_actual_data(limit=20, offset=0, search="", sort_by="discovery_time", order="DESC"):
    """Get coins from database showing actual available data"""
    try:
        conn = sqlite3.connect("data/trench.db")
        cursor = conn.cursor()
        
        # Build query with search
        where_clause = ""
        if search:
            where_clause = f"WHERE ticker LIKE '%{search}%' OR ca LIKE '%{search}%'"
        
        # Map sort options to actual columns
        sort_map = {
            "gain": "CASE WHEN discovery_price > 0 AND axiom_price > 0 THEN ((axiom_price - discovery_price) / discovery_price) * 100 ELSE 0 END",
            "ticker": "ticker",
            "wallets": "smart_wallets",
            "liquidity": "liquidity",
            "mc": "axiom_mc",
            "volume": "axiom_volume",
            "discovery_time": "discovery_time"
        }
        
        sort_column = sort_map.get(sort_by, "discovery_time")
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM coins {where_clause}"
        cursor.execute(count_query)
        total_count = cursor.fetchone()[0]
        
        # Get paginated data
        query = f"""
            SELECT ticker, ca, discovery_time, discovery_price, discovery_mc,
                   liquidity, peak_volume, smart_wallets, dex_paid, sol_price,
                   history, axiom_price, axiom_mc, axiom_volume
            FROM coins
            {where_clause}
            ORDER BY {sort_column} {order}
            LIMIT {limit} OFFSET {offset}
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        coins = []
        for row in rows:
            ticker = row[0]
            ca = row[1]
            discovery_time = row[2]
            discovery_price = row[3]
            discovery_mc = row[4]
            liquidity = row[5]
            peak_volume = row[6]
            smart_wallets = row[7]
            dex_paid = row[8]
            sol_price = row[9]
            history = row[10]
            axiom_price = row[11]
            axiom_mc = row[12]
            axiom_volume = row[13]
            
            # Calculate price gain
            price_gain = calculate_price_gain(discovery_price, axiom_price)
            
            # Analyze data completeness
            fields = {
                "Ticker": ticker,
                "Contract Address": ca,
                "Discovery Time": discovery_time,
                "Discovery Price": discovery_price,
                "Current Price": axiom_price,
                "Price Gain": price_gain if price_gain > 0 else None,
                "Discovery MC": discovery_mc,
                "Current MC": axiom_mc,
                "Liquidity": liquidity,
                "Volume": axiom_volume,
                "Peak Volume": peak_volume,
                "Smart Wallets": smart_wallets,
                "DEX Paid": dex_paid,
                "SOL Price": sol_price
            }
            
            available = [k for k, v in fields.items() if v is not None and v != 0]
            missing = [k for k, v in fields.items() if v is None or v == 0]
            completeness = (len(available) / len(fields)) * 100
            
            coins.append({
                'ticker': ticker,
                'contract_address': ca,
                'discovery_time': discovery_time,
                'discovery_price': discovery_price,
                'current_price': axiom_price,
                'price_gain': price_gain,
                'discovery_mc': discovery_mc,
                'market_cap': axiom_mc,
                'liquidity': liquidity,
                'volume': axiom_volume,
                'peak_volume': peak_volume,
                'smart_wallets': smart_wallets,
                'dex_paid': dex_paid,
                'sol_price': sol_price,
                'history': history,
                'available_fields': available,
                'missing_fields': missing,
                'completeness_score': completeness
            })
        
        return coins, total_count, "SUCCESS"
        
    except Exception as e:
        return [], 0, f"Database error: {str(e)}"

def render_actual_coin_card(coin):
    """Render coin card showing actual available data"""
    ticker = coin['ticker']
    gain = coin['price_gain']
    completeness = coin['completeness_score']
    
    # Performance-based styling
    if gain > 500:
        bg_color = "#10b981"
        status = "🚀 MOONSHOT"
    elif gain > 200:
        bg_color = "#3b82f6"
        status = "📈 STRONG"
    elif gain > 50:
        bg_color = "#8b5cf6"
        status = "💎 SOLID"
    elif gain > 0:
        bg_color = "#6b7280"
        status = "⚡ ACTIVE"
    else:
        bg_color = "#ef4444"
        status = "📊 DATA"
    
    # Create card content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {ticker}")
        if coin['contract_address']:
            st.caption(f"CA: {coin['contract_address'][:20]}...")
    
    with col2:
        if gain > 0:
            st.metric("Gain", f"+{gain:.1f}%", status)
        else:
            st.metric("Status", status)
    
    # Display available data in grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Liquidity", format_value(coin['liquidity'], 'liquidity'))
    
    with col2:
        st.metric("📊 Market Cap", format_value(coin['market_cap'], 'mc'))
    
    with col3:
        st.metric("📈 Volume", format_value(coin['volume'], 'volume'))
    
    with col4:
        st.metric("👥 Wallets", format_value(coin['smart_wallets'], 'wallets'))
    
    # Price information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔍 Discovery Price", format_value(coin['discovery_price'], 'price'))
    
    with col2:
        st.metric("💵 Current Price", format_value(coin['current_price'], 'price'))
    
    with col3:
        st.metric("⏰ Discovery", coin['discovery_time'] if coin['discovery_time'] else "N/A")
    
    # Data completeness
    st.progress(completeness / 100)
    st.caption(f"Data Completeness: {completeness:.0f}% ({len(coin['available_fields'])} of {len(coin['available_fields']) + len(coin['missing_fields'])} fields)")
    
    # Show missing fields
    if coin['missing_fields']:
        with st.expander("🔍 Missing Data Fields"):
            st.write(", ".join(coin['missing_fields']))
    
    st.divider()

def render_enhanced_coin_data_tab():
    """Enhanced coin data tab showing actual database information"""
    st.header("🗄️ Live Coin Database")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    # Get database stats
    try:
        conn = sqlite3.connect("data/trench.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM coins")
        total_coins = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM coins WHERE axiom_price > 0 AND discovery_price > 0")
        coins_with_prices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM coins WHERE liquidity > 0")
        coins_with_liquidity = cursor.fetchone()[0]
        
        conn.close()
        
        with col1:
            st.metric("Total Coins", f"{total_coins:,}")
        
        with col2:
            st.metric("With Price Data", f"{coins_with_prices:,}")
        
        with col3:
            st.metric("With Liquidity", f"{coins_with_liquidity:,}")
    
    except Exception as e:
        st.error(f"Database stats error: {e}")
    
    # Search and filters
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search = st.text_input("🔍 Search by ticker or contract", "")
    
    with col2:
        sort_by = st.selectbox("Sort by", ["discovery_time", "gain", "liquidity", "mc", "volume", "wallets"])
    
    with col3:
        order = st.selectbox("Order", ["DESC", "ASC"])
    
    # Pagination
    page = st.number_input("Page", min_value=1, value=1)
    limit = st.selectbox("Items per page", [10, 20, 50], index=1)
    offset = (page - 1) * limit
    
    # Get and display coins
    coins, total, status = get_coins_with_actual_data(limit, offset, search, sort_by, order)
    
    if status == "SUCCESS":
        st.info(f"Showing {len(coins)} coins (page {page} of {(total + limit - 1) // limit})")
        
        for coin in coins:
            render_actual_coin_card(coin)
    else:
        st.error(status)

# Example usage in streamlit_app.py
if __name__ == "__main__":
    st.set_page_config(page_title="Database Display Fix", layout="wide")
    st.title("TrenchCoat Pro - Actual Database Display")
    render_enhanced_coin_data_tab()