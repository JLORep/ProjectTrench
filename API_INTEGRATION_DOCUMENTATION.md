# 🔌 TrenchCoat Pro - API Integration Documentation

## Overview
TrenchCoat Pro uses multiple cryptocurrency data APIs to ensure maximum data coverage and reliability. The system implements intelligent fallback mechanisms, rate limiting, and caching to optimize performance.

---

## 📊 Supported APIs

### 1. **DexScreener** (Primary)
- **Base URL**: `https://api.dexscreener.com/latest/dex`
- **Rate Limit**: 10 requests/second
- **Priority**: 2
- **Best For**: DEX tokens, real-time prices, liquidity data
- **No API Key Required**: ✅

**Endpoints**:
```
GET /tokens/{address} - Get token data by contract address
GET /search?q={query} - Search for pairs
```

**Data Available**:
- Price (USD)
- Liquidity
- Market Cap
- 24h Volume
- Price Changes (5m, 1h, 6h, 24h)
- Trading pairs

### 2. **Birdeye** (High Priority)
- **Base URL**: `https://public-api.birdeye.so`
- **Rate Limit**: 5 requests/second
- **Priority**: 1
- **Best For**: Solana tokens, holder data, on-chain metrics
- **API Key**: Optional (higher limits with key)

**Endpoints**:
```
GET /public/token_overview?address={address} - Token overview
GET /public/token_holders?address={address} - Holder distribution
```

**Data Available**:
- Price & Market Cap
- Holder count & distribution
- Liquidity pools
- Trading volume
- Historical data

### 3. **Jupiter** (Price Aggregator)
- **Base URL**: `https://price.jup.ag/v4`
- **Rate Limit**: 20 requests/second
- **Priority**: 3
- **Best For**: Solana token prices, aggregated from multiple DEXs
- **No API Key Required**: ✅

**Endpoints**:
```
GET /price?ids={token_address} - Get token price
```

**Data Available**:
- Aggregated price
- Price confidence
- Last update time

### 4. **CoinGecko** (Comprehensive)
- **Base URL**: `https://api.coingecko.com/api/v3`
- **Rate Limit**: 10 requests/second (free tier)
- **Priority**: 4
- **Best For**: Established tokens, historical data, global metrics
- **No API Key Required**: ✅ (for basic usage)

**Endpoints**:
```
GET /simple/price?ids={coin_id}&vs_currencies=usd
GET /coins/solana/contract/{contract_address}
GET /coins/markets?vs_currency=usd
```

**Data Available**:
- Price in multiple currencies
- Market cap
- 24h volume
- Price changes
- ATH/ATL data
- Circulating supply

### 5. **CoinMarketCap** (Professional)
- **Base URL**: `https://pro-api.coinmarketcap.com/v1`
- **Rate Limit**: 3 requests/second (free tier)
- **Priority**: 5
- **Best For**: Professional data, global rankings
- **API Key Required**: ✅

**Endpoints**:
```
GET /cryptocurrency/quotes/latest?symbol={symbol}
GET /cryptocurrency/map
```

**Data Available**:
- Professional market data
- Global rankings
- Detailed supply metrics
- Tags and categories

---

## 🔄 Data Enrichment Pipeline

### Priority-Based Fallback Strategy

```python
# Enrichment order (by priority):
1. Birdeye      → Best for Solana, most comprehensive
2. DexScreener  → Real-time DEX data, no API key needed
3. Jupiter      → Price aggregation, very reliable
4. CoinGecko    → Fallback for established tokens
5. CoinMarketCap → Last resort, requires API key
```

### Implementation Example

```python
async def enrich_coin_multi_source(self, ticker: str, contract_address: str):
    """Try multiple APIs in priority order"""
    
    # Try each API in order
    for provider in self.providers:
        try:
            data = await self.fetch_from_provider(provider, contract_address)
            if data:
                return self.normalize_data(provider.name, data)
        except Exception as e:
            logger.debug(f"{provider.name} failed: {e}")
            continue
    
    return None  # All APIs failed
```

---

## 📝 Data Normalization

All API responses are normalized to a standard format:

```python
@dataclass
class EnrichedCoinData:
    ticker: str
    contract_address: str
    price_usd: float
    liquidity_usd: float
    market_cap: float
    volume_24h: float
    holders: int
    price_change_24h: float
    last_updated: str
    data_source: str
```

### Mapping Examples

