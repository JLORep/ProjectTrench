#!/usr/bin/env python3
"""Fix any syntax issues in blog system"""

# Read the file
with open('comprehensive_dev_blog_system.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check around line 188
print("Lines 185-195:")
for i in range(185, 195):
    if i < len(lines):
        print(f"{i}: {repr(lines[i-1])}")
        
# Look for any incomplete try blocks
incomplete_tries = []
for i, line in enumerate(lines, 1):
    if line.strip() == "try:":
        # Check if next line is properly indented
        if i < len(lines):
            next_line = lines[i]
            if not next_line.strip() or not next_line.startswith(' '):
                incomplete_tries.append(i)
                
if incomplete_tries:
    print(f"\nFound incomplete try blocks at lines: {incomplete_tries}")
else:
    print("\nNo incomplete try blocks found")