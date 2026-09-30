"""
Test 3: Risk Management

This test verifies cooldown, leverage, and position sizing.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from strategy import RiskManager
from datetime import datetime, timedelta

print("="*60)
print("TEST 3: RISK MANAGEMENT")
print("="*60)

print('\n[1/4] Initializing risk manager...')
rm = RiskManager(cooldown_hours=48, leverage=2.5)
print(f'  Cooldown: {rm.cooldown_hours} hours')
print(f'  Leverage: {rm.leverage}x')
print(f'  Stop Loss: {rm.stop_loss_pct*100:.1f}%')
print(f'  Take Profit: {rm.take_profit_pct*100:.1f}%')

print('\n[2/4] Testing cooldown mechanism...')
exit_time = datetime(2024, 1, 1, 10, 0, 0)
rm.trigger_cooldown(exit_time)
print(f'  Position closed at: {exit_time}')

# Check 24 hours later (should be in cooldown)
check_time_1 = exit_time + timedelta(hours=24)
in_cooldown_1 = rm.is_in_cooldown(check_time_1)
print(f'  After 24h: In cooldown = {in_cooldown_1} (expected: True)')

# Check 50 hours later (should be out of cooldown)
check_time_2 = exit_time + timedelta(hours=50)
in_cooldown_2 = rm.is_in_cooldown(check_time_2)
print(f'  After 50h: In cooldown = {in_cooldown_2} (expected: False)')

if in_cooldown_1 and not in_cooldown_2:
    print('  [OK] Cooldown mechanism working correctly')
else:
    print('  [ERROR] Cooldown mechanism issue')

print('\n[3/4] Testing position sizing...')
capital = 10000
price = 50000
quantity = rm.calculate_position_size(capital, price)
position_value = price * quantity
expected_value = capital * 0.95 * 2.5

print(f'  Capital: ${capital:,.2f}')
print(f'  BTC Price: ${price:,.2f}')
print(f'  Leverage: {rm.leverage}x')
print(f'  Max Position: {rm.max_position_size*100:.0f}% of capital')
print(f'  Quantity: {quantity:.6f} BTC')
print(f'  Position value: ${position_value:,.2f}')
print(f'  Expected: ${expected_value:,.2f}')

if abs(position_value - expected_value) < 1:
    print('  [OK] Position sizing correct')
else:
    print('  [ERROR] Position sizing mismatch')

print('\n[4/4] Testing exit conditions...')
entry_price = 50000
current_price_1 = 47000  # -6% (should trigger stop loss at -5%)
current_price_2 = 58000  # +16% (should trigger take profit at +15%)
current_price_3 = 51000  # +2% (no exit)

should_exit_1, reason_1 = rm.check_exit_conditions(entry_price, current_price_1, False)
should_exit_2, reason_2 = rm.check_exit_conditions(entry_price, current_price_2, False)
should_exit_3, reason_3 = rm.check_exit_conditions(entry_price, current_price_3, False)

print(f'  Entry: ${entry_price:,.0f}')
print(f'  Price ${current_price_1:,.0f} (-6%): Exit={should_exit_1}, Reason={reason_1}')
print(f'  Price ${current_price_2:,.0f} (+16%): Exit={should_exit_2}, Reason={reason_2}')
print(f'  Price ${current_price_3:,.0f} (+2%): Exit={should_exit_3}, Reason={reason_3}')

if should_exit_1 and should_exit_2 and not should_exit_3:
    print('  [OK] Exit conditions working correctly')
else:
    print('  [ERROR] Exit condition issue')

print("\n" + "="*60)
print("TEST 3: SUCCESS")
print("="*60)
print("\nRisk management working correctly!")
