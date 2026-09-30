"""
Simple test script to verify Phase 3 components can be imported.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("="*60)
print("PHASE 3: UI COMPONENTS TEST")
print("="*60)

print("\n[1/4] Testing UI component imports...")
try:
    from ui.components import (
        create_candlestick_chart,
        create_portfolio_chart,
        display_metrics_grid,
        render_config_panel
    )
    print("[OK] UI components imported successfully")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print("\n[2/4] Testing Streamlit import...")
try:
    import streamlit as st
    print(f"[OK] Streamlit version: {st.__version__}")
except Exception as e:
    print(f"[ERROR] Streamlit not installed: {e}")
    print("Install with: pip install streamlit")

print("\n[3/4] Testing Plotly import...")
try:
    import plotly
    print(f"[OK] Plotly version: {plotly.__version__}")
except Exception as e:
    print(f"[ERROR] Plotly not installed: {e}")

print("\n[4/4] Checking main app file...")
if os.path.exists("app.py"):
    print("[OK] app.py found")
    print("     Run with: streamlit run app.py")
else:
    print("[ERROR] app.py not found")

print("\n" + "="*60)
print("PHASE 3 COMPONENT TEST COMPLETE")
print("="*60)
print("\nTo start the dashboard:")
print("  1. cd C:\\Traning\\stock_analysis")
print("  2. streamlit run app.py")
print("\nThe dashboard will open in your web browser!")
