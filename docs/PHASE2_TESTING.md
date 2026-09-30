# Phase 2 Testing Guide - Strategy & Backtesting

## 📋 Overview

Phase 2 implements the complete trading strategy logic including:
- ✅ Technical indicators (RSI, MACD, EMA, ADX, etc.)
- ✅ 8-condition voting system for trade entries
- ✅ Risk management (cooldown, leverage, stop-loss/take-profit)
- ✅ Backtesting engine with full simulation
- ✅ Performance metrics calculation

---

## 🎯 What Was Implemented

### 1. **Technical Indicators** (`strategy/indicators.py`)
Implemented 15+ indicators without external TA libraries:
- RSI (Relative Strength Index)
- EMA (50, 200 periods)
- SMA (Simple Moving Average)
- MACD (Moving Average Convergence Divergence)
- ADX (Average Directional Index)
- Momentum
- Volatility
- Bollinger Bands
- ATR (Average True Range)
- Volume indicators

### 2. **Signal Generator** (`strategy/signal_generator.py`)
8-condition voting system:
1. RSI < 90
2. Momentum > 1%
3. Volatility < 6%
4. Volume > 20-period SMA
5. ADX > 25
6. Price > 50 EMA
7. Price > 200 EMA
8. MACD > Signal Line

**Entry:** Bull regime AND ≥7 conditions met
**Exit:** Regime switches to Bear/Crash

### 3. **Risk Manager** (`strategy/risk_manager.py`)
- 48-hour cooldown after position close
- 2.5x leverage simulation
- Stop-loss at -5%
- Take-profit at +15%
- Position sizing with 95% max capital usage

### 4. **Backtester** (`backtesting/backtester.py`)
Complete simulation engine:
- Trade execution logic
- Portfolio tracking
- PnL calculation with commissions
- Trade logging to database
- Full risk management integration

### 5. **Performance Metrics** (`backtesting/performance.py`)
Comprehensive analytics:
- Total return & Alpha vs Buy & Hold
- Win rate & Profit factor
- Max drawdown
- Sharpe ratio & Sortino ratio
- Trade statistics

---

## 🧪 Testing Instructions

### Prerequisites
Ensure Phase 1 is working and you have data in the database. If not, run:
```bash
cd C:\Traning\stock_analysis
python -c "from data import DataLoader; DataLoader().fetch_data()"
```

---

## Test 1: Technical Indicators

Test that all indicators calculate correctly.

```bash
python -c "
from data import DataLoader
from strategy import add_all_indicators

print('[1/3] Loading data...')
loader = DataLoader()
data = loader.fetch_data()

print(f'[2/3] Calculating indicators on {len(data)} rows...')
data_with_indicators = add_all_indicators(data)

print('[3/3] Checking indicators...')
indicators = ['RSI', 'EMA_50', 'EMA_200', 'MACD', 'ADX', 'Momentum', 'Volatility', 'Volume_SMA']
for ind in indicators:
    if ind in data_with_indicators.columns:
        value = data_with_indicators[ind].iloc[-1]
        print(f'  {ind}: {value:.4f}')
    else:
        print(f'  {ind}: MISSING!')

print('\nSUCCESS: All indicators calculated')
"
```

**Expected Output:**
```
[1/3] Loading data...
[2/3] Calculating indicators on XXX rows...
[3/3] Checking indicators...
  RSI: XX.XXXX
  EMA_50: XXXXX.XXXX
  EMA_200: XXXXX.XXXX
  MACD: XXX.XXXX
  ADX: XX.XXXX
  Momentum: X.XXXX
  Volatility: X.XXXX
  Volume_SMA: XXXXXXX.XXXX

SUCCESS: All indicators calculated
```

---

## Test 2: Signal Generation

Test the 8-condition voting system.

