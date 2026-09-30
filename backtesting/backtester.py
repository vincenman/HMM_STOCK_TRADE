"""
Backtesting engine for strategy simulation.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from data.database import db_manager, Trade
from strategy.signal_generator import SignalGenerator
from strategy.risk_manager import RiskManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Backtester:
    """Backtest trading strategy with full risk management."""

    def __init__(
        self,
        initial_capital: float = 10000.0,
        config: Dict = None,
    ):
        """
        Initialize backtester.

        Args:
            initial_capital: Starting capital (default $10,000)
            config: Strategy configuration
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.config = config

        # Initialize strategy components
        self.signal_generator = SignalGenerator(config)
        self.risk_manager = RiskManager(
            cooldown_hours=config.get('cooldown_hours', 48) if config else 48,
            leverage=config.get('leverage', 2.5) if config else 2.5,
            stop_loss_pct=config.get('stop_loss_pct', -0.05) if config else -0.05,
            take_profit_pct=config.get('take_profit_pct', 0.15) if config else 0.15,
        )

        # Position tracking
        self.in_position = False
        self.entry_price: Optional[float] = None
        self.entry_time: Optional[datetime] = None
        self.quantity: float = 0.0

        # Trade log
        self.trades: List[Dict] = []

        # Performance tracking
        self.portfolio_values: List[float] = []
        self.timestamps: List[datetime] = []

        logger.info(f"Backtester initialized with ${initial_capital:,.2f} capital")

    def run(
        self,
        data: pd.DataFrame,
        regime_states: np.ndarray,
        bull_state: int,
        bear_state: int,
    ) -> Dict:
        """
        Run backtest simulation.

        Args:
            data: DataFrame with price data
            regime_states: HMM predicted states
            bull_state: Index of bull state
            bear_state: Index of bear state

        Returns:
            Performance metrics dictionary
        """
        logger.info("Starting backtest simulation")

        # Generate signals
        data = self.signal_generator.evaluate_conditions(data)
        data = self.signal_generator.generate_signals(data, regime_states, bull_state)

        # Initialize tracking
        self.capital = self.initial_capital
        self.in_position = False

        # Iterate through each timestamp
        for idx in range(len(data)):
            row = data.iloc[idx]
            timestamp = row.name
            price = row['Close']
            signal = row['Signal']
            regime = row['Regime_State']
            conditions_met = row['Conditions_Met']

            # Check if in cooldown
            if self.risk_manager.is_in_cooldown(timestamp):
                # Cannot enter new positions during cooldown
                pass
            elif not self.in_position and signal == 1:
                # Entry signal
                self._enter_position(timestamp, price, regime, conditions_met)

            # Check exit conditions if in position
            if self.in_position:
                regime_is_bear = (regime == bear_state)
                should_exit, reason = self.risk_manager.check_exit_conditions(
                    self.entry_price, price, regime_is_bear
                )

                if should_exit or signal == -1:
                    self._exit_position(timestamp, price, reason, regime, conditions_met)

            # Track portfolio value
            portfolio_value = self._calculate_portfolio_value(price)
            self.portfolio_values.append(portfolio_value)
            self.timestamps.append(timestamp)

        # Close any open position at end
        if self.in_position:
            final_row = data.iloc[-1]
            self._exit_position(
                final_row.name,
                final_row['Close'],
                "End of backtest",
                final_row['Regime_State'],
                final_row['Conditions_Met']
            )

        # Calculate performance metrics
        metrics = self._calculate_metrics(data)

        logger.info(f"Backtest complete: {len(self.trades)} trades executed")

        return metrics

    def _enter_position(
        self,
        timestamp: datetime,
        price: float,
        regime: int,
        conditions_met: int,
    ):
        """Enter a long position."""
        # Calculate position size
        self.quantity = self.risk_manager.calculate_position_size(self.capital, price)

        # Update state
        self.in_position = True
        self.entry_price = price
        self.entry_time = timestamp

        # Deduct capital used (without leverage for accounting)
        position_cost = price * (self.quantity / self.risk_manager.leverage)
        self.capital -= position_cost

        logger.info(
            f"ENTRY @ {timestamp}: price=${price:.2f}, "
            f"qty={self.quantity:.6f}, cost=${position_cost:.2f}, "
            f"regime={regime}, conditions={conditions_met}/8"
        )

        # Log trade
        self.trades.append({
            'timestamp': timestamp,
            'action': 'BUY',
            'price': price,
            'quantity': self.quantity,
            'regime': regime,
            'conditions_met': conditions_met,
            'capital_remaining': self.capital,
        })

    def _exit_position(
        self,
        timestamp: datetime,
        price: float,
        reason: str,
        regime: int,
        conditions_met: int,
    ):
        """Exit the current position."""
        if not self.in_position:
            return

        # Calculate PnL
        pnl = self.risk_manager.calculate_pnl(
            self.entry_price,
            price,
            self.quantity,
            commission_rate=self.config.get('commission_rate', 0.001) if self.config else 0.001,
        )

        # Update capital
        position_value = price * (self.quantity / self.risk_manager.leverage)
        self.capital += position_value + pnl

        # Calculate return
        hold_time = (timestamp - self.entry_time).total_seconds() / 3600  # hours
        return_pct = (price - self.entry_price) / self.entry_price

        logger.info(
            f"EXIT @ {timestamp}: price=${price:.2f}, "
            f"pnl=${pnl:.2f} ({return_pct*100:.2f}%), "
            f"hold={hold_time:.1f}h, reason={reason}"
        )

        # Log trade
        self.trades.append({
            'timestamp': timestamp,
            'action': 'SELL',
            'price': price,
            'quantity': self.quantity,
            'pnl': pnl,
            'return_pct': return_pct,
            'hold_time_hours': hold_time,
            'reason': reason,
            'regime': regime,
            'conditions_met': conditions_met,
            'capital_after': self.capital,
        })

        # Trigger cooldown
        self.risk_manager.trigger_cooldown(timestamp)

        # Reset position
        self.in_position = False
        self.entry_price = None
        self.entry_time = None
        self.quantity = 0.0

    def _calculate_portfolio_value(self, current_price: float) -> float:
        """Calculate current portfolio value."""
        if self.in_position:
            position_value = current_price * (self.quantity / self.risk_manager.leverage)
            unrealized_pnl = (current_price - self.entry_price) * self.quantity
            return self.capital + position_value + unrealized_pnl
        else:
            return self.capital

    def _calculate_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate performance metrics."""
        logger.info("Calculating performance metrics")

        # Final values
        final_capital = self.capital
        total_return = (final_capital - self.initial_capital) / self.initial_capital

        # Trade statistics
        completed_trades = [t for t in self.trades if t['action'] == 'SELL']
        num_trades = len(completed_trades)

        if num_trades > 0:
            winning_trades = [t for t in completed_trades if t['pnl'] > 0]
            losing_trades = [t for t in completed_trades if t['pnl'] <= 0]

            win_rate = len(winning_trades) / num_trades
            avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
            avg_return = np.mean([t['return_pct'] for t in completed_trades])
            avg_hold_time = np.mean([t['hold_time_hours'] for t in completed_trades])

            total_profit = sum([t['pnl'] for t in winning_trades])
            total_loss = abs(sum([t['pnl'] for t in losing_trades]))
            profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            avg_return = 0
            avg_hold_time = 0
            profit_factor = 0

        # Buy & Hold comparison
        buy_hold_return = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
        alpha = total_return - buy_hold_return

        # Drawdown calculation
        portfolio_series = pd.Series(self.portfolio_values, index=self.timestamps)
        cumulative_max = portfolio_series.cummax()
        drawdown = (portfolio_series - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()

        # Sharpe ratio (simplified - assuming 0% risk-free rate)
        if len(self.portfolio_values) > 1:
            returns = pd.Series(self.portfolio_values).pct_change().dropna()
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0

        metrics = {
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'buy_hold_return': buy_hold_return,
            'buy_hold_return_pct': buy_hold_return * 100,
            'alpha': alpha,
            'alpha_pct': alpha * 100,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_return': avg_return,
            'avg_return_pct': avg_return * 100,
            'avg_hold_time_hours': avg_hold_time,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'sharpe_ratio': sharpe_ratio,
        }

        logger.info(
            f"Metrics: Return={total_return*100:.2f}%, "
            f"Alpha={alpha*100:.2f}%, "
            f"Win Rate={win_rate*100:.1f}%, "
            f"Max DD={max_drawdown*100:.2f}%"
        )

        return metrics

    def get_trades_dataframe(self) -> pd.DataFrame:
        """
        Get trades as a DataFrame.

        Returns:
            DataFrame with all trade records
        """
        if not self.trades:
            return pd.DataFrame()

        return pd.DataFrame(self.trades)

    def save_trades_to_db(self):
        """Save all trades to database."""
        if not self.trades:
            logger.info("No trades to save")
            return

        session = db_manager.get_session()
        try:
            for trade in self.trades:
                trade_record = Trade(
                    timestamp=trade['timestamp'],
                    action=trade['action'],
                    price=trade['price'],
                    quantity=trade['quantity'],
                    pnl=trade.get('pnl'),
                    regime=str(trade.get('regime')),
                    conditions_met=trade.get('conditions_met'),
                    portfolio_value=trade.get('capital_after', trade.get('capital_remaining')),
                    notes=trade.get('reason', ''),
                )
                session.add(trade_record)

            session.commit()
            logger.info(f"Saved {len(self.trades)} trades to database")

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving trades: {e}")
        finally:
            db_manager.close_session(session)

    def get_portfolio_history(self) -> pd.DataFrame:
        """
        Get portfolio value history.

        Returns:
            DataFrame with timestamps and portfolio values
        """
        return pd.DataFrame({
            'timestamp': self.timestamps,
            'portfolio_value': self.portfolio_values,
        }).set_index('timestamp')
