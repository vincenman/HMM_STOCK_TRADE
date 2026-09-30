"""
Risk management rules including cooldown, position sizing, and exit rules.
"""
from datetime import datetime, timedelta
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RiskManager:
    """Manage trading risk with cooldown, position sizing, and stop-loss/take-profit."""

    def __init__(
        self,
        cooldown_hours: int = 48,
        leverage: float = 2.5,
        stop_loss_pct: float = -0.05,
        take_profit_pct: float = 0.15,
        max_position_size: float = 0.95,
    ):
        """
        Initialize risk manager.

        Args:
            cooldown_hours: Hours to wait after position close (default 48)
            leverage: Position leverage multiplier (default 2.5x)
            stop_loss_pct: Stop loss percentage (default -5%)
            take_profit_pct: Take profit percentage (default +15%)
            max_position_size: Maximum position size as fraction of capital (default 95%)
        """
        self.cooldown_hours = cooldown_hours
        self.leverage = leverage
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_position_size = max_position_size

        # Track cooldown
        self.last_exit_time: Optional[datetime] = None
        self.in_cooldown = False

        logger.info(
            f"RiskManager initialized: cooldown={cooldown_hours}h, "
            f"leverage={leverage}x, stop_loss={stop_loss_pct*100:.1f}%, "
            f"take_profit={take_profit_pct*100:.1f}%"
        )

    def is_in_cooldown(self, current_time: datetime) -> bool:
        """
        Check if currently in cooldown period.

        Args:
            current_time: Current timestamp

        Returns:
            True if in cooldown
        """
        if self.last_exit_time is None:
            return False

        time_since_exit = current_time - self.last_exit_time
        hours_since_exit = time_since_exit.total_seconds() / 3600

        in_cooldown = hours_since_exit < self.cooldown_hours

        if in_cooldown:
            remaining_hours = self.cooldown_hours - hours_since_exit
            logger.debug(f"In cooldown: {remaining_hours:.1f} hours remaining")

        return in_cooldown

    def trigger_cooldown(self, exit_time: datetime):
        """
        Trigger cooldown period after position exit.

        Args:
            exit_time: Time when position was closed
        """
        self.last_exit_time = exit_time
        self.in_cooldown = True
        logger.info(f"Cooldown triggered at {exit_time}. Duration: {self.cooldown_hours} hours")

    def calculate_position_size(
        self, capital: float, price: float
    ) -> float:
        """
        Calculate position size with leverage.

        Args:
            capital: Available capital
            price: Current price

        Returns:
            Quantity to buy (with leverage applied)
        """
        # Use max position size (leave cash buffer)
        position_capital = capital * self.max_position_size

        # Apply leverage
        leveraged_capital = position_capital * self.leverage

        # Calculate quantity
        quantity = leveraged_capital / price

        logger.debug(
            f"Position size: capital=${capital:.2f}, "
            f"leveraged=${leveraged_capital:.2f}, "
            f"quantity={quantity:.6f}"
        )

        return quantity

    def calculate_pnl(
        self,
        entry_price: float,
        exit_price: float,
        quantity: float,
        commission_rate: float = 0.001,
    ) -> float:
        """
        Calculate profit/loss including commissions.

        Args:
            entry_price: Entry price
            exit_price: Exit price
            quantity: Position quantity
            commission_rate: Commission rate (default 0.1%)

        Returns:
            Net PnL
        """
        # Gross PnL
        gross_pnl = (exit_price - entry_price) * quantity

        # Commissions (charged on both entry and exit)
        entry_commission = entry_price * quantity * commission_rate
        exit_commission = exit_price * quantity * commission_rate
        total_commission = entry_commission + exit_commission

        # Net PnL
        net_pnl = gross_pnl - total_commission

        logger.debug(
            f"PnL: entry=${entry_price:.2f}, exit=${exit_price:.2f}, "
            f"qty={quantity:.6f}, gross=${gross_pnl:.2f}, "
            f"commission=${total_commission:.2f}, net=${net_pnl:.2f}"
        )

        return net_pnl

    def should_stop_loss(
        self, entry_price: float, current_price: float
    ) -> bool:
        """
        Check if stop-loss should trigger.

        Args:
            entry_price: Entry price
            current_price: Current price

        Returns:
            True if stop-loss triggered
        """
        pnl_pct = (current_price - entry_price) / entry_price

        if pnl_pct <= self.stop_loss_pct:
            logger.warning(
                f"Stop-loss triggered: {pnl_pct*100:.2f}% <= {self.stop_loss_pct*100:.2f}%"
            )
            return True

        return False

    def should_take_profit(
        self, entry_price: float, current_price: float
    ) -> bool:
        """
        Check if take-profit should trigger.

        Args:
            entry_price: Entry price
            current_price: Current price

        Returns:
            True if take-profit triggered
        """
        pnl_pct = (current_price - entry_price) / entry_price

        if pnl_pct >= self.take_profit_pct:
            logger.info(
                f"Take-profit triggered: {pnl_pct*100:.2f}% >= {self.take_profit_pct*100:.2f}%"
            )
            return True

        return False

    def check_exit_conditions(
        self,
        entry_price: float,
        current_price: float,
        regime_changed_to_bear: bool,
    ) -> tuple[bool, str]:
        """
        Check all exit conditions.

        Args:
            entry_price: Entry price
            current_price: Current price
            regime_changed_to_bear: True if regime switched to bear/crash

        Returns:
            Tuple of (should_exit, reason)
        """
        # Priority 1: Regime change
        if regime_changed_to_bear:
            return True, "Regime switched to Bear/Crash"

        # Priority 2: Stop-loss
        if self.should_stop_loss(entry_price, current_price):
            pnl_pct = (current_price - entry_price) / entry_price
            return True, f"Stop-loss triggered ({pnl_pct*100:.2f}%)"

        # Priority 3: Take-profit
        if self.should_take_profit(entry_price, current_price):
            pnl_pct = (current_price - entry_price) / entry_price
            return True, f"Take-profit triggered ({pnl_pct*100:.2f}%)"

        return False, "No exit condition met"

    def get_status(self, current_time: datetime) -> dict:
        """
        Get current risk manager status.

        Args:
            current_time: Current timestamp

        Returns:
            Status dictionary
        """
        in_cooldown = self.is_in_cooldown(current_time)

        status = {
            "in_cooldown": in_cooldown,
            "last_exit_time": self.last_exit_time,
            "cooldown_hours": self.cooldown_hours,
            "leverage": self.leverage,
            "stop_loss_pct": self.stop_loss_pct,
            "take_profit_pct": self.take_profit_pct,
            "max_position_size": self.max_position_size,
        }

        if in_cooldown and self.last_exit_time:
            time_remaining = (
                self.last_exit_time + timedelta(hours=self.cooldown_hours) - current_time
            )
            status["cooldown_remaining_hours"] = time_remaining.total_seconds() / 3600

        return status
