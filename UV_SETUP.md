# UV Setup Script - Install Python 3.12 and All Dependencies

## Step 1: Create Project with Python 3.12

```bash
cd C:\Traning\stock_analysis

# Use UV to create environment with Python 3.12
uv venv --python 3.12
```

## Step 2: Activate Environment

```bash
# Windows
.venv\Scripts\activate
```

## Step 3: Install Dependencies with UV

```bash
# Install all packages (UV is much faster than pip!)
uv pip install streamlit plotly yfinance pandas numpy scikit-learn
uv pip install sqlalchemy bcrypt python-dotenv
uv pip install pytest pytest-cov colorlog python-dateutil pytz
uv pip install hmmlearn
```

## Step 4: Run Dashboard

```bash
streamlit run app.py
```

## All Features Will Work!
- ✅ Data loading
- ✅ HMM model training
- ✅ Backtesting
- ✅ Regime detection
- ✅ Full functionality!
