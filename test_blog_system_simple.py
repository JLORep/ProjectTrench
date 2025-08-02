#!/usr/bin/env python3
"""
Simple test to check if blog system can be imported and initialized
"""

def test_blog_system():
    print("🔍 Testing Comprehensive Dev Blog System...")
    
    try:
        # Test import
        from comprehensive_dev_blog_system import ComprehensiveDevBlogSystem
        print("✅ Import successful")
        
        # Test initialization
        blog_system = ComprehensiveDevBlogSystem()
        print("✅ Initialization successful")
        
        # Check database
        import os
        db_path = "comprehensive_dev_blog.db"
        if os.path.exists(db_path):
            print(f"✅ Database exists: {db_path}")
            
            # Check database size
            size = os.path.getsize(db_path)
            print(f"   Database size: {size} bytes")
            
            # Check tables
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"   Tables: {[t[0] for t in tables]}")
            
            # Check post count
            try:
                cursor.execute("SELECT COUNT(*) FROM posts;")
                count = cursor.fetchone()[0]
                print(f"   Total posts: {count}")
            except:
                print("   ⚠️  Could not count posts")
            
            conn.close()
        else:
            print("❌ Database does not exist")
        
        # Check methods
        methods = [
            'render_comprehensive_interface',
            'render_create_update',
            'render_git_retrospective',
            'render_customer_focused',
            'render_webhook_integration'
        ]
        
        for method in methods:
            if hasattr(blog_system, method):
                print(f"✅ Method exists: {method}")
            else:
                print(f"❌ Method missing: {method}")
        
        print("\n✅ Blog system appears functional!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_blog_system()
    
    if success:
        print("\n💡 Next Steps:")
        print("1. Use the Blog tab in the dashboard (Tab 8)")
        print("2. Check if Queue Monitor shows queued messages")
        print("3. Start the queue processor to send Discord messages")
        print("4. Run simulation from within the dashboard, not standalone")
    else:
        print("\n❌ Blog system has issues that need fixing")