# Phase 1 Testing Guide

## Installation Status

### ✅ Successfully Installed Packages
- streamlit
- plotly  
- yfinance
- pandas
- numpy
- scikit-learn
- sqlalchemy
- bcrypt
- python-dotenv
- pytest
- pytest-cov
- colorlog
- python-dateutil
- pytz

### ⚠️ Known Issues

#### hmmlearn Installation Failed
**Issue**: `hmmlearn` requires C++ compilation which fails on Python 3.14 due to missing Windows SDK headers.

**Workarounds**:
1. **Use Python 3.11 or 3.12** (recommended for production)
2. **Install from conda**: `conda install -c conda-forge hmmlearn`
3. **Use pre-built wheel** (if available): Check https://www.lfd.uci.edu/~gohlke/pythonlibs/
4. **Install Windows SDK**: Install complete Visual Studio Build Tools with Windows 10 SDK

**For Testing Without hmmlearn**:
You can test the infrastructure components (data loading, database, logging) without hmmlearn. The HMM tests will be skipped.

---

## Phase 1 Testing Instructions

### Test 1: Verify Project Structure

```bash
cd C:/Traning/stock_analysis
ls -la
```

**Expected Output**: You should see all directories:
- `config/`
- `data/`
- `models/`
- `strategy/`
- `backtesting/`
- `paper_trading/`
- `ui/`
- `tests/`
- `utils/`
- `logs/`
- `requirements.txt`
- `README.md`

---

### Test 2: Import Core Modules

```bash
python -c "
from config import settings
from utils import logger
from data import db_manager
print('✓ All core modules imported successfully')
print(f'Database path: {settings.DATABASE_PATH}')
print(f'Asset symbol: {settings.ASSET_SYMBOL}')
"
```

**Expected Output**:
```
✓ All core modules imported successfully
Database path: C:\Traning\stock_analysis\data\trading_app.db
Asset symbol: BTC-USD
```

---

### Test 3: Database Initialization

```bash
python -c "
from data import db_manager
info = {
    'engine': db_manager.engine,
    'tables': db_manager.engine.table_names() if hasattr(db_manager.engine, 'table_names') else 'N/A'
}
print('✓ Database initialized')
print(f'Database engine: {db_manager.engine}')
print('Tables created: price_data, model_metadata, trades, strategy_configs')
"
```

**Expected Output**:
```
✓ Database initialized
Database engine: Engine(sqlite:///...)
Tables created: price_data, model_metadata, trades, strategy_configs
```

---

### Test 4: Data Loading (Critical Test)

```bash
python -c "
from data import DataLoader
from datetime import datetime, timedelta

print('Initializing DataLoader...')
loader = DataLoader(symbol='BTC-USD', interval='1h')

print('Fetching data (this may take 30-60 seconds)...')
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=7)

data = loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=True)

print(f'✓ Successfully fetched {len(data)} rows')
print(f'Date range: {data.index.min()} to {data.index.max()}')
print(f'Columns: {list(data.columns)}')
print(f'\\nLatest price:')
print(data.tail(1))

# Test caching
print('\\nTesting cache...')
data2 = loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=False)
print(f'✓ Loaded {len(data2)} rows from cache')

# Check data info
info = loader.get_data_info()
print(f'\\nDatabase info: {info}')
"
```

**Expected Output**:
```
Initializing DataLoader...
Fetching data (this may take 30-60 seconds)...
✓ Successfully fetched 168 rows
Date range: 2024-XX-XX to 2024-XX-XX
Columns: ['Open', 'High', 'Low', 'Close', 'Volume']

Latest price:
                     Open      High       Low     Close        Volume
2024-XX-XX XX:XX  XXXXX.XX  XXXXX.XX  XXXXX.XX  XXXXX.XX  XXXXX.XXXXXX

Testing cache...
✓ Loaded 168 rows from cache

Database info: {'total_rows': 168, 'earliest': ..., 'latest': ..., 'symbol': 'BTC-USD'}
```

