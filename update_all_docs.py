#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Documentation Updater
Updates all relevant MD files with new developments, fixes, and changes

Usage:
    python update_all_docs.py "Session Title" "Description of changes"
    
Or as a slash command function:
    /update-docs "Safe File Editor Implementation" "Created error prevention system"
"""

import os
import sys
import json
import requests
from datetime import datetime
from safe_file_editor import SafeEditor

# Fix console encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def safe_print(text):
    """Print text safely, handling Unicode issues"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: replace problematic Unicode with ASCII equivalents
        text = text.replace('✅', '[OK]').replace('❌', '[ERROR]').replace('⚠️', '[WARN]')
        text = text.replace('🎯', '*').replace('🔧', '[TOOL]').replace('📊', '[DATA]')
        print(text)

class DocumentationUpdater:
    """Automated system to update all project documentation"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.files_updated = []
        self.errors = []
        self.discord_webhooks = self.load_discord_webhooks()
        
        # Define ALL documentation files to update (comprehensive list)
        self.doc_files = {
            # Core project documentation
            'CLAUDE.md': 'session_history',
            'README.md': 'project_overview',
            'MISSION_STATEMENT.md': 'project_mission',
            
            # Technical documentation
            'logic.md': 'architecture_changes',
            'structure.md': 'file_additions', 
            'dashboard.md': 'dashboard_features',
            'deploy.md': 'deployment_improvements',
            
            # Process documentation
            'todo.md': 'task_tracking',
            'SAFE_EDITOR_GUIDE.md': 'tool_documentation',
            
            # Setup and configuration guides
            'AI_INTEGRATION_GUIDE.md': 'ai_features',
            'AUTO_DEPLOY_SETUP_COMPLETE.md': 'deployment_setup',
            'BUG_FIX_SYSTEM_GUIDE.md': 'debugging_tools',
            'CREDENTIALS.md': 'auth_security',
            'DASHBOARD_FIXES_SUMMARY.md': 'ui_improvements',
            'DEPLOYMENT_STATUS.md': 'deployment_tracking',
            'DNS_CONFIGURATION_GUIDE.md': 'network_config',
            'DOMAIN_SETUP_COMPLETE.md': 'domain_management',
            'ENRICHMENT_README.md': 'data_processing',
            'GITHUB_TOKEN_GUIDE.md': 'github_integration',
            'GITHUB_UPLOAD_GUIDE.md': 'version_control',
            'NEXT_STEPS_ROADMAP.md': 'future_planning',
            'PROGRESS_LOG.md': 'development_tracking',
            'QUICK_SETUP_GUIDE.md': 'installation',
            'REMOTE_ACCESS_GUIDE.md': 'remote_setup',
            'SESSION_SUMMARY_2025_07_31.md': 'historical_sessions',
            'SHARE_INSTRUCTIONS.md': 'collaboration',
            'STREAMLIT_DEPLOY_FINAL.md': 'streamlit_deployment',
            'STREAMLIT_DEPLOY_FIX.md': 'deployment_fixes',
            'ULTIMATE_STRATEGY.md': 'strategic_planning',
            'WEBHOOK_SETUP_GUIDE.md': 'webhook_integration',
            'WORKFLOW_INTEGRATION.md': 'process_integration',
            
            # Platform-specific documentation
            'azure_deployment_guide.md': 'azure_cloud',
            'discord_integration_guide.md': 'discord_features',
            'email_setup_guide.md': 'email_notifications',
            'fresh_streamlit_deploy.md': 'streamlit_fresh_setup',
            'github_setup_guide.md': 'github_configuration',
            'marketing_screenshots_guide.md': 'marketing_materials',
            'notification_setup_guide.md': 'notification_systems',
            'signal_sharing_guide.md': 'signal_management',
            'solana_trading_setup.md': 'solana_integration',
            'streamlit_deployment_fix.md': 'streamlit_troubleshooting',
            'streamlit_deployment_fix_guide.md': 'streamlit_debugging',
            'subdomain_architecture.md': 'network_architecture',
            'telegram_setup_guide.md': 'telegram_integration',
            'whatsapp_setup_guide.md': 'whatsapp_integration'
        }
    
    def load_discord_webhooks(self) -> dict:
        """Load Discord webhook URLs from configuration"""
        try:
            # Try to load from webhook_config.json
            if os.path.exists('webhook_config.json'):
                with open('webhook_config.json', 'r') as f:
                    config = json.load(f)
                    return config.get('discord_webhooks', {})
            
            # Default webhook channels (you can customize these)
            return {
                'development': None,  # Set to actual webhook URL
                'documentation': None,  # Set to actual webhook URL  
                'general': None,  # Set to actual webhook URL
                'alerts': None   # Set to actual webhook URL
            }
        except Exception as e:
            safe_print(f"[WARNING] Could not load Discord webhooks: {e}")
            return {}
    
    def send_discord_notification(self, webhook_url: str, title: str, description: str, color: int = 0x00ff00) -> bool:
        """Send notification to Discord webhook"""
        if not webhook_url:
            return False
            
        try:
            # Create Discord embed
            embed = {
                "title": f"📝 Documentation Update: {title}",
                "description": description,
                "color": color,
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {
                        "name": "📊 Files Updated",
                        "value": f"{len(self.files_updated)} files successfully updated",
                        "inline": True
                    },
                    {
                        "name": "⚠️ Errors",
                        "value": f"{len(self.errors)} errors encountered" if self.errors else "No errors",
                        "inline": True
                    },
                    {
                        "name": "🕐 Timestamp",
                        "value": self.timestamp,
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "TrenchCoat Pro - Automated Documentation System"
                }
            }
            
            # Add updated files list if not too long
            if self.files_updated and len(self.files_updated) <= 10:
                embed["fields"].append({
                    "name": "📁 Updated Files",
                    "value": "• " + "\n• ".join(self.files_updated[:10]),
                    "inline": False
                })
            
            payload = {
                "embeds": [embed],
                "username": "Documentation Bot",
                "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            safe_print(f"[ERROR] Discord notification failed: {e}")
            return False
    
    def notify_discord_channels(self, session_title: str, description: str) -> dict:
        """Send notifications to relevant Discord channels"""
        notifications = {}
        
        # Determine which channels to notify based on content
        channels_to_notify = []
        
        # Always notify development channel
        if 'development' in self.discord_webhooks:
            channels_to_notify.append('development')
        
        # Notify documentation channel for doc updates
        if 'documentation' in self.discord_webhooks:
            channels_to_notify.append('documentation')
        
        # Notify alerts channel if there were errors
        if self.errors and 'alerts' in self.discord_webhooks:
            channels_to_notify.append('alerts')
        
        # Send notifications
        for channel in channels_to_notify:
            webhook_url = self.discord_webhooks.get(channel)
            if webhook_url:
                # Customize message based on channel
                if channel == 'alerts' and self.errors:
                    color = 0xff0000  # Red for errors
                    custom_description = f"{description}\n\n⚠️ **Errors encountered during update**"
                else:
                    color = 0x00ff00  # Green for success
                    custom_description = description
                
                success = self.send_discord_notification(
                    webhook_url, 
                    session_title, 
                    custom_description, 
                    color
                )
                notifications[channel] = success
                
                if success:
                    safe_print(f"[OK] Discord notification sent to #{channel}")
                else:
                    safe_print(f"[ERROR] Failed to send Discord notification to #{channel}")
        
        return notifications
    
    def update_claude_md(self, session_title: str, description: str) -> bool:
        """Update CLAUDE.md with new session information"""
        editor = SafeEditor("CLAUDE.md")
        
        content = f"""### 🎯 {session_title.upper()} ✅
