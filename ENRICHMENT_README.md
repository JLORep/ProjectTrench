# 🔮 TrenchCoat Crypto Data Enrichment System

A comprehensive, production-ready system for enriching cryptocurrency data using **multiple free APIs** with intelligent rate limiting, error recovery, and beautiful progress tracking.

## 🚀 Features

### **Multi-API Integration**
- **CoinGecko** - Market data, prices, and metadata (100 requests/minute)
- **DexScreener** - DEX trading data and pair information
- **Jupiter** - Solana price aggregation and routing data  
- **Solscan** - On-chain Solana token and holder information
- **CryptoCompare** - Price data and market statistics
- **Messari** - Fundamental analysis and metrics

### **Smart Enrichment Engine**
- ⚡ **Concurrent processing** with configurable rate limiting
- 🔄 **Automatic retry logic** with exponential backoff
- 📊 **Data quality scoring** and source prioritization
- 🎯 **Priority-based processing** (high/medium/low)
- 💾 **Intelligent caching** to minimize API calls
- 📈 **Real-time progress tracking** with Rich CLI

### **Data Quality & Validation**
- ✅ **Multi-source price consistency** checking
- 🎯 **Enrichment scoring** (0-1) based on data completeness
- 🔍 **Contract address validation** for Solana tokens
- 📝 **Comprehensive metadata** storage with timestamps

## 📦 Installation

### 1. Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install all dependencies
pip install -r requirements.txt
```

### 2. Setup Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional - many APIs work without keys)
# COINGECKO_API_KEY=your_key_here  # Optional for higher rate limits
# COINMARKETCAP_API_KEY=your_key_here  # Optional
```

### 3. Test the System
```bash
# Run test suite to verify everything works
python test_enrichment.py
```

## 🎯 Usage

### **Enrich All Coins**
```bash
# Enrich all coins in your database
python scripts/enrich_coins.py --all

# Limit to 100 coins for testing
python scripts/enrich_coins.py --all --max-coins 100

# Only high-priority coins (recently added, high market cap)
python scripts/enrich_coins.py --all --priority 1
```

### **Enrich Specific Coins**
```bash
# Enrich specific tokens by contract address
python scripts/enrich_coins.py --addresses EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R

# Mix of contract addresses and symbols
python scripts/enrich_coins.py --addresses BTC ETH SOL
```

### **Generate Reports**
```bash
# Generate enrichment report
python scripts/enrich_coins.py --report

# Save report to file
python scripts/enrich_coins.py --report --output enrichment_report.json
```

## 📊 Real-time Progress Tracking

The enrichment script provides beautiful real-time progress tracking:

```
┌─ 🔮 TrenchCoat Coin Enrichment Engine ─┐
│    Powered by 6 Free APIs              │
└─────────────────────────────────────────┘

┌─ Progress ──────────────────────────────┐   ┌─ Live Statistics ─────┐
│                                        │   │ 🎯 Success Rate  92.5% │
│ 📊 Total Coins: 1,234                 │   │ ⚡ Speed        15.2/min │
│ ✅ Processed: 856                     │   │ ⏰ ETA           24.8m  │
│ 🎯 Successful: 792                    │   │ 🔥 Status      🟢 Active │
│ ❌ Failed: 64                         │   └───────────────────────┘
│                                        │
│ 📈 Success Rate: 92.5%                │
│ ⏱  Time Elapsed: 0:56:32             │
│ 🚀 Rate: 15.2 coins/minute            │
│                                        │
│ 🔋 [████████████████████░░░░░] 69.3%  │
└────────────────────────────────────────┘

*Last updated: 2025-08-02 16:42 - Complete Dev Blog Integration*
```

## 🗄 Database Schema

The enrichment system extends your existing `coins.db` with:

### **Enhanced Coins Table**
```sql
-- Existing + enriched fields
market_cap REAL,
volume_24h REAL,
circulating_supply REAL,
max_supply REAL,
updated_at TIMESTAMP
```

### **New Metadata Table**
```sql
CREATE TABLE coin_metadata (
    coin_id INTEGER PRIMARY KEY,
    metadata JSON,  -- Full enrichment data
    updated_at TIMESTAMP,
    FOREIGN KEY (coin_id) REFERENCES coins(id)
);
```

