#!/usr/bin/env python3
"""
Deployment Verification System - Ensures all changes are properly committed and deployed
Prevents issues where dashboard doesn't update due to uncommitted files
"""
import subprocess
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
import requests
import time

class DeploymentVerifier:
    """Comprehensive deployment verification system"""
    
    def __init__(self):
        self.verification_results = {}
        self.critical_files = [
            'streamlit_app.py',
            'streamlit_safe_dashboard.py', 
            'streamlit_database.py',
            'requirements.txt',
            'CLAUDE.md'
        ]
        
    def run_full_verification(self) -> Dict[str, Any]:
        """Run complete deployment verification"""
        print("🔍 Starting comprehensive deployment verification...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'git_status': self.check_git_status(),
            'file_changes': self.check_file_changes(),
            'commit_status': self.check_commit_status(),
            'push_status': self.check_push_status(),
            'streamlit_status': self.check_streamlit_status(),
            'deployment_score': 0,
            'critical_issues': [],
            'recommendations': []
        }
        
        # Calculate deployment score
        results['deployment_score'] = self.calculate_deployment_score(results)
        
        # Generate recommendations
        results['recommendations'] = self.generate_recommendations(results)
        
        # Print summary
        self.print_verification_summary(results)
        
        return results
    
    def check_git_status(self) -> Dict[str, Any]:
        """Check git repository status"""
        print("📋 Checking git status...")
        
        try:
            # Check for uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            uncommitted_files = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        status = line[:2]
                        filename = line[3:]
                        uncommitted_files.append({
                            'status': status,
                            'filename': filename,
                            'critical': filename in self.critical_files
                        })
            
            # Check current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True)
            current_branch = branch_result.stdout.strip()
            
            # Check if ahead of remote
            ahead_result = subprocess.run(['git', 'rev-list', '--count', 'HEAD@{upstream}..HEAD'], 
                                        capture_output=True, text=True)
            commits_ahead = int(ahead_result.stdout.strip()) if ahead_result.returncode == 0 else 0
            
            git_status = {
                'clean': len(uncommitted_files) == 0,
                'uncommitted_files': uncommitted_files,
                'critical_uncommitted': len([f for f in uncommitted_files if f['critical']]),
                'current_branch': current_branch,
                'commits_ahead': commits_ahead,
                'ready_to_push': commits_ahead > 0
            }
            
            print(f"   ✅ Branch: {current_branch}")
            print(f"   📝 Uncommitted files: {len(uncommitted_files)}")
            print(f"   🚀 Commits ahead: {commits_ahead}")
            
            return git_status
            
        except Exception as e:
            print(f"   ❌ Git status check failed: {e}")
            return {'error': str(e), 'clean': False}
    
    def check_file_changes(self) -> Dict[str, Any]:
        """Check if critical files have been modified"""
        print("📁 Checking critical file changes...")
        
        try:
            # Get list of changed files in last commit
            result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'], 
                                  capture_output=True, text=True)
            
            changed_files = result.stdout.strip().split('\n') if result.stdout else []
            
            # Check critical files
            critical_changes = []
            for file in self.critical_files:
                if file in changed_files:
                    critical_changes.append(file)
            
            file_changes = {
                'total_changed': len(changed_files),
                'changed_files': changed_files,
                'critical_changes': critical_changes,
                'dashboard_changed': 'streamlit_safe_dashboard.py' in changed_files,
                'database_changed': 'streamlit_database.py' in changed_files,
                'app_changed': 'streamlit_app.py' in changed_files
            }
            
            print(f"   📄 Files changed: {len(changed_files)}")
            print(f"   🔥 Critical changes: {len(critical_changes)}")
            
            return file_changes
            
        except Exception as e:
            print(f"   ❌ File changes check failed: {e}")
            return {'error': str(e)}
    
    def check_commit_status(self) -> Dict[str, Any]:
        """Check recent commit information"""
        print("💾 Checking commit status...")
        
        try:
            # Get last commit info
            result = subprocess.run(['git', 'log', '-1', '--format=%H|%s|%an|%ad'], 
                                  capture_output=True, text=True)
            
            if result.stdout:
                parts = result.stdout.strip().split('|')
                commit_hash = parts[0]
                commit_message = parts[1]
                author = parts[2]
                date = parts[3]
                
                commit_status = {
                    'hash': commit_hash,
                    'short_hash': commit_hash[:7],
                    'message': commit_message,
                    'author': author,
                    'date': date,
                    'recent': True  # Could add time check here
                }
                
                print(f"   🔗 Last commit: {commit_hash[:7]}")
                print(f"   📝 Message: {commit_message[:50]}...")
                
                return commit_status
            else:
                return {'error': 'No commits found'}
                
        except Exception as e:
            print(f"   ❌ Commit status check failed: {e}")
            return {'error': str(e)}
    
    def check_push_status(self) -> Dict[str, Any]:
        """Check if changes have been pushed to remote"""
        print("🚀 Checking push status...")
        
        try:
            # Try to push (dry run)
            result = subprocess.run(['git', 'push', '--dry-run'], 
                                  capture_output=True, text=True)
            
            push_needed = result.returncode == 0 and result.stderr
            
            # Check remote status
            remote_result = subprocess.run(['git', 'remote', '-v'], 
                                         capture_output=True, text=True)
            
            push_status = {
                'push_needed': push_needed,
                'has_remote': bool(remote_result.stdout),
                'last_push_result': result.stderr if result.stderr else 'Up to date',
                'can_push': result.returncode == 0
            }
            
            print(f"   📤 Push needed: {push_needed}")
            print(f"   🌐 Has remote: {push_status['has_remote']}")
            
            return push_status
            
        except Exception as e:
            print(f"   ❌ Push status check failed: {e}")
            return {'error': str(e)}
    
    def check_streamlit_status(self) -> Dict[str, Any]:
        """Check Streamlit app deployment status"""
        print("📱 Checking Streamlit deployment status...")
        
        # This would need to be configured with your actual Streamlit app URL
        streamlit_url = "https://your-streamlit-app.streamlit.app"  # Replace with actual URL
        
        try:
            response = requests.get(streamlit_url, timeout=10)
            
            streamlit_status = {
                'accessible': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'last_check': datetime.now().isoformat()
            }
            
            print(f"   🌐 App accessible: {streamlit_status['accessible']}")
            print(f"   ⚡ Response time: {streamlit_status['response_time']:.2f}s")
            
            return streamlit_status
            
        except Exception as e:
            print(f"   ⚠️ Streamlit check failed: {e}")
            return {
                'accessible': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def calculate_deployment_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall deployment score (0-100)"""
        score = 0
        
        # Git status (30 points)
        git_status = results.get('git_status', {})
        if git_status.get('clean', False):
            score += 15
        if git_status.get('commits_ahead', 0) == 0:  # All changes pushed
            score += 15
        
        # File changes (20 points)
        file_changes = results.get('file_changes', {})
        if file_changes.get('critical_changes'):
            score += 20  # Critical files were changed
        
        # Commit status (20 points)
        commit_status = results.get('commit_status', {})
        if commit_status.get('hash'):
            score += 20  # Valid commit exists
        
        # Push status (20 points)
        push_status = results.get('push_status', {})
        if not push_status.get('push_needed', True):
            score += 20  # No push needed (all up to date)
        
        # Streamlit status (10 points)
        streamlit_status = results.get('streamlit_status', {})
        if streamlit_status.get('accessible', False):
            score += 10
        
        return min(score, 100)
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate deployment recommendations"""
        recommendations = []
        
        git_status = results.get('git_status', {})
        
        # Check for uncommitted changes
        if not git_status.get('clean', True):
            uncommitted = git_status.get('uncommitted_files', [])
            critical_uncommitted = [f for f in uncommitted if f.get('critical', False)]
            
            if critical_uncommitted:
                recommendations.append(
                    f"🚨 CRITICAL: Commit {len(critical_uncommitted)} critical files: " + 
                    ", ".join([f['filename'] for f in critical_uncommitted])
                )
            else:
                recommendations.append(
                    f"⚠️ Commit {len(uncommitted)} uncommitted files before deployment"
                )
        
        # Check for unpushed commits
        if git_status.get('commits_ahead', 0) > 0:
            recommendations.append(
                f"📤 Push {git_status['commits_ahead']} local commits to remote repository"
            )
        
        # Check Streamlit status
        streamlit_status = results.get('streamlit_status', {})
        if not streamlit_status.get('accessible', False):
            recommendations.append("🌐 Verify Streamlit app is accessible and functioning")
        
        # Force rebuild recommendation
        file_changes = results.get('file_changes', {})
        if file_changes.get('dashboard_changed') or file_changes.get('database_changed'):
            recommendations.append("🔄 Consider forcing Streamlit cache clear for dashboard changes")
        
        if not recommendations:
            recommendations.append("✅ All systems operational - deployment looks good!")
        
        return recommendations
    
    def print_verification_summary(self, results: Dict[str, Any]):
        """Print comprehensive verification summary"""
        print("\n" + "="*60)
        print("📊 DEPLOYMENT VERIFICATION SUMMARY")
        print("="*60)
        
        score = results['deployment_score']
        
        # Score visualization
        if score >= 90:
            status = "🟢 EXCELLENT"
        elif score >= 70:
            status = "🟡 GOOD"
        elif score >= 50:
            status = "🟠 NEEDS ATTENTION"
        else:
            status = "🔴 CRITICAL ISSUES"
        
        print(f"Overall Score: {score}/100 - {status}")
        print()
        
        # Critical issues
        if results.get('critical_issues'):
            print("🚨 CRITICAL ISSUES:")
            for issue in results['critical_issues']:
                print(f"   • {issue}")
            print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        for rec in results['recommendations']:
            print(f"   • {rec}")
        print()
        
        # Quick status
        git_status = results.get('git_status', {})
        print("📋 QUICK STATUS:")
        print(f"   Git Clean: {'✅' if git_status.get('clean') else '❌'}")
        print(f"   Commits Ahead: {git_status.get('commits_ahead', 0)}")
        print(f"   Critical Files Changed: {len(results.get('file_changes', {}).get('critical_changes', []))}")
        print(f"   Streamlit Accessible: {'✅' if results.get('streamlit_status', {}).get('accessible') else '❌'}")
        
        print("="*60)
        
        # Save results
        self.save_verification_results(results)
    
    def save_verification_results(self, results: Dict[str, Any]):
        """Save verification results to file"""
        try:
            with open('deployment_verification_results.json', 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print("💾 Verification results saved to deployment_verification_results.json")
        except Exception as e:
            print(f"⚠️ Could not save results: {e}")

def main():
    """Run deployment verification"""
    verifier = DeploymentVerifier()
    results = verifier.run_full_verification()
    
    # Return exit code based on score
    if results['deployment_score'] >= 90:
        exit(0)  # Success
    elif results['deployment_score'] >= 50:
        exit(1)  # Warning
    else:
        exit(2)  # Critical issues

if __name__ == "__main__":
    main()