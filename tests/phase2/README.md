# Phase 2 Testing Files

## 📋 Quick Start

All Phase 2 tests are organized in this folder for easy testing.

---

## 🚀 How to Run Tests

### Option 1: Run Individual Tests

Open Command Prompt and navigate to the project:
```bash
cd C:\Traning\stock_analysis
```

Then run any test individually:

```bash
# Test 1: Technical Indicators
python tests/phase2/test1_indicators.py

# Test 2: Signal Generation (8-condition voting)
python tests/phase2/test2_signals.py

# Test 3: Risk Management
python tests/phase2/test3_risk_management.py

# Test 4: Complete Backtest (requires hmmlearn)
python tests/phase2/test4_backtest.py

# Test 5: Unit Tests
python tests/phase2/test5_unit_tests.py
```

### Option 2: Run All Tests at Once

```bash
python tests/phase2/run_all_tests.py
```

This will run all tests sequentially with pauses between each test.

---

## 📁 Test Files

| File | Description | Dependencies |
|------|-------------|--------------|
| `test1_indicators.py` | Tests technical indicator calculations | None |
| `test2_signals.py` | Tests 8-condition voting system | None |
| `test3_risk_management.py` | Tests cooldown, leverage, position sizing | None |
| `test4_backtest.py` | Full backtest simulation | **Requires hmmlearn** |
| `test5_unit_tests.py` | Runs pytest unit tests | pytest |
| `run_all_tests.py` | Runs all tests sequentially | None |

---

## ✅ What Each Test Does

### Test 1: Technical Indicators
- Loads data from database
- Calculates 15+ technical indicators
- Shows current values for each indicator
- **Time:** ~10 seconds

### Test 2: Signal Generation
- Evaluates 8 trading conditions
- Shows which conditions are met (YES/NO)
- Indicates if entry is allowed (need ≥7 conditions)
- **Time:** ~15 seconds

### Test 3: Risk Management
- Tests cooldown mechanism (48 hours)
- Tests position sizing with leverage (2.5x)
- Tests exit conditions (stop-loss, take-profit)
- **Time:** <1 second

### Test 4: Complete Backtest
- Trains HMM model on real data
- Runs full backtest simulation
- Shows comprehensive performance metrics
- **Time:** 30-60 seconds
- **⚠️ Requires hmmlearn** - will skip if not installed

### Test 5: Unit Tests
- Runs pytest test suite
- 9 tests for indicators
- 8 tests for backtester
- **Time:** 20-30 seconds

---

## 📊 Expected Results

### Test 1 Output:
```
TEST 1: TECHNICAL INDICATORS
[1/3] Loading data...
  Loaded 168 rows
[2/3] Calculating indicators...
[3/3] Checking indicators...

Indicator Values (Latest):
  RSI                 :         XX.XXXX
  EMA_50              :     XX,XXX.XXXX
  ...
TEST 1: SUCCESS ✓
```

### Test 2 Output:
```
TEST 2: SIGNAL GENERATION
[1/4] Loading data...
[2/4] Adding indicators...
[3/4] Generating signals...
[4/4] Checking conditions...

Conditions Met:
  ✓ YES  RSI < 90
  ✗ NO   Momentum > 1%
  ...
Total: 6/8 conditions met
Entry allowed: NO ✗ (need >= 7 conditions)

TEST 2: SUCCESS ✓
```

### Test 3 Output:
```
TEST 3: RISK MANAGEMENT
[1/4] Initializing risk manager...
  Cooldown: 48 hours
  Leverage: 2.5x
[2/4] Testing cooldown mechanism...
  After 24h: In cooldown = True (expected: True)
  After 50h: In cooldown = False (expected: False)
  ✓ Cooldown mechanism working correctly
...
TEST 3: SUCCESS ✓
```

### Test 4 Output (if hmmlearn installed):
```
TEST 4: COMPLETE BACKTEST
✓ hmmlearn is installed - proceeding with test
[1/5] Loading data...
[2/5] Training HMM model...
[3/5] Adding indicators...
[4/5] Running backtest...
[5/5] Results:
  Initial Capital:     $10,000.00
  Final Capital:       $XX,XXX.XX
  Total Return:           XX.XX%
  Alpha (vs B&H):         XX.XX%
  Number of Trades:           XX
  Win Rate:                XX.X%
...
TEST 4: SUCCESS ✓
```

---

## 🐛 Troubleshooting

### Error: "No module named 'strategy'"
**Fix:** Make sure you're in the correct directory:
```bash
cd C:\Traning\stock_analysis
```

### Error: "No cached data"
**Fix:** Fetch data first:
```bash
python -c "from data import DataLoader; DataLoader().fetch_data()"
```

### Test 4: "hmmlearn not installed"
**This is expected!** Test 4 will skip if hmmlearn is not installed.
- Tests 1-3 and 5 work without hmmlearn
- To install hmmlearn: `conda install -c conda-forge hmmlearn`
- Or use Python 3.11-3.13 instead of 3.14

### Tests are slow
**Normal:** First run fetches data from API (30-60 seconds)
**Solution:** Subsequent runs use cached data and are faster

---

## 📝 What to Report

After running tests, report:

1. **Which tests passed?**
   - Test 1: ✅/❌
   - Test 2: ✅/❌
   - Test 3: ✅/❌
   - Test 4: ✅/❌/SKIPPED
   - Test 5: X/17 passed

2. **If Test 4 ran, share these metrics:**
   - Total Return: ?%
   - Alpha: ?%
   - Number of Trades: ?
   - Win Rate: ?%

3. **Any errors?** Copy/paste the error message

---

## 🎯 Quick Verification

To quickly verify Phase 2 is working, run just Tests 1-3:

```bash
cd C:\Traning\stock_analysis
python tests/phase2/test1_indicators.py
python tests/phase2/test2_signals.py
python tests/phase2/test3_risk_management.py
```

These tests don't require hmmlearn and should complete in ~30 seconds total.

---

## 📚 More Information

- **Full testing guide:** `docs/PHASE2_TESTING.md`
- **Implementation summary:** `docs/PHASE2_SUMMARY.md`
- **Configuration:** `config/settings.py`

---

## 🚀 Next Steps

Once all tests pass (or Tests 1-3 if hmmlearn not installed):
1. Report results back
2. Proceed to **Phase 3: UI Development**

---

**Happy Testing!** 🧪
