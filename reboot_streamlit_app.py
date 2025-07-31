#!/usr/bin/env python3
"""
Manual Streamlit App Reboot Utility
Run this when you need to force a Streamlit app restart
"""
from streamlit_reboot import StreamlitRebooter
from unicode_handler import safe_print

def main():
    """Manual reboot utility"""
    safe_print("🔄 TrenchCoat Pro - Streamlit App Reboot Utility")
    safe_print("=" * 50)
    
    rebooter = StreamlitRebooter()
    
    # Always trigger reboot (don't check health first)
    safe_print("🚀 Triggering Streamlit app reboot...")
    
    if rebooter.trigger_github_commit_hook():
        safe_print("✅ Reboot triggered successfully")
        
        # Wait for recovery
        if rebooter.wait_for_app_recovery():
            safe_print("🎉 App successfully rebooted and is responding!")
            return 0
        else:
            safe_print("❌ App reboot triggered but recovery failed")
            safe_print("💡 Try waiting a few more minutes or check Streamlit Cloud manually")
            return 1
    else:
        safe_print("❌ Failed to trigger app reboot")
        safe_print("💡 Check git status and GitHub connection")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())