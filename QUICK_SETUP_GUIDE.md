# 🚀 TrenchCoat Pro - Quick Setup Guide

## Step 1: Install GitHub CLI (Manual)

### Option A: Download from Website
1. Go to: https://cli.github.com/
2. Download the Windows installer
3. Run the installer

### Option B: Use PowerShell (as Administrator)
```powershell
# Install using Chocolatey
choco install gh

# OR install using Scoop
scoop install gh
```

## Step 2: Authenticate with GitHub

After installing GitHub CLI:

```bash
# Login with your passkey
gh auth login

# Choose:
# - GitHub.com
# - HTTPS  
# - Yes (authenticate Git)
# - Login with a web browser (will use your passkey)
```

## Step 3: Push Your Ultra-Premium Dashboard

```bash
# Add all files
git add -A

# Commit everything
git commit -m "feat: Ultra-premium dashboard v1.0.0 - Apple-level design with live animations"

# Push to GitHub
git push -u origin master
```

## Step 4: Set Up Repository Features

```bash
# Create labels
gh label create "🚀 enhancement" --color "10b981" --description "New feature"
gh label create "🐛 bug" --color "ef4444" --description "Bug fix"
gh label create "💎 premium" --color "8b5cf6" --description "Premium feature"

# Create first release
gh release create v1.0.0 --title "TrenchCoat Pro v1.0.0" --notes "Ultra-premium dashboard with Apple-level design"
```

## Step 5: Deploy to Streamlit Cloud

1. Go to: https://share.streamlit.io
2. Sign in with GitHub
3. Connect repository: **JLORep/ProjectTrench**
4. Set main file: **ultra_premium_dashboard.py**
5. Click "Deploy!"

## Alternative: Quick Manual Push

If GitHub CLI is being difficult, use Git directly:

```bash
# Set up remote (if not already done)
git remote add origin https://github.com/JLORep/ProjectTrench.git

# Push code
git push -u origin master
```

You'll be prompted for:
- **Username**: `JLORep`
- **Password**: Use a Personal Access Token from https://github.com/settings/tokens

## What You'll Get:

✅ **Repository**: https://github.com/JLORep/ProjectTrench  
✅ **Ultra-Premium Dashboard**: Live animations and Apple-level design  
✅ **Streamlit Cloud**: Public demo URL  
✅ **Professional Setup**: Issue labels, releases, documentation  

## Your Ultra-Premium Features:

🎨 **Design**: Apple/PayPal-level UI with glassmorphism  
💰 **Live Metrics**: Real-time profit tracking with glowing animations  
🪙 **Coin Feed**: Animated processing from Discovery → Trading  
🤖 **AI Suggestions**: Claude-powered improvement recommendations  
📊 **3D Charts**: Portfolio visualization and performance heatmaps  
⚡ **Smooth Animations**: Professional transitions and hover effects  

## Quick Test:

Run locally right now:
```bash
streamlit run ultra_premium_dashboard.py
```

The dashboard will open with live animations and premium design! 🎉