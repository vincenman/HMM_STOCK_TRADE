"""
Live price feed manager for real-time data updates.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Callable
import time
import threading

from utils.logger import setup_logger

logger = setup_logger(__name__)


class LivePriceFeed:
    """
    Manages live price updates from yfinance.

    Polls yfinance API at regular intervals to get latest price data.
    """

    def __init__(
        self,
        symbol: str = "BTC-USD",
        interval: str = "1m",
        update_interval: int = 60,
        callback: Optional[Callable] = None
    ):
        """
        Initialize live price feed.

        Args:
            symbol: Trading symbol
            interval: Data interval (1m, 5m, 15m, 1h)
            update_interval: Seconds between updates
            callback: Function to call with new data
        """
        self.symbol = symbol
        self.interval = interval
        self.update_interval = update_interval
        self.callback = callback

        # State
        self.is_running = False
        self.thread = None
        self.last_price = None
        self.last_update = None
        self.error_count = 0

        logger.info(f"Live price feed initialized for {symbol} @ {interval}")

    def start(self):
        """Start live price feed."""
        if self.is_running:
            logger.warning("Live price feed already running")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

        logger.info("Live price feed started")

    def stop(self):
        """Stop live price feed."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)

        logger.info("Live price feed stopped")

    def _update_loop(self):
        """Main update loop (runs in background thread)."""
        while self.is_running:
            try:
                # Fetch latest data
                ticker = yf.Ticker(self.symbol)

                # Get recent data (last 100 periods for indicators)
                end = datetime.utcnow()

                # Determine lookback based on interval
                if self.interval == "1m":
                    start = end - timedelta(hours=2)
                elif self.interval == "5m":
                    start = end - timedelta(hours=8)
                elif self.interval == "15m":
                    start = end - timedelta(days=1)
                else:  # 1h
                    start = end - timedelta(days=5)

                # Fetch data
                data = ticker.history(
                    start=start,
                    end=end,
                    interval=self.interval
                )

                if data is not None and len(data) > 0:
                    # Get latest price
                    latest_price = data['Close'].iloc[-1]
                    latest_time = data.index[-1]

                    self.last_price = latest_price
                    self.last_update = latest_time
                    self.error_count = 0

                    # Call callback with full data
                    if self.callback:
                        self.callback(latest_price, latest_time, data)

                    logger.debug(f"Price update: ${latest_price:,.2f} @ {latest_time}")
                else:
                    logger.warning("No data received from yfinance")
                    self.error_count += 1

            except Exception as e:
                logger.error(f"Error fetching price: {e}")
                self.error_count += 1

                # Stop if too many errors
                if self.error_count > 10:
                    logger.error("Too many errors, stopping price feed")
                    self.is_running = False
                    break

            # Wait for next update
            time.sleep(self.update_interval)

    def get_status(self) -> dict:
        """Get current feed status."""
        return {
            'is_running': self.is_running,
            'symbol': self.symbol,
            'interval': self.interval,
            'last_price': self.last_price,
            'last_update': self.last_update,
            'error_count': self.error_count,
        }


class LiveDataManager:
    """
    Manages live data with historical context for indicators.

    Combines live price updates with historical data to maintain
    a rolling window suitable for technical indicator calculation.
    """

    def __init__(
        self,
        symbol: str = "BTC-USD",
        interval: str = "1h",
        lookback_periods: int = 200
    ):
        """
        Initialize live data manager.

        Args:
            symbol: Trading symbol
            interval: Data interval
            lookback_periods: Number of historical periods to maintain
        """
        self.symbol = symbol
        self.interval = interval
        self.lookback_periods = lookback_periods

        # Historical data buffer
        self.data_buffer: Optional[pd.DataFrame] = None

        logger.info(f"Live data manager initialized: {lookback_periods} periods")

    def initialize(self, historical_data: pd.DataFrame):
        """
        Initialize with historical data.

        Args:
            historical_data: Historical OHLCV data
        """
        # Keep last N periods
        self.data_buffer = historical_data.tail(self.lookback_periods).copy()
        logger.info(f"Initialized with {len(self.data_buffer)} historical periods")

    def update(self, new_price: float, timestamp: datetime):
        """
        Update with new price tick.

        Args:
            new_price: Latest price
            timestamp: Timestamp
        """
        if self.data_buffer is None:
            logger.warning("Data buffer not initialized")
            return

        # Create new row (simplified - in real scenario would have OHLCV)
        new_row = pd.DataFrame({
            'Open': [new_price],
            'High': [new_price],
            'Low': [new_price],
            'Close': [new_price],
            'Volume': [0]  # Volume not available in real-time tick
        }, index=[timestamp])

        # Append and trim
        self.data_buffer = pd.concat([self.data_buffer, new_row])
        self.data_buffer = self.data_buffer.tail(self.lookback_periods)

        logger.debug(f"Buffer updated: {len(self.data_buffer)} periods")

    def get_data(self) -> pd.DataFrame:
        """Get current data buffer."""
        return self.data_buffer.copy() if self.data_buffer is not None else pd.DataFrame()
