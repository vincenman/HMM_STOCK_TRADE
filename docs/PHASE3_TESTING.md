# Phase 3 Testing Guide - UI Development

## 📋 Overview

Phase 3 implements a complete Streamlit dashboard with:
- ✅ Interactive web interface
- ✅ Real-time market data display
- ✅ Regime detection visualization
- ✅ Interactive Plotly charts
- ✅ Performance metrics dashboard
- ✅ Configuration panel
- ✅ Trade history viewer

---

## 🎯 What Was Implemented

### 1. **Main Dashboard** (`app.py`)
- Multi-tab layout (Overview, Backtest, Configuration, About)
- Real-time signal display
- Current regime detection
- Interactive sidebar controls
- Data loading and model training interface

### 2. **Chart Components** (`ui/components/charts.py`)
- Candlestick chart with regime highlighting
- Portfolio value over time
- Drawdown visualization
- Returns distribution
- Volume indicators

### 3. **Metrics Components** (`ui/components/metrics.py`)
- Performance metrics grid
- Current signal card
- Conditions status table
- Trade summary statistics

### 4. **Configuration Panel** (`ui/components/config_panel.py`)
- Adjustable strategy parameters
- Save/Load configuration
- Export/Import settings
- Real-time parameter preview

---

## 🚀 How to Run the Dashboard

### Step 1: Verify Prerequisites

```bash
cd C:\Traning\stock_analysis

# Test that components work
python test_phase3.py
```

**Expected output:**
```
PHASE 3: UI COMPONENTS TEST
[1/4] Testing UI component imports...
[OK] UI components imported successfully
[2/4] Testing Streamlit import...
[OK] Streamlit version: X.XX.X
[3/4] Testing Plotly import...
[OK] Plotly version: X.XX.X
[4/4] Checking main app file...
[OK] app.py found

To start the dashboard:
  1. cd C:\Traning\stock_analysis
  2. streamlit run app.py
```

### Step 2: Start the Dashboard

```bash
cd C:\Traning\stock_analysis
streamlit run app.py
```

**What happens:**
- Streamlit will start a local web server
- Your default browser will open automatically
- Dashboard will be at: `http://localhost:8501`

### Step 3: Use the Dashboard

1. **Load Data** - Click "🔄 Refresh Data" in sidebar
2. **Train Model** - Click "🎯 Train Model" (requires hmmlearn)
3. **Run Backtest** - Click "▶️ Run Backtest"
4. **View Results** - Explore tabs and charts

---

## 📊 Dashboard Features

### Overview Tab
- **Current Signal**: LONG/CASH with conditions met
- **Market Regime**: Bull/Bear/Neutral with confidence
- **BTC Price**: Latest price
- **Interactive Chart**: Candlestick with regime colors
  - Green background = Bull regime
  - Red background = Bear regime
  - Gray = Neutral

### Backtest Results Tab
- **Performance Metrics Grid**:
  - Total Return, Alpha, Sharpe Ratio
  - Win Rate, Profit Factor
  - Max Drawdown
- **Portfolio Chart**: Value over time
- **Trade History**: Downloadable CSV
- **Trade Summary**: Best/worst trades

### Configuration Tab
- **Entry Conditions**: RSI, Momentum, Volatility, ADX, EMAs
- **Risk Management**: Cooldown, Leverage, Stop-loss, Take-profit
- **Save/Load**: Persistent configurations
- **Export/Import**: JSON format

### About Tab
- System information
- Strategy explanation
- Technology stack
- Disclaimers

---

## 🧪 Testing Instructions

### Test 1: Component Import Test

```bash
cd C:\Traning\stock_analysis
python test_phase3.py
```

**Pass Criteria:**
- [x] All imports successful
- [x] Streamlit version displayed
- [x] Plotly version displayed
- [x] app.py file found

---

### Test 2: Start Dashboard

```bash
streamlit run app.py
```

**Pass Criteria:**
- [x] Server starts without errors
- [x] Browser opens automatically
- [x] Dashboard loads at localhost:8501
- [x] Sidebar visible
- [x] Main content area visible

---

### Test 3: Load Data

**Steps:**
1. Click "🔄 Refresh Data" in sidebar
2. Wait for data to load (30-60 seconds first time)

**Pass Criteria:**
- [x] Success message appears
- [x] Shows "Loaded X rows"
- [x] Chart appears in Overview tab
- [x] BTC Price displays

---

### Test 4: Train Model (If hmmlearn installed)

**Steps:**
1. After loading data
2. Click "🎯 Train Model"
3. Wait for training (~30 seconds)

