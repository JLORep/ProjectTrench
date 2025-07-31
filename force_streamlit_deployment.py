#!/usr/bin/env python3
"""
Force Streamlit deployment by making a small change to trigger redeployment
"""
import datetime
from unicode_handler import safe_print

def force_deployment():
    """Force Streamlit deployment by updating app timestamp"""
    
    # Read current streamlit_app.py
    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # Find the line with deployment timestamp and update it
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Look for existing timestamp line or add one
    updated = False
    for i, line in enumerate(content):
        if 'DEPLOYMENT_TIMESTAMP' in line or 'Last deployment:' in line:
            content[i] = f"# DEPLOYMENT_TIMESTAMP: {timestamp} - Force deployment\n"
            updated = True
            break
    
    # If no timestamp line found, add one at the top
    if not updated:
        content.insert(1, f"# DEPLOYMENT_TIMESTAMP: {timestamp} - Force deployment\n")
    
    # Write updated content
    with open('streamlit_app.py', 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    safe_print(f"✅ Updated streamlit_app.py with deployment timestamp: {timestamp}")
    safe_print("🚀 This should trigger Streamlit Cloud to redeploy the app")
    
    return timestamp

if __name__ == "__main__":
    force_deployment()