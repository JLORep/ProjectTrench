# TrenchCoat Pro - Technical Architecture & Code Structure

📁 **Navigation**: [CLAUDE_SESSIONS.md](CLAUDE_SESSIONS.md) ← Previous | Next → [CLAUDE_PROTOCOLS.md](CLAUDE_PROTOCOLS.md)

## 📊 Dashboard Architecture

### Primary Dashboard Files

#### 1. **streamlit_app.py** - Main Entry Point
- **Location:** `C:\trench\streamlit_app.py:1-419`
- **Purpose:** Primary Streamlit application with fallback dashboard system
- **Key Features:**
  - 10-tab interface with full feature set
  - Live database connection to `trench.db` (1,733 coins)
  - Advanced dashboard loading with graceful fallback
  - Real-time coin data display with enhanced metrics

**Key Functions:**
- `get_live_coins_simple()` (line 58): Direct database connection for live coin data
  - **Returns**: `(coins_list, "SUCCESS: X live coins from trench.db")`
  - **Data Format**: `{'Ticker': 'waf', 'Price Gain %': '+180.0%', 'Smart Wallets': '7'}`
- Tab structure (line 137): 10 comprehensive tabs including coin data, database, Solana wallet
- **Status check fix** (line 320): Changed from `== "success"` to `status.startswith("SUCCESS")`
- **Data mapping fix** (lines 334-338): Enhanced format compatibility with fallback support

#### 2. **ultra_premium_dashboard.py** - Advanced Dashboard
- **Location:** `C:\trench\ultra_premium_dashboard.py:1-1300+`
- **Purpose:** Ultra-premium dashboard with Apple/PayPal-level design
- **Key Features:**
  - **10-tab interface** matching streamlit_app.py structure
  - Premium CSS with animations and glassmorphism effects
  - Live database integration with 1,733 coins
  - Real-time performance charts and metrics

**Complete 10-Tab Structure (lines 306-461):**
1. **📊 Live Dashboard** - Real-time market signals and performance
2. **🧠 Advanced Analytics** - AI-powered analysis and insights  
3. **🤖 Model Builder** - ML model configuration interface
4. **⚙ Trading Engine** - Automated trading controls
5. **📡 Telegram Signals** - Real-time signal monitoring
6. **📝 Dev Blog** - Development updates and progress
7. **💎 Solana Wallet** - Solana trading integration
8. **🗄 Coin Data** - Live cryptocurrency analytics
9. **🗃 Database** - Database management interface
10. **🚀 Enrichment** - API enrichment system

## 🏗 ARCHITECTURE PATTERNS & LESSONS LEARNED

### **Dual Dashboard Architecture**
The TrenchCoat Pro system implements a sophisticated dual-dashboard pattern:

#### **Primary Dashboard**: `ultra_premium_dashboard.py`
- **Purpose**: Advanced UI with premium styling and animations
- **Loading Priority**: Attempts to load first via `streamlit_app.py:118-125`
- **Data Integration**: **FIXED** - Now uses `get_live_coins_simple()` for coin data consistency
- **Error Handling**: If fails, gracefully falls back to enhanced fallback dashboard

#### **Fallback Dashboard**: `streamlit_app.py` tabs (lines 132-419)
- **Purpose**: Guaranteed working interface if advanced dashboard fails
- **Features**: Complete 10-tab functionality with live database integration
- **Reliability**: Uses proven data retrieval methods and enhanced error handling

### **Critical Architecture Issues Discovered & Resolved**

#### **Issue Pattern 1: Method Existence Assumptions**
```python
# PROBLEM: Assuming methods exist without verification
coins = self.get_validated_coin_data()  # ❌ Method doesn't exist

# SOLUTION: Method existence verification + external function use
from streamlit_app import get_live_coins_simple
coins, status = get_live_coins_simple()  # ✅ Uses working external function
```

#### **Issue Pattern 2: Data Format Inconsistencies**
```python
# PROBLEM: Different data sources return different key formats
coin.get('ticker')           # Fallback dashboard format
coin.get('Ticker')           # Advanced dashboard format  

# SOLUTION: Enhanced mapping with fallback chains
ticker = coin.get('Ticker', coin.get('ticker', f'COIN_{i+1}'))
price_gain_str = coin.get('Price Gain %', coin.get('price_gain_pct', '0%'))
```

#### **Issue Pattern 3: String vs Numeric Data Handling**
```python
# PROBLEM: Mixed data types from different sources
price_gain = '+471.0%'        # String format
smart_wallets = '396'         # String with commas possible

# SOLUTION: Robust type conversion with error handling
price_gain = float(price_gain_str.replace('%', '').replace('+', ''))
smart_wallets = int(smart_wallets_str.replace(',', ''))
```

## 🗄 Database Architecture

### Core Database Module

#### **src/data/database.py** - Primary Database Interface
- **Location:** `C:\trench\src\data\database.py:1-237`
- **Purpose:** Centralized database operations for all cryptocurrency data

**Key Classes & Methods:**

**`CoinDatabase` Class (line 9):**
- `__init__()` (line 10): Initialize database with schema creation
- `_init_database()` (line 15): Create tables and indexes for optimal performance
- `add_coin()` (line 137): Insert/update coin information
- `add_price_data()` (line 152): Store OHLCV price data
- `get_price_data()` (line 163): Retrieve historical price data as pandas DataFrame
- `add_telegram_signal()` (line 189): Store Telegram signals with metadata
- `get_telegram_signals()` (line 207): Query Telegram signals with filtering

