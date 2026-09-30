"""
Unit tests for HMM Engine.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models.hmm_engine import HMMEngine
from data.data_loader import DataLoader


class TestHMMEngine:
    """Test cases for HMM Engine."""

    @pytest.fixture(scope="class")
    def sample_data(self):
        """Fixture to fetch sample data for testing."""
        loader = DataLoader(symbol="BTC-USD", interval="1h")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=60)  # 60 days of data
        data = loader.fetch_data(start_date=start_date, end_date=end_date)
        return data

    def test_initialization(self):
        """Test HMM Engine initialization."""
        engine = HMMEngine(n_states=7, n_iter=100, random_state=42)
        assert engine.n_states == 7
        assert engine.n_iter == 100
        assert engine.random_state == 42
        assert engine.model is None
        assert not engine.is_trained()

    def test_prepare_features(self, sample_data):
        """Test feature preparation."""
        engine = HMMEngine()
        features, feature_df = engine.prepare_features(sample_data)

        # Check feature array
        assert isinstance(features, np.ndarray)
        assert features.ndim == 2
        assert features.shape[1] == 3  # 3 features

        # Check feature DataFrame
        assert isinstance(feature_df, pd.DataFrame)
        assert 'Returns' in feature_df.columns
        assert 'Range' in feature_df.columns
        assert 'Volume_Volatility' in feature_df.columns

        # Check no NaN/Inf
        assert not np.isnan(features).any()
        assert not np.isinf(features).any()

        print(f"✓ Prepared {features.shape[0]} samples with {features.shape[1]} features")
        print(f"  Feature stats:")
        print(f"    Returns: mean={features[:, 0].mean():.6f}, std={features[:, 0].std():.6f}")
        print(f"    Range: mean={features[:, 1].mean():.6f}, std={features[:, 1].std():.6f}")
        print(f"    Volume Vol: mean={features[:, 2].mean():.6f}, std={features[:, 2].std():.6f}")

    def test_train_model(self, sample_data):
        """Test model training."""
        engine = HMMEngine(n_states=7, n_iter=100, random_state=42)

        # Train
        success, error = engine.train(sample_data)

        # Check results
        assert success, f"Training failed: {error}"
        assert engine.is_trained()
        assert engine.model is not None
        assert engine.bull_state is not None
        assert engine.bear_state is not None
        assert engine.state_returns is not None

        # Check regime identification
        assert engine.bull_state >= 0
        assert engine.bull_state < engine.n_states
        assert engine.bear_state >= 0
        assert engine.bear_state < engine.n_states
        assert engine.bull_state != engine.bear_state

        # Bull state should have higher returns than bear state
        assert engine.state_returns[engine.bull_state] > engine.state_returns[engine.bear_state]

        print(f"✓ Model trained successfully")
        print(f"  Bull state: {engine.bull_state} (return: {engine.state_returns[engine.bull_state]:.4f})")
        print(f"  Bear state: {engine.bear_state} (return: {engine.state_returns[engine.bear_state]:.4f})")

    def test_predict(self, sample_data):
        """Test regime prediction."""
        engine = HMMEngine(n_states=7, n_iter=100, random_state=42)

        # Train first
        success, error = engine.train(sample_data)
        assert success

        # Predict
        states = engine.predict(sample_data)

        # Check predictions
        assert isinstance(states, np.ndarray)
        assert len(states) > 0
        assert states.min() >= 0
        assert states.max() < engine.n_states

        print(f"✓ Predicted {len(states)} states")
        print(f"  State distribution: {np.bincount(states)}")

    def test_predict_current_regime(self, sample_data):
        """Test current regime prediction."""
        engine = HMMEngine(n_states=7, n_iter=100, random_state=42)

        # Train first
        success, error = engine.train(sample_data)
        assert success

        # Predict current regime
        state, regime_name, confidence = engine.predict_current_regime(sample_data)

        # Check results
        assert isinstance(state, int)
        assert state >= 0
        assert state < engine.n_states
        assert isinstance(regime_name, str)
        assert regime_name in ["Bull Run", "Bear/Crash"] or regime_name.startswith("Neutral")
        assert 0.0 <= confidence <= 1.0

        print(f"✓ Current regime: {regime_name} (state {state}, confidence: {confidence:.2%})")

    def test_get_regime_info(self, sample_data):
        """Test getting regime information."""
        engine = HMMEngine(n_states=7, n_iter=100, random_state=42)

        # Before training - should be empty
        info = engine.get_regime_info()
        assert info == {}

        # After training
        success, error = engine.train(sample_data)
        assert success

        info = engine.get_regime_info()
        assert info["n_states"] == 7
        assert info["bull_state"] is not None
        assert info["bear_state"] is not None
        assert "state_returns" in info
        assert len(info["state_returns"]) == 7

        print(f"✓ Regime info: {info}")

    def test_insufficient_data(self):
        """Test training with insufficient data."""
        engine = HMMEngine()

        # Create minimal data (not enough for training)
        minimal_data = pd.DataFrame({
            'Open': [100] * 10,
            'High': [105] * 10,
            'Low': [95] * 10,
            'Close': [102] * 10,
            'Volume': [1000] * 10,
        })

        success, error = engine.train(minimal_data)

        # Should fail due to insufficient data
        assert not success
        assert error is not None
        assert "Insufficient data" in error

        print(f"✓ Correctly rejected insufficient data: {error}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
