# scanner_runner.py
import traceback
from score_system.scanner import get_top_coins
from utils.file_helper import DataIO

TIMEFRAMES = ["1h", "4h"]

def run_scan_and_save():
    for tf in TIMEFRAMES:
        try:
            result_df = get_top_coins(timeframe=tf)
            DataIO.save(result_df, f"scores_{tf}")
            print(f"[{tf}] ✅ Saved {len(result_df)} rows.")
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Running hourly scan task")
    run_scan_and_save()
