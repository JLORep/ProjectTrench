#!/usr/bin/env python3
"""
TrenchCoat Pro - Discord Webhook Integration System
Professional webhook management for all Discord channels
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import time

class TrenchCoatDiscordWebhooks:
    """Professional Discord webhook management system"""
    
    def __init__(self):
        # Primary webhook URLs for core channels
        self.webhooks = {
            # Trading Category Webhooks
            'analytics': 'https://discord.com/api/webhooks/1400549103305490595/ld4vTMpNY3KhVnA4aPgbciPdlwfg1XjsWeaeozk7AxWHiGreHtNZAtaoKlpIfklEqViI',
            'performance': 'https://discord.com/api/webhooks/1400546335047946363/tj9JJJCYAg4d9-VV4vnX3BgAfrtrxZKi2aqGEW2N3S_IsVaRGra9PsreJDQUNhe2i_Qe',
            'live_trades': 'https://discord.com/api/webhooks/1400564409520099498/cBmLi9RekqYXhhiPY2NYzjDoNMk5CwH6s2Qnpn3brvA2enc-mvlioeB8SNzJAjNKKky5',
            # Development Category Webhooks
            'bug_fixes': 'https://discord.com/api/webhooks/1400567015089115177/dtKTrDobQMgXRMTdXfvDMai33SWYFTmqqIDSxlLnJDJwQPHt80zLkV_mqltD_wqq37wc'
        }
        
        # Channel color schemes (matching Discord structure)
        self.colors = {
            'analytics': 0xF59E0B,  # Gold theme for trading
            'performance': 0x10B981,  # Green for performance 
            'live_trades': 0xEF4444,  # Red for urgent trades
            'bug_fixes': 0x8B5CF6,  # Purple for development
            'success': 0x10B981,  # Green
            'warning': 0xF59E0B,  # Yellow
            'error': 0xEF4444,  # Red
            'info': 0x3B82F6  # Blue
        }

    def send_analytics_report(self, data: Dict[str, Any]) -> bool:
        """Send analytics report to #analytics channel"""
        embed = {
            "title": "📊 TrenchCoat Pro - Analytics Report",
            "description": f"**Market Analysis Update** • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "color": self.colors['analytics'],
            "fields": [
                {
                    "name": "🎯 Win Rate Analysis",
                    "value": f"**Current**: {data.get('win_rate', 'N/A')}%\n**Target**: 75%+\n**Trend**: {data.get('trend', 'Stable')}",
                    "inline": True
                },
                {
                    "name": "📈 Market Conditions",
                    "value": f"**Volatility**: {data.get('volatility', 'Medium')}\n**Volume**: {data.get('volume', 'Normal')}\n**Sentiment**: {data.get('sentiment', 'Neutral')}",
                    "inline": True
                },
                {
                    "name": "🔍 Key Metrics",
                    "value": f"**Signals Today**: {data.get('signals_today', 0)}\n**Accuracy**: {data.get('accuracy', 'N/A')}%\n**Profit Factor**: {data.get('profit_factor', 'N/A')}",
                    "inline": True
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro • Advanced Trading Intelligence",
                "icon_url": "https://github.com/JLORep/ProjectTrench/raw/main/assets/logo.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._send_webhook('analytics', embed=embed)

    def send_performance_update(self, data: Dict[str, Any]) -> bool:
        """Send performance metrics to #performance channel"""
        embed = {
            "title": "🎯 Performance Metrics Update",
            "description": f"**Trading Performance Summary** • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "color": self.colors['performance'],
            "fields": [
                {
                    "name": "💰 Portfolio Performance",
                    "value": f"**Total Value**: ${data.get('portfolio_value', '0'):,}\n**Daily P&L**: {data.get('daily_pnl', '+$0')}\n**ROI**: {data.get('roi', '0')}%",
                    "inline": True
                },
                {
                    "name": "📊 Success Metrics",
                    "value": f"**Win Rate**: {data.get('win_rate', '0')}%\n**Profit Factor**: {data.get('profit_factor', '0.0')}\n**Sharpe Ratio**: {data.get('sharpe_ratio', '0.0')}",
                    "inline": True
                },
                {
                    "name": "⚡ Trade Statistics",
                    "value": f"**Total Trades**: {data.get('total_trades', 0)}\n**Winners**: {data.get('winning_trades', 0)}\n**Avg Win**: {data.get('avg_win', '0')}%",
                    "inline": True
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro • Performance Analytics",
                "icon_url": "https://github.com/JLORep/ProjectTrench/raw/main/assets/logo.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._send_webhook('performance', embed=embed)

    def send_live_trade_alert(self, trade_data: Dict[str, Any]) -> bool:
        """Send live trade execution to #live-trades channel"""
        action = trade_data.get('action', 'TRADE').upper()
        symbol = trade_data.get('symbol', 'UNKNOWN')
        
        # Determine color based on action
        if action in ['BUY', 'ENTRY']:
            color = self.colors['success']
            emoji = "🟢"
        elif action in ['SELL', 'EXIT']:
            color = self.colors['warning'] 
            emoji = "🟡"
        else:
            color = self.colors['info']
            emoji = "🔵"
            
        embed = {
            "title": f"{emoji} LIVE TRADE EXECUTED - {symbol}",
            "description": f"**{action}** • {datetime.now().strftime('%H:%M:%S')} UTC",
            "color": color,
            "fields": [
                {
                    "name": "📋 Trade Details",
                    "value": f"**Symbol**: {symbol}\n**Action**: {action}\n**Size**: {trade_data.get('size', 'N/A')}\n**Price**: ${trade_data.get('price', '0.00')}",
                    "inline": True
                },
                {
                    "name": "🎯 Strategy Info",
                    "value": f"**Strategy**: {trade_data.get('strategy', 'Unknown')}\n**Confidence**: {trade_data.get('confidence', '0')}%\n**Risk Level**: {trade_data.get('risk_level', 'Medium')}",
                    "inline": True
                },
                {
                    "name": "📊 Expected Outcome",
                    "value": f"**Target**: {trade_data.get('target', 'N/A')}\n**Stop Loss**: {trade_data.get('stop_loss', 'N/A')}\n**R:R Ratio**: {trade_data.get('risk_reward', 'N/A')}",
                    "inline": True
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro • Live Trading Engine",
                "icon_url": "https://github.com/JLORep/ProjectTrench/raw/main/assets/logo.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._send_webhook('live_trades', content=f"@here **LIVE TRADE**: {symbol} {action}", embed=embed)

    def send_bug_fix_notification(self, fix_data: Dict[str, Any]) -> bool:
        """Send bug fix notification to #bug-fixes channel"""
        bug_type = fix_data.get('type', 'General').upper()
        severity = fix_data.get('severity', 'Medium').upper()
        
        # Determine color and emoji based on severity
        if severity == 'CRITICAL':
            color = self.colors['error']
            emoji = "🚨"
        elif severity == 'HIGH':
            color = self.colors['warning']
            emoji = "🔥"
        elif severity == 'MEDIUM':
            color = self.colors['info']
            emoji = "🔧"
        else:  # LOW
            color = self.colors['success']
            emoji = "✨"
            
        embed = {
            "title": f"{emoji} BUG FIX DEPLOYED - {bug_type}",
            "description": f"**{severity} Priority Fix** • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "color": color,
            "fields": [
                {
                    "name": "🐛 Issue Description",
                    "value": f"**Problem**: {fix_data.get('problem', 'N/A')}\n**Component**: {fix_data.get('component', 'Unknown')}\n**Severity**: {severity}",
                    "inline": True
                },
                {
                    "name": "🔧 Fix Details",
                    "value": f"**Solution**: {fix_data.get('solution', 'N/A')}\n**Files Changed**: {fix_data.get('files_changed', 0)}\n**Lines Modified**: {fix_data.get('lines_modified', 0)}",
                    "inline": True
                },
                {
                    "name": "✅ Verification",
                    "value": f"**Tested**: {fix_data.get('tested', 'Yes')}\n**Deployed**: {fix_data.get('deployed', 'Yes')}\n**Status**: {fix_data.get('status', 'Fixed')}",
                    "inline": True
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro • Bug Fix System",
                "icon_url": "https://github.com/JLORep/ProjectTrench/raw/main/assets/logo.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add commit info if provided
        if fix_data.get('commit_hash'):
            embed['fields'].append({
                "name": "📝 Commit Info",
                "value": f"**Hash**: {fix_data.get('commit_hash', 'N/A')[:8]}\n**Message**: {fix_data.get('commit_message', 'N/A')}\n**Author**: {fix_data.get('author', 'TrenchCoat Pro Team')}",
                "inline": False
            })
        
        return self._send_webhook('bug_fixes', embed=embed)

    def send_system_status(self, status_data: Dict[str, Any], channel: str = 'analytics') -> bool:
        """Send system status update"""
        status = status_data.get('status', 'unknown').upper()
        
        if status == 'ONLINE':
            color = self.colors['success']
            emoji = "🟢"
        elif status == 'WARNING':
            color = self.colors['warning']
            emoji = "🟡"
        elif status == 'ERROR':
            color = self.colors['error']
            emoji = "🔴"
        else:
            color = self.colors['info']
            emoji = "🔵"
            
        embed = {
            "title": f"{emoji} System Status: {status}",
            "description": f"**TrenchCoat Pro System Update** • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "color": color,
            "fields": [
                {
                    "name": "🖥️ System Health",
                    "value": f"**Status**: {status}\n**Uptime**: {status_data.get('uptime', 'N/A')}\n**CPU**: {status_data.get('cpu_usage', 'N/A')}%",
                    "inline": True
                },
                {
                    "name": "📡 API Connections",
                    "value": f"**Active APIs**: {status_data.get('active_apis', '0')}/6\n**Response Time**: {status_data.get('avg_response', 'N/A')}ms\n**Success Rate**: {status_data.get('api_success', 'N/A')}%",
                    "inline": True
                },
                {
                    "name": "🔄 Trading Engine",
                    "value": f"**Status**: {status_data.get('trading_status', 'Unknown')}\n**Active Trades**: {status_data.get('active_trades', 0)}\n**Last Update**: {status_data.get('last_update', 'N/A')}",
                    "inline": True
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro • System Monitor",
                "icon_url": "https://github.com/JLORep/ProjectTrench/raw/main/assets/logo.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._send_webhook(channel, embed=embed)

    def _send_webhook(self, channel: str, content: str = None, embed: Dict = None) -> bool:
        """Internal method to send webhook message"""
        if channel not in self.webhooks:
            print(f"ERROR: Unknown channel: {channel}")
            return False
            
        webhook_url = self.webhooks[channel]
        
        payload = {}
        if content:
            payload['content'] = content
        if embed:
            payload['embeds'] = [embed]
            
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 204:
                print(f"SUCCESS: Sent to #{channel}")
                return True
            else:
                print(f"FAILED: #{channel} - Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"ERROR: #{channel} - {str(e)}")
            return False

    def test_all_webhooks(self) -> Dict[str, bool]:
        """Test all webhook connections"""
        results = {}
        
        print("Testing TrenchCoat Pro Discord Webhooks...")
        
        # Test analytics webhook
        results['analytics'] = self.send_analytics_report({
            'win_rate': 78.3,
            'trend': 'Bullish',
            'volatility': 'High',
            'volume': 'Above Average',
            'sentiment': 'Positive',
            'signals_today': 15,
            'accuracy': 82.1,
            'profit_factor': 2.4
        })
        
        time.sleep(1)  # Rate limiting
        
        # Test performance webhook
        results['performance'] = self.send_performance_update({
            'portfolio_value': 127845,
            'daily_pnl': '+$12,845',
            'roi': 11.2,
            'win_rate': 78.3,
            'profit_factor': 2.4,
            'sharpe_ratio': 3.1,
            'total_trades': 234,
            'winning_trades': 183,
            'avg_win': 15.7
        })
        
        time.sleep(1)  # Rate limiting
        
        # Test live trades webhook
        results['live_trades'] = self.send_live_trade_alert({
            'action': 'BUY',
            'symbol': '$PEPE',
            'size': '1000 USDC',
            'price': '0.00001234',
            'strategy': 'Whale Following',
            'confidence': 92,
            'risk_level': 'Medium',
            'target': '+250%',
            'stop_loss': '-15%',
            'risk_reward': '16.7:1'
        })
        
        time.sleep(1)  # Rate limiting
        
        # Test bug fixes webhook
        results['bug_fixes'] = self.send_bug_fix_notification({
            'type': 'UI',
            'severity': 'Medium',
            'problem': 'Coins spreadsheet flickering and showing resize bars',
            'component': 'Streamlit Dashboard',
            'solution': 'Fixed width constraints and CSS to prevent dynamic resizing',
            'files_changed': 1,
            'lines_modified': 25,
            'tested': 'Yes',
            'deployed': 'Yes',
            'status': 'Fixed',
            'commit_hash': '749f6f6a1b2c3d4e5f6789',
            'commit_message': 'Fix: Resolve spreadsheet flickering issue',
            'author': 'Claude Code Assistant'
        })
        
        return results

# Quick test script
if __name__ == "__main__":
    print("TrenchCoat Pro - Discord Webhook System")
    print("=" * 50)
    
    webhooks = TrenchCoatDiscordWebhooks()
    results = webhooks.test_all_webhooks()
    
    print("\nTest Results:")
    for channel, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  #{channel}: {status}")
    
    if all(results.values()):
        print("\nAll webhooks are working perfectly!")
        print("Your Discord channels are ready for live updates.")
    else:
        print("\nSome webhooks failed. Please check Discord permissions.")