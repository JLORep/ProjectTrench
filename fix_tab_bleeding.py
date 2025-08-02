#!/usr/bin/env python3
"""
Fix tab bleeding security vulnerability in Streamlit dashboard
"""

# Read the current streamlit_app.py
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add CSS isolation to prevent tab bleeding
css_fix = '''
<style>
/* SECURITY FIX: Prevent tab bleeding and content exposure */
.stTabs [data-baseweb="tab-list"] {
    isolation: isolate;
}

.stTabs [data-baseweb="tab-panel"] {
    isolation: isolate;
    overflow: hidden;
}

/* Ensure each tab's content is properly contained */
.stTabs > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    isolation: isolate;
    contain: layout style;
}

/* Prevent CSS from one tab affecting others */
.tab-content {
    isolation: isolate;
    contain: layout style paint;
}
</style>
'''

# Find where to insert the CSS fix (after the first CSS block)
insert_position = content.find('</style>') + len('</style>')

if insert_position > 6:  # Found a CSS block
    # Insert the tab bleeding fix
    fixed_content = content[:insert_position] + '\\n\\n' + css_fix + '\\n' + content[insert_position:]
    
    # Write the fixed file
    with open('streamlit_app.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Fixed tab bleeding vulnerability")
else:
    print("❌ Could not find CSS insertion point")