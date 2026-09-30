"""
Signal generation with 8-condition voting system.
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
from config.settings import STRATEGY_DEFAULTS
from strategy.indicators import add_all_indicators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SignalGenerator:
    """Generate trading signals based on strategy rules."""

    def __init__(self, config: Dict = None):
        """
        Initialize signal generator.

        Args:
            config: Strategy configuration (uses defaults if None)
        """
        self.config = config or STRATEGY_DEFAULTS.copy()
        logger.info(f"SignalGenerator initialized with config: {self.config}")

    def evaluate_conditions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluate all 8 trading conditions.

        Conditions:
        1. RSI < 90
        2. Momentum > 1%
        3. Volatility < 6%
        4. Volume > 20-period SMA
        5. ADX > 25
        6. Price > 50 EMA
        7. Price > 200 EMA
        8. MACD > Signal Line

        Args:
            df: DataFrame with price data and indicators

        Returns:
            DataFrame with condition columns added
        """
        logger.info("Evaluating 8 trading conditions")

        # Ensure indicators are calculated
        if 'RSI' not in df.columns:
            df = add_all_indicators(df)

        # Condition 1: RSI < threshold
        df['Cond_RSI'] = df['RSI'] < self.config['rsi_threshold']

        # Condition 2: Momentum > threshold
        df['Cond_Momentum'] = df['Momentum'] > self.config['momentum_threshold']

        # Condition 3: Volatility < threshold
        df['Cond_Volatility'] = df['Volatility'] < self.config['volatility_threshold']

        # Condition 4: Volume > SMA
        df['Cond_Volume'] = df['Volume'] > df['Volume_SMA']

        # Condition 5: ADX > threshold
        df['Cond_ADX'] = df['ADX'] > self.config['adx_threshold']

        # Condition 6: Price > 50 EMA
        df['Cond_EMA50'] = df['Close'] > df['EMA_50']

        # Condition 7: Price > 200 EMA
        df['Cond_EMA200'] = df['Close'] > df['EMA_200']

        # Condition 8: MACD > Signal
        df['Cond_MACD'] = df['MACD'] > df['MACD_Signal']

        # Count conditions met
        condition_cols = [col for col in df.columns if col.startswith('Cond_')]
        df['Conditions_Met'] = df[condition_cols].sum(axis=1)

        logger.info(f"Conditions evaluated. Average conditions met: {df['Conditions_Met'].mean():.2f}/8")

        return df

    def generate_signals(
        self, df: pd.DataFrame, regime_states: np.ndarray, bull_state: int
    ) -> pd.DataFrame:
        """
        Generate buy/sell signals based on conditions and regime.

        Entry: HMM is in Bull state AND >= 7 conditions met
        Exit: Regime switches to Bear/Crash

        Args:
            df: DataFrame with price data and conditions
            regime_states: Array of HMM predicted states
            bull_state: Index of the bull state

        Returns:
            DataFrame with signal column added
        """
        logger.info("Generating trading signals")

        # Add regime states to dataframe
        # Align regime_states length with df (they may differ due to feature preparation)
        if len(regime_states) < len(df):
            # Pad beginning with NaN
            padded_states = np.full(len(df), np.nan)
            padded_states[-len(regime_states):] = regime_states
            df['Regime_State'] = padded_states
        else:
            df['Regime_State'] = regime_states[:len(df)]

        # Check if in bull regime
        df['In_Bull_Regime'] = df['Regime_State'] == bull_state

        # Generate entry signals
        # Entry: Bull regime AND >= required conditions met
        df['Entry_Signal'] = (
            df['In_Bull_Regime'] &
            (df['Conditions_Met'] >= self.config['required_conditions'])
        )

        # Generate exit signals
        # Exit: Not in bull regime (switched to bear or neutral)
        df['Exit_Signal'] = ~df['In_Bull_Regime']

        # Create combined signal column
        # 1 = Buy, 0 = Hold, -1 = Sell
        df['Signal'] = 0
        df.loc[df['Entry_Signal'], 'Signal'] = 1
        df.loc[df['Exit_Signal'], 'Signal'] = -1

        entry_count = df['Entry_Signal'].sum()
        exit_count = df['Exit_Signal'].sum()

        logger.info(f"Signals generated: {entry_count} entries, {exit_count} exits")

        return df

    def get_current_signal(
        self, df: pd.DataFrame, regime_state: int, bull_state: int
    ) -> Tuple[str, int, Dict]:
        """
        Get the current trading signal for the latest data point.

        Args:
            df: DataFrame with price data and indicators
            regime_state: Current HMM state
            bull_state: Index of the bull state

        Returns:
            Tuple of (signal_name, conditions_met, condition_details)
        """
        # Evaluate conditions
        df = self.evaluate_conditions(df)

        # Get latest row
        latest = df.iloc[-1]

        conditions_met = int(latest['Conditions_Met'])
        in_bull = regime_state == bull_state

        # Determine signal
        if in_bull and conditions_met >= self.config['required_conditions']:
            signal = "LONG"
        else:
            signal = "CASH"

        # Get condition details
        condition_details = {
            'RSI': {
                'value': latest['RSI'],
                'threshold': self.config['rsi_threshold'],
                'met': latest['Cond_RSI'],
                'condition': f"RSI < {self.config['rsi_threshold']}"
            },
            'Momentum': {
                'value': latest['Momentum'],
                'threshold': self.config['momentum_threshold'],
                'met': latest['Cond_Momentum'],
                'condition': f"Momentum > {self.config['momentum_threshold']*100:.0f}%"
            },
            'Volatility': {
                'value': latest['Volatility'],
                'threshold': self.config['volatility_threshold'],
                'met': latest['Cond_Volatility'],
                'condition': f"Volatility < {self.config['volatility_threshold']*100:.0f}%"
            },
            'Volume': {
                'value': latest['Volume'],
                'threshold': latest['Volume_SMA'],
                'met': latest['Cond_Volume'],
                'condition': "Volume > 20-SMA"
            },
            'ADX': {
                'value': latest['ADX'],
                'threshold': self.config['adx_threshold'],
                'met': latest['Cond_ADX'],
                'condition': f"ADX > {self.config['adx_threshold']}"
            },
            'EMA_50': {
                'value': latest['Close'],
                'threshold': latest['EMA_50'],
                'met': latest['Cond_EMA50'],
                'condition': "Price > 50 EMA"
            },
            'EMA_200': {
                'value': latest['Close'],
                'threshold': latest['EMA_200'],
                'met': latest['Cond_EMA200'],
                'condition': "Price > 200 EMA"
            },
            'MACD': {
                'value': latest['MACD'],
                'threshold': latest['MACD_Signal'],
                'met': latest['Cond_MACD'],
                'condition': "MACD > Signal"
            },
        }

        logger.info(f"Current signal: {signal} ({conditions_met}/{self.config['required_conditions']} conditions)")

        return signal, conditions_met, condition_details
