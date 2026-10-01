# 📖 User Manual - HMM Trading Dashboard

## 🎯 Introduction

Welcome to the HMM Trading Dashboard! This manual will guide you through all features and functionality.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Loading Data](#loading-data)
4. [Training the Model](#training-the-model)
5. [Running Backtests](#running-backtests)
6. [Paper Trading](#paper-trading)
7. [Configuration](#configuration)
8. [Exporting Data](#exporting-data)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## 🚀 Getting Started

### **System Requirements**

- **Browser:** Chrome, Firefox, Edge, or Safari (latest version)
- **Internet:** Required for data fetching
- **Screen:** Minimum 1280x720 resolution recommended

### **Accessing the Dashboard**

**Local Installation:**
```bash
cd C:\Traning\stock_analysis
run_dashboard.bat
```

**Cloud Deployment:**
Navigate to your deployed URL (e.g., `https://your-app.streamlit.app`)

### **First Time Setup**

1. Dashboard opens automatically in your browser
2. You'll see 5 tabs: Overview, Backtest Results, Paper Trading, Configuration, About
3. Sidebar on the left contains controls and settings

---

## 🎛️ Dashboard Overview

### **Main Components**

#### **Sidebar (Left Panel)**
- **Data Settings:** Load and refresh market data
- **Model Settings:** Train HMM model
- **Strategy Settings:** Run backtests and adjust parameters

#### **Main Area (Center)**
- **Tabs:** Switch between different views
- **Charts:** Interactive visualizations
- **Metrics:** Performance indicators
- **Tables:** Trade history and details

#### **Status Bar (Top)**
- Current signal (LONG/CASH)
- Market regime (Bull/Bear/Neutral)
- Conditions met
- Latest BTC price

---

## 📊 Loading Data

### **Step 1: Set Lookback Period**

In the sidebar under "📊 Data Settings":
1. Use the slider: **"Lookback Days"**
2. Range: 30 to 365 days
3. Recommended: **60 days** for testing, **300 days** for production

### **Step 2: Force Refresh (Optional)**

- **Unchecked:** Uses cached data (faster)
- **Checked:** Fetches fresh data from yfinance (slower but up-to-date)

**When to use Force Refresh:**
- First time loading
- Want latest data
- Cache seems stale

### **Step 3: Click "🔄 Refresh Data"**

1. Click the button
2. Wait 10-30 seconds
3. Success message shows: "✅ Loaded XXX rows"
4. Chart appears in Overview tab

### **Understanding the Data**

**Data Source:** yfinance (Yahoo Finance)  
**Symbol:** BTC-USD (Bitcoin)  
**Interval:** 1 hour  
**Columns:** Open, High, Low, Close, Volume  

**Example:**
```
Loaded 7,166 rows from 2025-12-04 to 2026-09-30
```

---

## 🤖 Training the Model

### **What is the HMM Model?**

**Hidden Markov Model (HMM)** identifies market regimes:
- **7 States** representing different market conditions
- **Bull State:** Highest returns (good for buying)
- **Bear State:** Lowest returns (avoid trading)
- **Neutral States:** Intermediate conditions

### **Step 1: Load Data First**

⚠️ Must load data before training!

### **Step 2: Set HMM States**

In sidebar under "🤖 Model Settings":
1. **HMM States:** Number of states (default 7)
2. Range: 3 to 10
3. Recommended: **7** (good balance)

### **Step 3: Click "🎯 Train Model"**

1. Click the button
2. Wait 20-40 seconds
3. Success message: "✅ Model trained!"
4. Shows Bull state and Bear state numbers

**Example Output:**
```
✅ Model trained!
Bull state: 5
Bear state: 6
```

### **Understanding Training Results**

**In Overview Tab:**
- **Current Signal:** LONG or CASH
- **Market Regime:** Bull/Bear/Neutral
- **Confidence:** 85.3%
- **Conditions Met:** 7/8

---

## 📈 Running Backtests

### **What is Backtesting?**

Backtesting simulates your strategy on historical data to see how it would have performed.

### **Step 1: Prerequisites**

- ✅ Data loaded
- ✅ Model trained

### **Step 2: Click "▶️ Run Backtest"**

In sidebar under "💼 Strategy":
1. Click button
2. Wait 30-60 seconds
3. Success message appears
4. Results appear in "Backtest Results" tab

### **Understanding Results**

#### **Performance Metrics**

**Returns:**
- **Total Return:** Your strategy's profit/loss
- **Buy & Hold Return:** Just holding BTC
- **Alpha:** How much you beat buy & hold
- **Sharpe Ratio:** Risk-adjusted returns

**Example:**
```
Total Return:     +18.45%
Buy & Hold:       +12.30%
Alpha:            +6.15%  ← You beat the market!
Sharpe Ratio:     1.65
```

**Trade Statistics:**
- **Number of Trades:** How many trades executed
- **Win Rate:** Percentage of profitable trades
- **Profit Factor:** Total wins ÷ Total losses
- **Avg Win/Loss:** Average profit and loss per trade

**Example:**
```
Number of Trades: 22
Win Rate:         59.1%  ← 13 wins, 9 losses
Profit Factor:    1.89
Avg Win:          $287.34
Avg Loss:         -$152.18
```

**Risk Metrics:**
- **Max Drawdown:** Worst peak-to-trough decline
- **Calmar Ratio:** Return ÷ Max drawdown
- **Sortino Ratio:** Like Sharpe but only downside risk

#### **Interactive Charts**

**Portfolio Value Chart:**
- Shows your capital over time
- Starts at $10,000
- Green = profits, Red = losses
- Hover for exact values

**Price Chart with Trades:**
- BTC price over time
- Green markers = Buy
- Red markers = Sell
- Background colors = Regimes (green=bull, red=bear)

#### **Trade History Table**

Shows all trades with:
- Date and time
- Action (BUY/SELL)
- Price
- P&L (profit/loss)
- Return %
- Hold time
- Reason

**Download as CSV:**
- Click "📥 Download Trade History"
- Opens in Excel
- All trade details included

---

## 📡 Paper Trading

### **What is Paper Trading?**

Paper trading simulates real-time trading without risking real money.

**Differences from Backtest:**
- **Backtest:** Historical data, fast
- **Paper Trading:** Live prices, real-time

### **Prerequisites**

- ✅ Data loaded
- ✅ Model trained

### **Step 1: Go to Paper Trading Tab**

Click the **"📡 Paper Trading"** tab

### **Step 2: Start Trading**

Click **"▶️ Start Trading"**
- Status changes to 🟢 RUNNING
- Engine begins monitoring

### **Step 3: Manual Updates**

Click **"🔄 Manual Update"** to:
- Fetch latest BTC price
- Check trading conditions
- Execute trades if conditions met

**Repeat this every few minutes to see trades!**

### **Monitoring Your Trading**

#### **Current Status**
- **Status:** 🟢 RUNNING or ⚪ STOPPED
- **Current Capital:** Live balance
- **Total Return:** Percentage gain/loss
- **Trades Completed:** Number of closed trades

#### **Position Info** (When in trade)
- **Entry Price:** Price you bought at
- **Current Price:** Latest market price
- **Unrealized P&L:** Profit/loss on open position
- **Hold Time:** How long you've held

### **Stopping Trading**

Click **"⏸️ Stop Trading"** to pause

### **Resetting**

Click **"🔁 Reset Engine"** to:
- Clear all trades
- Reset capital to $10,000
- Start fresh

⚠️ Click twice to confirm!

### **Exporting Paper Trading Results**

**CSV Export:**
- Click "📥 Download CSV"
- Contains all trade details

**PDF Report:**
- Click "📄 Generate PDF Report"
- Professional report with:
  - Executive summary
  - Performance metrics
  - Trade statistics
  - Trade history

---

## ⚙️ Configuration

### **Accessing Configuration**

Go to **"⚙️ Configuration"** tab

### **Available Parameters**

#### **Entry Conditions**

**RSI Threshold:**
- **What:** Relative Strength Index limit
- **Default:** 90
- **Range:** 50-100
- **Higher = More selective**

**Momentum Threshold:**
- **What:** Minimum momentum required
- **Default:** 1%
- **Higher = Stronger trends only**

**Volatility Threshold:**
- **What:** Maximum volatility allowed
- **Default:** 6%
- **Lower = Less volatile entries**

**ADX Threshold:**
- **What:** Trend strength minimum
- **Default:** 25
- **Higher = Stronger trends**

**Volume Threshold:**
- **What:** Must exceed SMA
- **Default:** 20 periods
- **Ensures liquidity**

**EMA Settings:**
- **Short EMA:** Default 50
- **Long EMA:** Default 200
- **Price must be above both**

**Required Conditions:**
- **Default:** 7/8
- **Lower = More trades**
- **Higher = More selective**

#### **Risk Management**

**Stop Loss:**
- **Default:** -5%
- **Exits automatically at loss**
- **Lower = Tighter risk**

**Take Profit:**
- **Default:** +15%
- **Exits automatically at profit**
- **Higher = Larger targets**

**Leverage:**
- **Default:** 2.5x
- **Multiplies position size**
- **Higher = More risk & reward**

**Cooldown Period:**
- **Default:** 48 hours
- **Wait time after exit**
- **Prevents overtrading**

#### **Other Settings**

**Initial Capital:**
- **Default:** $10,000
- **Starting balance**

**Commission Rate:**
- **Default:** 0.1%
- **Per trade cost**

### **Applying Changes**

1. Adjust sliders/inputs
2. Changes save automatically
3. **Re-run backtest** to see effects

### **Saving/Loading Configurations**

**Export:**
- Click "💾 Export Configuration"
- Downloads JSON file
- Save for later use

**Import:**
- Click "📂 Import Configuration"
- Upload JSON file
- Settings restored

---

## 📥 Exporting Data

### **Trade History CSV**

**From Backtest:**
1. Go to "Backtest Results" tab
2. Click "📥 Download Trade History"
3. CSV file downloads

**From Paper Trading:**
1. Go to "Paper Trading" tab
2. Click "📥 Download CSV"
3. CSV file downloads

**CSV Contains:**
- Timestamp
- Action (BUY/SELL)
- Price
- Quantity
- P&L
- Return %
- Hold time
- Reason

**Use in Excel:**
- Open in Excel/Google Sheets
- Create pivot tables
- Generate charts
- Analyze patterns

### **PDF Reports**

**From Paper Trading:**
1. Click "📄 Generate PDF Report"
2. Wait for generation
3. Click "📥 Download PDF"

**Report Includes:**
- Cover page
- Executive summary
- Performance metrics table
- Trade statistics
- Strategy configuration
- Trade history (last 20 trades)

**Use Cases:**
- Share with team
- Document results
- Performance reviews
- Portfolio reporting

### **Configuration JSON**

**Export:**
- Go to Configuration tab
- Click "💾 Export Configuration"
- JSON file downloads

**Import:**
- Click "📂 Import Configuration"
- Upload JSON file

**Use Cases:**
- Backup settings
- Share strategies
- Version control
- A/B testing

---

## 🐛 Troubleshooting

### **Data Loading Issues**

**Problem:** "Error loading data"

**Solutions:**
1. Check internet connection
2. Try "Force Refresh"
3. Reduce lookback days
4. Wait and retry (yfinance may be slow)

---

**Problem:** Only 173 rows loaded instead of 7,000+

**Solution:**
1. Check "Force Refresh" checkbox
2. Click "Refresh Data" again
3. Wait for full download

---

### **Model Training Issues**

**Problem:** "Model not trained" or "hmmlearn not installed"

**Solutions:**
1. Install hmmlearn: `uv pip install hmmlearn`
2. Use Python 3.12 (not 3.14)
3. Run `setup_with_uv.bat`

---

**Problem:** "Insufficient data for training"

**Solutions:**
1. Load more data (300 days recommended)
2. Use "Force Refresh"
3. Check data loaded successfully

---

### **Backtest Issues**

**Problem:** No trades in backtest

**Causes:**
- Conditions too strict (7/8)
- Market mostly bearish
- Short time period

**Solutions:**
1. Lower required conditions to 6/8
2. Load more data
3. Check regime distribution in results

---

**Problem:** Poor performance (negative returns)

**Solutions:**
1. Adjust parameters in Configuration
2. Try different stop-loss/take-profit
3. Increase/decrease required conditions
4. Test different time periods

---

### **Paper Trading Issues**

**Problem:** No trades executing

**Check:**
1. Trading started? (🟢 RUNNING)
2. Clicked manual update?
3. Bull regime active? (check Overview)
4. 7+ conditions met?
5. Not in cooldown?

**Solution:** Keep clicking manual update!

---

**Problem:** PDF generation fails

**Solution:**
```bash
uv pip install reportlab
```

---

### **Performance Issues**

**Problem:** Dashboard slow or unresponsive

**Solutions:**
1. Reduce lookback days
2. Clear browser cache
3. Restart dashboard
4. Close other browser tabs
5. Use Chrome/Edge (fastest)

---

## ❓ FAQ

### **General Questions**

**Q: Is this real trading?**  
A: No! This is paper trading (simulation). No real money is used or at risk.

**Q: Can I use this for live trading?**  
A: Not directly. This is for analysis and testing only. Would need integration with a broker API.

**Q: What markets are supported?**  
A: Currently only BTC-USD. Can be extended to other symbols.

**Q: How accurate is the data?**  
A: Data from yfinance (Yahoo Finance) is generally reliable but may have delays.

---

### **Technical Questions**

**Q: What is HMM?**  
A: Hidden Markov Model - a machine learning algorithm that identifies market regimes.

**Q: How does the strategy work?**  
A: Enters LONG when in Bull regime AND 7/8 conditions met. Exits on regime change or stop-loss/take-profit.

**Q: What are the 8 conditions?**  
A:
1. RSI < 90
2. Momentum > 1%
3. Volatility < 6%
4. Volume > 20-SMA
5. ADX > 25
6. Price > 50 EMA
7. Price > 200 EMA
8. MACD > Signal

**Q: Why 48-hour cooldown?**  
A: Prevents overtrading and gives market time to establish new trends.

---

### **Strategy Questions**

**Q: What's a good win rate?**  
A: 50-60% is good. Above 60% is excellent. Strategy profitability depends more on profit factor.

**Q: What's a good Sharpe ratio?**  
A:
- < 1.0: Poor
- 1.0-2.0: Good
- > 2.0: Excellent

**Q: What's acceptable drawdown?**  
A:
- < 10%: Low risk
- 10-20%: Moderate risk
- > 20%: High risk

**Q: Why is my backtest negative?**  
A: Strategy may not work in all market conditions. Try:
- Different time periods
- Adjusted parameters
- Lower required conditions

---

### **Usage Questions**

**Q: How often should I update paper trading?**  
A: Every 5-15 minutes for active monitoring. Once per hour is fine for casual use.

**Q: Can I run multiple strategies?**  
A: Not directly. Would need to adjust parameters and re-run backtests.

**Q: How do I save my results?**  
A: Export CSV and PDF reports regularly. Configuration can also be saved as JSON.

**Q: Can I backtest other cryptocurrencies?**  
A: Code would need modification to support other symbols. Currently BTC-USD only.

---

## 📚 Additional Resources

### **Documentation**
- **README.md** - Project overview
- **DEPLOYMENT_GUIDE.md** - How to deploy
- **PHASE4_SUMMARY.md** - Phase 4 features
- **PHASE4_TESTING.md** - Testing guide

### **External Resources**
- **Streamlit Docs:** https://docs.streamlit.io
- **Pandas Docs:** https://pandas.pydata.org
- **yfinance Docs:** https://pypi.org/project/yfinance/
- **HMM Tutorial:** https://en.wikipedia.org/wiki/Hidden_Markov_model

### **Support**
- Report issues on GitHub
- Check documentation in `docs/` folder
- Review logs for error details

---

## 🎓 Learning Path

### **Beginner**
1. Load data and explore Overview tab
2. Train model and see regimes
3. Run simple backtest
4. Understand metrics

### **Intermediate**
1. Adjust configuration parameters
2. Compare different settings
3. Use paper trading
4. Export and analyze results

### **Advanced**
1. Optimize parameters systematically
2. Test multiple time periods
3. Analyze trade patterns
4. Develop custom strategies

---

## ✅ Quick Reference

### **Essential Workflow**
```
1. Load Data (300 days, Force Refresh)
2. Train Model (7 states)
3. Run Backtest
4. Review Results
5. Adjust Config
6. Test with Paper Trading
7. Export Results
```

### **Key Metrics**
- **Alpha > 0%** = Beat buy & hold
- **Win Rate > 50%** = More wins than losses
- **Sharpe > 1.0** = Good risk-adjusted returns
- **Max DD < 15%** = Acceptable risk

### **Common Actions**
- **Load data:** Sidebar → Refresh Data
- **Train model:** Sidebar → Train Model
- **Run backtest:** Sidebar → Run Backtest
- **Paper trade:** Paper Trading tab → Start Trading
- **Export:** Backtest/Paper Trading tab → Download buttons

---

**Happy Trading!** 📈

*Remember: This is educational software. Not financial advice. Past performance doesn't guarantee future results.*