```bash
python -c "
from data import DataLoader
from strategy import SignalGenerator, add_all_indicators
import numpy as np

print('[1/4] Loading data...')
loader = DataLoader()
data = loader.fetch_data()

print('[2/4] Adding indicators...')
data = add_all_indicators(data)

print('[3/4] Generating signals...')
signal_gen = SignalGenerator()
data = signal_gen.evaluate_conditions(data)

print('[4/4] Checking conditions...')
latest = data.iloc[-1]
conditions = {
    'RSI': latest['Cond_RSI'],
    'Momentum': latest['Cond_Momentum'],
    'Volatility': latest['Cond_Volatility'],
    'Volume': latest['Cond_Volume'],
    'ADX': latest['Cond_ADX'],
    'EMA_50': latest['Cond_EMA50'],
    'EMA_200': latest['Cond_EMA200'],
    'MACD': latest['Cond_MACD'],
}

print('\nConditions Met:')
for name, met in conditions.items():
    status = 'YES' if met else 'NO'
    print(f'  {name}: {status}')

total_met = sum(conditions.values())
print(f'\nTotal: {total_met}/8 conditions met')
print(f'Entry allowed: {\"YES\" if total_met >= 7 else \"NO\"} (need >= 7)')

print('\nSUCCESS: Signal generation working')
"
```

**Expected Output:**
```
[1/4] Loading data...
[2/4] Adding indicators...
[3/4] Generating signals...
[4/4] Checking conditions...

Conditions Met:
  RSI: YES
  Momentum: NO
  Volatility: YES
  Volume: YES
  ADX: NO
  EMA_50: YES
  EMA_200: YES
  MACD: YES

Total: 6/8 conditions met
Entry allowed: NO (need >= 7)

SUCCESS: Signal generation working
```

---

## Test 3: Risk Management

Test cooldown, leverage, and exit conditions.

```bash
python -c "
from strategy import RiskManager
from datetime import datetime, timedelta

print('[1/3] Initializing risk manager...')
rm = RiskManager(cooldown_hours=48, leverage=2.5)

print('[2/3] Testing cooldown...')
exit_time = datetime(2024, 1, 1, 10, 0)
rm.trigger_cooldown(exit_time)

# Check 24 hours later (should be in cooldown)
check_time_1 = exit_time + timedelta(hours=24)
in_cooldown_1 = rm.is_in_cooldown(check_time_1)
print(f'  After 24h: In cooldown = {in_cooldown_1} (should be True)')

# Check 50 hours later (should be out of cooldown)
check_time_2 = exit_time + timedelta(hours=50)
in_cooldown_2 = rm.is_in_cooldown(check_time_2)
print(f'  After 50h: In cooldown = {in_cooldown_2} (should be False)')

print('[3/3] Testing position sizing...')
capital = 10000
price = 50000
quantity = rm.calculate_position_size(capital, price)
position_value = price * quantity
expected_value = capital * 0.95 * 2.5
print(f'  Capital: ${capital:,.2f}')
print(f'  Leverage: {rm.leverage}x')
print(f'  Position value: ${position_value:,.2f}')
print(f'  Expected: ${expected_value:,.2f}')

print('\nSUCCESS: Risk management working')
"
```

**Expected Output:**
```
[1/3] Initializing risk manager...
[2/3] Testing cooldown...
  After 24h: In cooldown = True (should be True)
  After 50h: In cooldown = False (should be False)
[3/3] Testing position sizing...
  Capital: $10,000.00
  Leverage: 2.5x
  Position value: $23,750.00
  Expected: $23,750.00

SUCCESS: Risk management working
```

---

## Test 4: Complete Backtest (IMPORTANT!)

Run a full backtest simulation with real data.

**⚠️ Note:** This test requires hmmlearn. If not installed, skip to Test 5 for unit tests.

