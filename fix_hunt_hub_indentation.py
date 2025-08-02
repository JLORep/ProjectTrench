#!/usr/bin/env python3
"""Fix Hunt Hub indentation after adding try block"""

# Read the file
with open('memecoin_hunt_hub_ui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix indentation from line 185 onwards (after CSS block)
fixed_lines = []
for i, line in enumerate(lines):
    if i < 185:  # Keep everything before line 185 as is
        fixed_lines.append(line)
    elif i >= 185 and i < 308:  # Lines that need extra indentation
        if line.strip():  # Only indent non-empty lines
            # Add 4 spaces to existing indentation
            fixed_lines.append('    ' + line)
        else:
            fixed_lines.append(line)
    else:  # Keep everything after as is
        fixed_lines.append(line)

# Write back
with open('memecoin_hunt_hub_ui.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Fixed Hunt Hub indentation")