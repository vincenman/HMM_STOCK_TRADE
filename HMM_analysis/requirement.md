## Build a professional Regime-Based Trading Application using Python, Streamlit, Plotly, and yfinance.

1. Core Engine (HMM Logic):
Use hmmlearn.GaussianHMM configured with 7 status components to identify market regimes.
Train the model based on 3 features:
– Returns
– Range (calculated as High - Low / Close)
– Volume Volatility
Key requirement:
Automatically identify the "Bull Run" state — the regime with the highest positive returns.
Automatically identify the "Bear/Crash" state — the regime with the lowest returns.

2. Strategy Logic:
Implement a voting system with 8 confirmation conditions.
An entry trade is only allowed when the HMM identifies the current regime as bullish AND at least 7 out of the following 8 conditions are met:

– RSI < 90
– Momentum > 1%
– Volatility < 6%
– Volume > 20-period SMA
– ADX > 25
– Price > 50 EMA
– Price > 200 EMA
– MACD > Signal Line

1. Risk Management Rules:
– Cooldown Period:
Whenever any position is closed, the system forcibly enters a 48-hour cooldown period.
During these 48 hours, the bot cannot re-enter the market to avoid whipsaws in volatile range-bound conditions.
– Exit Rule:
If the market regime switches to "Bear" or "Crash", close the position immediately.
– Leverage:
Simulate 2.5x leverage in PnL calculations.

2. System Architecture:
– data_loader.py:
Use yfinance to fetch the last 730 days of hourly data for BTC-USD.
– backtester.py:
Run the backtest simulation with an initial capital of $10,000 and log every trade execution.
– app.py:
A Streamlit interactive visualization dashboard.

Dashboard Header:
Display the current signal (Long / Cash) along with the identified market regime.

Chart Section:
Use Plotly to render interactive candlestick charts with background colors dynamically changing based on the identified market regime:
– Green background for Bull Run regime
– Red background for Bear/Crash regime

Metrics Section:
Display the following performance metrics:
– Total Return
– Alpha vs Buy & Hold
– Win Rate
– Max Drawdown"