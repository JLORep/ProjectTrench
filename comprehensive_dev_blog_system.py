#!/usr/bin/env python3
"""
TrenchCoat Pro - Comprehensive Dev Blog System
Integrates all retrospective, webhook, and customer-focused features
WITH Discord rate limit queue management
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import sqlite3
import asyncio
import threading
from contextlib import contextmanager
from enhanced_blog_with_queue import DiscordRateLimitQueue, QueuedMessage, MessagePriority, run_async_safe

# Import all our systems
from integrated_webhook_blog_system import IntegratedWebhookBlogSystem, DevelopmentUpdate
from retrospective_blog_system import RetrospectiveBlogSystem
from customer_focused_retrospective import CustomerFocusedRetrospective
from dev_blog_system import DevBlogSystem

class ThreadSafeDatabaseManager:
    """Thread-safe database connection manager to prevent locking issues"""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.RLock()
    
    @contextmanager
    def get_connection(self):
        """Get a thread-safe database connection"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for concurrent reads
            conn.execute("PRAGMA busy_timeout=10000")  # 10 second timeout
            try:
                yield conn
            finally:
                conn.close()

class ComprehensiveDevBlogSystem:
    """Master system integrating all blog features WITH rate limit queue"""
    
    def __init__(self):
        # Initialize all subsystems
        self.webhook_blog = IntegratedWebhookBlogSystem()
        self.retrospective = RetrospectiveBlogSystem()
        self.customer_focused = CustomerFocusedRetrospective()
        self.original_blog = DevBlogSystem()
        
        # Initialize Discord rate limit queue
        self.discord_queue = DiscordRateLimitQueue()
        self.queue_processor_task = None
        
        # Unified database
        self.db_path = "comprehensive_dev_blog.db"
        self.db_manager = ThreadSafeDatabaseManager(self.db_path)
        self.init_comprehensive_database()
        
        # Discord channel mapping based on the screenshot
        self.discord_channels = {
            # Information Category
            'overview': {'webhook': self.original_blog.discord_webhook_url, 'purpose': 'Project overview and major updates'},
            'dev-blog': {'webhook': self.original_blog.discord_webhook_url, 'purpose': 'Development updates and technical details'},
            'announcements': {'webhook': '[NEEDS_WEBHOOK]', 'purpose': 'Major features and releases'},
            'documentation': {'webhook': '[NEEDS_WEBHOOK]', 'purpose': 'Documentation updates and guides'},
            
            # Development Category
            'bug-reports': {'webhook': self.webhook_blog.webhooks.webhooks.get('bug_fixes'), 'purpose': 'Bug fixes and issue resolutions'},
            'system-updates': {'webhook': '[NEEDS_WEBHOOK]', 'purpose': 'Critical system updates and maintenance'},
            'testing': {'webhook': '[NEEDS_WEBHOOK]', 'purpose': 'Test results and quality assurance'},
            
            # Trading Category
            'signals': {'webhook': '[NEEDS_WEBHOOK]', 'purpose': 'Trading signals and opportunities'},
            'analytics': {'webhook': self.webhook_blog.webhooks.webhooks.get('analytics'), 'purpose': 'Market analysis and insights'},
            'live-trades': {'webhook': self.webhook_blog.webhooks.webhooks.get('live_trades'), 'purpose': 'Real-time trade executions'},
            'performance': {'webhook': self.webhook_blog.webhooks.webhooks.get('performance'), 'purpose': 'Performance metrics and results'}
        }
        
        # Update routing strategy
        self.smart_routing = {
            'feature': ['announcements', 'dev-blog'],
            'bugfix': ['bug-reports', 'dev-blog'],
            'performance': ['performance', 'system-updates'],
            'security': ['system-updates', 'announcements'],
            'analytics': ['analytics', 'dev-blog'],
            'trading': ['live-trades', 'signals'],
            'critical': ['system-updates', 'announcements', 'overview'],
            'documentation': ['documentation', 'dev-blog']
        }
    
    def init_comprehensive_database(self):
        """Initialize comprehensive blog database"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Master posts table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS comprehensive_posts (
                id TEXT PRIMARY KEY,
                post_type TEXT NOT NULL, -- manual, retrospective, customer, automated
                title TEXT NOT NULL,
                version TEXT NOT NULL,
                content_json TEXT NOT NULL, -- Full post content as JSON
                channels_posted TEXT NOT NULL, -- JSON array of channels
                discord_success_rate REAL DEFAULT 0.0,
                git_commits TEXT, -- JSON array of associated commits
                created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_timestamp TIMESTAMP,
                author TEXT DEFAULT 'TrenchCoat Pro Team',
                priority TEXT DEFAULT 'medium',
                customer_impact_score INTEGER DEFAULT 0, -- 0-100
                technical_depth_score INTEGER DEFAULT 0, -- 0-100
                engagement_metrics TEXT -- JSON of likes, views, etc.
            )
            ''')
            
            # Analytics table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                views INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                reactions TEXT, -- JSON of reaction types and counts
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES comprehensive_posts(id)
            )
            ''')
            
            # Scheduled posts
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id TEXT PRIMARY KEY,
                post_content TEXT NOT NULL, -- JSON of full post
                scheduled_time TIMESTAMP NOT NULL,
                channels TEXT NOT NULL, -- JSON array
                status TEXT DEFAULT 'pending', -- pending, published, cancelled
                created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
    
    def render_comprehensive_interface(self):
        """Main Streamlit interface for comprehensive blog system"""
        
        st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-bottom: 2rem;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
            <h1 style='color: white; margin: 0; font-size: 3rem; font-weight: 800;'>
                📰 Comprehensive Dev Blog System
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin-top: 1rem; font-size: 1.3rem;'>
                Unified blogging with retrospective analysis, customer focus, and smart routing
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main navigation tabs
        main_tabs = st.tabs([
            "📝 Create Update",
            "🔄 Retrospective",
            "🎯 Customer Focus",
            "📅 Schedule",
            "📊 Analytics",
            "📡 Queue Monitor",
            "⚙️ Settings"
        ])
        
        with main_tabs[0]:
            self.render_create_update()
        
        with main_tabs[1]:
            self.render_git_retrospective()
        
        with main_tabs[2]:
            self.render_customer_focused()
        
        with main_tabs[3]:
            self.render_scheduling()
        
        with main_tabs[4]:
            self.render_analytics_dashboard()
        
        with main_tabs[5]:
            self.render_queue_monitor()
        
        with main_tabs[6]:
            self.render_settings()
    
    def render_create_update(self):
        """Unified update creation interface"""
        
        st.markdown("### 📝 Create Development Update")
        
        # Update type selection
        col1, col2 = st.columns([3, 1])
        
        with col1:
            update_method = st.radio(
                "Update Creation Method:",
                ["✍️ Manual Entry", "🔄 From Git Commits", "🎯 Customer-Focused", "🤖 AI-Generated"],
                horizontal=True
            )
        
        with col2:
            st.markdown("**Quick Actions:**")
            if st.button("📊 Analyze Recent Commits"):
                self.quick_analyze_commits()
            if st.button("🚀 Generate Weekly Summary"):
                self.generate_weekly_summary()
        
        st.markdown("---")
        
        if update_method == "✍️ Manual Entry":
            self.render_manual_entry()
        elif update_method == "🔄 From Git Commits":
            self.render_git_retrospective()
        elif update_method == "🎯 Customer-Focused":
            self.render_customer_creation()
        else:  # AI-Generated
            self.render_ai_generation()
    
    def render_manual_entry(self):
        """Manual blog post creation"""
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            title = st.text_input("📌 Update Title", placeholder="Major Feature Release - Hunt Hub Launch")
            
            # Smart category detection
            detected_category = self.detect_category_from_title(title)
            
            category = st.selectbox(
                "📁 Category",
                ["feature", "bugfix", "performance", "security", "analytics", "trading", "critical", "documentation"],
                index=["feature", "bugfix", "performance", "security", "analytics", "trading", "critical", "documentation"].index(detected_category) if detected_category else 0
            )
            
            # Component selection with smart suggestions
            suggested_components = self.suggest_components_from_category(category)
            components = st.multiselect(
                "🔧 Affected Components",
                ["Dashboard", "Trading Engine", "API System", "Webhooks", "Database", "UI/UX", "Security", "Analytics"],
                default=suggested_components,
                key="blog_create_components"
            )
            
            # Rich text editors
            technical_details = st.text_area(
                "👨‍💻 Technical Details",
                placeholder="Describe the technical implementation, changes made, and architecture decisions...",
                height=150
            )
            
            user_impact = st.text_area(
                "👥 User Impact",
                placeholder="Explain how this affects users, what they'll notice, and benefits they'll receive...",
                height=150
            )
        
        with col2:
            version = st.text_input("🏷️ Version", value=self.get_next_version())
            priority = st.select_slider(
                "⚡ Priority",
                options=["low", "medium", "high", "critical"],
                value="medium"
            )
            
            # Metrics
            st.markdown("**📊 Metrics:**")
            metrics = {}
            if st.checkbox("Add Performance Metrics"):
                metrics['Speed Improvement'] = st.text_input("Speed Improvement", "40% faster")
                metrics['Load Time'] = st.text_input("Load Time", "< 1s")
            
            if st.checkbox("Add Impact Metrics"):
                metrics['Users Affected'] = st.text_input("Users Affected", "All users")
                metrics['Downtime'] = st.text_input("Downtime", "None")
            
            # Channel selection
            st.markdown("**📢 Discord Channels:**")
            selected_channels = self.select_channels_for_category(category, priority)
        
        # Preview and publish
        if st.button("👁️ Preview Update", type="secondary"):
            self.preview_update(title, category, components, technical_details, user_impact, metrics, priority)
        
        if st.button("🚀 Publish Update", type="primary"):
            self.publish_comprehensive_update(
                title, category, version, components, technical_details, 
                user_impact, metrics, priority, selected_channels, "manual"
            )
    
    def render_git_retrospective(self):
        """Git commit-based update creation"""
        
        st.markdown("### 🔄 Create Update from Git History")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            time_range = st.selectbox(
                "📅 Time Range",
                ["Last 24 hours", "Last 3 days", "Last week", "Last 2 weeks", "Custom"]
            )
            
            if time_range == "Custom":
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
            else:
                start_date, end_date = self.parse_time_range(time_range)
        
        with col2:
            grouping = st.selectbox(
                "📊 Grouping Strategy",
                ["By Feature", "By Day", "By Category", "By Author", "Smart Grouping"]
            )
            
            min_commits = st.number_input(
                "Minimum Commits per Update",
                min_value=1,
                max_value=50,
                value=3
            )
        
        with col3:
            st.markdown("**Filters:**")
            exclude_docs = st.checkbox("Exclude documentation", value=True)
            exclude_tests = st.checkbox("Exclude test commits", value=True)
            major_only = st.checkbox("Major changes only", value=False)
        
        if st.button("🔍 Analyze Commits"):
            with st.spinner("Analyzing git history..."):
                # Get commits
                commits = self.retrospective.get_commits_since(
                    since_date=datetime.combine(start_date, datetime.min.time()),
                    until_date=datetime.combine(end_date, datetime.max.time()) if end_date else None
                )
                
                # Apply filters
                if exclude_docs:
                    commits = [c for c in commits if not any('doc' in f.lower() for f in c.files_changed)]
                if exclude_tests:
                    commits = [c for c in commits if 'test' not in c.message.lower()]
                if major_only:
                    commits = [c for c in commits if c.insertions + c.deletions > 100]
                
                st.success(f"Found {len(commits)} commits matching criteria")
                
                # Group and display
                if grouping == "Smart Grouping":
                    updates = self.smart_group_commits(commits)
                else:
                    updates = self.group_commits_by_strategy(commits, grouping, min_commits)
                
                # Display proposed updates
                st.markdown("### 📋 Proposed Updates")
                
                for idx, update in enumerate(updates):
                    with st.expander(f"{update['icon']} {update['title']} ({len(update['commits'])} commits)"):
                        st.markdown(f"**Category:** {update['category']}")
                        st.markdown(f"**Priority:** {update['priority']}")
                        st.markdown(f"**Components:** {', '.join(update['components'])}")
                        
                        st.markdown("**Commits:**")
                        for commit in update['commits'][:5]:
                            st.text(f"  {commit.hash[:8]} - {commit.message[:60]}")
                        if len(update['commits']) > 5:
                            st.text(f"  ... and {len(update['commits']) - 5} more")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✏️ Edit", key=f"edit_{idx}"):
                                st.session_state.editing_update = update
                        with col2:
                            if st.button(f"🚀 Publish", key=f"publish_{idx}"):
                                self.publish_retrospective_update(update)
    
    def render_customer_focused(self):
        """Customer-focused update creation"""
        
        st.markdown("### 🎯 Customer-Focused Updates")
        
        # Quick customer update templates
        template = st.selectbox(
            "📝 Update Template",
            [
                "🚀 New Feature Announcement",
                "🐛 Bug Fix & Stability Update",
                "⚡ Performance Improvements",
                "🔒 Security Update",
                "📊 Analytics & Insights Update",
                "🎉 Major Release",
                "⚠️ Critical Update"
            ]
        )
        
        # Auto-populate based on template
        template_data = self.get_customer_template_data(template)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            title = st.text_input("Title", value=template_data['title'])
            
            # Customer-friendly sections
            st.markdown("**What's New:**")
            whats_new = st.text_area(
                "List the key changes customers will notice",
                value=template_data.get('whats_new', ''),
                height=100
            )
            
            st.markdown("**Why It Matters:**")
            why_matters = st.text_area(
                "Explain the benefits in simple terms",
                value=template_data.get('why_matters', ''),
                height=100
            )
            
            st.markdown("**What You Need to Do:**")
            action_required = st.text_area(
                "Any action required from users?",
                value=template_data.get('action_required', 'No action required - updates are automatic!'),
                height=80
            )
        
        with col2:
            # Visual elements
            st.markdown("**Visual Elements:**")
            include_screenshot = st.checkbox("Include Screenshot", value=True)
            include_video = st.checkbox("Include Demo Video")
            include_emoji = st.checkbox("Use Emojis", value=True)
            
            # Tone selection
            tone = st.radio(
                "Tone",
                ["Excited", "Professional", "Urgent", "Friendly"],
                index=template_data.get('tone_index', 0)
            )
            
            # Target audience
            audience = st.multiselect(
                "Target Audience",
                ["All Users", "Pro Traders", "Beginners", "API Users", "Mobile Users"],
                default=["All Users"],
                key="blog_customer_audience"
            )
        
        # Generate customer-friendly content
        if st.button("🤖 Generate Customer Content"):
            content = self.generate_customer_content(
                template, title, whats_new, why_matters, 
                action_required, tone, audience
            )
            st.session_state.customer_content = content
        
        # Preview
        if 'customer_content' in st.session_state:
            st.markdown("### 👁️ Preview")
            st.markdown(st.session_state.customer_content['preview'])
            
            # Channel recommendations
            st.markdown("### 📢 Recommended Channels")
            recommended = self.recommend_channels_for_customer_update(template)
            selected_channels = st.multiselect(
                "Select Channels",
                list(self.discord_channels.keys()),
                default=recommended,
                key="blog_customer_channels"
            )
            
            if st.button("🚀 Publish Customer Update", type="primary"):
                self.publish_customer_update(
                    st.session_state.customer_content,
                    selected_channels
                )
    
    def render_scheduling(self):
        """Post scheduling interface"""
        
        st.markdown("### 📅 Schedule Posts")
        
        # Scheduled posts overview
        scheduled = self.get_scheduled_posts()
        
        if scheduled:
            st.markdown("#### 📋 Scheduled Posts")
            
            for post in scheduled:
                with st.expander(f"📅 {post['title']} - {post['scheduled_time']}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Channels:** {', '.join(post['channels'])}")
                        st.markdown(f"**Status:** {post['status']}")
                    
                    with col2:
                        if st.button("✏️ Edit", key=f"edit_scheduled_{post['id']}"):
                            st.session_state.editing_scheduled = post['id']
                    
                    with col3:
                        if st.button("❌ Cancel", key=f"cancel_scheduled_{post['id']}"):
                            self.cancel_scheduled_post(post['id'])
        
        st.markdown("---")
        
        # Schedule new post
        st.markdown("#### 📝 Schedule New Post")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Load draft posts
            drafts = self.get_draft_posts()
            
            if drafts:
                selected_draft = st.selectbox(
                    "Select Draft Post",
                    ["Create New"] + [f"{d['title']} (v{d['version']})" for d in drafts]
                )
                
                if selected_draft != "Create New":
                    # Load draft content
                    draft_idx = drafts[0] if len(drafts) == 1 else None  # Simplified
            else:
                st.info("No draft posts available. Create a new post above.")
        
        with col2:
            schedule_date = st.date_input("Schedule Date", min_value=datetime.now().date())
            schedule_time = st.time_input("Schedule Time")
            
            # Repeat options
            repeat = st.checkbox("Repeat Post")
            if repeat:
                repeat_frequency = st.selectbox(
                    "Frequency",
                    ["Daily", "Weekly", "Bi-weekly", "Monthly"]
                )
                repeat_count = st.number_input("Number of times", min_value=1, max_value=10, value=1)
        
        if st.button("📅 Schedule Post"):
            scheduled_datetime = datetime.combine(schedule_date, schedule_time)
            self.schedule_post(selected_draft, scheduled_datetime, repeat, repeat_frequency, repeat_count)
    
    def render_analytics_dashboard(self):
        """Analytics and insights dashboard"""
        
        st.markdown("### 📊 Blog Analytics Dashboard")
        
        # Time range selector
        time_range = st.selectbox(
            "Time Range",
            ["Last 7 days", "Last 30 days", "Last 3 months", "All time"],
            index=1
        )
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = self.get_blog_metrics(time_range)
        
        with col1:
            st.metric(
                "Total Posts",
                metrics['total_posts'],
                delta=f"↑{metrics['posts_growth']}"
            )
        
        with col2:
            st.metric(
                "Total Reach",
                f"{metrics['total_reach']:,}",
                delta=f"↑{metrics['reach_growth']}%"
            )
        
        with col3:
            st.metric(
                "Engagement Rate",
                f"{metrics['engagement_rate']:.1%}",
                delta=f"↑{metrics['engagement_growth']}%"
            )
        
        with col4:
            st.metric(
                "Active Channels",
                metrics['active_channels'],
                delta=f"{metrics['channel_growth']}"
            )
        
        # Charts
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Post Frequency")
            chart_data = self.get_post_frequency_data(time_range)
            st.area_chart(chart_data)
        
        with col2:
            st.markdown("#### 🎯 Category Distribution")
            category_data = self.get_category_distribution(time_range)
            st.bar_chart(category_data)
        
        # Channel performance
        st.markdown("#### 📢 Channel Performance")
        
        channel_metrics = self.get_channel_performance_metrics(time_range)
        
        # Create performance table
        for channel, metrics in channel_metrics.items():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"**#{channel}**")
            with col2:
                st.metric("Posts", metrics['posts'])
            with col3:
                st.metric("Reach", f"{metrics['reach']:,}")
            with col4:
                st.metric("Engagement", f"{metrics['engagement']:.1%}")
            with col5:
                status = "🟢" if metrics['webhook_status'] else "🔴"
                st.markdown(f"Status: {status}")
        
        # Top performing posts
        st.markdown("#### 🏆 Top Performing Posts")
        
        top_posts = self.get_top_performing_posts(time_range, limit=5)
        
        for idx, post in enumerate(top_posts, 1):
            with st.expander(f"{idx}. {post['title']} - {post['engagement']:,} engagements"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Published:** {post['published_date']}")
                    st.markdown(f"**Channels:** {', '.join(post['channels'])}")
                    st.markdown(f"**Category:** {post['category']}")
                
                with col2:
                    st.metric("Views", f"{post['views']:,}")
                    st.metric("Reactions", post['reactions'])
                    if st.button("📊 Detailed Analytics", key=f"analytics_{idx}"):
                        self.show_detailed_post_analytics(post['id'])
    
    def render_settings(self):
        """System settings and configuration"""
        
        st.markdown("### ⚙️ Blog System Settings")
        
        tabs = st.tabs(["🔗 Webhooks", "🤖 Automation", "📝 Templates", "🔐 Security"])
        
        with tabs[0]:
            self.render_webhook_settings()
        
        with tabs[1]:
            self.render_automation_settings()
        
        with tabs[2]:
            self.render_template_settings()
        
        with tabs[3]:
            self.render_security_settings()
    
    def render_webhook_settings(self):
        """Webhook configuration"""
        
        st.markdown("#### 🔗 Discord Webhook Configuration")
        
        # Show current webhook status
        for channel, config in self.discord_channels.items():
            col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
            
            with col1:
                st.markdown(f"**#{channel}**")
            
            with col2:
                webhook_url = config['webhook']
                if webhook_url == '[NEEDS_WEBHOOK]':
                    new_url = st.text_input(
                        f"Webhook URL",
                        key=f"webhook_{channel}",
                        placeholder="https://discord.com/api/webhooks/..."
                    )
                    if new_url and st.button("💾", key=f"save_{channel}"):
                        self.update_webhook(channel, new_url)
                else:
                    masked_url = webhook_url[:40] + "..." if len(webhook_url) > 40 else webhook_url
                    st.text(masked_url)
            
            with col3:
                status = "🟢" if webhook_url != '[NEEDS_WEBHOOK]' else "🔴"
                st.markdown(f"Status: {status}")
            
            with col4:
                if webhook_url != '[NEEDS_WEBHOOK]':
                    if st.button("🧪", key=f"test_{channel}"):
                        self.test_webhook(channel, webhook_url)
        
        # Bulk webhook testing
        if st.button("🧪 Test All Webhooks"):
            self.test_all_webhooks()
    
    # Helper methods
    def detect_category_from_title(self, title: str) -> Optional[str]:
        """Detect category from title using keywords"""
        if not title:
            return None
        
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['feature', 'launch', 'new', 'release']):
            return 'feature'
        elif any(word in title_lower for word in ['fix', 'bug', 'issue', 'repair']):
            return 'bugfix'
        elif any(word in title_lower for word in ['performance', 'speed', 'optimize']):
            return 'performance'
        elif any(word in title_lower for word in ['security', 'vulnerability', 'protect']):
            return 'security'
        elif any(word in title_lower for word in ['critical', 'urgent', 'emergency']):
            return 'critical'
        
        return None
    
    def suggest_components_from_category(self, category: str) -> List[str]:
        """Suggest components based on category"""
        suggestions = {
            'feature': ['Dashboard', 'UI/UX'],
            'bugfix': ['Dashboard', 'Database'],
            'performance': ['Trading Engine', 'Database'],
            'security': ['Security', 'API System'],
            'trading': ['Trading Engine', 'Analytics'],
            'analytics': ['Analytics', 'Dashboard']
        }
        
        return suggestions.get(category, [])
    
    def select_channels_for_category(self, category: str, priority: str) -> List[str]:
        """Auto-select appropriate channels"""
        selected = []
        
        # Always include dev-blog
        selected.append('dev-blog')
        
        # Category-based selection
        if category in self.smart_routing:
            selected.extend(self.smart_routing[category])
        
        # Priority-based additions
        if priority == 'critical':
            selected.extend(['overview', 'system-updates', 'announcements'])
        elif priority == 'high':
            selected.append('announcements')
        
        # Remove duplicates and non-existent channels
        selected = list(set(selected))
        selected = [ch for ch in selected if ch in self.discord_channels]
        
        return selected
    
    def get_next_version(self) -> str:
        """Get next version number"""
        # Query database for latest version
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM comprehensive_posts ORDER BY created_timestamp DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                # Increment patch version
                parts = result[0].split('.')
                if len(parts) == 3:
                    parts[2] = str(int(parts[2]) + 1)
                    return '.'.join(parts)
            
            return "1.3.0"
    
    def publish_comprehensive_update(self, title, category, version, components, 
                                   technical_details, user_impact, metrics, 
                                   priority, channels, post_type):
        """Publish update through all systems WITH queue management"""
        
        # Create development update
        update = DevelopmentUpdate(
            update_type=category,
            title=title,
            version=version,
            components=components,
            technical_details=technical_details,
            user_impact=user_impact,
            metrics=metrics,
            timestamp=datetime.now(),
            priority=priority
        )
        
        # Check if queue processor is running
        if not self.queue_processor_task or self.queue_processor_task.done():
            st.warning("⚠️ Queue processor not running. Starting it now...")
            try:
                run_async_safe(self.start_queue_processor())
            except Exception as e:
                st.error(f"Failed to start queue processor: {e}")
                return {"total_success": 0, "total_failed": len(channels), "discord_results": {}}
        
        # Create Discord embed
        embed = self._create_discord_embed(update)
        
        # Map priority
        priority_map = {
            'critical': MessagePriority.CRITICAL,
            'high': MessagePriority.HIGH,
            'medium': MessagePriority.NORMAL,
            'low': MessagePriority.LOW
        }
        msg_priority = priority_map.get(priority, MessagePriority.NORMAL)
        
        # Queue messages for each channel
        queued_count = 0
        post_id = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with st.spinner("Queueing messages for Discord channels..."):
            for channel in channels:
                webhook_url = self.discord_channels.get(channel, {}).get('webhook')
                
                if webhook_url and webhook_url != '[NEEDS_WEBHOOK]':
                    message = QueuedMessage(
                        channel=channel,
                        webhook_url=webhook_url,
                        embed=embed,
                        priority=msg_priority,
                        created_at=datetime.now(),
                        post_id=post_id
                    )
                    
                    self.discord_queue.add_to_queue(message)
                    queued_count += 1
        
        # Save to comprehensive database
        result = {
            'total_success': 0,
            'total_failed': 0,
            'discord_results': {ch: 'queued' for ch in channels}
        }
        self.save_comprehensive_post(update, result, post_type)
        
        # Show results
        if queued_count > 0:
            st.success(f"✅ Queued {queued_count} messages for Discord delivery!")
            
            # Show queue status
            queue_stats = self.discord_queue.get_queue_stats()
            st.info(f"📊 Total messages in queue: {queue_stats['total_queued']}")
            
            # Show rate limit status
            with st.expander("📡 Channel Rate Limit Status"):
                for channel, status in queue_stats['rate_limit_status'].items():
                    if channel in channels:
                        if status['can_send']:
                            st.write(f"✅ **{channel}**: Ready to send")
                        else:
                            st.write(f"⏳ **{channel}**: Rate limited (wait {status['wait_time']:.0f}s)")
        else:
            st.warning("⚠️ No valid webhooks configured for selected channels")
        
        # Show engagement tracking
        st.info("📊 Messages will be sent respecting Discord rate limits. Track delivery in the Queue Monitor tab.")
    
    def save_comprehensive_post(self, update: DevelopmentUpdate, result: Dict, post_type: str):
        """Save post to comprehensive database"""
        import random
        post_id = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        content = {
            'title': update.title,
            'technical_details': update.technical_details,
            'user_impact': update.user_impact,
            'components': update.components,
            'metrics': update.metrics
        }
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO comprehensive_posts 
            (id, post_type, title, version, content_json, channels_posted,
             discord_success_rate, created_timestamp, published_timestamp,
             author, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post_id,
                post_type,
                update.title,
                update.version,
                json.dumps(content),
                json.dumps(list(result.get('discord_results', {}).keys())),
                result['total_success'] / max(result['total_success'] + result['total_failed'], 1),
                datetime.now(),
                datetime.now(),
                update.author,
                update.priority
            ))
            
            conn.commit()
    
    def _create_discord_embed(self, update: DevelopmentUpdate) -> Dict[str, Any]:
        """Create Discord embed from development update"""
        # Color coding by update type
        colors = {
            'feature': 0x00FF00,      # Green
            'bugfix': 0xFF9800,       # Orange
            'critical': 0xFF0000,     # Red
            'performance': 0x2196F3,  # Blue
            'security': 0x9C27B0,     # Purple
            'enhancement': 0x4CAF50,  # Light Green
            'documentation': 0x607D8B # Blue Grey
        }
        
        embed = {
            "title": f"{update.title} (v{update.version})",
            "description": update.technical_details[:2000],  # Discord limit
            "color": colors.get(update.update_type, 0x000000),
            "fields": [
                {
                    "name": "💡 User Impact",
                    "value": update.user_impact[:1024],
                    "inline": False
                },
                {
                    "name": "🔧 Components",
                    "value": ", ".join(update.components[:5]),
                    "inline": True
                },
                {
                    "name": "⚡ Priority",
                    "value": update.priority.upper(),
                    "inline": True
                }
            ],
            "footer": {
                "text": f"TrenchCoat Pro • {update.update_type.title()} Update"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add metrics if available
        if update.metrics:
            metrics_text = "\n".join([f"• {k}: {v}" for k, v in list(update.metrics.items())[:5]])
            embed["fields"].append({
                "name": "📊 Metrics",
                "value": metrics_text[:1024],
                "inline": False
            })
        
        return embed
    
    async def start_queue_processor(self):
        """Start the Discord queue processor"""
        await self.discord_queue.initialize()
        
        # Set notification webhook for system updates
        system_webhook = self.discord_channels.get('system-updates', {}).get('webhook')
        if system_webhook and system_webhook != '[NEEDS_WEBHOOK]':
            self.discord_queue.notification_webhook = system_webhook
        
        # Start processing
        self.queue_processor_task = asyncio.create_task(self.discord_queue.process_queues())
        st.success("🚀 Queue processor started successfully!")
    
    def render_queue_monitor(self):
        """Render the Discord queue monitoring interface"""
        st.markdown("### 📡 Discord Queue Monitor")
        
        # Queue controls
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🚀 Start Queue Processor", type="primary"):
                try:
                    run_async_safe(self.start_queue_processor())
                except Exception as e:
                    st.error(f"Failed to start queue processor: {e}")
        
        with col2:
            if st.button("🛑 Stop Queue Processor"):
                if self.queue_processor_task:
                    self.discord_queue.processing = False
                    st.info("Queue processor stopping...")
        
        with col3:
            if st.button("🔄 Refresh Status"):
                st.rerun()
        
        # Queue statistics
        st.markdown("---")
        
        queue_stats = self.discord_queue.get_queue_stats()
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queued", queue_stats['total_queued'])
        
        with col2:
            st.metric("Failed Messages", queue_stats['failed_count'])
        
        with col3:
            active_channels = len([ch for ch in queue_stats['channels'] if queue_stats['channels'][ch]['queued'] > 0])
            st.metric("Active Channels", active_channels)
        
        with col4:
            processor_status = "Running" if self.queue_processor_task and not self.queue_processor_task.done() else "Stopped"
            st.metric("Processor Status", processor_status)
        
        # Channel details
        st.markdown("### 📊 Channel Queue Status")
        
        if not queue_stats['channels']:
            st.info("No messages currently queued")
        else:
            for channel, channel_stats in queue_stats['channels'].items():
                rate_status = queue_stats['rate_limit_status'].get(channel, {})
                
                with st.expander(f"#{channel} ({channel_stats['queued']} messages)"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Message priorities
                        if channel_stats['priorities']:
                            st.markdown("**Message Priorities:**")
                            for priority, count in channel_stats['priorities'].items():
                                st.write(f"• {priority}: {count}")
                        
                        # Rate limit status
                        st.markdown("**Rate Limit Status:**")
                        if rate_status.get('can_send', True):
                            st.success("✅ Ready to send")
                        else:
                            wait_time = rate_status.get('wait_time', 0)
                            st.warning(f"⏳ Rate limited - wait {wait_time:.0f}s")
                    
                    with col2:
                        # Channel webhook status
                        webhook = self.discord_channels.get(channel, {}).get('webhook', '[NEEDS_WEBHOOK]')
                        if webhook == '[NEEDS_WEBHOOK]':
                            st.error("❌ No webhook configured")
                        else:
                            st.success("✅ Webhook configured")
        
        # Failed messages section
        if queue_stats['failed_count'] > 0:
            st.markdown("### ❌ Failed Messages")
            
            st.warning(f"{queue_stats['failed_count']} messages failed to send after max retries")
            
            if st.button("🔄 Retry Failed Messages"):
                # Re-queue failed messages
                for msg in self.discord_queue.failed_messages[:]:
                    msg.retry_count = 0
                    self.discord_queue.add_to_queue(msg)
                    self.discord_queue.failed_messages.remove(msg)
                
                st.success("Failed messages re-queued!")
                st.rerun()
        
        # Queue history
        st.markdown("### 📜 Recent Queue Activity")
        
        # This would show recent sends, rate limits, etc.
        # For now, show a placeholder
        st.info("Queue activity logging will appear here once messages are processed")
    
    def get_customer_template_data(self, template: str) -> Dict[str, Any]:
        """Get template data for customer updates"""
        templates = {
            "🚀 New Feature Announcement": {
                'title': "Exciting New Feature: [Feature Name]",
                'whats_new': "• New [feature] that helps you [benefit]\n• Improved [area] for better [result]\n• Added [capability] to enhance your experience",
                'why_matters': "This update makes it easier to [achieve goal] by [method]. You'll save time and increase profits!",
                'action_required': "No action required - the feature is already live!",
                'tone_index': 0  # Excited
            },
            "🐛 Bug Fix & Stability Update": {
                'title': "Stability Improvements Released",
                'whats_new': "• Fixed issue where [problem]\n• Resolved [specific bug]\n• Improved stability in [area]",
                'why_matters': "These fixes ensure smoother operation and fewer interruptions to your trading.",
                'action_required': "No action required - fixes are automatically applied.",
                'tone_index': 1  # Professional
            },
            "⚠️ Critical Update": {
                'title': "Critical Security Update - Action Required",
                'whats_new': "• Critical security patch applied\n• System vulnerability addressed\n• Enhanced protection measures",
                'why_matters': "This update is essential for protecting your account and trading activities.",
                'action_required': "Please refresh your browser to ensure you're using the latest version.",
                'tone_index': 2  # Urgent
            }
        }
        
        return templates.get(template, {
            'title': template,
            'whats_new': '',
            'why_matters': '',
            'action_required': 'No action required.',
            'tone_index': 1
        })

# Streamlit app entry point
def main():
    st.set_page_config(
        page_title="TrenchCoat Pro - Dev Blog System",
        page_icon="📰",
        layout="wide"
    )
    
    # Initialize system
    if 'blog_system' not in st.session_state:
        st.session_state.blog_system = ComprehensiveDevBlogSystem()
    
    # Render interface
    st.session_state.blog_system.render_comprehensive_interface()

if __name__ == "__main__":
    main()