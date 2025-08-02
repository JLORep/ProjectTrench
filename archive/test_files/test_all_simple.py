#!/usr/bin/env python3
"""
Simple test of all notification platforms
"""

import asyncio
import requests
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

async def test_all_notifications():
    """Test all platforms simultaneously"""
    
    print("TRENCHCOAT PRO - TESTING ALL PLATFORMS")
    print("=" * 40)
    
    # Test data
    symbol = "PEPE"
    price = 0.00001234
    change = 67.5
    confidence = 92.1
    
    print(f"Sending {symbol} Runner alert to all platforms...")
    print()
    
    # Test all platforms
    email_result = await test_email(symbol, price, change, confidence)
    telegram_result = await test_telegram(symbol, price, change, confidence)  
    discord_result = await test_discord(symbol, price, change, confidence)
    
    # Results
    platforms = [
        ("Email", email_result),
        ("Telegram", telegram_result), 
        ("Discord", discord_result)
    ]
    
    success_count = 0
    for platform, result in platforms:
        status = "SUCCESS" if result else "FAILED"
        print(f"{platform}: {status}")
        if result:
            success_count += 1
    
    print()
    print(f"RESULT: {success_count}/3 platforms working")
    
    if success_count == 3:
        print("ALL SYSTEMS OPERATIONAL!")
        print("Ready for live Runner alerts across all platforms!")
    
    return success_count

async def test_email(symbol, price, change, confidence):
    """Test email notification"""
    try:
        subject = f"Runner Alert: {symbol} (+{change:.1f}%)"
        
        html = f"""
        <html><body style="font-family: Arial;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #065f46; text-align: center;">TrenchCoat Pro Signal</h1>
            <div style="background: linear-gradient(135deg, #065f46, #10b981); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h2>RUNNER IDENTIFIED!</h2>
                <p style="font-size: 18px; font-weight: bold;">{symbol}</p>
            </div>
            <div style="margin: 20px 0;">
                <p><strong>Price:</strong> ${price:.6f}</p>
                <p><strong>Change:</strong> +{change:.1f}%</p>
                <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
            </div>
            <div style="text-align: center;">
                <a href="https://demo.trenchcoat.pro" style="background: #065f46; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">View Dashboard</a>
            </div>
        </div>
        </body></html>
        """
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = "TrenchCoat Pro <support@trenchcoat.pro>"
        message["To"] = "jameseymail@hotmail.co.uk"
        message.attach(MIMEText(html, "html"))
        
        context = ssl.create_default_context()
        with smtplib.SMTP("mail.privateemail.com", 587) as server:
            server.starttls(context=context)
            server.login("support@trenchcoat.pro", "TrenchF00t")
            server.send_message(message)
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

async def test_telegram(symbol, price, change, confidence):
    """Test Telegram notification"""
    try:
        message = f"""
TRENCHCOAT PRO SIGNAL

Coin: {symbol}
Price: ${price:.6f}
Change: +{change:.1f}%
Confidence: {confidence:.1f}%

RUNNER IDENTIFIED
Time: {datetime.now().strftime('%H:%M:%S')}
        """.strip()
        
        payload = {
            "chat_id": "8158865103",
            "text": message,
            "reply_markup": json.dumps({
                "inline_keyboard": [[
                    {"text": "Dashboard", "url": "https://demo.trenchcoat.pro"}
                ]]
            })
        }
        
        url = "https://api.telegram.org/bot8479347588:AAH27CeFD3iiyQM7l6YKk9bMlQznlCLAhxo/sendMessage"
        response = requests.post(url, json=payload, timeout=10)
        
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

async def test_discord(symbol, price, change, confidence):
    """Test Discord notification"""
    try:
        embed = {
            "title": "RUNNER IDENTIFIED!",
            "description": f"High-confidence Runner: **{symbol}**",
            "color": 0x10B981,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "Symbol", "value": f"**{symbol}**", "inline": True},
                {"name": "Price", "value": f"${price:.6f}", "inline": True},
                {"name": "Change", "value": f"+{change:.1f}%", "inline": True},
                {"name": "Confidence", "value": f"**{confidence:.1f}%**", "inline": True},
                {"name": "Time", "value": datetime.now().strftime('%H:%M:%S'), "inline": True},
                {"name": "Action", "value": "Consider entry position", "inline": True}
            ],
            "footer": {"text": "TrenchCoat Pro | AI Trading Signals"}
        }
        
        payload = {
            "content": f"@here RUNNER ALERT - {symbol} detected!",
            "username": "TrenchCoat Pro",
            "embeds": [embed]
        }
        
        url = "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"
        response = requests.post(url, json=payload, timeout=10)
        
        return response.status_code == 200
    except Exception as e:
        print(f"Discord error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_all_notifications())
    
    if result == 3:
        print("\nUNIFIED NOTIFICATION SYSTEM IS READY!")
        print("When a Runner is detected, alerts will go to:")
        print("- Email (professional HTML)")
        print("- Telegram (instant mobile alerts)")
        print("- Discord (community notifications)")