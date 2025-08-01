# 🎯 Super Claude Trading Commands - Complete Reference

## Overview
This document provides a comprehensive reference for all trading-specific Super Claude commands available in TrenchCoat Pro. These commands leverage the full MCP server architecture (Context7, Sequential, Magic, Puppeteer) for professional-grade crypto trading analysis.

---

## 📊 **ANALYSIS COMMANDS**

### `/analyze` - Market Analysis
**Purpose**: Deep analysis of coins, markets, and trading opportunities

#### **Coin Analysis**
```bash
/analyze --coin $PEPE --seq --c7
# Deep analysis of PEPE with Sequential reasoning + Context7 documentation

/analyze --coin $BTC --fundamentals --technical --ultrathink
# Comprehensive Bitcoin analysis with maximum thinking depth

/analyze --coin $SOLANA --correlation BTC --evidence
# Solana correlation analysis with evidence-based results
```

#### **Market Analysis**
```bash
/analyze --market --performance --ultrathink  
# Comprehensive market analysis with deep reasoning

/analyze --sector defi --trends --seq
# DeFi sector analysis with systematic evaluation

/analyze --market-cap --distribution --evidence
# Market cap distribution analysis with documented results
```

#### **Portfolio Analysis**
```bash
/analyze --portfolio --risk --seq
# Portfolio risk analysis with systematic evaluation

/analyze --portfolio --performance --benchmark SP500
# Portfolio performance vs S&P 500 benchmark

/analyze --portfolio --diversification --modern-theory
# Portfolio diversification using Modern Portfolio Theory
```

### `/scan` - Market Scanning
**Purpose**: Identify opportunities, risks, and market patterns

#### **Opportunity Scanning**
```bash
/scan --opportunities --confidence 85
# Scan for high-confidence trading opportunities (85%+ confidence)

/scan --breakouts --volume --timeframe 4h
# Scan for volume-confirmed breakouts on 4-hour timeframe

/scan --undervalued --fundamentals --c7
# Scan for undervalued coins using fundamental analysis
```

#### **Risk Scanning**
```bash
/scan --risk --portfolio --drawdown 15%
# Scan portfolio for positions with >15% drawdown risk

/scan --rug-pull --indicators --evidence
# Scan for rug pull indicators with evidence-based assessment

/scan --liquidity --threshold 1M --seq
# Scan for liquidity issues using $1M threshold
```

#### **Technical Scanning**
```bash
/scan --technical --patterns --rsi oversold
# Scan for technical patterns with oversold RSI

/scan --momentum --breakouts --volume-confirmation
# Scan for momentum plays with volume confirmation

/scan --support-resistance --levels --accuracy 90%
# Scan for high-accuracy support/resistance levels
```

---

## 🎯 **TRADING COMMANDS**

### `/trade` - Trading Analysis
**Purpose**: Complete trading analysis with entry/exit points

#### **Trading Opportunity Analysis**
```bash
/trade --analyze $SOLANA --entry --exit --seq
# Complete Solana trading analysis with Sequential reasoning

/trade --opportunity $PEPE --risk-reward 1:3 --confidence
# PEPE trading opportunity with 1:3 risk-reward ratio

/trade --swing $BTC --timeframe daily --technical
# Bitcoin swing trading analysis on daily timeframe
```

#### **Strategy Analysis**
```bash
/trade --strategy momentum --backtest --period 6m
# Momentum strategy backtesting over 6 months

/trade --strategy dca --optimization --seq
# DCA strategy optimization with systematic analysis

/trade --strategy grid --parameters --risk-management
# Grid trading strategy with risk management parameters
```

#### **Risk Management**
```bash
/trade --risk-assessment --position-size --kelly
# Risk assessment with Kelly criterion position sizing

/trade --stop-loss --take-profit --trailing --evidence
# Stop-loss and take-profit with trailing stops

/trade --portfolio-heat --max-risk 2% --diversification
# Portfolio heat map with 2% max risk per trade
```

