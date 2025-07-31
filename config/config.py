from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    binance_api_key: Optional[str] = None
    binance_api_secret: Optional[str] = None
    
    # Telegram
    telegram_api_id: Optional[int] = None
    telegram_api_hash: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_group_id: Optional[int] = None
    
    # Database
    database_path: Path = Path("./data/coins.db")
    
    # Dashboard
    dashboard_port: int = 8050
    dashboard_host: str = "0.0.0.0"
    
    # Azure (for future deployment)
    azure_storage_connection_string: Optional[str] = None
    azure_container_name: str = "crypto-data"
    
    # Trading parameters
    default_timeframes: list[str] = ["1m", "5m", "15m", "1h", "4h", "1d"]
    max_data_points: int = 10000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()