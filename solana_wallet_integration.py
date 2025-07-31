#!/usr/bin/env python3
"""
Solana Wallet Integration for Real Portfolio Tracking
"""
import streamlit as st
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

class SolanaWalletTracker:
    """Real Solana wallet portfolio tracking"""
    
    def __init__(self):
        self.rpc_endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana"
        ]
        self.current_rpc = 0
        
    def get_rpc_endpoint(self) -> str:
        """Get current RPC endpoint with fallback"""
        return self.rpc_endpoints[self.current_rpc % len(self.rpc_endpoints)]
    
    def validate_wallet_address(self, address: str) -> bool:
        """Validate Solana wallet address format"""
        if not address or len(address) < 32 or len(address) > 44:
            return False
        
        # Basic base58 validation
        try:
            import base58
            decoded = base58.b58decode(address)
            return len(decoded) == 32
        except:
            # Fallback validation - check if it looks like a Solana address
            valid_chars = set('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
            return all(c in valid_chars for c in address) and 32 <= len(address) <= 44
    
    def get_wallet_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Get SOL balance for wallet"""
        try:
            rpc_url = self.get_rpc_endpoint()
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet_address]
            }
            
            response = requests.post(rpc_url, json=payload, timeout=10)
            data = response.json()
            
            if 'result' in data:
                lamports = data['result']['value']
                sol_balance = lamports / 1_000_000_000  # Convert lamports to SOL
                
                return {
                    'success': True,
                    'balance_sol': sol_balance,
                    'balance_lamports': lamports,
                    'wallet_address': wallet_address,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Invalid response format'}
                
        except Exception as e:
            # Try next RPC endpoint
            self.current_rpc += 1
            if self.current_rpc < len(self.rpc_endpoints):
                return self.get_wallet_balance(wallet_address)
            
            return {'success': False, 'error': str(e)}
    
    def get_token_accounts(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Get SPL token accounts for wallet"""
        try:
            rpc_url = self.get_rpc_endpoint()
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet_address,
                    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                    {"encoding": "jsonParsed"}
                ]
            }
            
            response = requests.post(rpc_url, json=payload, timeout=15)
            data = response.json()
            
            tokens = []
            
            if 'result' in data and 'value' in data['result']:
                for account in data['result']['value']:
                    try:
                        parsed_info = account['account']['data']['parsed']['info']
                        token_amount = parsed_info['tokenAmount']
                        
                        if float(token_amount['uiAmount'] or 0) > 0:
                            tokens.append({
                                'mint': parsed_info['mint'],
                                'balance': float(token_amount['uiAmount']),
                                'decimals': token_amount['decimals'],
                                'account': account['pubkey']
                            })
                    except (KeyError, ValueError):
                        continue
            
            return tokens
            
        except Exception as e:
            return []
    
    def get_token_metadata(self, mint_address: str) -> Dict[str, Any]:
        """Get token metadata (symbol, name, etc.)"""
        try:
            # Using Jupiter API for token info
            url = f"https://token.jup.ag/strict"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                tokens = response.json()
                for token in tokens:
                    if token.get('address') == mint_address:
                        return {
                            'symbol': token.get('symbol', 'UNKNOWN'),
                            'name': token.get('name', 'Unknown Token'),
                            'decimals': token.get('decimals', 9),
                            'logoURI': token.get('logoURI', '')
                        }
            
            return {
                'symbol': mint_address[:8] + '...',
                'name': 'Unknown Token',
                'decimals': 9,
                'logoURI': ''
            }
            
        except Exception:
            return {
                'symbol': 'UNKNOWN',
                'name': 'Unknown Token',
                'decimals': 9,
                'logoURI': ''
            }
    
    def get_full_portfolio(self, wallet_address: str) -> Dict[str, Any]:
        """Get complete portfolio including SOL and SPL tokens"""
        
        # Get SOL balance
        sol_data = self.get_wallet_balance(wallet_address)
        
        # Get token accounts
        tokens = self.get_token_accounts(wallet_address)
        
        # Enrich token data with metadata
        enriched_tokens = []
        for token in tokens:
            metadata = self.get_token_metadata(token['mint'])
            token.update(metadata)
            enriched_tokens.append(token)
        
        portfolio = {
            'wallet_address': wallet_address,
            'timestamp': datetime.now().isoformat(),
            'sol_balance': sol_data.get('balance_sol', 0) if sol_data.get('success') else 0,
            'tokens': enriched_tokens,
            'total_tokens': len(enriched_tokens),
            'success': sol_data.get('success', False)
        }
        
        return portfolio