### `/signal` - Signal Generation
**Purpose**: Generate and validate trading signals

#### **Signal Generation**
```bash
/signal --generate --timeframe 4h --seq
# Generate trading signals with 4-hour timeframe analysis

/signal --generate --coins top50 --momentum --volume
# Generate momentum signals for top 50 coins by volume

/signal --generate --strategy mean-reversion --oversold
# Generate mean-reversion signals for oversold conditions
```

#### **Signal Validation**
```bash
/signal --validate $BTC --confidence 90 --evidence
# Validate Bitcoin signals with 90% confidence threshold

/signal --backtest --accuracy --period 3m --results
# Backtest signal accuracy over 3-month period

/signal --paper --trade --live --tracking
# Paper trade signals with live tracking
```

#### **Signal Optimization**
```bash
/signal --optimize --parameters --genetic-algorithm
# Optimize signal parameters using genetic algorithms

/signal --filter --noise --confirmation --multi-timeframe
# Filter signal noise with multi-timeframe confirmation

/signal --ensemble --models --voting --weighted
# Ensemble signal generation with weighted voting
```

### `/portfolio` - Portfolio Management
**Purpose**: Portfolio optimization and rebalancing

#### **Portfolio Optimization**
```bash
/portfolio --optimize --modern-theory --seq
# Portfolio optimization using Modern Portfolio Theory

/portfolio --optimize --risk-parity --volatility-targeting
# Risk parity optimization with volatility targeting

/portfolio --optimize --black-litterman --views
# Black-Litterman optimization with market views
```

#### **Rebalancing**
```bash
/portfolio --rebalance --risk-level conservative --evidence
# Conservative portfolio rebalancing with evidence

/portfolio --rebalance --threshold 5% --tax-efficient
# Rebalance when allocation drifts >5%, tax-efficiently

/portfolio --rebalance --calendar --monthly --systematic
# Systematic monthly calendar rebalancing
```

#### **Performance Analysis**
```bash
/portfolio --performance --attribution --factor-analysis
# Performance attribution with factor analysis

/portfolio --performance --risk-adjusted --sharpe --sortino
# Risk-adjusted performance (Sharpe, Sortino ratios)

/portfolio --performance --drawdown --underwater --recovery
# Drawdown analysis with underwater periods and recovery
```

---

## 🔍 **RESEARCH COMMANDS**

### `/research` - Market Research
**Purpose**: Fundamental and technical research

#### **Coin Research**
```bash
/research --coin $PEPE --fundamentals --c7
# PEPE fundamental analysis with Context7 documentation

/research --coin $BTC --adoption --network-effects --seq
# Bitcoin adoption and network effects research

/research --coin $ETH --ecosystem --dapp-activity --evidence
# Ethereum ecosystem and dApp activity research
```

#### **Sector Research**
```bash
/research --sector defi --trends --seq --c7
# DeFi sector research with systematic analysis

/research --sector gaming --nft --metaverse --growth
# Gaming/NFT/Metaverse sector growth research

/research --sector layer1 --comparison --technical --evidence
# Layer 1 blockchain comparison with technical evidence
```

#### **Macro Research**
```bash
/research --macro --fed-policy --crypto-correlation
# Macro research on Fed policy and crypto correlation

/research --macro --inflation --bitcoin-hedge --evidence
# Inflation hedge research for Bitcoin with evidence

/research --macro --regulations --impact-analysis --seq
# Regulatory impact analysis with systematic approach
```

### `/compare` - Comparative Analysis
**Purpose**: Compare coins, strategies, and metrics

#### **Coin Comparison**
```bash
/compare --coins $BTC $ETH $SOL --metrics --seq
# Compare Bitcoin, Ethereum, Solana across key metrics

/compare --layer1 --scalability --security --decentralization
# Layer 1 comparison: scalability vs security vs decentralization

/compare --stablecoins --peg-stability --yield --risk
# Stablecoin comparison: peg stability, yield, risk
```

