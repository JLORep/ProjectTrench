#!/usr/bin/env python3
"""
MULTI-PLATFORM SENTIMENT DETECTION SYSTEM
Advanced sentiment analysis across all major crypto platforms
"""
import streamlit as st
import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
import time
import requests
from urllib.parse import quote_plus
import hashlib
import hmac
from textblob import TextBlob
import logging

@dataclass
class SentimentData:
    """Structured sentiment data from any platform"""
    platform: str
    content: str
    timestamp: datetime
    author: str
    sentiment_score: float  # -1 to 1 scale
    confidence: float      # 0 to 1 scale
    engagement: int        # likes, retweets, etc.
    reach: int            # followers, views, etc.
    token_mentions: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    influence_score: float = 0.0
    
    @property
    def sentiment_label(self) -> str:
        if self.sentiment_score >= 0.1:
            return "BULLISH"
        elif self.sentiment_score <= -0.1:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    @property
    def weighted_sentiment(self) -> float:
        """Sentiment weighted by influence and engagement"""
        weight = (self.influence_score + self.engagement/1000 + self.reach/10000) / 3
        return self.sentiment_score * min(weight, 2.0)  # Cap at 2x weight

@dataclass
class PlatformSentimentSummary:
    """Summary of sentiment for a specific token across platforms"""
    token_symbol: str
    total_mentions: int
    avg_sentiment: float
    bullish_count: int
    bearish_count: int
    neutral_count: int
    total_engagement: int
    top_influencers: List[str]
    trending_hashtags: List[str]
    sentiment_momentum: float  # Change over last 24h
    confidence_level: float

