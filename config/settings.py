"""
Global configuration settings for the HMM Trading Application.
"""
import os
from pathlib import Path
from typing import Dict, Any

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models" / "saved_models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_PATH = DATA_DIR / "trading_app.db"

# Data Settings
ASSET_SYMBOL = "BTC-USD"
DATA_INTERVAL = "1h"  # Hourly data
LOOKBACK_DAYS = 730  # 2 years

# HMM Model Configuration
HMM_N_STATES = 7
HMM_N_ITER = 100
HMM_RANDOM_STATE = 42
HMM_COVARIANCE_TYPE = "full"
MODEL_RETRAIN_DAYS = 7  # Weekly retraining

# Trading Strategy Parameters (Defaults - can be overridden in UI)
STRATEGY_DEFAULTS: Dict[str, Any] = {
    "rsi_threshold": 90,
    "momentum_threshold": 0.01,  # 1%
    "volatility_threshold": 0.06,  # 6%
    "volume_sma_period": 20,
    "adx_threshold": 25,
    "ema_short": 50,
    "ema_long": 200,
    "required_conditions": 7,  # Out of 8
    "cooldown_hours": 48,
    "leverage": 2.5,
    "stop_loss_pct": -0.05,  # -5%
    "take_profit_pct": 0.15,  # +15%
    "initial_capital": 10000.0,
    "commission_rate": 0.001,  # 0.1%
}

# Technical Indicator Periods
INDICATOR_PERIODS = {
    "rsi": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "adx": 14,
    "volatility_window": 20,
    "momentum_window": 10,
}

# Risk Management
MAX_POSITION_SIZE = 0.95  # 95% of capital
CASH_BUFFER = 0.05  # 5% cash reserve
MAX_DRAWDOWN_ALERT = 0.20  # 20%

# API Settings
YFINANCE_TIMEOUT = 30  # seconds
MAX_API_RETRIES = 3
API_RETRY_DELAY = 5  # seconds

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 30  # Keep 30 days

# Streamlit Configuration
STREAMLIT_THEME = {
    "primaryColor": "#1f77b4",
    "backgroundColor": "#ffffff",
    "secondaryBackgroundColor": "#f0f2f6",
    "textColor": "#262730",
    "font": "sans serif",
}

# Cache TTL (seconds)
CACHE_TTL_DATA = 3600  # 1 hour
CACHE_TTL_MODEL = 604800  # 7 days

# Regime Colors for Visualization
REGIME_COLORS = {
    "bull": "rgba(0, 255, 0, 0.1)",  # Green
    "bear": "rgba(255, 0, 0, 0.1)",  # Red
    "neutral": "rgba(128, 128, 128, 0.05)",  # Gray
}

# Model Convergence Settings
MODEL_CONVERGENCE_THRESHOLD = -1e6  # Log-likelihood threshold
MODEL_MAX_RETRIES = 3
MODEL_RETRY_SEEDS = [42, 123, 456]

# Data Validation
MAX_HOURLY_RETURN = 0.20  # 20% max return per hour (outlier detection)
MAX_VOLUME_SPIKE = 10  # 10x average volume
MAX_DATA_GAP_HOURS = 3  # Maximum acceptable gap in data

# Paper Trading
PAPER_TRADING_UPDATE_INTERVAL = 3600  # 1 hour in seconds

# Export Settings
EXPORT_FORMATS = ["csv", "json", "html", "pdf"]
CHART_EXPORT_WIDTH = 1200
CHART_EXPORT_HEIGHT = 600

# Authentication (for production - use Streamlit secrets)
DEFAULT_USERNAME = "admin"
# In production, use hashed passwords from .streamlit/secrets.toml
