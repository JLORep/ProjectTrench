#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple session documentation updater for key files
"""
import os
from datetime import datetime

def safe_read_file(filepath):
    """Read file with encoding safety"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def safe_write_file(filepath, content):
    """Write file with encoding safety"""
    try:
        # Create backup
        if os.path.exists(filepath):
            backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(filepath, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
        
        # Write new content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False

def update_dashboard_md():
    """Update dashboard.md with enhanced charts section"""
    filepath = "dashboard.md"
    content = safe_read_file(filepath)
    
    if content and "## Session 2025-08-01 ENHANCED CHARTS" not in content:
        # Find where to insert
        insert_point = content.rfind("*Last Updated:")
        if insert_point > 0:
            # Add new section before last updated line
            new_section = """

## Session 2025-08-01 ENHANCED CHARTS & NAVIGATION COMPLETE ✅

### 🎨 Chart System Enhancements
**Created**: `enhanced_charts_system.py` with stunning visualizations
**Features Implemented**:
- Auto-scaling with reactive updates for all chart types
- Bigger range selector buttons (1W, 2W, 1M, ALL)
- Dark theme with glassmorphism effects
- Gradient fills and glow effects on moving averages
- Custom modebar with drawing tools
- High-resolution export options (2x scale)
- Performance radar chart with 6 metrics

### 🧭 Breadcrumb Navigation Fix
**Issue**: HTML anchor tags don't work in Streamlit
**Solution**: Replaced with button-based navigation
```python
if st.button(name, key=f"breadcrumb_{key}_{current_path}"):
    st.session_state.show_coin_detail = False
    st.rerun()
```

### 📊 Enhanced Chart Details:
1. **Price Chart**:
   - Candlesticks with green/red gradient colors
   - Volume bars colored by buy/sell pressure
   - MA7/MA20 with glow effects
   - Price change annotation
   - Custom range selector

2. **Holder Distribution**:
   - Donut chart with pull-out effect for smart money
   - Center text showing total holders
   - Enhanced color scheme

3. **Liquidity Depth**:
   - Detailed order book visualization
   - Current price line with annotation
   - Spread percentage display
   - Gradient fills for bid/ask

4. **Performance Radar** (NEW):
   - 6 metrics: Liquidity, Volume, Holders, Trend, Market Cap, Activity
   - Benchmark comparison overlay
   - Score normalization to 0-100

### 🚀 Gradual Restoration Success
**Problem**: Spinning circle after chart integration
**Solution**: 3-step gradual restoration
1. Step 1 (v2.3.1): Basic structure without charts
2. Step 2 (v2.3.2): Visual features and cards
3. Step 3 (v2.3.3): Full charts and navigation

### Technical Implementation:
- Layered imports with fallbacks
- Chart functions return `(figure, config)` tuples
- Config includes custom buttons and export settings
- Graceful degradation if Plotly unavailable

"""
            # Insert before last updated
            new_content = content[:insert_point] + new_section + "\n" + content[insert_point:]
            
            # Update last updated timestamp
            new_content = new_content.replace(
                content[insert_point:insert_point+100].split('\n')[0],
                f"*Last Updated: 2025-08-01 22:30 - Enhanced charts with auto-scaling, fixed breadcrumb navigation*"
            )
            
            if safe_write_file(filepath, new_content):
                print(f"✅ Updated {filepath}")
                return True
    
    return False

def update_claude_md():
    """Update CLAUDE.md with session summary"""
    filepath = "CLAUDE.md"
    content = safe_read_file(filepath)
    
    if content and "Session 2025-08-01 ENHANCED CHARTS" not in content:
        # Find insertion point (after last session entry)
        insert_point = content.rfind("*Last updated:")
        if insert_point > 0:
            new_section = """

## Session 2025-08-01 ENHANCED CHARTS & NAVIGATION - Complete Implementation ✅

### 🎯 User Request and Resolution
**Request**: "take the chart visualiation to th enext level and make it very stylish and reactive auto scaling chart make the chart buttons bigger"
**Issue Fixed**: "the links on the breadcrumb text doesnt work"
**Status**: ✅ COMPLETE - All requested features implemented

### Technical Implementation:
1. **Enhanced Charts System** (`enhanced_charts_system.py`):
   - 4 enhanced chart types with auto-scaling
   - Bigger range selector buttons
   - Dark theme with glassmorphism
   - Gradient fills and glow effects
   - Custom modebar configuration
   - High-resolution export options

2. **Breadcrumb Navigation Fix**:
   - Replaced HTML anchors with Streamlit buttons
   - Used session state for navigation
   - Maintained visual styling

3. **Gradual Restoration Strategy**:
   - Step 1: Basic structure without charts
   - Step 2: Visual features and cards
   - Step 3: Full charts and navigation
   - Prevented spinning circle issue

### Files Created/Modified:
- `enhanced_charts_system.py` - Complete chart visualization system
- `breadcrumb_navigation.py` - Navigation with button-based links
- `streamlit_app.py` - Integrated enhanced charts
- `streamlit_app_v2.py`, `v3.py`, `v4.py` - Gradual restoration steps

### Key Learnings:
1. **HTML Links Don't Work**: Streamlit doesn't support HTML anchor navigation
2. **Button Navigation Works**: Use st.button() with session state for navigation
3. **Gradual Feature Addition**: Prevents spinning circle when adding complex features
4. **Chart Configuration**: Return (figure, config) tuples for better control

"""
            # Insert before last updated
            new_content = content[:insert_point] + new_section + "\n" + content[insert_point:]
            
            # Update last updated timestamp
            new_content = new_content.replace(
                content[insert_point:insert_point+100].split('\n')[0],
                f"*Last updated: 2025-08-01 22:30 - Enhanced charts system complete*"
            )
            
            if safe_write_file(filepath, new_content):
                print(f"✅ Updated {filepath}")
                return True
    
    return False

def update_todo_md():
    """Update todo.md with completed tasks"""
    filepath = "todo.md"
    content = safe_read_file(filepath)
    
    if content:
        # Find tasks to mark as completed
        updates_made = False
        
        # Task 20: Fix breadcrumb navigation links
        if "20. 🔄 **Fix breadcrumb navigation links**" in content and "Status: Pending" in content:
            content = content.replace(
                "20. 🔄 **Fix breadcrumb navigation links**\n   - Status: Pending",
                "20. ✅ **Fix breadcrumb navigation links - use buttons instead**\n   - Status: Completed"
            )
            updates_made = True
        
        # Task 21: Create enhanced charts
        if "21. 🔄 **Create enhanced charts**" in content and "Status: Pending" in content:
            content = content.replace(
                "21. 🔄 **Create enhanced charts**\n   - Status: Pending",
                "21. ✅ **Create enhanced charts with auto-scaling and reactive updates**\n   - Status: Completed"
            )
            updates_made = True
        
        # Task 22: Add performance radar chart
        if "22. 🔄 **Add performance radar chart**" in content and "Status: Pending" in content:
            content = content.replace(
                "22. 🔄 **Add performance radar chart**\n   - Status: Pending",
                "22. ✅ **Add performance radar chart visualization**\n   - Status: Completed"
            )
            updates_made = True
        
        if updates_made and safe_write_file(filepath, content):
            print(f"✅ Updated {filepath}")
            return True
    
    return False

def main():
    """Run documentation updates"""
    print("SESSION DOCUMENTATION UPDATE")
    print("=" * 60)
    print("Session: Enhanced Charts & Navigation")
    print("Date: 2025-08-01")
    print("=" * 60)
    
    # Update key documentation files
    results = {
        'dashboard.md': update_dashboard_md(),
        'CLAUDE.md': update_claude_md(),
        'todo.md': update_todo_md()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("UPDATE SUMMARY:")
    success_count = sum(1 for v in results.values() if v)
    print(f"Files updated: {success_count}/{len(results)}")
    
    for file, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{file}: {status}")

if __name__ == "__main__":
    main()