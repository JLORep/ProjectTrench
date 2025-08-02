#!/usr/bin/env python3
"""
TrenchCoat Pro - Retrospective Blog System
Automatically generates blog updates from git commit history
"""

import subprocess
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import sqlite3

from integrated_webhook_blog_system import IntegratedWebhookBlogSystem, DevelopmentUpdate

@dataclass
class GitCommit:
    """Represents a parsed git commit"""
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int
    
@dataclass
class CommitGroup:
    """Group of related commits forming an update"""
    commits: List[GitCommit]
    update_type: str
    title: str
    version: str
    components: List[str]
    technical_details: str
    user_impact: str
    metrics: Dict[str, Any]
    priority: str

class RetrospectiveBlogSystem(IntegratedWebhookBlogSystem):
    """Extended system that generates blog updates from git history"""
    
    def __init__(self):
        super().__init__()
        self.commit_patterns = {
            'feature': [r'FEATURE:', r'feat:', r'add:', r'new:'],
            'bugfix': [r'FIX:', r'fix:', r'bugfix:', r'fixed:'],
            'performance': [r'PERF:', r'perf:', r'optimize:', r'speed:'],
            'security': [r'SECURITY:', r'sec:', r'vuln:', r'secure:'],
            'docs': [r'DOCS:', r'doc:', r'documentation:'],
            'refactor': [r'REFACTOR:', r'refactor:', r'clean:', r'cleanup:'],
            'test': [r'TEST:', r'test:', r'tests:', r'testing:'],
            'deploy': [r'DEPLOY:', r'deployment:', r'ci:', r'cd:']
        }
        
        self.version_pattern = re.compile(r'v?(\d+)\.(\d+)\.(\d+)')
        self.current_version = self._get_current_version()
    
    def get_commits_since(self, since_date: Optional[datetime] = None, 
                         until_date: Optional[datetime] = None,
                         branch: str = "main") -> List[GitCommit]:
        """Get all commits within a time range"""
        
        # Build git log command
        cmd = [
            "git", "log", 
            "--pretty=format:%H|%an|%ai|%s",
            "--numstat",
            branch
        ]
        
        if since_date:
            cmd.append(f"--since={since_date.strftime('%Y-%m-%d')}")
        if until_date:
            cmd.append(f"--until={until_date.strftime('%Y-%m-%d')}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            if result.returncode != 0:
                print(f"Git log failed: {result.stderr}")
                return []
            
            return self._parse_git_log(result.stdout)
            
        except Exception as e:
            print(f"Error getting commits: {e}")
            return []
    
    def _parse_git_log(self, log_output: str) -> List[GitCommit]:
        """Parse git log output into commit objects"""
        commits = []
        lines = log_output.strip().split('\n')
        
        i = 0
        while i < len(lines):
            if '|' in lines[i]:
                # Parse commit line
                parts = lines[i].split('|')
                if len(parts) >= 4:
                    commit_hash = parts[0]
                    author = parts[1]
                    date_str = parts[2]
                    message = '|'.join(parts[3:])  # Handle messages with |
                    
                    # Parse date
                    date = datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
                    
                    # Parse file changes
                    files_changed = []
                    insertions = 0
                    deletions = 0
                    
                    i += 1
                    while i < len(lines) and lines[i] and '\t' in lines[i]:
                        parts = lines[i].split('\t')
                        if len(parts) >= 3:
                            try:
                                insertions += int(parts[0]) if parts[0] != '-' else 0
                                deletions += int(parts[1]) if parts[1] != '-' else 0
                                files_changed.append(parts[2])
                            except ValueError:
                                pass
                        i += 1
                    
                    commits.append(GitCommit(
                        hash=commit_hash,
                        author=author,
                        date=date,
                        message=message,
                        files_changed=files_changed,
                        insertions=insertions,
                        deletions=deletions
                    ))
            else:
                i += 1
        
        return commits
    
    def group_commits_into_updates(self, commits: List[GitCommit], 
                                 time_window_hours: int = 24) -> List[CommitGroup]:
        """Group related commits into logical updates"""
        
        if not commits:
            return []
        
        # Sort commits by date
        sorted_commits = sorted(commits, key=lambda c: c.date)
        
        groups = []
        current_group = []
        current_type = None
        group_start_time = None
        
        for commit in sorted_commits:
            commit_type = self._determine_commit_type(commit.message)
            
            # Start new group if:
            # 1. First commit
            # 2. Different type than current group
            # 3. More than time_window hours since group start
            if (not current_group or 
                commit_type != current_type or
                (group_start_time and (commit.date - group_start_time).total_seconds() > time_window_hours * 3600)):
                
                # Save previous group if exists
                if current_group:
                    groups.append(self._create_commit_group(current_group, current_type))
                
                # Start new group
                current_group = [commit]
                current_type = commit_type
                group_start_time = commit.date
            else:
                current_group.append(commit)
        
        # Don't forget last group
        if current_group:
            groups.append(self._create_commit_group(current_group, current_type))
        
        return groups
    
    def _determine_commit_type(self, message: str) -> str:
        """Determine the type of update from commit message"""
        message_lower = message.lower()
        
        for update_type, patterns in self.commit_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return update_type
        
        # Default based on keywords
        if any(word in message_lower for word in ['add', 'new', 'implement', 'create']):
            return 'feature'
        elif any(word in message_lower for word in ['fix', 'resolve', 'correct']):
            return 'bugfix'
        elif any(word in message_lower for word in ['update', 'improve', 'enhance']):
            return 'enhancement'
        
        return 'other'
    
    def _create_commit_group(self, commits: List[GitCommit], update_type: str) -> CommitGroup:
        """Create a commit group with aggregated information"""
        
        # Aggregate data
        total_insertions = sum(c.insertions for c in commits)
        total_deletions = sum(c.deletions for c in commits)
        all_files = []
        for c in commits:
            all_files.extend(c.files_changed)
        unique_files = list(set(all_files))
        
        # Determine components from files
        components = self._determine_components(unique_files)
        
        # Create title from most significant commit
        main_commit = max(commits, key=lambda c: c.insertions + c.deletions)
        title = self._clean_commit_message(main_commit.message)
        
        # Generate version
        version = self._increment_version(update_type)
        
        # Generate technical details
        technical_details = self._generate_technical_details(commits, unique_files)
        
        # Generate user impact
        user_impact = self._generate_user_impact(update_type, components, commits)
        
        # Generate metrics
        metrics = {
            'Commits': len(commits),
            'Files Changed': len(unique_files),
            'Lines Added': total_insertions,
            'Lines Removed': total_deletions,
            'Net Change': total_insertions - total_deletions
        }
        
        # Add type-specific metrics
        if update_type == 'performance':
            metrics['Performance Impact'] = 'Measured improvement'
        elif update_type == 'bugfix':
            metrics['Issues Resolved'] = len(commits)
        elif update_type == 'feature':
            metrics['Features Added'] = len(components)
        
        # Determine priority
        priority = self._determine_priority(update_type, total_insertions + total_deletions, commits)
        
        return CommitGroup(
            commits=commits,
            update_type=update_type,
            title=title,
            version=version,
            components=components,
            technical_details=technical_details,
            user_impact=user_impact,
            metrics=metrics,
            priority=priority
        )
    
    def _determine_components(self, files: List[str]) -> List[str]:
        """Determine affected components from file paths"""
        components = set()
        
        component_mapping = {
            'streamlit_app.py': 'Main Dashboard',
            'ultra_premium_dashboard.py': 'Premium Dashboard',
            'src/trading/': 'Trading Engine',
            'src/ai/': 'AI System',
            'src/data/': 'Data Processing',
            'src/telegram/': 'Telegram Integration',
            'discord_': 'Discord Integration',
            'webhook': 'Webhook System',
            'blog': 'Blog System',
            'test': 'Testing Framework',
            'deploy': 'Deployment System',
            '.github/': 'CI/CD Pipeline',
            'requirements': 'Dependencies',
            'docs/': 'Documentation',
            'config': 'Configuration'
        }
        
        for file in files:
            for pattern, component in component_mapping.items():
                if pattern in file.lower():
                    components.add(component)
                    break
            else:
                # Generic component based on directory
                if '/' in file:
                    dir_name = file.split('/')[0]
                    if dir_name not in ['archive', 'venv', '.git']:
                        components.add(f"{dir_name.title()} Module")
        
        return sorted(list(components))[:5]  # Limit to 5 components
    
    def _clean_commit_message(self, message: str) -> str:
        """Clean up commit message for use as title"""
        # Remove commit type prefixes
        for patterns in self.commit_patterns.values():
            for pattern in patterns:
                message = re.sub(pattern, '', message, flags=re.IGNORECASE).strip()
        
        # Capitalize first letter
        if message:
            message = message[0].upper() + message[1:]
        
        # Limit length
        if len(message) > 60:
            message = message[:57] + "..."
        
        return message
    
    def _generate_technical_details(self, commits: List[GitCommit], files: List[str]) -> str:
        """Generate technical details from commits"""
        details = []
        
        # Main changes
        details.append(f"This update includes {len(commits)} commits affecting {len(files)} files.")
        
        # Key changes by commit
        significant_commits = sorted(commits, key=lambda c: c.insertions + c.deletions, reverse=True)[:3]
        if significant_commits:
            details.append("\nKey changes:")
            for commit in significant_commits:
                msg = self._clean_commit_message(commit.message)
                details.append(f"• {msg} ({commit.insertions}+ {commit.deletions}-)")
        
        # File categories
        categories = {}
        for file in files:
            ext = file.split('.')[-1] if '.' in file else 'other'
            categories[ext] = categories.get(ext, 0) + 1
        
        if categories:
            details.append(f"\nFile types modified: {', '.join(f'{k} ({v})' for k, v in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3])}")
        
        return '\n'.join(details)
    
    def _generate_user_impact(self, update_type: str, components: List[str], commits: List[GitCommit]) -> str:
        """Generate user-facing impact description"""
        
        impact_templates = {
            'feature': "New capabilities added to {components}, providing enhanced functionality and improved user experience.",
            'bugfix': "Resolved {count} issues in {components}, resulting in more stable and reliable operation.",
            'performance': "Performance optimizations in {components} deliver faster response times and smoother operation.",
            'security': "Security enhancements in {components} provide better protection and data safety.",
            'docs': "Documentation improvements for {components} make the system easier to understand and use.",
            'refactor': "Code quality improvements in {components} ensure better maintainability and reliability.",
            'test': "Enhanced testing for {components} increases confidence in system stability.",
            'deploy': "Deployment improvements for {components} enable faster and more reliable updates."
        }
        
        template = impact_templates.get(update_type, "Updates to {components} improve overall system quality.")
        
        components_str = ", ".join(components[:2]) if len(components) > 2 else " and ".join(components)
        impact = template.format(
            components=components_str,
            count=len(commits)
        )
        
        return impact
    
    def _determine_priority(self, update_type: str, total_changes: int, commits: List[GitCommit]) -> str:
        """Determine update priority"""
        
        # Check for keywords indicating priority
        all_messages = ' '.join(c.message.lower() for c in commits)
        
        if any(word in all_messages for word in ['critical', 'urgent', 'emergency', 'hotfix']):
            return 'critical'
        elif any(word in all_messages for word in ['important', 'major', 'significant']):
            return 'high'
        elif update_type == 'security':
            return 'high'
        elif update_type == 'bugfix' and len(commits) > 3:
            return 'high'
        elif total_changes > 1000:
            return 'high'
        elif total_changes > 500:
            return 'medium'
        else:
            return 'low'
    
    def _get_current_version(self) -> Tuple[int, int, int]:
        """Get current version from git tags or default"""
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                match = self.version_pattern.search(result.stdout.strip())
                if match:
                    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except:
            pass
        
        return (1, 2, 2)  # Default to last known version
    
    def _increment_version(self, update_type: str) -> str:
        """Increment version based on update type"""
        major, minor, patch = self.current_version
        
        if update_type == 'feature':
            minor += 1
            patch = 0
        elif update_type in ['bugfix', 'security']:
            patch += 1
        else:
            patch += 1
        
        self.current_version = (major, minor, patch)
        return f"{major}.{minor}.{patch}"
    
    def generate_retrospective_updates(self, 
                                     since_date: Optional[datetime] = None,
                                     until_date: Optional[datetime] = None,
                                     time_window_hours: int = 24,
                                     auto_publish: bool = False,
                                     min_commits_per_update: int = 1,
                                     max_updates: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generate blog updates from git history"""
        
        # Default to last 7 days if no date specified
        if not since_date:
            since_date = datetime.now() - timedelta(days=7)
        
        print(f"📚 Generating retrospective updates from {since_date.strftime('%Y-%m-%d')} to {until_date.strftime('%Y-%m-%d') if until_date else 'now'}")
        
        # Get commits
        commits = self.get_commits_since(since_date, until_date)
        print(f"Found {len(commits)} commits")
        
        # Group commits
        groups = self.group_commits_into_updates(commits, time_window_hours)
        print(f"Grouped into {len(groups)} updates")
        
        # Filter and limit updates
        if min_commits_per_update > 1:
            groups = [g for g in groups if len(g.commits) >= min_commits_per_update]
        
        # Sort by date and limit if requested
        groups = sorted(groups, key=lambda g: g.commits[0].date, reverse=True)
        if max_updates:
            groups = groups[:max_updates]
        
        # Generate and optionally publish updates
        results = []
        for group in groups:
            # Convert to DevelopmentUpdate
            update = DevelopmentUpdate(
                update_type=group.update_type,
                title=group.title,
                version=group.version,
                components=group.components,
                technical_details=group.technical_details,
                user_impact=group.user_impact,
                metrics=group.metrics,
                timestamp=group.commits[0].date,  # Use first commit date
                author=group.commits[0].author,
                priority=group.priority
            )
            
            if auto_publish:
                print(f"\n📝 Publishing: {update.title} (v{update.version})")
                result = self.publish_integrated_update(update)
                results.append({
                    'update': update,
                    'result': result,
                    'commits': group.commits
                })
            else:
                results.append({
                    'update': update,
                    'result': None,
                    'commits': group.commits
                })
        
        return results
    
    def generate_retrospective_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate a report of retrospective updates"""
        
        report = f"""
# 📚 TrenchCoat Pro - Retrospective Blog Update Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Updates:** {len(results)}
**Commits Processed:** {sum(len(r['commits']) for r in results)}

## 📊 Updates Generated

"""
        
        for idx, result in enumerate(results, 1):
            update = result['update']
            commits = result['commits']
            
            report += f"""
### {idx}. {update.title} (v{update.version})

**Type:** {update.update_type.title()} | **Priority:** {update.priority.upper()}
**Date:** {update.timestamp.strftime('%Y-%m-%d %H:%M')}
**Author:** {update.author}

**Components:**
{chr(10).join([f'- {c}' for c in update.components])}

**Technical Details:**
{update.technical_details}

**User Impact:**
{update.user_impact}

**Metrics:**
{chr(10).join([f'- {k}: {v}' for k, v in update.metrics.items()])}

**Commits ({len(commits)}):**
{chr(10).join([f'- {c.hash[:8]} - {self._clean_commit_message(c.message)}' for c in commits[:5]])}
{f'- ... and {len(commits) - 5} more' if len(commits) > 5 else ''}

---
"""
        
        # Summary statistics
        update_types = {}
        total_insertions = 0
        total_deletions = 0
        
        for result in results:
            update_type = result['update'].update_type
            update_types[update_type] = update_types.get(update_type, 0) + 1
            
            for commit in result['commits']:
                total_insertions += commit.insertions
                total_deletions += commit.deletions
        
        report += f"""
## 📈 Summary Statistics

**Update Types:**
{chr(10).join([f'- {k.title()}: {v}' for k, v in sorted(update_types.items(), key=lambda x: x[1], reverse=True)])}

**Code Changes:**
- Total Insertions: {total_insertions:,}
- Total Deletions: {total_deletions:,}
- Net Change: {total_insertions - total_deletions:,}

**Publishing Status:**
- Published: {sum(1 for r in results if r['result'] is not None)}
- Draft: {sum(1 for r in results if r['result'] is None)}

---
*Generated by TrenchCoat Pro Retrospective Blog System*
"""
        
        return report

# Example usage
if __name__ == "__main__":
    print("🔄 TrenchCoat Pro - Retrospective Blog System")
    print("=" * 60)
    
    system = RetrospectiveBlogSystem()
    
    # Generate updates for last 7 days
    print("\n📚 Analyzing git history...")
    results = system.generate_retrospective_updates(
        since_date=datetime.now() - timedelta(days=7),
        time_window_hours=24,
        auto_publish=False  # Set to True to actually publish
    )
    
    # Generate report
    report = system.generate_retrospective_report(results)
    
    # Save report
    with open("retrospective_blog_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 Report saved to: retrospective_blog_report.md")
    print(f"📊 Total updates found: {len(results)}")
    print(f"💡 Set auto_publish=True to publish these updates")