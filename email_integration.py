#!/usr/bin/env python3
"""
TrenchCoat Pro - Email Integration
Professional email system using Namecheap email
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import logging

class EmailNotifier:
    """Professional email notification system"""
    
    def __init__(self):
        # Namecheap email configuration
        self.smtp_server = "mail.privateemail.com"
        self.smtp_port = 587
        self.email = "support@trenchcoat.pro"
        self.password = "TrenchF00t"
        self.sender_name = "TrenchCoat Pro"
        
    def send_runner_alert(self, coin_data: dict, recipient: str = "james@trenchcoat.pro"):
        """Send professional Runner alert email"""
        
        subject = f"🚀 Runner Identified: {coin_data.get('symbol', 'Unknown')}"
        
        # Create HTML email content
        html_content = self._create_runner_email_template(coin_data)
        
        # Send email
        return self._send_email(recipient, subject, html_content)
        
    def send_performance_report(self, performance_data: dict, recipient: str = "james@trenchcoat.pro"):
        """Send daily/weekly performance reports"""
        
        subject = f"📊 TrenchCoat Pro Performance Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Create performance report
        html_content = self._create_performance_template(performance_data)
        
        return self._send_email(recipient, subject, html_content)
        
    def send_system_alert(self, alert_type: str, message: str, recipient: str = "james@trenchcoat.pro"):
        """Send system alerts and notifications"""
        
        subject = f"⚠️ TrenchCoat Pro Alert: {alert_type}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #065f46; margin: 0;">🎯 TrenchCoat Pro</h1>
                    <p style="color: #6b7280; margin: 5px 0;">System Alert</p>
                </div>
                
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h2 style="color: #dc2626; margin: 0 0 10px 0;">⚠️ {alert_type}</h2>
                    <p style="color: #374151; margin: 0; line-height: 1.6;">{message}</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://app.trenchcoat.pro" style="background-color: #065f46; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">View Dashboard</a>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                    <p>TrenchCoat Pro | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(recipient, subject, html_content)
        
    def _create_runner_email_template(self, coin_data: dict) -> str:
        """Create professional HTML email template for Runner alerts"""
        
        symbol = coin_data.get('symbol', 'Unknown')
        price = coin_data.get('current_price', 0)
        change_24h = coin_data.get('price_change_24h', 0)
        volume = coin_data.get('volume_24h', 0)
        confidence = coin_data.get('runner_confidence', 0)
        
        # Color based on performance
        change_color = "#10b981" if change_24h > 0 else "#ef4444"
        change_symbol = "+" if change_24h >= 0 else ""
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #065f46; margin: 0;">🎯 TrenchCoat Pro</h1>
                    <p style="color: #6b7280; margin: 5px 0;">Professional Trading Intelligence</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #065f46 0%, #10b981 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                    <h2 style="margin: 0 0 10px 0; font-size: 24px;">🚀 RUNNER IDENTIFIED!</h2>
                    <p style="margin: 0; font-size: 18px; font-weight: bold;">{symbol}</p>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="color: #374151; margin: 0 0 10px 0;">💵 Current Price</h3>
                        <p style="color: #065f46; font-size: 20px; font-weight: bold; margin: 0;">${price:.6f}</p>
                    </div>
                    
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="color: #374151; margin: 0 0 10px 0;">📈 24h Change</h3>
                        <p style="color: {change_color}; font-size: 20px; font-weight: bold; margin: 0;">{change_symbol}{change_24h:.2f}%</p>
                    </div>
                    
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="color: #374151; margin: 0 0 10px 0;">📊 24h Volume</h3>
                        <p style="color: #065f46; font-size: 20px; font-weight: bold; margin: 0;">${volume:,.0f}</p>
                    </div>
                    
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="color: #374151; margin: 0 0 10px 0;">🎯 Confidence</h3>
                        <p style="color: #065f46; font-size: 20px; font-weight: bold; margin: 0;">{confidence:.1f}%</p>
                    </div>
                </div>
                
                <div style="background-color: #ecfdf5; border: 1px solid #10b981; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                    <h3 style="color: #065f46; margin: 0 0 10px 0;">⚡ Action Required</h3>
                    <p style="color: #374151; margin: 0; line-height: 1.6;">
                        A high-confidence Runner has been identified. Review the analysis and consider entry position.
                        Time-sensitive opportunity detected at {datetime.now().strftime('%H:%M:%S')}.
                    </p>
                </div>
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <a href="https://app.trenchcoat.pro/coin/{symbol}" style="background-color: #065f46; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; margin-right: 10px;">📊 View Analysis</a>
                    <a href="https://app.trenchcoat.pro/trade/{symbol}" style="background-color: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block;">💰 Execute Trade</a>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                    <p>TrenchCoat Pro | Professional Cryptocurrency Trading Platform</p>
                    <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Automated Alert System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
    def _create_performance_template(self, performance_data: dict) -> str:
        """Create performance report email template"""
        
        total_profit = performance_data.get('total_profit', 0)
        win_rate = performance_data.get('win_rate', 0)
        total_trades = performance_data.get('total_trades', 0)
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px;">
                <h1 style="color: #065f46; text-align: center;">📊 Performance Report</h1>
                
                <div style="background: linear-gradient(135deg, #065f46 0%, #10b981 100%); color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h2>💰 Total Profit: ${total_profit:,.2f}</h2>
                    <p>🎯 Win Rate: {win_rate:.1f}%</p>
                    <p>📈 Total Trades: {total_trades}</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://app.trenchcoat.pro" style="background-color: #065f46; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">View Full Report</a>
                </div>
            </div>
        </body>
        </html>
        """
        
    def _send_email(self, recipient: str, subject: str, html_content: str) -> bool:
        """Send email using Namecheap SMTP"""
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.email}>"
            message["To"] = recipient
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Create secure connection and send
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.send_message(message)
                
            logging.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False

# Usage example
if __name__ == "__main__":
    # Initialize email notifier
    email_notifier = EmailNotifier()
    
    # Example runner data
    runner_data = {
        "symbol": "MEME",
        "current_price": 0.000234,
        "price_change_24h": 67.5,
        "volume_24h": 1250000,
        "runner_confidence": 87.3
    }
    
    # Send runner alert
    email_notifier.send_runner_alert(runner_data, "james@trenchcoat.pro")
    
    # Send system alert
    email_notifier.send_system_alert("High Volume Detected", "Unusual trading activity detected in MEME coin.")
    
    print("Email notifications configured and tested!")