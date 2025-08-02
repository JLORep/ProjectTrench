#!/usr/bin/env python3
"""
HTML Guard System - Prevents HTML rendering errors in Streamlit
Protects against f-string syntax issues that cause raw HTML display
"""

import re
from typing import Dict, Any, Optional
import html

class HTMLGuardSystem:
    """
    Guards against common HTML rendering issues in Streamlit applications
    """
    
    @staticmethod
    def safe_format_html(template: str, **kwargs) -> str:
        """
        Safely format HTML templates with dynamic values
        Prevents f-string parsing errors and escapes problematic content
        
        Args:
            template: HTML template with {placeholder} markers
            **kwargs: Values to insert into template
            
        Returns:
            Safely formatted HTML string
        """
        # Pre-process all values to ensure they're safe
        safe_values = {}
        for key, value in kwargs.items():
            if value is None:
                safe_values[key] = ""
            elif isinstance(value, (int, float)):
                # Handle numeric formatting
                if key.endswith('_currency'):
                    safe_values[key] = f"${value:,.0f}"
                elif key.endswith('_percent'):
                    safe_values[key] = f"{value:+.2f}%"
                else:
                    safe_values[key] = str(value)
            else:
                # Escape HTML entities in string values
                safe_values[key] = html.escape(str(value))
        
        # Use string.format() instead of f-strings for safety
        try:
            return template.format(**safe_values)
        except KeyError as e:
            print(f"Warning: Missing template variable: {e}")
            return template
        except ValueError as e:
            print(f"Warning: Template formatting error: {e}")
            return template
    
    @staticmethod
    def create_coin_card_html(coin_data: Dict[str, Any]) -> str:
        """
        Create a coin card HTML with proper escaping and formatting
        
        Args:
            coin_data: Dictionary containing coin information
            
        Returns:
            Safe HTML string for the coin card
        """
        # Extract and prepare all values safely
        ticker = html.escape(str(coin_data.get('ticker', 'Unknown')))
        ca = str(coin_data.get('ca', ''))
        ca_display = f"{ca[:8]}...{ca[-8:]}" if len(ca) > 16 else ca
        ca_display = html.escape(ca_display)
        
        # Numeric values with safe defaults
        price = float(coin_data.get('current_price_usd', 0) or 0)
        mcap = float(coin_data.get('market_cap_usd', 0) or coin_data.get('discovery_mc', 0) or 0)
        volume_24h = float(coin_data.get('current_volume_24h', 0) or 0)
        smart_wallets = int(coin_data.get('smart_wallets', 0) or 0)
        price_change = coin_data.get('price_change_24h')
        
        # Create logo HTML safely
        logo_html = HTMLGuardSystem._create_logo_html(ticker, coin_data.get('image_url'))
        
        # Create price change HTML
        price_change_html = ""
        if price_change is not None:
            change_color = "#10b981" if price_change >= 0 else "#ef4444"
            change_symbol = "+" if price_change >= 0 else ""
            price_change_html = f'<div style="color: {change_color}; font-size: 14px; font-weight: 500;">{change_symbol}{price_change:.2f}%</div>'
        
        # Use template with placeholders
        template = """<div class="coin-card" style="background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px; padding: 16px; margin: 8px 0; transition: all 0.2s ease; cursor: pointer;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="flex-shrink: 0;">{logo_html}</div>
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <h3 style="color: #fff; font-size: 18px; font-weight: 600; margin: 0;">{ticker}</h3>
                        <div style="text-align: right;">
                            <div style="color: #fff; font-size: 16px; font-weight: 500;">${price:.8f}</div>
                            {price_change_html}
                        </div>
                    </div>
                    <div style="color: #718096; font-size: 11px; font-family: monospace; margin-top: 4px;">{ca_display}</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding-top: 12px; border-top: 1px solid #2d3748;">
                <div>
                    <div style="color: #718096; font-size: 11px; text-transform: uppercase;">Market Cap</div>
                    <div style="color: #fff; font-size: 14px; font-weight: 500;">${mcap:,.0f}</div>
                </div>
                <div>
                    <div style="color: #718096; font-size: 11px; text-transform: uppercase;">24h Volume</div>
                    <div style="color: #fff; font-size: 14px; font-weight: 500;">${volume_24h:,.0f}</div>
                </div>
                <div>
                    <div style="color: #718096; font-size: 11px; text-transform: uppercase;">Smart Wallets</div>
                    <div style="color: #fff; font-size: 14px; font-weight: 500;">{smart_wallets}</div>
                </div>
            </div>
        </div>"""
        
        # Format safely using string.format()
        return template.format(
            logo_html=logo_html,
            ticker=ticker,
            price=price,
            price_change_html=price_change_html,
            ca_display=ca_display,
            mcap=mcap,
            volume_24h=volume_24h,
            smart_wallets=smart_wallets
        )
    
    @staticmethod
    def _create_logo_html(ticker: str, image_url: Optional[str] = None) -> str:
        """Create safe logo HTML without complex nested quotes"""
        ticker_safe = html.escape(ticker)
        logo_text = ticker_safe[:2].upper() if len(ticker_safe) >= 2 else ticker_safe.upper()
        
        if image_url:
            # Simple img tag without onerror handler
            return f'<img src="{html.escape(image_url)}" alt="{ticker_safe}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover; border: 1px solid rgba(255, 255, 255, 0.1);">'
        else:
            # Fallback to text logo
            return f'<div class="coin-logo" style="width: 48px; height: 48px; font-size: 18px; background: #2d3748; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #10b981; font-weight: 600;">{logo_text}</div>'
    
    @staticmethod
    def validate_html_template(template: str) -> Dict[str, Any]:
        """
        Validate an HTML template for common issues
        
        Args:
            template: HTML template string to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        
        # Check for problematic f-string patterns
        if re.search(r'\$\{[^}]*\sor\s[^}]*\}', template):
            issues.append("Found 'or' operator inside f-string format specification")
        
        # Check for complex nested quotes
        if template.count("'") > 10 or template.count('"') > 10:
            # Check for onerror handlers with nested quotes
            if 'onerror=' in template and ('outerHTML' in template or 'innerHTML' in template):
                issues.append("Complex onerror handler with nested quotes detected")
        
        # Check for unescaped user input placeholders
        if re.search(r'\{[^}]+\[.+\]\}', template):
            issues.append("Direct dictionary access in template - use .get() method")
        
        # Check for balanced HTML tags
        open_divs = template.count('<div')
        close_divs = template.count('</div>')
        if open_divs != close_divs:
            issues.append(f"Unbalanced div tags: {open_divs} opening, {close_divs} closing")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": [
                "Use HTMLGuardSystem.safe_format_html() for dynamic content",
                "Pre-calculate all values before template formatting",
                "Avoid complex nested quotes in HTML attributes",
                "Use .get() method with defaults for dictionary access"
            ] if issues else []
        }
    
    @staticmethod
    def fix_common_issues(html_string: str) -> str:
        """
        Attempt to fix common HTML rendering issues
        
        Args:
            html_string: HTML string with potential issues
            
        Returns:
            Fixed HTML string
        """
        # Fix ${value or 0:,.0f} pattern
        html_string = re.sub(
            r'\$\{([^}]+)\sor\s([^}:]+)(:[^}]+)?\}',
            lambda m: f"${{{m.group(1)}.get('{m.group(1).strip()}', {m.group(2)}){m.group(3) or ''}}}",
            html_string
        )
        
        # Remove complex onerror handlers
        html_string = re.sub(
            r'onerror="[^"]*outerHTML[^"]*"',
            '',
            html_string
        )
        
        return html_string


def integrate_with_streamlit():
    """
    Example of how to integrate HTMLGuardSystem with Streamlit
    """
    import streamlit as st
    
    # Example usage in Streamlit
    def render_coin_card(coin_data):
        """Render a coin card with HTML guard protection"""
        guard = HTMLGuardSystem()
        
        # Create safe HTML
        card_html = guard.create_coin_card_html(coin_data)
        
        # Validate before rendering
        validation = guard.validate_html_template(card_html)
        if not validation['valid']:
            st.warning("HTML template issues detected:")
            for issue in validation['issues']:
                st.warning(f"- {issue}")
        
        # Render the HTML
        st.markdown(card_html, unsafe_allow_html=True)
    
    # Example coin data
    example_coin = {
        'ticker': 'PEPE',
        'ca': '0x1234567890abcdef1234567890abcdef12345678',
        'current_price_usd': 0.00001234,
        'market_cap_usd': 1000000,
        'current_volume_24h': 50000,
        'smart_wallets': 42,
        'price_change_24h': 15.67,
        'image_url': None
    }
    
    render_coin_card(example_coin)


if __name__ == "__main__":
    # Test the guard system
    guard = HTMLGuardSystem()
    
    # Test coin card creation
    test_coin = {
        'ticker': 'TEST',
        'ca': '0x' + 'a' * 40,
        'current_price_usd': 0.123456,
        'market_cap_usd': 1000000,
        'current_volume_24h': None,  # Test None handling
        'smart_wallets': 0,
        'price_change_24h': -5.23
    }
    
    html = guard.create_coin_card_html(test_coin)
    print("Generated HTML:")
    print(html)
    
    # Validate the HTML
    validation = guard.validate_html_template(html)
    print(f"\nValidation: {'PASSED' if validation['valid'] else 'FAILED'}")
    if validation['issues']:
        for issue in validation['issues']:
            print(f"- {issue}")