#!/usr/bin/env python3
"""
INSTANT SHARE WITH BRAVO - NO INPUT REQUIRED
"""
import subprocess
import sys
import time
import requests

def check_dashboard_running():
    """Check if TrenchCoat is running"""
    try:
        response = requests.get("http://localhost:8501", timeout=3)
        return True
    except:
        return False

def main():
    print("TRENCHCOAT ELITE - INSTANT SHARE WITH BRAVO")
    print("=" * 50)
    
    # Check if dashboard is running
    if check_dashboard_running():
        print("Dashboard is running on http://localhost:8501")
        print("\nTo share with Bravo, choose ONE option:")
        print("\n1. SERVEO TUNNEL (Free, no signup):")
        print("   ssh -o StrictHostKeyChecking=no -R 80:localhost:8501 serveo.net")
        
        print("\n2. LOCALTUNNEL (Free, no signup):")
        print("   npm install -g localtunnel")
        print("   lt --port 8501")
        
        print("\n3. NGROK (Most reliable):")
        print("   Download from ngrok.com")
        print("   ngrok http 8501")
        
        print("\nBRAVO'S LOGIN:")
        print("Username: collaborator")
        print("Password: TrenchCoat2024!")
        
        print("\nDashboard shows:")
        print("- Live trading interface")
        print("- Performance monitoring") 
        print("- Strategy backtesting")
        print("- Risk management")
        print("- Full access to all features")
        
    else:
        print("Dashboard not running. Start with:")
        print("python -m streamlit run app.py")

if __name__ == "__main__":
    main()