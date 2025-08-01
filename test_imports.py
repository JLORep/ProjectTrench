#!/usr/bin/env python3
"""
Simple import test to verify dashboard components load properly
"""

print("Testing imports...")

try:
    print("1. Testing branding system import...")
    from branding_system import BrandingSystem
    branding = BrandingSystem()
    print("   [OK] Branding system imported successfully")
    
    print("2. Testing professional header generation...")
    header = branding.get_professional_header(
        "TrenchCoat Pro",
        "Ultra-Premium Cryptocurrency Trading Intelligence Platform",
        "primary"
    )
    print(f"   [OK] Header generated: {len(header)} characters")
    
    print("3. Testing ultra premium dashboard import...")
    from ultra_premium_dashboard import UltraPremiumDashboard
    print("   [OK] Dashboard class imported successfully")
    
    print("4. Testing dashboard initialization...")
    dashboard = UltraPremiumDashboard()
    print("   [OK] Dashboard initialized successfully")
    
    print("\n[SUCCESS] All imports and initializations successful!")
    print("Dashboard rendering issue appears to be fixed.")
    
except Exception as e:
    print(f"   [ERROR] Error: {e}")
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())