#!/usr/bin/env python3
"""
Simple tunnel creation for Bravo
"""
import subprocess
import sys
import requests

def check_dashboard():
    try:
        requests.get("http://localhost:8501", timeout=3)
        return True
    except:
        return False

def main():
    print("CREATING TUNNEL FOR BRAVO")
    print("=" * 30)
    
    if not check_dashboard():
        print("Start dashboard first: python -m streamlit run app.py")
        return
    
    print("Dashboard is running")
    print("\nSIMPLE OPTIONS FOR YOU:")
    print("\n1. Use your current setup:")
    print("   - Dashboard is already running")
    print("   - Already has authentication")
    print("   - Use port forwarding or VPN")
    
    print("\n2. Manual ngrok:")
    print("   - Download from ngrok.com")
    print("   - Run: ngrok http 8501")
    print("   - Share the https URL with Bravo")
    
    print("\n3. Use existing external IP:")
    print("   - Your external IP with port :8501")
    print("   - Configure router port forwarding")
    
    print("\nBRAVO'S LOGIN (any method):")
    print("Username: collaborator")  
    print("Password: TrenchCoat2024!")
    
    print("\nDashboard URL: http://localhost:8501")
    print("(Convert to public URL using method above)")

if __name__ == "__main__":
    main()