"""
Paper trading engine for real-time simulation without real money.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import threading

from config.settings import STRATEGY_DEFAULTS
from strategy import SignalGenerator, RiskManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PaperTradingEngine:
    """
    Real-time paper trading engine for live simulation.

    Tracks positions, executes simulated trades, and monitors performance
    without risking real capital.
    """

    def __init__(
        self,
        initial_capital: float = 10000.0,
        model_engine = None,
        config: Dict = None
    ):
        """
        Initialize paper trading engine.

        Args:
            initial_capital: Starting capital
            model_engine: Trained HMM engine
            config: Strategy configuration
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.model_engine = model_engine
        self.config = config or STRATEGY_DEFAULTS.copy()

        # Components
        self.signal_generator = SignalGenerator(self.config)
        self.risk_manager = RiskManager(
            cooldown_hours=self.config['cooldown_hours'],
            leverage=self.config['leverage'],
            stop_loss_pct=self.config['stop_loss_pct'],
            take_profit_pct=self.config['take_profit_pct']
        )

        # Position tracking
        self.in_position = False
        self.position_entry_price = 0.0
        self.position_quantity = 0.0
        self.position_entry_time = None

        # Trade log
        self.trades: List[Dict] = []
        self.current_trade_id = 0

        # Performance tracking
        self.peak_capital = initial_capital
        self.max_drawdown = 0.0
        self.total_pnl = 0.0

        # Real-time tracking
        self.is_running = False
        self.last_price = 0.0
        self.last_update_time = None

        logger.info(f"Paper trading engine initialized with ${initial_capital:,.2f}")

    def start(self):
        """Start paper trading engine."""
        self.is_running = True
        logger.info("Paper trading engine started")

    def stop(self):
        """Stop paper trading engine."""
        self.is_running = False
        logger.info("Paper trading engine stopped")

    def update_price(self, price: float, timestamp: datetime, data: pd.DataFrame):
        """
        Update with new price tick and check for signals.

        Args:
            price: Current BTC price
            timestamp: Current timestamp
            data: Recent price data with indicators
        """
        if not self.is_running:
            return

        self.last_price = price
        self.last_update_time = timestamp

        # Check if we have a trained model
        if self.model_engine is None or not hasattr(self.model_engine, 'bull_state'):
            logger.warning("Model not trained, skipping signal check")
            return

        # Predict current regime
        try:
            regime_state, regime_name, confidence = self.model_engine.predict_current_regime(data)

            # Generate signal
            signal, conditions_met, details = self.signal_generator.get_current_signal(
                data, regime_state, self.model_engine.bull_state
            )

            # Process signal
            if self.in_position:
                # Check exit conditions
                self._check_exit(price, timestamp, regime_state, signal)
            else:
                # Check entry conditions
                self._check_entry(price, timestamp, regime_state, signal, conditions_met)

        except Exception as e:
            logger.error(f"Error processing price update: {e}")

    def _check_entry(
        self,
        price: float,
        timestamp: datetime,
        regime_state: int,
        signal: str,
        conditions_met: int
    ):
        """Check if we should enter a position."""
        # Check cooldown
        if self.risk_manager.is_in_cooldown(timestamp):
            return

        # Check signal
        if signal != "LONG":
            return

        # Enter position
        position_size = self.risk_manager.calculate_position_size(
            self.capital, price
        )

        if position_size > 0:
            self.in_position = True
            self.position_entry_price = price
            self.position_quantity = position_size
            self.position_entry_time = timestamp

            # Calculate cost including commission
            cost = position_size * price
            commission = cost * self.config['commission_rate']
            self.capital -= (cost + commission)

            # Log trade
            trade = {
                'id': self.current_trade_id,
                'action': 'BUY',
                'timestamp': timestamp,
                'price': price,
                'quantity': position_size,
                'cost': cost,
                'commission': commission,
                'capital_after': self.capital,
                'regime': regime_state,
                'conditions_met': conditions_met,
                'reason': 'Entry signal'
            }
            self.trades.append(trade)
            self.current_trade_id += 1

            logger.info(
                f"ENTER POSITION @ {timestamp}: "
                f"price=${price:,.2f}, qty={position_size:.6f}, "
                f"cost=${cost:,.2f}, regime={regime_state}, "
                f"conditions={conditions_met}/8"
            )

    def _check_exit(
        self,
        price: float,
        timestamp: datetime,
        regime_state: int,
        signal: str
    ):
        """Check if we should exit position."""
        # Calculate current P&L
        pnl_pct = (price - self.position_entry_price) / self.position_entry_price

        # Check exit conditions
        should_exit, exit_reason = self.risk_manager.check_exit_conditions(
            entry_price=self.position_entry_price,
            current_price=price
        )

        # Also exit if signal is CASH
        if signal == "CASH" and not should_exit:
            should_exit = True
            exit_reason = "Exit signal (regime change)"

        if should_exit:
            # Exit position
            proceeds = self.position_quantity * price
            commission = proceeds * self.config['commission_rate']
            self.capital += (proceeds - commission)

            # Calculate P&L
            cost = self.position_quantity * self.position_entry_price
            pnl = proceeds - cost - (2 * commission)  # Entry + exit commission
            pnl_pct = (pnl / cost) * 100

            # Hold time
            hold_time = (timestamp - self.position_entry_time).total_seconds() / 3600

            # Update performance
            self.total_pnl += pnl
            if self.capital > self.peak_capital:
                self.peak_capital = self.capital

            drawdown = (self.peak_capital - self.capital) / self.peak_capital * 100
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown

            # Log trade
            trade = {
                'id': self.current_trade_id,
                'action': 'SELL',
                'timestamp': timestamp,
                'price': price,
                'quantity': self.position_quantity,
                'proceeds': proceeds,
                'commission': commission,
                'capital_after': self.capital,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'hold_time_hours': hold_time,
                'entry_price': self.position_entry_price,
                'regime': regime_state,
                'reason': exit_reason
            }
            self.trades.append(trade)
            self.current_trade_id += 1

            # Reset position
            self.in_position = False
            self.position_entry_price = 0.0
            self.position_quantity = 0.0
            self.position_entry_time = None

            # Trigger cooldown
            self.risk_manager.trigger_cooldown(timestamp)

            logger.info(
                f"EXIT POSITION @ {timestamp}: "
                f"price=${price:,.2f}, pnl=${pnl:,.2f} ({pnl_pct:+.2f}%), "
                f"hold={hold_time:.1f}h, reason={exit_reason}"
            )

    def get_current_status(self) -> Dict:
        """Get current paper trading status."""
        status = {
            'is_running': self.is_running,
            'initial_capital': self.initial_capital,
            'current_capital': self.capital,
            'total_pnl': self.total_pnl,
            'total_return_pct': (self.capital - self.initial_capital) / self.initial_capital * 100,
            'in_position': self.in_position,
            'last_price': self.last_price,
            'last_update': self.last_update_time,
            'num_trades': len([t for t in self.trades if t['action'] == 'SELL']),
            'max_drawdown_pct': self.max_drawdown,
        }

        # Add position details if in position
        if self.in_position:
            unrealized_pnl = (self.last_price - self.position_entry_price) * self.position_quantity
            unrealized_pnl_pct = (self.last_price - self.position_entry_price) / self.position_entry_price * 100

            status.update({
                'position_entry_price': self.position_entry_price,
                'position_quantity': self.position_quantity,
                'position_entry_time': self.position_entry_time,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_pct': unrealized_pnl_pct,
                'position_value': self.position_quantity * self.last_price,
            })

        return status

    def get_trades_df(self) -> pd.DataFrame:
        """Get trades as DataFrame."""
        if not self.trades:
            return pd.DataFrame()

        return pd.DataFrame(self.trades)

    def reset(self):
        """Reset paper trading engine."""
        self.capital = self.initial_capital
        self.in_position = False
        self.position_entry_price = 0.0
        self.position_quantity = 0.0
        self.position_entry_time = None
        self.trades = []
        self.current_trade_id = 0
        self.peak_capital = self.initial_capital
        self.max_drawdown = 0.0
        self.total_pnl = 0.0

        logger.info("Paper trading engine reset")
