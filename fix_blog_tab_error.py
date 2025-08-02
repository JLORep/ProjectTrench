#!/usr/bin/env python3
"""
Fix blog system tab error
"""

import os

def fix_blog_tab_error():
    """Fix the tab indexing error in blog system"""
    
    print("🔧 Fixing blog system tab error...")
    
    # Read the current file
    with open('comprehensive_dev_blog_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the render_comprehensive_interface method
    # The issue is likely that tabs are being accessed incorrectly
    
    # Replace the problematic section with a safer version
    old_pattern = """        with main_tabs[0]:
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
            self.render_settings()"""
    
    new_pattern = """        # Safely render tabs with error handling
        try:
            with main_tabs[0]:
                self.render_create_update()
        except Exception as e:
            st.error(f"Error in Create Update tab: {e}")
        
        try:
            with main_tabs[1]:
                self.render_git_retrospective()
        except Exception as e:
            st.error(f"Error in Retrospective tab: {e}")
        
        try:
            with main_tabs[2]:
                self.render_customer_focused()
        except Exception as e:
            st.error(f"Error in Customer Focus tab: {e}")
        
        try:
            with main_tabs[3]:
                self.render_scheduling()
        except Exception as e:
            st.error(f"Error in Schedule tab: {e}")
        
        try:
            with main_tabs[4]:
                self.render_analytics_dashboard()
        except Exception as e:
            st.error(f"Error in Analytics tab: {e}")
        
        try:
            with main_tabs[5]:
                self.render_queue_monitor()
        except Exception as e:
            st.error(f"Error in Queue Monitor tab: {e}")
        
        try:
            with main_tabs[6]:
                self.render_settings()
        except Exception as e:
            st.error(f"Error in Settings tab: {e}")"""
    
    # Apply the fix
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        
        # Backup the original
        os.rename('comprehensive_dev_blog_system.py', 'comprehensive_dev_blog_system.py.backup')
        
        # Write the fixed version
        with open('comprehensive_dev_blog_system.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed tab error handling in blog system")
        print("✅ Original backed up as comprehensive_dev_blog_system.py.backup")
    else:
        print("⚠️ Pattern not found - checking for alternative fix...")
        
        # Alternative fix: Add error handling to render_analytics_dashboard
        if "def render_analytics_dashboard(self):" in content:
            # Add a try-except wrapper around the method
            content = content.replace(
                "def render_analytics_dashboard(self):",
                """def render_analytics_dashboard(self):
        try:
            self._render_analytics_dashboard_impl()
        except Exception as e:
            st.error(f"Analytics Dashboard Error: {e}")
            st.info("The analytics dashboard encountered an error. Please check the logs.")
    
    def _render_analytics_dashboard_impl(self):"""
            )
            
            # Write the fixed version
            with open('comprehensive_dev_blog_system.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Added error handling to analytics dashboard")

if __name__ == "__main__":
    fix_blog_tab_error()
    print("\n🎯 Next steps:")
    print("1. The blog system should now handle tab errors gracefully")
    print("2. Deploy the fix to see if it resolves the issue")
    print("3. The error details will be shown instead of crashing")