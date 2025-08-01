#!/usr/bin/env python3
"""
Deploy TrenchCoat Pro to Streamlit Cloud (UAT Environment)
"""
import os
import subprocess
import sys

def prepare_streamlit_deployment():
    """Prepare files for Streamlit Cloud deployment"""
    
    print("🚀 Preparing TrenchCoat Pro for Streamlit Cloud (UAT)...")
    
    # Create requirements.txt if not exists
    requirements = """streamlit>=1.47.0
plotly>=6.2.0
pandas>=2.2.1
numpy>=1.26.4
aiohttp>=3.10.10
loguru>=0.7.3
sqlite3
hashlib
datetime"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    # Create app_uat.py for UAT environment
    uat_config = '''#!/usr/bin/env python3
"""
TrenchCoat Pro - UAT Environment
Running in DEMO mode for testing
"""
import os

# Force UAT/Demo settings
os.environ['ENVIRONMENT'] = 'UAT'
os.environ['LIVE_TRADING_ENABLED'] = 'False'
os.environ['DEMO_MODE'] = 'True'

# Import and run main app
from app import main

if __name__ == "__main__":
    print("🔧 Running TrenchCoat Pro in UAT/DEMO mode")
    print("⚠️  Live trading is DISABLED")
    print("✅ Safe for testing and demonstration")
    main()
'''
    
    with open('app_uat.py', 'w') as f:
        f.write(uat_config)
    
    print("✅ UAT configuration created")
    print("\n📋 Next steps for Streamlit Cloud:")
    print("1. Commit and push to GitHub")
    print("2. Go to https://share.streamlit.io")
    print("3. Deploy 'app_uat.py' as the main file")
    print("4. Share the URL for UAT testing")

def main():
    prepare_streamlit_deployment()

if __name__ == "__main__":
    main()