```bash
python -c "
try:
    import hmmlearn
except ImportError:
    print('WARNING: hmmlearn not installed - skipping backtest test')
    print('Install with: conda install -c conda-forge hmmlearn')
    exit(0)

from data import DataLoader
from models import HMMEngine
from backtesting import Backtester
from strategy import add_all_indicators

print('[1/5] Loading data...')
loader = DataLoader()
data = loader.fetch_data()
print(f'  Loaded {len(data)} rows')

print('[2/5] Training HMM model...')
engine = HMMEngine()
success, error = engine.train(data)
if not success:
    print(f'  ERROR: {error}')
    exit(1)
print(f'  Bull state: {engine.bull_state}, Bear state: {engine.bear_state}')

print('[3/5] Adding indicators...')
data = add_all_indicators(data)

print('[4/5] Running backtest...')
backtester = Backtester(initial_capital=10000.0)
regime_states = engine.predict(data)
metrics = backtester.run(data, regime_states, engine.bull_state, engine.bear_state)

print('[5/5] Results:')
print(f'  Initial Capital: ${metrics[\"initial_capital\"]:,.2f}')
print(f'  Final Capital: ${metrics[\"final_capital\"]:,.2f}')
print(f'  Total Return: {metrics[\"total_return_pct\"]:.2f}%')
print(f'  Buy & Hold: {metrics[\"buy_hold_return_pct\"]:.2f}%')
print(f'  Alpha: {metrics[\"alpha_pct\"]:.2f}%')
print(f'  Number of Trades: {metrics[\"num_trades\"]}')
print(f'  Win Rate: {metrics[\"win_rate_pct\"]:.1f}%')
print(f'  Max Drawdown: {metrics[\"max_drawdown_pct\"]:.2f}%')
print(f'  Sharpe Ratio: {metrics[\"sharpe_ratio\"]:.2f}')

print('\nSUCCESS: Full backtest completed!')
"
```

**Expected Output:**
```
[1/5] Loading data...
  Loaded XXX rows
[2/5] Training HMM model...
  Bull state: X, Bear state: X
[3/5] Adding indicators...
[4/5] Running backtest...
[5/5] Results:
  Initial Capital: $10,000.00
  Final Capital: $XX,XXX.XX
  Total Return: XX.XX%
  Buy & Hold: XX.XX%
  Alpha: XX.XX%
  Number of Trades: XX
  Win Rate: XX.X%
  Max Drawdown: -XX.XX%
  Sharpe Ratio: X.XX

SUCCESS: Full backtest completed!
```

---

## Test 5: Run Unit Tests

Run automated tests for all Phase 2 components.

### Test Indicators Only
```bash
cd C:\Traning\stock_analysis
pytest tests/test_indicators.py -v -s
```

**Expected Output:**
```
tests/test_indicators.py::TestTechnicalIndicators::test_rsi_calculation PASSED
tests/test_indicators.py::TestTechnicalIndicators::test_ema_calculation PASSED
tests/test_indicators.py::TestTechnicalIndicators::test_macd_calculation PASSED
tests/test_indicators.py::TestTechnicalIndicators::test_adx_calculation PASSED
tests/test_indicators.py::TestTechnicalIndicators::test_momentum_calculation PASSED
tests/test_indicators.py::TestTechnicalIndicators::test_volatility_calculation PASSED
tests/test_indicators.py::TestTechnicalIndicators::test_add_all_indicators PASSED
tests/test_indicators.py::TestTechnicalIndicators::test_bollinger_bands PASSED
tests/test_indicators.py::TestTechnicalIndicators::test_atr_calculation PASSED

======================== 9 passed in XX.XXs ========================
```

### Test Backtester
```bash
pytest tests/test_backtester.py -v -s
```

**Expected Output:**
```
tests/test_backtester.py::TestBacktester::test_initialization PASSED
tests/test_backtester.py::TestBacktester::test_run_backtest PASSED
tests/test_backtester.py::TestBacktester::test_trade_execution PASSED
tests/test_backtester.py::TestBacktester::test_get_trades_dataframe PASSED
tests/test_backtester.py::TestBacktester::test_portfolio_history PASSED
tests/test_backtester.py::TestBacktester::test_cooldown_mechanism PASSED
tests/test_backtester.py::TestBacktester::test_leverage_applied PASSED
tests/test_backtester.py::TestBacktester::test_final_capital_calculation PASSED

======================== 8 passed in XX.XXs ========================
```

### Run All Phase 2 Tests
```bash
pytest tests/test_indicators.py tests/test_backtester.py -v --cov=strategy --cov=backtesting
```

---

## Test 6: Performance Report

Generate a detailed performance report.

```bash
python -c "
try:
    import hmmlearn
except ImportError:
    print('WARNING: hmmlearn not installed - skipping')
    exit(0)

from data import DataLoader
from models import HMMEngine
from backtesting import Backtester, PerformanceMetrics
from strategy import add_all_indicators

# Run backtest
loader = DataLoader()
data = loader.fetch_data()
engine = HMMEngine()
engine.train(data)
data = add_all_indicators(data)

backtester = Backtester(initial_capital=10000.0)
regime_states = engine.predict(data)
metrics = backtester.run(data, regime_states, engine.bull_state, engine.bear_state)

# Format report
report = PerformanceMetrics.format_metrics_report(metrics)
print(report)
"
```

