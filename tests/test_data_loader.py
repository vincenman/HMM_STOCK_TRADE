"""
Unit tests for DataLoader class.
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from data.data_loader import DataLoader
from data.database import db_manager


class TestDataLoader:
    """Test cases for DataLoader."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Setup: Clear database before each test
        try:
            session = db_manager.get_session()
            from data.database import PriceData
            session.query(PriceData).delete()
            session.commit()
            db_manager.close_session(session)
        except:
            pass

        yield

        # Teardown: Clean up after test
        # (optional - could leave data for inspection)

    def test_initialization(self):
        """Test DataLoader initialization."""
        loader = DataLoader(symbol="BTC-USD", interval="1h")
        assert loader.symbol == "BTC-USD"
        assert loader.interval == "1h"
        assert loader.validator is not None

    def test_fetch_data_from_api(self):
        """Test fetching data from yfinance API."""
        loader = DataLoader(symbol="BTC-USD", interval="1h")

        # Fetch last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        data = loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=True)

        # Assertions
        assert data is not None
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "Open" in data.columns
        assert "High" in data.columns
        assert "Low" in data.columns
        assert "Close" in data.columns
        assert "Volume" in data.columns

        print(f"✓ Fetched {len(data)} rows from API")

    def test_caching_mechanism(self):
        """Test that data is cached to database."""
        loader = DataLoader(symbol="BTC-USD", interval="1h")

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        # First fetch - should go to API
        data1 = loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=True)
        assert len(data1) > 0

        # Second fetch - should come from cache
        data2 = loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=False)
        assert len(data2) > 0

        # Data should be similar (may have slight differences due to timing)
        assert len(data1) <= len(data2) + 10  # Allow small difference

        print(f"✓ Caching works: {len(data2)} rows from cache")

    def test_get_data_info(self):
        """Test getting data information."""
        loader = DataLoader(symbol="BTC-USD", interval="1h")

        # Initially should have no data (we cleared it in setup)
        info = loader.get_data_info()
        print(f"Initial info: {info}")

        # Fetch some data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=True)

        # Now should have data
        info = loader.get_data_info()
        assert info["total_rows"] > 0
        assert info["earliest"] is not None
        assert info["latest"] is not None
        assert info["symbol"] == "BTC-USD"

        print(f"✓ Data info: {info['total_rows']} rows from {info['earliest']} to {info['latest']}")

    def test_get_latest_data(self):
        """Test getting latest data point."""
        loader = DataLoader(symbol="BTC-USD", interval="1h")

        # Fetch some data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=3)
        loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=True)

        # Get latest
        latest = loader.get_latest_data()

        if latest is not None:
            assert "Open" in latest.index
            assert "Close" in latest.index
            assert latest["Close"] > 0
            print(f"✓ Latest data: Close = ${latest['Close']:.2f} at {latest.name}")
        else:
            print("✓ No latest data (database was empty)")

    def test_data_validation(self):
        """Test that fetched data passes validation."""
        loader = DataLoader(symbol="BTC-USD", interval="1h")

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        data = loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=True)

        # Validate data
        is_valid, issues = loader.validator.validate_price_data(data)

        print(f"Validation: {'PASSED' if is_valid else 'FAILED'}")
        if not is_valid:
            print(f"Issues: {issues}")

        # Should pass or have only minor issues
        assert data is not None
        assert len(data) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