**Implementation**: {description}
**Timestamp**: {self.timestamp}

### Technical Details:
- **Safe File Editor**: Created comprehensive error prevention system
- **Unicode Handling**: Extensive emoji whitelist for project compatibility  
- **Error Prevention**: Eliminates "string not found" and "file not read" errors
- **Credit Saving**: Prevents expensive retry loops and failed operations
- **Automated Updates**: Script-based documentation management system

### Key Benefits:
- ✅ **No More Credit Waste**: Prevents common editing errors
- ✅ **Unicode Safe**: Handles all project emojis and special characters
- ✅ **Backup System**: Auto-backup before changes
- ✅ **Smart Fallbacks**: Alternative approaches when operations fail
- ✅ **Diagnostic Tools**: File analysis and similar string detection

### Files Created:
- `safe_file_editor.py` - Main error prevention system
- `update_all_docs.py` - Automated documentation updater
- `SAFE_EDITOR_GUIDE.md` - Comprehensive usage guide
- `test_error_prevention.py` - Testing and demonstration scripts"""
        
        return editor.smart_claude_md_update(f"Session {self.timestamp.split()[0]} - {session_title}", content)
    
    def update_todo_md(self, session_title: str, description: str) -> bool:
        """Update todo.md with completed tasks"""
        editor = SafeEditor("todo.md")
        
        # Read current content to get next task number
        if editor.read_file():
            lines = editor.content.split('\n')
            task_numbers = [int(line.split('.')[0]) for line in lines if line.strip() and line[0].isdigit()]
            next_task = max(task_numbers) + 1 if task_numbers else 12
        else:
            next_task = 12
            
        new_task = f"""
{next_task}. ✅ **{session_title}**
   - Status: Completed
   - Description: {description}
   - Files Created: safe_file_editor.py, update_all_docs.py, SAFE_EDITOR_GUIDE.md
   - Impact: Prevents credit-wasting file editing errors
   - Timestamp: {self.timestamp}"""
        
        # Update completion stats
        old_stats = f"**Overall Completion**: 100% ({next_task-1}/{next_task-1} tasks completed)"
        new_stats = f"**Overall Completion**: 100% ({next_task}/{next_task} tasks completed)"
        
        success1 = editor.safe_replace(old_stats, new_stats, confirm_exists=True)
        success2 = editor.safe_replace(f"- Total Tasks: {next_task-1}", f"- Total Tasks: {next_task}", confirm_exists=True)
        success3 = editor.safe_replace(f"- Completed Tasks: {next_task-1}", f"- Completed Tasks: {next_task}", confirm_exists=True)
        
        if not success1:
            # Fallback: append new task
            return editor.append_to_end(new_task)
        
        return success1 and success2 and success3
    
    def update_dashboard_md(self, session_title: str, description: str) -> bool:
        """Update dashboard.md with new features"""
        editor = SafeEditor("dashboard.md")
        
        new_section = f"""
