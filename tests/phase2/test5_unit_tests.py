"""
Test 5: Run All Unit Tests

This test runs the complete pytest test suite for Phase 2.
"""

import subprocess
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
os.chdir(project_root)

print("="*60)
print("TEST 5: UNIT TESTS")
print("="*60)

print("\n[1/2] Running indicator tests...")
print("-" * 60)
result1 = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_indicators.py", "-v"],
    capture_output=False
)

print("\n[2/2] Running backtester tests...")
print("-" * 60)
result2 = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_backtester.py", "-v"],
    capture_output=False
)

print("\n" + "="*60)
if result1.returncode == 0 and result2.returncode == 0:
    print("TEST 5: SUCCESS")
    print("="*60)
    print("\nAll unit tests passed!")
else:
    print("TEST 5: SOME TESTS FAILED")
    print("="*60)
    print("\nCheck output above for details.")
