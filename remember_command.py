#!/usr/bin/env python3
"""
/remember - Custom Claude Code slash command for crash recovery context
Scans all documentation, recent commits, and console output to resume work exactly where we left off.
"""

import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import glob
import argparse

def get_git_recent_commits(count=10):
    """Get recent git commits with details"""
    try:
        # Get commit history
        result = subprocess.run([
            'git', 'log', f'--oneline', f'-{count}', '--decorate'
        ], capture_output=True, text=True, cwd='.')
        
        commits = []
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    commits.append(line)
        
        # Get current status
        status_result = subprocess.run([
            'git', 'status', '--porcelain'
        ], capture_output=True, text=True, cwd='.')
        
        # Get current branch
        branch_result = subprocess.run([
            'git', 'branch', '--show-current'
        ], capture_output=True, text=True, cwd='.')
        
        return {
            'commits': commits,
            'status': status_result.stdout.strip() if status_result.returncode == 0 else "Unknown",
            'branch': branch_result.stdout.strip() if branch_result.returncode == 0 else "Unknown",
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': f"Git analysis failed: {e}"}

def scan_documentation_files():
    """Scan all MD files for recent context"""
    md_files = []
    
    # Get all markdown files
    for pattern in ['*.md', '**/*.md']:
        for file_path in glob.glob(pattern, recursive=True):
            try:
                stat = os.stat(file_path)
                md_files.append({
                    'path': file_path,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'priority': get_file_priority(file_path)
                })
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
    
    # Sort by priority and modification time
    md_files.sort(key=lambda x: (x['priority'], x['modified']), reverse=True)
    
    return md_files

def get_file_priority(file_path):
    """Determine file priority for context recovery"""
    file_name = os.path.basename(file_path).lower()
    
    # Critical files get highest priority
    critical_files = [
        'claude.md', 'claude_quick_context.md', 'claude_optimized.md',
        'gotchas_and_lessons_learned.md', 'session_summary', 'deployment_status.md'
    ]
    
    for critical in critical_files:
        if critical in file_name:
            return 10
    
    # Recent session files
    if 'session' in file_name or '2025-08-02' in file_name:
        return 8
    
    # Bug fixes and issues
    if any(word in file_name for word in ['fix', 'bug', 'error', 'issue', 'gotcha']):
        return 7
    
    # Architecture and guides
    if any(word in file_name for word in ['architecture', 'guide', 'protocol']):
        return 6
    
    # Deployment related
    if any(word in file_name for word in ['deploy', 'production']):
        return 5
    
    # Regular documentation
    return 3

def get_recent_logs():
    """Get recent console output and logs"""
    log_files = []
    
    # Common log file patterns
    log_patterns = [
        '*.log', '*.out', '*.err', 
        'deployment*.json', 'validation*.json',
        'complete_async_deploy.log'
    ]
    
    for pattern in log_patterns:
        for log_file in glob.glob(pattern):
            try:
                stat = os.stat(log_file)
                # Only include recent logs (last 24 hours)
                if datetime.fromtimestamp(stat.st_mtime) > datetime.now() - timedelta(hours=24):
                    log_files.append({
                        'path': log_file,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            except Exception as e:
                print(f"Error scanning log {log_file}: {e}")
    
    return sorted(log_files, key=lambda x: x['modified'], reverse=True)

def get_database_status():
    """Get current database status"""
    try:
        if os.path.exists('data/trench.db'):
            conn = sqlite3.connect('data/trench.db')
            cursor = conn.cursor()
            
            # Get coin count
            cursor.execute("SELECT COUNT(*) FROM coins")
            coin_count = cursor.fetchone()[0]
            
            # Get database size
            db_size = os.path.getsize('data/trench.db')
            
            conn.close()
            
            return {
                'coin_count': coin_count,
                'db_size_kb': db_size // 1024,
                'exists': True
            }
    except Exception as e:
        return {'error': f"Database check failed: {e}", 'exists': False}

def get_system_status():
    """Get current system and environment status"""
    return {
        'working_directory': os.getcwd(),
        'python_version': sys.version,
        'timestamp': datetime.now().isoformat(),
        'platform': sys.platform,
        'environment_vars': {
            'PYTHONPATH': os.environ.get('PYTHONPATH', 'Not set'),
            'PATH': os.environ.get('PATH', '')[:200] + '...' if len(os.environ.get('PATH', '')) > 200 else os.environ.get('PATH', '')
        }
    }

def analyze_recent_activity():
    """Analyze recent activity patterns"""
    analysis = {
        'git_activity': get_git_recent_commits(),
        'documentation': scan_documentation_files()[:10],  # Top 10 most relevant
        'recent_logs': get_recent_logs()[:5],  # Last 5 log files
        'database_status': get_database_status(),
        'system_status': get_system_status()
    }
    
    return analysis

def generate_context_summary(analysis):
    """Generate human-readable context summary"""
    summary = []
    
    summary.append("🔄 **CRASH RECOVERY CONTEXT**")
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")
    
    # Git status
    git_info = analysis['git_activity']
    if 'error' not in git_info:
        summary.append(f"🌿 **Current Branch**: {git_info['branch']}")
        summary.append(f"📊 **Git Status**: {'Clean' if not git_info['status'] else 'Modified files detected'}")
        summary.append("")
        summary.append("📝 **Recent Commits**:")
        for commit in git_info['commits'][:5]:
            summary.append(f"  • {commit}")
        summary.append("")
    
    # Database status
    db_info = analysis['database_status']
    if db_info.get('exists'):
        summary.append(f"🗄️ **Database**: {db_info.get('coin_count', 'Unknown')} coins ({db_info.get('db_size_kb', 'Unknown')}KB)")
    else:
        summary.append("🗄️ **Database**: ❌ Missing or inaccessible")
    summary.append("")
    
    # Key documentation files
    summary.append("📚 **Key Documentation** (most relevant):")
    for doc in analysis['documentation'][:5]:
        modified = datetime.fromisoformat(doc['modified']).strftime('%m-%d %H:%M')
        summary.append(f"  • {doc['path']} (modified: {modified})")
    summary.append("")
    
    # Recent logs
    if analysis['recent_logs']:
        summary.append("📋 **Recent Logs**:")
        for log in analysis['recent_logs'][:3]:
            modified = datetime.fromisoformat(log['modified']).strftime('%m-%d %H:%M')
            summary.append(f"  • {log['path']} (modified: {modified})")
        summary.append("")
    
    # System info
    sys_info = analysis['system_status']
    summary.append(f"💻 **Environment**: {sys_info['working_directory']}")
    summary.append(f"🐍 **Python**: {sys_info['python_version'].split()[0]}")
    
    return "\n".join(summary)

def main():
    """Main function for /remember command"""
    parser = argparse.ArgumentParser(description='Generate crash recovery context')
    parser.add_argument('--json', action='store_true', help='Output raw JSON data')
    parser.add_argument('--save', help='Save analysis to file')
    
    args = parser.parse_args()
    
    print("🔍 Analyzing system state for crash recovery...")
    
    analysis = analyze_recent_activity()
    
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        summary = generate_context_summary(analysis)
        print(summary)
    
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            if args.json:
                json.dump(analysis, f, indent=2)
            else:
                f.write(summary)
        print(f"\n💾 Context saved to: {args.save}")

if __name__ == "__main__":
    main()