### 🔧 Safe File Editor Integration - {self.timestamp}
- **Feature**: {description}
- **Impact**: Prevents credit-wasting errors in documentation updates
- **Location**: `safe_file_editor.py` with comprehensive Unicode handling
- **Benefits**: Automated MD file updates, error prevention, smart fallbacks"""
        
        # Try to add to recent updates section
        if not editor.safe_replace("### 🔄 Recent Updates", f"### 🔄 Recent Updates{new_section}", confirm_exists=True):
            return editor.append_to_end(f"## Recent Updates{new_section}")
        
        return True
    
    def update_deploy_md(self, session_title: str, description: str) -> bool:
        """Update deploy.md with deployment improvements"""
        editor = SafeEditor("deploy.md")
        
        new_gotcha = f"""
#### 11. **Documentation Update Errors**
- **Risk Level**: 🟡 MEDIUM
- **Issue**: "String to replace not found" and "File has not been read yet" errors
- **Symptom**: Credits wasted on failed documentation updates
- **Detection**: Repeated error messages during MD file editing
- **Solution**: Use SafeEditor class with error prevention and smart fallbacks  
- **Prevention**: Implement `update_all_docs.py` for automated documentation management
- **Added**: {self.timestamp}"""
        
        return editor.safe_replace("### Configuration Gotchas", f"### Configuration Gotchas{new_gotcha}", confirm_exists=True) or \
               editor.append_to_end(f"## Documentation Gotchas{new_gotcha}")
    
    def update_logic_md(self, session_title: str, description: str) -> bool:
        """Update logic.md with architecture changes"""
        editor = SafeEditor("logic.md")
        
        new_module = f"""
### safe_file_editor.py - Error Prevention System
- **Location:** `C:\\trench\\safe_file_editor.py:1-400+`
- **Purpose:** Prevent credit-wasting file editing errors
- **Added:** {self.timestamp}

**Key Classes & Methods:**
- `SafeEditor` (main class): Comprehensive file editing with error prevention
- `fix_unicode()`: Handles extensive emoji whitelist and Unicode normalization
- `safe_replace()`: String replacement with existence confirmation
- `string_exists()`: Pre-check string existence to prevent errors
- `append_to_end()`: Always-safe content appending
- `smart_claude_md_update()`: Intelligent CLAUDE.md session updates
- `find_similar_strings()`: Alternative string discovery for failed matches

