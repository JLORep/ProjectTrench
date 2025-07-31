#!/usr/bin/env python3
"""
TrenchCoat Pro - Code Protection Strategy
Remove sensitive code from public repo
"""

def create_protected_version():
    """Create public-safe version of TrenchCoat Pro"""
    
    # Files to make public-safe
    files_to_protect = [
        'streamlit_app.py',
        'ultra_premium_dashboard.py',
        'premium_components.py'
    ]
    
    protection_notice = '''
"""
🛡️ TRENCHCOAT PRO - PUBLIC DEMO VERSION

⚠️  NOTICE: This is a demonstration version with:
- Sample data only (no live trading)
- Basic UI components
- Limited functionality
- No proprietary algorithms

🚀 Live Demo: https://trenchdemo.streamlit.app
🚀 Full version available at: https://trenchcoat.pro
💼 Commercial licensing: contact@trenchcoat.pro

© 2025 TrenchCoat Pro. All rights reserved.
"""
'''
    
    print("Creating protected public version...")
    
    # Add protection notice to all files
    for file in files_to_protect:
        if os.path.exists(file):
            with open(file, 'r') as f:
                content = f.read()
            
            # Add protection notice at top
            protected_content = protection_notice + "\n" + content
            
            # Remove sensitive sections (if any)
            protected_content = remove_sensitive_code(protected_content)
            
            with open(f"{file}.protected", 'w') as f:
                f.write(protected_content)
            
            print(f"Protected: {file}")

def remove_sensitive_code(content):
    """Remove or obfuscate sensitive code"""
    
    # Replace real API keys with demo keys
    content = content.replace('github_pat_', 'demo_token_')
    
    # Replace real trading logic with demo
    sensitive_patterns = [
        'real_trading_enabled = True',
        'live_trading = True', 
        'actual_api_key',
        'private_key',
        'secret_key'
    ]
    
    for pattern in sensitive_patterns:
        content = content.replace(pattern, 'demo_mode_only')
    
    return content

import os
create_protected_version()
print("✅ Protected versions created!")