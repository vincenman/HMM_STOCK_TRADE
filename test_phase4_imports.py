"""
Quick test to verify Phase 4 imports work correctly.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("="*60)
print("PHASE 4 IMPORT TEST")
print("="*60)

print("\n[1/5] Testing PaperTradingEngine import...")
try:
    from paper_trading import PaperTradingEngine
    print("[OK] PaperTradingEngine imported")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print("\n[2/5] Testing LivePriceFeed import...")
try:
    from paper_trading.live_feed import LivePriceFeed, LiveDataManager
    print("[OK] LivePriceFeed and LiveDataManager imported")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print("\n[3/5] Testing NotificationManager import...")
try:
    from paper_trading.notifications import NotificationManager, TradeJournal
    print("[OK] NotificationManager and TradeJournal imported")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print("\n[4/5] Testing ReportGenerator import...")
try:
    from paper_trading.reports import ReportGenerator
    print("[OK] ReportGenerator imported")
except Exception as e:
    print(f"[ERROR] {e}")
    print("[INFO] Install reportlab: uv pip install reportlab")
    exit(1)

print("\n[5/5] Testing paper trading page import...")
try:
    from ui.pages.paper_trading import render_paper_trading_page
    print("[OK] Paper trading page imported")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print("\n" + "="*60)
print("ALL IMPORTS SUCCESSFUL!")
print("="*60)
print("\nPhase 4 is ready to use!")
print("\nNext steps:")
print("  1. Run: setup_phase4.bat")
print("  2. Run: run_dashboard.bat")
print("  3. Go to 'Paper Trading' tab")
print("="*60)
