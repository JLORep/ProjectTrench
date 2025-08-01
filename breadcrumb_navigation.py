"""
Breadcrumb Navigation System for TrenchCoat Pro
Provides easy website navigation with visual breadcrumb trails
"""
import streamlit as st
from typing import List, Optional, Dict

class BreadcrumbNavigation:
    """Enhanced breadcrumb navigation system"""
    
    def __init__(self):
        # Define the site structure
        self.site_structure = {
            "Home": {
                "icon": "🏠",
                "children": {
                    "Coin Data": {
                        "icon": "🗄️",
                        "children": {
                            "Coin Details": {"icon": "📊"},
                            "Analytics": {"icon": "📈"},
                            "Historical Data": {"icon": "📜"}
                        }
                    },
                    "Live Dashboard": {
                        "icon": "📊",
                        "children": {
                            "Market Signals": {"icon": "📡"},
                            "Portfolio": {"icon": "💼"},
                            "Performance": {"icon": "📈"}
                        }
                    },
                    "Advanced Analytics": {
                        "icon": "🧠",
                        "children": {
                            "AI Models": {"icon": "🤖"},
                            "Predictions": {"icon": "🔮"},
                            "Backtesting": {"icon": "⏮️"}
                        }
                    },
                    "Trading Engine": {
                        "icon": "⚙️",
                        "children": {
                            "Bot Config": {"icon": "🤖"},
                            "Strategies": {"icon": "📋"},
                            "Orders": {"icon": "📝"}
                        }
                    },
                    "Settings": {
                        "icon": "⚙️",
                        "children": {
                            "API Keys": {"icon": "🔑"},
                            "Preferences": {"icon": "🎨"},
                            "Security": {"icon": "🔒"}
                        }
                    }
                }
            }
        }
    
    def render(self, current_path: List[str], clickable: bool = True):
        """
        Render breadcrumb navigation
        
        Args:
            current_path: List of page names from root to current page
            clickable: Whether breadcrumb items should be clickable
        """
        # Style for breadcrumb container
        st.markdown("""
        <style>
        .breadcrumb-container {
            background: linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(16,185,129,0.05) 100%);
            border: 1px solid rgba(16,185,129,0.3);
            border-radius: 12px;
            padding: 12px 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .breadcrumb-item {
            color: #10b981;
            text-decoration: none;
            padding: 4px 8px;
            border-radius: 6px;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        
        .breadcrumb-item:hover {
            background: rgba(16,185,129,0.2);
            transform: translateY(-1px);
        }
        
        .breadcrumb-current {
            color: white;
            font-weight: bold;
            padding: 4px 8px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        
        .breadcrumb-separator {
            color: #6b7280;
            margin: 0 8px;
            font-size: 14px;
        }
        
        @media (max-width: 768px) {
            .breadcrumb-container {
                padding: 8px 12px;
                font-size: 14px;
            }
            
            .breadcrumb-separator {
                margin: 0 4px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Build breadcrumb HTML
        breadcrumb_parts = []
        
        # Always start with Home
        if not current_path or current_path[0] != "Home":
            current_path = ["Home"] + (current_path or [])
        
        # Get icons for each part
        for i, page in enumerate(current_path):
            icon = self._get_icon(current_path[:i+1])
            
            if i < len(current_path) - 1 and clickable:
                # Clickable breadcrumb item
                breadcrumb_parts.append(
                    f'<a href="#" class="breadcrumb-item" onclick="return false;">{icon} {page}</a>'
                )
            else:
                # Current page (not clickable)
                breadcrumb_parts.append(
                    f'<span class="breadcrumb-current">{icon} {page}</span>'
                )
            
            # Add separator except for last item
            if i < len(current_path) - 1:
                breadcrumb_parts.append('<span class="breadcrumb-separator">▶</span>')
        
        # Render the breadcrumb
        breadcrumb_html = f'<div class="breadcrumb-container">{"".join(breadcrumb_parts)}</div>'
        st.markdown(breadcrumb_html, unsafe_allow_html=True)
    
    def _get_icon(self, path: List[str]) -> str:
        """Get icon for a given path"""
        current = self.site_structure
        icon = "📄"  # Default icon
        
        for page in path:
            if isinstance(current, dict):
                if page in current:
                    if isinstance(current[page], dict) and "icon" in current[page]:
                        icon = current[page]["icon"]
                    if isinstance(current[page], dict) and "children" in current[page]:
                        current = current[page]["children"]
                    else:
                        break
                elif "children" in current and page in current["children"]:
                    current = current["children"]
                    if isinstance(current[page], dict) and "icon" in current[page]:
                        icon = current[page]["icon"]
        
        return icon
    
    def render_mini(self, current_page: str, parent_page: Optional[str] = None):
        """Render a minimal breadcrumb for simple navigation"""
        path = ["Home"]
        if parent_page:
            path.append(parent_page)
        if current_page and current_page != "Home":
            path.append(current_page)
        
        self.render(path)
    
    def render_with_actions(self, current_path: List[str], actions: List[Dict[str, str]]):
        """Render breadcrumb with action buttons on the right"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            self.render(current_path)
        
        with col2:
            # Action buttons
            for action in actions:
                if st.button(action.get("label", "Action"), key=action.get("key", None)):
                    if "callback" in action:
                        action["callback"]()

# Helper function for easy integration
def render_breadcrumb(current_page: str, parent_pages: Optional[List[str]] = None):
    """Quick helper to render breadcrumb navigation"""
    nav = BreadcrumbNavigation()
    path = ["Home"]
    if parent_pages:
        path.extend(parent_pages)
    if current_page:
        path.append(current_page)
    nav.render(path)

# Example usage
if __name__ == "__main__":
    st.set_page_config(page_title="Breadcrumb Navigation Demo", layout="wide")
    st.title("🧭 Breadcrumb Navigation System")
    
    # Create navigation instance
    nav = BreadcrumbNavigation()
    
    # Example 1: Simple breadcrumb
    st.subheader("Example 1: Simple Navigation")
    nav.render(["Home", "Coin Data", "Coin Details"])
    
    # Example 2: Different path
    st.subheader("Example 2: Trading Path")
    nav.render(["Home", "Trading Engine", "Bot Config"])
    
    # Example 3: Mini breadcrumb
    st.subheader("Example 3: Mini Breadcrumb")
    nav.render_mini("Portfolio", "Live Dashboard")
    
    # Example 4: With actions
    st.subheader("Example 4: With Actions")
    nav.render_with_actions(
        ["Home", "Advanced Analytics", "AI Models"],
        [
            {"label": "🔄 Refresh", "key": "refresh_btn"},
            {"label": "⚙️ Settings", "key": "settings_btn"}
        ]
    )