---

### Test 5: Data Validation

```bash
python -c "
from data import DataLoader
from utils.validators import DataValidator
from datetime import datetime, timedelta

loader = DataLoader()
validator = DataValidator()

print('Fetching data...')
data = loader.fetch_data(force_refresh=False)

print('Validating data quality...')
is_valid, issues = validator.validate_price_data(data)

print(f'\\nValidation result: {'PASSED' if is_valid else 'FAILED'}')
if issues:
    print(f'Issues found: {len(issues)}')
    for i, issue in enumerate(issues, 1):
        print(f'  {i}. {issue}')
else:
    print('No issues found - data quality is excellent!')
"
```

**Expected Output**:
```
Fetching data...
Validating data quality...

Validation result: PASSED
No issues found - data quality is excellent!
```

---

### Test 6: HMM Engine (Requires hmmlearn)

**⚠️ Skip this test if hmmlearn is not installed**

```bash
python -c "
try:
    import hmmlearn
    print('hmmlearn is installed - proceeding with test')
except ImportError:
    print('⚠️  hmmlearn not installed - skipping HMM test')
    print('Install with: conda install -c conda-forge hmmlearn')
    exit(0)

from models import HMMEngine
from data import DataLoader
from datetime import datetime, timedelta

print('\\nFetching data...')
loader = DataLoader()
data = loader.fetch_data()

print(f'Training HMM on {len(data)} rows...')
engine = HMMEngine(n_states=7, n_iter=100, random_state=42)

success, error = engine.train(data)

if success:
    print('✓ Model trained successfully')
    print(f'Bull state: {engine.bull_state}')
    print(f'Bear state: {engine.bear_state}')
    print(f'State returns: {engine.state_returns}')
    
    # Predict current regime
    state, regime, confidence = engine.predict_current_regime(data)
    print(f'\\nCurrent market regime: {regime}')
    print(f'State: {state}, Confidence: {confidence:.2%}')
else:
    print(f'✗ Training failed: {error}')
"
```

**Expected Output (if hmmlearn installed)**:
```
hmmlearn is installed - proceeding with test

Fetching data...
Training HMM on XXX rows...
✓ Model trained successfully
Bull state: X
Bear state: X
State returns: [...]

Current market regime: Bull Run (or Bear/Crash or Neutral-X)
State: X, Confidence: XX.XX%
```

---

### Test 7: Model Persistence (Requires hmmlearn)

**⚠️ Skip this test if hmmlearn is not installed**

```bash
python -c "
try:
    import hmmlearn
except ImportError:
    print('⚠️  hmmlearn not installed - skipping model persistence test')
    exit(0)

from models import HMMEngine, ModelManager
from data import DataLoader

print('Training and saving model...')
loader = DataLoader()
data = loader.fetch_data()

engine = HMMEngine()
success, error = engine.train(data)

if not success:
    print(f'Training failed: {error}')
    exit(1)

manager = ModelManager()
success, model_path = manager.save_model(engine, version='test_v1')

if success:
    print(f'✓ Model saved to: {model_path}')
else:
    print('✗ Model save failed')
    exit(1)

# Load model
print('\\nLoading model...')
loaded_engine = manager.load_model()

if loaded_engine:
    print('✓ Model loaded successfully')
    print(f'Model has {loaded_engine.n_states} states')
    print(f'Bull state: {loaded_engine.bull_state}')
    print(f'Bear state: {loaded_engine.bear_state}')
    
    # Get model info
    info = manager.get_model_info()
    print(f'\\nModel info:')
    for key, value in info.items():
        print(f'  {key}: {value}')
else:
    print('✗ Model load failed')
"
```

---

### Test 8: Run Unit Tests

#### Test Data Loader Only (Works Without hmmlearn)

```bash
cd C:/Traning/stock_analysis
pytest tests/test_data_loader.py -v -s
```