**DexScreener → Standard Format**:
```python
{
    "priceUsd": "0.001234",          → price_usd
    "liquidity": {"usd": 50000},     → liquidity_usd
    "marketCap": 1000000,            → market_cap
    "volume": {"h24": 25000}         → volume_24h
}
```

**Birdeye → Standard Format**:
```python
{
    "price": 0.001234,               → price_usd
    "liquidity": 50000,              → liquidity_usd
    "mc": 1000000,                   → market_cap
    "v24hUSD": 25000,                → volume_24h
    "holder": 1500                   → holders
}
```

---

## ⚡ Rate Limiting

Each API has its own rate limiter to prevent hitting limits:

```python
class RateLimiter:
    def __init__(self, rate: float):
        self.rate = rate  # requests per second
        self.last_call = 0
        
    async def acquire(self):
        # Ensures proper spacing between requests
        time_since_last = time.time() - self.last_call
        if time_since_last < 1.0 / self.rate:
            await asyncio.sleep(1.0 / self.rate - time_since_last)
        self.last_call = time.time()
```

---

## 🗄️ Database Integration

Enriched data is stored in the `coins` table:

```sql
UPDATE coins 
SET axiom_price = ?,      -- Current price in USD
    liquidity = ?,        -- Liquidity in USD
    axiom_mc = ?,         -- Market cap
    axiom_volume = ?,     -- 24h volume
    smart_wallets = ?     -- Holder count (if available)
WHERE ca = ?              -- Contract address
```

---

## 🚀 Usage Examples

### 1. Single Coin Enrichment
```python
enricher = MultiAPIEnricher()
data = await enricher.enrich_coin_multi_source("$BONK", "DezXAZ8...")
```

### 2. Batch Enrichment
```python
coins = [("$BONK", "DezXAZ8..."), ("$WIF", "EKpQGS...")]
await enricher.enrich_batch(coins, batch_size=5)
```

### 3. Full Database Enrichment
```python
async with MultiAPIEnricher() as enricher:
    await enricher.run_enrichment(limit=1000)
```

---

## 📊 Performance Metrics

### Typical Success Rates
- **DexScreener**: 60-70% (new tokens)
- **Birdeye**: 50-60% (Solana tokens)
- **Jupiter**: 40-50% (price only)
- **CoinGecko**: 20-30% (established tokens)
- **Combined**: 80-90% coverage

### Processing Speed
- **Sequential**: ~1 coin/second
- **Batch (5 concurrent)**: ~3-4 coins/second
- **With caching**: ~10+ coins/second

---

## 🔧 Configuration

### Environment Variables
```env
# Optional API Keys (for higher limits)
BIRDEYE_API_KEY=your_key_here
CMC_API_KEY=your_key_here

# Rate Limits (requests/second)
DEXSCREENER_RATE_LIMIT=10
BIRDEYE_RATE_LIMIT=5
JUPITER_RATE_LIMIT=20
COINGECKO_RATE_LIMIT=10
```

### Custom Provider Configuration
```python
custom_provider = APIProvider(
    name="custom",
    base_url="https://api.custom.com",
    headers={"Authorization": "Bearer token"},
    rate_limit=5.0,
    priority=0  # Highest priority
)
```

---

## 🚨 Error Handling

### Common Errors & Solutions

1. **Rate Limit Exceeded**
   - Solution: Automatic retry with exponential backoff
   - Prevention: Built-in rate limiters

2. **Contract Not Found**
   - Solution: Try next API in priority order
   - Note: New tokens may take time to appear

3. **Network Timeout**
   - Solution: 10-second timeout with retry
   - Prevention: Concurrent requests with limits

4. **Invalid Response**
   - Solution: Data validation before storage
   - Prevention: Schema validation

---

## 📈 Future Enhancements

1. **WebSocket Support**: Real-time price updates
2. **GraphQL Integration**: More efficient data queries
3. **AI-Powered Selection**: Choose best API based on token type
4. **Custom Metrics**: Calculate additional indicators
5. **Historical Data**: Time-series data collection

---

## 🎯 Best Practices

1. **Always use fallbacks**: Don't rely on a single API
2. **Cache aggressively**: Reduce API calls for same data
3. **Batch requests**: Process multiple coins together
4. **Monitor success rates**: Track which APIs work best
5. **Handle errors gracefully**: Log failures, continue processing

---

*Last Updated: 2025-08-01 - Multi-API enrichment system with 5 data sources*