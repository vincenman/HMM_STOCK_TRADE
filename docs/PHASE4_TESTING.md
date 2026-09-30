# Phase 4 Testing Guide

## 🎯 Objective

Test the new paper trading features to ensure they work correctly.

---

## ✅ Prerequisites

Before testing Phase 4:

- [ ] Phase 3 completed and working
- [ ] Dashboard can load data and train model
- [ ] Backtest runs successfully

---

## 🚀 Setup Instructions

### **Step 1: Install New Dependencies**

```bash
cd C:\Traning\stock_analysis
setup_phase4.bat
```

**Or manually:**

```bash
.venv\Scripts\activate
uv pip install reportlab
```

---

### **Step 2: Restart Dashboard**

```bash
run_dashboard.bat
```

---

## 📋 Test Plan

### **Test 1: Access Paper Trading Tab**

**Steps:**
1. Start dashboard
2. Load data (300 days)
3. Train model
4. Click "📡 Paper Trading" tab

**Expected:**
- [ ] Tab is visible in tab bar
- [ ] Tab loads without errors
- [ ] Shows "✅ Prerequisites met!" message
- [ ] Control panel visible

**Result:** PASS / FAIL

---

### **Test 2: Start Paper Trading**

**Steps:**
1. In Paper Trading tab
2. Click "▶️ Start Trading" button

**Expected:**
- [ ] Button becomes disabled
- [ ] Success message appears
- [ ] Status shows "🟢 RUNNING"
- [ ] Stop button becomes enabled

**Result:** PASS / FAIL

---

### **Test 3: Manual Price Update**

**Steps:**
1. With trading started
2. Click "🔄 Manual Update" button
3. Wait ~5 seconds

**Expected:**
- [ ] Success message with price appears
- [ ] "Last Price" updates
- [ ] No errors
- [ ] Status refreshes

**Result:** PASS / FAIL

**Note the price:** $________

---

### **Test 4: Monitor Current Status**

**Check these metrics:**
- [ ] Status: 🟢 RUNNING or ⚪ STOPPED
- [ ] Current Capital: Shows value
- [ ] Total Return: Shows percentage
- [ ] Trades Completed: Shows number

**Current values:**
- Capital: $________
- Return: _______% 
- Trades: _______

**Result:** PASS / FAIL

---

### **Test 5: Execute a Trade (May Take Multiple Updates)**

**Steps:**
1. Click "Manual Update" multiple times
2. Wait for trade entry
3. Continue updating to see exit

**Expected:**
- [ ] Eventually enters position (when conditions met)
- [ ] "📍 Current Position" section appears
- [ ] Shows entry price, current price, unrealized P&L
- [ ] Eventually exits position
- [ ] Trade appears in history

**Trade executed?** YES / NO / WAITING

**If YES:**
- Entry Price: $________
- Exit Price: $________
- P&L: $________ (_______%)

**Result:** PASS / FAIL

---

### **Test 6: Stop Paper Trading**

**Steps:**
1. Click "⏸️ Stop Trading" button

**Expected:**
- [ ] Status changes to "⚪ STOPPED"
- [ ] Info message appears
- [ ] Start button re-enabled
- [ ] Stop button disabled

**Result:** PASS / FAIL

---

### **Test 7: CSV Export**

**Steps:**
1. If trades exist in history
2. Click "📥 Download CSV" button
3. Open downloaded file

**Expected:**
- [ ] CSV file downloads
- [ ] File opens in Excel/spreadsheet
- [ ] Contains trade data
- [ ] Columns: timestamp, action, price, pnl, etc.

**Number of trades in CSV:** _______

**Result:** PASS / FAIL

---

### **Test 8: PDF Report Generation**

**Steps:**
1. Click "📄 Generate PDF Report" button
2. Wait for generation
3. Click "📥 Download PDF"
4. Open PDF file

**Expected:**
- [ ] Success message appears
- [ ] PDF downloads
- [ ] PDF opens correctly
- [ ] Contains sections:
  - [ ] Title page
  - [ ] Executive summary
  - [ ] Performance metrics
  - [ ] Trade statistics
  - [ ] Strategy configuration
  - [ ] Trade history

**Result:** PASS / FAIL

---

### **Test 9: Reset Engine**

**Steps:**
1. Click "🔁 Reset Engine" once
2. See warning message
3. Click "🔁 Reset Engine" again to confirm

**Expected:**
- [ ] First click: Warning message
- [ ] Second click: Success message
- [ ] Capital resets to $10,000
- [ ] Trades cleared
- [ ] Total return = 0%

**Result:** PASS / FAIL

---

### **Test 10: Settings Panel**

**Steps:**
1. Expand "⚙️ Paper Trading Settings"
2. Check email settings
3. Adjust update interval slider

**Expected:**
- [ ] Settings panel expands
- [ ] Email checkbox works
- [ ] SMTP fields appear when enabled
- [ ] Update interval slider works
- [ ] Info messages display

**Result:** PASS / FAIL

---

## 🐛 Known Limitations

### **Expected Behavior:**

1. **Manual Updates Required**
   - Auto-refresh not implemented in this version
   - Must click "Manual Update" to fetch new prices
   - This is by design (Streamlit limitation)

2. **Trade Execution May Be Slow**
   - Depends on market conditions
   - May need 5-10 manual updates to see a trade
   - Only trades when Bull regime + 7/8 conditions

3. **No WebSocket Support**
   - Uses yfinance polling
   - Not true tick-by-tick data
   - Updates are hourly candles

4. **Email Not Tested**
   - Email functionality coded but not verified
   - Would need real SMTP credentials to test

---

## ✅ Success Criteria

**Phase 4 is successful if:**

- [ ] All 10 tests pass
- [ ] Paper trading tab loads
- [ ] Can start/stop trading
- [ ] Manual updates work
- [ ] Status displays correctly
- [ ] Can export CSV
- [ ] Can generate PDF report
- [ ] Reset works
- [ ] No critical errors

**Minimum Passing:** 8/10 tests pass

---

## 📊 Test Results Summary

**Test Results:**
- Test 1 (Access Tab): ___________
- Test 2 (Start Trading): ___________
- Test 3 (Manual Update): ___________
- Test 4 (Monitor Status): ___________
- Test 5 (Execute Trade): ___________
- Test 6 (Stop Trading): ___________
- Test 7 (CSV Export): ___________
- Test 8 (PDF Report): ___________
- Test 9 (Reset Engine): ___________
- Test 10 (Settings): ___________

**Total Passed:** ___ / 10

**Overall Status:** PASS / FAIL

---

## 📝 Issues Found

List any issues encountered:

1. ___________________________________
2. ___________________________________
3. ___________________________________

---

## 🎯 Next Steps

**If all tests pass:**
- Phase 4 complete! ✅
- Ready for Phase 5 (Testing & Deployment)

**If issues found:**
- Document issues
- Report to developer
- Await fixes

---

## 💡 Tips for Testing

1. **Be Patient**: Trade execution may take multiple updates
2. **Check Conditions**: Look at "Conditions Met" in Overview tab
3. **Monitor Regime**: Bull regime needed for entries
4. **Save Work**: Export CSV and PDF for records
5. **Reset Safely**: Use reset only when you're sure

---

## 📸 Screenshots to Capture

Please capture screenshots of:

1. Paper Trading tab (initial view)
2. Status display (with running state)
3. Position info (if trade entered)
4. Trade history table
5. PDF report (first page)
6. Any errors encountered

---

**Happy Testing!** 🚀

Report results back for evaluation.