# Streamlit integration
def render_solana_wallet_section():
    """Render Solana wallet integration in Streamlit"""
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                background: linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(103, 58, 183, 0.1) 100%);
                border-radius: 15px; border: 1px solid rgba(156, 39, 176, 0.3);'>
        <h1 style='color: #9c27b0; margin: 0; font-size: 2.5rem; font-weight: 700;'>
            💎 Solana Wallet Tracker
        </h1>
        <p style='color: #a3a3a3; margin-top: 0.5rem; font-size: 1.2rem;'>
            Connect Your Wallet for Real Portfolio Tracking
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'wallet_address' not in st.session_state:
        st.session_state.wallet_address = ""
    if 'portfolio_data' not in st.session_state:
        st.session_state.portfolio_data = None
    
    # Wallet input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        wallet_input = st.text_input(
            "🔑 Enter Your Solana Wallet Address:",
            value=st.session_state.wallet_address,
            placeholder="e.g., 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
            help="Your wallet address will be used to fetch real-time portfolio data from Solana blockchain"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Space for alignment
        track_portfolio = st.button("📊 Track Portfolio", type="primary", use_container_width=True)
    
    # Validate and fetch portfolio
    if track_portfolio and wallet_input:
        tracker = SolanaWalletTracker()
        
        if tracker.validate_wallet_address(wallet_input):
            st.session_state.wallet_address = wallet_input
            
            with st.spinner("🔍 Fetching your portfolio from Solana blockchain..."):
                portfolio = tracker.get_full_portfolio(wallet_input)
                st.session_state.portfolio_data = portfolio
            
            if portfolio['success']:
                st.success(f"✅ Connected to wallet: {wallet_input[:8]}...{wallet_input[-8:]}")
            else:
                st.error("❌ Failed to fetch portfolio. Please check your wallet address and try again.")
        else:
            st.error("❌ Invalid Solana wallet address format")
    
    # Display portfolio if available
    if st.session_state.portfolio_data and st.session_state.portfolio_data['success']:
        portfolio = st.session_state.portfolio_data
        
        st.markdown("---")
        st.subheader("💰 Your Real Portfolio")
        
        # SOL balance
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💎 SOL Balance", 
                f"{portfolio['sol_balance']:.4f} SOL",
                help="Native SOL balance in your wallet"
            )
        
        with col2:
            st.metric(
                "🪙 Token Types", 
                f"{portfolio['total_tokens']} tokens",
                help="Number of different SPL tokens in your wallet"
            )
        
        with col3:
            st.metric(
                "🔄 Last Updated", 
                datetime.fromisoformat(portfolio['timestamp']).strftime("%H:%M:%S"),
                help="When this data was last fetched"
            )
        
        # Token holdings table
        if portfolio['tokens']:
            st.subheader("🏆 Token Holdings")
            
            # Create DataFrame
            token_data = []
            for token in portfolio['tokens']:
                token_data.append({
                    'Symbol': token['symbol'],
                    'Name': token['name'],
                    'Balance': f"{token['balance']:,.6f}",
                    'Mint Address': token['mint'][:8] + '...' + token['mint'][-8:],
                    'Decimals': token['decimals']
                })
            
            df = pd.DataFrame(token_data)
            st.dataframe(df, use_container_width=True)
            
            # Show full mint addresses in expander
            with st.expander("🔍 Full Token Details"):
                for i, token in enumerate(portfolio['tokens']):
                    st.code(f"{token['symbol']}: {token['mint']}")
        
        # Refresh button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Refresh Portfolio", use_container_width=True):
                st.rerun()
    
    # Instructions for new users
    if not st.session_state.portfolio_data:
        st.markdown("---")
        st.info("""
        **📚 How to use:**
        1. Enter your Solana wallet address above
        2. Click "Track Portfolio" to fetch real-time data
        3. View your SOL balance and all SPL tokens
        4. Refresh anytime to get updated balances
        
        **🔒 Privacy:** Your wallet address is only used to fetch public blockchain data. No private keys or sensitive information is stored.
        """)

# For integration with main dashboard
def get_wallet_portfolio_summary(wallet_address: str) -> Dict[str, Any]:
    """Get wallet portfolio summary for dashboard metrics"""
    if not wallet_address:
        return {'total_value_usd': 0, 'sol_balance': 0, 'token_count': 0}
    
    tracker = SolanaWalletTracker()
    portfolio = tracker.get_full_portfolio(wallet_address)
    
    if portfolio['success']:
        # Rough USD estimation (would need price feeds for accurate conversion)
        sol_price_estimate = 100  # Placeholder - should fetch from price API
        estimated_value = portfolio['sol_balance'] * sol_price_estimate
        
        return {
            'total_value_usd': estimated_value,
            'sol_balance': portfolio['sol_balance'],
            'token_count': portfolio['total_tokens'],
            'last_updated': portfolio['timestamp']
        }
    
    return {'total_value_usd': 0, 'sol_balance': 0, 'token_count': 0}