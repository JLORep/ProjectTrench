import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
from loguru import logger
from config.config import settings

class CoinDatabase:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.database_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Coins table - basic coin information
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    market_cap REAL,
                    volume_24h REAL,
                    circulating_supply REAL,
                    max_supply REAL,
                    ath REAL,
                    ath_date TIMESTAMP,
                    atl REAL,
                    atl_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Price data table - OHLCV data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    timeframe TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    quote_volume REAL,
                    FOREIGN KEY (coin_id) REFERENCES coins(id),
                    UNIQUE(coin_id, timestamp, timeframe)
                )
            """)
            
            # Technical indicators table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    timeframe TEXT NOT NULL,
                    indicator_name TEXT NOT NULL,
                    indicator_value REAL NOT NULL,
                    parameters JSON,
                    FOREIGN KEY (coin_id) REFERENCES coins(id)
                )
            """)
            
            # Telegram signals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telegram_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER UNIQUE,
                    channel_id INTEGER,
                    channel_name TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    coin_symbol TEXT,
                    signal_type TEXT,
                    entry_price REAL,
                    target_prices JSON,
                    stop_loss REAL,
                    confidence REAL,
                    raw_message TEXT,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Strategy backtests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backtests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_name TEXT NOT NULL,
                    coin_id INTEGER,
                    start_date TIMESTAMP NOT NULL,
                    end_date TIMESTAMP NOT NULL,
                    initial_capital REAL NOT NULL,
                    final_capital REAL NOT NULL,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    max_drawdown REAL,
                    sharpe_ratio REAL,
                    parameters JSON,
                    trades JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (coin_id) REFERENCES coins(id)
                )
            """)
            
            # Market metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    total_market_cap REAL,
                    btc_dominance REAL,
                    eth_dominance REAL,
                    fear_greed_index INTEGER,
                    total_volume_24h REAL,
                    active_cryptocurrencies INTEGER,
                    metadata JSON
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_data_coin_timestamp ON price_data(coin_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_data_timeframe ON price_data(timeframe)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_indicators_coin_timestamp ON indicators(coin_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_telegram_signals_timestamp ON telegram_signals(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_telegram_signals_coin ON telegram_signals(coin_symbol)")
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def add_coin(self, symbol: str, name: str, **kwargs) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO coins (symbol, name, market_cap, volume_24h, 
                    circulating_supply, max_supply, ath, ath_date, atl, atl_date, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol, name, kwargs.get('market_cap'), kwargs.get('volume_24h'),
                kwargs.get('circulating_supply'), kwargs.get('max_supply'),
                kwargs.get('ath'), kwargs.get('ath_date'), kwargs.get('atl'),
                kwargs.get('atl_date'), datetime.now()
            ))
            return cursor.lastrowid
    
    def add_price_data(self, coin_id: int, timestamp: datetime, timeframe: str,
                      open_price: float, high: float, low: float, close: float,
                      volume: float, quote_volume: Optional[float] = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO price_data (coin_id, timestamp, timeframe,
                    open, high, low, close, volume, quote_volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (coin_id, timestamp, timeframe, open_price, high, low, close, volume, quote_volume))
    
    def get_price_data(self, symbol: str, timeframe: str, 
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT p.timestamp, p.open, p.high, p.low, p.close, p.volume
                FROM price_data p
                JOIN coins c ON p.coin_id = c.id
                WHERE c.symbol = ? AND p.timeframe = ?
            """
            params = [symbol, timeframe]
            
            if start_date:
                query += " AND p.timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND p.timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY p.timestamp"
            
            df = pd.read_sql_query(query, conn, params=params, parse_dates=['timestamp'])
            df.set_index('timestamp', inplace=True)
            return df
    
    def add_telegram_signal(self, **kwargs):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO telegram_signals (
                    message_id, channel_id, channel_name, timestamp, coin_symbol,
                    signal_type, entry_price, target_prices, stop_loss, confidence,
                    raw_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kwargs.get('message_id'), kwargs.get('channel_id'),
                kwargs.get('channel_name'), kwargs.get('timestamp'),
                kwargs.get('coin_symbol'), kwargs.get('signal_type'),
                kwargs.get('entry_price'), kwargs.get('target_prices'),
                kwargs.get('stop_loss'), kwargs.get('confidence'),
                kwargs.get('raw_message'), kwargs.get('metadata')
            ))
    
    def close(self):
        pass