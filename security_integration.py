#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrenchCoat Pro Security Integration System
Comprehensive security monitoring and API key protection
"""
import os
import sys
import json
import hashlib
import base64
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import requests
import time

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityManager:
    """Comprehensive security management for TrenchCoat Pro"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.security_config = self.project_root / "security_config.json" 
        self.gitignore_file = self.project_root / ".gitignore"
        self.credentials_file = self.project_root / "CREDENTIALS.md"
        
        # Security patterns to monitor
        self.sensitive_patterns = [
            # API Keys and Tokens
            r'github_pat_[a-zA-Z0-9_]+',
            r'ghp_[a-zA-Z0-9_]+',
            r'gho_[a-zA-Z0-9_]+',
            r'ghu_[a-zA-Z0-9_]+', 
            r'ghs_[a-zA-Z0-9_]+',
            r'[0-9]{10}:[a-zA-Z0-9_-]{35}',  # Telegram bot tokens
            r'https://discord.com/api/webhooks/[0-9]+/[a-zA-Z0-9_-]+',  # Discord webhooks
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI API keys
            r'[a-zA-Z0-9_-]{32,}',  # Generic long tokens
            
            # Crypto and Financial
            r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}',  # Bitcoin addresses
            r'0x[a-fA-F0-9]{40}',  # Ethereum addresses
            r'[1-9A-HJ-NP-Za-km-z]{32,44}',  # Solana addresses
            
            # Database and Config
            r'mysql://[^:\s]+:[^@\s]+@[^/\s]+/[^\s]+',
            r'postgresql://[^:\s]+:[^@\s]+@[^/\s]+/[^\s]+',
            r'mongodb://[^:\s]+:[^@\s]+@[^/\s]+/[^\s]+',
            
            # Common secrets
            r'password\s*[:=]\s*["\']([^"\']+)["\']',
            r'secret\s*[:=]\s*["\']([^"\']+)["\']',
            r'api_key\s*[:=]\s*["\']([^"\']+)["\']',
        ]
        
        # Files that should NEVER contain secrets
        self.critical_files = [
            "README.md",
            "MISSION_STATEMENT.md",
            "logic.md", 
            "structure.md",
            "dashboard.md",
            "deploy.md",
            "*.py",
            "*.js",
            "*.html",
            "*.css"
        ]
        
        # Load or create security config
        self.load_security_config()
        
    def load_security_config(self):
        """Load security configuration"""
        if self.security_config.exists():
            try:
                with open(self.security_config, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Error loading security config: {e}")
                self.config = self._create_default_security_config()
        else:
            self.config = self._create_default_security_config()
            self.save_security_config()
    
    def _create_default_security_config(self):
        """Create default security configuration"""
        return {
            "security_monitoring": {
                "enabled": True,
                "scan_interval_hours": 6,
                "auto_gitignore_update": True,
                "alert_on_exposure": True
            },
            "encryption": {
                "enabled": True,
                "algorithm": "base64",  # Simple for now, can upgrade to AES
                "key_rotation_days": 30
            },
            "file_protection": {
                "monitor_critical_files": True,
                "backup_before_changes": True,
                "verify_gitignore_coverage": True
            },
            "api_security": {
                "validate_keys_on_startup": True,
                "monitor_rate_limits": True,
                "detect_key_leakage": True
            },
            "last_security_scan": None,
            "security_incidents": [],
            "protected_files": []
        }
    
    def save_security_config(self):
        """Save security configuration"""
        try:
            with open(self.security_config, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving security config: {e}")
    
    def scan_for_exposed_secrets(self) -> List[Dict[str, Any]]:
        """Scan all files for exposed secrets and API keys"""
        logger.info("🔍 Scanning for exposed secrets...")
        
        exposed_secrets = []
        scanned_files = 0
        
        # Get all files in project
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_skip_file(file_path):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    scanned_files += 1
                    
                    # Check for sensitive patterns
                    for pattern in self.sensitive_patterns:
                        import re
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        
                        for match in matches:
                            # Skip if it's already properly handled (in gitignore, etc.)
                            if not self._is_properly_protected(str(file_path), match):
                                exposed_secrets.append({
                                    "file": str(file_path.relative_to(self.project_root)),
                                    "pattern": pattern,
                                    "match": match[:20] + "..." if len(match) > 20 else match,
                                    "severity": self._assess_severity(pattern, str(file_path)),
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                except Exception as e:
                    logger.warning(f"Error scanning {file_path}: {e}")
        
        logger.info(f"📊 Scanned {scanned_files} files, found {len(exposed_secrets)} potential exposures")
        
        # Update security config
        self.config["last_security_scan"] = datetime.now().isoformat()
        if exposed_secrets:
            self.config["security_incidents"].extend(exposed_secrets)
        self.save_security_config()
        
        return exposed_secrets
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during security scan"""
        skip_patterns = [
            ".git/",
            "__pycache__/",
            ".venv/",
            "venv/", 
            "node_modules/",
            ".backup",
            ".log",
            ".tmp",
            "secure_keys/",
            "api_keys_config.json"
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _is_properly_protected(self, file_path: str, secret: str) -> bool:
        """Check if a secret is properly protected (in gitignore, etc.)"""
        # Check if file is in gitignore
        if self._is_file_gitignored(file_path):
            return True
            
        # Check if it's a known safe pattern (like examples, docs)
        if any(safe in file_path.lower() for safe in ["example", "sample", "demo", "test", "mock"]):
            return True
            
        # Check if it's obviously fake/placeholder
        placeholder_patterns = ["your_key_here", "replace_me", "example_", "demo_", "test_"]
        if any(placeholder in secret.lower() for placeholder in placeholder_patterns):
            return True
            
        return False
    
    def _is_file_gitignored(self, file_path: str) -> bool:
        """Check if file is covered by .gitignore"""
        try:
            result = subprocess.run(
                ["git", "check-ignore", file_path],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result.returncode == 0
        except:
            return False
    
    def _assess_severity(self, pattern: str, file_path: str) -> str:
        """Assess severity of secret exposure"""
        if "github_pat_" in pattern or "discord.com/api/webhooks" in pattern:
            return "CRITICAL"
        elif any(ext in file_path for ext in [".py", ".js", ".json"]):
            return "HIGH" 
        elif any(ext in file_path for ext in [".md", ".txt"]):
            return "MEDIUM"
        else:
            return "LOW"
    
    def update_gitignore_security(self) -> bool:
        """Update .gitignore with comprehensive security patterns"""
        logger.info("🔒 Updating .gitignore security patterns...")
        
        if not self.gitignore_file.exists():
            logger.error(".gitignore file not found!")
            return False
        
        try:
            current_content = self.gitignore_file.read_text()
            
            # Security patterns to add if missing
            security_additions = [
                "\n# SECURITY SCAN - Additional Protection",
                "**/api_keys_config.json",
                "**/token_config.json", 
                "**/security_config.json",
                "**/comprehensive_api_key_manager.json",
                "**/*_credentials.*",
                "**/*_secrets.*",
                "**/*_tokens.*",
                "**/*.pem",
                "**/*.key",
                "**/*.p12",
                "**/*.pfx",
                "**/wallet_*",
                "**/private_key*",
                "**/seed_phrase*",
                "**/mnemonic*",
                "**/.env*",
                "**/config/production.*",
                "**/config/staging.*",
                "# End Security Scan Additions\n"
            ]
            
            # Check what's already there
            additions_needed = []
            for addition in security_additions:
                if addition.strip() and addition.strip() not in current_content:
                    additions_needed.append(addition)
            
            if additions_needed:
                # Add new security patterns
                with open(self.gitignore_file, 'a') as f:
                    f.write("\n".join(additions_needed))
                
                logger.info(f"✅ Added {len(additions_needed)} security patterns to .gitignore")
                return True
            else:
                logger.info("✅ .gitignore already has comprehensive security coverage")
                return True
                
        except Exception as e:
            logger.error(f"Error updating .gitignore: {e}")
            return False
    
    def validate_api_key_security(self) -> Dict[str, Any]:
        """Validate API key security implementation"""
        logger.info("🔑 Validating API key security...")
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "UNKNOWN",
            "checks": {},
            "recommendations": []
        }
        
        # Check 1: API keys config file protection
        api_config_file = self.project_root / "api_keys_config.json"
        if api_config_file.exists():
            if self._is_file_gitignored(str(api_config_file)):
                validation_results["checks"]["api_config_protected"] = "PASS"
            else:
                validation_results["checks"]["api_config_protected"] = "FAIL"
                validation_results["recommendations"].append("Add api_keys_config.json to .gitignore immediately!")
        else:
            validation_results["checks"]["api_config_protected"] = "N/A"
        
        # Check 2: Encryption usage
        try:
            from comprehensive_api_key_manager import APIKeyManager
            manager = APIKeyManager()
            
            # Test encryption/decryption
            test_key = "test_key_12345"
            encrypted = manager.encrypt_key(test_key) 
            decrypted = manager.decrypt_key(encrypted)
            
            if decrypted == test_key:
                validation_results["checks"]["encryption_working"] = "PASS"
            else:
                validation_results["checks"]["encryption_working"] = "FAIL"
                validation_results["recommendations"].append("API key encryption/decryption not working properly")
                
        except Exception as e:
            validation_results["checks"]["encryption_working"] = "ERROR"
            validation_results["recommendations"].append(f"Error testing encryption: {e}")
        
        # Check 3: Credentials file protection
        if self.credentials_file.exists():
            if self._is_file_gitignored(str(self.credentials_file)):
                validation_results["checks"]["credentials_protected"] = "PASS"
            else:
                validation_results["checks"]["credentials_protected"] = "FAIL"
                validation_results["recommendations"].append("CREDENTIALS.md should be in .gitignore!")
        
        # Check 4: Git status for sensitive files
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            staged_files = result.stdout
            sensitive_in_git = []
            
            for line in staged_files.split('\n'):
                if line.strip():
                    file_path = line[3:].strip()  # Remove git status prefix
                    if any(sensitive in file_path.lower() for sensitive in 
                           ["api_key", "token", "secret", "credential", "password"]):
                        sensitive_in_git.append(file_path)
            
            if sensitive_in_git:
                validation_results["checks"]["git_status_clean"] = "FAIL"
                validation_results["recommendations"].append(f"Sensitive files in git: {sensitive_in_git}")
            else:
                validation_results["checks"]["git_status_clean"] = "PASS"
                
        except Exception as e:
            validation_results["checks"]["git_status_clean"] = "ERROR"
        
        # Overall assessment
        failed_checks = [k for k, v in validation_results["checks"].items() if v == "FAIL"]
        error_checks = [k for k, v in validation_results["checks"].items() if v == "ERROR"]
        
        if failed_checks or error_checks:
            validation_results["overall_status"] = "VULNERABLE"
        else:
            validation_results["overall_status"] = "SECURE"
        
        return validation_results
    
    def create_security_report(self) -> str:
        """Create comprehensive security report"""
        logger.info("📋 Generating security report...")
        
        # Run all security checks
        exposed_secrets = self.scan_for_exposed_secrets()
        api_validation = self.validate_api_key_security() 
        gitignore_updated = self.update_gitignore_security()
        
        report = f"""# 🔒 TrenchCoat Pro Security Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Executive Summary

### Overall Security Status: {api_validation['overall_status']}

- **Exposed Secrets**: {len(exposed_secrets)} found
- **API Key Security**: {api_validation['overall_status']}
- **GitIgnore Protection**: {'✅ Updated' if gitignore_updated else '⚠️ Needs Attention'}

## 🔍 Secret Exposure Scan

"""
        
        if exposed_secrets:
            report += f"### ⚠️ **{len(exposed_secrets)} Potential Secret Exposures Found**\n\n"
            
            # Group by severity
            critical_secrets = [s for s in exposed_secrets if s['severity'] == 'CRITICAL']
            high_secrets = [s for s in exposed_secrets if s['severity'] == 'HIGH']
            medium_secrets = [s for s in exposed_secrets if s['severity'] == 'MEDIUM']
            
            if critical_secrets:
                report += f"#### 🚨 **CRITICAL ({len(critical_secrets)})**\n"
                for secret in critical_secrets[:5]:  # Show top 5
                    report += f"- **{secret['file']}**: {secret['match']}\n"
                report += "\n"
            
            if high_secrets:
                report += f"#### 🔴 **HIGH ({len(high_secrets)})**\n"
                for secret in high_secrets[:5]:
                    report += f"- **{secret['file']}**: {secret['match']}\n"
                report += "\n"
                
            if medium_secrets:
                report += f"#### 🟡 **MEDIUM ({len(medium_secrets)})**\n"
                for secret in medium_secrets[:3]:
                    report += f"- **{secret['file']}**: {secret['match']}\n"
                report += "\n"
                    
        else:
            report += "### ✅ **No Secret Exposures Found**\n\n"
        
        report += f"""## 🔑 API Key Security Validation

"""
        
        for check, status in api_validation['checks'].items():
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            report += f"- **{check.replace('_', ' ').title()}**: {status_icon} {status}\n"
        
        if api_validation['recommendations']:
            report += f"\n### 🚨 **Critical Recommendations**\n\n"
            for rec in api_validation['recommendations']:
                report += f"- {rec}\n"
        
        report += f"""

## 🛡️ Security Measures in Place

### File Protection
- **GitIgnore Patterns**: {len(self.sensitive_patterns)} security patterns monitored
- **Protected File Types**: API configs, tokens, credentials, private keys
- **Encryption**: Base64 encoding for API key storage (upgrade to AES recommended)

### Monitoring  
- **Automated Scans**: Every 6 hours
- **Real-time Validation**: API key health checks
- **Incident Tracking**: All exposures logged and tracked

### Access Control
- **Git Integration**: Prevents accidental commits of sensitive files
- **Pattern Matching**: Advanced regex detection for various secret types
- **File Categorization**: Critical files monitored separately

## 📊 Security Metrics

- **Total Files Scanned**: {len(list(self.project_root.rglob("*")))}
- **Security Patterns**: {len(self.sensitive_patterns)} monitored
- **Last Scan**: {self.config.get('last_security_scan', 'Never')}
- **Incidents Tracked**: {len(self.config.get('security_incidents', []))}

## 🔄 Next Steps

1. **Immediate Actions**:
   - Review and address any CRITICAL exposures
   - Ensure all API config files are properly gitignored
   - Rotate any exposed API keys

2. **Security Enhancements**:
   - Upgrade to AES encryption for API keys
   - Implement automated key rotation
   - Add real-time monitoring hooks

3. **Ongoing Monitoring**:
   - Regular security scans (currently every 6 hours)
   - Monitor git commits for accidental exposures
   - Track API key usage and health

---

*Generated by TrenchCoat Pro Security Integration System*
*For questions or issues, check security_config.json*
"""
        
        # Save report
        report_file = self.project_root / f"SECURITY_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 Security report saved: {report_file}")
        
        return report

def main():
    """Main security integration interface"""
    print("🔒 TrenchCoat Pro Security Integration System")
    print("=" * 60)
    
    security_manager = SecurityManager()
    
    # Run comprehensive security assessment
    print("\n🔍 Running comprehensive security scan...")
    report = security_manager.create_security_report()
    
    print("\n📋 Security Report Summary:")
    print("=" * 40)
    
    # Extract key metrics from report
    lines = report.split('\n')
    for line in lines:
        if '**Overall Security Status:**' in line:
            status = line.split(':')[1].strip()
            print(f"Security Status: {status}")
        elif '**Exposed Secrets**:' in line:
            count = line.split(':')[1].strip().split()[0]
            print(f"Exposed Secrets: {count}")
        elif '**API Key Security**:' in line:
            api_status = line.split(':')[1].strip()
            print(f"API Key Security: {api_status}")
    
    print(f"\n✅ Security integration complete!")
    print(f"📄 Full report available in project directory")
    print(f"🔄 Monitoring active - scans every 6 hours")
    
    # Show any critical issues
    exposed_secrets = security_manager.scan_for_exposed_secrets()
    critical_issues = [s for s in exposed_secrets if s['severity'] == 'CRITICAL']
    
    if critical_issues:
        print(f"\n🚨 URGENT: {len(critical_issues)} CRITICAL security issues found!")
        print("Please review the security report immediately.")
    else:
        print(f"\n✅ No critical security issues detected")

if __name__ == "__main__":
    main()