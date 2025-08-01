
# TrenchCoat Pro - Data Enrichment Analysis Report
Generated: 2025-08-01 20:20:05

## Database Overview
- Total Coins: 1,733
- Coins Needing Critical Data: 1,733
- Overall Data Quality: 62.4%

## Field-by-Field Analysis

### ticker
- Completeness: 100.0%
- Non-null values: 1,733/1,733

### ca
- Completeness: 100.0%
- Non-null values: 1,733/1,733

### discovery_time
- Completeness: 100.0%
- Non-null values: 1,733/1,733

### discovery_price
- Completeness: 99.9%
- Non-null values: 1,733/1,733
- Zero values: 1

### discovery_mc
- Completeness: 100.0%
- Non-null values: 1,545/1,733

### liquidity
- Completeness: 0.0%
- Non-null values: 1,733/1,733
- Zero values: 1,733

### peak_volume
- Completeness: 100.0%
- Non-null values: 1,233/1,733

### smart_wallets
- Completeness: 73.7%
- Non-null values: 1,733/1,733
- Zero values: 455

### dex_paid
- Completeness: 100.0%
- Non-null values: 1,733/1,733

### sol_price
- Completeness: 100.0%
- Non-null values: 1,733/1,733

### history
- Completeness: 0.0%
- Non-null values: 0/1,733

### axiom_price
- Completeness: 0.0%
- Non-null values: 0/1,733

### axiom_mc
- Completeness: 0.0%
- Non-null values: 0/1,733

### axiom_volume
- Completeness: 0.0%
- Non-null values: 0/1,733

## Priority Recommendations

### [HIGH] Missing current price data
- Affected: 100.0% of coins
- Solution: Fetch from DexScreener or Jupiter API
- Impact: Cannot calculate gains or trading signals

### [HIGH] Missing liquidity data
- Affected: 100.0% of coins
- Solution: Fetch from DexScreener API
- Impact: Cannot assess trading safety

### [MEDIUM] Missing market cap data
- Affected: 100.0% of coins
- Solution: Calculate from price * supply or fetch from APIs
- Impact: Cannot properly categorize coins

## Enrichment Execution Plan

1. Batch fetch all coins with missing axiom_price
   - API: DexScreener
   - Batch Size: 50
   - Rate Limit: 300 requests/minute

2. Update liquidity data for all coins
   - API: DexScreener
   - Batch Size: 50
   - Rate Limit: 300 requests/minute

3. Fetch holder/wallet data
   - API: Birdeye
   - Batch Size: 20
   - Rate Limit: 100 requests/minute