### **Sample Enriched Data**
```json
{
  "contract_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "symbol": "USDC",
  "price": 1.0001,
  "price_change_24h": 0.01,
  "volume_24h": 28500000,
  "market_cap": 50000000000,
  "liquidity": 15000000,
  "total_holders": 145678,
  "top_10_concentration": 23.5,
  "data_sources": ["dexscreener", "jupiter", "solscan"],
  "enrichment_score": 0.95,
  "data_quality": {
    "has_price": true,
    "has_volume": true,
    "has_liquidity": true,
    "price_consistency": true
  }
}
```

## ⚙ Configuration

### **Rate Limiting**
Each API provider has intelligent rate limiting:
- **CoinGecko**: 1.5 req/sec (90/minute, leaves headroom)
- **DexScreener**: 5 req/sec (respectful usage)
- **Jupiter**: 10 req/sec (very permissive)
- **Solscan**: 5 req/sec
- **CryptoCompare**: 5 req/sec

### **Retry Logic**
- **Max retries**: 3 attempts per coin
- **Exponential backoff**: 2^attempt seconds delay
- **Smart failure handling**: Temporary vs permanent failures

### **Priority System**
1. **High Priority**: New coins, no recent data, high market cap
2. **Medium Priority**: Updated 1-6 hours ago
3. **Low Priority**: Recently updated (< 1 hour)

## 📈 Performance Optimization

### **Concurrent Processing**
- Default: 5 concurrent API calls
- Configurable via `MasterEnricher(max_concurrent=N)`
- Balanced for rate limits and performance

### **Intelligent Caching**
- **5-minute TTL** for API responses  
- **Memory-based caching** during session
- **Reduces redundant API calls**

### **Batch Processing**
- **Batches of 10 coins** for memory management
- **Progress checkpointing** for long runs
- **Graceful interruption** handling

## 🔧 Advanced Usage

### **Programmatic Access**
```python
from src.data.master_enricher import MasterEnricher

# Create enricher
enricher = MasterEnricher("path/to/coins.db")

# Enrich specific coins
stats = await enricher.enrich_specific_coins([
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "So11111111111111111111111111111111111111112"   # SOL
])

# Generate report
report = await enricher.get_enrichment_report()
```

### **Custom API Integration**
```python
from src.data.free_api_providers import FreeAPIProviders

async with FreeAPIProviders() as api:
    # Get data from specific source
    dex_data = await api.get_dexscreener_data(contract_address)
    
    # Get comprehensive data from all sources
    full_data = await api.get_comprehensive_data(address, symbol)
```

## 🚨 Error Handling

### **Common Issues & Solutions**

**❌ Rate Limited (429 errors)**
- System automatically handles with exponential backoff
- Consider reducing `max_concurrent` if persistent

**❌ No data for contract address**
- Verify contract address is correct
- Some tokens may not be listed on all exchanges

**❌ Database locked errors**
- Ensure no other processes are using the database
- Check file permissions

**❌ Network timeouts**
- System retries automatically
- Check internet connection stability

## 📊 Monitoring & Analytics

### **Success Metrics**
- **Enrichment Score**: 0-1 based on data completeness
- **Source Coverage**: Number of APIs providing data
- **Price Consistency**: Cross-API price validation
- **Processing Rate**: Coins per minute throughput

### **Quality Indicators**
- **High Quality** (Score > 0.8): Price, volume, liquidity, holders
- **Medium Quality** (Score > 0.6): Price + some additional data
- **Low Quality** (Score < 0.6): Limited data available

## 🎯 Master Plan Integration

This enrichment system is designed to support your master plan:

1. **📊 Rich Data Foundation** - Multiple data sources ensure comprehensive coverage
2. **🤖 Real-time Updates** - Supports continuous enrichment for live analysis  
3. **📈 Modeling Ready** - Clean, validated data perfect for ML models
4. **🎮 Game Theory** - Multi-source data enables market participant analysis
5. **☁ Azure Deployment** - Designed for cloud scalability

## 🔮 What's Next?

With your coins.db now richly enriched, you can:

1. **Run Advanced Strategies** - Use the momentum and other trading strategies
2. **Deploy Dashboards** - Visualize your enriched data with Streamlit
3. **Model Market Behavior** - Apply game theory validation
4. **Scale to Azure** - Deploy the full system to the cloud

---

**Ready to enrich your data?** Start with:
```bash
python scripts/enrich_coins.py --all --max-coins 50
```

🚀 **Happy enriching!**