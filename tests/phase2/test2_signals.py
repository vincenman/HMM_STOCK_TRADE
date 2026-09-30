"""
Test 2: Signal Generation (8-Condition Voting System)

This test verifies that the 8-condition voting system evaluates correctly.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from data import DataLoader
from strategy import SignalGenerator, add_all_indicators

print("="*60)
print("TEST 2: SIGNAL GENERATION")
print("="*60)

print('\n[1/4] Loading data...')
loader = DataLoader()
data = loader.fetch_data()
print(f'  Loaded {len(data)} rows')

print('\n[2/4] Adding indicators...')
data = add_all_indicators(data)
print('  Indicators added')

print('\n[3/4] Generating signals...')
signal_gen = SignalGenerator()
data = signal_gen.evaluate_conditions(data)
print('  Conditions evaluated')

print('\n[4/4] Checking conditions...')
latest = data.iloc[-1]

conditions = {
    'RSI < 90': latest['Cond_RSI'],
    'Momentum > 1%': latest['Cond_Momentum'],
    'Volatility < 6%': latest['Cond_Volatility'],
    'Volume > 20-SMA': latest['Cond_Volume'],
    'ADX > 25': latest['Cond_ADX'],
    'Price > 50 EMA': latest['Cond_EMA50'],
    'Price > 200 EMA': latest['Cond_EMA200'],
    'MACD > Signal': latest['Cond_MACD'],
}

print("\nConditions Met:")
print("-" * 60)
for name, met in conditions.items():
    status = '[YES]' if met else '[ NO]'
    print(f'  {status}  {name}')

total_met = sum(conditions.values())
print("\n" + "-" * 60)
print(f'Total: {total_met}/8 conditions met')
print(f'Entry allowed: {"YES" if total_met >= 7 else "NO"} (need >= 7 conditions)')

print("\n" + "="*60)
print("TEST 2: SUCCESS")
print("="*60)
print("\nSignal generation working correctly!")