#### **Strategy Comparison**
```bash
/compare --strategies momentum vs mean-reversion --backtest
# Compare momentum vs mean-reversion strategies

/compare --strategies dca vs lump-sum --evidence --periods
# Compare DCA vs lump-sum across different periods

/compare --strategies active vs passive --fees --tax --returns
# Compare active vs passive strategies including fees and taxes
```

---

## ⚙️ **AUTOMATION COMMANDS**

### `/bot` - Trading Bot Management
**Purpose**: Create, optimize, and manage trading bots

#### **Bot Creation**
```bash
/bot --create dca-strategy --test --pup
# Create DCA strategy bot with Puppeteer testing

/bot --create grid-trading --range 45000-55000 --btc
# Create Bitcoin grid trading bot in $45K-$55K range

/bot --create arbitrage --exchanges binance-coinbase --monitor
# Create arbitrage bot between Binance and Coinbase
```

#### **Bot Optimization**
```bash
/bot --optimize --performance --risk-limits --seq
# Optimize bot performance with risk management limits

/bot --optimize --parameters --walk-forward --validation
# Optimize parameters using walk-forward validation

/bot --optimize --execution --latency --slippage --costs
# Optimize execution to minimize latency and slippage
```

#### **Bot Testing**
```bash
/bot --backtest --strategy --historical --3-years
# Backtest bot strategy over 3-year historical period

/bot --paper-trade --live --monitoring --alerts
# Paper trade bot with live monitoring and alerts

/bot --stress-test --market-conditions --volatility
# Stress test bot under various market conditions
```

### `/alert` - Alert Management
**Purpose**: Set up and manage trading alerts

#### **Price Alerts**
```bash
/alert --setup $BTC --price 50000 --telegram --discord
# Set up Bitcoin $50K price alert via Telegram and Discord

/alert --setup $ETH --resistance 4000 --breakout --volume
# Set up Ethereum resistance breakout alert with volume

/alert --setup portfolio --value 100000 --milestone
# Set up portfolio milestone alert at $100K
```

#### **Technical Alerts**
```bash
/alert --rsi $SOLANA --oversold 30 --timeframe 4h
# Set up Solana RSI oversold alert on 4H timeframe

/alert --macd $BTC --bullish-cross --confirmation
# Set up Bitcoin MACD bullish crossover alert

/alert --volume-spike --threshold 300% --top100
# Set up volume spike alerts for top 100 coins
```

---

## 🧪 **TESTING COMMANDS**

### `/test` - Strategy Testing
**Purpose**: Comprehensive testing of strategies and systems

#### **Strategy Testing**
```bash
/test --strategy momentum --coverage --pup --evidence
# Test momentum strategy with Puppeteer E2E testing

/test --strategy portfolio --monte-carlo --1000-runs
# Monte Carlo testing of portfolio strategy (1000 runs)

/test --strategy signals --out-of-sample --validation
# Out-of-sample testing of signal strategy
```

#### **System Testing**
```bash
/test --trading-system --latency --execution --quality
# Test trading system latency and execution quality

/test --risk-management --stress --scenarios --evidence
# Stress test risk management under various scenarios

/test --backtesting --engine --accuracy --validation
# Test backtesting engine accuracy and validation
```

### `/validate` - Validation Commands
**Purpose**: Validate trades, signals, and compliance

#### **Trade Validation**
```bash
/validate --trades --risk-management --evidence --compliance
# Validate trades meet risk management and compliance requirements

/validate --execution --best-practices --slippage --timing
# Validate execution follows best practices for slippage and timing

/validate --portfolio --allocation --limits --diversification
# Validate portfolio allocation meets limits and diversification
```

#### **Signal Validation**
```bash
/validate --signals --confidence --threshold 80 --evidence
# Validate signals meet 80% confidence threshold with evidence

/validate --signals --accuracy --historical --forward-testing
# Validate signal accuracy using historical and forward testing

/validate --signals --risk-adjusted --sharpe --information-ratio
# Validate signals on risk-adjusted metrics (Sharpe, Information Ratio)
```

---

