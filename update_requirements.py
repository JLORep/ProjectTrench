# Update requirements.txt with all necessary dependencies for the enrichment system
import subprocess
import sys

# Enhanced requirements with all free API integrations
requirements = """
# Core dependencies
pandas>=2.1.0
numpy>=1.24.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0

# Async HTTP and networking
aiohttp>=3.9.0
asyncio>=3.4.3
websockets>=12.0

# Data collection & APIs
ccxt>=4.0.0
python-binance>=1.0.0

# Telegram integration
python-telegram-bot>=20.0
telethon>=1.30.0

# Data validation & modeling
pydantic>=2.0.0
scikit-learn>=1.3.0
statsmodels>=0.14.0

# Visualization & dashboards
plotly>=5.17.0
dash>=2.14.0
streamlit>=1.28.0

# Mathematical libraries
scipy>=1.11.0
sympy>=1.12

# Game theory & optimization
nashpy>=0.0.35
cvxpy>=1.4.0

# Rich CLI interface
rich>=13.0.0

# Logging and utilities
loguru>=0.7.0
python-dotenv>=1.0.0
pyyaml>=6.0

# Additional utilities for enrichment
requests>=2.31.0
urllib3>=2.0.0
dateutils>=0.6.12
pytz>=2023.3

# Optional: For advanced analytics
ta-lib>=0.4.25
yfinance>=0.2.20
"""

def update_requirements():
    """Update the requirements.txt file"""
    with open('requirements.txt', 'w') as f:
        f.write(requirements.strip())
    
    print("✅ Updated requirements.txt with all enrichment dependencies")
    print("\n📦 To install all dependencies, run:")
    print("   pip install -r requirements.txt")
    print("\n🔧 For development setup:")
    print("   python -m venv venv")
    print("   venv\\Scripts\\activate  # Windows")
    print("   # source venv/bin/activate  # Linux/Mac")
    print("   pip install -r requirements.txt")

if __name__ == "__main__":
    update_requirements()