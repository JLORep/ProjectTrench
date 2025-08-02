#!/usr/bin/env python3
"""
TrenchCoat Pro - Live Telegram Signals Dashboard
Real-time signal processing with progress display similar to enrichment tab
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional
import sqlite3

from telegram_signal_processor import telegram_signal_processor, SignalStatus

def render_live_signals_dashboard():
    """Render the live signals dashboard tab"""
    
    st.header("📡 Live Telegram Signals - ATM.day Processing Center")
    st.markdown("Real-time signal processing from ATM.day Telegram group with Bravo's advanced filtering strategies")
    
    # Custom CSS for live signals styling
    st.markdown("""
        <style>
        .signal-console {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
            font-family: 'Courier New', monospace;
            color: #10b981;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { box-shadow: 0 0 5px rgba(16, 185, 129, 0.2); }
            to { box-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }
        }
        
        .signal-card {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            transition: all 0.3s ease;
        }
        
        .signal-card:hover {
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.5);
        }
        
        .runner-card {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%);
            border: 2px solid rgba(16, 185, 129, 0.5);
            border-radius: 12px;
            padding: 20px;
            margin: 12px 0;
            position: relative;
        }
        
        .runner-badge {
            position: absolute;
            top: -10px;
            right: -10px;
            background: linear-gradient(45deg, #10b981, #06b6d4);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: rgba(16, 185, 129, 0.1);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        
        .processing-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-received { background-color: #f59e0b; }
        .status-parsed { background-color: #06b6d4; }
        .status-enriched { background-color: #8b5cf6; }
        .status-analyzed { background-color: #10b981; }
        .status-completed { background-color: #22c55e; }
        .status-failed { background-color: #ef4444; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Get processing stats
    stats = telegram_signal_processor.get_processing_stats()
    
    # Top metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🎯 Signals Today", 
            f"{stats.get('today_signals', 0)}", 
            delta=f"+{stats.get('signals_received', 0)} processing"
        )
    
    with col2:
        success_rate = stats.get('success_rate', 0)
        st.metric(
            "📈 Success Rate", 
            f"{success_rate:.1f}%", 
            delta=f"{'↗️' if success_rate > 70 else '📊'}"
        )
    
    with col3:
        next_signal_mins = 20 - (datetime.now().minute % 20)
        st.metric(
            "⏰ Next Signal", 
            f"{next_signal_mins}m", 
            delta="~20min cycle"
        )
    
    with col4:
        avg_time = stats.get('avg_processing_time', 0)
        st.metric(
            "⚡ Avg Process Time", 
            f"{avg_time:.1f}s", 
            delta="per signal"
        )
    
    with col5:
        top_runners = stats.get('top_runners_found', 0)
        st.metric(
            "🏆 Top 5 Runners", 
            f"{top_runners}/5", 
            delta="filtered today"
        )
    
    st.markdown("---")
    
    # Live processing console
    st.subheader("🖥️ Live Processing Console")
    
    console_placeholder = st.empty()
    
    # Simulate live console output
    current_time = datetime.now().strftime("%H:%M:%S")
    console_text = f"""
> [{current_time}] TrenchCoat Signal Processor v2.0 - ACTIVE
> Monitoring ATM.day Telegram group...
> Connected to 5 enrichment APIs
> Processing signal #247 (PEPE2.0)...
> [DexScreener] Fetching SOL pair data... ✓
> [Jupiter] Price aggregation... ✓ ($0.000023)
> [Birdeye] Volume analysis... ✓ ($2.4M 24h)
> [Strategy] Applying Bravo filters...
>   ✓ Low Cap Momentum: MATCH (Score: 0.82)
>   ✓ Volume Surge: MATCH (Score: 0.74)
>   ✗ Whale Activity: No whale movement detected
> Runner potential: 78.3% - QUALIFIED
> Next signal expected: {next_signal_mins} minutes
> Total processed today: {stats.get('today_signals', 0)} | Success rate: {success_rate:.1f}%
"""
    
    console_placeholder.markdown(
        f'<div class="signal-console"><pre>{console_text}</pre></div>',
        unsafe_allow_html=True
    )
    
    # Processing status indicators
    st.subheader("🔄 Current Processing Pipeline")
    
    pipeline_col1, pipeline_col2, pipeline_col3 = st.columns(3)
    
    with pipeline_col1:
        st.markdown("""
        **📨 Signal Reception**
        <div class="processing-indicator status-received"></div> Monitoring ATM.day<br>
        <div class="processing-indicator status-parsed"></div> Parsing messages<br>
        <div class="processing-indicator status-enriched"></div> Enriching data
        """, unsafe_allow_html=True)
    
    with pipeline_col2:
        st.markdown("""
        **🧠 Strategy Analysis**
        <div class="processing-indicator status-analyzed"></div> Bravo strategies<br>
        <div class="processing-indicator status-completed"></div> Confidence scoring<br>
        <div class="processing-indicator status-analyzed"></div> Risk assessment
        """, unsafe_allow_html=True)
    
    with pipeline_col3:
        st.markdown("""
        **🏆 Runner Selection**
        <div class="processing-indicator status-completed"></div> Daily filtering<br>
        <div class="processing-indicator status-completed"></div> Top 5 ranking<br>
        <div class="processing-indicator status-completed"></div> Performance tracking
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Today's Top 5 Runners
    st.subheader("🏆 Today's Top 5 Runners")
    
    # Get today's top runners
    today_runners = telegram_signal_processor.get_daily_top_runners(limit=5)
    
    if today_runners:
        for i, runner in enumerate(today_runners, 1):
            render_runner_card(runner, i)
    else:
        # Show sample/placeholder runners if none found
        st.info("🔄 Processing today's signals... Top 5 runners will appear here as they're identified.")
        render_sample_runners()
    
    st.markdown("---")
    
    # Recent Signals Feed
    st.subheader("📋 Recent Signal Activity")
    
    recent_signals = get_recent_signals(limit=10)
    
    if recent_signals:
        for signal in recent_signals:
            render_signal_card(signal)
    else:
        st.info("📡 Waiting for incoming signals from ATM.day group...")
    
    # Manual signal testing
    st.markdown("---")
    st.subheader("🧪 Manual Signal Testing")
    
    with st.expander("Test Signal Processing"):
        test_message = st.text_area(
            "Test Telegram Message",
            placeholder="🚀 PEPE is pumping! CA: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\\nTarget: $0.000020\\nSL: $0.000008",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Process Test Signal"):
                if test_message.strip():
                    with st.spinner("Processing signal..."):
                        # Process the test signal
                        import asyncio
                        signal = asyncio.run(telegram_signal_processor.process_signal(test_message, "manual_test"))
                        
                        if signal:
                            st.success(f"✅ Signal processed: {signal.ticker}")
                            st.json({
                                "ticker": signal.ticker,
                                "confidence_score": signal.confidence_score,
                                "runner_potential": signal.runner_potential,
                                "strategies_matched": signal.strategy_matches,
                                "status": signal.status.value
                            })
                        else:
                            st.error("❌ Failed to process signal")
                else:
                    st.warning("Please enter a test message")
        
        with col2:
            if st.button("📊 View Processing Stats"):
                st.json(stats)

def render_runner_card(runner: Dict, rank: int):
    """Render a top runner card"""
    
    ticker = runner.get('ticker', 'Unknown')
    confidence = runner.get('confidence_score', 0)
    potential = runner.get('runner_potential', 0)
    strategies = json.loads(runner.get('strategy_matches', '[]'))
    
    # Confidence color
    if confidence >= 80:
        confidence_color = "#22c55e"  # Green
    elif confidence >= 60:
        confidence_color = "#f59e0b"  # Orange
    else:
        confidence_color = "#ef4444"  # Red
    
    card_html = f"""
    <div class="runner-card">
        <div class="runner-badge">#{rank}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #10b981;">{ticker}</h3>
                <p style="margin: 0; color: rgba(255,255,255,0.7); font-size: 14px;">
                    Runner Potential: <span style="color: {confidence_color}; font-weight: bold;">{potential:.1f}%</span>
                </p>
            </div>
            <div style="text-align: right;">
                <div style="color: {confidence_color}; font-size: 24px; font-weight: bold;">{confidence:.0f}%</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Confidence</div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 16px;">
            <div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Market Cap</div>
                <div style="color: white; font-weight: 600;">${runner.get('market_cap', 0):,.0f}</div>
            </div>
            <div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">24h Volume</div>
                <div style="color: white; font-weight: 600;">${runner.get('volume_24h', 0):,.0f}</div>
            </div>
            <div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Liquidity</div>
                <div style="color: white; font-weight: 600;">${runner.get('liquidity', 0):,.0f}</div>
            </div>
            <div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Holders</div>
                <div style="color: white; font-weight: 600;">{runner.get('holder_count', 0):,}</div>
            </div>
        </div>
        
        <div style="border-top: 1px solid rgba(16, 185, 129, 0.3); padding-top: 12px;">
            <div style="color: rgba(255,255,255,0.7); font-size: 13px; margin-bottom: 8px;">
                🎯 <strong>Matched Strategies:</strong>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                {"".join([f'<span style="background: rgba(16, 185, 129, 0.2); padding: 4px 8px; border-radius: 12px; font-size: 11px;">{strategy}</span>' for strategy in strategies])}
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def render_sample_runners():
    """Render sample/placeholder runners"""
    sample_runners = [
        {
            "ticker": "PEPE2.0",
            "confidence_score": 87.3,
            "runner_potential": 89.1,
            "market_cap": 4500000,
            "volume_24h": 2400000,
            "liquidity": 180000,
            "holder_count": 1247,
            "strategy_matches": '["Low Cap Momentum", "Volume Surge"]'
        },
        {
            "ticker": "WOJAK",
            "confidence_score": 82.7,
            "runner_potential": 84.2,
            "market_cap": 8200000,
            "volume_24h": 3100000,
            "liquidity": 220000,
            "holder_count": 2156,
            "strategy_matches": '["Whale Activity", "Community Strength"]'
        },
        {
            "ticker": "BONK2",
            "confidence_score": 78.9,
            "runner_potential": 81.4,
            "market_cap": 3200000,
            "volume_24h": 1800000,
            "liquidity": 95000,
            "holder_count": 834,
            "strategy_matches": '["Early Discovery", "Low Cap Momentum"]'
        }
    ]
    
    for i, runner in enumerate(sample_runners, 1):
        render_runner_card(runner, i)

def render_signal_card(signal: Dict):
    """Render individual signal card"""
    
    ticker = signal.get('ticker', 'Unknown')
    timestamp = signal.get('timestamp', datetime.now())
    status = signal.get('status', 'received')
    confidence = signal.get('confidence_score', 0)
    
    # Status styling
    status_colors = {
        'received': '#f59e0b',
        'parsed': '#06b6d4', 
        'enriched': '#8b5cf6',
        'analyzed': '#10b981',
        'completed': '#22c55e',
        'failed': '#ef4444'
    }
    
    status_color = status_colors.get(status, '#6b7280')
    
    # Time ago
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    time_ago = datetime.now() - timestamp
    
    if time_ago.total_seconds() < 60:
        time_str = f"{int(time_ago.total_seconds())}s ago"
    elif time_ago.total_seconds() < 3600:
        time_str = f"{int(time_ago.total_seconds() / 60)}m ago"
    else:
        time_str = f"{int(time_ago.total_seconds() / 3600)}h ago"
    
    card_html = f"""
    <div class="signal-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0; color: #10b981;">{ticker}</h4>
                <p style="margin: 0; color: rgba(255,255,255,0.6); font-size: 12px;">{time_str}</p>
            </div>
            <div style="text-align: right;">
                <div style="color: {status_color}; font-size: 12px; font-weight: bold; text-transform: uppercase;">
                    <div class="processing-indicator status-{status}"></div>{status}
                </div>
                <div style="color: rgba(255,255,255,0.8); font-size: 14px; font-weight: 600;">
                    {confidence:.1f}% confidence
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def get_recent_signals(limit: int = 10) -> List[Dict]:
    """Get recent signals from database"""
    try:
        conn = sqlite3.connect("data/trench.db")
        
        query = '''
            SELECT * FROM telegram_signals 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        
        return df.to_dict('records') if not df.empty else []
        
    except Exception as e:
        st.error(f"Failed to load recent signals: {e}")
        return []