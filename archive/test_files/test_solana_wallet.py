#!/usr/bin/env python3
"""
Test script for Solana wallet integration
"""
from solana_wallet_integration import SolanaWalletTracker
import json

def test_wallet_validation():
    """Test wallet address validation"""
    tracker = SolanaWalletTracker()
    
    # Test cases
    test_wallets = [
        ("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU", True),  # Valid Solana address
        ("11111111111111111111111111111111", True),  # System program
        ("invalid", False),  # Too short
        ("!@#$%^&*()", False),  # Invalid characters
        ("", False),  # Empty
    ]
    
    print("Testing wallet validation:")
    for wallet, expected in test_wallets:
        result = tracker.validate_wallet_address(wallet)
        status = "✅" if result == expected else "❌"
        print(f"{status} {wallet[:20]}... - Valid: {result}")

def test_wallet_balance():
    """Test fetching wallet balance"""
    tracker = SolanaWalletTracker()
    
    # Test with a known wallet (Solana ecosystem fund)
    test_wallet = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    
    print(f"\nTesting wallet balance for: {test_wallet}")
    result = tracker.get_wallet_balance(test_wallet)
    
    if result['success']:
        print(f"✅ Balance: {result['balance_sol']:.4f} SOL")
        print(f"   Lamports: {result['balance_lamports']:,}")
    else:
        print(f"❌ Error: {result['error']}")

def test_token_accounts():
    """Test fetching token accounts"""
    tracker = SolanaWalletTracker()
    
    # Test with a wallet likely to have tokens
    test_wallet = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    
    print(f"\nTesting token accounts for: {test_wallet}")
    tokens = tracker.get_token_accounts(test_wallet)
    
    if tokens:
        print(f"✅ Found {len(tokens)} tokens")
        for token in tokens[:5]:  # Show first 5
            print(f"   - {token['mint'][:8]}... Balance: {token['balance']}")
    else:
        print("❌ No tokens found or error occurred")

def test_full_portfolio():
    """Test full portfolio fetch"""
    tracker = SolanaWalletTracker()
    
    # Test wallet
    test_wallet = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    
    print(f"\nTesting full portfolio for: {test_wallet}")
    portfolio = tracker.get_full_portfolio(test_wallet)
    
    if portfolio['success']:
        print(f"✅ Portfolio fetched successfully")
        print(f"   SOL Balance: {portfolio['sol_balance']:.4f}")
        print(f"   Total Tokens: {portfolio['total_tokens']}")
        print(f"   Timestamp: {portfolio['timestamp']}")
        
        if portfolio['tokens']:
            print("\n   Top tokens:")
            for token in portfolio['tokens'][:3]:
                print(f"   - {token['symbol']}: {token['balance']:,.6f}")
    else:
        print("❌ Failed to fetch portfolio")

if __name__ == "__main__":
    print("🚀 Testing Solana Wallet Integration\n")
    
    test_wallet_validation()
    test_wallet_balance()
    test_token_accounts()
    test_full_portfolio()
    
    print("\n✅ Tests completed!")