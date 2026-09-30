# Regime-Based Trading Application - Final Requirements

## Executive Summary
Build a professional, production-ready regime-based trading application for BTC-USD using Python, Streamlit, Plotly, and yfinance. The system will use Hidden Markov Models (HMM) to identify market regimes and execute trades based on a multi-condition voting system with robust risk management.

---

## 1. Core Engine (HMM Logic)

### 1.1 Model Configuration
- **Algorithm**: `hmmlearn.GaussianHMM` with 7 state components
- **Asset**: BTC-USD only (initially)
- **Training Features**:
  - Returns
  - Range (calculated as `(High - Low) / Close`)
  - Volume Volatility

### 1.2 Regime Identification
- **Automatic State Classification**:
  - **Bull Run State**: Regime with the highest positive mean returns
  - **Bear/Crash State**: Regime with the lowest mean returns
  - **Neutral States**: All other regimes (5 states)

### 1.3 Model Training & Persistence
- **Training Schedule**: Weekly automatic retraining
- **Model Persistence**: 
  - Save trained models to disk (pickle format)
  - Load existing models on app startup
  - Store model metadata (training date, performance metrics)
- **Convergence Handling**:
  - Retry training with different random seeds (max 3 attempts)
  - Fall back to last successfully trained model
  - Log warnings and notify user via UI

---

## 2. Data Management

### 2.1 Data Source
- **Provider**: yfinance API
- **Asset**: BTC-USD
- **Timeframe**: Hourly data
- **Historical Range**: Last 730 days (2 years)
- **Real-time Updates**: Fetch latest data on user request or scheduled intervals

### 2.2 Data Storage (SQLite)
- **Database Schema**:
  ```
  Table: price_data
  - id (PRIMARY KEY)
  - timestamp (DATETIME, INDEXED)
  - open (REAL)
  - high (REAL)
  - low (REAL)
  - close (REAL)
  - volume (REAL)
  - created_at (DATETIME)
  
  Table: model_metadata
  - id (PRIMARY KEY)
  - model_version (TEXT)
  - training_date (DATETIME)
  - n_states (INTEGER)
  - convergence_score (REAL)
  - model_path (TEXT)
  
  Table: trades
  - id (PRIMARY KEY)
  - timestamp (DATETIME)
  - action (TEXT) -- 'BUY' or 'SELL'
  - price (REAL)
  - quantity (REAL)
  - pnl (REAL)
  - regime (TEXT)
  - conditions_met (INTEGER)
  
  Table: strategy_configs
  - id (PRIMARY KEY)
  - config_name (TEXT, UNIQUE)
  - config_json (TEXT)
  - created_at (DATETIME)
  - is_active (BOOLEAN)
  ```

### 2.3 Data Quality & Validation
- **Missing Data Handling**:
  - Forward-fill gaps < 3 hours
  - Flag and alert for gaps > 3 hours
  - Prevent model training on incomplete data
- **Outlier Detection**:
  - Flag returns > 20% in 1 hour
  - Validate volume spikes (> 10x average)

---

## 3. Trading Strategy Logic

### 3.1 Entry Conditions (8-Point Voting System)
Trade entry requires:
1. **HMM identifies current regime as "Bull Run"**, AND
2. **At least 7 out of 8 conditions are met**:
   - RSI < 90
   - Momentum > 1%
   - Volatility < 6%
   - Volume > 20-period SMA
   - ADX > 25
   - Price > 50 EMA
   - Price > 200 EMA
   - MACD > Signal Line

### 3.2 Exit Conditions
- **Immediate Exit Triggers**:
  - Market regime switches to "Bear" or "Crash"
  - Stop-loss threshold reached (configurable, default -5%)
  - Take-profit threshold reached (configurable, default +15%)

### 3.3 Risk Management

#### 3.3.1 Cooldown Period
- **Duration**: 48 hours (configurable)
- **Trigger**: Any position close (win or loss)
- **Purpose**: Prevent overtrading and whipsaw losses
- **Implementation**: Track last exit timestamp, block new entries

#### 3.3.2 Position Sizing
- **Leverage**: 2.5x (simulated for backtesting)
- **Max Position Size**: 95% of available capital (5% cash buffer)
- **Fractional Shares**: Supported

