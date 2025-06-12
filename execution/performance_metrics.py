import pandas as pd

def calculate_performance_metrics(df: pd.DataFrame, starting_capital: float):
    """
    Calculate performance metrics: total return, max drawdown, return series.

    Parameters:
    - df (pd.DataFrame): DataFrame with 'capital' column
    - starting_capital (float): Initial capital

    Returns:
    - None (prints metrics and chart)
    """
    df = df.copy()
    df["capital"] = df["capital"].ffill()
    df["returns"] = df["capital"].pct_change().fillna(0)
    df["cum_return"] = df["capital"] - starting_capital
    df["rolling_max"] = df["capital"].cummax()
    df["drawdown"] = df["capital"] - df["rolling_max"]
    df["drawdown_pct"] = df["drawdown"] / df["rolling_max"]

    max_dd = df["drawdown"].min()
    max_dd_pct = df["drawdown_pct"].min()

    print(f"Total Return ($): {df['cum_return'].iloc[-1]:.2f}")
    print(f"Max Drawdown ($): {max_dd:.2f}")
    print(f"Max Drawdown (%): {max_dd_pct * 100:.2f}%")

    return df[["timestamp", "capital", "realized_pnl", "unrealized_pnl", "returns", "drawdown"]]
