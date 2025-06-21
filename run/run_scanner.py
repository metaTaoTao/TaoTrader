# scheduler_runner.py
import time
import traceback
from score_system.scanner import get_top_coins
from utils.file_helper import DataIO

TIMEFRAMES = ["1h", "4h"]  # 可扩展多个时间维度

def run_scan_and_save():
    for tf in TIMEFRAMES:
        try:
            result_df = get_top_coins(timeframe=tf)
            DataIO.save(result_df, f"scores_{tf}")
            print(f"[{tf}] ✅ Saved {len(result_df)} rows.")
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Hourly Scanner Running...")
    while True:
        run_scan_and_save()
        print("✅ Scan complete. Sleeping 1 hour...\n")
        time.sleep(3600)
