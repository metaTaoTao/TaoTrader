# run/scanner_entry.py
import sys
import os

# 自动添加项目根目录到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sys
from datetime import datetime
from score_system.scanner import get_top_coins
from utils.file_helper import DataIO

SUPPORTED_TIMEFRAMES = ["15m", "1h", "4h", "1d"]

def run_scanner(tf: str):
    try:
        result_df = get_top_coins(timeframe=tf)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "timestamp": timestamp,
            "data": result_df
        }
        DataIO.save(data, f"scores_{tf}")
        print(f"[{tf}] ✅ Saved {len(result_df)} rows at {timestamp}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in SUPPORTED_TIMEFRAMES:
        print(f"Usage: python scanner_entry.py [{'|'.join(SUPPORTED_TIMEFRAMES)}]")
        sys.exit(1)

    run_scanner(sys.argv[1])
