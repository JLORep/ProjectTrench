#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safe wrapper for running documentation updates with proper encoding
"""
import sys
import io
import os

# Set up proper encoding for Windows
if sys.platform == 'win32':
    # Force UTF-8 encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
# Import after encoding is set
from update_all_docs import DocumentationUpdater

def safe_print(text):
    """Print with encoding safety"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to ASCII representation
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

def run_safe_update():
    """Run documentation update with encoding protection"""
    
    # Session details
    session_title = "Enhanced Charts & Breadcrumb Navigation"
    description = """Complete implementation of interactive charts with Plotly, fixed breadcrumb navigation using buttons, 
    added enhanced auto-scaling visualizations, created performance radar chart, and resolved spinning circle issues 
    through gradual restoration strategy"""
    
    safe_print(f"Starting safe documentation update...")
    safe_print(f"Session: {session_title}")
    safe_print(f"Description: {description}")
    safe_print("=" * 60)
    
    try:
        updater = DocumentationUpdater()
        
        # Run the update directly
        results = updater.run_full_update(session_title, description)
        
        # Summary
        safe_print("\n" + "=" * 60)
        safe_print("UPDATE COMPLETE")
        safe_print(f"Total files processed: {len(results)}")
        safe_print(f"Successful updates: {sum(1 for v in results.values() if v)}")
        safe_print(f"Failed updates: {sum(1 for v in results.values() if not v)}")
        
        return results
        
    except Exception as e:
        safe_print(f"ERROR: {str(e).encode('ascii', 'replace').decode('ascii')}")
        return {}

if __name__ == "__main__":
    run_safe_update()