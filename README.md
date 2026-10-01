# 📈 HMM Trading Dashboard

A professional-grade trading system using Hidden Markov Models for regime detection and multi-condition signal generation.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

---

## 🎯 Overview

The HMM Trading Dashboard is a complete trading system that combines machine learning, technical analysis, and risk management to identify profitable trading opportunities in cryptocurrency markets.

**Key Features:**
- 🤖 Hidden Markov Model (HMM) regime detection
- 📊 8-condition voting system for entries
- 📈 Complete backtesting engine
- 📡 Real-time paper trading simulation
- 📄 Professional PDF reports
- 📥 CSV export capabilities
- ⚙️ Configurable parameters
- 🎨 Interactive Streamlit dashboard

---

## 🚀 Quick Start

### **Prerequisites**

- Python 3.12
- UV package manager (recommended) or pip
- Internet connection (for data fetching)

### **Installation**

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/hmm-trading-dashboard.git
cd hmm-trading-dashboard

# Setup with UV (recommended)
setup_with_uv.bat

# Or manual setup
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
pip install hmmlearn
```

### **Running the Dashboard**

```bash
# Windows
run_dashboard.bat

# Or manual
streamlit run app.py
```

Dashboard opens at: http://localhost:8502

---

## 📊 Features

### **1. HMM Regime Detection**

- **7-state model** identifies market conditions
- Automatic Bull/Bear/Neutral classification
- Confidence scoring for each regime
- Trained on returns, range, and volume patterns

### **2. Multi-Condition Signal System**

Requires **7 out of 8 conditions** for entry:

1. ✅ RSI < 90 (not overbought)
2. ✅ Momentum > 1% (upward trend)
3. ✅ Volatility < 6% (stable market)
4. ✅ Volume > 20-SMA (high liquidity)
5. ✅ ADX > 25 (strong trend)
6. ✅ Price > 50 EMA (short-term bullish)
7. ✅ Price > 200 EMA (long-term bullish)
8. ✅ MACD > Signal (momentum confirmation)

### **3. Risk Management**

- **Stop-loss:** -5% automatic exit
- **Take-profit:** +15% automatic exit
- **Cooldown:** 48-hour wait after exit
- **Leverage:** 2.5x position sizing
- **Commission:** 0.1% per trade

### **4. Backtesting Engine**

- Test on historical data
- Comprehensive performance metrics
- Trade-by-trade analysis
- Interactive visualizations
- Compare vs buy & hold

### **5. Paper Trading**

- Real-time simulation
- Live price updates
- Position tracking
- Trade journal
- No real money risk

### **6. Export & Reporting**

- **CSV:** Trade history export
- **PDF:** Professional reports
- **JSON:** Configuration backup
- Excel-compatible formats

---

## 📸 Screenshots

### **Overview Tab**
- Current signal and market regime
- Interactive price charts
- Real-time indicators

### **Backtest Results**
- Performance metrics dashboard
- Portfolio value over time
- Trade history table

### **Paper Trading**
- Live trading simulation
- Position monitoring
- Real-time P&L tracking

### **Configuration**
- Adjustable parameters
- Strategy customization
- Import/export settings

---

## 📖 Documentation

Comprehensive documentation available in `docs/` folder:

- **[USER_MANUAL.md](docs/USER_MANUAL.md)** - Complete user guide
- **[DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Deployment instructions
- **[PHASE4_SUMMARY.md](docs/PHASE4_SUMMARY.md)** - Phase 4 features
- **[PHASE4_TESTING.md](docs/PHASE4_TESTING.md)** - Testing guide

---

## 🛠️ Technology Stack

**Backend:**
- Python 3.12
- Pandas (data manipulation)
- NumPy (numerical computing)
- scikit-learn (machine learning utilities)
- hmmlearn (Hidden Markov Models)

**Frontend:**
- Streamlit (web framework)
- Plotly (interactive charts)

**Data:**
- yfinance (market data)
- SQLAlchemy (database)
- SQLite (local storage)

**Utilities:**
- ReportLab (PDF generation)
- python-dateutil (date handling)
- colorlog (logging)

---

## 📊 Project Structure

```
hmm-trading-dashboard/
├── app.py                      # Main Streamlit application
├── config/
│   └── settings.py             # Configuration constants
├── data/
│   ├── __init__.py
│   ├── data_loader.py          # Data fetching and caching
│   └── database.py             # Database management
├── models/
│   ├── __init__.py
│   └── hmm_engine.py           # HMM model training & prediction
├── strategy/
│   ├── __init__.py
│   ├── indicators.py           # Technical indicators
│   ├── signal_generator.py    # Signal generation
│   └── risk_manager.py         # Risk management
├── backtesting/
│   ├── __init__.py
│   ├── backtester.py           # Backtesting engine
│   └── performance.py          # Performance metrics
├── paper_trading/
│   ├── __init__.py             # Paper trading engine
│   ├── live_feed.py            # Live price feed
│   ├── notifications.py        # Notifications & journal
│   └── reports.py              # PDF report generation
├── ui/
│   ├── components/
│   │   ├── charts.py           # Chart components
│   │   └── metrics.py          # Metric displays
│   └── pages/
│       └── paper_trading.py    # Paper trading page
├── utils/
│   ├── logger.py               # Logging utilities
│   ├── validators.py           # Data validation
│   ├── performance.py          # Performance optimization
│   └── config.py               # Environment configuration
├── docs/                        # Documentation
├── tests/                       # Test files
├── .streamlit/
│   └── config.toml             # Streamlit configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🎯 Usage

