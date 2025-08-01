#!/usr/bin/env python3
"""
AI PIPELINE LAUNCHER
Launch complete AI-enhanced trading system
"""
import asyncio
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

def launch_webhook_server():
    """Launch the AI webhook server"""
    logger.info("🚀 Starting AI webhook server...")
    subprocess.run([
        sys.executable, "-c",
        "from src.ai.realtime_webhook import start_webhook_server; start_webhook_server()"
    ])

def launch_enhanced_monitoring():
    """Launch enhanced Telegram monitoring"""
    logger.info("📡 Starting enhanced Telegram monitoring...")
    subprocess.run([
        sys.executable, "-c", 
        "import asyncio; from src.ai.enhanced_telegram_monitor import run_enhanced_monitoring; asyncio.run(run_enhanced_monitoring())"
    ])

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    logger.info("💎 Starting TrenchCoat Elite dashboard...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

async def test_ai_pipeline():
    """Test the AI pipeline with sample data"""
    logger.info("🧪 Testing AI pipeline...")
    
    import aiohttp
    
    # Test signal
    test_signal = {
        "symbol": "PEPE",
        "contract_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "source": "atm.day",
        "message": "🚀 PEPE is pumping! Target: $0.000020",
        "confidence": 0.8,
        "timestamp": "2024-01-20T12:00:00Z"
    }
    
    # Wait for webhook server to start
    await asyncio.sleep(3)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/webhook/telegram-signal",
                json=test_signal
            ) as response:
                result = await response.json()
                logger.info(f"✅ Pipeline test result: {result}")
                
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {e}")

def main():
    """Main launcher"""
    print("🤖 TRENCHCOAT AI PIPELINE LAUNCHER")
    print("=" * 50)
    
    print("\nAvailable components:")
    print("1. AI Webhook Server (port 8000)")
    print("2. Enhanced Telegram Monitor")
    print("3. TrenchCoat Elite Dashboard (port 8501)")
    print("4. Complete Pipeline (all components)")
    print("5. Test Pipeline")
    
    choice = input("\nSelect component to launch (1-5): ").strip()
    
    if choice == "1":
        launch_webhook_server()
    elif choice == "2":
        launch_enhanced_monitoring()
    elif choice == "3":
        launch_dashboard()
    elif choice == "4":
        print("\n🚀 Launching complete AI pipeline...")
        
        # Use ThreadPoolExecutor to run components in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Start all components
            futures = [
                executor.submit(launch_webhook_server),
                executor.submit(launch_enhanced_monitoring),
                executor.submit(launch_dashboard)
            ]
            
            print("✅ All components started!")
            print("📊 Dashboard: http://localhost:8501")
            print("🤖 AI API: http://localhost:8000")
            print("\nPress Ctrl+C to stop all components")
            
            try:
                # Wait for all futures (they'll run indefinitely)
                for future in futures:
                    future.result()
            except KeyboardInterrupt:
                print("\n👋 Shutting down AI pipeline...")
                
    elif choice == "5":
        print("\n🧪 Testing AI pipeline...")
        asyncio.run(test_ai_pipeline())
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()