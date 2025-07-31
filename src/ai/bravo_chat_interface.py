#!/usr/bin/env python3
"""
BRAVO CLAUDE CHAT INTERFACE
Direct communication with Claude for strategy development
"""
import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import anthropic
import os
from dataclasses import dataclass, field

from src.strategies.top10_strategies import Top10Strategies
from src.data.comprehensive_enricher import ComprehensiveTokenData

@dataclass
class StrategyConversation:
    """Track strategy development conversations"""
    timestamp: datetime
    user_input: str
    claude_response: str
    strategy_code: Optional[str] = None
    backtest_results: Optional[Dict] = None
    approved: bool = False

class BravoChatInterface:
    """
    Direct Claude interface for Bravo strategy development
    """
    
    def __init__(self):
        self.claude_client = None
        self.conversation_history = []
        self.strategies_engine = Top10Strategies()
        
        # Initialize Claude client if API key available
        try:
            api_key = None
            # Try to get API key from secrets
            try:
                if hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
                    api_key = st.secrets['ANTHROPIC_API_KEY']
                    # Skip if it's the placeholder value
                    if api_key and api_key.startswith('sk-ant-api03-your_key_here'):
                        api_key = None
            except:
                pass
            
            # Try environment variable if secrets failed
            if not api_key:
                api_key = os.getenv('ANTHROPIC_API_KEY')
                # Skip if it's the placeholder value
                if api_key and api_key.startswith('sk-ant-api03-your_key_here'):
                    api_key = None
            
            # Initialize client if we have a valid key
            if api_key and api_key.startswith('sk-ant-api03-') and len(api_key) > 20:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
            else:
                self.claude_client = None
        except Exception as e:
            self.claude_client = None
        
        # Initialize session state for chat
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'custom_strategies' not in st.session_state:
            st.session_state.custom_strategies = {}
        if 'strategy_prototypes' not in st.session_state:
            st.session_state.strategy_prototypes = []
    
    def render_chat_interface(self):
        """Render the main chat interface for Bravo"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem;
                    border: 2px solid #10b981;">
            <h2 style="color: #10b981; margin: 0;">🤖 Claude Strategy Assistant</h2>
            <p style="color: #9ca3af; margin: 0.5rem 0 0 0;">
                Direct communication with Claude for strategy development and testing
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show API key status
        if not self.claude_client:
            st.info("""
            🔑 **Claude API Key Required**: To enable real-time AI strategy development, add your Anthropic API key to `.streamlit/secrets.toml`:
            
            ```
            ANTHROPIC_API_KEY = "sk-ant-api03-your_actual_key_here"
            ```
            
            Get your API key at: https://console.anthropic.com/
            
            Without the API key, the system will use local processing with pre-built strategy templates.
            """)
        
        # Chat input section
        st.subheader("💬 Strategy Development Chat")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_area(
                "Describe your strategy idea or ask Claude anything:",
                placeholder="Example: 'Create a momentum strategy that focuses on tokens with increasing social media mentions and locked liquidity'",
                height=100,
                key="strategy_input",
                value=st.session_state.get("strategy_input_value", "")
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if st.button("💡 Send to Claude", type="primary", use_container_width=True):
                if user_input.strip():
                    self.process_strategy_request(user_input)
            
            if st.button("🧪 Test Strategy", use_container_width=True):
                if st.session_state.strategy_prototypes:
                    self.test_latest_strategy()
            
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        # Display chat history
        self.render_chat_history()
        
        # Quick strategy templates
        self.render_strategy_templates()
    
    def process_strategy_request(self, user_input: str):
        """Process strategy request through Claude"""
        if not self.claude_client:
            # Fallback to local processing if no Claude API
            response = self.process_local_strategy_request(user_input)
        else:
            response = self.process_claude_strategy_request(user_input)
        
        # Add to chat history
        st.session_state.chat_history.append({
            'timestamp': datetime.now(),
            'type': 'user',
            'content': user_input
        })
        
        st.session_state.chat_history.append({
            'timestamp': datetime.now(),
            'type': 'claude',
            'content': response['content'],
            'strategy_code': response.get('strategy_code'),
            'metadata': response.get('metadata', {})
        })
        
        st.rerun()
    
    def process_claude_strategy_request(self, user_input: str) -> Dict[str, Any]:
        """Process request through Claude API"""
        try:
            # Prepare context about TrenchCoat system
            system_context = """
