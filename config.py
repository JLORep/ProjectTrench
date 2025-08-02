"""
🔧 TrenchCoat Pro - Unified Configuration System
Single source of truth for all configuration
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import streamlit as st

@dataclass
class Config:
    """Application configuration with environment support"""
    
    # App Settings
    APP_NAME: str = "TrenchCoat Pro"
    APP_VERSION: str = "2.2.0"
    APP_URL: str = "https://trenchdemo.streamlit.app"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_PATH: str = "data/trench.db"
    DATABASE_BACKUP_DIR: str = "data/backups"
    MAX_QUERY_SIZE: int = 1000
    
    # API Configuration
    API_TIMEOUT: int = 30
    API_RETRY_COUNT: int = 3
    API_RATE_LIMIT: int = 100  # requests per minute
    
    # Caching
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_SIZE: int = 1000  # max items
    
    # UI Settings
    MAX_COINS_PER_PAGE: int = 50
    CHART_UPDATE_INTERVAL: int = 60
    AUTO_REFRESH: bool = True
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_INTERVAL: int = 60
    ERROR_LOG_PATH: str = "logs/errors.log"
    
    # Feature Flags
    FEATURES: Dict[str, bool] = None
    
    def __post_init__(self):
        """Initialize feature flags and create directories"""
        self.FEATURES = {
            "hunt_hub": True,
            "alpha_radar": True,
            "mathematical_runners": True,
            "live_signals": True,
            "auto_trading": False,  # Disabled by default for safety
            "debug_mode": self.DEBUG
        }
        
        # Create necessary directories
        Path("logs").mkdir(exist_ok=True)
        Path(self.DATABASE_BACKUP_DIR).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def load_from_file(cls, config_file: str = "config.json") -> "Config":
        """Load configuration from JSON file"""
        config = cls()
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                overrides = json.load(f)
                for key, value in overrides.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        
        return config
    
    @classmethod
    def from_streamlit_secrets(cls) -> "Config":
        """Load configuration from Streamlit secrets"""
        config = cls()
        
        # Override with Streamlit secrets if available
        if hasattr(st, 'secrets'):
            for key in dir(config):
                if not key.startswith('_') and key in st.secrets:
                    setattr(config, key, st.secrets[key])
        
        return config
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service"""
        # First check environment variables
        env_key = f"{service.upper()}_API_KEY"
        if env_value := os.getenv(env_key):
            return env_value
        
        # Then check Streamlit secrets
        if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
            return st.secrets['api_keys'].get(service)
        
        # Finally check local secrets file
        secrets_file = Path(".streamlit/secrets.toml")
        if secrets_file.exists():
            # Parse TOML file (simplified)
            import toml
            secrets = toml.load(secrets_file)
            return secrets.get('api_keys', {}).get(service)
        
        return None
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.FEATURES.get(feature, False)
    
    def get_database_url(self) -> str:
        """Get database URL for different environments"""
        if self.ENVIRONMENT == "test":
            return "data/test.db"
        return self.DATABASE_PATH
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            key: getattr(self, key)
            for key in dir(self)
            if not key.startswith('_') and not callable(getattr(self, key))
        }

# Global config instance
_config = None

def get_config() -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        # Try different loading methods
        if os.path.exists("config.json"):
            _config = Config.load_from_file()
        elif 'streamlit' in globals():
            _config = Config.from_streamlit_secrets()
        else:
            _config = Config()
    return _config

# Convenience exports
config = get_config()