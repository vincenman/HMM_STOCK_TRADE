"""
Configuration panel component for strategy parameters.
"""
import streamlit as st
import json
from config.settings import STRATEGY_DEFAULTS


def render_config_panel():
    """
    Render the strategy configuration panel.
    """
    st.markdown("""
    Adjust strategy parameters below. Changes will apply to the next backtest run.
    """)

    st.markdown("---")

    # Entry conditions
    st.subheader("📊 Entry Conditions")

    col1, col2 = st.columns(2)

    with col1:
        rsi_threshold = st.slider(
            "RSI Threshold",
            50, 100,
            STRATEGY_DEFAULTS['rsi_threshold'],
            5,
            help="Entry allowed when RSI < threshold"
        )

        momentum_threshold = st.slider(
            "Momentum Threshold (%)",
            0.0, 5.0,
            STRATEGY_DEFAULTS['momentum_threshold'] * 100,
            0.1,
            help="Entry allowed when momentum > threshold"
        ) / 100

        volatility_threshold = st.slider(
            "Volatility Threshold (%)",
            1.0, 10.0,
            STRATEGY_DEFAULTS['volatility_threshold'] * 100,
            0.5,
            help="Entry allowed when volatility < threshold"
        ) / 100

        adx_threshold = st.slider(
            "ADX Threshold",
            10, 50,
            STRATEGY_DEFAULTS['adx_threshold'],
            5,
            help="Entry allowed when ADX > threshold"
        )

    with col2:
        ema_short = st.number_input(
            "Short EMA Period",
            10, 100,
            STRATEGY_DEFAULTS['ema_short'],
            10,
            help="Shorter EMA for trend detection"
        )

        ema_long = st.number_input(
            "Long EMA Period",
            100, 300,
            STRATEGY_DEFAULTS['ema_long'],
            10,
            help="Longer EMA for trend detection"
        )

        required_conditions = st.slider(
            "Required Conditions",
            5, 8,
            STRATEGY_DEFAULTS['required_conditions'],
            1,
            help="Minimum conditions needed for entry (out of 8)"
        )

    st.markdown("---")

    # Risk management
    st.subheader("⚠️ Risk Management")

    col1, col2 = st.columns(2)

    with col1:
        cooldown_hours = st.number_input(
            "Cooldown Period (hours)",
            0, 168,
            STRATEGY_DEFAULTS['cooldown_hours'],
            12,
            help="Hours to wait after closing a position"
        )

        leverage = st.slider(
            "Leverage",
            1.0, 5.0,
            STRATEGY_DEFAULTS['leverage'],
            0.5,
            help="Position leverage multiplier"
        )

        stop_loss_pct = st.slider(
            "Stop Loss (%)",
            -10.0, 0.0,
            STRATEGY_DEFAULTS['stop_loss_pct'] * 100,
            0.5,
            help="Exit when loss reaches this percentage"
        ) / 100

    with col2:
        take_profit_pct = st.slider(
            "Take Profit (%)",
            0.0, 30.0,
            STRATEGY_DEFAULTS['take_profit_pct'] * 100,
            1.0,
            help="Exit when profit reaches this percentage"
        ) / 100

        initial_capital = st.number_input(
            "Initial Capital ($)",
            1000, 100000,
            int(STRATEGY_DEFAULTS['initial_capital']),
            1000,
            help="Starting capital for backtest"
        )

        commission_rate = st.slider(
            "Commission Rate (%)",
            0.0, 1.0,
            STRATEGY_DEFAULTS['commission_rate'] * 100,
            0.01,
            help="Trading commission percentage"
        ) / 100

    st.markdown("---")

    # Save/Load configuration
    st.subheader("💾 Configuration Management")

    col1, col2, col3 = st.columns(3)

    # Build current config
    current_config = {
        'rsi_threshold': rsi_threshold,
        'momentum_threshold': momentum_threshold,
        'volatility_threshold': volatility_threshold,
        'adx_threshold': adx_threshold,
        'ema_short': ema_short,
        'ema_long': ema_long,
        'required_conditions': required_conditions,
        'cooldown_hours': cooldown_hours,
        'leverage': leverage,
        'stop_loss_pct': stop_loss_pct,
        'take_profit_pct': take_profit_pct,
        'initial_capital': initial_capital,
        'commission_rate': commission_rate,
    }

    with col1:
        if st.button("💾 Save Configuration", use_container_width=True):
            st.session_state.custom_config = current_config
            st.success("Configuration saved!")

    with col2:
        if st.button("🔄 Load Saved Config", use_container_width=True):
            if 'custom_config' in st.session_state:
                st.info("Configuration loaded! Refresh to apply.")
            else:
                st.warning("No saved configuration found")

    with col3:
        if st.button("↩️ Reset to Defaults", use_container_width=True):
            st.session_state.custom_config = STRATEGY_DEFAULTS.copy()
            st.info("Reset to defaults! Refresh to apply.")

    # Download/Upload configuration
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # Download current config as JSON
        config_json = json.dumps(current_config, indent=2)
        st.download_button(
            label="📥 Download Config (JSON)",
            data=config_json,
            file_name="strategy_config.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        # Upload config file
        uploaded_file = st.file_uploader(
            "📤 Upload Config (JSON)",
            type=['json'],
            help="Upload a previously saved configuration file"
        )

        if uploaded_file is not None:
            try:
                loaded_config = json.load(uploaded_file)
                st.session_state.custom_config = loaded_config
                st.success("Configuration uploaded! Refresh to apply.")
            except Exception as e:
                st.error(f"Error loading config: {e}")

    # Store config in session state for use in backtesting
    st.session_state.current_config = current_config

    # Display current configuration summary
    st.markdown("---")
    st.subheader("📋 Current Configuration")

    with st.expander("View Configuration Details"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Entry Conditions:**")
            st.write(f"- RSI < {rsi_threshold}")
            st.write(f"- Momentum > {momentum_threshold*100:.1f}%")
            st.write(f"- Volatility < {volatility_threshold*100:.1f}%")
            st.write(f"- ADX > {adx_threshold}")
            st.write(f"- EMA Short: {ema_short}")
            st.write(f"- EMA Long: {ema_long}")
            st.write(f"- Required: {required_conditions}/8")

        with col2:
            st.write("**Risk Management:**")
            st.write(f"- Cooldown: {cooldown_hours}h")
            st.write(f"- Leverage: {leverage}x")
            st.write(f"- Stop Loss: {stop_loss_pct*100:.1f}%")
            st.write(f"- Take Profit: {take_profit_pct*100:.1f}%")
            st.write(f"- Initial Capital: ${initial_capital:,}")
            st.write(f"- Commission: {commission_rate*100:.2f}%")
