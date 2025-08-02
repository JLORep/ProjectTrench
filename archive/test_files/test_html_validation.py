"""Test HTML validation issues"""

import re

# Test the card HTML that's reported as having issues
card_html = """
<div style="
    background: linear-gradient(135deg, #0a0f1c 0%, #1a2332 50%, #0a0f1c 100%);
    border: 2px solid rgba(16, 185, 129, 0.5);
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.1), transparent);
        animation: shimmer 3s infinite;
    "></div>
    
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px; position: relative; z-index: 2;">
        <div style="flex-shrink: 0;">
            LOGO_HERE
        </div>
        <div style="flex: 1;">
            <h2 style="color: #10b981; font-size: 20px; font-weight: 700; margin: 0; text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);">TICKER</h2>
            <div style="color: rgba(255,255,255,0.6); font-size: 11px; font-family: monospace; background: rgba(16, 185, 129, 0.1); padding: 2px 6px; border-radius: 4px; display: inline-block; margin-top: 4px;">CA_DISPLAY</div>
        </div>
        <div style="text-align: right;">
            <div style="color: #ffffff; font-size: 18px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">$0.00001234</div>
            PRICE_CHANGE
        </div>
    </div>
    
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div style="color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 600;">Market Cap: $1.2M</div>
        <div style="color: rgba(255,255,255,0.7); font-size: 12px;">METADATA</div>
    </div>
</div>
"""

# Count opening and closing tags
opening_divs = card_html.count('<div')
closing_divs = card_html.count('</div>')
opening_h2 = card_html.count('<h2')
closing_h2 = card_html.count('</h2>')

print(f"Opening <div> tags: {opening_divs}")
print(f"Closing </div> tags: {closing_divs}")
print(f"Opening <h2> tags: {opening_h2}")
print(f"Closing </h2> tags: {closing_h2}")

if opening_divs == closing_divs:
    print("✅ All div tags are properly closed")
else:
    print(f"❌ Unclosed div tags: {opening_divs - closing_divs}")

if opening_h2 == closing_h2:
    print("✅ All h2 tags are properly closed")
else:
    print(f"❌ Unclosed h2 tags: {opening_h2 - closing_h2}")

# Check other potential issues
detailed_header = """
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            border: 2px solid rgba(16, 185, 129, 0.4); border-radius: 20px; padding: 32px;
            margin: 20px 0; box-shadow: 0 20px 60px rgba(16, 185, 129, 0.2);">
    <h1 style="text-align: center; color: #10b981; font-size: 36px; margin-bottom: 8px;">🔍 DETAILED COIN ANALYSIS</h1>
    <p style="text-align: center; color: rgba(255,255,255,0.6); margin-bottom: 24px;">Complete trading intelligence with live charts and metrics</p>
</div>
"""

print("\nChecking detailed header:")
print(f"Opening <div>: {detailed_header.count('<div')}")
print(f"Closing </div>: {detailed_header.count('</div>')}")
print(f"Opening <h1>: {detailed_header.count('<h1')}")
print(f"Closing </h1>: {detailed_header.count('</h1>')}")
print(f"Opening <p>: {detailed_header.count('<p')}")
print(f"Closing </p>: {detailed_header.count('</p>')}")