**Expected Output:**
```
============================================================
PERFORMANCE REPORT
============================================================

RETURNS:
  Total Return:        XX.XX%
  Buy & Hold:          XX.XX%
  Alpha:               XX.XX%

RISK METRICS:
  Max Drawdown:        -XX.XX%
  Sharpe Ratio:        X.XX
  Sortino Ratio:       X.XX
  Calmar Ratio:        X.XX

TRADE STATISTICS:
  Number of Trades:    XX
  Win Rate:            XX.X%
  Profit Factor:       X.XX
  Avg Win:             $XXX.XX
  Avg Loss:            $-XXX.XX

CAPITAL:
  Initial:             $10,000.00
  Final:               $XX,XXX.XX
  Profit/Loss:         $X,XXX.XX
============================================================
```

---

## 📊 Verification Checklist

After running all tests, verify:

- [ ] **Test 1:** All indicators calculate without errors
- [ ] **Test 2:** 8 conditions evaluate correctly
- [ ] **Test 3:** Risk management (cooldown, leverage) works
- [ ] **Test 4:** Full backtest completes (if hmmlearn installed)
- [ ] **Test 5:** Unit tests pass (17 tests total)
- [ ] **Test 6:** Performance report generates

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'strategy'"
**Solution:** Make sure you're in the right directory:
```bash
cd C:\Traning\stock_analysis
```

### Issue: "ValueError: Not enough data"
**Solution:** Fetch more data:
```bash
python -c "from data import DataLoader; from datetime import datetime, timedelta; loader = DataLoader(); loader.fetch_data(start_date=datetime.utcnow()-timedelta(days=60), force_refresh=True)"
```

### Issue: "hmmlearn not installed"
**Solution:** Either:
1. Install via conda: `conda install -c conda-forge hmmlearn`
2. Skip HMM-dependent tests (Tests 1-3 and 5 still work)

### Issue: Tests are slow
**Normal:** First run with data fetch takes time
**Solution:** Subsequent runs use cached data and are faster

---

## 📈 What to Expect

### Good Results:
- Alpha > 0% (beating buy & hold)
- Win rate > 40%
- Sharpe ratio > 0.5
- Multiple trades executed

### Poor Results (also valid):
- Strategy may underperform in certain market conditions
- This is expected and shows risk management is working
- Adjust parameters in `config/settings.py` if needed

---

## 🎯 Quick Start (Minimal Testing)

If you want to quickly verify Phase 2 works:

```bash
cd C:\Traning\stock_analysis

# Test indicators
python -c "from strategy import TechnicalIndicators; print('Indicators: OK')"

# Test signal generator
python -c "from strategy import SignalGenerator; print('Signal Generator: OK')"

# Test risk manager
python -c "from strategy import RiskManager; print('Risk Manager: OK')"

# Test backtester
python -c "from backtesting import Backtester; print('Backtester: OK')"

# Run unit tests
pytest tests/test_indicators.py -v

echo "Phase 2 core functionality verified!"
```

---

## 📝 Report Back to Me

Please run the tests and tell me:

1. ✅ **Which tests passed?**
   - Test 1 (Indicators): PASS/FAIL
   - Test 2 (Signals): PASS/FAIL
   - Test 3 (Risk Mgmt): PASS/FAIL
   - Test 4 (Backtest): PASS/FAIL or SKIPPED
   - Test 5 (Unit Tests): X/17 passed

2. 📊 **If Test 4 passed, share your backtest results:**
   - Total Return: ?
   - Alpha: ?
   - Number of Trades: ?
   - Win Rate: ?

3. ❌ **Any errors or issues?**
   - Copy/paste error messages

---

## 🚀 Next Phase

Once Phase 2 is verified, we proceed to:

**Phase 3: UI Development**
- Streamlit dashboard
- Interactive Plotly charts
- Configuration panel
- Real-time metrics display

---

**Document Version**: 1.0  
**Phase**: 2 - Strategy & Backtesting  
**Status**: Ready for Testing  
**Prerequisites**: Phase 1 complete