**Expected Output**:
```
tests/test_data_loader.py::TestDataLoader::test_initialization PASSED
tests/test_data_loader.py::TestDataLoader::test_fetch_data_from_api PASSED
tests/test_data_loader.py::TestDataLoader::test_caching_mechanism PASSED
tests/test_data_loader.py::TestDataLoader::test_get_data_info PASSED
tests/test_data_loader.py::TestDataLoader::test_get_latest_data PASSED
tests/test_data_loader.py::TestDataLoader::test_data_validation PASSED

======================== 6 passed in XX.XXs ========================
```

#### Test HMM Engine (Requires hmmlearn)

```bash
pytest tests/test_hmm_engine.py -v -s
```

**Expected Output** (if hmmlearn installed):
```
tests/test_hmm_engine.py::TestHMMEngine::test_initialization PASSED
tests/test_hmm_engine.py::TestHMMEngine::test_prepare_features PASSED
tests/test_hmm_engine.py::TestHMMEngine::test_train_model PASSED
tests/test_hmm_engine.py::TestHMMEngine::test_predict PASSED
tests/test_hmm_engine.py::TestHMMEngine::test_predict_current_regime PASSED
tests/test_hmm_engine.py::TestHMMEngine::test_get_regime_info PASSED
tests/test_hmm_engine.py::TestHMMEngine::test_insufficient_data PASSED

======================== 7 passed in XX.XXs ========================
```

#### Run All Tests With Coverage

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## Verification Checklist

After running all tests, verify:

- [ ] **Project structure created** - All directories exist
- [ ] **Config module works** - Settings load correctly
- [ ] **Logging works** - Logs appear in console and `logs/app.log`
- [ ] **Database initialized** - `data/trading_app.db` file exists
- [ ] **Data fetching works** - BTC-USD data downloads successfully
- [ ] **Data caching works** - Second fetch is faster (from cache)
- [ ] **Data validation works** - Quality checks pass
- [ ] **HMM training works** (if hmmlearn installed) - Model trains successfully
- [ ] **Model persistence works** (if hmmlearn installed) - Save/load functions
- [ ] **Unit tests pass** - All applicable tests green

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'X'"
**Solution**: Install missing package: `pip install X`

### Issue: "yfinance returns empty data"
**Solution**: 
- Check internet connection
- Try different date range
- Verify BTC-USD symbol is correct
- Check yfinance API status

### Issue: "Database is locked"
**Solution**: Close all Python processes and try again

### Issue: "hmmlearn won't install"
**Solutions**:
1. Use Python 3.11 or 3.12 instead of 3.14
2. Try conda: `conda install -c conda-forge hmmlearn`
3. Skip HMM tests for now - infrastructure tests still valid

### Issue: "Tests are slow"
**Cause**: First run fetches data from API (30-60 seconds)
**Solution**: Subsequent runs use cache and are much faster

---

## Next Steps After Phase 1 Verification

Once all tests pass:
1. ✅ **Confirm with me that Phase 1 works**
2. 🚀 **Proceed to Phase 2**: Technical indicators and strategy logic
3. 📊 **Phase 3**: Streamlit UI development
4. 📈 **Phase 4**: Paper trading and export features
5. 🚢 **Phase 5**: Testing and deployment

---

## Quick Start Testing (Minimal)

If you want to do a quick sanity check:

```bash
cd C:/Traning/stock_analysis

# Test imports
python -c "from config import settings; from utils import logger; from data import DataLoader; print('✓ Imports work')"

# Test data loading (30-60 seconds)
python -c "from data import DataLoader; d = DataLoader().fetch_data(); print(f'✓ Fetched {len(d)} rows')"

# Test database
python -c "from data import db_manager; print(f'✓ Database at {db_manager.engine.url}')"

echo "Phase 1 core functionality verified!"
```

**Expected output**:
```
✓ Imports work
✓ Fetched XXX rows
✓ Database at sqlite:///...
Phase 1 core functionality verified!
```

---

**Document Version**: 1.0  
**Phase**: 1 - Core Infrastructure  
**Status**: Ready for Testing
