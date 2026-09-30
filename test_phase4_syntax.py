"""
Quick syntax check for Phase 4 files.
"""
import sys
import os
import py_compile

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("="*60)
print("PHASE 4 SYNTAX CHECK")
print("="*60)

files_to_check = [
    "paper_trading/__init__.py",
    "paper_trading/live_feed.py",
    "paper_trading/notifications.py",
    "paper_trading/reports.py",
    "ui/pages/paper_trading.py",
]

all_ok = True

for file in files_to_check:
    filepath = os.path.join(project_root, file)
    print(f"\nChecking {file}...")
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  [OK] Syntax valid")
    except py_compile.PyCompileError as e:
        print(f"  [ERROR] Syntax error: {e}")
        all_ok = False

print("\n" + "="*60)
if all_ok:
    print("ALL FILES PASSED SYNTAX CHECK!")
    print("="*60)
    print("\nReady to start dashboard!")
else:
    print("ERRORS FOUND - FIX BEFORE RUNNING")
    print("="*60)
    exit(1)
