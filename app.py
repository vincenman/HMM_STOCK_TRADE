"""
Main Streamlit application for HMM Trading Dashboard.
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Setup page config
st.set_page_config(
    page_title="HMM Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data import DataLoader
from models import HMM_AVAILABLE
if HMM_AVAILABLE:
    from models import HMMEngine, ModelManager
from strategy import SignalGenerator, add_all_indicators
from backtesting import Backtester, PerformanceMetrics
from ui.components.charts import create_candlestick_chart, create_portfolio_chart
from ui.components.metrics import display_metrics_grid
from ui.components.config_panel import render_config_panel
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'model_trained' not in st.session_state:
    st.session_state.model_trained = False
if 'backtest_run' not in st.session_state:
    st.session_state.backtest_run = False

# Title and header
st.title("📈 HMM Regime-Based Trading Dashboard")
st.markdown("**Real-time cryptocurrency trading signals using Hidden Markov Models**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    # Data settings
    st.subheader("📊 Data Settings")
    lookback_days = st.slider("Lookback Days", 30, 365, 60, 30)
    force_refresh = st.checkbox("Force Refresh (bypass cache)", value=False)

    if st.button("🔄 Refresh Data", use_container_width=True):
        with st.spinner("Fetching latest data..."):
            try:
                loader = DataLoader()
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=lookback_days)
                data = loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=force_refresh)
                st.session_state.data = data
                st.session_state.data_loaded = True
                st.success(f"✅ Loaded {len(data)} rows from {data.index.min().date()} to {data.index.max().date()}")
            except Exception as e:
                st.error(f"Error loading data: {e}")

    st.markdown("---")

    # Model settings
    st.subheader("🤖 Model Settings")
    n_states = st.number_input("HMM States", 3, 10, 7, 1)

    # Display HMM availability status
    if not HMM_AVAILABLE:
        st.warning("⚠️ hmmlearn not installed. Model training disabled.")
        st.info("Dashboard works without it! You can still view data and configure settings.")

    if HMM_AVAILABLE:
        if st.button("🎯 Train Model", use_container_width=True, disabled=not st.session_state.data_loaded):
            with st.spinner("Training HMM model..."):
                try:
                    engine = HMMEngine(n_states=n_states)
                    success, error = engine.train(st.session_state.data)
                    if success:
                        st.session_state.engine = engine
                        st.session_state.model_trained = True
                        st.success("✅ Model trained!")
                    else:
                        st.error(f"Training failed: {error}")
                except Exception as e:
                    st.error(f"Error training model: {e}")

    st.markdown("---")

    # Strategy settings
    st.subheader("💼 Strategy")
    initial_capital = st.number_input("Initial Capital ($)", 1000, 100000, 10000, 1000)

    if st.button("▶️ Run Backtest", use_container_width=True,
                 disabled=not (st.session_state.data_loaded and st.session_state.model_trained)):
        with st.spinner("Running backtest..."):
            try:
                # Add indicators
                data_with_indicators = add_all_indicators(st.session_state.data.copy())

                # Get regime states
                regime_states = st.session_state.engine.predict(st.session_state.data)

                # Run backtest
                backtester = Backtester(initial_capital=initial_capital)
                metrics = backtester.run(
                    data_with_indicators,
                    regime_states,
                    st.session_state.engine.bull_state,
                    st.session_state.engine.bear_state
                )

                st.session_state.backtest_metrics = metrics
                st.session_state.backtest_data = data_with_indicators
                st.session_state.regime_states = regime_states
                st.session_state.backtester = backtester
                st.session_state.backtest_run = True

                st.success("✅ Backtest complete!")
            except Exception as e:
                st.error(f"Error running backtest: {e}")

# Main content area
if not st.session_state.data_loaded:
    st.info("👈 Start by loading data from the sidebar")

    # Show data info
    st.subheader("📊 Getting Started")
    st.markdown("""
    **Steps to use this dashboard:**
    1. Click **"🔄 Refresh Data"** in the sidebar to load BTC-USD data
    2. Click **"🎯 Train Model"** to train the HMM model (requires hmmlearn)
    3. Click **"▶️ Run Backtest"** to simulate the trading strategy
    4. View results and metrics below

    **Features:**
    - Real-time regime detection (Bull/Bear/Neutral)
    - 8-condition voting system for trade entries
    - Risk management with 48-hour cooldown
    - Interactive charts and performance metrics
    """)

else:
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Backtest Results", "⚙️ Configuration", "ℹ️ About"])

    with tab1:
        st.header("Market Overview")

        # Current signal section
        col1, col2, col3, col4 = st.columns(4)

        if st.session_state.model_trained:
            # Get current regime
            state, regime_name, confidence = st.session_state.engine.predict_current_regime(st.session_state.data)

            # Get signal
            data_with_indicators = add_all_indicators(st.session_state.data.copy())
            signal_gen = SignalGenerator()
            signal, conditions_met, details = signal_gen.get_current_signal(
                data_with_indicators, state, st.session_state.engine.bull_state
            )

            with col1:
                signal_color = "green" if signal == "LONG" else "gray"
                st.metric("Current Signal", signal, delta=None)

            with col2:
                regime_color = "green" if "Bull" in regime_name else ("red" if "Bear" in regime_name else "gray")
                st.metric("Market Regime", regime_name, f"{confidence*100:.1f}% confidence")

            with col3:
                st.metric("Conditions Met", f"{conditions_met}/8", delta=None)

            with col4:
                latest_price = st.session_state.data['Close'].iloc[-1]
                st.metric("BTC Price", f"${latest_price:,.2f}", delta=None)

        else:
            with col1:
                st.metric("Current Signal", "N/A", delta=None)
            with col2:
                st.metric("Market Regime", "N/A", delta=None)
            with col3:
                st.metric("Conditions Met", "N/A", delta=None)
            with col4:
                latest_price = st.session_state.data['Close'].iloc[-1]
                st.metric("BTC Price", f"${latest_price:,.2f}", delta=None)

        st.markdown("---")

        # Price chart
        st.subheader("📉 Price Chart")

        if st.session_state.backtest_run:
            # Chart with regime highlighting
            fig = create_candlestick_chart(
                st.session_state.backtest_data,
                st.session_state.regime_states,
                st.session_state.engine.bull_state,
                st.session_state.engine.bear_state,
                st.session_state.backtester.trades
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Simple price chart
            st.line_chart(st.session_state.data['Close'])

    with tab2:
        st.header("Backtest Results")

        if st.session_state.backtest_run:
            # Performance metrics
            display_metrics_grid(st.session_state.backtest_metrics)

            st.markdown("---")

            # Portfolio chart
            st.subheader("📊 Portfolio Value Over Time")
            portfolio_history = st.session_state.backtester.get_portfolio_history()
            fig = create_portfolio_chart(portfolio_history, st.session_state.backtest_metrics)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Trade history
            st.subheader("📝 Trade History")
            trades_df = st.session_state.backtester.get_trades_dataframe()
            if not trades_df.empty:
                st.dataframe(trades_df, use_container_width=True)

                # Download button
                csv = trades_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Trade History",
                    data=csv,
                    file_name="trade_history.csv",
                    mime="text/csv"
                )
            else:
                st.info("No trades executed in this backtest")
        else:
            st.info("👈 Run a backtest from the sidebar to see results")

    with tab3:
        st.header("Strategy Configuration")
        render_config_panel()

    with tab4:
        st.header("About This Dashboard")
        st.markdown("""
        ### 🎯 HMM Regime-Based Trading System

        This dashboard implements a sophisticated trading strategy using:

        **1. Hidden Markov Models (HMM)**
        - 7-state model to identify market regimes
        - Automatic Bull/Bear regime classification
        - Trained on returns, range, and volume volatility

        **2. 8-Condition Voting System**
        Entry requires Bull regime AND ≥7 conditions:
        - RSI < 90
        - Momentum > 1%
        - Volatility < 6%
        - Volume > 20-SMA
        - ADX > 25
        - Price > 50 EMA
        - Price > 200 EMA
        - MACD > Signal Line

        **3. Risk Management**
        - 48-hour cooldown after position close
        - 2.5x leverage simulation
        - Stop-loss: -5%
        - Take-profit: +15%

        **4. Performance Metrics**
        - Total return & Alpha vs Buy & Hold
        - Win rate & Profit factor
        - Max drawdown & Sharpe ratio

        ---

        **Technology Stack:**
        - Python 3.10+
        - Streamlit (UI)
        - Plotly (Charts)
        - yfinance (Data)
        - hmmlearn (Machine Learning)
        - SQLite (Database)

        **Version:** Phase 3 - UI Development
        """)

# Footer
st.markdown("---")
st.markdown("**⚠️ Disclaimer:** This is for educational purposes only. Not financial advice. Cryptocurrency trading carries substantial risk.")
