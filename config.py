"""
AATE Configuration Management
Centralized configuration with environment variables and validation.
"""
import os
from dataclasses import dataclass
from typing import Optional
import logging

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation."""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    
    @classmethod
    def from_env(cls) -> Optional['FirebaseConfig']:
        """Initialize from environment variables."""
        try:
            return cls(
                project_id=os.getenv('FIREBASE_PROJECT_ID', ''),
                private_key_id=os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                private_key=os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                client_email=os.getenv('FIREBASE_CLIENT_EMAIL', ''),
                client_id=os.getenv('FIREBASE_CLIENT_ID', '')
            )
        except Exception as e:
            logging.error(f"Firebase config error: {e}")
            return None

@dataclass
class TradingConfig:
    """Trading configuration parameters."""
    # Risk parameters
    max_position_size: float = 0.1  # 10% of portfolio per trade
    max_daily_loss: float = 0.02  # 2% max daily loss
    stop_loss_pct: float = 0.02  # 2% stop loss
    
    # Trading parameters
    lookback_period: int = 100
    min_volume_threshold: float = 1000000  # $1M minimum volume
    
    # Exchange configuration
    exchange_fee: float = 0.001  # 0.1% trading fee
    api_timeout: int = 30
    
    @property
    def is_valid(self) -> bool:
        """Validate configuration parameters."""
        return all([
            self.max_position_size > 0,
            self.max_daily_loss > 0,
            self.stop_loss_pct > 0,
            self.lookback_period > 0
        ])

class ConfigManager:
    """Centralized configuration management with validation."""
    
    def __init__(self):
        self.firebase_config = FirebaseConfig.from_env()
        self.trading_config = TradingConfig()
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Initialize logging
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate all configuration parameters."""
        if not self.firebase_config:
            logging.warning("Firebase configuration not found - running in offline mode")
        
        if not self.trading_config.is_valid:
            raise ValueError("Invalid trading configuration parameters")
        
        logging.info("Configuration validated successfully")
    
    def get_api_keys(self, exchange: str) -> dict:
        """Safely retrieve API keys from environment."""
        prefix = exchange.upper()
        return {
            'apiKey': os.getenv(f'{prefix}_API_KEY', ''),
            'secret': os.getenv(f'{prefix}_API_SECRET', ''),
            'password': os.getenv(f'{prefix}_API_PASSWORD', '')
        }

config = ConfigManager()