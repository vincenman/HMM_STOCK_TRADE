"""
Data loading and caching from yfinance with SQLite persistence.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple
import time

from config.settings import (
    ASSET_SYMBOL,
    DATA_INTERVAL,
    LOOKBACK_DAYS,
    YFINANCE_TIMEOUT,
    MAX_API_RETRIES,
    API_RETRY_DELAY,
)
from data.database import db_manager, PriceData
from utils.logger import setup_logger
from utils.validators import DataValidator

logger = setup_logger(__name__)


class DataLoader:
    """Handles data fetching from yfinance and caching to SQLite."""

    def __init__(self, symbol: str = ASSET_SYMBOL, interval: str = DATA_INTERVAL):
        """
        Initialize DataLoader.

        Args:
            symbol: Trading symbol (default: BTC-USD)
            interval: Data interval (default: 1h)
        """
        self.symbol = symbol
        self.interval = interval
        self.validator = DataValidator()
        logger.info(f"DataLoader initialized for {symbol} at {interval} interval")

    def fetch_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch price data with caching.

        Args:
            start_date: Start date for data (default: LOOKBACK_DAYS ago)
            end_date: End date for data (default: now)
            force_refresh: Force refresh from API instead of using cache

        Returns:
            DataFrame with OHLCV data
        """
        # Set default date range
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=LOOKBACK_DAYS)

        logger.info(f"Fetching data from {start_date} to {end_date}")

        # Try to load from cache first
        if not force_refresh:
            cached_data = self._load_from_cache(start_date, end_date)
            if cached_data is not None and len(cached_data) > 0:
                logger.info(f"Loaded {len(cached_data)} rows from cache")

                # Check if we need to fetch additional recent data
                latest_cached = cached_data.index.max()
                if (end_date - latest_cached).total_seconds() > 3600:  # More than 1 hour old
                    logger.info("Cache is stale, fetching recent data")
                    recent_data = self._fetch_from_api(latest_cached, end_date)
                    if recent_data is not None and len(recent_data) > 0:
                        # Combine cached and recent data
                        cached_data = pd.concat([cached_data, recent_data])
                        cached_data = cached_data[~cached_data.index.duplicated(keep='last')]
                        cached_data = cached_data.sort_index()
                        self._save_to_cache(recent_data)

                return cached_data

        # Fetch from API
        logger.info("Fetching data from yfinance API")
        data = self._fetch_from_api(start_date, end_date)

        if data is not None and len(data) > 0:
            # Save to cache
            self._save_to_cache(data)
            return data
        else:
            logger.error("Failed to fetch data from API")
            raise ValueError("Unable to fetch data from API")

    def _fetch_from_api(
        self, start_date: datetime, end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data from yfinance API with retry logic.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame or None if failed
        """
        for attempt in range(MAX_API_RETRIES):
            try:
                logger.debug(f"API fetch attempt {attempt + 1}/{MAX_API_RETRIES}")

                ticker = yf.Ticker(self.symbol)
                data = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval=self.interval,
                    timeout=YFINANCE_TIMEOUT,
                )

                if data.empty:
                    logger.warning(f"No data returned from API for {self.symbol}")
                    return None

                # Validate data
                is_valid, issues = self.validator.validate_price_data(data)
                if not is_valid:
                    logger.warning(f"Data validation issues: {issues}")
                    # Continue anyway, but log the issues

                logger.info(f"Successfully fetched {len(data)} rows from API")
                return data

            except Exception as e:
                logger.error(f"API fetch attempt {attempt + 1} failed: {e}")
                if attempt < MAX_API_RETRIES - 1:
                    logger.info(f"Retrying in {API_RETRY_DELAY} seconds...")
                    time.sleep(API_RETRY_DELAY)
                else:
                    logger.error("All API fetch attempts failed")
                    return None

        return None

    def _load_from_cache(
        self, start_date: datetime, end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Load data from SQLite cache.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame or None if no cached data
        """
        try:
            session = db_manager.get_session()

            # Query price data
            query = session.query(PriceData).filter(
                PriceData.timestamp >= start_date,
                PriceData.timestamp <= end_date,
            ).order_by(PriceData.timestamp)

            results = query.all()

            if not results:
                logger.info("No cached data found")
                return None

            # Convert to DataFrame
            data = pd.DataFrame([
                {
                    "Open": row.open,
                    "High": row.high,
                    "Low": row.low,
                    "Close": row.close,
                    "Volume": row.volume,
                }
                for row in results
            ], index=[row.timestamp for row in results])

            logger.info(f"Loaded {len(data)} rows from cache")
            return data

        except Exception as e:
            logger.error(f"Error loading from cache: {e}")
            return None
        finally:
            db_manager.close_session(session)

    def _save_to_cache(self, data: pd.DataFrame) -> bool:
        """
        Save data to SQLite cache.

        Args:
            data: DataFrame to save

        Returns:
            True if successful
        """
        try:
            session = db_manager.get_session()

            saved_count = 0
            for timestamp, row in data.iterrows():
                # Check if already exists
                exists = session.query(PriceData).filter_by(
                    timestamp=timestamp
                ).first()

                if exists:
                    # Update existing record
                    exists.open = float(row["Open"])
                    exists.high = float(row["High"])
                    exists.low = float(row["Low"])
                    exists.close = float(row["Close"])
                    exists.volume = float(row["Volume"])
                else:
                    # Insert new record
                    price_data = PriceData(
                        timestamp=timestamp,
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float(row["Close"]),
                        volume=float(row["Volume"]),
                    )
                    session.add(price_data)
                    saved_count += 1

            session.commit()
            logger.info(f"Saved {saved_count} new rows to cache")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving to cache: {e}")
            return False
        finally:
            db_manager.close_session(session)

    def get_latest_data(self) -> Optional[pd.Series]:
        """
        Get the latest data point.

        Returns:
            Series with latest OHLCV data or None
        """
        latest = db_manager.get_latest_price()
        if latest:
            return pd.Series({
                "Open": latest.open,
                "High": latest.high,
                "Low": latest.low,
                "Close": latest.close,
                "Volume": latest.volume,
            }, name=latest.timestamp)
        return None

    def get_data_info(self) -> dict:
        """
        Get information about cached data.

        Returns:
            Dictionary with data statistics
        """
        try:
            session = db_manager.get_session()

            count = session.query(PriceData).count()

            if count == 0:
                return {
                    "total_rows": 0,
                    "earliest": None,
                    "latest": None,
                    "symbol": self.symbol,
                }

            earliest = session.query(PriceData).order_by(
                PriceData.timestamp.asc()
            ).first()

            latest = session.query(PriceData).order_by(
                PriceData.timestamp.desc()
            ).first()

            return {
                "total_rows": count,
                "earliest": earliest.timestamp if earliest else None,
                "latest": latest.timestamp if latest else None,
                "symbol": self.symbol,
            }

        except Exception as e:
            logger.error(f"Error getting data info: {e}")
            return {
                "total_rows": 0,
                "earliest": None,
                "latest": None,
                "symbol": self.symbol,
            }
        finally:
            db_manager.close_session(session)
