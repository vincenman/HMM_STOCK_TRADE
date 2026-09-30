"""
Performance metrics calculation.
"""
import pandas as pd
import numpy as np
from typing import Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PerformanceMetrics:
    """Calculate and analyze trading performance metrics."""

    @staticmethod
    def calculate_returns_metrics(
        portfolio_values: pd.Series,
        initial_capital: float,
    ) -> Dict:
        """
        Calculate return-based metrics.

        Args:
            portfolio_values: Time series of portfolio values
            initial_capital: Starting capital

        Returns:
            Dictionary of return metrics
        """
        final_value = portfolio_values.iloc[-1]
        total_return = (final_value - initial_capital) / initial_capital

        # Periodic returns
        returns = portfolio_values.pct_change().dropna()

        return {
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'mean_return': returns.mean(),
            'std_return': returns.std(),
            'final_value': final_value,
        }

    @staticmethod
    def calculate_drawdown(portfolio_values: pd.Series) -> Dict:
        """
        Calculate drawdown metrics.

        Args:
            portfolio_values: Time series of portfolio values

        Returns:
            Dictionary of drawdown metrics
        """
        cumulative_max = portfolio_values.cummax()
        drawdown = (portfolio_values - cumulative_max) / cumulative_max

        max_drawdown = drawdown.min()
        max_drawdown_idx = drawdown.idxmin()

        # Calculate recovery time
        recovery_time = None
        if max_drawdown_idx in drawdown.index:
            after_max_dd = drawdown.loc[max_drawdown_idx:]
            recovery_idx = after_max_dd[after_max_dd >= 0].index
            if len(recovery_idx) > 0:
                recovery_time = (recovery_idx[0] - max_drawdown_idx).total_seconds() / 3600  # hours

        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'max_drawdown_date': max_drawdown_idx,
            'recovery_time_hours': recovery_time,
        }

    @staticmethod
    def calculate_sharpe_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 8760,  # hourly data
    ) -> float:
        """
        Calculate Sharpe ratio.

        Args:
            returns: Return series
            risk_free_rate: Risk-free rate (default 0)
            periods_per_year: Number of periods per year (8760 for hourly)

        Returns:
            Annualized Sharpe ratio
        """
        if len(returns) < 2 or returns.std() == 0:
            return 0.0

        excess_returns = returns - risk_free_rate / periods_per_year
        sharpe = excess_returns.mean() / returns.std() * np.sqrt(periods_per_year)

        return sharpe

    @staticmethod
    def calculate_sortino_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 8760,
    ) -> float:
        """
        Calculate Sortino ratio (downside deviation).

        Args:
            returns: Return series
            risk_free_rate: Risk-free rate (default 0)
            periods_per_year: Number of periods per year

        Returns:
            Annualized Sortino ratio
        """
        if len(returns) < 2:
            return 0.0

        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return float('inf')

        sortino = excess_returns.mean() / downside_returns.std() * np.sqrt(periods_per_year)

        return sortino

    @staticmethod
    def calculate_calmar_ratio(
        total_return: float,
        max_drawdown: float,
        years: float = 1.0,
    ) -> float:
        """
        Calculate Calmar ratio (return / max drawdown).

        Args:
            total_return: Total return
            max_drawdown: Maximum drawdown
            years: Time period in years

        Returns:
            Calmar ratio
        """
        if max_drawdown == 0:
            return float('inf')

        annualized_return = (1 + total_return) ** (1 / years) - 1
        calmar = annualized_return / abs(max_drawdown)

        return calmar

    @staticmethod
    def calculate_trade_metrics(trades_df: pd.DataFrame) -> Dict:
        """
        Calculate trade-specific metrics.

        Args:
            trades_df: DataFrame with trade records

        Returns:
            Dictionary of trade metrics
        """
        if trades_df.empty or 'action' not in trades_df.columns:
            return {
                'num_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
            }

        sells = trades_df[trades_df['action'] == 'SELL'].copy()

        if sells.empty or 'pnl' not in sells.columns:
            return {
                'num_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
            }

        num_trades = len(sells)
        wins = sells[sells['pnl'] > 0]
        losses = sells[sells['pnl'] <= 0]

        win_rate = len(wins) / num_trades if num_trades > 0 else 0
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0

        total_profit = wins['pnl'].sum() if len(wins) > 0 else 0
        total_loss = abs(losses['pnl'].sum()) if len(losses) > 0 else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')

        return {
            'num_trades': num_trades,
            'num_wins': len(wins),
            'num_losses': len(losses),
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'profit_factor': profit_factor,
        }

    @staticmethod
    def calculate_all_metrics(
        portfolio_values: pd.Series,
        initial_capital: float,
        trades_df: pd.DataFrame,
        benchmark_return: float = None,
    ) -> Dict:
        """
        Calculate all performance metrics.

        Args:
            portfolio_values: Time series of portfolio values
            initial_capital: Starting capital
            trades_df: DataFrame with trade records
            benchmark_return: Optional benchmark return for alpha

        Returns:
            Complete metrics dictionary
        """
        metrics = {}

        # Returns
        returns_metrics = PerformanceMetrics.calculate_returns_metrics(
            portfolio_values, initial_capital
        )
        metrics.update(returns_metrics)

        # Drawdown
        drawdown_metrics = PerformanceMetrics.calculate_drawdown(portfolio_values)
        metrics.update(drawdown_metrics)

        # Risk-adjusted returns
        returns = portfolio_values.pct_change().dropna()
        metrics['sharpe_ratio'] = PerformanceMetrics.calculate_sharpe_ratio(returns)
        metrics['sortino_ratio'] = PerformanceMetrics.calculate_sortino_ratio(returns)

        # Calmar ratio
        years = len(portfolio_values) / 8760  # assuming hourly data
        metrics['calmar_ratio'] = PerformanceMetrics.calculate_calmar_ratio(
            metrics['total_return'],
            metrics['max_drawdown'],
            years,
        )

        # Trade metrics
        trade_metrics = PerformanceMetrics.calculate_trade_metrics(trades_df)
        metrics.update(trade_metrics)

        # Alpha (if benchmark provided)
        if benchmark_return is not None:
            metrics['benchmark_return'] = benchmark_return
            metrics['benchmark_return_pct'] = benchmark_return * 100
            metrics['alpha'] = metrics['total_return'] - benchmark_return
            metrics['alpha_pct'] = metrics['alpha'] * 100

        return metrics

    @staticmethod
    def format_metrics_report(metrics: Dict) -> str:
        """
        Format metrics as a readable report.

        Args:
            metrics: Metrics dictionary

        Returns:
            Formatted report string
        """
        report = [
            "=" * 60,
            "PERFORMANCE REPORT",
            "=" * 60,
            "",
            "RETURNS:",
            f"  Total Return:        {metrics.get('total_return_pct', 0):.2f}%",
            f"  Buy & Hold:          {metrics.get('benchmark_return_pct', 0):.2f}%",
            f"  Alpha:               {metrics.get('alpha_pct', 0):.2f}%",
            "",
            "RISK METRICS:",
            f"  Max Drawdown:        {metrics.get('max_drawdown_pct', 0):.2f}%",
            f"  Sharpe Ratio:        {metrics.get('sharpe_ratio', 0):.2f}",
            f"  Sortino Ratio:       {metrics.get('sortino_ratio', 0):.2f}",
            f"  Calmar Ratio:        {metrics.get('calmar_ratio', 0):.2f}",
            "",
            "TRADE STATISTICS:",
            f"  Number of Trades:    {metrics.get('num_trades', 0)}",
            f"  Win Rate:            {metrics.get('win_rate_pct', 0):.1f}%",
            f"  Profit Factor:       {metrics.get('profit_factor', 0):.2f}",
            f"  Avg Win:             ${metrics.get('avg_win', 0):.2f}",
            f"  Avg Loss:            ${metrics.get('avg_loss', 0):.2f}",
            "",
            "CAPITAL:",
            f"  Initial:             ${metrics.get('initial_capital', 0):,.2f}",
            f"  Final:               ${metrics.get('final_value', 0):,.2f}",
            f"  Profit/Loss:         ${metrics.get('final_value', 0) - metrics.get('initial_capital', 0):,.2f}",
            "=" * 60,
        ]

        return "\n".join(report)
