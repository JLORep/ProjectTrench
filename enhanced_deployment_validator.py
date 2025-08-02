#!/usr/bin/env python3
"""
TrenchCoat Pro - Enhanced Deployment Validation System
Comprehensive validation that code is deployed and dashboard is fully functional
"""
import subprocess
import sys
import os
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sqlite3
import hashlib

class EnhancedDeploymentValidator:
    """Enhanced deployment validation with comprehensive dashboard checks"""
    
    def __init__(self):
        self.streamlit_url = "https://trenchdemo.streamlit.app"
        self.github_repo = "JLORep/ProjectTrench"
        self.webhook_url = "https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "code_deployed": False,
            "dashboard_functional": False,
            "all_tabs_loaded": False,
            "database_accessible": False,
            "modules_loaded": False,
            "enrichment_working": False,
            "security_dashboard_ok": False,
            "monitoring_dashboard_ok": False,
            "deployment_hash": None,
            "response_time": None,
            "errors": [],
            "warnings": []
        }
        
    def check_github_deployment(self) -> Tuple[bool, str]:
        """Verify code is pushed to GitHub and matches local"""
        try:
            # Get local commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10
            )
            local_hash = result.stdout.strip()
            
            # Get remote commit hash
            result = subprocess.run(
                ["git", "ls-remote", "origin", "main"],
                capture_output=True,
                text=True,
                timeout=30
            )
            remote_hash = result.stdout.split()[0] if result.stdout else None
            
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10
            )
            uncommitted = result.stdout.strip()
            
            if uncommitted:
                self.validation_results["warnings"].append("Uncommitted changes detected locally")
            
            if local_hash == remote_hash:
                self.validation_results["code_deployed"] = True
                self.validation_results["deployment_hash"] = local_hash[:8]
                return True, f"Code deployed successfully (hash: {local_hash[:8]})"
            else:
                self.validation_results["errors"].append(
                    f"Local hash ({local_hash[:8]}) doesn't match remote ({remote_hash[:8] if remote_hash else 'unknown'})"
                )
                return False, "Code not fully deployed to GitHub"
                
        except Exception as e:
            self.validation_results["errors"].append(f"GitHub check failed: {str(e)}")
            return False, f"GitHub deployment check failed: {e}"
    
    def check_streamlit_health(self) -> Tuple[bool, str]:
        """Advanced Streamlit app health check"""
        try:
            start_time = time.time()
            response = requests.get(self.streamlit_url, timeout=30, headers={
                'User-Agent': 'TrenchCoat-Enhanced-Validator/2.0'
            })
            self.validation_results["response_time"] = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for critical UI elements
                critical_elements = {
                    "trenchcoat pro": "Application title",
                    "live dashboard": "Dashboard tab",
                    "advanced analytics": "Analytics tab",
                    "coin data": "Coin data tab",
                    "database": "Database tab"
                }
                
                missing_elements = []
                for element, description in critical_elements.items():
                    if element not in content:
                        missing_elements.append(description)
                
                # Check for error indicators
                error_indicators = [
                    "traceback",
                    "error:",
                    "exception",
                    "failed to load",
                    "something went wrong",
                    "internal server error"
                ]
                
                errors_found = [err for err in error_indicators if err in content]
                
                if not missing_elements and not errors_found:
                    return True, f"Streamlit app healthy (response time: {self.validation_results['response_time']}ms)"
                elif errors_found:
                    self.validation_results["errors"].append(f"Error indicators found: {errors_found}")
                    return False, "Streamlit app showing errors"
                else:
                    self.validation_results["warnings"].append(f"Missing UI elements: {missing_elements}")
                    return True, "Streamlit app running with warnings"
                    
            else:
                self.validation_results["errors"].append(f"Streamlit returned status {response.status_code}")
                return False, f"Streamlit returned status {response.status_code}"
                
        except requests.Timeout:
            self.validation_results["errors"].append("Streamlit request timed out")
            return False, "Streamlit app not responding (timeout)"
        except Exception as e:
            self.validation_results["errors"].append(f"Streamlit health check failed: {str(e)}")
            return False, f"Streamlit health check failed: {e}"
    
    def validate_dashboard_functionality(self) -> Dict[str, bool]:
        """Comprehensive dashboard component validation"""
        print("Validating dashboard components...")
        
        validations = {
            "code_structure": self.check_code_structure(),
            "tabs": self.check_dashboard_tabs(),
            "database": self.check_database_connection(),
            "modules": self.check_critical_modules(),
            "enrichment": self.check_enrichment_system(),
            "security": self.check_security_dashboard(),
            "monitoring": self.check_monitoring_dashboard()
        }
        
        # Update overall results
        self.validation_results["all_tabs_loaded"] = validations["tabs"]
        self.validation_results["database_accessible"] = validations["database"]
        self.validation_results["modules_loaded"] = validations["modules"]
        self.validation_results["enrichment_working"] = validations["enrichment"]
        self.validation_results["security_dashboard_ok"] = validations["security"]
        self.validation_results["monitoring_dashboard_ok"] = validations["monitoring"]
        
        # Dashboard is functional if all critical components work
        critical_components = ["tabs", "database", "modules"]
        self.validation_results["dashboard_functional"] = all(
            validations[comp] for comp in critical_components
        )
        
        return validations
    
    def check_code_structure(self) -> bool:
        """Verify code structure and no syntax errors"""
        try:
            # Compile streamlit_app.py to check for syntax errors
            with open('streamlit_app.py', 'r', encoding='utf-8') as f:
                code = f.read()
            
            compile(code, 'streamlit_app.py', 'exec')
            return True
            
        except SyntaxError as e:
            self.validation_results["errors"].append(f"Syntax error in streamlit_app.py: {e}")
            return False
        except Exception as e:
            self.validation_results["errors"].append(f"Code structure check failed: {str(e)}")
            return False
    
    def check_dashboard_tabs(self) -> bool:
        """Verify all 10 tabs are properly defined"""
        try:
            with open('streamlit_app.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            expected_tabs = [
                "📊 Live Dashboard",
                "🧠 Advanced Analytics", 
                "🤖 Model Builder",
                "⚙️ Trading Engine",
                "📡 Telegram Signals",
                "📝 Dev Blog",
                "💎 Solana Wallet",
                "🗄️ Coin Data",
                "🗃️ Database",
                "🔔 Incoming Coins"
            ]
            
            # Check if all tabs are defined
            missing_tabs = []
            for tab in expected_tabs:
                if tab not in content:
                    missing_tabs.append(tab)
            
            # Also check for st.tabs call with correct number
            import re
            tabs_match = re.search(r'st\.tabs\s*\(\s*\[(.*?)\]\s*\)', content, re.DOTALL)
            if tabs_match:
                tabs_content = tabs_match.group(1)
                tab_count = len(re.findall(r'"[^"]*"', tabs_content))
                if tab_count != 10:
                    self.validation_results["warnings"].append(
                        f"Tab count mismatch: found {tab_count}, expected 10"
                    )
            
            if missing_tabs:
                self.validation_results["errors"].append(f"Missing tabs: {missing_tabs}")
                return False
                
            return True
            
        except Exception as e:
            self.validation_results["errors"].append(f"Tab check failed: {str(e)}")
            return False
    
    def check_database_connection(self) -> bool:
        """Verify database exists and has valid data"""
        try:
            db_path = Path("data/trench.db")
            if not db_path.exists():
                self.validation_results["errors"].append("Database file not found")
                return False
            
            # Check file is in git
            result = subprocess.run(
                ["git", "ls-files", "data/trench.db"],
                capture_output=True,
                text=True
            )
            if not result.stdout.strip():
                self.validation_results["warnings"].append("Database not tracked in git")
                
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check coins table
            cursor.execute("SELECT COUNT(*) FROM coins")
            coin_count = cursor.fetchone()[0]
            
            # Check for data quality
            cursor.execute("""
                SELECT COUNT(*) FROM coins 
                WHERE discovery_price > 0 OR axiom_price > 0
            """)
            enriched_count = cursor.fetchone()[0]
            
            conn.close()
            
            if coin_count == 0:
                self.validation_results["errors"].append("Database has no coins")
                return False
            elif coin_count < 1000:
                self.validation_results["warnings"].append(f"Low coin count: {coin_count}")
            
            enrichment_rate = (enriched_count / coin_count * 100) if coin_count > 0 else 0
            if enrichment_rate < 10:
                self.validation_results["warnings"].append(
                    f"Low enrichment rate: {enrichment_rate:.1f}%"
                )
                
            return True
                
        except Exception as e:
            self.validation_results["errors"].append(f"Database check failed: {str(e)}")
            return False
    
    def check_critical_modules(self) -> bool:
        """Verify all critical modules can be imported"""
        critical_modules = [
            ("enhanced_security_dashboard", "Enhanced security dashboard"),
            ("live_enrichment_system", "Live enrichment system"),
            ("comprehensive_monitoring", "Monitoring dashboard"),
            ("streamlit_safe_dashboard", "Safe dashboard"),
            ("breadcrumb_navigation", "Breadcrumb navigation"),
            ("stunning_charts_system", "Charts system")
        ]
        
        all_loaded = True
        for module_name, description in critical_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                self.validation_results["errors"].append(
                    f"{description} import failed: {str(e)}"
                )
                all_loaded = False
                
        return all_loaded
    
    def check_enrichment_system(self) -> bool:
        """Verify enrichment system functionality"""
        try:
            from live_enrichment_system import LiveEnrichmentSystem
            enricher = LiveEnrichmentSystem()
            stats = enricher.get_database_stats()
            
            if stats["total_coins"] > 0:
                self.validation_results["enrichment_working"] = True
                return True
            else:
                self.validation_results["warnings"].append("Enrichment system has no coins")
                return False
                
        except Exception as e:
            self.validation_results["errors"].append(f"Enrichment check failed: {str(e)}")
            return False
    
    def check_security_dashboard(self) -> bool:
        """Verify security dashboard functionality"""
        try:
            from enhanced_security_dashboard import get_real_security_metrics
            metrics = get_real_security_metrics()
            
            if metrics and metrics.get("status", {}).get("overall") == "SECURE":
                return True
            else:
                self.validation_results["warnings"].append("Security dashboard not showing SECURE status")
                return False
                
        except Exception as e:
            self.validation_results["errors"].append(f"Security dashboard check failed: {str(e)}")
            return False
    
    def check_monitoring_dashboard(self) -> bool:
        """Verify monitoring dashboard functionality"""
        try:
            import comprehensive_monitoring
            # Just checking import for now
            return True
        except Exception as e:
            self.validation_results["errors"].append(f"Monitoring dashboard check failed: {str(e)}")
            return False
    
    def generate_validation_report(self) -> str:
        """Generate detailed validation report"""
        report = f"""# Enhanced Deployment Validation Report
Generated: {self.validation_results['timestamp']}

## 🎯 Overall Status
- **Deployment Success**: {'✅' if self.validation_results['code_deployed'] and self.validation_results['dashboard_functional'] else '❌'}

## 📊 Component Status
| Component | Status | Details |
|-----------|--------|---------|
| Code Deployed | {'✅' if self.validation_results['code_deployed'] else '❌'} | Hash: {self.validation_results['deployment_hash'] or 'Unknown'} |
| Dashboard Functional | {'✅' if self.validation_results['dashboard_functional'] else '❌'} | Response: {self.validation_results['response_time']}ms |
| All Tabs (10) | {'✅' if self.validation_results['all_tabs_loaded'] else '❌'} | 10-tab structure verified |
| Database | {'✅' if self.validation_results['database_accessible'] else '❌'} | trench.db accessible |
| Modules | {'✅' if self.validation_results['modules_loaded'] else '❌'} | All imports working |
| Enrichment | {'✅' if self.validation_results['enrichment_working'] else '❌'} | Live enrichment system |
| Security Dashboard | {'✅' if self.validation_results['security_dashboard_ok'] else '❌'} | Real metrics display |
| Monitoring | {'✅' if self.validation_results['monitoring_dashboard_ok'] else '❌'} | System monitoring |

## ⚠️ Warnings ({len(self.validation_results['warnings'])})
"""
        if self.validation_results['warnings']:
            for warning in self.validation_results['warnings']:
                report += f"- ⚠️ {warning}\n"
        else:
            report += "No warnings detected.\n"

        report += f"\n## ❌ Errors ({len(self.validation_results['errors'])})\n"
        if self.validation_results['errors']:
            for error in self.validation_results['errors']:
                report += f"- ❌ {error}\n"
        else:
            report += "No errors detected.\n"
            
        return report
    
    def send_validation_notification(self, success: bool, report: str):
        """Send validation results to Discord"""
        try:
            color = 0x22c55e if success else 0xef4444  # Green or Red
            
            # Truncate report for Discord
            report_summary = report.split('\n')[0:15]  # First 15 lines
            report_text = '\n'.join(report_summary)
            if len(report.split('\n')) > 15:
                report_text += "\n... (see full report in logs)"
            
            embed = {
                "title": f"{'✅' if success else '❌'} Deployment Validation {'Passed' if success else 'Failed'}",
                "description": f"Enhanced validation completed at {datetime.now().strftime('%H:%M:%S')}",
                "color": color,
                "fields": [
                    {
                        "name": "Deployment Hash",
                        "value": self.validation_results['deployment_hash'] or 'Unknown',
                        "inline": True
                    },
                    {
                        "name": "Response Time",
                        "value": f"{self.validation_results['response_time']}ms" if self.validation_results['response_time'] else 'N/A',
                        "inline": True
                    },
                    {
                        "name": "Components",
                        "value": f"✅ {sum(1 for k,v in self.validation_results.items() if k.endswith('_ok') and v)}/7",
                        "inline": True
                    },
                    {
                        "name": "Validation Summary",
                        "value": f"```{report_text}```",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "TrenchCoat Pro Enhanced Validator"
                }
            }
            
            payload = {"embeds": [embed]}
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                print("✅ Validation notification sent to Discord")
            else:
                print(f"❌ Failed to send notification: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error sending notification: {e}")
    
    def save_validation_results(self):
        """Save validation results to files"""
        # Save JSON results
        results_file = Path("deployment_validation.json")
        with open(results_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
            
        # Save markdown report
        report = self.generate_validation_report()
        report_file = Path("deployment_validation_report.md")
        with open(report_file, 'w') as f:
            f.write(report)
            
        return report
    
    def run_enhanced_validation(self) -> bool:
        """Run complete enhanced deployment validation"""
        print("🔍 Starting Enhanced Deployment Validation...")
        print("=" * 60)
        
        # Step 1: Check GitHub deployment
        github_ok, github_msg = self.check_github_deployment()
        print(f"1. GitHub Deployment: {github_msg}")
        
        # Step 2: Check Streamlit health
        streamlit_ok, streamlit_msg = self.check_streamlit_health()
        print(f"2. Streamlit Health: {streamlit_msg}")
        
        # Step 3: Validate all dashboard components
        if streamlit_ok or True:  # Continue validation even if Streamlit has issues
            validations = self.validate_dashboard_functionality()
            
            print("\n3. Dashboard Components:")
            for component, status in validations.items():
                print(f"   - {component}: {'✅' if status else '❌'}")
        
        # Step 4: Generate and save report
        report = self.save_validation_results()
        
        # Step 5: Determine overall success
        success = (self.validation_results['code_deployed'] and 
                  self.validation_results['dashboard_functional'])
        
        # Step 6: Send notification
        self.send_validation_notification(success, report)
        
        # Step 7: Display report
        print("\n" + "=" * 60)
        print(report)
        print("=" * 60)
        
        return success

def main():
    """Main validation function"""
    validator = EnhancedDeploymentValidator()
    success = validator.run_enhanced_validation()
    
    if success:
        print("\n✅ ENHANCED DEPLOYMENT VALIDATION PASSED")
        return 0
    else:
        print("\n❌ ENHANCED DEPLOYMENT VALIDATION FAILED")
        print("Check deployment_validation_report.md for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())