You are Claude, an AI assistant helping Bravo develop cryptocurrency trading strategies for the TrenchCoat Elite system.

CONTEXT ABOUT TRENCHCOAT:
- Focuses on Solana memecoins
- Uses comprehensive data from multiple APIs (DexScreener, Birdeye, Jupiter, etc.)
- Has 10 existing strategies with different risk/return profiles
- Trades 30 coins out of 75 daily opportunities
- Each strategy returns signals with entry/exit parameters

AVAILABLE DATA POINTS:
- Price data (5m, 1h, 6h, 24h changes)
- Volume data across timeframes
- Market cap, liquidity, holder data
- Whale concentration metrics
- Social media metrics (Twitter, Telegram)
- Risk scores (rug risk, honeypot risk)
- Technical indicators (RSI, moving averages)
- On-chain data (creator holdings, mint status)

YOUR ROLE:
1. Help Bravo develop new trading strategies
2. Provide Python code for strategy implementation
3. Suggest improvements to existing strategies
4. Analyze market patterns and opportunities
5. Create testable strategy prototypes

When providing strategy code, use this template:
```python
def custom_strategy_name(self, tokens: List[ComprehensiveTokenData]) -> List[Dict]:
    signals = []
    for token in tokens:
        score = 0
        reasoning = []
        
        # Add your strategy logic here
        # Example: if token.price_change_5m > 10: score += 0.3
        
        if score >= THRESHOLD:
            signals.append({
                'token': token,
                'action': 'BUY',
                'entry_price': token.price_usd,
                'profit_target': token.price_usd * TARGET_MULTIPLIER,
                'stop_loss': token.price_usd * STOP_MULTIPLIER,
                'time_limit_hours': HOURS,
                'position_size': POSITION_PERCENT,
                'score': score,
                'reasoning': reasoning,
                'strategy': 'custom_strategy_name'
            })
    
    return sorted(signals, key=lambda x: x['score'], reverse=True)[:30]
```

Be specific, actionable, and focus on profitable opportunities in the Solana memecoin space.
"""
            
            messages = [
                {"role": "user", "content": f"{system_context}\n\nBravo's request: {user_input}"}
            ]
            
            # Add recent chat history for context
            for msg in st.session_state.chat_history[-6:]:  # Last 6 messages
                role = "user" if msg['type'] == 'user' else "assistant"
                messages.append({"role": role, "content": msg['content']})
            
            response = self.claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.7,
                messages=messages
            )
            
            response_content = response.content[0].text
            
            # Extract strategy code if present
            strategy_code = None
            if "```python" in response_content:
                try:
                    start = response_content.find("```python") + 9
                    end = response_content.find("```", start)
                    strategy_code = response_content[start:end].strip()
                except:
                    pass
            
            return {
                'content': response_content,
                'strategy_code': strategy_code,
                'metadata': {'source': 'claude_api'}
            }
            
        except Exception as e:
            return {
                'content': f"Claude API Error: {e}. Using local processing instead.",
                'strategy_code': None,
                'metadata': {'source': 'error_fallback'}
            }
    
    def process_local_strategy_request(self, user_input: str) -> Dict[str, Any]:
        """Local processing when Claude API unavailable"""
        
        # Simple keyword-based strategy suggestions
        keywords = user_input.lower()
        
        if "momentum" in keywords:
            strategy_suggestion = """
I'll help you create a momentum-based strategy! Here's a framework:

**Momentum Strategy Concept:**
- Focus on tokens with strong 5-minute and 1-hour price increases
- Combine with volume validation to avoid fake pumps
- Add social sentiment as confirmation signal

**Key Factors to Consider:**
1. Price momentum across multiple timeframes
2. Volume surge confirmation (2x+ normal volume)
3. Market cap sweet spot ($100K - $10M for memecoins)
4. Low rug risk scores
5. Adequate liquidity for entry/exit

**Suggested Entry Criteria:**
- 5m change > 15% AND 1h change > 20%
- Volume spike > 2x average
- Rug risk < 0.3
- Liquidity > $50K

**Risk Management:**
- Position size: 3-5% of portfolio
- Profit target: +50% 
- Stop loss: -15%
- Max hold time: 4 hours

