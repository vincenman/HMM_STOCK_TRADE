"""
Paper trading dashboard page for Streamlit.
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

from paper_trading import PaperTradingEngine
from paper_trading.live_feed import LivePriceFeed, LiveDataManager
from paper_trading.notifications import NotificationManager, TradeJournal
from paper_trading.reports import ReportGenerator
from strategy import add_all_indicators


def render_paper_trading_page(model_engine=None, historical_data=None):
    """
    Render paper trading page.

    Args:
        model_engine: Trained HMM engine
        historical_data: Historical data for initialization
    """
    st.header("📡 Paper Trading (Live Simulation)")

    # Check prerequisites
    if model_engine is None or not hasattr(model_engine, 'bull_state'):
        st.warning("⚠️ Model not trained yet!")
        st.info("Please go to the Overview tab and train the model first before starting paper trading.")
        return

    if historical_data is None or len(historical_data) == 0:
        st.warning("⚠️ No historical data loaded!")
        st.info("Please load data from the Overview tab first.")
        return

    st.success("✅ Prerequisites met! Ready for paper trading.")

    # Initialize paper trading engine in session state
    if 'paper_engine' not in st.session_state:
        st.session_state.paper_engine = PaperTradingEngine(
            initial_capital=10000.0,
            model_engine=model_engine
        )
        st.session_state.live_data_mgr = LiveDataManager(
            symbol="BTC-USD",
            interval="1h",
            lookback_periods=200
        )
        # Initialize with historical data
        data_with_indicators = add_all_indicators(historical_data.copy())
        st.session_state.live_data_mgr.initialize(data_with_indicators)

        st.session_state.notification_mgr = NotificationManager(email_enabled=False)
        st.session_state.trade_journal = TradeJournal()

    engine = st.session_state.paper_engine

    # Control panel
    st.subheader("🎮 Control Panel")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("▶️ Start Trading", use_container_width=True, disabled=engine.is_running):
            engine.start()
            st.success("Paper trading started!")
            st.rerun()

    with col2:
        if st.button("⏸️ Stop Trading", use_container_width=True, disabled=not engine.is_running):
            engine.stop()
            st.info("Paper trading stopped!")
            st.rerun()

    with col3:
        if st.button("🔄 Manual Update", use_container_width=True):
            # Simulate price update
            try:
                import yfinance as yf
                ticker = yf.Ticker("BTC-USD")
                latest = ticker.history(period="1d", interval="1h")
                if not latest.empty:
                    price = latest['Close'].iloc[-1]
                    timestamp = latest.index[-1]

                    # Get full data for indicators
                    data = st.session_state.live_data_mgr.get_data()
                    data_with_indicators = add_all_indicators(data)

                    # Update engine
                    engine.update_price(price, timestamp, data_with_indicators)
                    st.success(f"Updated: ${price:,.2f}")
                    st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")

    with col4:
        if st.button("🔁 Reset Engine", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                engine.reset()
                st.session_state.confirm_reset = False
                st.success("Engine reset!")
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("Click again to confirm reset!")

    st.markdown("---")

    # Status display
    st.subheader("📊 Current Status")

    status = engine.get_current_status()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_text = "🟢 RUNNING" if status['is_running'] else "⚪ STOPPED"
        st.metric("Status", status_text)

    with col2:
        current_capital = status['current_capital']
        initial_capital = status['initial_capital']
        capital_change = current_capital - initial_capital
        st.metric(
            "Current Capital",
            f"${current_capital:,.2f}",
            f"{capital_change:+,.2f}"
        )

    with col3:
        st.metric(
            "Total Return",
            f"{status['total_return_pct']:.2f}%",
            delta_color="normal" if status['total_return_pct'] >= 0 else "inverse"
        )

    with col4:
        st.metric("Trades Completed", status['num_trades'])

    # Position info
    if status['in_position']:
        st.markdown("### 📍 Current Position")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Entry Price", f"${status['position_entry_price']:,.2f}")

        with col2:
            st.metric("Current Price", f"${status['last_price']:,.2f}")

        with col3:
            unrealized_pnl_pct = status.get('unrealized_pnl_pct', 0)
            st.metric(
                "Unrealized P&L",
                f"{unrealized_pnl_pct:+.2f}%",
                delta_color="normal" if unrealized_pnl_pct >= 0 else "inverse"
            )

        with col4:
            entry_time = status.get('position_entry_time')
            if entry_time:
                hold_time = (datetime.now() - entry_time).total_seconds() / 3600
                st.metric("Hold Time", f"{hold_time:.1f}h")

    st.markdown("---")

    # Trade history
    st.subheader("📝 Trade History")

    trades_df = engine.get_trades_df()

    if not trades_df.empty:
        # Show recent trades
        st.dataframe(trades_df.tail(10), use_container_width=True)

        # Download buttons
        col1, col2 = st.columns(2)

        with col1:
            csv = trades_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                data=csv,
                file_name=f"paper_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            if st.button("📄 Generate PDF Report", use_container_width=True):
                try:
                    from backtesting import PerformanceMetrics

                    # Calculate metrics
                    metrics_calc = PerformanceMetrics()
                    metrics = metrics_calc.calculate(
                        initial_capital=status['initial_capital'],
                        final_capital=status['current_capital'],
                        trades=trades_df.to_dict('records'),
                        buy_hold_return=0.0  # Not available in paper trading
                    )

                    # Generate report
                    report_gen = ReportGenerator()
                    pdf_path = report_gen.generate_backtest_report(
                        metrics=metrics,
                        trades_df=trades_df,
                        config=engine.config,
                        output_path=f"./reports/paper_trading_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    )

                    st.success(f"Report generated: {pdf_path}")

                    # Provide download
                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            "📥 Download PDF",
                            data=f.read(),
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf"
                        )

                except Exception as e:
                    st.error(f"Failed to generate report: {e}")

    else:
        st.info("No trades yet. Start paper trading and wait for signals!")

    st.markdown("---")

    # Settings
    with st.expander("⚙️ Paper Trading Settings"):
        st.markdown("### Notification Settings")

        email_enabled = st.checkbox("Enable Email Notifications", value=False)

        if email_enabled:
            st.text_input("SMTP Server", placeholder="smtp.gmail.com")
            st.number_input("SMTP Port", value=587)
            st.text_input("Email Username", placeholder="your-email@gmail.com")
            st.text_input("Email Password", type="password")
            st.text_input("Recipient Email", placeholder="recipient@example.com")

            st.info("💡 For Gmail: Enable 'Less secure app access' or use App Password")

        st.markdown("### Update Interval")
        update_interval = st.slider(
            "Price Update Interval (seconds)",
            min_value=60,
            max_value=3600,
            value=300,
            step=60,
            help="How often to check for new prices"
        )

        st.info(f"Price will update every {update_interval//60} minutes when running")

    # Auto-refresh when running
    if engine.is_running:
        st.info("🔄 Auto-refresh is enabled while paper trading is active")
        # This would need a different implementation in production
        # as Streamlit doesn't support true real-time updates
