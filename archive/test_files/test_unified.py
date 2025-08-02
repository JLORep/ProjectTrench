#!/usr/bin/env python3
"""
Test Unified Notification System - Simple Version
"""

import asyncio
import requests
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

async def test_all_platforms():
    """Test all notification platforms simultaneously"""
    
    print("TRENCHCOAT PRO UNIFIED NOTIFICATIONS TEST")
    print("=" * 45)
    
    # Test data
    test_data = {
        "symbol": "PEPE",
        "current_price": 0.00001234,
        "price_change_24h": 67.5,
        "volume_24h": 2500000,
        "runner_confidence": 92.1
    }
    
    print(f"Sending Runner alert for {test_data['symbol']} to all platforms...")
    print()
    
    # Create tasks for all platforms
    tasks = [
        send_email_test(test_data),
        send_telegram_test(test_data),
        send_discord_test(test_data)
    ]
    
    # Execute all simultaneously
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Report results
    platforms = ["Email", "Telegram", "Discord"]
    success_count = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"X {platforms[i]}: Failed - {result}")
        elif result:
            print(f"✓ {platforms[i]}: Success")
            success_count += 1
        else:
            print(f"X {platforms[i]}: Failed")
            
    print()
    print(f"Summary: {success_count}/{len(platforms)} platforms notified successfully")
    
    if success_count == len(platforms):
        print("ALL SYSTEMS OPERATIONAL - Ready for live Runner alerts!")
    
    return success_count > 0

async def send_email_test(coin_data):
    """Send email notification"""
    
    try:
        symbol = coin_data.get('symbol', 'Unknown')
        price = coin_data.get('current_price', 0)
        change_24h = coin_data.get('price_change_24h', 0)
        confidence = coin_data.get('runner_confidence', 0)
        
        subject = f"Runner Alert: {symbol} (+{change_24h:.1f}%)"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="color: #065f46; text-align: center;">TrenchCoat Pro Signal</h1>
                
                <div style="background: linear-gradient(135deg, #065f46 0%, #10b981 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                    <h2 style="margin: 0;">RUNNER IDENTIFIED!</h2>
                    <p style="margin: 10px 0 0 0; font-size: 18px; font-weight: bold;">{symbol}</p>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <h3 style="margin: 0 0 10px 0; color: #374151;">Price</h3>
                        <p style="margin: 0; color: #065f46; font-size: 16px; font-weight: bold;">${price:.6f}</p>
                    </div>
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <h3 style="margin: 0 0 10px 0; color: #374151;">Change</h3>
                        <p style="margin: 0; color: #10b981; font-size: 16px; font-weight: bold;">+{change_24h:.1f}%</p>
                    </div>
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <h3 style="margin: 0 0 10px 0; color: #374151;">Confidence</h3>
                        <p style="margin: 0; color: #065f46; font-size: 16px; font-weight: bold;">{confidence:.1f}%</p>
                    </div>
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <h3 style="margin: 0 0 10px 0; color: #374151;">Time</h3>
                        <p style="margin: 0; color: #065f46; font-size: 16px; font-weight: bold;">{datetime.now().strftime('%H:%M:%S')}</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://demo.trenchcoat.pro" style="background: #065f46; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">View Dashboard</a>
                </div>
                
                <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                    <p>TrenchCoat Pro | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = "TrenchCoat Pro <support@trenchcoat.pro>"
        message["To"] = "jameseymail@hotmail.co.uk"
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        context = ssl.create_default_context()
        with smtplib.SMTP("mail.privateemail.com", 587) as server:
            server.starttls(context=context)
            server.login("support@trenchcoat.pro", "TrenchF00t")
            server.send_message(message)
            
        return True
        
    except Exception as e:
        print(f"Email error: {e}")
        return False

async def send_telegram_test(coin_data):
    """Send Telegram notification"""
    
    try:
        symbol = coin_data.get('symbol', 'Unknown')
        price = coin_data.get('current_price', 0)
        change_24h = coin_data.get('price_change_24h', 0)
        confidence = coin_data.get('runner_confidence', 0)
        
        message = f"""
TRENCHCOAT PRO SIGNAL

Coin: {symbol}
Price: ${price:.6f}
Change: +{change_24h:.1f}%
Confidence: {confidence:.1f}%

RUNNER IDENTIFIED
Time: {datetime.now().strftime('%H:%M:%S')}

Signal by TrenchCoat Pro AI
        """.strip()
        
        keyboard = {
            "inline_keyboard": [[
                {"text": "View Dashboard", "url": "https://demo.trenchcoat.pro"},
                {"text": "Trade Now", "url": "https://app.trenchcoat.pro"}
            ]]
        }
        
        bot_token = "8479347588:AAH27CeFD3iiyQM7l6YKk9bMlQznlCLAhxo"
        chat_id = "8158865103"  # Your chat ID
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "reply_markup": json.dumps(keyboard)
        }
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        response = requests.post(url, json=payload, timeout=10)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

async def send_discord_test(coin_data):
    """Send Discord notification"""
    
    try:
        symbol = coin_data.get('symbol', 'Unknown')
        price = coin_data.get('current_price', 0)
        change_24h = coin_data.get('price_change_24h', 0)
        confidence = coin_data.get('runner_confidence', 0)
        
        embed = {
            "title": "RUNNER IDENTIFIED!",
            "description": f"High-confidence Runner detected: **{symbol}**",
            "color": 0x10B981,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {
                    "name": "Symbol",
                    "value": f"**{symbol}**",
                    "inline": True
                },
                {
                    "name": "Price",
                    "value": f"${price:.6f}",
                    "inline": True
                },
                {
                    "name": "24h Change",
                    "value": f"+{change_24h:.1f}%",
                    "inline": True
                },
                {
                    "name": "Confidence",
                    "value": f"**{confidence:.1f}%**",
                    "inline": True
                },
                {
                    "name": "Time",
                    "value": datetime.now().strftime('%H:%M:%S'),
                    "inline": True
                },
                {
                    "name": "Action",
                    "value": "Review and consider entry",
                    "inline": True
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro | AI Trading Signals"
            }
        }
        
        payload = {
            "content": f"@here RUNNER ALERT - {symbol} detected!",
            "username": "TrenchCoat Pro",
            "embeds": [embed]
        }
        
        webhook_url = "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        print(f"Discord error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_all_platforms())