"""
Unit tests for technical indicators.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategy.indicators import TechnicalIndicators, add_all_indicators


class TestTechnicalIndicators:
    """Test cases for technical indicators."""

    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data."""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='h')
        np.random.seed(42)

        # Generate synthetic price data
        close_prices = 50000 + np.cumsum(np.random.randn(100) * 100)

        data = pd.DataFrame({
            'Open': close_prices + np.random.randn(100) * 50,
            'High': close_prices + np.abs(np.random.randn(100) * 100),
            'Low': close_prices - np.abs(np.random.randn(100) * 100),
            'Close': close_prices,
            'Volume': np.abs(np.random.randn(100) * 1000000),
        }, index=dates)

        return data

    def test_rsi_calculation(self, sample_data):
        """Test RSI calculation."""
        indicators = TechnicalIndicators()
        rsi = indicators.calculate_rsi(sample_data['Close'], period=14)

        # Check output
        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(sample_data)

        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert valid_rsi.min() >= 0
        assert valid_rsi.max() <= 100

        print(f"✓ RSI calculated: min={valid_rsi.min():.2f}, max={valid_rsi.max():.2f}")

    def test_ema_calculation(self, sample_data):
        """Test EMA calculation."""
        indicators = TechnicalIndicators()
        ema_50 = indicators.calculate_ema(sample_data['Close'], period=50)

        assert isinstance(ema_50, pd.Series)
        assert len(ema_50) == len(sample_data)
        assert not ema_50.iloc[-1] == 0  # Should have valid values

        print(f"✓ EMA_50 calculated: last value={ema_50.iloc[-1]:.2f}")

    def test_macd_calculation(self, sample_data):
        """Test MACD calculation."""
        indicators = TechnicalIndicators()
        macd, signal, histogram = indicators.calculate_macd(sample_data['Close'])

        assert isinstance(macd, pd.Series)
        assert isinstance(signal, pd.Series)
        assert isinstance(histogram, pd.Series)

        assert len(macd) == len(sample_data)
        assert len(signal) == len(sample_data)
        assert len(histogram) == len(sample_data)

        print(f"✓ MACD calculated: macd={macd.iloc[-1]:.2f}, signal={signal.iloc[-1]:.2f}")

    def test_adx_calculation(self, sample_data):
        """Test ADX calculation."""
        indicators = TechnicalIndicators()
        adx = indicators.calculate_adx(
            sample_data['High'],
            sample_data['Low'],
            sample_data['Close']
        )

        assert isinstance(adx, pd.Series)
        assert len(adx) == len(sample_data)

        # ADX should be positive
        valid_adx = adx.dropna()
        assert valid_adx.min() >= 0

        print(f"✓ ADX calculated: last value={adx.iloc[-1]:.2f}")

    def test_momentum_calculation(self, sample_data):
        """Test momentum calculation."""
        indicators = TechnicalIndicators()
        momentum = indicators.calculate_momentum(sample_data['Close'], period=10)

        assert isinstance(momentum, pd.Series)
        assert len(momentum) == len(sample_data)

        print(f"✓ Momentum calculated: last value={momentum.iloc[-1]*100:.2f}%")

    def test_volatility_calculation(self, sample_data):
        """Test volatility calculation."""
        indicators = TechnicalIndicators()
        volatility = indicators.calculate_volatility(sample_data['Close'], period=20)

        assert isinstance(volatility, pd.Series)
        assert len(volatility) == len(sample_data)

        # Volatility should be positive
        valid_vol = volatility.dropna()
        assert valid_vol.min() >= 0

        print(f"✓ Volatility calculated: last value={volatility.iloc[-1]*100:.2f}%")

    def test_add_all_indicators(self, sample_data):
        """Test adding all indicators to DataFrame."""
        df = add_all_indicators(sample_data.copy())

        # Check that indicators were added
        expected_indicators = [
            'RSI', 'EMA_50', 'EMA_200', 'SMA_20',
            'MACD', 'MACD_Signal', 'MACD_Hist',
            'ADX', 'Momentum', 'Volatility',
            'Volume_SMA', 'BB_Upper', 'BB_Middle', 'BB_Lower', 'ATR'
        ]

        for indicator in expected_indicators:
            assert indicator in df.columns, f"Missing indicator: {indicator}"

        print(f"✓ All {len(expected_indicators)} indicators added successfully")
        print(f"  Columns: {df.columns.tolist()}")

    def test_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation."""
        indicators = TechnicalIndicators()
        upper, middle, lower = indicators.calculate_bollinger_bands(
            sample_data['Close'], period=20
        )

        assert isinstance(upper, pd.Series)
        assert isinstance(middle, pd.Series)
        assert isinstance(lower, pd.Series)

        # Upper should be > Middle > Lower
        valid_idx = ~(upper.isna() | middle.isna() | lower.isna())
        assert (upper[valid_idx] >= middle[valid_idx]).all()
        assert (middle[valid_idx] >= lower[valid_idx]).all()

        print(f"✓ Bollinger Bands: upper={upper.iloc[-1]:.2f}, middle={middle.iloc[-1]:.2f}, lower={lower.iloc[-1]:.2f}")

    def test_atr_calculation(self, sample_data):
        """Test ATR calculation."""
        indicators = TechnicalIndicators()
        atr = indicators.calculate_atr(
            sample_data['High'],
            sample_data['Low'],
            sample_data['Close']
        )

        assert isinstance(atr, pd.Series)
        assert len(atr) == len(sample_data)

        # ATR should be positive
        valid_atr = atr.dropna()
        assert valid_atr.min() >= 0

        print(f"✓ ATR calculated: last value={atr.iloc[-1]:.2f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
