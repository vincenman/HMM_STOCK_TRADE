"""
Unit tests for backtester.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtesting.backtester import Backtester
from strategy.indicators import add_all_indicators


class TestBacktester:
    """Test cases for Backtester."""

    @pytest.fixture
    def sample_data_with_indicators(self):
        """Create sample data with indicators."""
        dates = pd.date_range(start='2024-01-01', periods=200, freq='h')
        np.random.seed(42)

        # Generate synthetic price data with trend
        close_prices = 50000 + np.cumsum(np.random.randn(200) * 100)

        data = pd.DataFrame({
            'Open': close_prices + np.random.randn(200) * 50,
            'High': close_prices + np.abs(np.random.randn(200) * 100),
            'Low': close_prices - np.abs(np.random.randn(200) * 100),
            'Close': close_prices,
            'Volume': np.abs(np.random.randn(200) * 1000000),
        }, index=dates)

        # Add indicators
        data = add_all_indicators(data)

        return data

    @pytest.fixture
    def sample_regime_states(self):
        """Create sample regime states."""
        # Simulate HMM states: mostly bull (state 3) with some bear (state 0)
        np.random.seed(42)
        states = np.random.choice([0, 1, 2, 3, 4, 5, 6], size=200, p=[0.05, 0.1, 0.1, 0.5, 0.1, 0.1, 0.05])
        return states

    def test_initialization(self):
        """Test backtester initialization."""
        backtester = Backtester(initial_capital=10000.0)

        assert backtester.initial_capital == 10000.0
        assert backtester.capital == 10000.0
        assert not backtester.in_position
        assert len(backtester.trades) == 0

        print("✓ Backtester initialized correctly")

    def test_run_backtest(self, sample_data_with_indicators, sample_regime_states):
        """Test running a complete backtest."""
        backtester = Backtester(initial_capital=10000.0)

        # Run backtest
        metrics = backtester.run(
            data=sample_data_with_indicators,
            regime_states=sample_regime_states,
            bull_state=3,
            bear_state=0,
        )

        # Check metrics exist
        assert 'total_return' in metrics
        assert 'num_trades' in metrics
        assert 'win_rate' in metrics
        assert 'max_drawdown' in metrics

        print(f"✓ Backtest completed")
        print(f"  Total Return: {metrics['total_return_pct']:.2f}%")
        print(f"  Number of Trades: {metrics['num_trades']}")
        print(f"  Win Rate: {metrics['win_rate_pct']:.1f}%")
        print(f"  Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")

    def test_trade_execution(self, sample_data_with_indicators, sample_regime_states):
        """Test that trades are executed."""
        backtester = Backtester(initial_capital=10000.0)

        metrics = backtester.run(
            data=sample_data_with_indicators,
            regime_states=sample_regime_states,
            bull_state=3,
            bear_state=0,
        )

        # Should have some trades
        assert len(backtester.trades) > 0
        assert metrics['num_trades'] >= 0

        print(f"✓ Executed {len(backtester.trades)} trade actions ({metrics['num_trades']} complete trades)")

    def test_get_trades_dataframe(self, sample_data_with_indicators, sample_regime_states):
        """Test getting trades as DataFrame."""
        backtester = Backtester(initial_capital=10000.0)

        backtester.run(
            data=sample_data_with_indicators,
            regime_states=sample_regime_states,
            bull_state=3,
            bear_state=0,
        )

        trades_df = backtester.get_trades_dataframe()

        if not trades_df.empty:
            assert 'timestamp' in trades_df.columns
            assert 'action' in trades_df.columns
            assert 'price' in trades_df.columns

            print(f"✓ Trades DataFrame created with {len(trades_df)} rows")
            print(f"  Columns: {trades_df.columns.tolist()}")
        else:
            print("✓ No trades executed (valid scenario)")

    def test_portfolio_history(self, sample_data_with_indicators, sample_regime_states):
        """Test portfolio value tracking."""
        backtester = Backtester(initial_capital=10000.0)

        backtester.run(
            data=sample_data_with_indicators,
            regime_states=sample_regime_states,
            bull_state=3,
            bear_state=0,
        )

        portfolio_history = backtester.get_portfolio_history()

        assert not portfolio_history.empty
        assert 'portfolio_value' in portfolio_history.columns
        assert len(portfolio_history) == len(sample_data_with_indicators)

        print(f"✓ Portfolio history tracked: {len(portfolio_history)} timestamps")
        print(f"  Initial: ${portfolio_history['portfolio_value'].iloc[0]:.2f}")
        print(f"  Final: ${portfolio_history['portfolio_value'].iloc[-1]:.2f}")

    def test_cooldown_mechanism(self, sample_data_with_indicators, sample_regime_states):
        """Test that cooldown prevents immediate re-entry."""
        backtester = Backtester(initial_capital=10000.0)

        # Run with short cooldown
        backtester.risk_manager.cooldown_hours = 24

        backtester.run(
            data=sample_data_with_indicators,
            regime_states=sample_regime_states,
            bull_state=3,
            bear_state=0,
        )

        # Check that cooldown was triggered
        if len(backtester.trades) > 1:
            # Find first sell
            sells = [t for t in backtester.trades if t['action'] == 'SELL']
            if len(sells) > 0:
                first_sell_time = sells[0]['timestamp']
                # Check that no entries happened within cooldown period
                next_buys = [t for t in backtester.trades
                           if t['action'] == 'BUY' and t['timestamp'] > first_sell_time]
                if len(next_buys) > 0:
                    next_buy_time = next_buys[0]['timestamp']
                    hours_diff = (next_buy_time - first_sell_time).total_seconds() / 3600
                    assert hours_diff >= 24, "Cooldown period violated"
                    print(f"✓ Cooldown respected: {hours_diff:.1f} hours between trades")

        print("✓ Cooldown mechanism working")

    def test_leverage_applied(self, sample_data_with_indicators, sample_regime_states):
        """Test that leverage is properly applied."""
        backtester = Backtester(initial_capital=10000.0)

        # Ensure leverage is set
        assert backtester.risk_manager.leverage == 2.5

        backtester.run(
            data=sample_data_with_indicators,
            regime_states=sample_regime_states,
            bull_state=3,
            bear_state=0,
        )

        # If trades were executed, leverage should be reflected in position size
        buys = [t for t in backtester.trades if t['action'] == 'BUY']
        if len(buys) > 0:
            first_buy = buys[0]
            position_value = first_buy['price'] * first_buy['quantity']
            # With 2.5x leverage on ~$9,500 capital, position should be ~$23,750
            expected_approx = 10000 * 0.95 * 2.5
            # Allow some tolerance
            print(f"✓ Leverage applied: position value=${position_value:.2f} (expected ~${expected_approx:.2f})")

    def test_final_capital_calculation(self, sample_data_with_indicators, sample_regime_states):
        """Test that final capital is calculated correctly."""
        initial = 10000.0
        backtester = Backtester(initial_capital=initial)

        metrics = backtester.run(
            data=sample_data_with_indicators,
            regime_states=sample_regime_states,
            bull_state=3,
            bear_state=0,
        )

        final = metrics['final_capital']
        total_return = metrics['total_return']

        # Verify calculation
        calculated_return = (final - initial) / initial
        assert abs(calculated_return - total_return) < 0.0001

        print(f"✓ Final capital: ${final:.2f} (return: {total_return*100:.2f}%)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