#### 3.3.3 Portfolio Protection
- **Max Drawdown Alert**: Notify when drawdown > 20%
- **Daily Loss Limit**: Optional circuit breaker (configurable)

---

## 4. System Architecture

### 4.1 Project Structure
```
HMM_analysis/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Global configuration
│   └── default_strategies.json
├── data/
│   ├── __init__.py
│   ├── data_loader.py       # yfinance integration
│   ├── database.py          # SQLite ORM
│   └── cache_manager.py     # Data caching logic
├── models/
│   ├── __init__.py
│   ├── hmm_engine.py        # HMM training & prediction
│   ├── model_manager.py     # Model persistence
│   └── saved_models/        # Stored model files
├── strategy/
│   ├── __init__.py
│   ├── indicators.py        # Technical indicators
│   ├── regime_detector.py   # Regime classification
│   ├── signal_generator.py  # Entry/exit logic
│   └── risk_manager.py      # Risk controls
├── backtesting/
│   ├── __init__.py
│   ├── backtester.py        # Core backtest engine
│   └── performance.py       # Metrics calculation
├── paper_trading/
│   ├── __init__.py
│   └── paper_trader.py      # Live paper trading
├── ui/
│   ├── __init__.py
│   ├── app.py               # Main Streamlit app
│   ├── components/
│   │   ├── __init__.py
│   │   ├── charts.py        # Plotly visualizations
│   │   ├── metrics.py       # Performance displays
│   │   └── config_panel.py  # Parameter controls
│   └── auth.py              # User authentication
├── tests/
│   ├── __init__.py
│   ├── test_hmm_engine.py
│   ├── test_indicators.py
│   ├── test_backtester.py
│   └── test_data_loader.py
├── utils/
│   ├── __init__.py
│   ├── logger.py            # Logging configuration
│   ├── validators.py        # Data validation
│   └── export.py            # Export functionality
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── requirement_final.md
```

### 4.2 Core Components

#### 4.2.1 data_loader.py
- Fetch hourly BTC-USD data from yfinance
- Cache to SQLite database
- Provide data retrieval API with date range filtering
- Handle API rate limits and failures gracefully

#### 4.2.2 hmm_engine.py
- Train GaussianHMM with 7 states
- Calculate training features (returns, range, volume volatility)
- Identify Bull/Bear regimes automatically
- Predict current market regime

#### 4.2.3 backtester.py
- Simulate trading with configurable initial capital (default $10,000)
- Execute entry/exit logic with 48-hour cooldown
- Calculate leveraged PnL (2.5x)
- Log all trades to database
- Generate performance metrics

#### 4.2.4 paper_trader.py (NEW)
- Real-time paper trading mode
- Fetch latest data every 1 hour
- Execute signals without real money
- Track simulated portfolio value
- Alert on trade executions

#### 4.2.5 app.py (Streamlit Dashboard)
- User authentication (username/password)
- Multi-page layout:
  - **Home**: Current signal and regime
  - **Backtest**: Run historical simulations
  - **Paper Trading**: Live simulation mode
  - **Configuration**: Parameter tuning
  - **Analysis**: Performance metrics and charts

---

## 5. User Interface (Streamlit)

### 5.1 Authentication
- **Login Screen**: Username and password (hashed storage)
- **Session Management**: Maintain user state
- **Deployment**: Use Streamlit secrets for credentials on Streamlit Cloud

### 5.2 Dashboard Layout

#### 5.2.1 Header Section
- **Current Signal**: Display "LONG" (green) or "CASH" (gray)
- **Current Regime**: Display identified regime with confidence score
- **Last Update**: Timestamp of latest data
- **Account Value**: Current portfolio value (backtest or paper trading)

#### 5.2.2 Chart Section (Plotly Interactive)
- **Candlestick Chart**: BTC-USD price action
- **Dynamic Background Colors**:
  - Green tint: Bull Run regime
  - Red tint: Bear/Crash regime
  - Gray tint: Neutral regimes
- **Overlays**:
  - 50 EMA (blue line)
  - 200 EMA (orange line)
  - Buy/Sell markers
  - Regime change indicators
