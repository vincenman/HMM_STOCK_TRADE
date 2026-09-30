"""
End-to-end test of the complete dashboard flow
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("="*60)
print("END-TO-END DASHBOARD TEST")
print("="*60)

print("\n[1/5] Testing data loading...")
try:
    from data import DataLoader
    from datetime import datetime, timedelta

    loader = DataLoader()
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=60)

    data = loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=False)
    print(f"[OK] Data loaded: {len(data)} rows")
    print(f"  Date range: {data.index.min()} to {data.index.max()}")
except Exception as e:
    print(f"[ERROR] Data loading failed: {e}")
    exit(1)

print("\n[2/5] Testing HMM model training...")
try:
    from models import HMM_AVAILABLE, HMMEngine

    if not HMM_AVAILABLE:
        print("[SKIP] hmmlearn not available - this is your issue!")
        print("  Solution: Run setup_with_uv.bat to get Python 3.12 + hmmlearn")
        exit(0)

    engine = HMMEngine(n_states=7)
    success, error = engine.train(data)

    if success:
        print(f"[OK] Model trained successfully")
        print(f"  Bull state: {engine.bull_state}")
        print(f"  Bear state: {engine.bear_state}")
    else:
        print(f"[ERROR] Training failed: {error}")
        exit(1)

except Exception as e:
    print(f"[ERROR] Model training failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n[3/5] Testing signal generation...")
try:
    from strategy import SignalGenerator, add_all_indicators

    data_with_indicators = add_all_indicators(data.copy())
    signal_gen = SignalGenerator()
    data_with_indicators = signal_gen.evaluate_conditions(data_with_indicators)

    print(f"[OK] Indicators and signals calculated")
    print(f"  Conditions met: {data_with_indicators['Conditions_Met'].iloc[-1]}/8")

except Exception as e:
    print(f"[ERROR] Signal generation failed: {e}")
    exit(1)

print("\n[4/5] Testing backtest...")
try:
    from backtesting import Backtester

    regime_states = engine.predict(data)
    backtester = Backtester(initial_capital=10000.0)

    metrics = backtester.run(
        data_with_indicators,
        regime_states,
        engine.bull_state,
        engine.bear_state
    )

    print(f"[OK] Backtest completed")
    print(f"  Total return: {metrics['total_return_pct']:.2f}%")
    print(f"  Number of trades: {metrics['num_trades']}")
    print(f"  Win rate: {metrics['win_rate_pct']:.1f}%")

except Exception as e:
    print(f"[ERROR] Backtest failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n[5/5] Testing dashboard components...")
try:
    from ui.components import create_candlestick_chart, display_metrics_grid
    import streamlit as st

    print(f"[OK] Dashboard components imported")
    print(f"  Streamlit version: {st.__version__}")

except Exception as e:
    print(f"[ERROR] Dashboard components failed: {e}")
    exit(1)

print("\n" + "="*60)
print("END-TO-END TEST: ALL PASSED!")
print("="*60)
print("\nConclusion:")
print("  - All backend functionality works")
print("  - Dashboard should work correctly")
print("\nIf dashboard still fails:")
print("  1. Check browser console (F12) for errors")
print("  2. Check terminal for Streamlit errors")
print("  3. Make sure you're using .venv environment")
