"""
Quick test to verify the timezone fix
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from data import DataLoader
from datetime import datetime, timedelta

print("="*60)
print("TESTING TIMEZONE FIX")
print("="*60)

print("\n[1/2] Creating DataLoader...")
loader = DataLoader()
print("[OK] DataLoader created")

print("\n[2/2] Testing data fetch...")
try:
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    print(f"  Fetching from {start_date} to {end_date}")
    data = loader.fetch_data(start_date=start_date, end_date=end_date, force_refresh=True)

    print(f"[OK] Successfully fetched {len(data)} rows")
    print(f"  Date range: {data.index.min()} to {data.index.max()}")
    print(f"  Latest price: ${data['Close'].iloc[-1]:,.2f}")

except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print("\n" + "="*60)
print("TIMEZONE FIX VERIFIED!")
print("="*60)
print("\nNow run: streamlit run app.py")
print("And click 'Refresh Data' - it should work now!")
