#!/usr/bin/env python3
"""
Force Streamlit rebuild by making significant file changes
"""
import os
import time
from datetime import datetime
from unicode_handler import safe_print

def force_rebuild():
    """Force Streamlit to rebuild by making file changes"""
    
    # Method 1: Update requirements.txt with timestamp comment
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    # Remove any existing timestamp comments
    lines = [line for line in content.split('\n') if not line.startswith('# Updated:')]
    
    # Add new timestamp comment
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lines.append(f'# Updated: {timestamp} - Force rebuild')
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(lines))
    
    safe_print(f"✅ Updated requirements.txt with timestamp: {timestamp}")
    
    # Method 2: Create a .streamlit/config.toml change
    config_content = f"""[global]
developmentMode = false

[server]
runOnSave = true
port = 8501

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#10b981"
backgroundColor = "#0f0f0f"  
secondaryBackgroundColor = "#1a1a1a"
textColor = "#ffffff"

# Force rebuild: {timestamp}
"""
    
    os.makedirs('.streamlit', exist_ok=True)
    with open('.streamlit/config.toml', 'w') as f:
        f.write(config_content)
    
    safe_print(f"✅ Updated .streamlit/config.toml with timestamp: {timestamp}")
    
    return timestamp

if __name__ == "__main__":
    timestamp = force_rebuild()
    safe_print(f"🚀 Ready to commit force rebuild changes - {timestamp}")