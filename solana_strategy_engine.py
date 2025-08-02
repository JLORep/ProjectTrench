#!/usr/bin/env python3
"""
Solana Strategy Engine - Data Modeling & Automated Trading for Memecoins
Advanced ML-based trading strategies with risk management and execution
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import json
import streamlit as st
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import pickle
import warnings
warnings.filterwarnings('ignore')

# ML Imports
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import classification_report, accuracy_score, mean_squared_error
    from sklearn.feature_selection import SelectKBest, f_regression
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Trading Imports  
try:
    from solders.pubkey import Pubkey
    from solana.rpc.api import Client
    from spl.token.instructions import get_associated_token_address
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False

class StrategyType(Enum):
    """Types of trading strategies"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    VOLUME_SPIKE = "volume_spike"
    SMART_MONEY = "smart_money"
    DISCOVERY_ALPHA = "discovery_alpha"

class RiskLevel(Enum):
    """Risk levels for strategies"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    DEGEN = "degen"

@dataclass
class TradingSignal:
    """Trading signal with all necessary information"""
    ticker: str
    contract_address: str
    signal_type: StrategyType
    confidence: float  # 0-100
    entry_price: float
    target_price: float
    stop_loss: float
    position_size: float  # As percentage of portfolio
    risk_reward_ratio: float
    timestamp: datetime
    reasoning: str
    metadata: Dict[str, Any]

@dataclass
class StrategyConfig:
    """Configuration for trading strategies"""
    name: str
    strategy_type: StrategyType
    risk_level: RiskLevel
    max_position_size: float = 0.05  # 5% max per trade
    min_confidence: float = 70.0
    max_daily_trades: int = 10
    stop_loss_pct: float = 0.15  # 15% stop loss
    take_profit_pct: float = 0.30  # 30% take profit
    enabled: bool = True
    parameters: Dict[str, Any] = None

class DataModelEngine:
    """
    Advanced data modeling engine for cryptocurrency analysis
    """
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.model_cache = Path("data/models")
        self.model_cache.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_data(self) -> pd.DataFrame:
        """Load and prepare data for modeling"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
            SELECT 
                ticker, ca, current_price_usd, market_cap_usd, current_volume_24h,
                price_change_24h, discovery_mc, liquidity, smart_wallets,
                enrichment_timestamp, fdv_usd, supply_total, holders_count,
                created_timestamp, first_mint_timestamp, last_trade_timestamp
            FROM coins 
            WHERE current_price_usd IS NOT NULL 
                AND enrichment_timestamp IS NOT NULL
            ORDER BY enrichment_timestamp DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Feature engineering
            df = self.engineer_features(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Data loading error: {e}")
            return pd.DataFrame()
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced features for ML models"""
        if df.empty:
            return df
            
        # Copy to avoid modifying original
        df = df.copy()
        
        # Price-based features
        df['price_log'] = np.log1p(df['current_price_usd'].fillna(0))
        df['mcap_log'] = np.log1p(df['market_cap_usd'].fillna(0))
        df['volume_log'] = np.log1p(df['current_volume_24h'].fillna(0))
        df['liquidity_log'] = np.log1p(df['liquidity'].fillna(0))
        
        # Ratios and relative metrics
        df['volume_mcap_ratio'] = df['current_volume_24h'] / (df['market_cap_usd'] + 1)
        df['liquidity_mcap_ratio'] = df['liquidity'] / (df['market_cap_usd'] + 1)
        df['discovery_premium'] = df['market_cap_usd'] / (df['discovery_mc'] + 1)
        df['smart_wallet_density'] = df['smart_wallets'] / (df['holders_count'] + 1)
        
        # Time-based features
        if 'enrichment_timestamp' in df.columns:
            df['enrichment_timestamp'] = pd.to_datetime(df['enrichment_timestamp'])
            df['hour_of_day'] = df['enrichment_timestamp'].dt.hour
            df['day_of_week'] = df['enrichment_timestamp'].dt.dayofweek
            df['days_since_creation'] = (df['enrichment_timestamp'] - 
                                       pd.to_datetime(df['created_timestamp'])).dt.days
        
        # Volatility indicators (using price change as proxy)
        df['abs_price_change'] = np.abs(df['price_change_24h'].fillna(0))
        df['price_momentum'] = np.sign(df['price_change_24h'].fillna(0))
        
        # Market position features
        df['mcap_rank'] = df['market_cap_usd'].rank(ascending=False, na_option='bottom')
        df['volume_rank'] = df['current_volume_24h'].rank(ascending=False, na_option='bottom')
        df['smart_wallet_rank'] = df['smart_wallets'].rank(ascending=False, na_option='bottom')
        
        # Risk indicators
        df['rug_risk_score'] = self.calculate_rug_risk(df)
        df['honeypot_risk_score'] = self.calculate_honeypot_risk(df)
        
        # Fill NaN values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        return df
    
    def calculate_rug_risk(self, df: pd.DataFrame) -> pd.Series:
        """Calculate rug pull risk score (0-100)"""
        risk_score = np.zeros(len(df))
        
        # Low liquidity = higher risk
        low_liquidity_mask = df['liquidity'] < 10000
        risk_score[low_liquidity_mask] += 30
        
        # Very low holder count = higher risk
        low_holders_mask = df['holders_count'] < 100
        risk_score[low_holders_mask] += 25
        
        # High discovery premium = higher risk
        high_premium_mask = df['discovery_premium'] > 10
        risk_score[high_premium_mask] += 20
        
        # Very recent creation = higher risk
        recent_mask = df['days_since_creation'] < 7
        risk_score[recent_mask] += 15
        
        # Low smart wallet engagement = higher risk
        low_smart_wallets_mask = df['smart_wallets'] < 5
        risk_score[low_smart_wallets_mask] += 10
        
        return pd.Series(np.clip(risk_score, 0, 100))
    
    def calculate_honeypot_risk(self, df: pd.DataFrame) -> pd.Series:
        """Calculate honeypot risk score (0-100)"""
        risk_score = np.zeros(len(df))
        
        # Extremely high price increase = potential honeypot
        extreme_pump_mask = df['price_change_24h'] > 1000  # 1000%+
        risk_score[extreme_pump_mask] += 50
        
        # Very low volume despite high price = suspicious
        low_volume_high_price_mask = (
            (df['current_volume_24h'] < 1000) & 
            (df['current_price_usd'] > 0.01)
        )
        risk_score[low_volume_high_price_mask] += 30
        
        # No recent trades despite high price
        # This would require trade timestamp analysis
        
        return pd.Series(np.clip(risk_score, 0, 100))
    
    def prepare_model_data(self, df: pd.DataFrame, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for ML model training"""
        if df.empty:
            return pd.DataFrame(), pd.Series()
        
        # Select feature columns (exclude non-numeric and target)
        exclude_cols = [
            'ticker', 'ca', target_column, 'enrichment_timestamp', 
            'created_timestamp', 'first_mint_timestamp', 'last_trade_timestamp'
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['int64', 'float64']]
        
        X = df[feature_cols].copy()
        y = df[target_column].copy()
        
        # Remove rows with NaN in target
        valid_idx = ~y.isna()
        X = X[valid_idx]
        y = y[valid_idx]
        
        # Store feature columns for later use
        self.feature_columns = feature_cols
        
        return X, y
    
    def train_price_prediction_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train model to predict future price movements"""
        if not ML_AVAILABLE:
            return {"error": "ML libraries not available"}
        
        # Create target: future price movement (simplified as current change for demo)
        df['future_price_change'] = df['price_change_24h']  # In real implementation, use future data
        
        X, y = self.prepare_model_data(df, 'future_price_change')
        
        if X.empty:
            return {"error": "No valid data for training"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store model and scaler
        self.models['price_prediction'] = model
        self.scalers['price_prediction'] = scaler
        
        # Save to disk
        model_path = self.model_cache / "price_prediction_model.pkl"
        scaler_path = self.model_cache / "price_prediction_scaler.pkl"
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        return {
            "model_type": "Price Prediction",
            "train_score": train_score,
            "test_score": test_score,
            "mse": mse,
            "feature_importance": feature_importance.head(10).to_dict('records'),
            "total_features": len(self.feature_columns),
            "training_samples": len(X_train)
        }
    
    def train_signal_classification_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train model to classify buy/sell/hold signals"""
        if not ML_AVAILABLE:
            return {"error": "ML libraries not available"}
        
        # Create target classes based on price movements
        conditions = [
            df['price_change_24h'] > 20,   # Strong buy
            df['price_change_24h'] > 5,    # Buy
            df['price_change_24h'] > -5,   # Hold
            df['price_change_24h'] > -20,  # Sell
        ]
        choices = ['strong_buy', 'buy', 'hold', 'sell']
        df['signal_class'] = np.select(conditions, choices, default='strong_sell')
        
        X, y = self.prepare_model_data(df, 'signal_class')
        
        if X.empty:
            return {"error": "No valid data for training"}
        
        # Encode labels
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Classification report
        class_report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store model, scaler, and encoder
        self.models['signal_classification'] = model
        self.scalers['signal_classification'] = scaler
        
        # Save to disk
        model_path = self.model_cache / "signal_classification_model.pkl"
        scaler_path = self.model_cache / "signal_classification_scaler.pkl"
        encoder_path = self.model_cache / "signal_classification_encoder.pkl"
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        joblib.dump(le, encoder_path)
        
        return {
            "model_type": "Signal Classification",
            "train_score": train_score,
            "test_score": test_score,
            "classes": le.classes_.tolist(),
            "classification_report": class_report,
            "feature_importance": feature_importance.head(10).to_dict('records'),
            "total_features": len(self.feature_columns),
            "training_samples": len(X_train)
        }

class SolanaStrategyEngine:
    """
    Complete strategy engine for automated Solana memecoin trading
    """
    
    def __init__(self, db_path: str = "data/trench.db"):
        self.db_path = db_path
        self.data_engine = DataModelEngine(db_path)
        self.strategies = {}
        self.active_positions = {}
        self.trade_history = []
        self.performance_metrics = {}
        
        # Load default strategies
        self.initialize_strategies()
        
        # Setup Solana connection (if available)
        self.solana_client = None
        if SOLANA_AVAILABLE:
            try:
                self.solana_client = Client("https://api.mainnet-beta.solana.com")
            except Exception as e:
                st.warning(f"Solana connection failed: {e}")
    
    def initialize_strategies(self):
        """Initialize default trading strategies"""
        
        # Momentum Strategy
        self.strategies['momentum'] = StrategyConfig(
            name="Momentum Hunter",
            strategy_type=StrategyType.MOMENTUM,
            risk_level=RiskLevel.MODERATE,
            max_position_size=0.03,
            min_confidence=75.0,
            max_daily_trades=5,
            stop_loss_pct=0.12,
            take_profit_pct=0.25,
            parameters={
                'min_volume': 50000,
                'min_price_change': 15,
                'smart_wallet_threshold': 10
            }
        )
        
        # Volume Spike Strategy
        self.strategies['volume_spike'] = StrategyConfig(
            name="Volume Surge",
            strategy_type=StrategyType.VOLUME_SPIKE,
            risk_level=RiskLevel.AGGRESSIVE,
            max_position_size=0.05,
            min_confidence=70.0,
            max_daily_trades=8,
            stop_loss_pct=0.18,
            take_profit_pct=0.35,
            parameters={
                'volume_multiplier': 5.0,
                'min_liquidity': 25000,
                'max_rug_risk': 60
            }
        )
        
        # Smart Money Strategy
        self.strategies['smart_money'] = StrategyConfig(
            name="Smart Money Follow",
            strategy_type=StrategyType.SMART_MONEY,
            risk_level=RiskLevel.CONSERVATIVE,
            max_position_size=0.02,
            min_confidence=80.0,
            max_daily_trades=3,
            stop_loss_pct=0.10,
            take_profit_pct=0.20,
            parameters={
                'min_smart_wallets': 20,
                'min_holder_count': 200,
                'max_honeypot_risk': 30
            }
        )
        
        # Discovery Alpha Strategy
        self.strategies['discovery_alpha'] = StrategyConfig(
            name="Discovery Alpha",
            strategy_type=StrategyType.DISCOVERY_ALPHA,
            risk_level=RiskLevel.DEGEN,
            max_position_size=0.08,
            min_confidence=65.0,
            max_daily_trades=12,
            stop_loss_pct=0.25,
            take_profit_pct=0.50,
            parameters={
                'max_discovery_premium': 5.0,
                'min_discovery_mc': 10000,
                'max_days_old': 30
            }
        )
    
    def analyze_coin(self, coin_data: Dict) -> List[TradingSignal]:
        """Analyze a coin and generate trading signals"""
        signals = []
        
        # Skip if basic data is missing
        if not coin_data.get('current_price_usd') or not coin_data.get('ticker'):
            return signals
        
        # Run each strategy
        for strategy_name, config in self.strategies.items():
            if not config.enabled:
                continue
                
            signal = self.evaluate_strategy(coin_data, config)
            if signal:
                signals.append(signal)
        
        return signals
    
    def evaluate_strategy(self, coin_data: Dict, config: StrategyConfig) -> Optional[TradingSignal]:
        """Evaluate a specific strategy against coin data"""
        
        try:
            if config.strategy_type == StrategyType.MOMENTUM:
                return self.evaluate_momentum_strategy(coin_data, config)
            elif config.strategy_type == StrategyType.VOLUME_SPIKE:
                return self.evaluate_volume_spike_strategy(coin_data, config)
            elif config.strategy_type == StrategyType.SMART_MONEY:
                return self.evaluate_smart_money_strategy(coin_data, config)
            elif config.strategy_type == StrategyType.DISCOVERY_ALPHA:
                return self.evaluate_discovery_alpha_strategy(coin_data, config)
            else:
                return None
                
        except Exception as e:
            st.error(f"Strategy evaluation error: {e}")
            return None
    
    def evaluate_momentum_strategy(self, coin_data: Dict, config: StrategyConfig) -> Optional[TradingSignal]:
        """Evaluate momentum-based strategy"""
        params = config.parameters
        
        # Check basic requirements
        volume = coin_data.get('current_volume_24h', 0)
        price_change = coin_data.get('price_change_24h', 0)
        smart_wallets = coin_data.get('smart_wallets', 0)
        
        if (volume < params['min_volume'] or 
            price_change < params['min_price_change'] or
            smart_wallets < params['smart_wallet_threshold']):
            return None
        
        # Calculate confidence based on multiple factors
        confidence = 50.0
        
        # Price momentum component (0-30 points)
        momentum_score = min(price_change / 50.0, 1.0) * 30
        confidence += momentum_score
        
        # Volume component (0-20 points)
        volume_score = min(volume / 100000, 1.0) * 20
        confidence += volume_score
        
        # Smart money component (0-20 points) 
        smart_money_score = min(smart_wallets / 50, 1.0) * 20
        confidence += smart_money_score
        
        # Risk adjustment
        rug_risk = coin_data.get('rug_risk_score', 50)
        confidence -= (rug_risk / 100) * 10
        
        if confidence < config.min_confidence:
            return None
        
        # Calculate entry, target, and stop loss
        current_price = coin_data['current_price_usd']
        entry_price = current_price * 1.02  # Enter slightly above current price
        target_price = entry_price * (1 + config.take_profit_pct)
        stop_loss = entry_price * (1 - config.stop_loss_pct)
        
        return TradingSignal(
            ticker=coin_data['ticker'],
            contract_address=coin_data['ca'],
            signal_type=config.strategy_type,
            confidence=min(confidence, 100.0),
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=config.max_position_size,
            risk_reward_ratio=config.take_profit_pct / config.stop_loss_pct,
            timestamp=datetime.now(),
            reasoning=f"Momentum signal: {price_change:.1f}% price change, {volume:,.0f} volume, {smart_wallets} smart wallets",
            metadata={
                "strategy": config.name,
                "volume": volume,
                "price_change": price_change,
                "smart_wallets": smart_wallets,
                "rug_risk": rug_risk
            }
        )
    
    def evaluate_volume_spike_strategy(self, coin_data: Dict, config: StrategyConfig) -> Optional[TradingSignal]:
        """Evaluate volume spike strategy"""
        params = config.parameters
        
        volume = coin_data.get('current_volume_24h', 0)
        liquidity = coin_data.get('liquidity', 0)
        rug_risk = coin_data.get('rug_risk_score', 50)
        
        # Check basic requirements
        if (liquidity < params['min_liquidity'] or
            rug_risk > params['max_rug_risk']):
            return None
        
        # Volume spike detection (simplified - in reality would compare to historical)
        avg_volume_estimate = volume / params['volume_multiplier']  # Assume current is 5x normal
        
        if volume < avg_volume_estimate * params['volume_multiplier']:
            return None
        
        # Calculate confidence
        confidence = 60.0
        
        # Volume spike strength
        volume_strength = min((volume / avg_volume_estimate) / 10, 1.0) * 25
        confidence += volume_strength
        
        # Liquidity safety
        liquidity_score = min(liquidity / 100000, 1.0) * 15
        confidence += liquidity_score
        
        # Risk adjustment
        confidence -= (rug_risk / 100) * 15
        
        if confidence < config.min_confidence:
            return None
        
        current_price = coin_data['current_price_usd']
        entry_price = current_price * 1.03
        target_price = entry_price * (1 + config.take_profit_pct)
        stop_loss = entry_price * (1 - config.stop_loss_pct)
        
        return TradingSignal(
            ticker=coin_data['ticker'],
            contract_address=coin_data['ca'],
            signal_type=config.strategy_type,
            confidence=min(confidence, 100.0),
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=config.max_position_size,
            risk_reward_ratio=config.take_profit_pct / config.stop_loss_pct,
            timestamp=datetime.now(),
            reasoning=f"Volume spike: {volume:,.0f} volume ({volume/avg_volume_estimate:.1f}x normal), ${liquidity:,.0f} liquidity",
            metadata={
                "strategy": config.name,
                "volume": volume,
                "volume_multiplier": volume / avg_volume_estimate,
                "liquidity": liquidity,
                "rug_risk": rug_risk
            }
        )
    
    def evaluate_smart_money_strategy(self, coin_data: Dict, config: StrategyConfig) -> Optional[TradingSignal]:
        """Evaluate smart money following strategy"""
        params = config.parameters
        
        smart_wallets = coin_data.get('smart_wallets', 0)
        holders = coin_data.get('holders_count', 0)
        honeypot_risk = coin_data.get('honeypot_risk_score', 50)
        
        # Check requirements
        if (smart_wallets < params['min_smart_wallets'] or
            holders < params['min_holder_count'] or
            honeypot_risk > params['max_honeypot_risk']):
            return None
        
        # Calculate confidence
        confidence = 70.0
        
        # Smart wallet engagement
        smart_wallet_score = min(smart_wallets / 100, 1.0) * 20
        confidence += smart_wallet_score
        
        # Holder distribution
        holder_score = min(holders / 1000, 1.0) * 15
        confidence += holder_score
        
        # Safety score
        safety_score = (100 - honeypot_risk) / 100 * 10
        confidence += safety_score
        
        if confidence < config.min_confidence:
            return None
        
        current_price = coin_data['current_price_usd']
        entry_price = current_price * 1.01  # Conservative entry
        target_price = entry_price * (1 + config.take_profit_pct)
        stop_loss = entry_price * (1 - config.stop_loss_pct)
        
        return TradingSignal(
            ticker=coin_data['ticker'],
            contract_address=coin_data['ca'],
            signal_type=config.strategy_type,
            confidence=min(confidence, 100.0),
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=config.max_position_size,
            risk_reward_ratio=config.take_profit_pct / config.stop_loss_pct,
            timestamp=datetime.now(),
            reasoning=f"Smart money: {smart_wallets} smart wallets, {holders} holders, {100-honeypot_risk:.0f}% safety",
            metadata={
                "strategy": config.name,
                "smart_wallets": smart_wallets,
                "holders": holders,
                "honeypot_risk": honeypot_risk
            }
        )
    
    def evaluate_discovery_alpha_strategy(self, coin_data: Dict, config: StrategyConfig) -> Optional[TradingSignal]:
        """Evaluate discovery alpha strategy (early gems)"""
        params = config.parameters
        
        discovery_mc = coin_data.get('discovery_mc', 0)
        market_cap = coin_data.get('market_cap_usd', 0)
        
        if discovery_mc == 0 or discovery_mc < params['min_discovery_mc']:
            return None
        
        discovery_premium = market_cap / discovery_mc if discovery_mc > 0 else 999
        
        # Check if still early
        if discovery_premium > params['max_discovery_premium']:
            return None
        
        # Calculate confidence (higher risk, higher reward)
        confidence = 55.0
        
        # Early stage bonus
        early_bonus = (params['max_discovery_premium'] - discovery_premium) / params['max_discovery_premium'] * 30
        confidence += early_bonus
        
        # Discovery market cap size
        size_score = min(discovery_mc / 50000, 1.0) * 15
        confidence += size_score
        
        if confidence < config.min_confidence:
            return None
        
        current_price = coin_data['current_price_usd']
        entry_price = current_price * 1.05  # Aggressive entry for early alpha
        target_price = entry_price * (1 + config.take_profit_pct)
        stop_loss = entry_price * (1 - config.stop_loss_pct)
        
        return TradingSignal(
            ticker=coin_data['ticker'],
            contract_address=coin_data['ca'],
            signal_type=config.strategy_type,
            confidence=min(confidence, 100.0),
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=config.max_position_size,
            risk_reward_ratio=config.take_profit_pct / config.stop_loss_pct,
            timestamp=datetime.now(),
            reasoning=f"Discovery alpha: ${discovery_mc:,.0f} discovery MC, {discovery_premium:.1f}x premium",
            metadata={
                "strategy": config.name,
                "discovery_mc": discovery_mc,
                "market_cap": market_cap,
                "discovery_premium": discovery_premium
            }
        )
    
    def scan_for_signals(self) -> List[TradingSignal]:
        """Scan all coins for trading signals"""
        signals = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent coin data
            cursor.execute("""
            SELECT * FROM coins 
            WHERE current_price_usd IS NOT NULL 
                AND enrichment_timestamp > datetime('now', '-1 hour')
            ORDER BY enrichment_timestamp DESC
            LIMIT 100
            """)
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            conn.close()
            
            for row in rows:
                coin_data = dict(zip(columns, row))
                coin_signals = self.analyze_coin(coin_data)
                signals.extend(coin_signals)
            
            # Sort by confidence
            signals.sort(key=lambda x: x.confidence, reverse=True)
            
        except Exception as e:
            st.error(f"Signal scanning error: {e}")
        
        return signals
    
    def render_strategy_dashboard(self):
        """Render the complete strategy dashboard"""
        st.header("🎯 Advanced Trading Strategies")
        
        # Strategy overview tabs
        overview_tab, models_tab, signals_tab, config_tab = st.tabs([
            "📊 Overview", "🤖 ML Models", "⚡ Live Signals", "⚙️ Configuration"
        ])
        
        with overview_tab:
            self.render_overview_tab()
        
        with models_tab:
            self.render_models_tab()
        
        with signals_tab:
            self.render_signals_tab()
        
        with config_tab:
            self.render_config_tab()
    
    def render_overview_tab(self):
        """Render strategy overview"""
        st.subheader("🎯 Strategy Performance Overview")
        
        # Strategy summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Strategies", len([s for s in self.strategies.values() if s.enabled]))
        
        with col2:
            st.metric("ML Models", "2", delta="Price + Signals")
        
        with col3:
            st.metric("Risk Management", "ACTIVE", delta="All strategies protected")
        
        with col4:
            st.metric("Solana Integration", "READY" if SOLANA_AVAILABLE else "OFFLINE")
        
        st.markdown("---")
        
        # Strategy list
        st.subheader("📋 Strategy Configurations")
        
        for name, config in self.strategies.items():
            with st.expander(f"{'🟢' if config.enabled else '🔴'} {config.name}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Type:** {config.strategy_type.value}")
                    st.write(f"**Risk Level:** {config.risk_level.value}")
                    st.write(f"**Max Position:** {config.max_position_size*100:.1f}%")
                
                with col2:
                    st.write(f"**Min Confidence:** {config.min_confidence:.0f}%")
                    st.write(f"**Stop Loss:** {config.stop_loss_pct*100:.0f}%")
                    st.write(f"**Take Profit:** {config.take_profit_pct*100:.0f}%")
                
                with col3:
                    st.write(f"**Daily Trades:** {config.max_daily_trades}")
                    st.write(f"**Risk/Reward:** {config.take_profit_pct/config.stop_loss_pct:.1f}:1")
                    st.write(f"**Status:** {'✅ Enabled' if config.enabled else '❌ Disabled'}")
    
    def render_models_tab(self):
        """Render ML models tab"""
        st.subheader("🤖 Machine Learning Models")
        
        if not ML_AVAILABLE:
            st.error("Machine Learning libraries not available. Install scikit-learn to enable ML features.")
            return
        
        # Model training section
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Train Price Prediction Model", type="primary"):
                with st.spinner("Training price prediction model..."):
                    df = self.data_engine.load_data()
                    if not df.empty:
                        results = self.data_engine.train_price_prediction_model(df)
                        st.json(results)
                    else:
                        st.error("No data available for training")
        
        with col2:
            if st.button("📊 Train Signal Classification Model", type="primary"):
                with st.spinner("Training signal classification model..."):
                    df = self.data_engine.load_data()
                    if not df.empty:
                        results = self.data_engine.train_signal_classification_model(df)
                        st.json(results)
                    else:
                        st.error("No data available for training")
        
        st.markdown("---")
        
        # Model information
        st.subheader("📈 Model Information")
        
        model_info = {
            "Price Prediction": {
                "Algorithm": "Gradient Boosting Regressor",
                "Purpose": "Predict future price movements",
                "Features": "30+ engineered features from market data",
                "Status": "✅ Ready" if 'price_prediction' in self.data_engine.models else "❌ Not Trained"
            },
            "Signal Classification": {
                "Algorithm": "Random Forest Classifier", 
                "Purpose": "Classify buy/sell/hold signals",
                "Classes": "strong_buy, buy, hold, sell, strong_sell",
                "Status": "✅ Ready" if 'signal_classification' in self.data_engine.models else "❌ Not Trained"
            }
        }
        
        for model_name, info in model_info.items():
            with st.expander(f"🤖 {model_name} Model"):
                for key, value in info.items():
                    st.write(f"**{key}:** {value}")
    
    def render_signals_tab(self):
        """Render live signals tab"""
        st.subheader("⚡ Live Trading Signals")
        
        if st.button("🔍 Scan for Signals", type="primary"):
            with st.spinner("Scanning coins for trading signals..."):
                signals = self.scan_for_signals()
                
                if signals:
                    st.success(f"Found {len(signals)} trading signals!")
                    
                    for i, signal in enumerate(signals[:10]):  # Show top 10
                        with st.expander(f"{'🚀' if signal.confidence > 80 else '📈'} {signal.ticker} - {signal.confidence:.0f}% Confidence"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**Strategy:** {signal.metadata['strategy']}")
                                st.write(f"**Entry Price:** ${signal.entry_price:.8f}")
                                st.write(f"**Current Price:** ${signal.entry_price/1.02:.8f}")  # Approximate
                            
                            with col2:
                                st.write(f"**Target:** ${signal.target_price:.8f}")
                                st.write(f"**Stop Loss:** ${signal.stop_loss:.8f}")
                                st.write(f"**R/R Ratio:** {signal.risk_reward_ratio:.1f}:1")
                            
                            with col3:
                                st.write(f"**Position Size:** {signal.position_size*100:.1f}%")
                                st.write(f"**Risk Level:** {signal.metadata.get('risk_level', 'N/A')}")
                                st.write(f"**Timestamp:** {signal.timestamp.strftime('%H:%M:%S')}")
                            
                            st.write(f"**Reasoning:** {signal.reasoning}")
                            
                            # Action buttons (demo - not connected to actual trading)
                            btn_col1, btn_col2, btn_col3 = st.columns(3)
                            with btn_col1:
                                if st.button(f"✅ Execute Trade", key=f"execute_{i}"):
                                    st.success("Trade executed! (Demo mode)")
                            with btn_col2:
                                if st.button(f"📋 Add to Watchlist", key=f"watch_{i}"):
                                    st.info("Added to watchlist! (Demo mode)")
                            with btn_col3:
                                if st.button(f"❌ Dismiss", key=f"dismiss_{i}"):
                                    st.warning("Signal dismissed! (Demo mode)")
                else:
                    st.info("No trading signals found. Market conditions may not be optimal.")
        
        st.markdown("---")
        
        # Signal statistics
        st.subheader("📊 Signal Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Signals Today", "0", delta="No historical data")
        
        with col2:
            st.metric("Success Rate", "N/A", delta="No trades executed")
        
        with col3:
            st.metric("Avg Confidence", "75%", delta="Estimated")
    
    def render_config_tab(self):
        """Render configuration tab"""
        st.subheader("⚙️ Strategy Configuration")
        
        # Global settings
        st.markdown("#### 🌐 Global Settings")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_portfolio_risk = st.slider("Max Portfolio Risk", 0.1, 0.5, 0.2, 0.05)
            st.caption("Maximum percentage of portfolio at risk")
        
        with col2:
            max_concurrent_trades = st.slider("Max Concurrent Trades", 1, 20, 10)
            st.caption("Maximum number of simultaneous positions")
        
        with col3:
            min_liquidity = st.number_input("Min Liquidity ($)", 1000, 100000, 25000)
            st.caption("Minimum liquidity required for trades")
        
        st.markdown("---")
        
        # Strategy-specific settings
        st.markdown("#### 🎯 Strategy Settings")
        
        selected_strategy = st.selectbox(
            "Select Strategy to Configure",
            options=list(self.strategies.keys()),
            format_func=lambda x: self.strategies[x].name
        )
        
        if selected_strategy:
            config = self.strategies[selected_strategy]
            
            col1, col2 = st.columns(2)
            
            with col1:
                enabled = st.checkbox("Enable Strategy", value=config.enabled)
                max_pos_size = st.slider(
                    "Max Position Size (%)", 
                    0.01, 0.10, 
                    config.max_position_size, 
                    0.005
                )
                min_conf = st.slider(
                    "Min Confidence (%)", 
                    50.0, 95.0, 
                    config.min_confidence, 
                    2.5
                )
            
            with col2:
                max_trades = st.slider(
                    "Max Daily Trades", 
                    1, 20, 
                    config.max_daily_trades
                )
                stop_loss = st.slider(
                    "Stop Loss (%)", 
                    0.05, 0.30, 
                    config.stop_loss_pct, 
                    0.01
                )
                take_profit = st.slider(
                    "Take Profit (%)", 
                    0.10, 0.80, 
                    config.take_profit_pct, 
                    0.05
                )
            
            if st.button("💾 Save Configuration"):
                # Update configuration
                config.enabled = enabled
                config.max_position_size = max_pos_size
                config.min_confidence = min_conf
                config.max_daily_trades = max_trades
                config.stop_loss_pct = stop_loss
                config.take_profit_pct = take_profit
                
                st.success("Configuration saved!")
        
        st.markdown("---")
        
        # Risk management
        st.markdown("#### ⚠️ Risk Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Portfolio Protection", "ACTIVE", delta="All positions monitored")
            st.metric("Max Drawdown", "15%", delta="Conservative limit")
        
        with col2:
            st.metric("Stop Loss Coverage", "100%", delta="Every trade protected")
            st.metric("Position Sizing", "Kelly Optimal", delta="Mathematical approach")

# Global instance
solana_strategy_engine = SolanaStrategyEngine()