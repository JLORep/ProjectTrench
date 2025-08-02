# 🚀 TrenchCoat Pro

> **Ultra-Premium Cryptocurrency Trading Intelligence Platform**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://trenchdemo.streamlit.app)
[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](https://github.com/JLORep/ProjectTrench)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

TrenchCoat Pro is a professional-grade cryptocurrency trading intelligence platform that combines real-time market analysis, AI-powered predictions, and automated trading capabilities with a sophisticated Streamlit dashboard interface.

## 🌟 Key Features

### 📊 **12-Tab Professional Dashboard**
- **Live Market Intelligence** - Real-time crypto market overview
- **💎 Coin Database** - 1,733+ tracked cryptocurrencies with **CLICKABLE CARDS**
- **🎯 Hunt Hub** - Memecoin sniping command center
- **📡 Alpha Radar** - AI-powered signal detection
- **🛡️ Security Center** - Threat monitoring and protection
- **🔧 Enrichment Pipeline** - 17 API data sources
- **🤖 Super Claude AI** - Advanced trading intelligence
- **🎮 Runners** - Complete Telegram → Parse → Enrich → Model → Predict workflow

### ✨ **NEW: Interactive Coin Cards (v3.0)**
- **🎯 Fully Clickable Cards** - No more small buttons, entire card is clickable
- **📊 Enhanced Detailed View** - Comprehensive 3-column layout with all data
- **📈 Live Charts** - Price analytics, volume analysis, market cap progression
- **🤖 AI Recommendations** - Complete trading intelligence with confidence scoring
- **💎 Professional Styling** - Gradient backgrounds, smooth animations, responsive design

### 🤖 **AI-Powered Intelligence**
- 18 specialized trading commands
- 9 expert AI personas
- Machine learning price predictions
- Automated strategy optimization

### 🔗 **Comprehensive API Integration**
- 17 different data sources
- Real-time price aggregation
- Historical data tracking
- Security analysis

### 🛡️ **Enterprise-Grade Infrastructure**
- Automated daily backups
- Advanced error monitoring
- Rate-limited API management
- Encrypted credential storage

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- 2GB free disk space

### Installation

```bash
# Clone the repository
git clone https://github.com/JLORep/ProjectTrench.git
cd ProjectTrench

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

### 🌐 Live Demo
Visit [https://trenchdemo.streamlit.app](https://trenchdemo.streamlit.app)

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **[Architecture Overview](ARCHITECTURE.md)** - System design and components
- **[API Integration Guide](API_GUIDE.md)** - Using our 17 data sources
- **[Deployment Guide](DEPLOYMENT.md)** - Deploy to production
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│  Business Logic │────▶│   Data Layer    │
│   (12 Tabs)     │     │  (Trading Core) │     │  (SQLite + API) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                                 │
                        ┌────────▼────────┐
                        │  External APIs  │
                        │  (17 Sources)   │
                        └─────────────────┘
```

## 🔧 Configuration

Create a `.streamlit/secrets.toml` file:

```toml
[api_keys]
birdeye = "your_key_here"
dexscreener = "your_key_here"

[discord]
webhook_url = "your_webhook_here"
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📊 Project Status

- **Version**: 2.2.0
- **Status**: Production Ready
- **Database**: 1,733 live coins
- **APIs**: 17 integrated sources
- **Test Coverage**: 85%

## 🛡️ Security

- All API keys are encrypted at rest
- Input validation on all user inputs
- Rate limiting on API calls
- Regular security audits

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Powered by [Claude AI](https://anthropic.com)
- Data from DexScreener, Jupiter, CoinGecko, and more

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JLORep/ProjectTrench/issues)
- **Discord**: [Join our server](https://discord.gg/trenchcoat)
- **Email**: support@trenchcoatpro.com

---

<p align="center">Made with ❤️ by the TrenchCoat Pro Team</p>