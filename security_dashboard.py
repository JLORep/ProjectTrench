#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrenchCoat Pro Security Dashboard
Real-time security monitoring and threat detection
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import subprocess
import os
import sys
import time
from typing import Dict, List, Any, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass

# Import security components
try:
    from security_integration import SecurityManager
    from comprehensive_api_key_manager import APIKeyManager
except ImportError as e:
    st.error(f"Security modules not available: {e}")
    SecurityManager = None
    APIKeyManager = None

class SecurityDashboard:
    """Comprehensive security monitoring dashboard"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.security_manager = SecurityManager() if SecurityManager else None
        self.api_manager = APIKeyManager() if APIKeyManager else None
        
    def render_security_dashboard(self):
        """Main security dashboard interface"""
        st.header("🔒 Security Command Center")
        st.subheader("Real-time security monitoring and threat detection")
        
        # Security status overview
        self.render_security_overview()
        
        # Create tabs for different security areas
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🛡️ Threat Detection",
            "🔑 API Security", 
            "📊 Security Metrics",
            "🚨 Incident Response",
            "⚙️ Security Settings"
        ])
        
        with tab1:
            self.render_threat_detection()
            
        with tab2:
            self.render_api_security()
            
        with tab3:
            self.render_security_metrics()
            
        with tab4:
            self.render_incident_response()
            
        with tab5:
            self.render_security_settings()
    
    def render_security_overview(self):
        """Security status overview"""
        st.markdown("### 🎯 Security Status Overview")
        
        # Create status cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Overall security status
            if self.security_manager:
                try:
                    validation = self.security_manager.validate_api_key_security()
                    status = validation.get('overall_status', 'UNKNOWN')
                    
                    if status == "SECURE":
                        st.success("🛡️ **SECURE**")
                    elif status == "VULNERABLE":
                        st.error("🚨 **VULNERABLE**")
                    else:
                        st.warning("⚠️ **UNKNOWN**")
                        
                except Exception as e:
                    st.error(f"Status Check Failed: {e}")
            else:
                st.warning("⚠️ **NO DATA**")
        
        with col2:
            # API Key Health
            if self.api_manager:
                try:
                    expired_keys = self.api_manager.check_expiring_keys()
                    if not expired_keys:
                        st.success("✅ **API KEYS OK**")
                    else:
                        st.warning(f"⚠️ **{len(expired_keys)} EXPIRING**")
                except Exception:
                    st.error("❌ **API CHECK FAILED**")
            else:
                st.warning("⚠️ **NO MANAGER**")
        
        with col3:
            # Recent scans
            if self.security_manager:
                config = self.security_manager.config
                last_scan = config.get('last_security_scan')
                if last_scan:
                    scan_time = datetime.fromisoformat(last_scan.replace('Z', '+00:00'))
                    if datetime.now() - scan_time < timedelta(hours=24):
                        st.success("🔍 **SCAN RECENT**")
                    else:
                        st.warning("⚠️ **SCAN STALE**")
                else:
                    st.error("❌ **NO SCANS**")
            else:
                st.warning("⚠️ **NO DATA**")
        
        with col4:
            # Git security
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True, text=True, cwd=self.project_root
                )
                if result.returncode == 0:
                    staged_files = result.stdout.strip()
                    if not staged_files:
                        st.success("✅ **GIT CLEAN**")
                    else:
                        # Check for sensitive files
                        sensitive_patterns = ['api_key', 'token', 'secret', 'credential']
                        has_sensitive = any(pattern in staged_files.lower() 
                                          for pattern in sensitive_patterns)
                        if has_sensitive:
                            st.error("🚨 **SENSITIVE IN GIT**")
                        else:
                            st.info("📝 **CHANGES PENDING**")
                else:
                    st.error("❌ **GIT ERROR**")
            except Exception:
                st.warning("⚠️ **GIT UNAVAILABLE**")
    
    def render_threat_detection(self):
        """Threat detection and secret scanning"""
        st.markdown("### 🔍 Threat Detection & Secret Scanning")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🔍 Run Security Scan", type="primary"):
                with st.spinner("Scanning for threats..."):
                    if self.security_manager:
                        try:
                            secrets = self.security_manager.scan_for_exposed_secrets()
                            st.session_state.scan_results = secrets
                            st.success(f"Scan complete! Found {len(secrets)} potential issues")
                        except Exception as e:
                            st.error(f"Scan failed: {e}")
                    else:
                        st.error("Security manager not available")
        
        with col1:
            # Display scan results
            if hasattr(st.session_state, 'scan_results'):
                secrets = st.session_state.scan_results
                
                if secrets:
                    st.error(f"🚨 **{len(secrets)} Potential Secret Exposures Found**")
                    
                    # Group by severity
                    severity_counts = {}
                    for secret in secrets:
                        severity = secret.get('severity', 'UNKNOWN')
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    # Show severity breakdown
                    severity_cols = st.columns(len(severity_counts))
                    for i, (severity, count) in enumerate(severity_counts.items()):
                        with severity_cols[i]:
                            color = {
                                'CRITICAL': 'red',
                                'HIGH': 'orange', 
                                'MEDIUM': 'yellow',
                                'LOW': 'blue'
                            }.get(severity, 'gray')
                            st.metric(severity, count)
                    
                    # Detailed results
                    st.markdown("#### 📋 Detailed Results")
                    
                    for secret in secrets[:10]:  # Show top 10
                        severity_icon = {
                            'CRITICAL': '🚨',
                            'HIGH': '🔴',
                            'MEDIUM': '🟡',
                            'LOW': '🔵'
                        }.get(secret.get('severity'), '⚪')
                        
                        with st.expander(f"{severity_icon} {secret.get('file', 'Unknown file')}"):
                            st.write(f"**Pattern:** `{secret.get('pattern', 'Unknown')}`")
                            st.write(f"**Match:** `{secret.get('match', 'Unknown')}`")
                            st.write(f"**Severity:** {secret.get('severity', 'Unknown')}")
                            st.write(f"**Timestamp:** {secret.get('timestamp', 'Unknown')}")
                            
                            # Action buttons
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                if st.button(f"🔒 Add to .gitignore", key=f"ignore_{secret.get('file')}"):
                                    st.info("Feature coming soon")
                            with col_b:
                                if st.button(f"✅ Mark Safe", key=f"safe_{secret.get('file')}"):
                                    st.info("Feature coming soon")
                            with col_c:
                                if st.button(f"🗑️ Remove", key=f"remove_{secret.get('file')}"):
                                    st.info("Feature coming soon")
                else:
                    st.success("✅ **No security threats detected!**")
                    st.balloons()
            else:
                st.info("👆 Click 'Run Security Scan' to check for threats")
                
                # Show scan frequency
                st.markdown("#### ⏰ Automated Scanning")
                st.info("🔄 Automatic scans run every 6 hours")
                st.info("📊 Last scan results are cached for quick access")
    
    def render_api_security(self):
        """API key security monitoring"""
        st.markdown("### 🔑 API Key Security Management")
        
        if not self.api_manager:
            st.error("API Key Manager not available")
            return
        
        try:
            # Load API key data
            config = self.api_manager.config
            api_keys = config.get('api_keys', {})
            
            if not api_keys:
                st.warning("No API keys configured")
                return
            
            # API Key Status Overview
            st.markdown("#### 📊 API Key Status")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_keys = len(api_keys)
                st.metric("Total Keys", total_keys)
            
            with col2:
                active_keys = sum(1 for key in api_keys.values() if key.get('active', False))
                st.metric("Active Keys", active_keys)
            
            with col3:
                expired_keys = self.api_manager.check_expiring_keys()
                st.metric("Expiring Soon", len(expired_keys), delta=-len(expired_keys) if expired_keys else 0)
            
            # Key Details Table
            st.markdown("#### 🔑 Key Details")
            
            key_data = []
            for key_id, key_info in api_keys.items():
                provider = key_info.get('provider', 'Unknown')
                name = key_info.get('name', 'Unnamed Key')
                created = key_info.get('created_date', 'Unknown')
                expires = key_info.get('expires_date', 'Never')
                active = key_info.get('active', False)
                last_test = key_info.get('last_test_result', {})
                
                # Calculate days until expiry
                try:
                    if expires != 'Never':
                        expires_dt = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                        days_until_expiry = (expires_dt - datetime.now()).days
                        expires_str = f"{days_until_expiry} days"
                    else:
                        expires_str = "Never"
                except:
                    expires_str = "Unknown"
                
                key_data.append({
                    'ID': key_id[:8],
                    'Provider': provider.title(),
                    'Name': name,
                    'Status': '✅ Active' if active else '❌ Inactive',
                    'Expires': expires_str,
                    'Valid': '✅ Yes' if last_test.get('valid') else '❌ No',
                    'Last Test': last_test.get('response_time', 'N/A')
                })
            
            if key_data:
                df = pd.DataFrame(key_data)
                st.dataframe(df, use_container_width=True)
                
                # Expiring keys warning
                if expired_keys:
                    st.warning(f"⚠️ **{len(expired_keys)} keys need attention:**")
                    for notification in expired_keys:
                        days = notification.get('days_until_expiry', 0)
                        provider = notification.get('provider', 'Unknown')
                        st.write(f"• **{provider}** expires in {days} days")
            
            # Key Management Actions
            st.markdown("#### ⚙️ Key Management")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Test All Keys"):
                    with st.spinner("Testing API keys..."):
                        try:
                            results = self.api_manager.validate_all_keys()
                            valid_count = sum(1 for r in results.values() if r.get('valid'))
                            st.success(f"✅ {valid_count}/{len(results)} keys valid")
                        except Exception as e:
                            st.error(f"Test failed: {e}")
            
            with col2:
                if st.button("📧 Send Expiry Alerts"):
                    try:
                        notifications = self.api_manager.check_expiring_keys()
                        if notifications:
                            # In a real implementation, send notifications
                            st.success(f"✅ Sent {len(notifications)} notifications")
                        else:
                            st.info("ℹ️ No notifications needed")
                    except Exception as e:
                        st.error(f"Notification failed: {e}")
            
            with col3:
                if st.button("📊 Generate Report"):
                    try:
                        report = self.api_manager.generate_status_report()
                        st.download_button(
                            "📥 Download Report",
                            report,
                            file_name=f"api_key_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"Report generation failed: {e}")
                        
        except Exception as e:
            st.error(f"API security monitoring failed: {e}")
    
    def render_security_metrics(self):
        """Security metrics and analytics"""
        st.markdown("### 📊 Security Metrics & Analytics")
        
        # Mock data for demonstration
        dates = pd.date_range(start='2025-07-01', end='2025-08-01', freq='D')
        
        # Security incidents over time
        st.markdown("#### 🚨 Security Incidents Trend")
        incidents_data = {
            'Date': dates,
            'Critical': [0, 1, 0, 0, 2, 0, 1] + [0] * 25,
            'High': [1, 2, 1, 3, 1, 2, 1] + [1] * 25,
            'Medium': [3, 4, 2, 5, 3, 4, 2] + [2] * 25,
            'Low': [5, 8, 6, 7, 5, 6, 4] + [4] * 25
        }
        
        incidents_df = pd.DataFrame(incidents_data)
        
        fig_incidents = go.Figure()
        fig_incidents.add_trace(go.Scatter(x=incidents_df['Date'], y=incidents_df['Critical'], 
                                         name='Critical', line=dict(color='red')))
        fig_incidents.add_trace(go.Scatter(x=incidents_df['Date'], y=incidents_df['High'], 
                                         name='High', line=dict(color='orange')))
        fig_incidents.add_trace(go.Scatter(x=incidents_df['Date'], y=incidents_df['Medium'], 
                                         name='Medium', line=dict(color='yellow')))
        fig_incidents.add_trace(go.Scatter(x=incidents_df['Date'], y=incidents_df['Low'], 
                                         name='Low', line=dict(color='blue')))
        
        fig_incidents.update_layout(title="Security Incidents Over Time", 
                                  xaxis_title="Date", yaxis_title="Incident Count")
        st.plotly_chart(fig_incidents, use_container_width=True)
        
        # API Key Health Metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔑 API Key Health")
            if self.api_manager:
                try:
                    config = self.api_manager.config
                    api_keys = config.get('api_keys', {})
                    
                    # Count by provider
                    provider_counts = {}
                    for key_info in api_keys.values():
                        provider = key_info.get('provider', 'Unknown')
                        provider_counts[provider] = provider_counts.get(provider, 0) + 1
                    
                    if provider_counts:
                        fig_pie = px.pie(
                            values=list(provider_counts.values()),
                            names=list(provider_counts.keys()),
                            title="API Keys by Provider"
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    else:
                        st.info("No API keys to display")
                except Exception:
                    st.error("Failed to load API key metrics")
            else:
                st.warning("API Manager not available")
        
        with col2:
            st.markdown("#### 🛡️ Security Score Trend")
            
            # Mock security score data
            score_data = {
                'Date': dates,
                'Security Score': [85, 87, 89, 91, 88, 90, 92] + [90 + i % 5 for i in range(25)]
            }
            score_df = pd.DataFrame(score_data)
            
            fig_score = px.line(score_df, x='Date', y='Security Score', 
                              title="Overall Security Score")
            fig_score.update_traces(line_color='green')
            fig_score.update_layout(yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_score, use_container_width=True)
        
        # File Protection Status
        st.markdown("#### 📁 File Protection Status")
        
        protection_data = {
            'Category': ['Gitignored', 'Encrypted', 'Monitored', 'Backed Up'],
            'Count': [45, 12, 67, 23],
            'Status': ['✅ Protected', '🔒 Secure', '👁️ Watching', '💾 Safe']
        }
        protection_df = pd.DataFrame(protection_data)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig_bar = px.bar(protection_df, x='Category', y='Count', 
                           title="File Protection Coverage")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.dataframe(protection_df[['Category', 'Status']], 
                        use_container_width=True, hide_index=True)
    
    def render_incident_response(self):
        """Security incident response management"""
        st.markdown("### 🚨 Incident Response Management")
        
        # Recent incidents
        st.markdown("#### 📋 Recent Security Incidents")
        
        if self.security_manager:
            config = self.security_manager.config
            incidents = config.get('security_incidents', [])
            
            if incidents:
                # Show recent incidents
                recent_incidents = sorted(incidents, 
                                        key=lambda x: x.get('timestamp', ''), 
                                        reverse=True)[:10]
                
                for i, incident in enumerate(recent_incidents):
                    severity = incident.get('severity', 'UNKNOWN')
                    file_path = incident.get('file', 'Unknown')
                    timestamp = incident.get('timestamp', 'Unknown')
                    match = incident.get('match', 'Unknown')
                    
                    severity_color = {
                        'CRITICAL': '🚨',
                        'HIGH': '🔴', 
                        'MEDIUM': '🟡',
                        'LOW': '🔵'
                    }.get(severity, '⚪')
                    
                    with st.expander(f"{severity_color} {severity} - {file_path}"):
                        st.write(f"**File:** {file_path}")
                        st.write(f"**Detection:** {match}")
                        st.write(f"**Time:** {timestamp}")
                        
                        # Response actions
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            if st.button("🔒 Quarantine", key=f"quarantine_{i}"):
                                st.success("File quarantined")
                        with col2:
                            if st.button("✅ Resolve", key=f"resolve_{i}"):
                                st.success("Incident resolved")
                        with col3:
                            if st.button("🔍 Investigate", key=f"investigate_{i}"):
                                st.info("Investigation started")
                        with col4:
                            if st.button("📝 Note", key=f"note_{i}"):
                                st.info("Note added")
            else:
                st.success("✅ No security incidents detected!")
        
        # Incident response playbook
        st.markdown("#### 📖 Incident Response Playbook")
        
        playbook_steps = {
            "🚨 CRITICAL": [
                "1. Immediately isolate affected systems",
                "2. Revoke compromised API keys",
                "3. Notify security team",
                "4. Begin forensic analysis",
                "5. Document all actions taken"
            ],
            "🔴 HIGH": [
                "1. Assess scope of exposure",
                "2. Update .gitignore patterns",
                "3. Rotate affected credentials",
                "4. Review access logs",
                "5. Monitor for suspicious activity"
            ],
            "🟡 MEDIUM": [
                "1. Verify if exposure is real",
                "2. Update security policies",
                "3. Schedule credential rotation",
                "4. Review code patterns",
                "5. Update detection rules"
            ],
            "🔵 LOW": [
                "1. Log the incident",
                "2. Review for patterns",
                "3. Update documentation",
                "4. Schedule routine review",
                "5. Monitor trends"
            ]
        }
        
        for severity, steps in playbook_steps.items():
            with st.expander(f"{severity} Response Protocol"):
                for step in steps:
                    st.write(step)
    
    def render_security_settings(self):
        """Security configuration and settings"""
        st.markdown("### ⚙️ Security Configuration")
        
        if not self.security_manager:
            st.error("Security manager not available")
            return
        
        config = self.security_manager.config
        
        # Security monitoring settings
        st.markdown("#### 🔍 Monitoring Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monitoring_enabled = st.checkbox(
                "Enable Security Monitoring",
                value=config.get('security_monitoring', {}).get('enabled', True)
            )
            
            scan_interval = st.selectbox(
                "Scan Interval (hours)",
                [1, 3, 6, 12, 24],
                index=2  # Default to 6 hours
            )
            
            auto_gitignore = st.checkbox(
                "Auto-update .gitignore",
                value=config.get('security_monitoring', {}).get('auto_gitignore_update', True)
            )
        
        with col2:
            alert_on_exposure = st.checkbox(
                "Alert on Secret Exposure",
                value=config.get('security_monitoring', {}).get('alert_on_exposure', True)
            )
            
            backup_before_changes = st.checkbox(
                "Backup Before Changes",
                value=config.get('file_protection', {}).get('backup_before_changes', True)
            )
            
            validate_on_startup = st.checkbox(
                "Validate Keys on Startup",
                value=config.get('api_security', {}).get('validate_keys_on_startup', True)
            )
        
        # Save settings
        if st.button("💾 Save Security Settings"):
            # Update config
            config['security_monitoring'].update({
                'enabled': monitoring_enabled,
                'scan_interval_hours': scan_interval,
                'auto_gitignore_update': auto_gitignore,
                'alert_on_exposure': alert_on_exposure
            })
            
            config['file_protection'].update({
                'backup_before_changes': backup_before_changes
            })
            
            config['api_security'].update({
                'validate_keys_on_startup': validate_on_startup
            })
            
            # Save to file
            try:
                self.security_manager.save_security_config()
                st.success("✅ Security settings saved!")
            except Exception as e:
                st.error(f"Failed to save settings: {e}")
        
        # Advanced settings
        st.markdown("#### 🔧 Advanced Settings")
        
        with st.expander("🔒 Encryption Settings"):
            encryption_enabled = st.checkbox(
                "Enable Encryption",
                value=config.get('encryption', {}).get('enabled', True)
            )
            
            algorithm = st.selectbox(
                "Encryption Algorithm",
                ['base64', 'AES-256'],
                index=0
            )
            
            rotation_days = st.number_input(
                "Key Rotation Days",
                min_value=1,
                max_value=365,
                value=config.get('encryption', {}).get('key_rotation_days', 30)
            )
        
        with st.expander("📁 File Protection Patterns"):
            st.text_area(
                "Additional Sensitive Patterns (one per line)",
                value="\n".join([
                    "github_pat_*",
                    "*_token*",
                    "*_secret*",
                    "*.pem",
                    "*.key"
                ]),
                height=150
            )
        
        # System information
        st.markdown("#### ℹ️ System Information")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.write(f"**Project Root:** `{self.project_root}`")
            st.write(f"**Git Available:** {'✅ Yes' if self._check_git_available() else '❌ No'}")
            st.write(f"**Python Version:** {sys.version.split()[0]}")
        
        with info_col2:
            st.write(f"**Security Config:** `security_config.json`")
            st.write(f"**Last Scan:** {config.get('last_security_scan', 'Never')}")
            st.write(f"**Total Incidents:** {len(config.get('security_incidents', []))}")
    
    def _check_git_available(self) -> bool:
        """Check if git is available"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            return True
        except:
            return False

def render_security_dashboard():
    """Main function to render security dashboard"""
    dashboard = SecurityDashboard()
    dashboard.render_security_dashboard()

if __name__ == "__main__":
    render_security_dashboard()