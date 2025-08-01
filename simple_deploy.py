#!/usr/bin/env python3
"""
Simple Deployment Package Creator
"""
import shutil
import zipfile
from pathlib import Path

def create_simple_package():
    # Essential files
    files = [
        "ultra_premium_dashboard.py",
        "premium_components.py", 
        "streamlit_app.py",
        "requirements.txt",
        "MISSION_STATEMENT.md",
        "check_token.py"
    ]
    
    # Create ZIP
    with zipfile.ZipFile("TrenchCoat_Pro.zip", 'w') as zipf:
        for file in files:
            if Path(file).exists():
                zipf.write(file)
                print(f"Added: {file}")
        
        # Add .streamlit folder if exists
        if Path(".streamlit").exists():
            for item in Path(".streamlit").rglob("*"):
                if item.is_file():
                    zipf.write(item)
                    print(f"Added: {item}")
    
    print("Package created: TrenchCoat_Pro.zip")

if __name__ == "__main__":
    create_simple_package()