class MultiPlatformSentimentMonitor:
    """
    Comprehensive sentiment monitoring across crypto platforms
    """
    
    def __init__(self):
        # Platform configurations
        self.platforms = {
            'twitter': {
                'enabled': True,
                'weight': 0.3,
                'api_calls_per_hour': 500,
                'last_call': None
            },
            'reddit': {
                'enabled': True,
                'weight': 0.2,
                'api_calls_per_hour': 100,
                'last_call': None
            },
            'telegram': {
                'enabled': True,
                'weight': 0.25,
                'api_calls_per_hour': 1000,
                'last_call': None
            },
            'discord': {
                'enabled': True,
                'weight': 0.15,
                'api_calls_per_hour': 300,
                'last_call': None
            },
            'youtube': {
                'enabled': True,
                'weight': 0.1,
                'api_calls_per_hour': 50,
                'last_call': None
            }
        }
        
        # Initialize session state
        if 'sentiment_data' not in st.session_state:
            st.session_state.sentiment_data = []
        if 'sentiment_summaries' not in st.session_state:
            st.session_state.sentiment_summaries = {}
        if 'sentiment_config' not in st.session_state:
            st.session_state.sentiment_config = {
                'update_interval': 300,  # 5 minutes
                'max_posts_per_platform': 100,
                'min_engagement_threshold': 10,
                'track_influencers': True
            }
        
        # Crypto-specific keywords and patterns
        self.crypto_keywords = [
            'memecoin', 'altcoin', 'defi', 'solana', 'ethereum', 'bitcoin',
            'pump', 'dump', 'moon', 'diamond hands', 'paper hands', 'hodl',
            'bullish', 'bearish', 'fud', 'fomo', 'dyor', 'nfa', 'ath', 'btfd'
        ]
        
        # Sentiment analysis patterns
        self.bullish_patterns = [
            r'\b(moon|mooning|bullish|pump|gem|diamond|hold|hodl|buy|accumulate)\b',
            r'\b(to the moon|diamond hands|this is it|huge potential|next 100x)\b',
            r'\b(golden opportunity|perfect entry|loading up|all in)\b'
        ]
        
        self.bearish_patterns = [
            r'\b(dump|crash|bearish|sell|exit|scam|rug|dead|rip)\b',
            r'\b(paper hands|getting out|this is over|red flag|avoid)\b',
            r'\b(ponzi|scam coin|exit liquidity|dump incoming)\b'
        ]
    
    def extract_token_mentions(self, text: str) -> List[str]:
        """Extract cryptocurrency token mentions from text"""
        # Look for $TOKEN pattern
        token_pattern = r'\$([A-Z]{3,10})\b'
        tokens = re.findall(token_pattern, text.upper())
        
        # Look for common token names
        common_tokens = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'AVAX', 'MATIC', 'LINK']
        for token in common_tokens:
            if token.lower() in text.lower():
                tokens.append(token)
        
        return list(set(tokens))
    
    def analyze_sentiment(self, text: str) -> Tuple[float, float]:
        """Analyze sentiment of text content"""
        # Basic TextBlob sentiment
        blob = TextBlob(text)
        base_sentiment = blob.sentiment.polarity
        confidence = blob.sentiment.subjectivity
        
        # Crypto-specific pattern matching
        bullish_matches = sum(len(re.findall(pattern, text.lower())) for pattern in self.bullish_patterns)
        bearish_matches = sum(len(re.findall(pattern, text.lower())) for pattern in self.bearish_patterns)
        
        # Combine scores
        pattern_sentiment = 0
        if bullish_matches > bearish_matches:
            pattern_sentiment = min(bullish_matches * 0.2, 0.8)
        elif bearish_matches > bullish_matches:
            pattern_sentiment = -min(bearish_matches * 0.2, 0.8)
        
        # Weighted combination
        final_sentiment = (base_sentiment * 0.6) + (pattern_sentiment * 0.4)
        final_confidence = min(confidence + (abs(pattern_sentiment) * 0.3), 1.0)
        
        return final_sentiment, final_confidence
    
    async def fetch_twitter_sentiment(self, query: str, max_results: int = 100) -> List[SentimentData]:
        """Fetch sentiment data from Twitter (simulated - would need Twitter API v2)"""
        # Simulate Twitter data for demonstration
        await asyncio.sleep(0.1)  # Simulate API delay
        
        sentiments = []
        for i in range(min(max_results, 20)):  # Simulate 20 tweets
            # Generate realistic tweet content
            tweet_templates = [
                f"Just bought more ${query}! This is going to moon 🚀",
                f"${query} looks like it's forming a bullish pattern",
                f"Not sure about ${query}, seems like a risky play",
                f"${query} to the moon! Diamond hands 💎🙌",
                f"Thinking of selling my ${query} bag, thoughts?",
                f"${query} community is growing fast, bullish!",
                f"Technical analysis shows ${query} ready for breakout",
                f"${query} fundamentals look strong, accumulating"
            ]
            
            content = np.random.choice(tweet_templates)
            sentiment_score, confidence = self.analyze_sentiment(content)
            
            sentiment = SentimentData(
                platform="twitter",
                content=content,
                timestamp=datetime.now() - timedelta(minutes=np.random.randint(1, 1440)),
                author=f"user_{i}",
                sentiment_score=sentiment_score,
                confidence=confidence,
                engagement=np.random.randint(1, 500),
                reach=np.random.randint(100, 10000),
                token_mentions=[query],
                hashtags=[f"#{query}", "#crypto", "#altcoin"],
                influence_score=np.random.uniform(0.1, 0.9)
            )
            sentiments.append(sentiment)
        
        return sentiments
    
    async def fetch_reddit_sentiment(self, query: str, max_results: int = 50) -> List[SentimentData]:
        """Fetch sentiment data from Reddit (simulated)"""
        await asyncio.sleep(0.2)
        
        sentiments = []
        for i in range(min(max_results, 15)):
            post_templates = [
                f"DD: Why ${query} is undervalued and ready to pump",
                f"Thoughts on ${query}? Seems like a solid project",
                f"${query} price prediction for end of year?",
                f"Warning: ${query} showing some red flags",
                f"Just discovered ${query}, what's the community think?",
                f"${query} technical analysis - bullish divergence forming",
                f"Should I FOMO into ${query} or wait for dip?"
            ]
            
            content = np.random.choice(post_templates)
            sentiment_score, confidence = self.analyze_sentiment(content)
            
            sentiment = SentimentData(
                platform="reddit",
                content=content,
                timestamp=datetime.now() - timedelta(minutes=np.random.randint(1, 2880)),
                author=f"redditor_{i}",
                sentiment_score=sentiment_score,
                confidence=confidence,
                engagement=np.random.randint(5, 200),
                reach=np.random.randint(1000, 50000),
                token_mentions=[query],
                hashtags=[],
                influence_score=np.random.uniform(0.2, 0.8)
            )
            sentiments.append(sentiment)
        
        return sentiments
    
    async def fetch_telegram_sentiment(self, query: str, max_results: int = 200) -> List[SentimentData]:
        """Fetch sentiment data from Telegram (simulated)"""
        await asyncio.sleep(0.05)
        
        sentiments = []
        for i in range(min(max_results, 30)):
            message_templates = [
                f"${query} signal: BUY NOW! Target: +50%",
                f"Alert: ${query} volume spike detected",
                f"${query} looking weak, might dump soon",
                f"Gem found: ${query} - low cap, high potential",
                f"${query} breaking resistance, moon mission started",
                f"Caution on ${query}, whale movements detected",
                f"${query} community update: major partnership coming"
            ]
            
            content = np.random.choice(message_templates)
            sentiment_score, confidence = self.analyze_sentiment(content)
            
            sentiment = SentimentData(
                platform="telegram",
                content=content,
                timestamp=datetime.now() - timedelta(minutes=np.random.randint(1, 720)),
                author=f"tg_user_{i}",
                sentiment_score=sentiment_score,
                confidence=confidence,
                engagement=np.random.randint(1, 100),
                reach=np.random.randint(500, 5000),
                token_mentions=[query],
                hashtags=[],
                influence_score=np.random.uniform(0.3, 1.0)
            )
            sentiments.append(sentiment)
        
        return sentiments
    
    async def fetch_discord_sentiment(self, query: str, max_results: int = 75) -> List[SentimentData]:
        """Fetch sentiment data from Discord (simulated)"""
        await asyncio.sleep(0.1)
        
        sentiments = []
        for i in range(min(max_results, 20)):
            message_templates = [
                f"Anyone else bullish on ${query}? Chart looks ready",
                f"${query} dev team seems legit, good tokenomics",
                f"Sold my ${query} bag, didn't feel right",
                f"${query} community is solid, holding long term",
                f"Quick flip on ${query} or longer hold?",
                f"${query} partnerships looking promising",
                f"Risk assessment on ${query}? Thinking of entering"
            ]
            
            content = np.random.choice(message_templates)
            sentiment_score, confidence = self.analyze_sentiment(content)
            
            sentiment = SentimentData(
                platform="discord",
                content=content,
                timestamp=datetime.now() - timedelta(minutes=np.random.randint(1, 480)),
                author=f"discord_user_{i}",
                sentiment_score=sentiment_score,
                confidence=confidence,
                engagement=np.random.randint(1, 50),
                reach=np.random.randint(200, 2000),
                token_mentions=[query],
                hashtags=[],
                influence_score=np.random.uniform(0.2, 0.7)
            )
            sentiments.append(sentiment)
        
        return sentiments
    
    async def fetch_youtube_sentiment(self, query: str, max_results: int = 25) -> List[SentimentData]:
        """Fetch sentiment data from YouTube (simulated)"""
        await asyncio.sleep(0.3)
        
        sentiments = []
        for i in range(min(max_results, 10)):
            video_templates = [
                f"${query} Price Prediction: 100x Potential? (FULL ANALYSIS)",
                f"Why ${query} Could Be The Next Big Thing in Crypto",
                f"${query} Review: Scam or Gem? My Honest Opinion",
                f"Technical Analysis: ${query} Ready for Breakout?",
                f"${query} News Update: Major Developments Coming",
                f"Should You Buy ${query} Now? Risk vs Reward Analysis"
            ]
            
            content = np.random.choice(video_templates)
            sentiment_score, confidence = self.analyze_sentiment(content)
            
            sentiment = SentimentData(
                platform="youtube",
                content=content,
                timestamp=datetime.now() - timedelta(hours=np.random.randint(1, 168)),
                author=f"crypto_youtuber_{i}",
                sentiment_score=sentiment_score,
                confidence=confidence,
                engagement=np.random.randint(50, 5000),
                reach=np.random.randint(10000, 500000),
                token_mentions=[query],
                hashtags=[],
                influence_score=np.random.uniform(0.5, 1.0)
            )
            sentiments.append(sentiment)
        
        return sentiments
    
    async def fetch_all_platform_sentiment(self, token_symbol: str) -> List[SentimentData]:
        """Fetch sentiment data from all enabled platforms"""
        all_sentiments = []
        tasks = []
        
        if self.platforms['twitter']['enabled']:
            tasks.append(self.fetch_twitter_sentiment(token_symbol))
        
        if self.platforms['reddit']['enabled']:
            tasks.append(self.fetch_reddit_sentiment(token_symbol))
        
        if self.platforms['telegram']['enabled']:
            tasks.append(self.fetch_telegram_sentiment(token_symbol))
        
        if self.platforms['discord']['enabled']:
            tasks.append(self.fetch_discord_sentiment(token_symbol))
        
        if self.platforms['youtube']['enabled']:
            tasks.append(self.fetch_youtube_sentiment(token_symbol))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_sentiments.extend(result)
        
        return all_sentiments
    
    def calculate_sentiment_summary(self, sentiments: List[SentimentData], token_symbol: str) -> PlatformSentimentSummary:
        """Calculate comprehensive sentiment summary for a token"""
        if not sentiments:
            return PlatformSentimentSummary(
                token_symbol=token_symbol,
                total_mentions=0,
                avg_sentiment=0.0,
                bullish_count=0,
                bearish_count=0,
                neutral_count=0,
                total_engagement=0,
                top_influencers=[],
                trending_hashtags=[],
                sentiment_momentum=0.0,
                confidence_level=0.0
            )
        
        # Basic metrics
        total_mentions = len(sentiments)
        avg_sentiment = np.mean([s.weighted_sentiment for s in sentiments])
        total_engagement = sum(s.engagement for s in sentiments)
        
        # Sentiment distribution
        bullish_count = sum(1 for s in sentiments if s.sentiment_label == "BULLISH")
        bearish_count = sum(1 for s in sentiments if s.sentiment_label == "BEARISH")
        neutral_count = sum(1 for s in sentiments if s.sentiment_label == "NEUTRAL")
        
        # Top influencers (by influence score and engagement)
        sorted_by_influence = sorted(sentiments, key=lambda x: x.influence_score * x.engagement, reverse=True)
        top_influencers = [s.author for s in sorted_by_influence[:5]]
        
        # Trending hashtags
        all_hashtags = []
        for s in sentiments:
            all_hashtags.extend(s.hashtags)
        hashtag_counts = {}
        for tag in all_hashtags:
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        trending_hashtags = sorted(hashtag_counts.keys(), key=hashtag_counts.get, reverse=True)[:5]
        
        # Sentiment momentum (change over last 24h)
        recent_sentiments = [s for s in sentiments if (datetime.now() - s.timestamp).total_seconds() < 24*3600]
        older_sentiments = [s for s in sentiments if (datetime.now() - s.timestamp).total_seconds() >= 24*3600]
        
        recent_avg = np.mean([s.weighted_sentiment for s in recent_sentiments]) if recent_sentiments else 0
        older_avg = np.mean([s.weighted_sentiment for s in older_sentiments]) if older_sentiments else 0
        sentiment_momentum = recent_avg - older_avg
        
        # Confidence level based on volume and consistency
        confidence_level = min(
            (total_mentions / 100) * 0.5 +  # Volume factor
            (1 - np.std([s.sentiment_score for s in sentiments])) * 0.5,  # Consistency factor
            1.0
        )
        
        return PlatformSentimentSummary(
            token_symbol=token_symbol,
            total_mentions=total_mentions,
            avg_sentiment=avg_sentiment,
            bullish_count=bullish_count,
            bearish_count=bearish_count,
            neutral_count=neutral_count,
            total_engagement=total_engagement,
            top_influencers=top_influencers,
            trending_hashtags=trending_hashtags,
            sentiment_momentum=sentiment_momentum,
            confidence_level=confidence_level
        )
    
    def render_sentiment_dashboard(self):
        """Render the main sentiment analysis dashboard"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                    border: 2px solid #8b5cf6;">
            <h1 style="color: #8b5cf6; margin: 0;">📊 Multi-Platform Sentiment Analysis</h1>
            <p style="color: #d1d5db; margin: 0.5rem 0 0 0;">
                Real-time sentiment tracking across Twitter, Reddit, Telegram, Discord & YouTube
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Platform status overview
        col1, col2, col3, col4, col5 = st.columns(5)
        
        platform_colors = {
            'twitter': '#1DA1F2',
            'reddit': '#FF4500', 
            'telegram': '#0088CC',
            'discord': '#7289DA',
            'youtube': '#FF0000'
        }
        
        for i, (platform, config) in enumerate(self.platforms.items()):
            col = [col1, col2, col3, col4, col5][i]
            status = "🟢 ACTIVE" if config['enabled'] else "🔴 DISABLED"
            color = platform_colors.get(platform, '#9ca3af')
            
            with col:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: {color}20; 
                           border-radius: 8px; border: 1px solid {color};">
                    <h4 style="margin: 0; color: {color};">{platform.title()}</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #d1d5db; font-size: 0.8rem;">{status}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Token analysis input
        st.subheader("🔍 Token Sentiment Analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            token_symbol = st.text_input(
                "Enter Token Symbol (e.g., SOL, BTC, ETH)",
                placeholder="SOL",
                help="Enter the cryptocurrency symbol to analyze sentiment"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📊 Analyze Sentiment", type="primary"):
                if token_symbol:
                    self.run_sentiment_analysis(token_symbol.upper())
        
        # Display results if available
        if st.session_state.sentiment_summaries:
            self.render_sentiment_results()
    
    def run_sentiment_analysis(self, token_symbol: str):
        """Run comprehensive sentiment analysis for a token"""
        with st.spinner(f"Analyzing sentiment for ${token_symbol} across all platforms..."):
            # Simulate the async call (in real implementation, would use asyncio.run)
            # For demo purposes, we'll generate data directly
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate fetching from each platform
            all_sentiments = []
            platforms = ['Twitter', 'Reddit', 'Telegram', 'Discord', 'YouTube']
            
            for i, platform in enumerate(platforms):
                status_text.text(f'Fetching data from {platform}...')
                progress_bar.progress((i + 1) / len(platforms))
                
                # Generate sample data for each platform
                if platform.lower() == 'twitter':
                    sentiments = asyncio.run(self.fetch_twitter_sentiment(token_symbol))
                elif platform.lower() == 'reddit':
                    sentiments = asyncio.run(self.fetch_reddit_sentiment(token_symbol))
                elif platform.lower() == 'telegram':
                    sentiments = asyncio.run(self.fetch_telegram_sentiment(token_symbol))
                elif platform.lower() == 'discord':
                    sentiments = asyncio.run(self.fetch_discord_sentiment(token_symbol))
                elif platform.lower() == 'youtube':
                    sentiments = asyncio.run(self.fetch_youtube_sentiment(token_symbol))
                
                all_sentiments.extend(sentiments)
                time.sleep(0.5)  # Simulate processing time
            
            # Calculate summary
            summary = self.calculate_sentiment_summary(all_sentiments, token_symbol)
            
            # Store results
            st.session_state.sentiment_data = all_sentiments
            st.session_state.sentiment_summaries[token_symbol] = summary
            
            status_text.text('Analysis complete!')
            progress_bar.progress(1.0)
            
            st.success(f"✅ Sentiment analysis complete for ${token_symbol}!")
            time.sleep(1)
            st.rerun()
    
    def render_sentiment_results(self):
        """Render sentiment analysis results"""
        st.subheader("📈 Sentiment Analysis Results")
        
        # Display summary for each analyzed token
        for token_symbol, summary in st.session_state.sentiment_summaries.items():
            self.render_token_sentiment_summary(summary)
    
    def render_token_sentiment_summary(self, summary: PlatformSentimentSummary):
        """Render detailed sentiment summary for a specific token"""
        
        # Header with token info
        sentiment_color = "#10b981" if summary.avg_sentiment > 0.1 else "#ef4444" if summary.avg_sentiment < -0.1 else "#f59e0b"
        momentum_arrow = "📈" if summary.sentiment_momentum > 0 else "📉" if summary.sentiment_momentum < 0 else "➡️"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                   padding: 2rem; border-radius: 16px; margin: 1rem 0; 
                   border-left: 4px solid {sentiment_color};">
            <h2 style="color: {sentiment_color}; margin: 0;">${summary.token_symbol} Sentiment Analysis</h2>
            <p style="color: #d1d5db; margin: 0.5rem 0 0 0;">
                {momentum_arrow} Overall Sentiment: <strong>{summary.avg_sentiment:+.2f}</strong> 
                | Confidence: <strong>{summary.confidence_level:.1%}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Mentions", f"{summary.total_mentions:,}")
        
        with col2:
            st.metric("Bullish Posts", summary.bullish_count, 
                     delta=f"{(summary.bullish_count/summary.total_mentions)*100:.1f}%")
        
        with col3:
            st.metric("Bearish Posts", summary.bearish_count,
                     delta=f"{(summary.bearish_count/summary.total_mentions)*100:.1f}%")
        
        with col4:
            st.metric("Total Engagement", f"{summary.total_engagement:,}")
        
        with col5:
            momentum_delta = f"{summary.sentiment_momentum:+.2f}" if summary.sentiment_momentum != 0 else "No change"
            st.metric("24h Momentum", f"{summary.avg_sentiment:+.2f}", delta=momentum_delta)
        
        # Platform breakdown
        st.subheader(f"📊 Platform Breakdown for ${summary.token_symbol}")
        
        # Get platform-specific data
        platform_data = {}
        for sentiment in st.session_state.sentiment_data:
            if summary.token_symbol in sentiment.token_mentions:
                platform = sentiment.platform
                if platform not in platform_data:
                    platform_data[platform] = []
                platform_data[platform].append(sentiment)
        
        # Create platform comparison
        platform_comparison = []
        for platform, sentiments in platform_data.items():
            avg_sentiment = np.mean([s.sentiment_score for s in sentiments])
            total_engagement = sum(s.engagement for s in sentiments)
            mention_count = len(sentiments)
            
            platform_comparison.append({
                'Platform': platform.title(),
                'Mentions': mention_count,
                'Avg Sentiment': f"{avg_sentiment:+.2f}",
                'Total Engagement': f"{total_engagement:,}",
                'Sentiment Label': "BULLISH" if avg_sentiment > 0.1 else "BEARISH" if avg_sentiment < -0.1 else "NEUTRAL"
            })
        
        if platform_comparison:
            df = pd.DataFrame(platform_comparison)
            st.dataframe(df, use_container_width=True)
        
        # Top influencers and trending hashtags
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🌟 Top Influencers**")
            for i, influencer in enumerate(summary.top_influencers[:5]):
                st.write(f"{i+1}. {influencer}")
        
        with col2:
            st.markdown("**📱 Trending Hashtags**")
            for i, hashtag in enumerate(summary.trending_hashtags[:5]):
                st.write(f"{i+1}. {hashtag}")
        
        # Recent sentiment timeline (sample data)
        st.subheader("📈 Sentiment Timeline (Last 24h)")
        
        # Generate sample timeline data
        timeline_data = []
        for i in range(24):
            hour = datetime.now() - timedelta(hours=23-i)
            # Simulate sentiment for each hour
            hourly_sentiments = [s for s in st.session_state.sentiment_data 
                               if summary.token_symbol in s.token_mentions and 
                               abs((s.timestamp - hour).total_seconds()) < 1800]  # Within 30 min
            
            if hourly_sentiments:
                avg_sentiment = np.mean([s.sentiment_score for s in hourly_sentiments])
            else:
                avg_sentiment = np.random.normal(summary.avg_sentiment, 0.1)  # Simulate based on overall sentiment
            
            timeline_data.append({
                'Hour': hour.strftime('%H:00'),
                'Sentiment': avg_sentiment,
                'Mentions': len(hourly_sentiments)
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create timeline chart
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Sentiment line
        fig.add_trace(
            go.Scatter(
                x=timeline_df['Hour'],
                y=timeline_df['Sentiment'],
                mode='lines+markers',
                name='Sentiment Score',
                line=dict(color=sentiment_color, width=3)
            ),
            secondary_y=False
        )
        
        # Mentions bar
        fig.add_trace(
            go.Bar(
                x=timeline_df['Hour'],
                y=timeline_df['Mentions'],
                name='Mentions',
                opacity=0.3,
                marker_color='#8b5cf6'
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title=f"${summary.token_symbol} Sentiment Timeline",
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        fig.update_yaxes(title_text="Sentiment Score", secondary_y=False)
        fig.update_yaxes(title_text="Mentions Count", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)

def render_sentiment_analysis_interface():
    """Main function to render the sentiment analysis interface"""
    monitor = MultiPlatformSentimentMonitor()
    monitor.render_sentiment_dashboard()

if __name__ == "__main__":
    render_sentiment_analysis_interface()