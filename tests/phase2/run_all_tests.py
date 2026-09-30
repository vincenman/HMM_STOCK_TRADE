"""
Run All Phase 2 Tests

This script runs all Phase 2 tests sequentially.
"""

import subprocess
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

print("="*70)
print(" "*20 + "PHASE 2 TEST SUITE")
print("="*70)
print("\nRunning all Phase 2 tests...\n")

# Get the tests directory
tests_dir = os.path.dirname(os.path.abspath(__file__))

# List of tests to run
tests = [
    ("Test 1: Technical Indicators", "test1_indicators.py"),
    ("Test 2: Signal Generation", "test2_signals.py"),
    ("Test 3: Risk Management", "test3_risk_management.py"),
    ("Test 4: Complete Backtest", "test4_backtest.py"),
]

results = []

for i, (name, filename) in enumerate(tests, 1):
    print("\n" + "="*70)
    print(f"Running {name}...")
    print("="*70)

    test_path = os.path.join(tests_dir, filename)
    result = subprocess.run([sys.executable, test_path])

    results.append((name, result.returncode == 0))

    if result.returncode != 0:
        print(f"\n[WARNING] {name} encountered an issue")

    # Add spacing between tests
    if i < len(tests):
        print("\n" + "-"*70)
        input("\nPress Enter to continue to next test...")

# Summary
print("\n" + "="*70)
print(" "*25 + "TEST SUMMARY")
print("="*70)

passed = sum(1 for _, success in results if success)
total = len(results)

for name, success in results:
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status}  {name}")

print("-"*70)
print(f"Total: {passed}/{total} tests passed")
print("="*70)

if passed == total:
    print("\nAll Phase 2 tests passed! Phase 2 is COMPLETE!")
    print("\nNext: Proceed to Phase 3 - UI Development")
else:
    print(f"\n{total - passed} test(s) failed. Check output above for details.")

print("\nNote: Test 4 (Backtest) requires hmmlearn and will skip if not installed.")
print("Tests 1-3 can run without hmmlearn.\n")
