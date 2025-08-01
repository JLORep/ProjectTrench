#!/usr/bin/env python3
"""
Quick share TrenchCoat Elite - No signup required!
"""
import subprocess
import requests
import time
import json

def start_bore_tunnel():
    """Start bore.pub tunnel - no signup needed!"""
    print("🚀 Setting up public access (no signup required)...")
    
    try:
        # Download bore if not available
        print("📥 Setting up tunnel service...")
        
        # Use bore.pub - completely free, no signup
        cmd = "npx bore@latest local 8501 --to bore.pub"
        
        print(f"\n✅ Your collaborator can access TrenchCoat Elite at:")
        print(f"🌐 Public URL will appear below...")
        print(f"\n📝 Login credentials:")
        print(f"   Username: collaborator")
        print(f"   Password: TrenchCoat2024!")
        print(f"\n⏳ Starting tunnel...\n")
        
        # Run bore
        subprocess.run(cmd, shell=True)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nAlternative: Use serveo.net:")
        print("ssh -R 80:localhost:8501 serveo.net")

if __name__ == "__main__":
    print("💎 TRENCHCOAT ELITE - INSTANT SHARE")
    print("=" * 50)
    
    print("\n1️⃣ First, make sure TrenchCoat is running:")
    print("   python -m streamlit run app.py")
    
    print("\n2️⃣ Then run this tunnel...")
    input("\nPress Enter when TrenchCoat is running...")
    
    start_bore_tunnel()