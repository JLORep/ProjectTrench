#!/usr/bin/env python3
"""Test blog system to find AttributeError"""

import sys
import traceback

try:
    from comprehensive_dev_blog_system import ComprehensiveDevBlogSystem
    
    blog = ComprehensiveDevBlogSystem()
    
    # Test initialization
    print("✅ Blog system initialized")
    
    # Test each method that might be missing
    methods_to_test = [
        'render_comprehensive_interface',
        'render_create_update',
        'render_git_retrospective',
        'render_customer_focused',
        'render_scheduling',
        'render_analytics_dashboard',
        'render_queue_monitor',
        'render_settings'
    ]
    
    for method_name in methods_to_test:
        if hasattr(blog, method_name):
            print(f"✅ Method exists: {method_name}")
        else:
            print(f"❌ MISSING METHOD: {method_name}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()