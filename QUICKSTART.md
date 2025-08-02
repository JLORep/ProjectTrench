# 🚀 TrenchCoat Pro - Quick Start Guide

Get TrenchCoat Pro running in 5 minutes or less!

## 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.11 or higher** ([Download Python](https://python.org))
- **Git** ([Download Git](https://git-scm.com))
- **2GB free disk space**
- **Internet connection** for API access

## 🏃 Quick Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/JLORep/ProjectTrench.git
cd ProjectTrench
```

### Step 2: Set Up Python Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
streamlit run streamlit_app.py
```

Your browser should automatically open to `http://localhost:8501`

## 🎉 That's It! You're Running!

## 🔧 Optional Configuration

### Add API Keys (For Enhanced Features)

1. Create a `.streamlit` folder in the project root
2. Create a `secrets.toml` file:

```bash
mkdir .streamlit
```

3. Add your API keys (optional):

```toml
# .streamlit/secrets.toml
[api_keys]
birdeye = "your_birdeye_api_key"
dexscreener = "your_dexscreener_key"

[discord]
webhook_url = "your_discord_webhook"
```

## 🎯 What You Can Do Now

### 1. **Explore the Dashboard**
- Click through the 12 tabs
- View live cryptocurrency data
- Check out the Hunt Hub for memecoin sniping
- Explore Alpha Radar for trading signals

### 2. **View Sample Data**
- The app comes with 1,733 pre-loaded coins
- All features work without API keys
- Enhanced data requires API configuration

### 3. **Try Super Claude AI**
- Navigate to the Super Claude tab
- Try commands like `/analyze BTC`
- Explore the 9 AI personas

## 🆘 Troubleshooting

### Common Issues:

**1. "Module not found" errors**
```bash
pip install -r requirements.txt --force-reinstall
```

**2. Port already in use**
```bash
streamlit run streamlit_app.py --server.port 8502
```

**3. Database not found**
```bash
# The database should be at data/trench.db
ls data/trench.db  # Should show the file
```

**4. Streamlit won't start**
```bash
# Check Python version
python --version  # Should be 3.11+

# Try direct Python
python -m streamlit run streamlit_app.py
```

## 🚀 Next Steps

1. **Deploy to Cloud**: See [Deployment Guide](DEPLOYMENT.md)
2. **Add More APIs**: See [API Integration Guide](API_GUIDE.md)
3. **Customize Features**: See [Architecture Overview](ARCHITECTURE.md)
4. **Join Community**: [Discord Server](https://discord.gg/trenchcoat)

## 📊 Quick Feature Overview

| Tab | Feature | Description |
|-----|---------|-------------|
| 🚀 Dashboard | Market Overview | Real-time crypto market stats |
| 💎 Coins | Database Browser | Browse 1,733+ cryptocurrencies |
| 🎯 Hunt Hub | Memecoin Sniper | Detect new token launches |
| 📡 Alpha Radar | Signal Feed | AI-powered trading signals |
| 🛡️ Security | Threat Monitor | Security alerts and monitoring |
| 🔧 Enrichment | Data Pipeline | 17 API sources integration |
| 🤖 Super Claude | AI Assistant | Trading intelligence system |
| 📱 Blog | Dev Updates | Latest features and changes |
| 📊 Monitoring | System Health | Performance metrics |
| ⚙️ System | Configuration | Database and settings |
| 🧪 Beta | New Features | Experimental features |
| ✨ Features | Showcase | Complete feature overview |

## 💡 Pro Tips

1. **Performance**: The app caches data for 5 minutes to reduce API calls
2. **Navigation**: Use keyboard shortcuts (1-9) to switch tabs quickly
3. **Data**: Export coin data using the download button in the Coins tab
4. **Monitoring**: Check the System tab for database health

## 🎊 Welcome to TrenchCoat Pro!

You're now part of the elite crypto trading intelligence community. Happy trading!

---

**Need Help?** 
- 📖 [Full Documentation](README.md)
- 💬 [Discord Community](https://discord.gg/trenchcoat)
- 📧 [Email Support](mailto:support@trenchcoatpro.com)