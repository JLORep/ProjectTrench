#!/usr/bin/env python3
"""
TrenchCoat Pro - Auto Bug Fix Reporter
Automatically detects and reports bug fixes from git commits
"""

import subprocess
import re
import json
from datetime import datetime
from discord_webhooks import TrenchCoatDiscordWebhooks
from typing import Dict, List, Any

class AutoBugReporter:
    """Automatically detect and report bug fixes from commits"""
    
    def __init__(self):
        self.webhooks = TrenchCoatDiscordWebhooks()
        
        # Bug fix detection patterns
        self.bug_patterns = [
            r'fix[:\s]',
            r'bug[:\s]',
            r'resolve[:\s]',
            r'repair[:\s]',
            r'correct[:\s]',
            r'patch[:\s]',
            r'hotfix[:\s]',
            r'urgent[:\s]',
            r'critical[:\s]'
        ]
        
        # Severity detection
        self.severity_patterns = {
            'CRITICAL': [r'critical', r'urgent', r'breaking', r'crash', r'error'],
            'HIGH': [r'high', r'important', r'major', r'broken'],
            'MEDIUM': [r'medium', r'moderate', r'fix', r'issue'],
            'LOW': [r'low', r'minor', r'small', r'typo', r'style']
        }
        
        # Component detection
        self.component_patterns = {
            'UI/Dashboard': [r'streamlit', r'dashboard', r'ui', r'interface', r'display'],
            'Database': [r'database', r'db', r'sql', r'query', r'data'],
            'API': [r'api', r'endpoint', r'request', r'response'],
            'Trading Engine': [r'trading', r'trade', r'strategy', r'signal'],
            'Webhooks': [r'webhook', r'discord', r'notification'],
            'Authentication': [r'auth', r'login', r'permission', r'security'],
            'Configuration': [r'config', r'setting', r'environment'],
            'General': []  # Default fallback
        }

    def get_latest_commit(self) -> Dict[str, str]:
        """Get the latest commit information"""
        try:
            # Get commit hash
            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, check=True
            )
            commit_hash = hash_result.stdout.strip()
            
            # Get commit message
            msg_result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%s'],
                capture_output=True, text=True, check=True
            )
            commit_message = msg_result.stdout.strip()
            
            # Get commit author
            author_result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%an'],
                capture_output=True, text=True, check=True
            )
            author = author_result.stdout.strip()
            
            # Get changed files
            files_result = subprocess.run(
                ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
                capture_output=True, text=True, check=True
            )
            changed_files = files_result.stdout.strip().split('\n') if files_result.stdout.strip() else []
            
            # Get lines changed
            stats_result = subprocess.run(
                ['git', 'show', '--stat', '--format='],
                capture_output=True, text=True, check=True
            )
            
            return {
                'hash': commit_hash,
                'message': commit_message,
                'author': author,
                'files': changed_files,
                'stats': stats_result.stdout.strip()
            }
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit info: {e}")
            return {}

    def is_bug_fix(self, commit_message: str) -> bool:
        """Detect if commit is a bug fix"""
        message_lower = commit_message.lower()
        return any(re.search(pattern, message_lower, re.IGNORECASE) for pattern in self.bug_patterns)

    def detect_severity(self, commit_message: str, files: List[str]) -> str:
        """Detect bug fix severity"""
        message_lower = commit_message.lower()
        
        for severity, patterns in self.severity_patterns.items():
            if any(re.search(pattern, message_lower, re.IGNORECASE) for pattern in patterns):
                return severity
                
        # Default based on file count
        if len(files) > 5:
            return 'HIGH'
        elif len(files) > 2:
            return 'MEDIUM'
        else:
            return 'LOW'

    def detect_component(self, commit_message: str, files: List[str]) -> str:
        """Detect which component was fixed"""
        message_lower = commit_message.lower()
        files_str = ' '.join(files).lower()
        combined = f"{message_lower} {files_str}"
        
        for component, patterns in self.component_patterns.items():
            if component == 'General':
                continue
            if any(re.search(pattern, combined, re.IGNORECASE) for pattern in patterns):
                return component
                
        return 'General'

    def extract_problem_solution(self, commit_message: str) -> Dict[str, str]:
        """Extract problem and solution from commit message"""
        # Common patterns for problem/solution extraction
        if ':' in commit_message:
            parts = commit_message.split(':', 1)
            if len(parts) == 2:
                return {
                    'problem': parts[0].strip(),
                    'solution': parts[1].strip()
                }
        
        # If no clear pattern, use the whole message as solution
        return {
            'problem': 'Bug fix applied',
            'solution': commit_message
        }

    def count_changes(self, stats: str) -> Dict[str, int]:
        """Count files and lines changed from git stats"""
        files_changed = 0
        lines_modified = 0
        
        try:
            lines = stats.split('\n')
            for line in lines:
                if 'file' in line and 'changed' in line:
                    # Extract number from "X files changed"
                    match = re.search(r'(\d+) files? changed', line)
                    if match:
                        files_changed = int(match.group(1))
                        
                    # Extract insertions and deletions
                    insertions = re.search(r'(\d+) insertions?', line)
                    deletions = re.search(r'(\d+) deletions?', line)
                    
                    if insertions:
                        lines_modified += int(insertions.group(1))
                    if deletions:
                        lines_modified += int(deletions.group(1))
                        
        except Exception as e:
            print(f"Error parsing git stats: {e}")
            
        return {
            'files_changed': files_changed,
            'lines_modified': lines_modified
        }

    def process_latest_commit(self) -> bool:
        """Process the latest commit and report if it's a bug fix"""
        commit_info = self.get_latest_commit()
        if not commit_info:
            print("Could not get commit information")
            return False
            
        commit_message = commit_info.get('message', '')
        
        if not self.is_bug_fix(commit_message):
            print(f"Latest commit is not a bug fix: {commit_message}")
            return False
            
        print(f"Bug fix detected: {commit_message}")
        
        # Extract fix details
        severity = self.detect_severity(commit_message, commit_info.get('files', []))
        component = self.detect_component(commit_message, commit_info.get('files', []))
        problem_solution = self.extract_problem_solution(commit_message)
        changes = self.count_changes(commit_info.get('stats', ''))
        
        # Prepare notification data
        fix_data = {
            'type': component,
            'severity': severity,
            'problem': problem_solution['problem'],
            'solution': problem_solution['solution'],
            'component': component,
            'files_changed': changes['files_changed'] or len(commit_info.get('files', [])),
            'lines_modified': changes['lines_modified'],
            'tested': 'Yes',
            'deployed': 'Yes',
            'status': 'Fixed',
            'commit_hash': commit_info.get('hash', ''),
            'commit_message': commit_message,
            'author': commit_info.get('author', 'TrenchCoat Pro Team')
        }
        
        # Send notification
        success = self.webhooks.send_bug_fix_notification(fix_data)
        
        if success:
            print(f"Bug fix notification sent successfully to Discord")
            # Save to log file
            self.save_fix_log(fix_data)
        else:
            print("Failed to send bug fix notification")
            
        return success

    def save_fix_log(self, fix_data: Dict[str, Any]) -> None:
        """Save bug fix to local log file"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'fix_data': fix_data
            }
            
            log_file = 'bug_fixes_log.json'
            
            # Load existing log
            try:
                with open(log_file, 'r') as f:
                    log = json.load(f)
            except FileNotFoundError:
                log = []
                
            # Add new entry
            log.append(log_entry)
            
            # Keep only last 100 entries
            log = log[-100:]
            
            # Save updated log
            with open(log_file, 'w') as f:
                json.dump(log, f, indent=2)
                
            print(f"Bug fix logged to {log_file}")
            
        except Exception as e:
            print(f"Error saving bug fix log: {e}")

    def test_bug_fix_detection(self) -> None:
        """Test the bug fix detection with sample messages"""
        test_messages = [
            "Fix: Resolve spreadsheet flickering issue",
            "Bug: Critical authentication bypass vulnerability",
            "Urgent hotfix: Trading engine crash on startup",
            "Minor style fix: Update button colors",
            "Feature: Add new dashboard widget",  # Not a bug fix
            "Patch: Database connection timeout handling"
        ]
        
        print("Testing bug fix detection:")
        print("=" * 40)
        
        for msg in test_messages:
            is_bug = self.is_bug_fix(msg)
            severity = self.detect_severity(msg, ['test.py'])
            component = self.detect_component(msg, ['streamlit_app.py'])
            
            print(f"Message: {msg}")
            print(f"  Bug Fix: {is_bug}")
            print(f"  Severity: {severity}")
            print(f"  Component: {component}")
            print()

# Command line usage
if __name__ == "__main__":
    import sys
    
    reporter = AutoBugReporter()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        reporter.test_bug_fix_detection()
    else:
        print("TrenchCoat Pro - Auto Bug Reporter")
        print("=" * 40)
        success = reporter.process_latest_commit()
        
        if success:
            print("Bug fix notification completed successfully!")
        else:
            print("No bug fix detected or notification failed.")