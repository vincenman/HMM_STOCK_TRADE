"""
HMM Engine for market regime identification.
"""
import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from typing import Tuple, Optional, Dict
from datetime import datetime
import warnings

from config.settings import (
    HMM_N_STATES,
    HMM_N_ITER,
    HMM_RANDOM_STATE,
    HMM_COVARIANCE_TYPE,
    MODEL_CONVERGENCE_THRESHOLD,
    MODEL_MAX_RETRIES,
    MODEL_RETRY_SEEDS,
)
from utils.logger import setup_logger
from utils.validators import DataValidator

logger = setup_logger(__name__)

# Suppress convergence warnings from hmmlearn
warnings.filterwarnings('ignore', category=RuntimeWarning, module='hmmlearn')


class HMMEngine:
    """Hidden Markov Model engine for regime detection."""

    def __init__(
        self,
        n_states: int = HMM_N_STATES,
        n_iter: int = HMM_N_ITER,
        random_state: int = HMM_RANDOM_STATE,
    ):
        """
        Initialize HMM Engine.

        Args:
            n_states: Number of hidden states (default: 7)
            n_iter: Maximum training iterations
            random_state: Random seed for reproducibility
        """
        self.n_states = n_states
        self.n_iter = n_iter
        self.random_state = random_state
        self.model: Optional[GaussianHMM] = None
        self.validator = DataValidator()

        # Regime classification
        self.bull_state: Optional[int] = None
        self.bear_state: Optional[int] = None
        self.state_returns: Optional[np.ndarray] = None

        logger.info(f"HMM Engine initialized with {n_states} states")

    def prepare_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Prepare features for HMM training.

        Features:
        1. Returns
        2. Range (High - Low) / Close
        3. Volume Volatility

        Args:
            data: DataFrame with OHLCV data

        Returns:
            Tuple of (feature_array, feature_dataframe)
        """
        logger.info("Preparing features for HMM training")

        df = data.copy()

        # Feature 1: Returns
        df['Returns'] = df['Close'].pct_change()

        # Feature 2: Range
        df['Range'] = (df['High'] - df['Low']) / df['Close']

        # Feature 3: Volume Volatility
        df['Volume_Returns'] = df['Volume'].pct_change()
        df['Volume_Volatility'] = df['Volume_Returns'].rolling(window=20).std()

        # Drop NaN values
        df = df.dropna()

        # Extract feature columns
        feature_cols = ['Returns', 'Range', 'Volume_Volatility']
        features = df[feature_cols].values

        # Validate features
        is_valid, issues = self.validator.validate_features(features, feature_cols)
        if not is_valid:
            logger.warning(f"Feature validation issues: {issues}")
            # Handle NaN/Inf by replacing with 0
            features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

        logger.info(f"Prepared {len(features)} samples with {features.shape[1]} features")

        return features, df

    def train(self, data: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Train HMM model on data.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            Tuple of (success, error_message)
        """
        logger.info("Starting HMM model training")

        try:
            # Prepare features
            features, feature_df = self.prepare_features(data)

            if len(features) < 100:
                error_msg = f"Insufficient data for training: {len(features)} samples"
                logger.error(error_msg)
                return False, error_msg

            # Try training with different seeds if convergence fails
            for attempt, seed in enumerate(MODEL_RETRY_SEEDS[:MODEL_MAX_RETRIES]):
                logger.info(f"Training attempt {attempt + 1} with seed {seed}")

                try:
                    model = GaussianHMM(
                        n_components=self.n_states,
                        covariance_type=HMM_COVARIANCE_TYPE,
                        n_iter=self.n_iter,
                        random_state=seed,
                        verbose=False,
                    )

                    # Fit the model
                    model.fit(features)

                    # Check convergence
                    if not model.monitor_.converged:
                        logger.warning(f"Model did not converge (attempt {attempt + 1})")
                        if attempt < MODEL_MAX_RETRIES - 1:
                            continue

                    # Calculate score
                    score = model.score(features)
                    logger.info(f"Model score (log-likelihood): {score:.2f}")

                    if score < MODEL_CONVERGENCE_THRESHOLD:
                        logger.warning(f"Poor convergence score: {score}")
                        if attempt < MODEL_MAX_RETRIES - 1:
                            continue

                    # Success - store the model
                    self.model = model

                    # Identify regimes
                    self._identify_regimes(features, feature_df)

                    logger.info("Model training completed successfully")
                    logger.info(f"Bull state: {self.bull_state}, Bear state: {self.bear_state}")

                    return True, None

                except Exception as e:
                    logger.error(f"Training attempt {attempt + 1} failed: {e}")
                    if attempt < MODEL_MAX_RETRIES - 1:
                        continue
                    else:
                        return False, str(e)

            # All attempts failed
            return False, "Model failed to converge after all retries"

        except Exception as e:
            error_msg = f"Error during training: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _identify_regimes(self, features: np.ndarray, feature_df: pd.DataFrame):
        """
        Identify bull and bear regimes based on state returns.

        Args:
            features: Feature array used for training
            feature_df: DataFrame with features and returns
        """
        if self.model is None:
            raise ValueError("Model not trained")

        # Predict states for all data
        states = self.model.predict(features)

        # Calculate mean returns for each state
        state_returns = []
        for state in range(self.n_states):
            state_mask = states == state
            if state_mask.sum() > 0:
                mean_return = feature_df.loc[state_mask, 'Returns'].mean()
                state_returns.append(mean_return)
            else:
                state_returns.append(0.0)

        self.state_returns = np.array(state_returns)

        # Identify bull state (highest positive returns)
        self.bull_state = int(np.argmax(self.state_returns))

        # Identify bear state (lowest returns)
        self.bear_state = int(np.argmin(self.state_returns))

        logger.info(f"State returns: {self.state_returns}")
        logger.info(f"Bull state {self.bull_state}: {self.state_returns[self.bull_state]:.4f}")
        logger.info(f"Bear state {self.bear_state}: {self.state_returns[self.bear_state]:.4f}")

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """
        Predict regimes for new data.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            Array of predicted states
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        features, _ = self.prepare_features(data)
        states = self.model.predict(features)

        return states

    def predict_current_regime(self, data: pd.DataFrame) -> Tuple[int, str, float]:
        """
        Predict the current market regime.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            Tuple of (state_number, regime_name, confidence)
        """
        states = self.predict(data)
        current_state = states[-1]

        # Classify regime
        if current_state == self.bull_state:
            regime_name = "Bull Run"
        elif current_state == self.bear_state:
            regime_name = "Bear/Crash"
        else:
            regime_name = f"Neutral-{current_state}"

        # Calculate confidence (probability of being in this state)
        features, _ = self.prepare_features(data)

        try:
            # Get probability distribution for last observation
            log_prob, posteriors = self.model.score_samples(features[-1:])
            confidence = float(posteriors[0, current_state])
        except:
            confidence = 0.0

        return int(current_state), regime_name, confidence

    def get_regime_info(self) -> Dict[str, any]:
        """
        Get information about identified regimes.

        Returns:
            Dictionary with regime information
        """
        if self.state_returns is None:
            return {}

        return {
            "n_states": self.n_states,
            "bull_state": self.bull_state,
            "bear_state": self.bear_state,
            "state_returns": self.state_returns.tolist(),
            "bull_return": float(self.state_returns[self.bull_state]) if self.bull_state is not None else None,
            "bear_return": float(self.state_returns[self.bear_state]) if self.bear_state is not None else None,
        }

    def is_trained(self) -> bool:
        """Check if model is trained."""
        return self.model is not None
