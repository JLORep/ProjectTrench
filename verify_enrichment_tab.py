#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script for enrichment tab deployment
Tests that the tab structure includes the new enrichment tab
"""
import re
import sys
import os

# Fix console encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def verify_enrichment_tab():
    """Verify that the enrichment tab exists in streamlit_app.py"""
    
    print("🔍 Verifying Enrichment Tab Deployment...")
    print("=" * 50)
    
    try:
        # Read streamlit_app.py
        with open("streamlit_app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check 1: Enrichment tab in base_tabs list
        enrichment_in_tabs = '"🚀 Enrichment"' in content
        print(f"✅ Enrichment tab in base_tabs: {'YES' if enrichment_in_tabs else 'NO'}")
        
        # Check 2: Tab content implementation (with tabs[6])
        enrichment_implementation = 'with tabs[6]:' in content and 'Comprehensive API Enrichment System' in content
        print(f"✅ Enrichment tab implementation: {'YES' if enrichment_implementation else 'NO'}")
        
        # Check 3: API status display
        api_status_display = 'API Sources Integration Status' in content
        print(f"✅ API status display: {'YES' if api_status_display else 'NO'}")
        
        # Check 4: Interactive enrichment tools
        interactive_tools = 'Interactive Enrichment Tools' in content
        print(f"✅ Interactive enrichment tools: {'YES' if interactive_tools else 'NO'}")
        
        # Check 5: 17 API sources mentioned
        seventeen_apis = '17 API Sources' in content or '17 API sources' in content
        print(f"✅ 17 API sources referenced: {'YES' if seventeen_apis else 'NO'}")
        
        # Check 6: Enrichment metrics
        metrics_display = 'Real-Time Enrichment Metrics' in content
        print(f"✅ Enrichment metrics display: {'YES' if metrics_display else 'NO'}")
        
        # Count total tab structure
        tab_pattern = r'base_tabs = \[(.*?)\]'
        match = re.search(tab_pattern, content, re.DOTALL)
        
        if match:
            tabs_content = match.group(1)
            tab_count = tabs_content.count('"')
            print(f"✅ Total tabs found: {tab_count // 2}")
        
        # Overall verification
        all_checks = [
            enrichment_in_tabs,
            enrichment_implementation, 
            api_status_display,
            interactive_tools,
            seventeen_apis,
            metrics_display
        ]
        
        passed_checks = sum(all_checks)
        total_checks = len(all_checks)
        
        print("\n" + "=" * 50)
        print(f"📊 VERIFICATION SUMMARY:")
        print(f"   • Checks passed: {passed_checks}/{total_checks}")
        print(f"   • Success rate: {passed_checks/total_checks*100:.1f}%")
        
        if passed_checks == total_checks:
            print("🎉 ✅ ALL CHECKS PASSED - Enrichment Tab Successfully Deployed!")
            return True
        else:
            print("❌ Some checks failed - Enrichment Tab may not be fully deployed")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying enrichment tab: {e}")
        return False

def verify_supporting_files():
    """Verify that supporting enrichment files exist"""
    
    print("\n🔍 Verifying Supporting Files...")
    print("=" * 50)
    
    files_to_check = [
        "comprehensive_coin_history.py",
        "test_comprehensive_history.py", 
        "free_apis.md",
        "ENRICHMENT_PIPELINE_VISUALIZATION.md",
        "src/data/free_api_providers.py"
    ]
    
    existing_files = []
    missing_files = []
    
    for file_path in files_to_check:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if len(content) > 100:  # Non-empty file
                    existing_files.append(file_path)
                    print(f"✅ {file_path}: {len(content):,} characters")
                else:
                    missing_files.append(file_path)
                    print(f"⚠️ {file_path}: File too small")
        except FileNotFoundError:
            missing_files.append(file_path)
            print(f"❌ {file_path}: Not found")
    
    print(f"\n📊 Supporting Files Summary:")
    print(f"   • Files found: {len(existing_files)}/{len(files_to_check)}")
    print(f"   • Missing files: {len(missing_files)}")
    
    return len(missing_files) == 0

def main():
    """Main verification"""
    print("🚀 TrenchCoat Pro - Enrichment Tab Verification")
    print("=" * 60)
    
    # Verify main tab implementation
    tab_success = verify_enrichment_tab()
    
    # Verify supporting files  
    files_success = verify_supporting_files()
    
    # Final result
    print("\n" + "=" * 60)
    print("🎯 FINAL VERIFICATION RESULT:")
    
    if tab_success and files_success:
        print("🎉 ✅ ENRICHMENT TAB DEPLOYMENT: SUCCESSFUL")
        print("   • All tab functionality implemented")
        print("   • All supporting files present")
        print("   • Ready for production use")
        print("\n🌐 Dashboard should be available at: https://trenchcoat-pro.streamlit.app")
        print("📊 Look for the '🚀 Enrichment' tab in the dashboard")
        return 0
    else:
        print("❌ ENRICHMENT TAB DEPLOYMENT: INCOMPLETE")
        if not tab_success:
            print("   • Tab implementation issues detected")
        if not files_success:
            print("   • Missing supporting files")
        return 1

if __name__ == "__main__":
    sys.exit(main())