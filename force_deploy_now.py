#!/usr/bin/env python3
"""
Force deployment trigger - updates timestamp to force Streamlit rebuild
"""
import re
from datetime import datetime

def force_deployment():
    """Updates timestamp to trigger Streamlit rebuild"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update streamlit_app.py with deployment timestamp
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update the timestamp in the file
        content = re.sub(
            r'Updated: .*',
            f'Updated: {timestamp} - FORCE DEPLOY',
            content
        )
        
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Deployment timestamp updated: {timestamp}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating timestamp: {e}")
        return False

if __name__ == "__main__":
    force_deployment()