Would you like me to code this into a testable strategy?
"""
            
        elif "social" in keywords or "twitter" in keywords or "telegram" in keywords:
            strategy_suggestion = """
Great idea focusing on social sentiment! Here's my approach:

**Social Sentiment Strategy:**
- Identify tokens with growing social presence
- Correlate social metrics with price action
- Time entries based on social momentum peaks

**Data Points to Use:**
1. Twitter followers growth rate
2. Telegram member count
3. Website presence (shows legitimacy)
4. Social mentions volume
5. Community engagement metrics

**Strategy Logic:**
- High social activity + early price movement = opportunity
- Avoid tokens with declining social metrics
- Focus on organic growth vs artificial pumping

**Entry Signals:**
- Twitter followers > 1000 OR Telegram > 500
- Recent social growth (if trackable)
- Price momentum confirming social buzz
- Community engagement indicators

Want me to develop the full strategy code?
"""
            
        elif "whale" in keywords:
            strategy_suggestion = """
Whale tracking is powerful! Here's my whale-following approach:

**Whale Following Strategy:**
- Monitor whale wallet movements
- Identify accumulation patterns
- Follow smart money into positions

**Key Metrics:**
1. Whale count (2-10 ideal range)
2. Top 10 holders concentration (<40%)
3. Recent whale entry patterns
4. Whale retention rates

**Strategy Framework:**
- Good whale distribution = stability
- New whale entries = bullish signal
- Whale exits = immediate risk
- Creator whale behavior = critical

**Implementation:**
- Track holder concentration changes
- Monitor large wallet movements
- Set alerts for whale activity spikes
- Correlate whale behavior with price action

This requires good on-chain data. Should I code a whale-following strategy?
"""
            
        else:
            strategy_suggestion = f"""
I understand you want to develop a strategy around: "{user_input}"

**Let me help you break this down:**

1. **Define the Core Signal**: What specific market condition triggers this strategy?
2. **Data Requirements**: Which data points from our comprehensive dataset are most relevant?
3. **Entry Criteria**: What combination of factors creates a buy signal?
4. **Risk Management**: How do we protect capital and maximize profits?
5. **Exit Strategy**: When and how do we close positions?

**Available Strategy Types:**
- Momentum-based (price action focused)
- Volume-based (trading activity focused)  
- Social sentiment (community metrics)
- Technical analysis (indicators and patterns)
- Risk arbitrage (multi-DEX opportunities)
- Fundamental analysis (tokenomics and team)

**Next Steps:**
1. Clarify your strategy concept
2. I'll create the Python implementation
3. We'll backtest it against historical data
4. Optimize parameters for maximum profitability

