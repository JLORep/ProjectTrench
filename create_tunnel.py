#!/usr/bin/env python3
"""
Create instant tunnel for Bravo access
"""
from pyngrok import ngrok
import time
import requests

def check_dashboard():
    """Check if dashboard is running"""
    try:
        response = requests.get("http://localhost:8501", timeout=3)
        return True
    except:
        return False

def create_ngrok_tunnel():
    """Create ngrok tunnel"""
    try:
        print("Creating public tunnel...")
        
        # Create tunnel
        tunnel = ngrok.connect(8501, "http")
        public_url = tunnel.public_url
        
        print("\n" + "="*60)
        print("SUCCESS! BRAVO CAN ACCESS TRENCHCOAT NOW!")
        print("="*60)
        print(f"\nPUBLIC URL: {public_url}")
        print(f"\nLOGIN CREDENTIALS FOR BRAVO:")
        print(f"Username: collaborator")
        print(f"Password: TrenchCoat2024!")
        print(f"\nBravo can use this URL on ANY device:")
        print(f"- Computer, phone, tablet")
        print(f"- Works from anywhere in the world")
        print(f"- Secure HTTPS connection")
        print(f"\nTELL BRAVO: Go to {public_url}")
        print("="*60)
        
        print(f"\nTunnel is ACTIVE! Press Ctrl+C to stop sharing...")
        
        # Keep tunnel alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping tunnel...")
            ngrok.kill()
            print("Tunnel stopped. Bravo can no longer access.")
            
    except Exception as e:
        print(f"Error creating tunnel: {e}")
        print("\nFree ngrok might need signup. Try this instead:")
        print("1. Go to https://ngrok.com")
        print("2. Sign up free")
        print("3. Download ngrok")
        print("4. Run: ngrok http 8501")

def main():
    print("CREATING PUBLIC ACCESS FOR BRAVO")
    print("="*40)
    
    if not check_dashboard():
        print("Dashboard not running! Start it first:")
        print("python -m streamlit run app.py")
        return
    
    print("Dashboard is running ✓")
    create_ngrok_tunnel()

if __name__ == "__main__":
    main()