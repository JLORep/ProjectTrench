#!/usr/bin/env python3
"""
Launch TrenchCoat Elite with secure internet access
"""
import subprocess
import sys
import time
from pyngrok import ngrok
import json

def setup_tunnel():
    """Set up secure ngrok tunnel"""
    print("🔐 Setting up secure tunnel for remote access...")
    
    # Start ngrok tunnel on port 8501
    try:
        # Configure ngrok
        ngrok.set_auth_token("YOUR_NGROK_TOKEN")  # Free account works
        
        # Create tunnel
        tunnel = ngrok.connect(8501, "http")
        public_url = tunnel.public_url
        
        print(f"\n✅ SUCCESS! TrenchCoat Elite is now accessible at:")
        print(f"🌐 Public URL: {public_url}")
        print(f"\n📝 Share these credentials with your collaborator:")
        print(f"   URL: {public_url}")
        print(f"   Username: collaborator")
        print(f"   Password: TrenchCoat2024!")
        print(f"\n⚠️  Keep these credentials secure!")
        
        # Save tunnel info
        with open("tunnel_info.json", "w") as f:
            json.dump({
                "public_url": public_url,
                "local_url": "http://localhost:8501",
                "username": "collaborator",
                "note": "Share the public URL and credentials with your collaborator"
            }, f, indent=2)
        
        return public_url
        
    except Exception as e:
        print(f"❌ Error setting up tunnel: {e}")
        print("\n💡 To use ngrok:")
        print("1. Sign up for free at https://ngrok.com")
        print("2. Get your auth token from the dashboard")
        print("3. Replace YOUR_NGROK_TOKEN in this script")
        return None

def launch_streamlit():
    """Launch Streamlit app"""
    print("\n🚀 Launching TrenchCoat Elite...")
    subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])

def main():
    print("💎 TRENCHCOAT ELITE - REMOTE ACCESS SETUP")
    print("=" * 50)
    
    # Launch Streamlit
    launch_streamlit()
    
    # Wait for Streamlit to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Set up tunnel
    public_url = setup_tunnel()
    
    if public_url:
        print("\n🎯 Remote access is ready!")
        print("Press Ctrl+C to stop the server and close the tunnel.")
        
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            ngrok.kill()
    else:
        print("\n❌ Failed to set up remote access")

if __name__ == "__main__":
    main()