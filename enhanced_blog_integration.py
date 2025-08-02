#!/usr/bin/env python3
"""
TrenchCoat Pro - Enhanced Blog Integration
Integrates dev blog, retrospective, webhook, and queue systems with dashboard
"""

import streamlit as st
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
from pathlib import Path

# Import all blog systems
from comprehensive_dev_blog_system import ComprehensiveDevBlogSystem
from retrospective_blog_system import RetrospectiveBlogSystem
from customer_focused_retrospective import CustomerFocusedRetrospective
from integrated_webhook_blog_system import DevelopmentUpdate
from enhanced_blog_with_queue import DiscordRateLimitQueue, QueuedMessage, MessagePriority

class EnhancedBlogIntegration:
    """Complete integration of all blog systems with dashboard"""
    
    def __init__(self):
        # Initialize all systems
        self.comprehensive_system = ComprehensiveDevBlogSystem()
        self.retrospective = RetrospectiveBlogSystem()
        self.customer_focused = CustomerFocusedRetrospective()
        
        # Database paths
        self.blog_db_path = "comprehensive_dev_blog.db"
        self.webhook_db_path = "trenchcoat_webhook_blog.db"
        
        # Initialize session state
        if 'blog_posts' not in st.session_state:
            st.session_state.blog_posts = self.load_all_posts()
        if 'simulation_running' not in st.session_state:
            st.session_state.simulation_running = False
        if 'queue_processor_running' not in st.session_state:
            st.session_state.queue_processor_running = False
    
    def load_all_posts(self) -> List[Dict[str, Any]]:
        """Load all blog posts from various sources"""
        posts = []
        
        # Load from comprehensive blog database
        try:
            conn = sqlite3.connect(self.blog_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, post_type, title, version, content_json, 
                       created_timestamp, author, priority, customer_impact_score
                FROM comprehensive_posts
                ORDER BY created_timestamp DESC
                LIMIT 50
            ''')
            
            for row in cursor.fetchall():
                content = json.loads(row[4])
                posts.append({
                    'id': row[0],
                    'type': row[1],
                    'title': row[2],
                    'version': row[3],
                    'content': content,
                    'timestamp': row[5],
                    'author': row[6],
                    'priority': row[7],
                    'impact_score': row[8]
                })
            
            conn.close()
        except Exception as e:
            print(f"Error loading from comprehensive DB: {e}")
        
        # Load from legacy blog posts file
        try:
            with open('dev_blog_posts.json', 'r') as f:
                legacy_posts = json.load(f)
                for post in legacy_posts:
                    if not any(p['id'] == post.get('id', '') for p in posts):
                        posts.append(post)
        except:
            pass
        
        # Sort by timestamp
        posts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return posts
    
    def render_blog_tab(self):
        """Render the enhanced blog tab with all features"""
        # Create sub-tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Blog Posts", 
            "📡 Queue Monitor", 
            "🔄 Retrospective", 
            "🧪 Simulation"
        ])
        
        with tab1:
            self.render_blog_posts()
        
        with tab2:
            self.render_queue_monitor()
        
        with tab3:
            self.render_retrospective()
        
        with tab4:
            self.render_simulation()
    
    def render_blog_posts(self):
        """Render blog posts with live updates"""
        st.subheader("📝 Latest Development Updates")
        
        # Refresh button
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("🔄 Refresh", key="refresh_posts"):
                st.session_state.blog_posts = self.load_all_posts()
                st.rerun()
        
        with col2:
            if st.button("📤 Create Post", key="create_post"):
                st.session_state.show_create_form = True
        
        # Filter options
        with st.expander("🔍 Filter Options"):
            col1, col2, col3 = st.columns(3)
            with col1:
                post_type = st.selectbox(
                    "Post Type",
                    ["All", "manual", "retrospective", "customer", "automated"]
                )
            with col2:
                priority = st.selectbox(
                    "Priority",
                    ["All", "critical", "high", "medium", "low"]
                )
            with col3:
                days_back = st.slider("Days Back", 1, 30, 7)
        
        # Display posts
        posts_to_show = st.session_state.blog_posts
        
        # Apply filters
        if post_type != "All":
            posts_to_show = [p for p in posts_to_show if p.get('type') == post_type]
        if priority != "All":
            posts_to_show = [p for p in posts_to_show if p.get('priority') == priority]
        
        # Time filter
        cutoff_date = datetime.now() - timedelta(days=days_back)
        posts_to_show = [
            p for p in posts_to_show 
            if datetime.fromisoformat(p.get('timestamp', '2025-01-01')) > cutoff_date
        ]
        
        # Display posts
        if posts_to_show:
            for post in posts_to_show[:20]:  # Show max 20
                self.render_single_post(post)
        else:
            st.info("No blog posts found matching the criteria.")
        
        # Create post form
        if st.session_state.get('show_create_form', False):
            self.render_create_post_form()
    
    def render_single_post(self, post: Dict[str, Any]):
        """Render a single blog post"""
        # Color based on priority
        priority_colors = {
            'critical': '#ff4444',
            'high': '#ff8800',
            'medium': '#ffaa00',
            'low': '#88ff88'
        }
        color = priority_colors.get(post.get('priority', 'medium'), '#ffffff')
        
        with st.expander(
            f"{post.get('title', 'Untitled')} - v{post.get('version', '1.0.0')} "
            f"({post.get('timestamp', '')[:10]})"
        ):
            # Metadata
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Type:** {post.get('type', 'manual')}")
            with col2:
                st.markdown(f"**Priority:** <span style='color:{color}'>{post.get('priority', 'medium')}</span>", 
                           unsafe_allow_html=True)
            with col3:
                st.markdown(f"**Author:** {post.get('author', 'System')}")
            with col4:
                st.markdown(f"**Impact:** {post.get('impact_score', 0)}/100")
            
            # Content
            content = post.get('content', {})
            if isinstance(content, dict):
                if content.get('description'):
                    st.markdown("### Description")
                    st.markdown(content['description'])
                
                if content.get('technical_details'):
                    st.markdown("### Technical Details")
                    st.code(content['technical_details'][:500])
                
                if content.get('user_impact'):
                    st.markdown("### User Impact")
                    st.info(content['user_impact'])
                
                if content.get('components'):
                    st.markdown("### Components")
                    for comp in content['components']:
                        st.markdown(f"- {comp}")
            else:
                st.markdown(str(content))
    
    def render_queue_monitor(self):
        """Render the Discord queue monitor"""
        st.subheader("📡 Discord Queue Monitor")
        
        # Try to use the comprehensive system's queue monitor
        try:
            self.comprehensive_system.render_queue_monitor()
        except Exception as e:
            st.error(f"Error rendering queue monitor: {e}")
            
            # Fallback UI
            st.info("Queue monitor is initializing...")
            
            # Basic controls
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🚀 Start Queue Processor"):
                    st.session_state.queue_processor_running = True
                    st.success("Queue processor started!")
            
            with col2:
                if st.button("⏸️ Stop Queue Processor"):
                    st.session_state.queue_processor_running = False
                    st.info("Queue processor stopped.")
            
            with col3:
                st.metric("Status", 
                         "Running" if st.session_state.queue_processor_running else "Stopped")
    
    def render_retrospective(self):
        """Render retrospective blog generation"""
        st.subheader("🔄 Retrospective Blog Generation")
        
        st.markdown("""
        Generate blog posts from your git commit history. This analyzes commits
        and creates customer-friendly updates automatically.
        """)
        
        # Time range selection
        col1, col2 = st.columns(2)
        with col1:
            days_back = st.number_input("Days to analyze", 1, 30, 7)
            since_date = datetime.now() - timedelta(days=days_back)
        
        with col2:
            if st.button("🔍 Analyze Commits", type="primary"):
                with st.spinner("Analyzing commit history..."):
                    self.generate_retrospective_posts(since_date)
        
        # Show recent retrospective posts
        st.markdown("### Recent Retrospective Posts")
        retro_posts = [p for p in st.session_state.blog_posts if p.get('type') == 'retrospective']
        
        if retro_posts:
            for post in retro_posts[:5]:
                self.render_single_post(post)
        else:
            st.info("No retrospective posts yet. Click 'Analyze Commits' to generate some!")
    
    def render_simulation(self):
        """Render blog simulation interface"""
        st.subheader("🧪 Blog Simulation")
        
        st.markdown("""
        Simulate blog posts for testing the system. This creates realistic
        development updates and sends them through the complete pipeline.
        """)
        
        # Simulation controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sim_days = st.number_input("Days to simulate", 1, 30, 7)
        
        with col2:
            posts_per_day = st.slider("Posts per day", 1, 10, 3)
        
        with col3:
            include_discord = st.checkbox("Send to Discord", value=False)
        
        # Simulation types
        st.markdown("### Update Types to Simulate")
        col1, col2 = st.columns(2)
        
        with col1:
            sim_features = st.checkbox("Features", value=True)
            sim_bugs = st.checkbox("Bug Fixes", value=True)
            sim_performance = st.checkbox("Performance", value=True)
        
        with col2:
            sim_security = st.checkbox("Security", value=False)
            sim_docs = st.checkbox("Documentation", value=True)
            sim_analytics = st.checkbox("Analytics", value=True)
        
        # Run simulation button
        if st.button("🚀 Run Simulation", type="primary", key="run_sim"):
            self.run_blog_simulation(
                days=sim_days,
                posts_per_day=posts_per_day,
                include_discord=include_discord,
                types={
                    'feature': sim_features,
                    'bugfix': sim_bugs,
                    'performance': sim_performance,
                    'security': sim_security,
                    'documentation': sim_docs,
                    'analytics': sim_analytics
                }
            )
    
    def generate_retrospective_posts(self, since_date: datetime):
        """Generate retrospective blog posts from git history"""
        try:
            # Get commits
            commits = self.retrospective.get_commits_since(since_date)
            
            if not commits:
                st.warning("No commits found in the specified time range.")
                return
            
            # Group and analyze commits
            groups = self.retrospective.group_commits_by_update(commits)
            
            # Generate customer-focused updates
            updates_created = 0
            for group in groups:
                # Create customer-focused version
                customer_update = self.customer_focused.transform_to_customer_update(group)
                
                # Publish through comprehensive system
                result = self.comprehensive_system.publish_comprehensive_update(
                    title=customer_update['title'],
                    category=customer_update['category'],
                    version=customer_update['version'],
                    components=customer_update['components'],
                    technical_details=customer_update.get('technical_details', ''),
                    user_impact=customer_update['user_impact'],
                    metrics=customer_update.get('metrics', {}),
                    author="Retrospective System",
                    priority=customer_update.get('priority', 'medium'),
                    channels=customer_update.get('channels', ['dev-blog'])
                )
                
                if result.get('success'):
                    updates_created += 1
            
            st.success(f"Created {updates_created} retrospective blog posts!")
            st.session_state.blog_posts = self.load_all_posts()
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generating retrospective posts: {e}")
    
    def run_blog_simulation(self, days: int, posts_per_day: int, 
                           include_discord: bool, types: Dict[str, bool]):
        """Run a blog simulation"""
        st.info(f"Starting simulation for {days} days with {posts_per_day} posts/day...")
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulation data
        update_templates = {
            'feature': [
                ("New Trading Algorithm", "Implemented ML-based prediction engine"),
                ("Enhanced Dashboard UI", "Redesigned coin cards with animations"),
                ("API Integration", "Added support for 5 new data sources"),
                ("Real-time Alerts", "Push notifications for price movements")
            ],
            'bugfix': [
                ("Fixed Memory Leak", "Resolved issue causing high memory usage"),
                ("Database Connection Fix", "Improved connection pooling"),
                ("UI Rendering Bug", "Fixed tab switching display issues"),
                ("API Rate Limit", "Better handling of rate limited requests")
            ],
            'performance': [
                ("Query Optimization", "50% faster database queries"),
                ("Caching Implementation", "Reduced API calls by 70%"),
                ("Async Processing", "Parallel data enrichment"),
                ("Memory Optimization", "Reduced memory footprint by 30%")
            ],
            'security': [
                ("API Key Encryption", "Enhanced security for stored credentials"),
                ("SQL Injection Fix", "Sanitized all database inputs"),
                ("Authentication Update", "Implemented 2FA support"),
                ("Security Audit", "Fixed 3 critical vulnerabilities")
            ],
            'documentation': [
                ("API Documentation", "Complete API reference guide"),
                ("User Guide Update", "Added 10 new tutorials"),
                ("Code Comments", "Improved inline documentation"),
                ("Architecture Docs", "System design documentation")
            ],
            'analytics': [
                ("New Metrics Dashboard", "Added 15 new performance metrics"),
                ("Trading Analytics", "Win/loss ratio tracking"),
                ("User Behavior Tracking", "Anonymous usage analytics"),
                ("Performance Reports", "Automated weekly reports")
            ]
        }
        
        # Generate posts
        total_posts = days * posts_per_day
        posts_created = 0
        
        # Enabled types
        enabled_types = [t for t, enabled in types.items() if enabled]
        if not enabled_types:
            st.error("Please select at least one update type!")
            return
        
        for day in range(days):
            for post_num in range(posts_per_day):
                # Progress update
                progress = (posts_created + 1) / total_posts
                progress_bar.progress(progress)
                status_text.text(f"Creating post {posts_created + 1} of {total_posts}...")
                
                # Select random type and template
                update_type = enabled_types[posts_created % len(enabled_types)]
                templates = update_templates[update_type]
                template = templates[posts_created % len(templates)]
                
                # Create update
                timestamp = datetime.now() - timedelta(days=days-day, hours=post_num*8)
                
                try:
                    result = self.comprehensive_system.publish_comprehensive_update(
                        title=f"{template[0]} (Simulated)",
                        category=update_type,
                        version=f"1.{day}.{post_num}",
                        components=[f"component_{update_type}", "core_system"],
                        technical_details=f"Simulated: {template[1]}",
                        user_impact=f"This update improves {update_type} significantly",
                        metrics={
                            "improvement": f"{20 + (posts_created % 80)}%",
                            "affected_users": 1000 + (posts_created * 100)
                        },
                        author="Simulation System",
                        priority="medium" if update_type != "security" else "high",
                        channels=["dev-blog"] if not include_discord else None,
                        simulation_timestamp=timestamp
                    )
                    
                    if result.get('success'):
                        posts_created += 1
                    
                except Exception as e:
                    st.error(f"Error creating post: {e}")
                
                # Small delay to avoid overwhelming the system
                time.sleep(0.1)
        
        # Complete
        progress_bar.progress(1.0)
        status_text.text(f"Simulation complete! Created {posts_created} posts.")
        
        # Refresh posts
        st.session_state.blog_posts = self.load_all_posts()
        
        # Show summary
        st.success(f"""
        ### Simulation Complete!
        - Created {posts_created} blog posts
        - Timeframe: {days} days
        - Discord: {'Enabled' if include_discord else 'Disabled'}
        """)
        
        if include_discord:
            st.info("Check the Queue Monitor tab to see Discord delivery status.")
    
    def render_create_post_form(self):
        """Render form for creating a new blog post"""
        with st.expander("📝 Create New Blog Post", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title")
                category = st.selectbox(
                    "Category",
                    ["feature", "bugfix", "performance", "security", "documentation", "analytics"]
                )
                priority = st.selectbox(
                    "Priority",
                    ["low", "medium", "high", "critical"]
                )
            
            with col2:
                version = st.text_input("Version", value="1.0.0")
                components = st.text_area("Components (one per line)")
                channels = st.multiselect(
                    "Discord Channels",
                    ["dev-blog", "announcements", "bug-reports", "performance", "analytics"]
                )
            
            technical_details = st.text_area("Technical Details")
            user_impact = st.text_area("User Impact")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Publish", type="primary"):
                    if title and technical_details and user_impact:
                        result = self.comprehensive_system.publish_comprehensive_update(
                            title=title,
                            category=category,
                            version=version,
                            components=components.split('\n') if components else [],
                            technical_details=technical_details,
                            user_impact=user_impact,
                            priority=priority,
                            channels=channels if channels else ["dev-blog"]
                        )
                        
                        if result.get('success'):
                            st.success("Blog post published successfully!")
                            st.session_state.show_create_form = False
                            st.session_state.blog_posts = self.load_all_posts()
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('error')}")
                    else:
                        st.error("Please fill in all required fields!")
            
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.show_create_form = False
                    st.rerun()


def integrate_blog_tab():
    """Function to be called from streamlit_app.py to render the blog tab"""
    integration = EnhancedBlogIntegration()
    integration.render_blog_tab()


# For testing
if __name__ == "__main__":
    st.set_page_config(page_title="Blog Integration Test", layout="wide")
    st.title("Enhanced Blog Integration Test")
    integrate_blog_tab()