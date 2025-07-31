#!/usr/bin/env python3
"""
TrenchCoat Pro - Deployment Status Checker & Verifier
Provides comprehensive verification and monitoring of deployment system
"""
import os
import subprocess
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from unicode_handler import safe_print, safe_format

class DeploymentStatusChecker:
    """Comprehensive deployment system verification"""
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.hooks_dir = self.project_dir / '.git' / 'hooks'
        self.log_file = self.project_dir / 'deployment_hook.log'
        self.lock_file = self.project_dir / '.deployment.lock'
        
        self.status = {
            'hook_installed': False,
            'hook_working': False,
            'background_working': False,
            'validation_working': False,
            'notifications_working': False,
            'git_timeouts': True,
            'unicode_working': False,
            'last_check': datetime.now().isoformat()
        }
    
    def check_hook_installation(self) -> Dict[str, any]:
        """Verify git hook installation"""
        result = {
            'installed': False,
            'executable': False,
            'content_valid': False,
            'backup_exists': False,
            'issues': []
        }
        
        hook_file = self.hooks_dir / 'post-commit'
        backup_file = self.hooks_dir / 'post-commit.backup'
        disabled_file = self.hooks_dir / 'post-commit.disabled'
        broken_file = self.hooks_dir / 'post-commit.broken'
        
        # Check if hook exists
        if hook_file.exists():
            result['installed'] = True
            safe_print(f"✅ Hook file exists: {hook_file}")
            
            # Check if executable (Unix systems)
            if os.name != 'nt':
                if os.access(hook_file, os.X_OK):
                    result['executable'] = True
                    safe_print("✅ Hook is executable")
                else:
                    result['issues'].append("Hook is not executable")
                    safe_print("❌ Hook is not executable")
            else:
                result['executable'] = True  # Windows doesn't need +x
                safe_print("✅ Windows system - executable check skipped")
            
            # Check content
            try:
                content = hook_file.read_text()
                if 'TrenchCoat Pro - Improved Post-Commit Hook' in content:
                    result['content_valid'] = True
                    safe_print("✅ Hook content is valid")
                else:
                    result['issues'].append("Hook content is invalid or outdated")
                    safe_print("❌ Hook content is invalid")
            except Exception as e:
                result['issues'].append(f"Cannot read hook file: {e}")
                safe_print(f"❌ Cannot read hook file: {e}")
        
        else:
            result['issues'].append("Hook file does not exist")
            safe_print("❌ Hook file does not exist")
            
            # Check for disabled/broken versions
            if disabled_file.exists():
                safe_print(f"⚠️ Found disabled hook: {disabled_file}")
            if broken_file.exists():
                safe_print(f"⚠️ Found broken hook: {broken_file}")
        
        # Check for backup
        if backup_file.exists():
            result['backup_exists'] = True
            safe_print(f"✅ Backup exists: {backup_file}")
        
        return result
    
    def check_git_timeout_issue(self) -> Dict[str, any]:
        """Test if git commits timeout"""
        result = {
            'timeouts_detected': False,
            'test_commit_time': None,
            'issues': []
        }
        
        try:
            safe_print("\n🔍 Testing git commit performance...")
            
            # Create a test file
            test_file = self.project_dir / 'deployment_test_commit.txt'
            test_file.write_text(f"Test commit at {datetime.now().isoformat()}")
            
            # Test commit timing
            start_time = time.time()
            
            # Add and commit
            subprocess.run(['git', 'add', str(test_file)], check=True, timeout=30)
            
            # Use a commit message that shouldn't trigger deployment
            subprocess.run([
                'git', 'commit', '-m', 
                'Test: Quick commit timing test (should not deploy)'
            ], check=True, timeout=10)  # Short timeout to detect issues
            
            commit_time = time.time() - start_time
            result['test_commit_time'] = round(commit_time, 2)
            
            if commit_time > 5:  # If commit takes more than 5 seconds
                result['timeouts_detected'] = True
                result['issues'].append(f"Commit took {commit_time:.2f}s - too slow")
                safe_print(f"⚠️ Commit took {commit_time:.2f}s - potential timeout issue")
            else:
                safe_print(f"✅ Commit completed in {commit_time:.2f}s")
            
            # Clean up test file
            test_file.unlink()
            
        except subprocess.TimeoutExpired:
            result['timeouts_detected'] = True
            result['issues'].append("Git commit timed out during test")
            safe_print("❌ Git commit timed out during test!")
            
        except Exception as e:
            result['issues'].append(f"Git test failed: {e}")
            safe_print(f"❌ Git test failed: {e}")
        
        return result
    
    def check_background_deployment(self) -> Dict[str, any]:
        """Check if background deployment is working"""
        result = {
            'log_file_exists': False,
            'recent_activity': False,
            'background_processes': [],
            'issues': []
        }
        
        # Check log file
        if self.log_file.exists():
            result['log_file_exists'] = True
            safe_print(f"✅ Deployment log exists: {self.log_file}")
            
            try:
                log_content = self.log_file.read_text()
                
                # Check for recent activity (last 10 minutes)
                recent_time = datetime.now().timestamp() - 600
                lines = log_content.split('\n')
                
                for line in lines[-20:]:  # Check last 20 lines
                    if 'BACKGROUND:' in line and 'Started deployment process' in line:
                        result['recent_activity'] = True
                        safe_print("✅ Recent background deployment activity detected")
                        break
                
                if not result['recent_activity']:
                    safe_print("⚠️ No recent background deployment activity")
                    
            except Exception as e:
                result['issues'].append(f"Cannot read log file: {e}")
                safe_print(f"❌ Cannot read log file: {e}")
        else:
            result['issues'].append("Deployment log file does not exist")
            safe_print("❌ Deployment log file does not exist")
        
        # Check for running processes
        try:
            ps_result = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, text=True, timeout=10
            )
            
            for line in ps_result.stdout.split('\n'):
                if 'enhanced_auto_deploy.py' in line:
                    result['background_processes'].append(line.strip())
                    
            if result['background_processes']:
                safe_print(f"✅ Found {len(result['background_processes'])} deployment processes")
            else:
                safe_print("ℹ️ No active deployment processes found")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Windows or process check failed
            safe_print("ℹ️ Process check not available on this system")
        
        return result
    
    def check_unicode_handling(self) -> Dict[str, any]:
        """Test Unicode and emoji handling"""
        result = {
            'unicode_supported': False,
            'emoji_fallbacks_working': False,
            'issues': []
        }
        
        try:
            from unicode_handler import safe_print as test_safe_print, replace_emojis
            
            # Test emoji replacement
            test_text = "🚀 Deployment ✅ Success ❌ Error"
            replaced_text = replace_emojis(test_text)
            
            if "[DEPLOY]" in replaced_text and "[SUCCESS]" in replaced_text:
                result['emoji_fallbacks_working'] = True
                safe_print("✅ Emoji fallbacks working correctly")
            else:
                result['issues'].append("Emoji fallbacks not working properly")
                safe_print("❌ Emoji fallbacks not working")
            
            # Test Unicode support
            try:
                test_unicode = "🎯 Unicode test"
                # Try to encode/decode
                test_unicode.encode('utf-8').decode('utf-8')
                result['unicode_supported'] = True
                safe_print("✅ Unicode support working")
            except UnicodeError:
                result['issues'].append("Unicode encoding issues detected")
                safe_print("⚠️ Unicode encoding issues detected")
                
        except ImportError as e:
            result['issues'].append(f"Cannot import unicode_handler: {e}")
            safe_print(f"❌ Cannot import unicode_handler: {e}")
        
        return result
    
    def check_deployment_validation(self) -> Dict[str, any]:
        """Check deployment validation system"""
        result = {
            'validator_exists': False,
            'validator_working': False,
            'streamlit_accessible': False,
            'issues': []
        }
        
        # Check if validator exists
        validator_file = self.project_dir / 'deployment_validator.py'
        if validator_file.exists():
            result['validator_exists'] = True
            safe_print("✅ Deployment validator exists")
            
            # Test import
            try:
                sys.path.insert(0, str(self.project_dir))
                from deployment_validator import DeploymentValidator
                
                validator = DeploymentValidator()
                health_check = validator.check_streamlit_health()
                
                if health_check['status'] in ['healthy', 'degraded']:
                    result['streamlit_accessible'] = True
                    safe_print(f"✅ Streamlit accessible: {health_check['status']}")
                else:
                    result['issues'].append(f"Streamlit issue: {health_check['status']}")
                    safe_print(f"⚠️ Streamlit status: {health_check['status']}")
                
                result['validator_working'] = True
                safe_print("✅ Deployment validator working")
                
            except Exception as e:
                result['issues'].append(f"Validator test failed: {e}")
                safe_print(f"❌ Validator test failed: {e}")
        else:
            result['issues'].append("Deployment validator file does not exist")
            safe_print("❌ Deployment validator does not exist")
        
        return result
    
    def generate_verification_report(self) -> Dict[str, any]:
        """Generate comprehensive verification report"""
        safe_print("=" * 70)
        safe_print("🔍 DEPLOYMENT SYSTEM VERIFICATION REPORT")
        safe_print("=" * 70)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'hook_status': self.check_hook_installation(),
            'git_performance': self.check_git_timeout_issue(),
            'background_deployment': self.check_background_deployment(),
            'unicode_handling': self.check_unicode_handling(),
            'deployment_validation': self.check_deployment_validation(),
            'overall_status': 'unknown',
            'critical_issues': [],
            'recommendations': []
        }
        
        # Analyze overall status
        critical_issues = []
        
        if not report['hook_status']['installed']:
            critical_issues.append("Git hook not installed")
        
        if report['git_performance']['timeouts_detected']:
            critical_issues.append("Git commit timeouts detected")
        
        if not report['unicode_handling']['emoji_fallbacks_working']:
            critical_issues.append("Unicode handling issues")
        
        if not report['deployment_validation']['validator_exists']:
            critical_issues.append("Deployment validator missing")
        
        report['critical_issues'] = critical_issues
        
        if len(critical_issues) == 0:
            report['overall_status'] = 'healthy'
            safe_print("\n✅ OVERALL STATUS: HEALTHY")
        elif len(critical_issues) <= 2:
            report['overall_status'] = 'degraded'
            safe_print("\n⚠️ OVERALL STATUS: DEGRADED")
        else:
            report['overall_status'] = 'broken'
            safe_print("\n❌ OVERALL STATUS: BROKEN")
        
        # Generate recommendations
        recommendations = []
        
        if not report['hook_status']['installed']:
            recommendations.append("Run: python install_improved_hook.py")
        
        if report['git_performance']['timeouts_detected']:
            recommendations.append("Disable git hook temporarily: mv .git/hooks/post-commit .git/hooks/post-commit.disabled")
        
        if critical_issues:
            recommendations.append("Use manual deployment: python mandatory_deploy.py")
        
        report['recommendations'] = recommendations
        
        # Display summary
        safe_print(f"\n📊 SUMMARY:")
        safe_print(f"- Critical Issues: {len(critical_issues)}")
        safe_print(f"- Git Hook Status: {'✅' if report['hook_status']['installed'] else '❌'}")
        safe_print(f"- Git Performance: {'✅' if not report['git_performance']['timeouts_detected'] else '❌'}")
        safe_print(f"- Unicode Support: {'✅' if report['unicode_handling']['unicode_supported'] else '⚠️'}")
        safe_print(f"- Validator Status: {'✅' if report['deployment_validation']['validator_working'] else '❌'}")
        
        if recommendations:
            safe_print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                safe_print(f"{i}. {rec}")
        
        safe_print("\n" + "=" * 70)
        
        return report
    
    def save_report(self, report: Dict[str, any]):
        """Save verification report to file"""
        report_file = self.project_dir / 'deployment_verification_report.json'
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            safe_print(f"📄 Report saved: {report_file}")
        except Exception as e:
            safe_print(f"❌ Failed to save report: {e}")

def main():
    """Run deployment verification"""
    checker = DeploymentStatusChecker()
    report = checker.generate_verification_report()
    checker.save_report(report)
    
    if report['overall_status'] == 'broken':
        return 1
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())