- **Zoom & Pan**: Fully interactive
- **Tooltips**: Show all condition values on hover

#### 5.2.3 Metrics Section
Display key performance indicators:
- **Total Return**: Percentage gain/loss
- **Alpha vs Buy & Hold**: Excess return over passive strategy
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Worst peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return
- **Number of Trades**: Total executed
- **Average Hold Time**: Mean position duration
- **Profit Factor**: Gross profit / Gross loss

#### 5.2.4 Configuration Panel (Sidebar)
**Strategy Parameters** (editable):
- RSI Threshold (default: 90)
- Momentum Threshold (default: 1%)
- Volatility Threshold (default: 6%)
- ADX Threshold (default: 25)
- Required Conditions (default: 7 out of 8)
- Cooldown Hours (default: 48)
- Leverage (default: 2.5x)
- Stop Loss % (default: -5%)
- Take Profit % (default: +15%)

**Backtest Settings**:
- Date Range Selector (start/end dates)
- Initial Capital (default: $10,000)
- Commission Rate (default: 0.1%)

**Actions**:
- "Save Configuration" button → Store to database
- "Load Configuration" dropdown → Select saved configs
- "Export Results" button → Download CSV/PDF

### 5.3 Export Functionality
- **CSV Export**: Trade log with all details
- **Chart Export**: Save Plotly charts as PNG/HTML
- **PDF Report**: Summary with metrics and chart
- **JSON Config**: Export current parameter settings

---

## 6. Testing & Validation

### 6.1 Unit Tests (pytest)
Required test coverage:
- `test_hmm_engine.py`: Model training, regime detection
- `test_indicators.py`: All technical indicator calculations
- `test_backtester.py`: Entry/exit logic, PnL calculation
- `test_data_loader.py`: Data fetching, caching, validation
- `test_risk_manager.py`: Cooldown, position sizing

**Target Coverage**: Minimum 80% code coverage

### 6.2 Data Validation
- Schema validation for all database writes
- Range checks for price data (no negative values)
- Timestamp continuity checks
- Feature calculation validation (no NaN/Inf values)

### 6.3 Logging Strategy
**Logging Levels** (configurable):
- **DEBUG**: All function calls, data transformations
- **INFO**: Trade executions, model training, data updates
- **WARNING**: Failed API calls, missing data, convergence issues
- **ERROR**: Database errors, model failures, critical exceptions

**Log Outputs**:
- Console (during development)
- File: `logs/app_{date}.log` (rotating daily, keep 30 days)
- UI: Real-time log viewer in Streamlit (optional tab)

---

## 7. Deployment (Streamlit Cloud)

### 7.1 Deployment Checklist
- [ ] Create `requirements.txt` with pinned versions
- [ ] Configure Streamlit secrets (database path, auth credentials)
- [ ] Set up GitHub repository with proper `.gitignore`
- [ ] Configure scheduled model retraining (GitHub Actions or external cron)
- [ ] Set environment variables for production
- [ ] Enable HTTPS and secure authentication

### 7.2 Environment Variables
```
# .env.example
DATABASE_PATH=./data/trading_app.db
LOG_LEVEL=INFO
MODEL_RETRAIN_SCHEDULE=weekly
YFINANCE_TIMEOUT=30
MAX_API_RETRIES=3
```

### 7.3 Secrets Management (Streamlit Cloud)
```toml
# .streamlit/secrets.toml (DO NOT COMMIT)
[auth]
admin_username = "admin"
admin_password = "$2b$12$..." # bcrypt hash

[database]
path = "/mount/data/trading_app.db"
```

---

## 8. Performance & Optimization

### 8.1 Caching Strategy
- **Streamlit Cache**: 
  - `@st.cache_data` for data loading
  - `@st.cache_resource` for model loading
  - TTL: 1 hour for price data, 7 days for models
- **Database Indexing**: 
  - Index on `timestamp` columns
  - Optimize queries with EXPLAIN

### 8.2 API Rate Limiting
- **yfinance**: Max 2000 requests/hour
- **Mitigation**: Cache aggressively, use batch downloads
- **Fallback**: Display "API limit reached" message with retry time

---

## 9. Error Handling & Reliability

