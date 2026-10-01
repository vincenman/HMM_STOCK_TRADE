"""
Environment configuration management for production deployment.
"""
import os
from typing import Dict, Any
from dataclasses import dataclass

from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class EnvironmentConfig:
    """Environment configuration settings."""

    # Environment
    environment: str = "development"
    debug_mode: bool = False

    # Database
    db_path: str = "./data/trading.db"

    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file_path: str = "./logs/app.log"

    # Data
    default_lookback_days: int = 60
    max_lookback_days: int = 365
    cache_enabled: bool = True

    # Performance
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    max_data_points: int = 10000

    # Paper Trading
    paper_trading_enabled: bool = True
    update_interval_seconds: int = 300  # 5 minutes

    # Email (optional)
    email_enabled: bool = False
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    recipient_email: str = ""

    # Security
    enable_auth: bool = False
    session_timeout_minutes: int = 60


class ConfigManager:
    """Manages configuration across different environments."""

    def __init__(self):
        """Initialize configuration manager."""
        self.config = EnvironmentConfig()
        self._load_from_environment()
        logger.info(f"Configuration loaded for environment: {self.config.environment}")

    def _load_from_environment(self):
        """Load configuration from environment variables."""

        # Environment
        self.config.environment = os.getenv("ENVIRONMENT", "development")
        self.config.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

        # Database
        self.config.db_path = os.getenv("DB_PATH", self.config.db_path)

        # Logging
        self.config.log_level = os.getenv("LOG_LEVEL", self.config.log_level)
        self.config.log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"

        # Data
        self.config.default_lookback_days = int(os.getenv("DEFAULT_LOOKBACK_DAYS", "60"))
        self.config.max_lookback_days = int(os.getenv("MAX_LOOKBACK_DAYS", "365"))

        # Performance
        self.config.enable_caching = os.getenv("ENABLE_CACHING", "true").lower() == "true"
        self.config.cache_ttl = int(os.getenv("CACHE_TTL", "3600"))

        # Paper Trading
        self.config.paper_trading_enabled = os.getenv("PAPER_TRADING_ENABLED", "true").lower() == "true"
        self.config.update_interval_seconds = int(os.getenv("UPDATE_INTERVAL", "300"))

        # Email
        self.config.email_enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        self.config.smtp_server = os.getenv("SMTP_SERVER", "")
        self.config.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.config.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.config.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.config.recipient_email = os.getenv("RECIPIENT_EMAIL", "")

    def get_config(self) -> EnvironmentConfig:
        """Get current configuration."""
        return self.config

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.config.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development."""
        return self.config.environment == "development"

    def get_streamlit_secrets(self) -> Dict[str, Any]:
        """
        Load secrets from Streamlit secrets.toml.

        Returns:
            Dictionary of secrets
        """
        try:
            import streamlit as st

            if hasattr(st, 'secrets'):
                # Update config from secrets
                if 'email' in st.secrets:
                    email_secrets = st.secrets['email']
                    self.config.email_enabled = True
                    self.config.smtp_server = email_secrets.get('smtp_server', '')
                    self.config.smtp_port = email_secrets.get('smtp_port', 587)
                    self.config.smtp_username = email_secrets.get('smtp_username', '')
                    self.config.smtp_password = email_secrets.get('smtp_password', '')
                    self.config.recipient_email = email_secrets.get('recipient_email', '')

                if 'general' in st.secrets:
                    general_secrets = st.secrets['general']
                    self.config.environment = general_secrets.get('environment', 'production')
                    self.config.debug_mode = general_secrets.get('debug_mode', False)
                    self.config.log_level = general_secrets.get('log_level', 'INFO')

                return dict(st.secrets)

        except Exception as e:
            logger.warning(f"Could not load Streamlit secrets: {e}")

        return {}

    def validate_config(self) -> bool:
        """
        Validate configuration.

        Returns:
            True if valid, False otherwise
        """
        issues = []

        # Check database path
        db_dir = os.path.dirname(self.config.db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create database directory: {e}")

        # Check log path if file logging enabled
        if self.config.log_to_file:
            log_dir = os.path.dirname(self.config.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create log directory: {e}")

        # Check email config if enabled
        if self.config.email_enabled:
            if not self.config.smtp_server:
                issues.append("Email enabled but SMTP server not configured")
            if not self.config.smtp_username:
                issues.append("Email enabled but SMTP username not configured")

        if issues:
            for issue in issues:
                logger.warning(f"Configuration issue: {issue}")
            return False

        logger.info("Configuration validation passed")
        return True

    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary for display."""
        return {
            "Environment": self.config.environment,
            "Debug Mode": self.config.debug_mode,
            "Database": self.config.db_path,
            "Log Level": self.config.log_level,
            "Caching Enabled": self.config.enable_caching,
            "Paper Trading Enabled": self.config.paper_trading_enabled,
            "Email Notifications": self.config.email_enabled,
        }


# Global config instance
config_manager = ConfigManager()
