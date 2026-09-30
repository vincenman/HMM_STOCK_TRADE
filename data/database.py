"""
SQLite database management and ORM.
"""
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
import json

from config.settings import DATABASE_PATH
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Create engine
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class PriceData(Base):
    """Price data table."""

    __tablename__ = "price_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True, unique=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PriceData(timestamp={self.timestamp}, close={self.close})>"


class ModelMetadata(Base):
    """Model metadata table."""

    __tablename__ = "model_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version = Column(String(50), nullable=False)
    training_date = Column(DateTime, nullable=False)
    n_states = Column(Integer, nullable=False)
    convergence_score = Column(Float, nullable=True)
    model_path = Column(String(255), nullable=False)
    bull_state = Column(Integer, nullable=True)
    bear_state = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ModelMetadata(version={self.model_version}, date={self.training_date})>"


class Trade(Base):
    """Trade log table."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    action = Column(String(10), nullable=False)  # 'BUY' or 'SELL'
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)
    regime = Column(String(50), nullable=True)
    conditions_met = Column(Integer, nullable=True)
    portfolio_value = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Trade(timestamp={self.timestamp}, action={self.action}, price={self.price})>"


class StrategyConfig(Base):
    """Strategy configuration table."""

    __tablename__ = "strategy_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_name = Column(String(100), nullable=False, unique=True)
    config_json = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<StrategyConfig(name={self.config_name}, active={self.is_active})>"

    def get_config_dict(self):
        """Parse JSON config to dictionary."""
        return json.loads(self.config_json)

    def set_config_dict(self, config_dict):
        """Set config from dictionary."""
        self.config_json = json.dumps(config_dict)


class DatabaseManager:
    """Database operations manager."""

    def __init__(self):
        """Initialize database manager."""
        self.engine = engine
        self.SessionLocal = SessionLocal
        self._create_tables()

    def _create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables initialized")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def close_session(self, session: Session):
        """Close database session."""
        session.close()

    def clear_all_data(self):
        """Clear all data from tables (use with caution!)."""
        session = self.get_session()
        try:
            session.query(PriceData).delete()
            session.query(ModelMetadata).delete()
            session.query(Trade).delete()
            session.query(StrategyConfig).delete()
            session.commit()
            logger.warning("All data cleared from database")
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing database: {e}")
            raise
        finally:
            self.close_session(session)

    def get_latest_price(self) -> Optional[PriceData]:
        """Get the latest price data entry."""
        session = self.get_session()
        try:
            latest = (
                session.query(PriceData)
                .order_by(PriceData.timestamp.desc())
                .first()
            )
            return latest
        finally:
            self.close_session(session)

    def get_active_model_metadata(self) -> Optional[ModelMetadata]:
        """Get the active model metadata."""
        session = self.get_session()
        try:
            active_model = (
                session.query(ModelMetadata)
                .filter_by(is_active=True)
                .order_by(ModelMetadata.training_date.desc())
                .first()
            )
            return active_model
        finally:
            self.close_session(session)

    def get_active_strategy_config(self) -> Optional[StrategyConfig]:
        """Get the active strategy configuration."""
        session = self.get_session()
        try:
            active_config = (
                session.query(StrategyConfig)
                .filter_by(is_active=True)
                .first()
            )
            return active_config
        finally:
            self.close_session(session)


# Global database manager instance
db_manager = DatabaseManager()