### 9.1 Graceful Degradation
- **No Internet**: Display cached data with warning
- **Model Training Fails**: Use last successful model
- **Missing Data**: Show "Insufficient data" message, disable trading

### 9.2 User Notifications
- **Success Messages**: "Backtest completed successfully"
- **Warnings**: "Model convergence low, results may be unreliable"
- **Errors**: "Failed to fetch data. Retry in 5 minutes."

---

## 10. Future Enhancements (Out of Scope - V1)
- Multi-asset support (ETH-USD, stocks)
- Machine learning hyperparameter optimization
- Telegram/Email trade alerts
- Live trading integration with exchange APIs
- Advanced portfolio analytics (factor analysis)
- Multi-strategy ensemble

---

## 11. Success Criteria

### 11.1 Functional Requirements ✓
- [x] HMM correctly identifies 7 regimes
- [x] 8-condition voting system enforced
- [x] 48-hour cooldown implemented
- [x] Backtest produces accurate PnL
- [x] Paper trading runs in real-time
- [x] UI displays all required metrics
- [x] Authentication protects access
- [x] Export functionality works for all formats

### 11.2 Non-Functional Requirements ✓
- [x] App loads in < 5 seconds
- [x] Chart renders 730 days of data smoothly
- [x] Database queries execute in < 1 second
- [x] Model training completes in < 2 minutes
- [x] Unit tests pass with > 80% coverage
- [x] No crashes during 24-hour stress test
- [x] Mobile-responsive UI (tablet and above)

---

## 12. Development Phases

### Phase 1: Core Infrastructure (Week 1-2)
- Set up project structure
- Implement data_loader.py with SQLite caching
- Build hmm_engine.py with model persistence
- Create basic unit tests

### Phase 2: Strategy & Backtesting (Week 3-4)
- Implement all technical indicators
- Build signal_generator.py with 8-condition logic
- Create backtester.py with risk management
- Add trade logging to database

### Phase 3: UI Development (Week 5-6)
- Build Streamlit app.py with authentication
- Create interactive Plotly charts
- Implement configuration panel
- Add metrics dashboard

### Phase 4: Paper Trading & Export (Week 7)
- Build paper_trader.py for live simulation
- Implement CSV/PDF export functionality
- Add real-time data updates

### Phase 5: Testing & Deployment (Week 8)
- Complete unit test suite
- Perform integration testing
- Deploy to Streamlit Cloud
- User acceptance testing

---

## 13. Documentation Requirements

### 13.1 Code Documentation
- Docstrings for all functions (Google style)
- Type hints for function signatures
- Inline comments for complex logic

### 13.2 User Documentation
- **README.md**: Installation, quick start, architecture overview
- **USER_GUIDE.md**: How to use the dashboard, interpret metrics
- **API_REFERENCE.md**: Function documentation for developers

### 13.3 Deployment Documentation
- **DEPLOYMENT.md**: Step-by-step Streamlit Cloud setup
- **TROUBLESHOOTING.md**: Common issues and solutions

---

## Appendix A: Technology Stack

### Core Libraries
- **Python**: 3.10+
- **Streamlit**: 1.28+
- **Plotly**: 5.17+
- **yfinance**: 0.2.28+
- **hmmlearn**: 0.3.0+
- **pandas**: 2.0+
- **numpy**: 1.24+
- **SQLite**: 3.x (built-in)
- **scikit-learn**: 1.3+ (for additional metrics)
- **ta-lib** or **pandas-ta**: Technical indicators

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest-cov**: Coverage reporting

### Deployment
- **Streamlit Cloud**: Hosting platform
- **GitHub**: Version control and CI/CD
- **bcrypt**: Password hashing

---

## Appendix B: Risk Disclaimers

**Important**: This application is for educational and research purposes only. It does not constitute financial advice. Cryptocurrency trading carries substantial risk of loss. Past performance does not guarantee future results. Users should:
- Never invest more than they can afford to lose
- Understand that leveraged trading amplifies both gains and losses
- Consult a financial advisor before making investment decisions
- Test thoroughly in paper trading mode before considering live trading

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Author**: Trading Application Development Team  
**Status**: Approved for Development
