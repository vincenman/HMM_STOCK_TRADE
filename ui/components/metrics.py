"""
Metrics display components for the dashboard.
"""
import streamlit as st
from typing import Dict


def display_metrics_grid(metrics: Dict):
    """
    Display performance metrics in a grid layout.

    Args:
        metrics: Performance metrics dictionary
    """
    st.subheader("📊 Performance Metrics")

    # Returns section
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_return = metrics.get('total_return_pct', 0)
        color = "normal" if total_return >= 0 else "inverse"
        st.metric(
            "Total Return",
            f"{total_return:.2f}%",
            delta=None,
            delta_color=color
        )

    with col2:
        buy_hold = metrics.get('buy_hold_return_pct', 0)
        st.metric(
            "Buy & Hold",
            f"{buy_hold:.2f}%",
            delta=None
        )

    with col3:
        alpha = metrics.get('alpha_pct', 0)
        color = "normal" if alpha >= 0 else "inverse"
        st.metric(
            "Alpha (Excess Return)",
            f"{alpha:.2f}%",
            delta=None,
            delta_color=color
        )

    with col4:
        sharpe = metrics.get('sharpe_ratio', 0)
        st.metric(
            "Sharpe Ratio",
            f"{sharpe:.2f}",
            delta=None
        )

    st.markdown("---")

    # Trade statistics
    st.subheader("📈 Trade Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        num_trades = metrics.get('num_trades', 0)
        st.metric("Number of Trades", num_trades)

    with col2:
        win_rate = metrics.get('win_rate_pct', 0)
        st.metric("Win Rate", f"{win_rate:.1f}%")

    with col3:
        profit_factor = metrics.get('profit_factor', 0)
        pf_display = f"{profit_factor:.2f}" if profit_factor != float('inf') else "∞"
        st.metric("Profit Factor", pf_display)

    with col4:
        avg_return = metrics.get('avg_return_pct', 0)
        st.metric("Avg Return/Trade", f"{avg_return:.2f}%")

    st.markdown("---")

    # Risk metrics
    st.subheader("⚠️ Risk Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        max_dd = metrics.get('max_drawdown_pct', 0)
        st.metric(
            "Max Drawdown",
            f"{max_dd:.2f}%",
            delta=None,
            delta_color="inverse"
        )

    with col2:
        avg_win = metrics.get('avg_win', 0)
        st.metric("Avg Win", f"${avg_win:.2f}")

    with col3:
        avg_loss = metrics.get('avg_loss', 0)
        st.metric("Avg Loss", f"${avg_loss:.2f}")

    with col4:
        # Calculate expected value
        if num_trades > 0:
            win_rate_decimal = win_rate / 100
            expected_value = (win_rate_decimal * avg_win) + ((1 - win_rate_decimal) * avg_loss)
            st.metric("Expected Value", f"${expected_value:.2f}")
        else:
            st.metric("Expected Value", "N/A")

    st.markdown("---")

    # Capital summary
    st.subheader("💰 Capital Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        initial = metrics.get('initial_capital', 0)
        st.metric("Initial Capital", f"${initial:,.2f}")

    with col2:
        final = metrics.get('final_capital', 0)
        st.metric("Final Capital", f"${final:,.2f}")

    with col3:
        profit = final - initial
        color = "normal" if profit >= 0 else "inverse"
        st.metric(
            "Profit/Loss",
            f"${profit:,.2f}",
            delta=None,
            delta_color=color
        )


def display_current_signal_card(
    signal: str,
    regime: str,
    confidence: float,
    conditions_met: int,
    total_conditions: int = 8
):
    """
    Display current trading signal in a card format.

    Args:
        signal: Current signal (LONG/CASH)
        regime: Current regime name
        confidence: Regime confidence (0-1)
        conditions_met: Number of conditions met
        total_conditions: Total number of conditions
    """
    st.subheader("🎯 Current Signal")

    col1, col2 = st.columns(2)

    with col1:
        # Signal card
        if signal == "LONG":
            st.success(f"### 📈 {signal}")
            st.write("**Action:** Enter long position")
        else:
            st.info(f"### 💵 {signal}")
            st.write("**Action:** Stay in cash")

    with col2:
        # Regime card
        if "Bull" in regime:
            st.success(f"### 🐂 {regime}")
        elif "Bear" in regime or "Crash" in regime:
            st.error(f"### 🐻 {regime}")
        else:
            st.warning(f"### ➖ {regime}")

        st.write(f"**Confidence:** {confidence*100:.1f}%")

    # Conditions progress bar
    st.write(f"**Conditions Met:** {conditions_met}/{total_conditions}")
    progress = conditions_met / total_conditions
    st.progress(progress)

    if conditions_met >= 7:
        st.success("✅ Entry conditions satisfied (≥7/8)")
    else:
        st.warning(f"⚠️ Need {7 - conditions_met} more condition(s) for entry")


def display_conditions_table(conditions_details: Dict):
    """
    Display detailed conditions status in a table.

    Args:
        conditions_details: Dictionary with condition details
    """
    st.subheader("📋 Conditions Details")

    # Create table data
    table_data = []
    for name, details in conditions_details.items():
        status = "✅ YES" if details['met'] else "❌ NO"
        condition_text = details['condition']

        if isinstance(details['value'], float):
            if abs(details['value']) > 1000:
                value_str = f"{details['value']:,.2f}"
            else:
                value_str = f"{details['value']:.4f}"
        else:
            value_str = str(details['value'])

        if isinstance(details['threshold'], float):
            if abs(details['threshold']) > 1000:
                threshold_str = f"{details['threshold']:,.2f}"
            else:
                threshold_str = f"{details['threshold']:.4f}"
        else:
            threshold_str = str(details['threshold'])

        table_data.append({
            'Status': status,
            'Condition': condition_text,
            'Current': value_str,
            'Threshold': threshold_str,
        })

    # Display as dataframe
    import pandas as pd
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_trade_summary(trades_df):
    """
    Display summary statistics for trades.

    Args:
        trades_df: DataFrame with trade records
    """
    if trades_df.empty:
        st.info("No trades executed")
        return

    st.subheader("📊 Trade Summary")

    # Filter to completed trades (SELL actions)
    sells = trades_df[trades_df['action'] == 'SELL'].copy()

    if sells.empty:
        st.info("No completed trades")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Trades", len(sells))

    with col2:
        if 'hold_time_hours' in sells.columns:
            avg_hold = sells['hold_time_hours'].mean()
            st.metric("Avg Hold Time", f"{avg_hold:.1f}h")
        else:
            st.metric("Avg Hold Time", "N/A")

    with col3:
        if 'pnl' in sells.columns:
            total_pnl = sells['pnl'].sum()
            st.metric("Total PnL", f"${total_pnl:,.2f}")
        else:
            st.metric("Total PnL", "N/A")

    # Best and worst trades
    if 'pnl' in sells.columns and len(sells) > 0:
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**🏆 Best Trade:**")
            best_trade = sells.loc[sells['pnl'].idxmax()]
            st.write(f"- PnL: ${best_trade['pnl']:.2f}")
            if 'return_pct' in best_trade:
                st.write(f"- Return: {best_trade['return_pct']*100:.2f}%")
            st.write(f"- Date: {best_trade['timestamp']}")

        with col2:
            st.write("**📉 Worst Trade:**")
            worst_trade = sells.loc[sells['pnl'].idxmin()]
            st.write(f"- PnL: ${worst_trade['pnl']:.2f}")
            if 'return_pct' in worst_trade:
                st.write(f"- Return: {worst_trade['return_pct']*100:.2f}%")
            st.write(f"- Date: {worst_trade['timestamp']}")