### **Basic Workflow**

1. **Load Data**
   ```
   Sidebar → Set Lookback Days → Click "Refresh Data"
   ```

2. **Train Model**
   ```
   Sidebar → Set HMM States → Click "Train Model"
   ```

3. **Run Backtest**
   ```
   Sidebar → Click "Run Backtest" → View Results
   ```

4. **Paper Trade** (Optional)
   ```
   Paper Trading Tab → Start Trading → Manual Updates
   ```

5. **Export Results**
   ```
   Download CSV or Generate PDF Report
   ```

### **Configuration**

Adjust parameters in Configuration tab:
- Entry conditions thresholds
- Stop-loss and take-profit levels
- Leverage and cooldown period
- Required conditions (7/8 default)

### **Optimization**

1. Run backtest with default settings
2. Analyze results
3. Adjust parameters
4. Re-run backtest
5. Compare results
6. Iterate until satisfied

---

## 📈 Performance Metrics

### **Key Metrics Explained**

**Total Return:** Overall profit/loss percentage

**Alpha:** Excess return vs buy & hold strategy

**Sharpe Ratio:** Risk-adjusted returns (higher is better)

**Max Drawdown:** Largest peak-to-trough decline

**Win Rate:** Percentage of profitable trades

**Profit Factor:** Total wins ÷ Total losses

### **Interpreting Results**

**Good Performance:**
- Total Return > 0%
- Alpha > 0% (beat buy & hold)
- Win Rate > 50%
- Sharpe Ratio > 1.0
- Max Drawdown < 15%

**Needs Optimization:**
- Negative returns
- Low win rate (< 40%)
- High drawdown (> 20%)
- Low Sharpe ratio (< 0.5)

---

## 🚀 Deployment

### **Streamlit Cloud (Recommended)**

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Deploy!

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for details.

### **Self-Hosted**

```bash
# Clone and setup
git clone <repo>
cd hmm-trading-dashboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
streamlit run app.py --server.port 8501
```

### **Docker**

```bash
# Build
docker build -t hmm-dashboard .

# Run
docker run -p 8501:8501 hmm-dashboard
```

---

## 🔒 Security

**Important Notes:**
- Never commit `.env` or `secrets.toml` files
- Use environment variables for sensitive data
- Enable HTTPS in production
- Regular backups of database
- Keep dependencies updated

---

## 🐛 Troubleshooting

### **Common Issues**

**Issue:** hmmlearn not installing  
**Solution:** Use Python 3.12 (not 3.14)

**Issue:** No trades in backtest  
**Solution:** Lower required conditions to 6/8

**Issue:** Dashboard slow  
**Solution:** Reduce lookback days or enable caching

See [USER_MANUAL.md](docs/USER_MANUAL.md) for more troubleshooting.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## ⚠️ Disclaimer

**Educational Purpose Only**

This software is for educational and research purposes only. It is NOT financial advice.

**Important:**
- ❌ Not a recommendation to buy or sell
- ❌ No guarantee of profits
- ❌ Past performance ≠ future results
- ❌ Cryptocurrency trading carries substantial risk
- ❌ Only invest what you can afford to lose

**Use at your own risk.** The authors are not responsible for any financial losses.

---

## 🙏 Acknowledgments

**Technologies:**
- Streamlit for the amazing web framework
- yfinance for market data
- hmmlearn for HMM implementation
- Plotly for interactive charts

**Inspiration:**
- Quantitative trading research
- Machine learning in finance
- Open source trading tools

---

## 📞 Support

**Documentation:** See `docs/` folder  
**Issues:** Report on GitHub Issues  
**Questions:** Check USER_MANUAL.md FAQ section

---

## 🗺️ Roadmap

**Completed (Phase 1-4):**
- ✅ Core infrastructure
- ✅ HMM model implementation
- ✅ Backtesting engine
- ✅ Interactive dashboard
- ✅ Paper trading
- ✅ Export features

**Phase 5 (Current):**
- ✅ Deployment configuration
- ✅ Performance optimization
- ✅ Documentation
- ⏳ Production hardening

**Future Enhancements:**
- Multi-asset support
- Real-time WebSocket feeds
- Advanced optimization algorithms
- Mobile app
- Social features
- Cloud database integration

---

## 📊 Stats

- **Lines of Code:** ~10,000+
- **Files:** 30+
- **Documentation:** 8 comprehensive guides
- **Dependencies:** 15+ packages
- **Development Time:** 5 phases
- **Status:** Production-ready ✅

---

## 🎉 Getting Started

Ready to use the dashboard?

```bash
# Quick start
git clone <repo>
cd hmm-trading-dashboard
setup_with_uv.bat
run_dashboard.bat
```

**That's it!** Dashboard opens automatically.

---

**Built with ❤️ for the trading community**

*Happy Trading!* 📈🚀
"# Deployment fix" 
