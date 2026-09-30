"""
Test 4: Complete Backtest Simulation

This test runs a full backtest with real data and HMM model.

WARNING: This test requires hmmlearn to be installed.
If hmmlearn is not installed, this test will be skipped.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

print("="*60)
print("TEST 4: COMPLETE BACKTEST")
print("="*60)

# Check if hmmlearn is installed
try:
    import hmmlearn
    print('\n[OK] hmmlearn is installed - proceeding with test')
except ImportError:
    print('\n[WARNING] hmmlearn not installed - skipping backtest test')
    print('Install with: conda install -c conda-forge hmmlearn')
    print('\nYou can still run Tests 1-3 and 5 without hmmlearn.')
    exit(0)

from data import DataLoader
from models import HMMEngine
from backtesting import Backtester
from strategy import add_all_indicators

print('\n[1/5] Loading data...')
loader = DataLoader()
data = loader.fetch_data()
print(f'  Loaded {len(data)} rows')

print('\n[2/5] Training HMM model...')
engine = HMMEngine()
success, error = engine.train(data)
if not success:
    print(f'  [ERROR] {error}')
    exit(1)
print(f'  [OK] Model trained successfully')
print(f'  Bull state: {engine.bull_state}, Bear state: {engine.bear_state}')

print('\n[3/5] Adding indicators...')
data = add_all_indicators(data)
print(f'  [OK] Added indicators to {len(data)} rows')

print('\n[4/5] Running backtest...')
backtester = Backtester(initial_capital=10000.0)
regime_states = engine.predict(data)
metrics = backtester.run(data, regime_states, engine.bull_state, engine.bear_state)
print(f'  [OK] Backtest complete: {len(backtester.trades)} trade actions')

print('\n[5/5] Results:')
print("-" * 60)
print(f'  Initial Capital:     ${metrics["initial_capital"]:>12,.2f}')
print(f'  Final Capital:       ${metrics["final_capital"]:>12,.2f}')
print(f'  Profit/Loss:         ${metrics["final_capital"] - metrics["initial_capital"]:>12,.2f}')
print("-" * 60)
print(f'  Total Return:        {metrics["total_return_pct"]:>12.2f}%')
print(f'  Buy & Hold Return:   {metrics["buy_hold_return_pct"]:>12.2f}%')
print(f'  Alpha (vs B&H):      {metrics["alpha_pct"]:>12.2f}%')
print("-" * 60)
print(f'  Number of Trades:    {metrics["num_trades"]:>12}')
print(f'  Win Rate:            {metrics["win_rate_pct"]:>12.1f}%')
print(f'  Profit Factor:       {metrics["profit_factor"]:>12.2f}')
print(f'  Avg Win:             ${metrics["avg_win"]:>12.2f}')
print(f'  Avg Loss:            ${metrics["avg_loss"]:>12.2f}')
print("-" * 60)
print(f'  Max Drawdown:        {metrics["max_drawdown_pct"]:>12.2f}%')
print(f'  Sharpe Ratio:        {metrics["sharpe_ratio"]:>12.2f}')
print("-" * 60)

print("\n" + "="*60)
print("TEST 4: SUCCESS")
print("="*60)
print("\nFull backtest completed successfully!")
print(f"\nStrategy {'OUTPERFORMED' if metrics['alpha_pct'] > 0 else 'UNDERPERFORMED'} Buy & Hold by {abs(metrics['alpha_pct']):.2f}%")
