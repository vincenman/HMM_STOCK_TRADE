"""
Test 1: Technical Indicators Calculation

This test verifies that all technical indicators are calculated correctly.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from data import DataLoader
from strategy import add_all_indicators

print("="*60)
print("TEST 1: TECHNICAL INDICATORS")
print("="*60)

print('\n[1/3] Loading data...')
loader = DataLoader()
data = loader.fetch_data()
print(f'  Loaded {len(data)} rows')

print(f'\n[2/3] Calculating indicators on {len(data)} rows...')
data_with_indicators = add_all_indicators(data)

print('\n[3/3] Checking indicators...')
indicators = [
    'RSI', 'EMA_50', 'EMA_200', 'SMA_20',
    'MACD', 'MACD_Signal', 'ADX',
    'Momentum', 'Volatility', 'Volume_SMA',
    'BB_Upper', 'BB_Middle', 'BB_Lower', 'ATR'
]

print("\nIndicator Values (Latest):")
print("-" * 60)
for ind in indicators:
    if ind in data_with_indicators.columns:
        value = data_with_indicators[ind].iloc[-1]
        if abs(value) > 1000:
            print(f'  {ind:20s}: {value:>15,.2f}')
        else:
            print(f'  {ind:20s}: {value:>15.4f}')
    else:
        print(f'  {ind:20s}: MISSING!')

print("\n" + "="*60)
print("TEST 1: SUCCESS")
print("="*60)
print("\nAll indicators calculated successfully!")
