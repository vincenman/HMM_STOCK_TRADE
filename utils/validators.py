"""
Data validation utilities for price data and model inputs.
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataValidator:
    """Validates data quality and integrity."""

    def __init__(
        self,
        max_hourly_return: float = 0.20,
        max_volume_spike: float = 10.0,
        max_gap_hours: int = 3,
    ):
        """
        Initialize data validator.

        Args:
            max_hourly_return: Maximum acceptable hourly return (default 20%)
            max_volume_spike: Maximum volume spike as multiple of average
            max_gap_hours: Maximum acceptable gap in hours
        """
        self.max_hourly_return = max_hourly_return
        self.max_volume_spike = max_volume_spike
        self.max_gap_hours = max_gap_hours

    def validate_price_data(
        self, df: pd.DataFrame
    ) -> Tuple[bool, List[str]]:
        """
        Validate price data quality.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        # Check required columns
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")
            return False, issues

        # Check for empty data
        if df.empty:
            issues.append("DataFrame is empty")
            return False, issues

        # Check for negative values
        if (df[["Open", "High", "Low", "Close", "Volume"]] < 0).any().any():
            issues.append("Found negative price or volume values")

        # Check for NaN values
        nan_cols = df[required_cols].columns[df[required_cols].isna().any()].tolist()
        if nan_cols:
            issues.append(f"Found NaN values in columns: {nan_cols}")

        # Check OHLC consistency
        invalid_ohlc = (
            (df["High"] < df["Low"]) |
            (df["High"] < df["Open"]) |
            (df["High"] < df["Close"]) |
            (df["Low"] > df["Open"]) |
            (df["Low"] > df["Close"])
        )
        if invalid_ohlc.any():
            issues.append(f"Found {invalid_ohlc.sum()} rows with invalid OHLC relationships")

        # Check for outlier returns
        returns = df["Close"].pct_change().abs()
        outliers = returns > self.max_hourly_return
        if outliers.any():
            issues.append(
                f"Found {outliers.sum()} extreme returns (>{self.max_hourly_return*100}%)"
            )
            logger.warning(f"Outlier returns at indices: {df[outliers].index.tolist()[:5]}")

        # Check for volume spikes
        avg_volume = df["Volume"].rolling(window=24).mean()
        volume_spikes = df["Volume"] > (avg_volume * self.max_volume_spike)
        if volume_spikes.any():
            issues.append(
                f"Found {volume_spikes.sum()} volume spikes (>{self.max_volume_spike}x average)"
            )
            logger.warning(f"Volume spikes at indices: {df[volume_spikes].index.tolist()[:5]}")

        # Check for time gaps
        if isinstance(df.index, pd.DatetimeIndex):
            time_diffs = df.index.to_series().diff()
            expected_freq = pd.Timedelta(hours=1)
            gaps = time_diffs > expected_freq * self.max_gap_hours
            if gaps.any():
                issues.append(
                    f"Found {gaps.sum()} time gaps > {self.max_gap_hours} hours"
                )
                logger.warning(f"Time gaps at indices: {df[gaps].index.tolist()[:5]}")

        is_valid = len(issues) == 0

        if is_valid:
            logger.info("Data validation passed")
        else:
            logger.warning(f"Data validation found {len(issues)} issues")

        return is_valid, issues

    def validate_features(
        self, features: np.ndarray, feature_names: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate feature array for model training.

        Args:
            features: Feature array (n_samples, n_features)
            feature_names: Optional names for features

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        # Check for NaN or Inf
        if np.isnan(features).any():
            nan_count = np.isnan(features).sum()
            issues.append(f"Found {nan_count} NaN values in features")

        if np.isinf(features).any():
            inf_count = np.isinf(features).sum()
            issues.append(f"Found {inf_count} Inf values in features")

        # Check shape
        if features.ndim != 2:
            issues.append(f"Features must be 2D array, got shape {features.shape}")
            return False, issues

        # Check for constant features
        for i in range(features.shape[1]):
            if np.std(features[:, i]) < 1e-10:
                feat_name = feature_names[i] if feature_names else f"Feature {i}"
                issues.append(f"{feat_name} has zero variance (constant)")

        is_valid = len(issues) == 0

        if is_valid:
            logger.info("Feature validation passed")
        else:
            logger.error(f"Feature validation found {len(issues)} issues")

        return is_valid, issues

    def handle_missing_data(
        self, df: pd.DataFrame, method: str = "ffill"
    ) -> pd.DataFrame:
        """
        Handle missing data in DataFrame.

        Args:
            df: Input DataFrame
            method: Method to handle missing data ('ffill', 'drop', 'interpolate')

        Returns:
            DataFrame with missing data handled
        """
        initial_len = len(df)

        if method == "ffill":
            df = df.ffill().bfill()
        elif method == "drop":
            df = df.dropna()
        elif method == "interpolate":
            df = df.interpolate(method="time")
        else:
            raise ValueError(f"Unknown method: {method}")

        final_len = len(df)

        if final_len < initial_len:
            logger.info(f"Removed {initial_len - final_len} rows due to missing data")

        return df
