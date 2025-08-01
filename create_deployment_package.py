#!/usr/bin/env python3
"""
Create Clean Deployment Package for TrenchCoat Pro
Creates ZIP file for manual GitHub upload
"""
import os
import shutil
import zipfile
from pathlib import Path

def create_deployment_package():
    """Create clean deployment package"""
    
    print("Creating TrenchCoat Pro deployment package...")
    
    # Essential files for deployment
    essential_files = [
        "ultra_premium_dashboard.py",
        "premium_components.py", 
        "streamlit_app.py",
        "app.py",
        "requirements.txt",
        "MISSION_STATEMENT.md",
        "PROGRESS_LOG.md",
        "DEPLOYMENT_STATUS.md",
        "check_token.py",
        "token_renewal_system.bat",
        "GITHUB_TOKEN_GUIDE.md"
    ]
    
    # Essential directories
    essential_dirs = [
        ".streamlit",
        "tests",
        "src"
    ]
    
    # Create deployment directory
    deploy_dir = Path("deployment_package")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Copy essential files
    copied_files = 0
    for file_name in essential_files:
        file_path = Path(file_name)
        if file_path.exists():
            shutil.copy2(file_path, deploy_dir / file_name)
            copied_files += 1
            print(f"✅ Copied: {file_name}")
        else:
            print(f"⚠️ Missing: {file_name}")
    
    # Copy essential directories
    copied_dirs = 0
    for dir_name in essential_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.copytree(dir_path, deploy_dir / dir_name)
            copied_dirs += 1
            print(f"✅ Copied directory: {dir_name}")
        else:
            print(f"⚠️ Missing directory: {dir_name}")
    
    # Create README for deployment
    readme_content = """# TrenchCoat Pro - Ultra Premium Cryptocurrency Trading Dashboard

## 🚀 Quick Start

### Local Testing
```bash
pip install -r requirements.txt
streamlit run ultra_premium_dashboard.py
```

### Streamlit Cloud Deployment
1. Upload these files to your GitHub repository
2. Go to: https://share.streamlit.io
3. Repository: JLORep/ProjectTrench
4. Main file: streamlit_app.py
5. Deploy!

## ✨ Features
- Apple/PayPal-level design with glassmorphism effects
- Live coin processing animations
- Real-time performance metrics
- AI-powered suggestions from Claude
- 3D portfolio visualizations
- Professional dark theme

## 🔧 Architecture
- Ultra-premium dashboard with live animations
- Comprehensive API integrations (6+ sources)
- Advanced risk management systems
- Token renewal management system
- Professional documentation

Ready for production deployment! 🎉
"""
    
    with open(deploy_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    # Create ZIP package
    zip_path = Path("TrenchCoat_Pro_v1.0.0.zip")
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(deploy_dir)
                zipf.write(file_path, arc_path)
                
    # Clean up temp directory
    shutil.rmtree(deploy_dir)
    
    print(f"\n✅ Deployment package created: {zip_path}")
    print(f"📦 Files included: {copied_files}")
    print(f"📁 Directories included: {copied_dirs}")
    print(f"💾 Package size: {zip_path.stat().st_size // 1024} KB")
    
    return zip_path

def create_manual_upload_guide():
    """Create manual upload instructions"""
    
    guide = """# 🚀 TrenchCoat Pro - Manual Upload Guide

## Your Token Status ✅
- **Token**: Working with full permissions
- **Expires**: October 29, 2025 (89 days remaining)
- **Status**: Ready for deployment

## Quick Upload to GitHub

### Option 1: Web Upload (Recommended)
1. **Go to**: https://github.com/JLORep/ProjectTrench
2. **Click**: "Add file" → "Upload files"
3. **Drag and drop**: TrenchCoat_Pro_v1.0.0.zip
4. **Or upload individual files**:
   - ultra_premium_dashboard.py
   - streamlit_app.py  
   - requirements.txt
   - .streamlit/config.toml
5. **Commit message**: "feat: TrenchCoat Pro v1.0.0 - Ultra-premium dashboard"
6. **Click**: "Commit changes"

### Option 2: Git Command Line
```bash
# Extract ZIP contents to fresh directory
# Then:
git init
git remote add origin https://github.com/JLORep/ProjectTrench.git
git add -A
git commit -m "feat: TrenchCoat Pro v1.0.0 - Ultra-premium dashboard"
git push -u origin master
```

## Deploy to Streamlit Cloud

1. **Go to**: https://share.streamlit.io
2. **Sign in** with GitHub
3. **New app**:
   - Repository: **JLORep/ProjectTrench**
   - Branch: **master**
   - Main file: **streamlit_app.py**
4. **Deploy!**

## Expected Results

**GitHub Repository**: https://github.com/JLORep/ProjectTrench
**Live Demo**: https://trenchcoat-pro.streamlit.app (after deployment)

## ✨ Your Ultra-Premium Features

- **Apple-level Design**: Glassmorphism effects with dark theme
- **Live Animations**: Real-time coin processing and smooth transitions  
- **AI Integration**: Claude-powered suggestions and optimizations
- **Performance Tracking**: Live profit metrics with glowing indicators
- **Professional UI**: 3D charts, heatmaps, and advanced visualizations

## 🔧 Token Management

Your token renewal system is ready:
- **Check status**: `python check_token.py`
- **Automated reminders**: Every 30, 14, 7, 3, and 1 days before expiry
- **Renewal date**: October 29, 2025

## Support

Everything is ready for deployment! The ultra-premium dashboard will look incredible on Streamlit Cloud.

**Next Step**: Upload to GitHub and deploy to Streamlit Cloud! 🎉
"""
    
    with open("MANUAL_UPLOAD_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("✅ Created MANUAL_UPLOAD_GUIDE.md")

def main():
    """Create deployment package and guide"""
    zip_path = create_deployment_package()
    create_manual_upload_guide()
    
    print("\n" + "="*60)
    print("🎉 TrenchCoat Pro - Deployment Ready!")
    print("="*60)
    print(f"📦 Package: {zip_path}")
    print("📋 Guide: MANUAL_UPLOAD_GUIDE.md")
    print("\n🚀 Next Steps:")
    print("1. Upload TrenchCoat_Pro_v1.0.0.zip to GitHub")
    print("2. Deploy to Streamlit Cloud")
    print("3. Your ultra-premium dashboard will be live!")
    print("\n✨ Features ready:")
    print("- Apple-level design with live animations")
    print("- Real-time performance tracking")  
    print("- AI-powered suggestions")
    print("- Token renewal management")
    print("- Professional documentation")

if __name__ == "__main__":
    main()