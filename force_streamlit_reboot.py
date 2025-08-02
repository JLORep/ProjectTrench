#!/usr/bin/env python3
"""
Force Streamlit app reboot by making a significant change
"""
import time
import subprocess

print("🔄 Forcing Streamlit app reboot...")

# Read current file
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add a comment to force change
timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
new_content = content.replace(
    '# -*- coding: utf-8 -*-',
    f'# -*- coding: utf-8 -*-\n# FORCE REBOOT: {timestamp}'
)

# Write back
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ Added reboot marker: {timestamp}")

# Commit and push
subprocess.run(['git', 'add', 'streamlit_app.py'])
subprocess.run(['git', 'commit', '-m', f'FORCE REBOOT: Streamlit app at {timestamp}', '--no-verify'])
subprocess.run(['git', 'push'])

print("✅ Changes pushed - Streamlit should reboot")