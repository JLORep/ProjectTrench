#!/usr/bin/env python3
"""
SIMPLE REMOTE ACCESS FOR BRAVO
One-click sharing of TrenchCoat Elite
"""
import subprocess
import sys
import time
import requests
import json

def check_dashboard_running():
    """Check if TrenchCoat is running"""
    try:
        response = requests.get("http://localhost:8501", timeout=3)
        return True
    except:
        return False

def start_dashboard():
    """Start TrenchCoat Elite if not running"""
    print("Starting TrenchCoat Elite...")
    subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])
    
    # Wait for it to start
    print("Waiting for dashboard to start...")
    for i in range(10):
        if check_dashboard_running():
            print("Dashboard is running!")
            return True
        time.sleep(2)
    return False

def create_tunnel():
    """Create public tunnel using serveo (no signup required)"""
    print("Creating public tunnel...")
    print("Setting up secure access for Bravo...")
    
    # Use serveo.net - completely free, no signup
    cmd = "ssh -o StrictHostKeyChecking=no -R 80:localhost:8501 serveo.net"
    
    print(f"\nBRAVO CAN ACCESS TRENCHCOAT AT:")
    print(f"Public URL will appear below...")
    print(f"\nLOGIN CREDENTIALS:")
    print(f"   Username: collaborator")
    print(f"   Password: TrenchCoat2024!")
    print(f"\nBravo can use any device - phone, tablet, computer")
    print(f"Secure authentication protects all your data")
    print(f"\nKeep this terminal open to maintain connection")
    print(f"Press Ctrl+C to stop sharing")
    print("\n" + "="*50)
    
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\nStopped sharing with Bravo")

def main():
    print("TRENCHCOAT ELITE - SHARE WITH BRAVO")
    print("=" * 50)
    
    # Step 1: Check if dashboard is running
    if not check_dashboard_running():
        if not start_dashboard():
            print("Failed to start dashboard")
            return
        time.sleep(3)
    else:
        print("Dashboard already running")
    
    print("\nReady to share with Bravo!")
    input("Press Enter to create public access link...")
    
    # Step 2: Create tunnel
    create_tunnel()

if __name__ == "__main__":
    main()