**Pass Criteria:**
- [x] Success message "Model trained!"
- [x] Current Signal shows regime
- [x] Conditions Met displays

**If hmmlearn NOT installed:**
- Warning message appears
- Button is disabled
- This is expected - you can skip to Test 6

---

### Test 5: Run Backtest (If hmmlearn installed)

**Steps:**
1. After training model
2. Click "▶️ Run Backtest"
3. Wait for completion (~30 seconds)

**Pass Criteria:**
- [x] Success message "Backtest complete!"
- [x] Backtest Results tab shows metrics
- [x] Charts display correctly
- [x] Trade history appears

---

### Test 6: Test UI Interactions

**Chart Interactions:**
- [x] Hover over chart shows tooltips
- [x] Zoom in/out works
- [x] Pan left/right works
- [x] Trade markers visible (if backtest ran)

**Tab Navigation:**
- [x] All 4 tabs clickable
- [x] Content loads in each tab
- [x] No errors in any tab

**Configuration Panel:**
- [x] Sliders move smoothly
- [x] Values update
- [x] Save button works
- [x] Download config works

---

### Test 7: Export Data

**Steps:**
1. Go to "Backtest Results" tab
2. Scroll to Trade History
3. Click "📥 Download Trade History"

**Pass Criteria:**
- [x] CSV file downloads
- [x] File opens in Excel/spreadsheet
- [x] Contains trade data

---

## 📸 Screenshots to Capture

Please take screenshots of:

1. **Overview Tab** - Showing current signal and chart
2. **Backtest Results** - Showing metrics grid
3. **Configuration Tab** - Showing sliders
4. **Trade History** - Showing table

---

## 🐛 Common Issues & Solutions

### Issue: "streamlit: command not found"
**Solution:**
```bash
pip install streamlit
```

### Issue: Browser doesn't open automatically
**Solution:**
- Manually open: http://localhost:8501
- Or click the link in terminal output

### Issue: "Address already in use"
**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Issue: Charts don't display
**Solution:**
- Check console for errors
- Ensure plotly is installed: `pip install plotly`

### Issue: "hmmlearn not installed" warning
**Solution:**
- This is expected on Python 3.14
- Dashboard still works for viewing data and configuration
- Install hmmlearn for full functionality:
  ```bash
  conda install -c conda-forge hmmlearn
  ```

### Issue: Data loading fails
**Solution:**
- Check internet connection
- yfinance might be down temporarily
- Try again in a few minutes

### Issue: Dashboard is slow
**Solution:**
- First load is slower (fetches data)
- Subsequent loads use cache
- Reduce lookback days in sidebar

---

## 📋 Verification Checklist

After testing, verify:

- [ ] Dashboard starts successfully
- [ ] Data loads from yfinance
- [ ] Charts display correctly
- [ ] Tabs are navigable
- [ ] Metrics display properly
- [ ] Configuration panel works
- [ ] Export functionality works
- [ ] No critical errors in console

---

## 📊 What to Report

### 1. Test Results
- Which tests passed? (1-7)
- Which tests failed? (if any)
- Which tests skipped? (if hmmlearn not installed)

### 2. Screenshots
- Share screenshot of Overview tab
- Share screenshot of any errors

### 3. Performance
- How long did data loading take?
- Is the dashboard responsive?
- Any lag or slowness?

### 4. Errors
- Any error messages in browser console?
- Any error messages in terminal?
- Copy/paste error text

---

## 🎯 Success Criteria

**Minimum (Without hmmlearn):**
- [x] Dashboard starts
- [x] Data loads and displays
- [x] Charts render
- [x] All tabs accessible
- [x] Configuration panel works

**Full (With hmmlearn):**
- [x] All minimum criteria
- [x] Model trains successfully
- [x] Backtest runs
- [x] Regime detection works
- [x] Signals generate correctly

---

## 🚀 Next Steps

Once Phase 3 is verified:
1. Report which tests passed
2. Share screenshots
3. Note any issues
4. Proceed to Phase 4: Paper Trading & Export Features

---

## 💡 Tips

- **First Time**: Initial data fetch takes 30-60 seconds
- **Subsequent Runs**: Much faster due to caching
- **Without hmmlearn**: Dashboard still useful for data viewing and configuration
- **Stop Dashboard**: Press `Ctrl+C` in terminal
- **Restart**: Run `streamlit run app.py` again

---

## 📱 Mobile/Tablet Support

The dashboard is responsive and works on tablets (iPad, etc.). Mobile phones may have limited functionality due to screen size.

---

**Document Version**: 1.0  
**Phase**: 3 - UI Development  
**Status**: Ready for Testing  
**Prerequisites**: Phase 1 & 2 complete