**Database Schema:**
- **coins**: Basic coin information (symbol, name, market_cap, volume_24h, etc.)
- **price_data**: OHLCV data with multiple timeframes
- **indicators**: Technical analysis indicators with parameters
- **telegram_signals**: Signal data from Telegram channels
- **backtests**: Strategy backtesting results
- **market_metrics**: Overall market health data

### Live Database Status
- **File:** `data/trench.db` (319 KB)
- **Records:** 1,733 cryptocurrencies
- **Status:** ✅ Live and operational
- **Connection:** Direct SQLite3 integration

## 🤖 AI Integration - Super Claude System

### **Super Claude System** (`super_claude_system.py`)
- **Location**: `C:\trench\super_claude_system.py`
- **Purpose**: Advanced AI-powered trading intelligence system
- **Version**: 1.0.0
- **Integration Points**: Live Dashboard (Tab 1), Advanced Analytics (Tab 2)

#### **Core Components**:
1. **SuperClaudeConfig**: Configuration dataclass with capabilities, models, thresholds
2. **AIInsight**: Dataclass for AI-generated insights with confidence scores
3. **SuperClaudeSystem**: Main AI system class with analysis methods

#### **Key Features**:
- **Market Analysis**: Analyzes up to 200 coins for opportunities
- **Confidence Scoring**: 0-100% confidence based on multiple factors
- **Sentiment Detection**: BULLISH/BEARISH/NEUTRAL market classification
- **Risk Assessment**: Identifies risk factors and warnings
- **Opportunity Detection**: Finds high-confidence trading opportunities

#### **Analysis Factors**:
```python
# Opportunity scoring based on:
- momentum_score: Price gain analysis (0-100)
- smart_money_score: Wallet activity (0-100)  
- liquidity_score: Liquidity depth (0-100)
- volume_score: Trading volume (0-100)
- composite_score: Average of all factors
- risk_factors: Low liquidity, excessive gains, etc.
```

## 🤖 Trading & Analysis Engine

### Automated Trading System

#### **src/trading/automated_trader.py** - Core Trading Engine
- **Location:** `C:\trench\src\trading\automated_trader.py:1-508`
- **Purpose:** Weaponized automated trading system with microsecond execution

**Key Classes & Methods:**

**`Trade` Class (line 22):** Individual trade tracking with full lifecycle
- Entry/exit prices, P&L calculations, risk management
- Rug detection alerts and performance metrics

**`AutomatedTrader` Class (line 76):** Main trading engine
- `start_trading_engine()` (line 106): Launch concurrent monitoring systems
- `_telegram_signal_processor()` (line 122): Process real-time Telegram signals
- `_evaluate_new_signal()` (line 136): Analyze signals for trading opportunities
- `_execute_trade()` (line 162): Execute trades with position sizing
- `_position_monitor()` (line 222): Monitor all active positions
- `_rug_detection_monitor()` (line 288): Emergency rug pull detection
- `_exit_trade()` (line 314): Exit trades with P&L calculation

### Rug Intelligence System

#### **src/analysis/rug_intelligence.py** - Advanced Rug Detection
- **Location:** `C:\trench\src\analysis\rug_intelligence.py:1-466`
- **Purpose:** Predict and profit from cryptocurrency rug pulls

**Key Classes & Methods:**

**`TokenLifecycle` Class (line 21):** Complete token analysis from launch to rug
- Price action tracking, volume analysis, wallet monitoring
- Performance metrics and risk factors

**`RugIntelligenceEngine` Class (line 66):** Main analysis engine
- `analyze_historical_rugs()` (line 79): Pattern extraction from historical data
- `analyze_new_token()` (line 226): Real-time token analysis for profit potential
- `_make_trading_decision()` (line 357): AI-powered trading decisions
- `real_time_rug_detection()` (line 405): Live rug detection for active positions

## 📡 Telegram Integration

### Signal Monitoring System

#### **src/telegram/telegram_monitor.py** - Telegram Signal Processing
- **Location:** `C:\trench\src\telegram\telegram_monitor.py:1-353`
- **Purpose:** Real-time monitoring and parsing of Telegram trading signals

**Key Classes & Methods:**

**`CoinSignal` Class (line 15):** Structured signal data
- Ticker, contract address, signal type, prices, confidence scoring

**`SignalPattern` Class (line 32):** Advanced pattern matching
- Sophisticated regex patterns for buy/sell signals
- Contract address extraction, price parsing, target identification

**`TelegramSignalMonitor` Class (line 71):** Main monitoring system
- `start()` (line 81): Initialize Telegram client with channels
- `add_channel()` (line 98): Add new channels to monitoring list
- `_handle_new_message()` (line 116): Process incoming messages
- `_parse_message()` (line 155): Extract signals using pattern matching
- `_calculate_confidence()` (line 278): AI-powered confidence scoring

## 📈 Data Processing Pipeline

### Enrichment System (17 API Sources)

#### **comprehensive_coin_history.py** - Historical Tracking
- **Purpose:** Complete historical tracking system for any coin
- **Database:** SQLite with 5 tables for comprehensive data storage
- **Features:** Multi-tier API fallback, rate limiting, batch processing

#### **free_apis.md** - API Documentation
- **17 API Sources:** Expanded from 8 to 17 comprehensive sources
- **Coverage:** Price data, on-chain metrics, social sentiment, security analysis
- **Rate Limits:** Documented for each API with fallback strategies

## Continue Reading

👉 **Next Section**: [CLAUDE_PROTOCOLS.md](CLAUDE_PROTOCOLS.md) - Development protocols and best practices

*Last updated: 2025-08-02 00:07 - Architecture documentation extracted and organized*