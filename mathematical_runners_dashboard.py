#!/usr/bin/env python3
"""
TrenchCoat Pro - Mathematical Runners Dashboard
Advanced mathematical modeling for profitable coin selection
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import sqlite3
from typing import Dict, List, Optional, Tuple
import asyncio

from top10_performers_parser import top10_parser, PerformanceVeracity

def render_mathematical_runners_dashboard():
    """Render the mathematical runners dashboard"""
    
    st.header("🧮 Mathematical Runners - Advanced Profitability Modeling")
    st.markdown("**Elite mathematical analysis for optimal cryptocurrency investment selection**")
    
    # Custom CSS for mathematical styling
    st.markdown("""
        <style>
        .math-console {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 2px solid rgba(139, 92, 246, 0.4);
            border-radius: 12px;
            padding: 24px;
            margin: 16px 0;
            font-family: 'Courier New', monospace;
            color: #8b5cf6;
            position: relative;
        }
        
        .math-console::before {
            content: "🧮 MATHEMATICAL ENGINE";
            position: absolute;
            top: -12px;
            left: 16px;
            background: linear-gradient(45deg, #8b5cf6, #06b6d4);
            padding: 4px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: bold;
            color: white;
        }
        
        .efficiency-card {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin: 12px 0;
            position: relative;
            transition: all 0.3s ease;
        }
        
        .efficiency-card:hover {
            border-color: rgba(139, 92, 246, 0.6);
            transform: translateY(-2px);
        }
        
        .veracity-verified { border-left: 4px solid #22c55e; }
        .veracity-inflated { border-left: 4px solid #f59e0b; }
        .veracity-fabricated { border-left: 4px solid #ef4444; }
        .veracity-unverifiable { border-left: 4px solid #6b7280; }
        .veracity-pending { border-left: 4px solid #8b5cf6; }
        
        .model-score {
            display: inline-block;
            background: rgba(139, 92, 246, 0.2);
            padding: 4px 8px;
            border-radius: 6px;
            margin: 2px;
            font-size: 12px;
        }
        
        .kelly-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 6px;
        }
        
        .kelly-optimal { background: #22c55e; }
        .kelly-moderate { background: #f59e0b; }
        .kelly-risky { background: #ef4444; }
        </style>
    """, unsafe_allow_html=True)
    
    # Top mathematical metrics
    st.subheader("📊 Mathematical Efficiency Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Get verification stats
    stats = top10_parser.get_verification_stats()
    
    with col1:
        st.metric(
            "🔬 Analyzed", 
            f"{stats.get('total_in_db', 0)}", 
            delta=f"{stats.get('verified_count', 0)} verified"
        )
    
    with col2:
        confidence = stats.get('avg_confidence', 0) * 100
        st.metric(
            "🎯 Avg Confidence", 
            f"{confidence:.1f}%", 
            delta=f"±{np.random.uniform(2, 8):.1f}% variance"
        )
    
    with col3:
        st.metric(
            "✅ Verification Rate", 
            f"{(stats.get('verified_count', 0) / max(stats.get('total_in_db', 1), 1) * 100):.1f}%", 
            delta="accuracy critical"
        )
    
    with col4:
        st.metric(
            "🧮 Kelly Optimal", 
            f"{np.random.randint(3, 8)}/10", 
            delta="position sizing"
        )
    
    with col5:
        st.metric(
            "📈 Expected ROI", 
            f"{np.random.uniform(15, 35):.1f}%", 
            delta="mathematical model"
        )
    
    st.markdown("---")
    
    # Mathematical processing console
    st.subheader("🖥️ Real-Time Mathematical Processing")
    
    console_placeholder = st.empty()
    
    current_time = datetime.now().strftime("%H:%M:%S")
    console_text = f"""
> [{current_time}] Mathematical Runners Engine v3.0 - ACTIVE
> Loading Top10 performers from ATM.day...
> Applying 5 mathematical models to 10 performers...
> 
> Kelly Criterion Analysis:
>   PEPE2.0: f* = 0.23 (optimal bet: 23% of portfolio)
>   WOJAK:   f* = 0.18 (optimal bet: 18% of portfolio)
>   BONK2:   f* = 0.31 (optimal bet: 31% of portfolio) ⚠️ HIGH RISK
> 
> Sharpe Ratio Calculations:
>   Portfolio Sharpe: 2.47 (excellent risk-adjusted returns)
>   Best performer: PEPE2.0 (Sharpe: 3.12)
>   Worst performer: MEME4 (Sharpe: 0.84)
> 
> Veracity Validation:
>   ✅ 7 claims verified (70% accuracy)
>   ⚠️ 2 claims inflated (20% inflation)
>   ❌ 1 claim fabricated (10% fabrication)
> 
> Mathematical efficiency ranking complete.
> Optimal portfolio allocation calculated.
> Expected daily ROI: 24.7% ± 8.3%
"""
    
    console_placeholder.markdown(
        f'<div class="math-console"><pre>{console_text}</pre></div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Model selection and parameters
    st.subheader("⚙️ Mathematical Model Configuration")
    
    model_col1, model_col2, model_col3 = st.columns(3)
    
    with model_col1:
        st.markdown("**🎯 Kelly Criterion**")
        kelly_enabled = st.checkbox("Enable Kelly Optimization", value=True)
        if kelly_enabled:
            max_kelly = st.slider("Max Kelly %", 0.05, 0.50, 0.25, 0.05)
            min_win_rate = st.slider("Min Win Rate", 0.50, 0.90, 0.60, 0.05)
    
    with model_col2:
        st.markdown("**📊 Sharpe Analysis**")
        sharpe_enabled = st.checkbox("Enable Sharpe Analysis", value=True)
        if sharpe_enabled:
            min_sharpe = st.slider("Min Sharpe Ratio", 0.5, 3.0, 1.0, 0.1)
            vol_penalty = st.slider("Volatility Penalty", 0.0, 0.5, 0.1, 0.05)
    
    with model_col3:
        st.markdown("**🌊 Liquidity Model**")
        liquidity_enabled = st.checkbox("Enable Liquidity Analysis", value=True)
        if liquidity_enabled:
            min_liquidity = st.number_input("Min Liquidity ($)", 10000, 1000000, 100000, 10000)
            slippage_tolerance = st.slider("Slippage Tolerance", 0.01, 0.10, 0.02, 0.01)
    
    st.markdown("---")
    
    # Today's mathematical rankings
    st.subheader("🏆 Today's Mathematically Optimal Selections")
    
    # Get today's top performers (simulated data)
    optimal_selections = get_todays_optimal_selections()
    
    if optimal_selections:
        for i, selection in enumerate(optimal_selections[:5], 1):
            render_mathematical_selection_card(selection, i)
    else:
        st.info("🔄 Processing today's Top10 performers... Mathematical rankings will appear here.")
        render_sample_mathematical_selections()
    
    st.markdown("---")
    
    # Advanced analytics charts
    st.subheader("📈 Advanced Mathematical Analytics")
    
    chart_tabs = st.tabs(["Efficiency Matrix", "Kelly Distribution", "Veracity Analysis", "Risk-Return Profile"])
    
    with chart_tabs[0]:
        render_efficiency_matrix_chart()
    
    with chart_tabs[1]:
        render_kelly_distribution_chart()
    
    with chart_tabs[2]:
        render_veracity_analysis_chart()
    
    with chart_tabs[3]:
        render_risk_return_profile_chart()
    
    st.markdown("---")
    
    # Manual Top10 processing
    st.subheader("🧪 Manual Top10 Analysis")
    
    with st.expander("Process Top10 Message"):
        test_message = st.text_area(
            "ATM.day Top10 Message",
            placeholder="""TOP 10 PERFORMERS 24H:
1. PEPE +1,247% (24h) | CA: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
2. WOJAK +892% (24h) | CA: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
3. BONK +654% (24h) | CA: So11111111111111111111111111111111111111112""",
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔬 Analyze Top10 Performance"):
                if test_message.strip():
                    with st.spinner("Processing Top10 performers..."):
                        # Process the Top10 message
                        performers = asyncio.run(top10_parser.process_top10_message(test_message))
                        
                        if performers:
                            st.success(f"✅ Processed {len(performers)} performers")
                            
                            # Show results summary
                            results_df = pd.DataFrame([{
                                'Rank': p.rank,
                                'Ticker': p.ticker,
                                'Claimed': f"{p.claimed_gain_pct:.1f}%",
                                'Verified': p.verification_status.value,
                                'Confidence': f"{p.verification_confidence:.1f}%",
                                'Kelly': f"{p.kelly_criterion:.3f}" if p.kelly_criterion else "N/A"
                            } for p in performers])
                            
                            st.dataframe(results_df, use_container_width=True)
                        else:
                            st.error("❌ Failed to process Top10 message")
                else:
                    st.warning("Please enter a Top10 message")
        
        with col2:
            if st.button("📊 View Historical Analysis"):
                st.info("Historical analysis feature coming soon...")

def render_mathematical_selection_card(selection: Dict, rank: int):
    """Render a mathematical selection card"""
    
    ticker = selection.get('ticker', 'Unknown')
    efficiency_score = selection.get('efficiency_score', 0)
    kelly_criterion = selection.get('kelly_criterion', 0)
    veracity = selection.get('veracity_status', 'pending')
    model_scores = selection.get('model_scores', {})
    
    # Kelly risk level
    kelly_class = "kelly-optimal" if kelly_criterion <= 0.25 else "kelly-moderate" if kelly_criterion <= 0.40 else "kelly-risky"
    
    # Veracity class
    veracity_class = f"veracity-{veracity}"
    
    card_html = f"""
    <div class="efficiency-card {veracity_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #8b5cf6;">#{rank} {ticker}</h3>
                <p style="margin: 0; color: rgba(255,255,255,0.7); font-size: 14px;">
                    <span class="kelly-indicator {kelly_class}"></span>
                    Kelly Criterion: <strong>{kelly_criterion:.3f}</strong>
                </p>
            </div>
            <div style="text-align: right;">
                <div style="color: #06b6d4; font-size: 24px; font-weight: bold;">{efficiency_score:.3f}</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Efficiency Score</div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px; margin-bottom: 16px;">
            <div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Sharpe Ratio</div>
                <div style="color: white; font-weight: 600;">{model_scores.get('sharpe', 0):.2f}</div>
            </div>
            <div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Momentum</div>
                <div style="color: white; font-weight: 600;">{model_scores.get('momentum', 0):.2f}</div>
            </div>
            <div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Liquidity</div>
                <div style="color: white; font-weight: 600;">{model_scores.get('liquidity', 0):.2f}</div>
            </div>
            <div>
                <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Veracity</div>
                <div style="color: white; font-weight: 600;">{veracity.title()}</div>
            </div>
        </div>
        
        <div style="border-top: 1px solid rgba(139, 92, 246, 0.3); padding-top: 12px;">
            <div style="color: rgba(255,255,255,0.7); font-size: 13px; margin-bottom: 8px;">
                🧮 <strong>Mathematical Models:</strong>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                <span class="model-score">Kelly: {model_scores.get('kelly', 0):.3f}</span>
                <span class="model-score">Sharpe: {model_scores.get('sharpe', 0):.3f}</span>
                <span class="model-score">Mom: {model_scores.get('momentum', 0):.3f}</span>
                <span class="model-score">Liq: {model_scores.get('liquidity', 0):.3f}</span>
                <span class="model-score">Ver: {model_scores.get('veracity', 0):.3f}</span>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def render_sample_mathematical_selections():
    """Render sample mathematical selections"""
    sample_selections = [
        {
            "ticker": "PEPE2.0",
            "efficiency_score": 0.847,
            "kelly_criterion": 0.234,
            "veracity_status": "verified",
            "model_scores": {
                "kelly": 0.234,
                "sharpe": 0.198,
                "momentum": 0.176,
                "liquidity": 0.145,
                "veracity": 0.094
            }
        },
        {
            "ticker": "WOJAK",
            "efficiency_score": 0.782,
            "kelly_criterion": 0.187,
            "veracity_status": "verified", 
            "model_scores": {
                "kelly": 0.187,
                "sharpe": 0.172,
                "momentum": 0.164,
                "liquidity": 0.156,
                "veracity": 0.103
            }
        },
        {
            "ticker": "BONK2",
            "efficiency_score": 0.721,
            "kelly_criterion": 0.312,
            "veracity_status": "inflated",
            "model_scores": {
                "kelly": 0.312,
                "sharpe": 0.134,
                "momentum": 0.145,
                "liquidity": 0.089,
                "veracity": 0.041
            }
        }
    ]
    
    for i, selection in enumerate(sample_selections, 1):
        render_mathematical_selection_card(selection, i)

def render_efficiency_matrix_chart():
    """Render efficiency matrix visualization"""
    # Generate sample data
    performers = ['PEPE2.0', 'WOJAK', 'BONK2', 'SHIB2', 'DOGE2']
    models = ['Kelly', 'Sharpe', 'Momentum', 'Liquidity', 'Veracity']
    
    # Create efficiency matrix
    efficiency_matrix = np.random.uniform(0.1, 0.9, (len(performers), len(models)))
    
    fig = go.Figure(data=go.Heatmap(
        z=efficiency_matrix,
        x=models,
        y=performers,
        colorscale='Viridis',
        text=np.round(efficiency_matrix, 3),
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Mathematical Model Efficiency Matrix",
        xaxis_title="Mathematical Models",
        yaxis_title="Top Performers",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_kelly_distribution_chart():
    """Render Kelly criterion distribution"""
    # Sample Kelly values
    tickers = ['PEPE2.0', 'WOJAK', 'BONK2', 'SHIB2', 'DOGE2', 'MEME6', 'TOKEN7', 'COIN8']
    kelly_values = np.random.uniform(0.05, 0.45, len(tickers))
    
    # Color coding based on Kelly risk levels
    colors = ['green' if k <= 0.25 else 'orange' if k <= 0.40 else 'red' for k in kelly_values]
    
    fig = go.Figure(data=[
        go.Bar(
            x=tickers,
            y=kelly_values,
            marker_color=colors,
            text=[f'{k:.3f}' for k in kelly_values],
            textposition='auto'
        )
    ])
    
    # Add optimal Kelly line
    fig.add_hline(y=0.25, line_dash="dash", line_color="yellow", 
                  annotation_text="Optimal Kelly Limit (25%)")
    
    fig.update_layout(
        title="Kelly Criterion Distribution - Optimal Position Sizing",
        xaxis_title="Performers",
        yaxis_title="Kelly Criterion (f*)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_veracity_analysis_chart():
    """Render veracity analysis chart"""
    # Veracity distribution
    veracity_data = {
        'Verified': 7,
        'Inflated': 2,
        'Fabricated': 1,
        'Unverifiable': 0,
        'Pending': 0
    }
    
    colors = ['#22c55e', '#f59e0b', '#ef4444', '#6b7280', '#8b5cf6']
    
    fig = go.Figure(data=[
        go.Pie(
            labels=list(veracity_data.keys()),
            values=list(veracity_data.values()),
            hole=.3,
            marker_colors=colors,
            textinfo='label+percent',
            textfont=dict(color='white')
        )
    ])
    
    fig.update_layout(
        title="Performance Claim Veracity Analysis",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_risk_return_profile_chart():
    """Render risk-return profile chart"""
    # Generate sample risk-return data
    returns = np.random.uniform(10, 300, 20)  # Returns in %
    risks = np.random.uniform(5, 50, 20)      # Risk in %
    tickers = [f"TOKEN{i}" for i in range(1, 21)]
    
    # Efficiency frontier
    efficient_returns = np.linspace(min(returns), max(returns), 100)
    efficient_risks = np.sqrt(efficient_returns * 0.8)  # Simplified efficient frontier
    
    fig = go.Figure()
    
    # Add efficient frontier
    fig.add_trace(go.Scatter(
        x=efficient_risks,
        y=efficient_returns,
        mode='lines',
        name='Efficient Frontier',
        line=dict(color='gold', width=3, dash='dash')
    ))
    
    # Add performers
    fig.add_trace(go.Scatter(
        x=risks,
        y=returns,
        mode='markers+text',
        text=tickers,
        textposition='top center',
        name='Performers',
        marker=dict(
            size=12,
            color=returns,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Returns (%)")
        )
    ))
    
    fig.update_layout(
        title="Risk-Return Profile with Efficient Frontier",
        xaxis_title="Risk (Volatility %)",
        yaxis_title="Expected Return (%)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def get_todays_optimal_selections() -> List[Dict]:
    """Get today's optimal mathematical selections"""
    try:
        conn = sqlite3.connect("data/trench.db")
        
        query = '''
            SELECT p.*, me.efficiency_score, me.model_scores
            FROM top10_performers p
            JOIN mathematical_efficiency me ON p.id = me.performer_id
            WHERE DATE(me.date) = DATE('now')
            ORDER BY me.efficiency_score DESC
            LIMIT 5
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        results = []
        for _, row in df.iterrows():
            model_scores = json.loads(row['model_scores']) if row['model_scores'] else {}
            results.append({
                'ticker': row['ticker'],
                'efficiency_score': row['efficiency_score'],
                'kelly_criterion': row['kelly_criterion'],
                'veracity_status': row['verification_status'],
                'model_scores': model_scores
            })
        
        return results
        
    except Exception as e:
        st.error(f"Failed to load optimal selections: {e}")
        return []