## 🎨 **VISUALIZATION COMMANDS**

### `/chart` - Chart Generation
**Purpose**: Generate trading charts and visualizations

#### **Technical Analysis Charts**
```bash
/chart --coin $BTC --technical --magic --indicators
# Generate Bitcoin technical analysis chart with Magic styling

/chart --coin $ETH --candlestick --volume --support-resistance
# Generate Ethereum candlestick chart with volume and S/R levels

/chart --coin $SOLANA --multi-timeframe --daily-4h-1h
# Generate Solana multi-timeframe chart (daily, 4H, 1H)
```

#### **Portfolio Charts**
```bash
/chart --portfolio --performance --benchmark --interactive
# Generate interactive portfolio performance vs benchmark chart

/chart --portfolio --allocation --pie-chart --sectors
# Generate portfolio allocation pie chart by sectors

/chart --portfolio --risk-return --scatter --efficient-frontier
# Generate risk-return scatter plot with efficient frontier
```

#### **Correlation and Heatmaps**
```bash
/chart --correlation-matrix --top20 --heatmap --magic
# Generate correlation heatmap for top 20 coins with Magic styling

/chart --sector-rotation --heatmap --performance --monthly
# Generate sector rotation heatmap with monthly performance

/chart --volatility --surface --options --3d
# Generate 3D volatility surface chart for options
```

### `/report` - Report Generation
**Purpose**: Generate comprehensive trading reports

#### **Performance Reports**
```bash
/report --trading --monthly --evidence --statistics
# Generate monthly trading report with evidence-based statistics

/report --portfolio --quarterly --risk-metrics --attribution
# Generate quarterly portfolio report with risk metrics and attribution

/report --strategy --annual --backtest --forward-test --comparison
# Generate annual strategy report with backtest vs forward test
```

#### **Risk Reports**
```bash
/report --risk --var --expected-shortfall --monte-carlo
# Generate VaR and Expected Shortfall risk report

/report --risk --stress-test --scenarios --correlation-breakdown
# Generate stress test report with scenario analysis

/report --risk --drawdown --underwater --recovery-analysis
# Generate drawdown report with underwater periods and recovery
```

---

## 🚀 **ADVANCED COMMANDS**

### `/deploy` - Strategy Deployment
**Purpose**: Deploy strategies to live trading

#### **Strategy Deployment**
```bash
/deploy --strategy live --validate --monitor --alerts
# Deploy strategy to live trading with validation, monitoring, and alerts

/deploy --strategy paper --duration 30-days --evaluation
# Deploy strategy to paper trading for 30-day evaluation

/deploy --strategy hybrid --live 50% --paper 50% --comparison
# Deploy hybrid strategy: 50% live, 50% paper for comparison
```

#### **Bot Deployment**
```bash
/deploy --bot production --checkpoint --backup --rollback
# Deploy bot to production with checkpoint, backup, and rollback capability

/deploy --bot staging --testing --monitoring --gradual-rollout
# Deploy bot to staging with testing, monitoring, and gradual rollout

/deploy --bot multi-exchange --arbitrage --risk-limits
# Deploy multi-exchange arbitrage bot with risk limits
```

### `/optimize` - Advanced Optimization
**Purpose**: Optimize strategies, portfolios, and execution

#### **Strategy Optimization**
```bash
/optimize --strategy --genetic-algorithm --seq --parameters
# Optimize strategy using genetic algorithms with Sequential analysis

/optimize --strategy --bayesian --hyperparameter --tuning
# Bayesian hyperparameter tuning for strategy optimization

/optimize --strategy --reinforcement-learning --dynamic --adaptation
# Reinforcement learning optimization with dynamic adaptation
```

#### **Portfolio Optimization**
```bash
/optimize --portfolio --sharpe-ratio --ultrathink --constraints
# Optimize portfolio for maximum Sharpe ratio with constraints

/optimize --portfolio --black-litterman --views --confidence
# Black-Litterman portfolio optimization with market views

/optimize --portfolio --risk-budgeting --factor-based --allocation
# Risk budgeting optimization with factor-based allocation
```