What specific aspect would you like to focus on first?
"""
        
        return {
            'content': strategy_suggestion,
            'strategy_code': None,
            'metadata': {'source': 'local_processing'}
        }
    
    def render_chat_history(self):
        """Render the chat conversation history"""
        if not st.session_state.chat_history:
            st.info("💡 Start a conversation! Describe your strategy ideas or ask questions about trading approaches.")
            return
        
        st.subheader("💬 Conversation History")
        
        for i, msg in enumerate(reversed(st.session_state.chat_history[-10:])):  # Show last 10 messages
            timestamp = msg['timestamp'].strftime("%H:%M:%S")
            
            if msg['type'] == 'user':
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 8px; 
                           border-left: 4px solid #10b981; margin: 0.5rem 0;">
                    <strong>🧑‍💼 Bravo ({timestamp}):</strong><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 8px; 
                           border-left: 4px solid #3b82f6; margin: 0.5rem 0;">
                    <strong>🤖 Claude ({timestamp}):</strong><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
                
                # Show strategy code if present
                if msg.get('strategy_code'):
                    with st.expander("📝 Generated Strategy Code"):
                        st.code(msg['strategy_code'], language='python')
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"💾 Save Strategy {i}", key=f"save_{i}"):
                                self.save_strategy_prototype(msg['strategy_code'], f"strategy_{i}")
                        
                        with col2:
                            if st.button(f"🧪 Test Now {i}", key=f"test_{i}"):
                                self.test_strategy_code(msg['strategy_code'])
    
    def render_strategy_templates(self):
        """Render quick strategy templates"""
        st.subheader("⚡ Quick Strategy Templates")
        
        templates = {
            "Momentum Breakout": "Create a strategy that buys tokens with >20% 1-hour momentum and high volume",
            "Social Surge": "Develop a strategy based on Twitter follower growth + price correlation",
            "Whale Following": "Track whale accumulation patterns and follow smart money",
            "New Coin Sniper": "Target newly launched tokens with locked liquidity",
            "Reversal Hunter": "Find oversold tokens showing reversal signals",
            "Volume Explosion": "Identify unusual volume spikes before price moves",
            "Risk Arbitrage": "Exploit price differences across multiple DEXs",
            "Technical Signals": "Use RSI, moving averages for entry/exit timing"
        }
        
        col1, col2 = st.columns(2)
        
        for i, (name, description) in enumerate(templates.items()):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                if st.button(f"🎯 {name}", key=f"template_{i}", use_container_width=True):
                    st.session_state.strategy_input_value = description
                    self.process_strategy_request(description)
                    st.rerun()
    
    def save_strategy_prototype(self, strategy_code: str, strategy_name: str):
        """Save strategy prototype for testing"""
        prototype = {
            'name': strategy_name,
            'code': strategy_code,
            'timestamp': datetime.now(),
            'tested': False,
            'results': None
        }
        
        st.session_state.strategy_prototypes.append(prototype)
        st.success(f"✅ Strategy '{strategy_name}' saved for testing!")
    
    def test_strategy_code(self, strategy_code: str):
        """Test strategy code with sample data"""
        try:
            # This would integrate with the actual backtesting system
            st.info("🧪 Strategy testing functionality would integrate with the backtesting engine here.")
            st.code(strategy_code, language='python')
            
        except Exception as e:
            st.error(f"Strategy test error: {e}")
    
    def test_latest_strategy(self):
        """Test the most recent strategy prototype"""
        if not st.session_state.strategy_prototypes:
            st.warning("No strategy prototypes available to test.")
            return
        
        latest = st.session_state.strategy_prototypes[-1]
        st.info(f"🧪 Testing strategy: {latest['name']}")
        
        # This would run the actual backtest
        # For now, show the code
        with st.expander("Strategy Code"):
            st.code(latest['code'], language='python')
    
    def render_strategy_management(self):
        """Render strategy management panel"""
        st.subheader("📊 Strategy Management")
        
        if not st.session_state.strategy_prototypes:
            st.info("No custom strategies created yet. Start a conversation with Claude to develop strategies!")
            return
        
        # Show saved strategies
        for i, prototype in enumerate(st.session_state.strategy_prototypes):
            with st.expander(f"Strategy: {prototype['name']} ({prototype['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
                st.code(prototype['code'], language='python')
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"🧪 Test", key=f"test_proto_{i}"):
                        self.test_strategy_code(prototype['code'])
                
                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_proto_{i}"):
                        st.text_area("Edit Strategy Code:", value=prototype['code'], key=f"edit_code_{i}")
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_proto_{i}"):
                        st.session_state.strategy_prototypes.pop(i)
                        st.rerun()

def render_bravo_interface():
    """Main function to render Bravo's interface"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                border-radius: 16px; margin-bottom: 2rem; border: 2px solid #ffd700;">
        <h1 style="color: #ffd700; margin: 0;">👑 Bravo's Strategy Command Center</h1>
        <p style="color: #d1d5db; margin: 0.5rem 0 0 0;">
            Direct access to Claude AI for strategy development, testing, and optimization
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    chat_interface = BravoChatInterface()
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["💬 Claude Chat", "📊 Strategy Management", "🧪 Testing Lab"])
    
    with tab1:
        chat_interface.render_chat_interface()
    
    with tab2:
        chat_interface.render_strategy_management()
    
    with tab3:
        st.subheader("🧪 Strategy Testing Laboratory")
        st.info("Advanced backtesting and optimization tools will be integrated here.")
        
        if st.session_state.strategy_prototypes:
            st.write("**Available Prototypes:**")
            for proto in st.session_state.strategy_prototypes:
                st.write(f"- {proto['name']} ({proto['timestamp'].strftime('%Y-%m-%d %H:%M')})")

if __name__ == "__main__":
    render_bravo_interface()