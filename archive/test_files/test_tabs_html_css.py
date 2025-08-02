#!/usr/bin/env python3
"""
Comprehensive testing script for TrenchCoat Pro tabs, HTML, and CSS
Tests all 12 tabs, validates HTML/CSS implementations, and ensures proper rendering
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
import subprocess

class TabHTMLCSSValidator:
    def __init__(self):
        self.results = {
            "tabs": {},
            "html_css": {},
            "errors": [],
            "warnings": [],
            "summary": {}
        }
        
    def test_tab_structure(self) -> bool:
        """Test the 12-tab structure in streamlit_app.py"""
        print("🔍 Testing tab structure...")
        
        try:
            with open("streamlit_app.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Expected 12 tabs (based on actual implementation)
            expected_tabs = [
                ("tab1", "🚀 Dashboard", "Market intelligence overview"),
                ("tab2", "💎 Coins", "Coin database and analysis"),
                ("tab3", "🎯 Hunt Hub", "Memecoin sniping dashboard"),
                ("tab4", "📡 Alpha Radar", "AI-powered signal feed"),
                ("tab5", "🛡️ Security", "Security and threat monitoring"),
                ("tab6", "🔧 Enrichment", "Data enrichment system"),
                ("tab7", "🤖 Super Claude", "AI assistant"),
                ("tab8", "📱 Blog", "Development blog"),
                ("tab9", "📊 Monitoring", "System monitoring"),
                ("tab10", "⚙️ System", "System configuration"),
                ("tab11", "📡 Live Signals", "Live signal monitoring"),
                ("tab12", "🧮 Runners", "Trading bot runners")
            ]
            
            # Find tab definition
            tab_pattern = r'tab1.*?=\s*st\.tabs\(\[(.*?)\]\)'
            tab_match = re.search(tab_pattern, content, re.DOTALL)
            
            if not tab_match:
                self.results["errors"].append("Could not find tab definition in streamlit_app.py")
                return False
            
            tab_def = tab_match.group(1)
            defined_tabs = re.findall(r'"([^"]+)"', tab_def)
            
            # Validate tab count
            if len(defined_tabs) != 12:
                self.results["errors"].append(f"Expected 12 tabs, found {len(defined_tabs)}")
                return False
            
            # Validate each tab
            all_valid = True
            for i, (var_name, expected_icon_name, description) in enumerate(expected_tabs):
                if i < len(defined_tabs):
                    actual = defined_tabs[i]
                    expected = expected_icon_name
                    
                    # Check if tab matches expected pattern
                    if not actual.startswith(expected.split()[0]):  # Check icon match
                        self.results["warnings"].append(
                            f"Tab {i+1} mismatch: expected '{expected}', got '{actual}'"
                        )
                    
                    self.results["tabs"][var_name] = {
                        "index": i + 1,
                        "name": actual,
                        "description": description,
                        "valid": True
                    }
                else:
                    self.results["tabs"][var_name] = {
                        "index": i + 1,
                        "name": "MISSING",
                        "description": description,
                        "valid": False
                    }
                    all_valid = False
            
            # Check tab content implementation
            for var_name in ["tab1", "tab2", "tab3", "tab4", "tab5", "tab6", 
                            "tab7", "tab8", "tab9", "tab10", "tab11", "tab12"]:
                pattern = f"with {var_name}:"
                if pattern in content:
                    self.results["tabs"][var_name]["implemented"] = True
                else:
                    self.results["tabs"][var_name]["implemented"] = False
                    self.results["errors"].append(f"Tab {var_name} not implemented")
                    all_valid = False
            
            return all_valid
            
        except Exception as e:
            self.results["errors"].append(f"Error testing tab structure: {str(e)}")
            return False
    
    def test_html_css_implementations(self) -> bool:
        """Test all HTML/CSS implementations"""
        print("🎨 Testing HTML/CSS implementations...")
        
        try:
            with open("streamlit_app.py", "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
            
            # Track HTML/CSS usage
            html_usages = []
            css_blocks = []
            
            # Find all st.markdown with unsafe_allow_html=True
            for i, line in enumerate(lines):
                if "unsafe_allow_html=True" in line:
                    # Look for the HTML content
                    html_start = max(0, i - 20)
                    html_end = min(len(lines), i + 5)
                    context = "\n".join(lines[html_start:html_end])
                    
                    html_usages.append({
                        "line": i + 1,
                        "context": context[:200] + "..." if len(context) > 200 else context
                    })
            
            # Find CSS blocks
            css_pattern = r'<style>(.*?)</style>'
            css_matches = re.findall(css_pattern, content, re.DOTALL)
            
            for match in css_matches:
                css_blocks.append({
                    "content": match.strip()[:200] + "..." if len(match) > 200 else match.strip()
                })
            
            # Validate CSS syntax
            css_valid = True
            for i, block in enumerate(css_blocks):
                css_content = block["content"]
                
                # Basic CSS validation
                if css_content.count('{') != css_content.count('}'):
                    self.results["errors"].append(f"CSS block {i+1} has mismatched braces")
                    css_valid = False
                
                if css_content.count('(') != css_content.count(')'):
                    self.results["warnings"].append(f"CSS block {i+1} has mismatched parentheses")
            
            # Store results
            self.results["html_css"] = {
                "html_usages": len(html_usages),
                "css_blocks": len(css_blocks),
                "html_locations": html_usages[:5],  # First 5 for summary
                "css_valid": css_valid
            }
            
            # Check for specific required CSS classes (only those actually used)
            required_classes = [
                "coin-card",
                "enrichment-container",
                "coin-logo",
                "coin-ticker",
                "coin-price"
            ]
            
            found_classes = []
            for css_class in required_classes:
                if f".{css_class}" in content or f'class="{css_class}"' in content:
                    found_classes.append(css_class)
                else:
                    self.results["warnings"].append(f"Required CSS class '{css_class}' not found")
            
            self.results["html_css"]["found_classes"] = found_classes
            self.results["html_css"]["missing_classes"] = [c for c in required_classes if c not in found_classes]
            
            return css_valid and len(html_usages) > 0
            
        except Exception as e:
            self.results["errors"].append(f"Error testing HTML/CSS: {str(e)}")
            return False
    
    def test_tab_specific_features(self) -> bool:
        """Test specific features for each tab"""
        print("🧪 Testing tab-specific features...")
        
        try:
            with open("streamlit_app.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Tab-specific tests
            tab_tests = {
                "tab3": {  # Hunt Hub
                    "required": ["Hunt Hub", "memecoin", "Active Scans"],
                    "description": "Hunt Hub memecoin sniping"
                },
                "tab4": {  # Alpha Radar
                    "required": ["Alpha Radar", "signal", "AI"],
                    "description": "Alpha Radar signal system"
                },
                "tab5": {  # Security
                    "required": ["Security", "System Status", "SECURE"],
                    "description": "Security monitoring"
                },
                "tab6": {  # Enrichment
                    "required": ["Enrichment", "API", "console-output"],
                    "description": "Enrichment system"
                }
            }
            
            all_valid = True
            for tab_name, test_config in tab_tests.items():
                # Find tab content
                tab_pattern = f"with {tab_name}:(.*?)(?=with tab\\d+:|$)"
                tab_match = re.search(tab_pattern, content, re.DOTALL)
                
                if tab_match:
                    tab_content = tab_match.group(1)
                    found_features = []
                    missing_features = []
                    
                    for feature in test_config["required"]:
                        if feature.lower() in tab_content.lower():
                            found_features.append(feature)
                        else:
                            missing_features.append(feature)
                    
                    if missing_features:
                        self.results["warnings"].append(
                            f"{tab_name} missing features: {', '.join(missing_features)}"
                        )
                    
                    self.results["tabs"][tab_name]["features"] = {
                        "found": found_features,
                        "missing": missing_features,
                        "description": test_config["description"]
                    }
                else:
                    self.results["errors"].append(f"Could not find content for {tab_name}")
                    all_valid = False
            
            return all_valid
            
        except Exception as e:
            self.results["errors"].append(f"Error testing tab features: {str(e)}")
            return False
    
    def run_html_css_validator(self) -> bool:
        """Run the separate HTML/CSS validator"""
        print("🔧 Running HTML/CSS validator...")
        
        try:
            result = subprocess.run(
                [sys.executable, "validate_html_css.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self.results["html_css"]["validator_output"] = result.stdout
            self.results["html_css"]["validator_success"] = result.returncode == 0
            
            if result.returncode != 0:
                self.results["errors"].append("HTML/CSS validator failed")
                if result.stderr:
                    self.results["errors"].append(f"Validator error: {result.stderr}")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.results["errors"].append("HTML/CSS validator timed out")
            return False
        except Exception as e:
            self.results["errors"].append(f"Error running HTML/CSS validator: {str(e)}")
            return False
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report = ["# TrenchCoat Pro Tab & HTML/CSS Test Report\n"]
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Summary
        total_errors = len(self.results["errors"])
        total_warnings = len(self.results["warnings"])
        
        if total_errors == 0:
            report.append("## ✅ All Tests Passed!\n")
        else:
            report.append(f"## ❌ Tests Failed ({total_errors} errors, {total_warnings} warnings)\n")
        
        # Tab Structure
        report.append("\n## 📑 Tab Structure (12 tabs)\n")
        report.append("| Tab | Name | Implemented | Status |\n")
        report.append("|-----|------|-------------|--------|\n")
        
        for tab_var, tab_info in self.results["tabs"].items():
            impl = "✅" if tab_info.get("implemented", False) else "❌"
            status = "✅" if tab_info.get("valid", False) else "❌"
            report.append(f"| {tab_var} | {tab_info['name']} | {impl} | {status} |\n")
        
        # HTML/CSS Summary
        report.append("\n## 🎨 HTML/CSS Implementation\n")
        report.append(f"- HTML usages with unsafe_allow_html: {self.results['html_css'].get('html_usages', 0)}\n")
        report.append(f"- CSS blocks found: {self.results['html_css'].get('css_blocks', 0)}\n")
        report.append(f"- CSS validation: {'✅ Valid' if self.results['html_css'].get('css_valid', False) else '❌ Invalid'}\n")
        
        # Required CSS Classes
        if "found_classes" in self.results["html_css"]:
            report.append("\n### Required CSS Classes:\n")
            for css_class in self.results["html_css"]["found_classes"]:
                report.append(f"- ✅ {css_class}\n")
            for css_class in self.results["html_css"].get("missing_classes", []):
                report.append(f"- ❌ {css_class} (missing)\n")
        
        # Errors and Warnings
        if self.results["errors"]:
            report.append("\n## ❌ Errors\n")
            for error in self.results["errors"]:
                report.append(f"- {error}\n")
        
        if self.results["warnings"]:
            report.append("\n## ⚠️ Warnings\n")
            for warning in self.results["warnings"]:
                report.append(f"- {warning}\n")
        
        # Recommendations
        report.append("\n## 📋 Pre-Deployment Checklist\n")
        report.append("- [ ] All 12 tabs are implemented and accessible\n")
        report.append("- [ ] HTML/CSS validator passes without errors\n")
        report.append("- [ ] Required CSS classes are present\n")
        report.append("- [ ] No missing tab features\n")
        report.append("- [ ] Console has no JavaScript errors\n")
        report.append("- [ ] Mobile responsive design works\n")
        
        return "".join(report)
    
    def save_results(self):
        """Save test results to file"""
        # Save JSON results
        with open("tab_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)
        
        # Save markdown report
        report = self.generate_report()
        with open("tab_test_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n📄 Results saved to tab_test_results.json and tab_test_report.md")

def main():
    print("🚀 TrenchCoat Pro Tab & HTML/CSS Testing Suite")
    print("=" * 50)
    
    validator = TabHTMLCSSValidator()
    
    # Run all tests
    tests = [
        ("Tab Structure", validator.test_tab_structure),
        ("HTML/CSS Implementation", validator.test_html_css_implementations),
        ("Tab Features", validator.test_tab_specific_features),
        ("HTML/CSS Validator", validator.run_html_css_validator)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        passed = test_func()
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"Result: {status}")
        all_passed = all_passed and passed
    
    # Generate and save report
    validator.save_results()
    
    # Print summary
    print("\n" + "=" * 50)
    print(validator.generate_report())
    
    # Exit code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()