#### **Execution Optimization**
```bash
/optimize --execution --twap --vwap --implementation-shortfall
# Optimize execution using TWAP, VWAP, and implementation shortfall

/optimize --execution --market-impact --timing --liquidity
# Optimize execution for minimal market impact and optimal timing

/optimize --execution --multi-venue --routing --best-execution
# Optimize multi-venue execution routing for best execution
```

---

## 💡 **EXAMPLE WORKFLOWS**

### **Complete Coin Analysis Workflow**
```bash
# Step 1: Research
/research --coin $PEPE --fundamentals --c7

# Step 2: Technical Analysis  
/analyze --coin $PEPE --technical --seq --ultrathink

# Step 3: Signal Generation
/signal --generate $PEPE --confidence 85 --evidence

# Step 4: Risk Assessment
/trade --analyze $PEPE --risk-reward 1:3 --position-size

# Step 5: Visualization
/chart --coin $PEPE --technical --magic --indicators

# Step 6: Validation
/validate --trade-plan $PEPE --risk-management --compliance
```

### **Portfolio Optimization Workflow**
```bash
# Step 1: Current Analysis
/portfolio --analyze --current --performance --risk

# Step 2: Optimization
/optimize --portfolio --sharpe-ratio --ultrathink --constraints

# Step 3: Backtesting
/test --portfolio --optimization --monte-carlo --validation

# Step 4: Implementation
/portfolio --rebalance --optimized --tax-efficient --gradual

# Step 5: Monitoring
/deploy --portfolio --monitoring --alerts --reporting
```

### **Trading Strategy Development Workflow**
```bash
# Step 1: Research
/research --strategy momentum --literature --c7 --evidence

# Step 2: Design
/design --strategy momentum --parameters --risk-management

# Step 3: Backtesting
/test --strategy momentum --backtest --3-years --validation

# Step 4: Optimization
/optimize --strategy --parameters --walk-forward --seq

# Step 5: Paper Trading
/deploy --strategy paper --monitoring --30-days --evaluation

# Step 6: Live Deployment
/deploy --strategy live --gradual --risk-limits --monitoring
```

---

## 🎯 **MCP SERVER INTEGRATION**

All commands are enhanced when used with MCP server flags:

### **Context7 Integration** (`--c7`)
- Provides official documentation and best practices
- Real-time API documentation lookup
- Version compatibility checking
- Implementation examples

### **Sequential Integration** (`--seq`)
- Multi-step systematic analysis
- Root cause investigation
- Complex problem solving
- Evidence-based reasoning

### **Magic Integration** (`--magic`)
- Premium UI component generation
- Beautiful chart styling
- Consistent design system
- Interactive visualizations

### **Puppeteer Integration** (`--pup`)
- End-to-end testing
- Performance validation
- Browser automation
- Visual regression testing

### **Combined MCP Usage**
```bash
# Ultimate analysis with all MCP servers
/analyze --coin $BTC --seq --c7 --magic --pup --ultrathink

# Complete strategy testing
/test --strategy momentum --coverage --pup --evidence --c7

# Professional report generation
/report --trading --monthly --magic --evidence --seq
```

---

## 🎯 **EVIDENCE-BASED LANGUAGE**

All commands follow professional evidence-based language patterns:

### **Required Language**
- "Analysis indicates potential opportunity"
- "Historical data suggests correlation"  
- "Backtesting confirms profitability"
- "Risk metrics show acceptable levels"
- "Evidence supports the hypothesis"
- "Data indicates strong performance"

### **Prohibited Language**
- "This coin will definitely moon"
- "Guaranteed profits"
- "Best trading strategy"
- "Always profitable"
- "Never fails"
- "100% accurate"

---

**This comprehensive command system transforms TrenchCoat Pro into a professional-grade crypto trading platform with AI-powered analysis at every level!** 🚀💎

*Last Updated: 2025-08-01 - Complete trading command integration with MCP server enhancement*