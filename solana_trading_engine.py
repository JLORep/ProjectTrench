#!/usr/bin/env python3
"""
TrenchCoat Pro - Solana Trading Engine
Automated execution of Solana trades via Jupiter DEX
"""

import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, Optional, List
import requests
import logging
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import aiohttp

class SolanaTrader:
    """Professional Solana trading engine for TrenchCoat Pro"""
    
    def __init__(self, rpc_endpoint: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_endpoint = rpc_endpoint
        self.client = AsyncClient(rpc_endpoint)
        self.jupiter_api = "https://quote-api.jup.ag/v6"
        
        # Trading configuration
        self.wallet_keypair = None
        self.wallet_pubkey = None
        self.slippage_bps = 50  # 0.5% slippage tolerance
        self.priority_fee = 0.001  # SOL priority fee
        
        # Token addresses
        self.tokens = {
            "SOL": "So11111111111111111111111111111111111111112",
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "WSOL": "So11111111111111111111111111111111111111112"
        }
        
        # Safety limits
        self.max_trade_amount_sol = 0.1  # Maximum 0.1 SOL per trade
        self.min_trade_amount_sol = 0.01  # Minimum 0.01 SOL per trade
        
    def setup_wallet(self, private_key_base58: str):
        """Setup trading wallet from private key"""
        try:
            # Convert base58 private key to keypair
            private_key_bytes = base64.b58decode(private_key_base58)
            self.wallet_keypair = Keypair.from_bytes(private_key_bytes)
            self.wallet_pubkey = self.wallet_keypair.pubkey()
            
            print(f"Wallet configured: {str(self.wallet_pubkey)}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to setup wallet: {e}")
            return False
            
    async def get_wallet_balance(self, token_mint: Optional[str] = None) -> float:
        """Get wallet balance for SOL or specific token"""
        
        try:
            if token_mint is None or token_mint == self.tokens["SOL"]:
                # Get SOL balance
                response = await self.client.get_balance(self.wallet_pubkey)
                if response.value:
                    return response.value / 1e9  # Convert lamports to SOL
                    
            else:
                # Get SPL token balance
                response = await self.client.get_token_accounts_by_owner(
                    self.wallet_pubkey,
                    {"mint": Pubkey.from_string(token_mint)}
                )
                
                if response.value:
                    for account in response.value:
                        account_info = await self.client.get_account_info(account.pubkey)
                        if account_info.value:
                            # Parse token account data
                            # This is simplified - full implementation would decode the account data
                            return 0.0  # Placeholder
                            
            return 0.0
            
        except Exception as e:
            logging.error(f"Failed to get wallet balance: {e}")
            return 0.0
            
    async def get_quote(self, input_mint: str, output_mint: str, amount: int) -> Optional[Dict]:
        """Get trading quote from Jupiter"""
        
        try:
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": amount,
                "slippageBps": self.slippage_bps,
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.jupiter_api}/quote", params=params) as response:
                    if response.status == 200:
                        quote_data = await response.json()
                        return quote_data
                    else:
                        logging.error(f"Quote request failed: {response.status}")
                        return None
                        
        except Exception as e:
            logging.error(f"Failed to get quote: {e}")
            return None
            
    async def execute_swap(self, quote: Dict) -> Optional[str]:
        """Execute swap transaction using Jupiter"""
        
        try:
            # Get swap transaction from Jupiter
            swap_request = {
                "quoteResponse": quote,
                "userPublicKey": str(self.wallet_pubkey),
                "wrapAndUnwrapSol": True,
                "prioritizationFeeLamports": int(self.priority_fee * 1e9)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.jupiter_api}/swap", 
                    json=swap_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        swap_data = await response.json()
                        
                        # Decode and sign transaction
                        swap_transaction = swap_data["swapTransaction"]
                        transaction_bytes = base64.b64decode(swap_transaction)
                        transaction = Transaction.from_bytes(transaction_bytes)
                        
                        # Sign transaction
                        transaction.sign([self.wallet_keypair])
                        
                        # Send transaction
                        tx_response = await self.client.send_transaction(
                            transaction, 
                            opts={"skip_preflight": False, "max_retries": 3}
                        )
                        
                        if tx_response.value:
                            tx_signature = str(tx_response.value)
                            
                            # Wait for confirmation
                            await self._wait_for_confirmation(tx_signature)
                            
                            return tx_signature
                        else:
                            logging.error("Failed to send transaction")
                            return None
                            
                    else:
                        error_text = await response.text()
                        logging.error(f"Swap request failed: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logging.error(f"Failed to execute swap: {e}")
            return None
            
    async def _wait_for_confirmation(self, signature: str, max_retries: int = 30):
        """Wait for transaction confirmation"""
        
        for i in range(max_retries):
            try:
                response = await self.client.get_signature_status(signature)
                if response.value and response.value[0]:
                    status = response.value[0]
                    if status.confirmation_status == Confirmed:
                        logging.info(f"Transaction confirmed: {signature}")
                        return True
                        
                await asyncio.sleep(2)  # Wait 2 seconds between checks
                
            except Exception as e:
                logging.error(f"Error checking confirmation: {e}")
                await asyncio.sleep(2)
                
        logging.warning(f"Transaction confirmation timeout: {signature}")
        return False
        
    async def buy_token(self, token_address: str, sol_amount: float, max_slippage: float = 0.5) -> Optional[Dict]:
        """Buy token with SOL"""
        
        # Safety checks
        if sol_amount > self.max_trade_amount_sol:
            logging.error(f"Trade amount {sol_amount} SOL exceeds maximum {self.max_trade_amount_sol} SOL")
            return None
            
        if sol_amount < self.min_trade_amount_sol:
            logging.error(f"Trade amount {sol_amount} SOL below minimum {self.min_trade_amount_sol} SOL")
            return None
            
        # Check wallet balance
        sol_balance = await self.get_wallet_balance()
        if sol_balance < sol_amount + 0.001:  # Reserve for transaction fees
            logging.error(f"Insufficient SOL balance: {sol_balance}, need: {sol_amount}")
            return None
            
        try:
            # Convert SOL amount to lamports
            amount_lamports = int(sol_amount * 1e9)
            
            # Get quote
            quote = await self.get_quote(
                input_mint=self.tokens["SOL"],
                output_mint=token_address,
                amount=amount_lamports
            )
            
            if not quote:
                logging.error("Failed to get buy quote")
                return None
                
            # Calculate expected output
            expected_output = int(quote["outAmount"])
            price_impact = float(quote.get("priceImpactPct", 0))
            
            # Safety check - reject high price impact trades
            if abs(price_impact) > max_slippage:
                logging.error(f"Price impact too high: {price_impact}%")
                return None
                
            # Execute swap
            tx_signature = await self.execute_swap(quote)
            
            if tx_signature:
                trade_result = {
                    "type": "BUY",
                    "token_address": token_address,
                    "sol_amount": sol_amount,
                    "expected_tokens": expected_output,
                    "price_impact": price_impact,
                    "transaction": tx_signature,
                    "timestamp": datetime.now().isoformat(),
                    "status": "SUCCESS"
                }
                
                logging.info(f"Buy order executed: {trade_result}")
                return trade_result
            else:
                return {"status": "FAILED", "error": "Transaction failed"}
                
        except Exception as e:
            logging.error(f"Buy order failed: {e}")
            return {"status": "FAILED", "error": str(e)}
            
    async def sell_token(self, token_address: str, token_amount: int, max_slippage: float = 0.5) -> Optional[Dict]:
        """Sell token for SOL"""
        
        try:
            # Get quote for selling
            quote = await self.get_quote(
                input_mint=token_address,
                output_mint=self.tokens["SOL"],
                amount=token_amount
            )
            
            if not quote:
                logging.error("Failed to get sell quote")
                return None
                
            # Calculate expected SOL output
            expected_sol = int(quote["outAmount"]) / 1e9
            price_impact = float(quote.get("priceImpactPct", 0))
            
            # Safety check
            if abs(price_impact) > max_slippage:
                logging.error(f"Price impact too high: {price_impact}%")
                return None
                
            # Execute swap
            tx_signature = await self.execute_swap(quote)
            
            if tx_signature:
                trade_result = {
                    "type": "SELL",
                    "token_address": token_address,
                    "token_amount": token_amount,
                    "expected_sol": expected_sol,
                    "price_impact": price_impact,
                    "transaction": tx_signature,
                    "timestamp": datetime.now().isoformat(),
                    "status": "SUCCESS"
                }
                
                logging.info(f"Sell order executed: {trade_result}")
                return trade_result
            else:
                return {"status": "FAILED", "error": "Transaction failed"}
                
        except Exception as e:
            logging.error(f"Sell order failed: {e}")
            return {"status": "FAILED", "error": str(e)}
            
    async def execute_runner_trade(self, runner_data: Dict) -> Optional[Dict]:
        """Execute trade for detected Runner"""
        
        try:
            token_address = runner_data.get("token_address")
            confidence = runner_data.get("runner_confidence", 0)
            symbol = runner_data.get("symbol", "Unknown")
            
            if not token_address:
                logging.error("No token address provided for Runner trade")
                return None
                
            # Calculate trade size based on confidence
            base_trade_size = 0.05  # Base 0.05 SOL
            confidence_multiplier = min(confidence / 100, 1.0)  # Max 1.0x
            trade_size = base_trade_size * confidence_multiplier
            
            # Ensure within limits
            trade_size = max(self.min_trade_amount_sol, min(trade_size, self.max_trade_amount_sol))
            
            logging.info(f"Executing Runner trade: {symbol} with {trade_size} SOL (confidence: {confidence}%)")
            
            # Execute buy order
            result = await self.buy_token(token_address, trade_size)
            
            if result and result.get("status") == "SUCCESS":
                # Send notification of successful trade
                await self._notify_trade_executed(runner_data, result)
                
            return result
            
        except Exception as e:
            logging.error(f"Runner trade execution failed: {e}")
            return {"status": "FAILED", "error": str(e)}
            
    async def _notify_trade_executed(self, runner_data: Dict, trade_result: Dict):
        """Send notification when trade is executed"""
        
        try:
            symbol = runner_data.get("symbol", "Unknown")
            sol_amount = trade_result.get("sol_amount", 0)
            tx_signature = trade_result.get("transaction", "")
            
            # Create notification message
            message = f"""
🚀 TRADE EXECUTED! 🚀

💰 Token: {symbol}
💵 Amount: {sol_amount} SOL
📈 Status: SUCCESS
🔗 TX: {tx_signature[:8]}...

⏰ {datetime.now().strftime('%H:%M:%S')}

Trade executed automatically by TrenchCoat Pro AI
            """.strip()
            
            # Here you would integrate with your notification system
            print(f"TRADE NOTIFICATION: {message}")
            
        except Exception as e:
            logging.error(f"Failed to send trade notification: {e}")
            
    def get_trading_status(self) -> Dict:
        """Get current trading engine status"""
        
        return {
            "wallet_connected": self.wallet_keypair is not None,
            "wallet_address": str(self.wallet_pubkey) if self.wallet_pubkey else None,
            "rpc_endpoint": self.rpc_endpoint,
            "max_trade_size": self.max_trade_amount_sol,
            "min_trade_size": self.min_trade_amount_sol,
            "slippage_tolerance": self.slippage_bps / 100,
            "priority_fee": self.priority_fee,
            "jupiter_api": self.jupiter_api,
            "status": "READY" if self.wallet_keypair else "NOT_CONFIGURED"
        }

# Safety wrapper for live trading
class SafeTrader:
    """Safety wrapper around SolanaTrader with additional checks"""
    
    def __init__(self, solana_trader: SolanaTrader):
        self.trader = solana_trader
        self.daily_limit_sol = 0.5  # Maximum 0.5 SOL per day
        self.trades_today = []
        self.enabled = False  # Must be explicitly enabled
        
    def enable_live_trading(self, confirmation_code: str):
        """Enable live trading with confirmation"""
        if confirmation_code == "TRENCHCOAT_LIVE_TRADING_ENABLED":
            self.enabled = True
            logging.info("Live trading enabled")
            return True
        else:
            logging.error("Invalid confirmation code")
            return False
            
    def disable_live_trading(self):
        """Disable live trading"""
        self.enabled = False
        logging.info("Live trading disabled")
        
    async def safe_execute_trade(self, runner_data: Dict) -> Optional[Dict]:
        """Execute trade with safety checks"""
        
        if not self.enabled:
            logging.warning("Live trading is disabled")
            return {"status": "DISABLED", "message": "Live trading is disabled"}
            
        # Check daily limits
        today_total = sum(trade.get("sol_amount", 0) for trade in self.trades_today)
        proposed_amount = min(0.05, self.trader.max_trade_amount_sol)
        
        if today_total + proposed_amount > self.daily_limit_sol:
            logging.warning(f"Daily limit exceeded: {today_total + proposed_amount} > {self.daily_limit_sol}")
            return {"status": "LIMIT_EXCEEDED", "message": "Daily trading limit exceeded"}
            
        # Execute trade
        result = await self.trader.execute_runner_trade(runner_data)
        
        # Track successful trades
        if result and result.get("status") == "SUCCESS":
            self.trades_today.append(result)
            
        return result

# Usage example and testing
async def test_solana_trader():
    """Test Solana trading functionality"""
    
    # Initialize trader
    trader = SolanaTrader()
    
    # Display status
    status = trader.get_trading_status()
    print("Solana Trading Engine Status:")
    print(json.dumps(status, indent=2))
    
    # Example Runner data
    runner_data = {
        "symbol": "PEPE",
        "token_address": "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC",  # Example token
        "runner_confidence": 85.0,
        "current_price": 0.00001234,
        "price_change_24h": 67.5
    }
    
    print("\nExample Runner trade simulation:")
    print(f"Would execute: {runner_data['symbol']} with confidence {runner_data['runner_confidence']}%")
    
    # Note: Actual trading requires wallet setup and funding
    print("\n⚠️  LIVE TRADING REQUIRES:")
    print("1. Funded Solana wallet")
    print("2. Private key configuration")
    print("3. Explicit trading confirmation")
    print("4. Risk management setup")
    
    return trader

if __name__ == "__main__":
    # Test the trading engine
    trader = asyncio.run(test_solana_trader())
    
    print("\n🚀 Solana Trading Engine Ready!")
    print("Configure wallet and enable live trading to start automated execution.")