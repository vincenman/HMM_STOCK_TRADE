"""
Technical indicators implementation.
All indicators are implemented using pandas and numpy (no external TA libraries needed).
"""
import pandas as pd
import numpy as np
from typing import Tuple
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators for trading strategy."""

    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).

        Args:
            data: Price series (typically Close)
            period: RSI period (default 14)

        Returns:
            RSI values (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA).

        Args:
            data: Price series
            period: EMA period

        Returns:
            EMA values
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA).

        Args:
            data: Price series
            period: SMA period

        Returns:
            SMA values
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def calculate_macd(
        data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            data: Price series
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)

        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_adx(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Calculate Average Directional Index (ADX).

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ADX period (default 14)

        Returns:
            ADX values
        """
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Calculate Directional Movement
        dm_plus = high.diff()
        dm_minus = -low.diff()

        dm_plus[dm_plus < 0] = 0
        dm_minus[dm_minus < 0] = 0
        dm_plus[(dm_plus < dm_minus)] = 0
        dm_minus[(dm_minus < dm_plus)] = 0

        # Smooth TR and DM
        atr = tr.rolling(window=period).mean()
        di_plus = 100 * (dm_plus.rolling(window=period).mean() / atr)
        di_minus = 100 * (dm_minus.rolling(window=period).mean() / atr)

        # Calculate DX and ADX
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = dx.rolling(window=period).mean()

        return adx

    @staticmethod
    def calculate_momentum(data: pd.Series, period: int = 10) -> pd.Series:
        """
        Calculate Momentum (rate of change).

        Args:
            data: Price series
            period: Lookback period (default 10)

        Returns:
            Momentum as percentage change
        """
        return data.pct_change(periods=period)

    @staticmethod
    def calculate_volatility(data: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate rolling volatility (standard deviation of returns).

        Args:
            data: Price series
            period: Window period (default 20)

        Returns:
            Volatility values
        """
        returns = data.pct_change()
        volatility = returns.rolling(window=period).std()
        return volatility

    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series, period: int = 20, std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.

        Args:
            data: Price series
            period: SMA period (default 20)
            std_dev: Standard deviation multiplier (default 2.0)

        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return upper, middle, lower

    @staticmethod
    def calculate_atr(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range (ATR).

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period (default 14)

        Returns:
            ATR values
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = tr.rolling(window=period).mean()
        return atr


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators to a DataFrame.

    Args:
        df: DataFrame with OHLCV data

    Returns:
        DataFrame with all indicators added
    """
    logger.info("Calculating technical indicators")

    indicators = TechnicalIndicators()

    # Price-based indicators
    df['RSI'] = indicators.calculate_rsi(df['Close'], period=14)
    df['EMA_50'] = indicators.calculate_ema(df['Close'], period=50)
    df['EMA_200'] = indicators.calculate_ema(df['Close'], period=200)
    df['SMA_20'] = indicators.calculate_sma(df['Close'], period=20)

    # MACD
    macd, signal, histogram = indicators.calculate_macd(df['Close'])
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Hist'] = histogram

    # ADX
    df['ADX'] = indicators.calculate_adx(df['High'], df['Low'], df['Close'])

    # Momentum
    df['Momentum'] = indicators.calculate_momentum(df['Close'], period=10)

    # Volatility
    df['Volatility'] = indicators.calculate_volatility(df['Close'], period=20)

    # Volume indicators
    df['Volume_SMA'] = indicators.calculate_sma(df['Volume'], period=20)

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = indicators.calculate_bollinger_bands(df['Close'])
    df['BB_Upper'] = bb_upper
    df['BB_Middle'] = bb_middle
    df['BB_Lower'] = bb_lower

    # ATR
    df['ATR'] = indicators.calculate_atr(df['High'], df['Low'], df['Close'])

    logger.info(f"Added {len([col for col in df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']])} indicators")

    return df
