"""
🔒 TrenchCoat Pro - Security Hardening System
API key management, input validation, and security monitoring
"""

import os
import secrets
import hashlib
import hmac
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import bleach
from cryptography.fernet import Fernet
from pathlib import Path
import json

from config import config
from monitoring import logger, monitor

@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    timestamp: datetime
    event_type: str
    severity: str  # low, medium, high, critical
    description: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SecurityManager:
    """Comprehensive security management"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        self.security_events = []
        self.rate_limiters = {}
        
        # Security patterns
        self.sql_injection_patterns = [
            r"(\bunion\b.*\bselect\b|\bselect\b.*\bfrom\b|\binsert\b.*\binto\b|\bupdate\b.*\bset\b|\bdelete\b.*\bfrom\b)",
            r"(--|\#|\/\*|\*\/)",
            r"(\bor\b\s*\d+\s*=\s*\d+|\band\b\s*\d+\s*=\s*\d+)",
            r"(\bdrop\b.*\btable\b|\bcreate\b.*\btable\b|\balter\b.*\btable\b)"
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>"
        ]
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = Path(".streamlit/encryption.key")
        key_file.parent.mkdir(exist_ok=True)
        
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            # Set restrictive permissions (Windows)
            os.chmod(key_file, 0o600)
            return key
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key"""
        try:
            return self.cipher.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            logger.log_error("Failed to decrypt API key", e)
            return ""
    
    def validate_input(self, input_str: str, input_type: str = "general") -> Tuple[bool, str]:
        """Validate and sanitize user input"""
        if not input_str:
            return True, ""
        
        # Check length
        if len(input_str) > 10000:
            return False, "Input too long"
        
        # Check for SQL injection
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                self.log_security_event(
                    "sql_injection_attempt",
                    "high",
                    f"SQL injection pattern detected: {pattern}"
                )
                return False, "Invalid input detected"
        
        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                self.log_security_event(
                    "xss_attempt",
                    "high",
                    f"XSS pattern detected: {pattern}"
                )
                return False, "Invalid input detected"
        
        # Type-specific validation
        if input_type == "contract_address":
            # Solana address validation
            if not re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", input_str):
                return False, "Invalid contract address format"
        
        elif input_type == "ticker":
            # Ticker symbol validation
            if not re.match(r"^[A-Z0-9]{1,10}$", input_str.upper()):
                return False, "Invalid ticker format"
        
        elif input_type == "numeric":
            # Numeric validation
            try:
                float(input_str)
            except ValueError:
                return False, "Invalid numeric value"
        
        # Sanitize HTML
        clean = bleach.clean(input_str, tags=[], strip=True)
        
        return True, clean
    
    def check_rate_limit(self, user_id: str, action: str, 
                        limit: int = 100, window: int = 3600) -> bool:
        """Check if user has exceeded rate limit"""
        key = f"{user_id}:{action}"
        now = datetime.now()
        
        if key not in self.rate_limiters:
            self.rate_limiters[key] = []
        
        # Remove old entries
        cutoff = now - timedelta(seconds=window)
        self.rate_limiters[key] = [
            ts for ts in self.rate_limiters[key] if ts > cutoff
        ]
        
        # Check limit
        if len(self.rate_limiters[key]) >= limit:
            self.log_security_event(
                "rate_limit_exceeded",
                "medium",
                f"Rate limit exceeded for {action}",
                user_id=user_id
            )
            return False
        
        # Add current request
        self.rate_limiters[key].append(now)
        return True
    
    def generate_session_token(self, user_id: str) -> str:
        """Generate secure session token"""
        data = f"{user_id}:{datetime.now().isoformat()}:{secrets.token_urlsafe(32)}"
        return self.cipher.encrypt(data.encode()).decode()
    
    def verify_session_token(self, token: str, max_age: int = 86400) -> Optional[str]:
        """Verify session token and return user_id"""
        try:
            data = self.cipher.decrypt(token.encode()).decode()
            user_id, timestamp, _ = data.split(":", 2)
            
            # Check age
            token_time = datetime.fromisoformat(timestamp)
            if (datetime.now() - token_time).total_seconds() > max_age:
                return None
            
            return user_id
        except:
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_bytes(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt, 
                                      100000)
        return (salt + pwdhash).hex()
    
    def verify_password(self, password: str, hash_str: str) -> bool:
        """Verify password against hash"""
        try:
            hash_bytes = bytes.fromhex(hash_str)
            salt = hash_bytes[:32]
            stored_hash = hash_bytes[32:]
            
            pwdhash = hashlib.pbkdf2_hmac('sha256',
                                         password.encode('utf-8'),
                                         salt,
                                         100000)
            
            return hmac.compare_digest(stored_hash, pwdhash)
        except:
            return False
    
    def log_security_event(self, event_type: str, severity: str, 
                          description: str, **kwargs):
        """Log security event"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            description=description,
            **kwargs
        )
        
        self.security_events.append(event)
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
        
        # Log to file
        logger.log_warning(f"SECURITY: {event_type} - {description}")
        
        # Alert on high/critical events
        if severity in ["high", "critical"]:
            monitor.record_metric("security_alert", 1, {
                "type": event_type,
                "severity": severity
            })
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        report = {
            "total_events": len(self.security_events),
            "events_by_type": {},
            "events_by_severity": {},
            "recent_high_severity": []
        }
        
        for event in self.security_events:
            # Count by type
            if event.event_type not in report["events_by_type"]:
                report["events_by_type"][event.event_type] = 0
            report["events_by_type"][event.event_type] += 1
            
            # Count by severity
            if event.severity not in report["events_by_severity"]:
                report["events_by_severity"][event.severity] = 0
            report["events_by_severity"][event.severity] += 1
            
            # Recent high severity
            if event.severity in ["high", "critical"]:
                report["recent_high_severity"].append({
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "description": event.description
                })
        
        # Keep only last 10 high severity events
        report["recent_high_severity"] = report["recent_high_severity"][-10:]
        
        return report
    
    def secure_api_keys(self) -> Dict[str, str]:
        """Get all API keys securely"""
        api_keys = {}
        
        # Check environment variables
        for service in ["dexscreener", "birdeye", "coingecko", "messari"]:
            env_key = f"{service.upper()}_API_KEY"
            if env_value := os.getenv(env_key):
                api_keys[service] = env_value
        
        # Check encrypted storage
        encrypted_file = Path(".streamlit/api_keys.enc")
        if encrypted_file.exists():
            try:
                encrypted_data = encrypted_file.read_text()
                decrypted = self.cipher.decrypt(encrypted_data.encode()).decode()
                stored_keys = json.loads(decrypted)
                api_keys.update(stored_keys)
            except:
                logger.log_error("Failed to decrypt API keys")
        
        return api_keys
    
    def save_api_key(self, service: str, api_key: str):
        """Save API key securely"""
        # Load existing keys
        api_keys = self.secure_api_keys()
        api_keys[service] = api_key
        
        # Encrypt and save
        encrypted_file = Path(".streamlit/api_keys.enc")
        encrypted_file.parent.mkdir(exist_ok=True)
        
        encrypted_data = self.cipher.encrypt(
            json.dumps(api_keys).encode()
        ).decode()
        
        encrypted_file.write_text(encrypted_data)
        os.chmod(encrypted_file, 0o600)
        
        logger.log_info(f"API key saved for {service}")

# Global instance
security_manager = SecurityManager()

# Streamlit integration
def render_security_dashboard():
    """Render security dashboard in Streamlit"""
    import streamlit as st
    
    st.header("🔒 Security Dashboard")
    
    report = security_manager.get_security_report()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", report["total_events"])
    
    with col2:
        high_events = report["events_by_severity"].get("high", 0)
        critical_events = report["events_by_severity"].get("critical", 0)
        st.metric("High/Critical", high_events + critical_events)
    
    with col3:
        unique_types = len(report["events_by_type"])
        st.metric("Event Types", unique_types)
    
    with col4:
        # Calculate security score
        score = 100
        if report["total_events"] > 0:
            high_ratio = (high_events + critical_events) / report["total_events"]
            score = max(0, 100 - int(high_ratio * 100))
        st.metric("Security Score", f"{score}/100")
    
    # Recent high severity events
    if report["recent_high_severity"]:
        st.subheader("⚠️ Recent Security Alerts")
        for event in report["recent_high_severity"][-5:]:
            st.warning(f"**{event['type']}** - {event['description']} ({event['timestamp']})")
    
    # API Key Management
    st.subheader("🔑 API Key Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        service = st.selectbox("Service", 
                             ["dexscreener", "birdeye", "coingecko", "messari"])
    
    with col2:
        api_key = st.text_input("API Key", type="password")
    
    if st.button("Save API Key"):
        if api_key:
            security_manager.save_api_key(service, api_key)
            st.success(f"API key saved for {service}")
        else:
            st.error("Please enter an API key")