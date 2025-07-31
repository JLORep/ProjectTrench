#!/usr/bin/env python3
"""
TrenchCoat Pro - Professional Branding System
Custom logos, icons, and visual elements for ultra-professional appearance
"""
import streamlit as st
import base64
from typing import Dict, List
import io

class BrandingSystem:
    """Professional branding and visual elements"""
    
    def __init__(self):
        self.brand_colors = {
            'primary': '#10b981',      # TrenchCoat Emerald
            'primary_dark': '#059669',  # Dark Emerald
            'primary_light': '#34d399', # Light Emerald
            'secondary': '#1f2937',     # Professional Dark
            'accent': '#3b82f6',        # Premium Blue
            'success': '#22c55e',       # Success Green
            'warning': '#f59e0b',       # Warning Amber
            'danger': '#ef4444',        # Danger Red
            'info': '#06b6d4',         # Info Cyan
            'purple': '#8b5cf6',        # Premium Purple
            'gold': '#f59e0b',         # Gold Accent
            'silver': '#6b7280',        # Silver Gray
            'background': '#0f0f0f',    # Deep Black
            'surface': '#1a1a1a',      # Dark Surface
            'text_primary': '#f9fafb',  # Primary Text
            'text_secondary': '#9ca3af', # Secondary Text
            'border': 'rgba(16, 185, 129, 0.3)', # Emerald Border
        }
        
        # Professional emoji set for crypto trading
        self.brand_emojis = {
            # Core branding
            'logo': '🎯',
            'brand': '💎',
            'premium': '👑',
            
            # Trading & Finance
            'trading': '📈',
            'profit': '💰',
            'loss': '📉',   
            'signal': '🚨',
            'runner': '🚀',
            'gem': '💎',
            'moon': '🌙',
            'bull': '🐂',
            'bear': '🐻',
            'money': '💵',
            'chart': '📊',
            'trend_up': '⬆️',
            'trend_down': '⬇️',
            
            # Technology
            'ai': '🤖',
            'ml': '🧠',
            'analytics': '📊',
            'data': '📊',
            'api': '🔗',
            'database': '🗄️',
            'processing': '⚙️',
            'computing': '💻',
            'algorithm': '🔬',
            'model': '🏗️',
            
            # Notifications & Communication
            'alert': '🔔',
            'notification': '📢',
            'telegram': '📱',
            'discord': '💬',
            'email': '✉️',
            'whatsapp': '📞',
            'message': '💌',
            
            # Status & Quality
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'verified': '✅',
            'premium_badge': '🏆',
            'security': '🔒',
            'shield': '🛡️',
            'fire': '🔥',
            'lightning': '⚡',
            'star': '⭐',
            
            # Features
            'dashboard': '📊',
            'monitoring': '👁️',
            'live': '🔴',
            'real_time': '⏱️',
            'history': '📚',
            'report': '📋',
            'export': '📤',
            'import': '📥',
            'search': '🔍',
            'filter': '🔽',
            'settings': '⚙️',
            'config': '🎛️',
            
            # Performance
            'speed': '💨',
            'efficiency': '⚡',
            'accuracy': '🎯',
            'precision': '🔬',
            'optimization': '📈',
            'performance': '🏃‍♂️',
            
            # Social & Community
            'community': '👥',
            'team': '👨‍💻',
            'users': '👤',
            'feedback': '💬',
            'support': '🆘',
            'help': '❓',
            
            # Development
            'code': '💻',
            'bug': '🐛',
            'fix': '🔧',
            'update': '🆙',
            'version': '🏷️',
            'release': '🚀',
            'deploy': '🌐',
            'test': '🧪',
            
            # Time & Schedule
            'time': '🕐',
            'calendar': '📅',
            'schedule': '⏰',
            'timer': '⏳',
            'clock': '🕒',
            
            # Location & Global
            'global': '🌍',
            'location': '📍',
            'network': '🌐',
            'connection': '🔗',
            
            # Special Effects
            'sparkles': '✨',
            'boom': '💥',
            'rocket_launch': '🚀',
            'celebration': '🎉',
            'trophy': '🏆'
        }
    
    def get_logo_svg(self, size: int = 64, style: str = "default") -> str:
        """Generate TrenchCoat Pro logo as SVG"""
        
        if style == "minimal":
            return f"""
            <svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:{self.brand_colors['primary']};stop-opacity:1" />
                        <stop offset="100%" style="stop-color:{self.brand_colors['primary_dark']};stop-opacity:1" />
                    </linearGradient>
                </defs>
                <circle cx="32" cy="32" r="30" fill="url(#logoGradient)" stroke="{self.brand_colors['primary_light']}" stroke-width="2"/>
                <text x="32" y="38" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="24" font-weight="bold">TC</text>
            </svg>
            """
        
        elif style == "detailed":
            return f"""
            <svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:{self.brand_colors['primary']};stop-opacity:1" />
                        <stop offset="50%" style="stop-color:{self.brand_colors['accent']};stop-opacity:1" />
                        <stop offset="100%" style="stop-color:{self.brand_colors['primary_dark']};stop-opacity:1" />
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                        <feMerge> 
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                <circle cx="32" cy="32" r="30" fill="url(#logoGradient)" stroke="{self.brand_colors['primary_light']}" stroke-width="2" filter="url(#glow)"/>
                <polygon points="20,20 44,20 40,32 48,32 32,48 16,32 24,32" fill="white" opacity="0.9"/>
                <text x="32" y="54" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="8" font-weight="bold">PRO</text>
            </svg>
            """
        
        else:  # default
            return f"""
            <svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:{self.brand_colors['primary']};stop-opacity:1" />
                        <stop offset="100%" style="stop-color:{self.brand_colors['primary_dark']};stop-opacity:1" />
                    </linearGradient>
                </defs>
                <rect x="4" y="4" width="56" height="56" rx="12" ry="12" fill="url(#logoGradient)" stroke="{self.brand_colors['primary_light']}" stroke-width="2"/>
                <text x="32" y="40" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="18" font-weight="bold">🎯</text>
                <text x="32" y="52" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="6" font-weight="normal">TRENCH</text>
            </svg>
            """
    
    def get_feature_icon(self, feature: str, size: int = 24) -> str:
        """Get professional icon for features"""
        
        icon_map = {
            'dashboard': '📊',
            'analytics': '📈', 
            'live_data': '📡',
            'ml_models': '🤖',
            'trading': '💰',
            'notifications': '🔔',
            'telegram': '📱',
            'discord': '💬',
            'historic_data': '📚',
            'validation': '✅',
            'risk_assessment': '🛡️',
            'performance': '🚀',
            'enrichment': '🔍',
            'signals': '📢',
            'monitoring': '👁️',
            'automation': '⚙️',
            'api': '🔗',
            'database': '🗄️',
            'security': '🔒',
            'reports': '📋'
        }
        
        emoji = icon_map.get(feature, '⭐')
        
        return f"""
        <div style="display: inline-flex; align-items: center; justify-content: center; 
                    width: {size}px; height: {size}px; font-size: {size-4}px;">
            {emoji}
        </div>
        """
    
    def get_status_badge(self, status: str, text: str = None) -> str:
        """Get professional status badge"""
        
        if text is None:
            text = status.title()
        
        badge_configs = {
            'live': {
                'bg': self.brand_colors['success'],
                'icon': '🟢',
                'pulse': True
            },
            'demo': {
                'bg': self.brand_colors['info'],
                'icon': '🔵',
                'pulse': False
            },
            'processing': {
                'bg': self.brand_colors['warning'],
                'icon': '🟡',
                'pulse': True
            },
            'error': {
                'bg': self.brand_colors['danger'],
                'icon': '🔴',
                'pulse': False
            },
            'verified': {
                'bg': self.brand_colors['success'],
                'icon': '✅',
                'pulse': False
            },
            'premium': {
                'bg': self.brand_colors['gold'],
                'icon': '👑',
                'pulse': False
            }
        }
        
        config = badge_configs.get(status, {
            'bg': self.brand_colors['silver'],
            'icon': '⚪',
            'pulse': False
        })
        
        pulse_animation = """
            animation: pulse 2s infinite;
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
        """ if config['pulse'] else ""
        
        return f"""
        <div style="display: inline-flex; align-items: center; gap: 6px; 
                    background: {config['bg']}; color: white; 
                    padding: 4px 12px; border-radius: 16px; 
                    font-size: 12px; font-weight: 600; {pulse_animation}">
            <span>{config['icon']}</span>
            <span>{text}</span>
        </div>
        """
    
    def get_metric_card(self, title: str, value: str, delta: str = None, 
                       icon: str = None, color: str = None) -> str:
        """Get professional metric card"""
        
        if color is None:
            color = self.brand_colors['primary']
        
        if icon is None:
            icon = '📊'
        
        delta_html = ""
        if delta:
            delta_color = self.brand_colors['success'] if delta.startswith('+') else self.brand_colors['danger']
            delta_html = f"""
            <div style="color: {delta_color}; font-size: 14px; font-weight: 600; margin-top: 4px;">
                {delta}
            </div>
            """
        
        return f"""
        <div style="background: rgba(255, 255, 255, 0.05); 
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 16px; padding: 20px; margin: 8px 0;
                    transition: all 0.3s ease; position: relative; overflow: hidden;">
            
            <!-- Gradient overlay -->
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; 
                        background: linear-gradient(90deg, {color} 0%, {self.brand_colors['primary_light']} 100%);"></div>
            
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <div style="font-size: 24px;">{icon}</div>
                <div style="color: {self.brand_colors['text_secondary']}; font-size: 14px; font-weight: 500;">
                    {title}
                </div>
            </div>
            
            <div style="color: {color}; font-size: 28px; font-weight: 700; margin-bottom: 4px;">
                {value}
            </div>
            
            {delta_html}
        </div>
        """
    
    def get_feature_showcase(self, features: List[Dict[str, str]]) -> str:
        """Get professional feature showcase grid"""
        
        feature_cards = []
        
        for feature in features:
            icon = self.get_feature_icon(feature.get('key', 'default'), 32)
            
            card = f"""
            <div style="background: rgba(255, 255, 255, 0.03); 
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 20px; padding: 24px; margin: 12px;
                        transition: all 0.3s ease; cursor: pointer;
                        min-height: 200px; display: flex; flex-direction: column;">
                
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                    {icon}
                    <h3 style="color: {self.brand_colors['primary']}; margin: 0; font-size: 18px; font-weight: 600;">
                        {feature.get('title', 'Feature')}
                    </h3>
                </div>
                
                <p style="color: {self.brand_colors['text_secondary']}; font-size: 14px; line-height: 1.6; margin: 0; flex-grow: 1;">
                    {feature.get('description', 'Feature description goes here.')}
                </p>
                
                <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="color: {self.brand_colors['primary']}; font-size: 12px; font-weight: 600;">
                        {feature.get('status', 'Available')}
                    </div>
                </div>
            </div>
            """
            feature_cards.append(card)
        
        return f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                    gap: 16px; margin: 24px 0;">
            {''.join(feature_cards)}
        </div>
        """
    
    def get_professional_header(self, title: str, subtitle: str = None, 
                              gradient_type: str = "primary") -> str:
        """Get professional page header"""
        
        gradients = {
            'primary': f"linear-gradient(135deg, {self.brand_colors['primary']} 0%, {self.brand_colors['primary_dark']} 100%)",
            'analytics': f"linear-gradient(135deg, {self.brand_colors['purple']} 0%, {self.brand_colors['accent']} 100%)",
            'trading': f"linear-gradient(135deg, {self.brand_colors['success']} 0%, {self.brand_colors['primary']} 100%)",
            'model': f"linear-gradient(135deg, {self.brand_colors['accent']} 0%, {self.brand_colors['purple']} 100%)",
            'data': f"linear-gradient(135deg, {self.brand_colors['info']} 0%, {self.brand_colors['primary']} 100%)"
        }
        
        gradient = gradients.get(gradient_type, gradients['primary'])
        logo_svg = self.get_logo_svg(48, "minimal")
        
        subtitle_html = ""
        if subtitle:
            subtitle_html = f"""
            <p style='color: rgba(255, 255, 255, 0.8); margin: 8px 0 0 0; font-size: 1.2rem; font-weight: 400;'>
                {subtitle}
            </p>
            """
        
        return f"""
        <div style='text-align: center; padding: 3rem 2rem; margin-bottom: 2rem;
                    background: {gradient};
                    border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                    position: relative; overflow: hidden;'>
            
            <!-- Animated background pattern -->
            <div style='position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                        background: url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.1"%3E%3Ccircle cx="7" cy="7" r="2"/%3E%3Ccircle cx="27" cy="7" r="2"/%3E%3Ccircle cx="47" cy="7" r="2"/%3E%3Ccircle cx="7" cy="27" r="2"/%3E%3Ccircle cx="27" cy="27" r="2"/%3E%3Ccircle cx="47" cy="27" r="2"/%3E%3Ccircle cx="7" cy="47" r="2"/%3E%3Ccircle cx="27" cy="47" r="2"/%3E%3Ccircle cx="47" cy="47" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
                        opacity: 0.3;'></div>
            
            <div style='position: relative; z-index: 1;'>
                <div style='display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 16px;'>
                    {logo_svg}
                    <h1 style='color: white; margin: 0; font-size: 2.5rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>
                        {title}
                    </h1>
                </div>
                {subtitle_html}
            </div>
        </div>
        """
    
    def get_loading_animation(self, text: str = "Loading TrenchCoat Pro...") -> str:
        """Get professional loading animation"""
        
        return f"""
        <div style='text-align: center; padding: 4rem 2rem; margin: 2rem 0;
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
                    border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.3);'>
            
            <div style='margin-bottom: 2rem;'>
                {self.get_logo_svg(64, "detailed")}
            </div>
            
            <h2 style='color: {self.brand_colors['primary']}; margin: 0 0 1rem 0; font-size: 1.8rem; font-weight: 600;'>
                {text}
            </h2>
            
            <div style='display: flex; justify-content: center; gap: 8px; margin: 2rem 0;'>
                <div style='width: 12px; height: 12px; border-radius: 50%; 
                           background: {self.brand_colors['primary']}; 
                           animation: pulse 1.5s infinite;'></div>
                <div style='width: 12px; height: 12px; border-radius: 50%; 
                           background: {self.brand_colors['primary']}; 
                           animation: pulse 1.5s infinite 0.2s;'></div>
                <div style='width: 12px; height: 12px; border-radius: 50%; 
                           background: {self.brand_colors['primary']}; 
                           animation: pulse 1.5s infinite 0.4s;'></div>
            </div>
            
            <p style='color: {self.brand_colors['text_secondary']}; font-size: 14px; margin: 0;'>
                Ultra-Premium Trading Intelligence Loading...
            </p>
            
            <style>
                @keyframes pulse {{
                    0%, 80%, 100% {{ opacity: 0.3; transform: scale(1); }}
                    40% {{ opacity: 1; transform: scale(1.2); }}
                }}
            </style>
        </div>
        """
    
    def get_navigation_tabs(self, tabs: List[Dict[str, str]], active_tab: str = None) -> str:
        """Get professional navigation tabs"""
        
        tab_items = []
        
        for tab in tabs:
            is_active = tab.get('key') == active_tab
            icon = self.get_feature_icon(tab.get('key', 'default'), 20)
            
            active_styles = f"""
                background: {self.brand_colors['primary']};
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
            """ if is_active else f"""
                background: rgba(255, 255, 255, 0.05);
                color: {self.brand_colors['text_secondary']};
            """
            
            tab_item = f"""
            <div style="display: flex; align-items: center; gap: 8px; 
                        padding: 12px 20px; border-radius: 12px; 
                        cursor: pointer; transition: all 0.3s ease;
                        {active_styles}">
                {icon}
                <span style="font-weight: 600; font-size: 14px;">{tab.get('title', 'Tab')}</span>
            </div>
            """
            tab_items.append(tab_item)
        
        return f"""
        <div style="display: flex; gap: 8px; padding: 16px; 
                    background: rgba(255, 255, 255, 0.02); 
                    border-radius: 16px; margin-bottom: 24px;
                    border: 1px solid rgba(255, 255, 255, 0.1);">
            {''.join(tab_items)}
        </div>
        """
    
    def apply_custom_css(self):
        """Apply custom CSS for professional branding"""
        
        st.markdown(f"""
        <style>
            /* Import premium fonts */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
            
            /* Global styles */
            * {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            
            /* Hide Streamlit branding */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            .stDeployButton {{visibility: hidden;}}
            
            /* Premium background */
            .stApp {{
                background: linear-gradient(135deg, {self.brand_colors['background']} 0%, {self.brand_colors['surface']} 100%);
                background-attachment: fixed;
            }}
            
            /* Premium cards */
            .premium-card {{
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 24px;
                margin: 12px 0;
                transition: all 0.3s ease;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }}
            
            .premium-card:hover {{
                transform: translateY(-4px);
                border-color: {self.brand_colors['border']};
                box-shadow: 0 20px 60px rgba(16, 185, 129, 0.2);
            }}
            
            /* Glowing metrics */
            .metric-glow {{
                text-shadow: 0 0 20px {self.brand_colors['primary']};
                animation: metricPulse 3s ease-in-out infinite alternate;
            }}
            
            @keyframes metricPulse {{
                0% {{ opacity: 0.8; }}
                100% {{ opacity: 1; }}
            }}
            
            /* Premium buttons */
            .stButton > button {{
                background: linear-gradient(135deg, {self.brand_colors['primary']} 0%, {self.brand_colors['primary_dark']} 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(16, 185, 129, 0.6);
                background: linear-gradient(135deg, {self.brand_colors['primary_light']} 0%, {self.brand_colors['primary']} 100%);
            }}
            
            /* Premium inputs */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stTextArea > div > div > textarea {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: {self.brand_colors['text_primary']};
                padding: 12px 16px;
                transition: all 0.3s ease;
            }}
            
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus,
            .stTextArea > div > div > textarea:focus {{
                border-color: {self.brand_colors['primary']};
                box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
            }}
            
            /* Premium tabs */
            .stTabs [data-baseweb="tab-list"] {{
                background: rgba(255, 255, 255, 0.02);
                border-radius: 16px;
                padding: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .stTabs [data-baseweb="tab"] {{
                background: transparent;
                border-radius: 12px;
                color: {self.brand_colors['text_secondary']};
                font-weight: 600;
                padding: 12px 20px;
                transition: all 0.3s ease;
            }}
            
            .stTabs [aria-selected="true"] {{
                background: {self.brand_colors['primary']};
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            }}
            
            /* Premium metrics */
            .stMetric {{
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 20px;
                transition: all 0.3s ease;
            }}
            
            .stMetric:hover {{
                transform: translateY(-2px);
                border-color: {self.brand_colors['border']};
                box-shadow: 0 8px 25px rgba(16, 185, 129, 0.2);
            }}
            
            .stMetric > div > div > div:first-child {{
                color: {self.brand_colors['text_secondary']};
                font-weight: 600;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stMetric > div > div > div:nth-child(2) {{
                color: {self.brand_colors['primary']};
                font-weight: 700;
                font-size: 28px;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }}
            
            /* Success flash animation */
            .success-flash {{
                animation: successFlash 2s ease-in-out;
            }}
            
            @keyframes successFlash {{
                0% {{ background-color: rgba(34, 197, 94, 0.3); }}
                50% {{ background-color: rgba(34, 197, 94, 0.1); }}
                100% {{ background-color: transparent; }}
            }}
            
            /* Live indicator */
            .live-indicator {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(34, 197, 94, 0.2);
                color: #22c55e;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .live-indicator::before {{
                content: '';
                width: 8px;
                height: 8px;
                background: #22c55e;
                border-radius: 50%;
                animation: livePulse 2s infinite;
            }}
            
            @keyframes livePulse {{
                0% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.5; transform: scale(1.2); }}
                100% {{ opacity: 1; transform: scale(1); }}
            }}
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {{
                width: 8px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {self.brand_colors['primary']};
                border-radius: 4px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {self.brand_colors['primary_light']};
            }}
            
            /* Professional shadows */
            .shadow-sm {{ box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24); }}
            .shadow-md {{ box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.06); }}
            .shadow-lg {{ box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1), 0 4px 10px rgba(0, 0, 0, 0.06); }}
            .shadow-xl {{ box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 0 8px 16px rgba(0, 0, 0, 0.06); }}
            
            /* Gradient text */
            .gradient-text {{
                background: linear-gradient(135deg, {self.brand_colors['primary']} 0%, {self.brand_colors['accent']} 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700;
            }}
            
            /* Professional spacing */
            .space-y-4 > * + * {{ margin-top: 1rem; }}
            .space-y-6 > * + * {{ margin-top: 1.5rem; }}
            .space-y-8 > * + * {{ margin-top: 2rem; }}
        </style>
        """, unsafe_allow_html=True)

# Create global branding instance
branding = BrandingSystem()

if __name__ == "__main__":
    # Demo of branding system
    st.set_page_config(page_title="TrenchCoat Pro Branding", layout="wide")
    
    branding.apply_custom_css()
    
    st.markdown(branding.get_professional_header(
        "TrenchCoat Pro Branding System",
        "Professional Visual Elements & Brand Identity"
    ), unsafe_allow_html=True)
    
    # Feature showcase demo
    features = [
        {
            'key': 'dashboard',
            'title': 'Ultra-Premium Dashboard',
            'description': 'Professional trading interface with glassmorphism design and real-time updates.',
            'status': 'Live'
        },
        {
            'key': 'analytics',
            'title': 'Advanced Analytics', 
            'description': 'ML-powered market analysis with predictive modeling and risk assessment.',
            'status': 'Beta'
        },
        {
            'key': 'trading',
            'title': 'Automated Trading',
            'description': 'Smart trading execution with safety limits and performance tracking.',
            'status': 'Coming Soon'
        }
    ]
    
    st.markdown(branding.get_feature_showcase(features), unsafe_allow_html=True)