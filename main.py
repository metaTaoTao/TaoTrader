# main.py

import argparse
import pandas as pd
from utils.config_loader import load_strategy_config
from execution.execution import ExecutionEngine
from utils.plots import plot_backtest_results


def parse_args():
    parser = argparse.ArgumentParser(description="Run trading strategy backtest.")
    parser.add_argument("--data", type=str, default="data/sample_data.csv", help="Path to OHLCV data CSV file.")
    parser.add_argument("--config", type=str, default="strategy_config.jsonc", help="Path to strategy config file.")
    parser.add_argument("--start", type=str, default=None, help="Start date (YYYY-MM-DD).")
    parser.add_argument("--end", type=str, default=None, help="End date (YYYY-MM-DD).")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load data
    df = pd.read_csv(args.data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=False)

    # Filter by date range if provided
    if args.start:
        df = df[df["timestamp"] >= pd.to_datetime(args.start)]
    if args.end:
        df = df[df["timestamp"] <= pd.to_datetime(args.end)]

    # Load config & init engine
    config = load_strategy_config(args.config)
    engine = ExecutionEngine()

    # Run backtest
    results = engine.run_backtest(df)

    # Plot results
    plot_backtest_results(results, title="Strategy Backtest")


if __name__ == "__main__":
    main()