#!/usr/bin/env python3
"""
Comprehensive Deployment Step Validator
Validates each step of the deployment process
"""
import subprocess
import sys
import os
import requests
import time
from datetime import datetime
from pathlib import Path
from unicode_handler import safe_print

class DeploymentStepValidator:
    """Validates all deployment steps comprehensively"""
    
    def __init__(self):
        self.streamlit_url = "https://trenchcoat-pro.streamlit.app/"
        self.results = []
        
    def log_result(self, step: str, success: bool, details: str):
        """Log validation result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'step': step,
            'success': success,
            'details': details,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.results.append(result)
        safe_print(f"{status} {step}: {details}")
        return success
    
    def validate_git_status(self) -> bool:
        """Check if all changes are committed"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return self.log_result("Git Status", False, "Git command failed")
            
            uncommitted = result.stdout.strip()
            if uncommitted:
                modified_files = [line.strip() for line in uncommitted.split('\n') if line.strip()]
                return self.log_result("Git Status", False, f"{len(modified_files)} uncommitted files")
            else:
                return self.log_result("Git Status", True, "All changes committed")
                
        except Exception as e:
            return self.log_result("Git Status", False, f"Error: {e}")
    
    def validate_git_push(self) -> bool:
        """Check if latest commit is pushed to GitHub"""
        try:
            # Get local HEAD commit
            local_result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                        capture_output=True, text=True, timeout=10)
            if local_result.returncode != 0:
                return self.log_result("Git Push", False, "Can't get local HEAD")
            
            local_commit = local_result.stdout.strip()
            
            # Get remote HEAD commit
            remote_result = subprocess.run(['git', 'rev-parse', 'origin/main'], 
                                         capture_output=True, text=True, timeout=10)
            if remote_result.returncode != 0:
                return self.log_result("Git Push", False, "Can't get remote HEAD")
            
            remote_commit = remote_result.stdout.strip()
            
            if local_commit == remote_commit:
                return self.log_result("Git Push", True, f"Synced: {local_commit[:8]}")
            else:
                return self.log_result("Git Push", False, f"Local {local_commit[:8]} != Remote {remote_commit[:8]}")
                
        except Exception as e:
            return self.log_result("Git Push", False, f"Error: {e}")
    
    def validate_streamlit_accessibility(self) -> bool:
        """Check if Streamlit app is accessible"""
        try:
            response = requests.get(self.streamlit_url, timeout=15)
            
            if response.status_code == 200:
                return self.log_result("Streamlit Access", True, f"App responding (200) in {response.elapsed.total_seconds():.1f}s")
            elif response.status_code == 303:
                return self.log_result("Streamlit Access", False, "303 redirect - app stuck in cache")
            else:
                return self.log_result("Streamlit Access", False, f"HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            return self.log_result("Streamlit Access", False, "Timeout after 15s")
        except Exception as e:
            return self.log_result("Streamlit Access", False, f"Error: {e}")
    
    def validate_streamlit_content(self) -> bool:
        """Check if Streamlit app has expected content"""
        try:
            response = requests.get(self.streamlit_url, timeout=15)
            
            if response.status_code != 200:
                return self.log_result("Streamlit Content", False, f"HTTP {response.status_code}")
            
            content = response.text.lower()
            
            # Check for key indicators of the new dashboard
            indicators = [
                ("coin data", "Coin Data tab"),
                ("telegram", "Telegram features"),
                ("trenchcoat pro", "App branding"),
                ("1,733", "Live coin count"),
                ("streamlit", "Streamlit framework")
            ]
            
            found_indicators = []
            for keyword, description in indicators:
                if keyword in content:
                    found_indicators.append(description)
            
            if len(found_indicators) >= 3:
                return self.log_result("Streamlit Content", True, f"Found: {', '.join(found_indicators)}")
            else:
                return self.log_result("Streamlit Content", False, f"Missing indicators. Found: {found_indicators}")
                
        except Exception as e:
            return self.log_result("Streamlit Content", False, f"Error: {e}")
    
    def validate_deployment_logs(self) -> bool:
        """Check deployment logs for success"""
        try:
            log_file = Path("complete_async_deploy.log")
            if not log_file.exists():
                return self.log_result("Deployment Logs", False, "Log file not found")
            
            # Read last 20 lines
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            recent_lines = lines[-20:] if len(lines) >= 20 else lines
            recent_content = ''.join(recent_lines)
            
            # Check for success indicators
            if "DEPLOY SUCCESS" in recent_content:
                if "Discord notification sent" in recent_content:
                    return self.log_result("Deployment Logs", True, "Success with notifications")
                else:
                    return self.log_result("Deployment Logs", True, "Success but no notifications")
            elif "DEPLOY FAILED" in recent_content:
                return self.log_result("Deployment Logs", False, "Deployment failed in logs")
            else:
                return self.log_result("Deployment Logs", False, "No clear success/failure in logs")
                
        except Exception as e:
            return self.log_result("Deployment Logs", False, f"Error: {e}")
    
    def run_full_validation(self) -> dict:
        """Run all validation steps"""
        safe_print("🔍 TrenchCoat Pro - Deployment Step Validator")
        safe_print("=" * 50)
        
        # Run all validations
        validations = [
            self.validate_git_status,
            self.validate_git_push,
            self.validate_deployment_logs,
            self.validate_streamlit_accessibility,
            self.validate_streamlit_content
        ]
        
        passed = 0
        total = len(validations)
        
        for validation in validations:
            if validation():
                passed += 1
            time.sleep(0.5)  # Brief pause between checks
        
        safe_print("=" * 50)
        safe_print(f"📊 VALIDATION SUMMARY: {passed}/{total} checks passed")
        
        if passed == total:
            safe_print("🎉 ALL VALIDATIONS PASSED - Deployment is successful!")
            return {'success': True, 'passed': passed, 'total': total, 'results': self.results}
        else:
            safe_print(f"⚠️  {total - passed} validations failed - Deployment issues detected")
            return {'success': False, 'passed': passed, 'total': total, 'results': self.results}

def main():
    """Main entry point"""
    validator = DeploymentStepValidator()
    result = validator.run_full_validation()
    
    return 0 if result['success'] else 1

if __name__ == "__main__":
    sys.exit(main())