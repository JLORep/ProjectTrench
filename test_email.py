#!/usr/bin/env python3
"""
Quick email test for TrenchCoat Pro
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_test_email():
    """Send a simple test email"""
    
    # Email configuration
    smtp_server = "mail.privateemail.com"
    smtp_port = 587
    sender_email = "support@trenchcoat.pro"
    sender_password = "TrenchF00t"
    recipient_email = "jameseymail@hotmail.co.uk"  # Your personal email
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = "TrenchCoat Pro Email Test"
    message["From"] = "TrenchCoat Pro <support@trenchcoat.pro>"
    message["To"] = recipient_email
    
    # Create HTML content
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h1 style="color: #065f46; text-align: center;">TrenchCoat Pro Email Test</h1>
            
            <div style="background: linear-gradient(135deg, #065f46 0%, #10b981 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                <h2 style="margin: 0;">Email System Active!</h2>
                <p style="margin: 10px 0 0 0;">Professional email notifications are working</p>
            </div>
            
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #374151; margin: 0 0 10px 0;">Test Details:</h3>
                <p><strong>From:</strong> support@trenchcoat.pro</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Status:</strong> Email system operational</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://demo.trenchcoat.pro" style="background-color: #065f46; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block;">View Dashboard</a>
            </div>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                <p>TrenchCoat Pro | Professional Email System</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Add HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    try:
        # Create secure connection and send
        print("Connecting to SMTP server...")
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("Starting TLS...")
            server.starttls(context=context)
            print("Logging in...")
            server.login(sender_email, sender_password)
            print("Sending email...")
            server.send_message(message)
            
        print(f"SUCCESS: Test email sent to {recipient_email}")
        print("Check your inbox for the TrenchCoat Pro test email!")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to send email - {e}")
        return False

if __name__ == "__main__":
    print("TrenchCoat Pro Email Test")
    print("=" * 30)
    send_test_email()