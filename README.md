# HMM Trading Application

Regime-based trading application using Hidden Markov Models for BTC-USD cryptocurrency trading.

## Features

- **7-State HMM**: Identifies market regimes (Bull, Bear, Neutral states)
- **Multi-Condition Strategy**: 8-point voting system for trade entries
- **Risk Management**: 48-hour cooldown, leveraged positions, stop-loss/take-profit
- **Data Caching**: SQLite database for efficient data management
- **Model Persistence**: Save and load trained models
- **Real-time Updates**: Fetch latest data from yfinance
- **Paper Trading**: Simulate trades without risk
- **Interactive Dashboard**: Streamlit-based UI with Plotly charts

## Project Structure

```
stock_analysis/
├── config/           # Configuration settings
├── data/             # Data loading and database management
├── models/           # HMM engine and model persistence
├── strategy/         # Trading strategy logic (Phase 2)
├── backtesting/      # Backtesting engine (Phase 2)
├── paper_trading/    # Paper trading mode (Phase 4)
├── ui/               # Streamlit dashboard (Phase 3)
├── tests/            # Unit tests
├── utils/            # Utilities (logging, validation)
└── logs/             # Application logs
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. Clone or navigate to the project directory:
```bash
cd stock_analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python -c "import streamlit; import pandas; import yfinance; print('✓ All packages installed')"
```

## Usage

### Phase 1: Core Infrastructure (Current)

#### Test Data Loading
```bash
# Test data loader
pytest tests/test_data_loader.py -v

# Or run manually
python -c "
from data import DataLoader
loader = DataLoader()
data = loader.fetch_data()
print(f'Loaded {len(data)} rows')
print(data.head())
"
```

#### Test HMM Engine
```bash
# Run HMM tests
pytest tests/test_hmm_engine.py -v

# Or train a model manually
python -c "
from data import DataLoader
from models import HMMEngine
loader = DataLoader()
data = loader.fetch_data()
engine = HMMEngine()
success, error = engine.train(data)
if success:
    state, regime, conf = engine.predict_current_regime(data)
    print(f'Current Regime: {regime} (confidence: {conf:.2%})')
"
```

#### Test Model Persistence
```bash
python -c "
from data import DataLoader
from models import HMMEngine, ModelManager
# Train model
loader = DataLoader()
data = loader.fetch_data()
engine = HMMEngine()
engine.train(data)
# Save model
manager = ModelManager()
manager.save_model(engine)
print('✓ Model saved')
# Load model
loaded_engine = manager.load_model()
print('✓ Model loaded')
print(f'Model info: {manager.get_model_info()}')
"
```

### Run All Tests
```bash
# Run all unit tests with coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_data_loader.py -v -s

# Run with verbose output
pytest tests/ -v -s
```

## Configuration

Edit `config/settings.py` to customize:

- **Data Settings**: Symbol, interval, lookback period
- **HMM Parameters**: Number of states, iterations, convergence thresholds
- **Strategy Parameters**: RSI/MACD thresholds, cooldown period, leverage
- **Risk Management**: Stop-loss, take-profit, position sizing
- **Logging**: Log levels, file rotation

## Database

SQLite database is automatically created at `data/trading_app.db`

Tables:
- `price_data`: Cached OHLCV data
- `model_metadata`: Model training history
- `trades`: Trade execution log
- `strategy_configs`: Saved strategy configurations

## Logging

Logs are written to:
- Console: Colored output (if colorlog installed)
- File: `logs/app.log` (rotated daily, 30-day retention)

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Development Status

### ✅ Phase 1: Core Infrastructure (COMPLETE)
- [x] Project structure
- [x] Configuration management
- [x] Data loading with yfinance
- [x] SQLite caching
- [x] HMM engine implementation
- [x] Model persistence
- [x] Logging system
- [x] Data validation
- [x] Unit tests

### 🚧 Phase 2: Strategy & Backtesting (Next)
- [ ] Technical indicators (RSI, MACD, ADX, etc.)
- [ ] Signal generation with 8-condition voting
- [ ] Risk management rules
- [ ] Backtesting engine
- [ ] Trade logging

### 🚧 Phase 3: UI Development
- [ ] Streamlit dashboard
- [ ] Interactive Plotly charts
- [ ] Configuration panel
- [ ] Metrics display

### 🚧 Phase 4: Paper Trading & Export
- [ ] Real-time paper trading
- [ ] Export functionality (CSV, PDF)
- [ ] Trade notifications

### 🚧 Phase 5: Testing & Deployment
- [ ] Integration tests
- [ ] Streamlit Cloud deployment
- [ ] User authentication
- [ ] Documentation

## Troubleshooting

### Import Errors
If you get import errors, ensure you're in the correct directory:
```bash
cd stock_analysis
python -c "import sys; print(sys.path)"
```

### Data Fetch Issues
If yfinance fails to fetch data:
- Check internet connection
- Verify BTC-USD symbol is correct
- Check yfinance rate limits
- Try force_refresh=True

### Model Training Issues
If HMM fails to converge:
- Ensure sufficient data (60+ days recommended)
- Check for data quality issues
- Try different random seeds
- Adjust n_iter parameter

## Contributing

This is an educational project. Key development principles:
- Write tests before implementing features
- Follow PEP 8 style guidelines
- Document all functions with docstrings
- Log important events and errors
- Validate all inputs

## License

Educational use only. Not financial advice.

## Contact

For questions or issues, refer to `requirement_final.md` for full specifications.

---

**Current Version**: Phase 1 Complete
**Last Updated**: 2024