**Error Prevention Features:**
- Pre-validates string existence before replacement attempts
- Caches file content to prevent "file not read" errors
- Creates automatic backups before modifications
- Provides smart fallbacks when operations fail
- Handles Unicode normalization for deployment safety"""
        
        return editor.safe_replace("## 🔧 Configuration & Utilities", f"## 🔧 Configuration & Utilities{new_module}", confirm_exists=True) or \
               editor.append_to_end(f"## Error Prevention & Utilities{new_module}")
    
    def update_structure_md(self, session_title: str, description: str) -> bool:
        """Update structure.md with new files"""
        editor = SafeEditor("structure.md")
        
        new_files = f"""
├── safe_file_editor.py                   # 🛡️ ERROR PREVENTION SYSTEM
├── update_all_docs.py                    # 📝 AUTOMATED DOCUMENTATION UPDATER  
├── SAFE_EDITOR_GUIDE.md                  # 📖 Safe editing usage guide
├── test_error_prevention.py              # 🧪 Error prevention testing
├── demo_safe_editor.py                   # 🎯 Safe editor demonstration"""
        
        return editor.safe_replace("## SCRIPTS & UTILITIES", f"## SCRIPTS & UTILITIES{new_files}", confirm_exists=True) or \
               editor.append_to_end(f"## Error Prevention Tools{new_files}")
    
    def update_safe_editor_guide(self, session_title: str, description: str) -> bool:
        """Update the safe editor guide with new information"""
        editor = SafeEditor("SAFE_EDITOR_GUIDE.md")
        
        update_note = f"""

## Recent Updates - {self.timestamp}

### Automated Documentation System
- **Script**: `update_all_docs.py` for batch documentation updates
- **Integration**: Works with all project MD files simultaneously  
- **Usage**: `python update_all_docs.py "Title" "Description"`
- **Benefits**: Consistent documentation, error prevention, time savings

### Enhanced Unicode Support
- **Emoji Whitelist**: 100+ project-specific emojis supported
- **Safe Deployment**: Prevents encoding errors in production
- **Smart Conversion**: Problematic Unicode → ASCII equivalents
- **Preservation**: Keeps all dashboard and status emojis intact"""
        
        return editor.append_to_end(update_note)
    
    def update_generic_md(self, file_name: str, session_title: str, description: str) -> bool:
        """Generic update method for any MD file"""
        if not os.path.exists(file_name):
            safe_print(f"[SKIP] {file_name} not found")
            return False
            
        editor = SafeEditor(file_name)
        
        # Read the file to understand its structure
        if not editor.read_file():
            return False
            
        # Determine appropriate update strategy based on file content
        content_lower = editor.content.lower()
        
        update_section = f"""
## Update - {self.timestamp}
**{session_title}**: {description}

### Safe File Editor System Implementation
- **Error Prevention**: Eliminates "string not found" and "file not read" errors
- **Unicode Handling**: Comprehensive emoji support for project compatibility
- **Automated Documentation**: Batch update system for all project files
- **Credit Savings**: Prevents expensive retry loops and failed operations
- **Smart Fallbacks**: Alternative approaches when primary operations fail

*Updated via automated documentation system*"""
        
        # Try different update strategies based on file type
        if 'last updated' in content_lower:
            return editor.replace_last_updated(f"{self.timestamp} - {session_title}")
        elif '# ' in editor.content:  # Has headers
            return editor.append_to_end(update_section)
        else:
            # Simple append for files without clear structure
            return editor.append_to_end(f"\n---\n**{self.timestamp}**: {session_title} - {description}")
    
    def read_all_docs_for_context(self) -> dict:
        """Read all documentation files to understand current state"""
        context = {}
        
        safe_print("Reading documentation files for context...")
        for file_name, category in self.doc_files.items():
            if os.path.exists(file_name):
                editor = SafeEditor(file_name)
                if editor.read_file():
                    context[file_name] = {
                        'category': category,
                        'size': len(editor.content),
                        'lines': len(editor.content.split('\n')),
                        'last_modified': editor.last_read,
                        'has_timestamps': 'last updated' in editor.content.lower(),
                        'has_headers': '# ' in editor.content,
                        'editor': editor  # Keep editor for potential updates
                    }
                else:
                    context[file_name] = {'error': 'Could not read file'}
            else:
                context[file_name] = {'error': 'File not found'}
        
        return context
    
    def smart_update_all_docs(self, session_title: str, description: str) -> dict:
        """Intelligently update all documentation files based on their content and purpose"""
        
        # First, read all files to understand current state
        context = self.read_all_docs_for_context()
        
        safe_print(f"\nANALYZED {len(context)} DOCUMENTATION FILES")
        safe_print("=" * 60)
        
        results = {}
        
        # Core files get specialized updates
        specialized_updates = {
            'CLAUDE.md': self.update_claude_md,
            'todo.md': self.update_todo_md,
            'dashboard.md': self.update_dashboard_md,
            'deploy.md': self.update_deploy_md,
            'logic.md': self.update_logic_md,
            'structure.md': self.update_structure_md,
            'SAFE_EDITOR_GUIDE.md': self.update_safe_editor_guide
        }
        
        # Update each file
        for file_name, file_context in context.items():
            if 'error' in file_context:
                safe_print(f"[SKIP] {file_name}: {file_context['error']}")
                results[file_name] = False
                continue
                
            try:
                safe_print(f"Updating {file_name} ({file_context['size']:,} chars)...")
                
                # Use specialized update if available
                if file_name in specialized_updates:
                    success = specialized_updates[file_name](session_title, description)
                else:
                    # Use generic update for other files
                    success = self.update_generic_md(file_name, session_title, description)
                
                results[file_name] = success
                
                if success:
                    safe_print("[UPDATED]")
                    self.files_updated.append(file_name)
                else:
                    safe_print("[SKIPPED]")
                    
            except Exception as e:
                safe_print(f"[ERROR] {str(e).encode('ascii', 'replace').decode('ascii')}")
                self.errors.append(f"{file_name}: {str(e).encode('ascii', 'replace').decode('ascii')}")
                results[file_name] = False
        
        return results
    
    def run_full_update(self, session_title: str, description: str) -> dict:
        """Run complete documentation update across ALL files"""
        
        safe_print(f"COMPREHENSIVE DOCUMENTATION UPDATE")
        safe_print(f"Session: {session_title}")
        safe_print(f"Description: {description}")
        safe_print(f"Time: {self.timestamp}")
        safe_print("=" * 60)
        
        # Use smart update system that reads and analyzes all files
        results = self.smart_update_all_docs(session_title, description)
        
        # Summary
        safe_print("\n" + "=" * 60)
        safe_print(f"COMPREHENSIVE UPDATE SUMMARY:")
        safe_print(f"Files updated: {len(self.files_updated)}")
        safe_print(f"Files analyzed: {len(self.doc_files)}")
        safe_print(f"Errors: {len(self.errors)}")
        
        if self.files_updated:
            files_str = ', '.join([f.encode('ascii', 'replace').decode('ascii') for f in self.files_updated])
            safe_print(f"Successfully updated: {files_str}")
            
        if self.errors:
            error_str = '; '.join([e.encode('ascii', 'replace').decode('ascii') for e in self.errors])
            safe_print(f"Errors encountered: {error_str}")
        
        # Send Discord notifications
        safe_print("\n" + "-" * 40)
        safe_print("DISCORD NOTIFICATIONS:")
        discord_results = self.notify_discord_channels(session_title, description)
        
        if discord_results:
            for channel, success in discord_results.items():
                status = "SUCCESS" if success else "FAILED"
                safe_print(f"#{channel}: {status}")
        else:
            safe_print("No Discord webhooks configured")
        
        return results

def main():
    """Main function for command line usage"""
    
    if len(sys.argv) < 3:
        safe_print("Usage: python update_all_docs.py \"Session Title\" \"Description\"")
        safe_print("Example: python update_all_docs.py \"Safe File Editor\" \"Error prevention system\"")
        return
    
    session_title = sys.argv[1]
    description = sys.argv[2]
    
    updater = DocumentationUpdater()
    results = updater.run_full_update(session_title, description)
    
    return results

def slash_command_update(title: str, description: str) -> dict:
    """Function for integration with slash command system"""
    updater = DocumentationUpdater()
    return updater.run_full_update(title, description)

if __name__ == "__main__":
    main()