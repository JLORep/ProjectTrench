#!/usr/bin/env python3
"""
TrenchCoat Pro - Smart Retrospective Blog Summary
Intelligently summarizes git commits into meaningful blog updates
"""

from retrospective_blog_system import RetrospectiveBlogSystem, GitCommit, CommitGroup, DevelopmentUpdate
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

class SmartRetrospectiveBlogSummary(RetrospectiveBlogSystem):
    """Enhanced system that intelligently summarizes commits"""
    
    def create_daily_summaries(self, 
                             since_date: Optional[datetime] = None,
                             until_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Create daily summary updates from commits"""
        
        # Get all commits
        commits = self.get_commits_since(since_date, until_date)
        print(f"📊 Processing {len(commits)} commits...")
        
        # Group by day and type
        daily_groups = defaultdict(lambda: defaultdict(list))
        
        for commit in commits:
            day = commit.date.date()
            commit_type = self._determine_commit_type(commit.message)
            daily_groups[day][commit_type].append(commit)
        
        # Create summary updates
        summaries = []
        
        for day, type_groups in sorted(daily_groups.items(), reverse=True):
            # Skip days with few commits
            total_commits = sum(len(commits) for commits in type_groups.values())
            if total_commits < 3:
                continue
            
            # Create a comprehensive daily update
            all_commits = []
            for commits in type_groups.values():
                all_commits.extend(commits)
            
            # Determine primary update type
            primary_type = max(type_groups.items(), key=lambda x: len(x[1]))[0]
            
            # Generate title
            title = f"Daily Development Update - {day.strftime('%B %d, %Y')}"
            
            # Generate version
            version = self._increment_version(primary_type)
            
            # Aggregate components
            all_files = []
            for commit in all_commits:
                all_files.extend(commit.files_changed)
            components = self._determine_components(list(set(all_files)))
            
            # Generate summary details
            technical_details = self._generate_daily_technical_summary(type_groups, all_files)
            user_impact = self._generate_daily_user_impact(type_groups, components)
            
            # Generate metrics
            metrics = self._generate_daily_metrics(type_groups, all_commits)
            
            # Determine priority based on activity
            if total_commits > 20:
                priority = 'high'
            elif total_commits > 10:
                priority = 'medium'
            else:
                priority = 'low'
            
            summaries.append({
                'date': day,
                'update': DevelopmentUpdate(
                    update_type='summary',
                    title=title,
                    version=version,
                    components=components,
                    technical_details=technical_details,
                    user_impact=user_impact,
                    metrics=metrics,
                    timestamp=datetime.combine(day, datetime.min.time()),
                    priority=priority
                ),
                'commits': all_commits,
                'type_breakdown': {k: len(v) for k, v in type_groups.items()}
            })
        
        return summaries
    
    def create_feature_focused_updates(self,
                                     since_date: Optional[datetime] = None,
                                     until_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Create updates focused on major features"""
        
        commits = self.get_commits_since(since_date, until_date)
        
        # Look for feature patterns
        feature_keywords = {
            'dashboard': ['dashboard', 'ui', 'interface', 'display'],
            'trading': ['trading', 'trade', 'sniper', 'bot'],
            'integration': ['webhook', 'discord', 'telegram', 'api'],
            'ai': ['ai', 'claude', 'ml', 'analysis', 'intelligence'],
            'security': ['security', 'auth', 'protection', 'encryption'],
            'performance': ['performance', 'optimize', 'speed', 'cache'],
            'data': ['database', 'enrichment', 'data', 'pipeline']
        }
        
        feature_groups = defaultdict(list)
        
        for commit in commits:
            message_lower = commit.message.lower()
            
            # Categorize by feature
            for feature, keywords in feature_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    feature_groups[feature].append(commit)
                    break
            else:
                # Check files for categorization
                for file in commit.files_changed:
                    file_lower = file.lower()
                    for feature, keywords in feature_keywords.items():
                        if any(keyword in file_lower for keyword in keywords):
                            feature_groups[feature].append(commit)
                            break
                    else:
                        feature_groups['other'].append(commit)
        
        # Create feature updates
        updates = []
        
        for feature, commits in feature_groups.items():
            if len(commits) < 5:  # Skip minor features
                continue
            
            # Create feature update
            title = f"{feature.title()} System Enhancements"
            version = self._increment_version('feature')
            
            # Get unique files
            all_files = []
            for commit in commits:
                all_files.extend(commit.files_changed)
            unique_files = list(set(all_files))
            
            components = self._determine_components(unique_files)
            
            # Feature-specific details
            technical_details = f"""
Major improvements to the {feature} system including:

{self._summarize_commits_by_impact(commits)}

Technical scope:
- {len(commits)} commits implemented
- {len(unique_files)} files modified
- {sum(c.insertions for c in commits)} lines added
- {sum(c.deletions for c in commits)} lines removed
""".strip()
            
            user_impact = self._generate_feature_user_impact(feature, commits)
            
            metrics = {
                'Commits': len(commits),
                'Files Changed': len(unique_files),
                'Code Added': sum(c.insertions for c in commits),
                'Code Removed': sum(c.deletions for c in commits),
                'Contributors': len(set(c.author for c in commits))
            }
            
            updates.append({
                'feature': feature,
                'update': DevelopmentUpdate(
                    update_type='feature',
                    title=title,
                    version=version,
                    components=components,
                    technical_details=technical_details,
                    user_impact=user_impact,
                    metrics=metrics,
                    timestamp=commits[0].date,
                    priority='high' if len(commits) > 10 else 'medium'
                ),
                'commits': commits
            })
        
        return sorted(updates, key=lambda x: len(x['commits']), reverse=True)
    
    def _generate_daily_technical_summary(self, type_groups: Dict[str, List[GitCommit]], 
                                        all_files: List[str]) -> str:
        """Generate technical summary for daily update"""
        
        summary_parts = ["Today's development activity included:"]
        
        # Summarize by type
        for update_type, commits in sorted(type_groups.items(), key=lambda x: len(x[1]), reverse=True):
            if update_type == 'other':
                continue
            summary_parts.append(f"\n**{update_type.title()} Updates ({len(commits)}):**")
            
            # Get top 3 commits by size
            top_commits = sorted(commits, key=lambda c: c.insertions + c.deletions, reverse=True)[:3]
            for commit in top_commits:
                msg = self._clean_commit_message(commit.message)
                summary_parts.append(f"• {msg}")
        
        # File statistics
        file_types = defaultdict(int)
        for file in all_files:
            ext = file.split('.')[-1] if '.' in file else 'other'
            file_types[ext] += 1
        
        summary_parts.append(f"\n**Files Modified:** {', '.join(f'{ext} ({count})' for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5])}")
        
        return '\n'.join(summary_parts)
    
    def _generate_daily_user_impact(self, type_groups: Dict[str, List[GitCommit]], 
                                  components: List[str]) -> str:
        """Generate user impact for daily summary"""
        
        impacts = []
        
        if 'feature' in type_groups:
            impacts.append(f"✨ {len(type_groups['feature'])} new features enhance your trading capabilities")
        
        if 'bugfix' in type_groups:
            impacts.append(f"🐛 {len(type_groups['bugfix'])} bug fixes improve stability and reliability")
        
        if 'performance' in type_groups:
            impacts.append(f"⚡ {len(type_groups['performance'])} performance improvements deliver faster operation")
        
        if 'security' in type_groups:
            impacts.append(f"🔒 {len(type_groups['security'])} security updates protect your data better")
        
        if not impacts:
            impacts.append("Various improvements enhance overall system quality")
        
        return f"Today's updates bring significant improvements: {', '.join(impacts)}. Affected components include {', '.join(components[:3])}."
    
    def _generate_daily_metrics(self, type_groups: Dict[str, List[GitCommit]], 
                              all_commits: List[GitCommit]) -> Dict[str, Any]:
        """Generate metrics for daily summary"""
        
        metrics = {
            'Total Commits': len(all_commits),
            'Update Types': len(type_groups),
            'Lines Added': sum(c.insertions for c in all_commits),
            'Lines Removed': sum(c.deletions for c in all_commits),
            'Net Change': sum(c.insertions - c.deletions for c in all_commits),
            'Contributors': len(set(c.author for c in all_commits))
        }
        
        # Add type breakdown
        for update_type, commits in type_groups.items():
            if update_type != 'other':
                metrics[f'{update_type.title()} Updates'] = len(commits)
        
        return metrics
    
    def _summarize_commits_by_impact(self, commits: List[GitCommit]) -> str:
        """Summarize commits by their impact"""
        
        # Group similar commits
        message_groups = defaultdict(list)
        
        for commit in commits:
            # Extract key action from message
            msg = self._clean_commit_message(commit.message)
            key_words = msg.lower().split()[:3]  # First 3 words as key
            key = ' '.join(key_words)
            message_groups[key].append(commit)
        
        # Create summary
        summaries = []
        
        # Get top groups by size
        top_groups = sorted(message_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        
        for key, group_commits in top_groups:
            if len(group_commits) > 1:
                summaries.append(f"• {len(group_commits)} updates for {key}")
            else:
                msg = self._clean_commit_message(group_commits[0].message)
                summaries.append(f"• {msg}")
        
        return '\n'.join(summaries)
    
    def _generate_feature_user_impact(self, feature: str, commits: List[GitCommit]) -> str:
        """Generate user impact for feature updates"""
        
        impact_templates = {
            'dashboard': "Enhanced dashboard functionality provides a more intuitive and powerful trading interface with improved visualizations and real-time updates.",
            'trading': "Advanced trading capabilities enable faster execution, better opportunity detection, and more profitable trades.",
            'integration': "Improved integrations ensure you never miss important signals and stay connected across all platforms.",
            'ai': "Enhanced AI intelligence delivers more accurate predictions, better risk assessment, and smarter trading decisions.",
            'security': "Strengthened security measures protect your assets and data with enterprise-grade protection.",
            'performance': "Performance optimizations deliver lightning-fast response times and smoother operation even with high data volumes.",
            'data': "Enhanced data processing provides more comprehensive market insights and better decision-making information."
        }
        
        return impact_templates.get(feature, f"Improvements to the {feature} system enhance overall platform capabilities and user experience.")
    
    def generate_smart_summary_report(self, daily_summaries: List[Dict], 
                                    feature_updates: List[Dict]) -> str:
        """Generate a comprehensive summary report"""
        
        report = f"""
# 📊 TrenchCoat Pro - Smart Development Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Period:** {daily_summaries[-1]['date'] if daily_summaries else 'N/A'} to {daily_summaries[0]['date'] if daily_summaries else 'N/A'}

## 📅 Daily Development Summaries ({len(daily_summaries)} days with significant activity)

"""
        
        for summary in daily_summaries[:7]:  # Show last week
            update = summary['update']
            report += f"""
### {update.title}

**Activity Level:** {update.priority.upper()} | **Version:** {update.version}

**Update Breakdown:**
{chr(10).join([f"- {k}: {v} commits" for k, v in summary['type_breakdown'].items() if k != 'other'])}

**Key Metrics:**
{chr(10).join([f"- {k}: {v}" for k, v in list(update.metrics.items())[:5]])}

**Impact:** {update.user_impact}

---
"""
        
        report += f"""
## 🚀 Major Feature Updates ({len(feature_updates)} feature areas)

"""
        
        for feat in feature_updates[:5]:  # Top 5 features
            update = feat['update']
            report += f"""
### {update.title}

**Commits:** {len(feat['commits'])} | **Priority:** {update.priority.upper()}

{update.technical_details}

**User Impact:** {update.user_impact}

---
"""
        
        # Overall statistics
        all_commits = []
        for summary in daily_summaries:
            all_commits.extend(summary['commits'])
        
        report += f"""
## 📈 Overall Development Statistics

- **Total Days Active:** {len(daily_summaries)}
- **Total Commits:** {len(all_commits)}
- **Average Commits/Day:** {len(all_commits) / max(len(daily_summaries), 1):.1f}
- **Most Active Day:** {max(daily_summaries, key=lambda x: len(x['commits']))['date'] if daily_summaries else 'N/A'}
- **Primary Focus Areas:** {', '.join([f['feature'] for f in feature_updates[:3]])}

---
*Generated by TrenchCoat Pro Smart Retrospective System*
"""
        
        return report

# Example usage
if __name__ == "__main__":
    print("🧠 TrenchCoat Pro - Smart Retrospective Summary")
    print("=" * 60)
    
    system = SmartRetrospectiveBlogSummary()
    
    # Generate smart summaries
    print("\n📅 Creating daily summaries...")
    daily_summaries = system.create_daily_summaries(
        since_date=datetime.now() - timedelta(days=7)
    )
    
    print(f"📊 Created {len(daily_summaries)} daily summaries")
    
    print("\n🚀 Creating feature-focused updates...")
    feature_updates = system.create_feature_focused_updates(
        since_date=datetime.now() - timedelta(days=7)
    )
    
    print(f"✨ Created {len(feature_updates)} feature updates")
    
    # Generate report
    report = system.generate_smart_summary_report(daily_summaries, feature_updates)
    
    # Save report
    with open("smart_retrospective_summary.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ Smart summary complete!")
    print(f"📄 Report saved to: smart_retrospective_summary.md")
    
    # Show sample
    if daily_summaries:
        print(f"\n📝 Latest daily summary: {daily_summaries[0]['update'].title}")
        print(f"   Commits: {len(daily_summaries[0]['commits'])}")
        print(f"   Types: {', '.join(daily_summaries[0]['type_breakdown'].keys())}")