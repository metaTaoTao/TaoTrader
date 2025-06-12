import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd

def plot_kline_chart(
    df,
    title='Candlestick Chart',
    show_ema=True,
    show_volume=True,
    show_entry_signal=True,
    show_exit_signal=True,
    show_exit_types=True,
    ema_spans=[5, 10, 20, 60],
    fig_scale=1.5,
    fig_ratio=(20, 10)
):
    """
    Plot candlestick chart with optional EMA lines, volume, entry/exit strategy, and detailed exit types.

    Parameters:
    ----------
    df : pd.DataFrame
        DataFrame containing candlestick data with columns:
        ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    title : str
        Title of the chart
    show_ema : bool
        Whether to overlay EMA lines
    show_volume : bool
        Whether to show volume subplot
    show_entry_signal : bool
        Plot green '^' where df['entry_signal'] == True
    show_exit_signal : bool
        Plot red 'v' where df['exit_signal'] == True
    show_exit_types : bool
        If True, also marks exit_signal_1/2/3 separately (purple, orange, gray)
    ema_spans : list of int
        List of periods for calculating EMAs
    fig_scale : float
        Scaling factor for figure size
    fig_ratio : tuple of int
        Aspect ratio of the figure (width, height)
    """
    df_plot = df.copy()
    df_plot.index = pd.to_datetime(df_plot['timestamp'])

    addplots = []

    # Add EMA overlays
    if show_ema:
        for span in ema_spans:
            label = f"EMA{span}"
            df_plot[label] = df_plot["close"].ewm(span=span).mean()
            color = {5: 'green', 10: 'blue', 20: 'orange', 60: 'red'}.get(span, 'gray')
            addplots.append(mpf.make_addplot(df_plot[label], color=color, width=1))

    # Entry strategy marker
    if show_entry_signal and 'entry_signal' in df_plot.columns:
        buy_mask = df_plot["entry_signal"] == True
        buy_price = df_plot["low"] * 0.995
        addplots.append(mpf.make_addplot(
            buy_price.where(buy_mask),
            type='scatter',
            markersize=100,
            marker='^',
            color='lime'
        ))

    # Combined exit strategy marker
    if show_exit_signal and 'exit_signal' in df_plot.columns:
        sell_mask = df_plot["exit_signal"] == True
        sell_price = df_plot["high"] * 1.005
        addplots.append(mpf.make_addplot(
            sell_price.where(sell_mask),
            type='scatter',
            markersize=100,
            marker='v',
            color='red'
        ))

    # Individual exit strategy types
    if show_exit_types:
        for col, color in [
            ("exit_signal_1", 'purple'),
            ("exit_signal_2", 'orange'),
            ("exit_signal_3", 'gray')
        ]:
            if col in df_plot.columns:
                signal_mask = df_plot[col] == True
                signal_price = df_plot["high"] * 1.01
                addplots.append(mpf.make_addplot(
                    signal_price.where(signal_mask),
                    type='scatter',
                    markersize=60,
                    marker='v',
                    color=color
                ))

    mpf.plot(
        df_plot,
        type='candle',
        volume=show_volume,
        addplot=addplots if addplots else None,
        style='charles',
        title=title,
        ylabel='Price (USD)',
        ylabel_lower='Volume',
        figratio=fig_ratio,
        figscale=fig_scale,
        tight_layout=True
    )


def plot_backtest_results(df: pd.DataFrame, title="Backtest Result with Executed Trades"):
    """
    Plot backtest result focusing on actual executed entry/exit signals.

    Parameters:
    - df (pd.DataFrame): Must contain ['timestamp', 'close', 'executed_entry', 'executed_exit', 'capital', 'realized_pnl', 'unrealized_pnl']
    - title (str): Title of the plot
    """
    df = df.copy()
    df.set_index("timestamp", inplace=True)

    fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)

    # --- Price chart with actual trades ---
    axes[0].plot(df["close"], label="Close Price", color="black")
    axes[0].scatter(df[df["executed_entry"]].index, df[df["executed_entry"]]["close"],
                    marker="^", color="lime", label="Buy Executed", s=100)
    axes[0].scatter(df[df["executed_exit"]].index, df[df["executed_exit"]]["close"],
                    marker="v", color="red", label="Sell Executed", s=100)
    axes[0].set_ylabel("Price")
    axes[0].set_title(f"{title} - Price & Trades")
    axes[0].legend()

    # --- Capital curve ---
    axes[1].plot(df["capital"], label="Capital", color="blue")
    axes[1].set_ylabel("Capital ($)")
    axes[1].set_title("Capital Over Time")
    axes[1].legend()

    # --- PnL curve ---
    axes[2].plot(df["realized_pnl"], label="Realized PnL", color="green")
    axes[2].plot(df["unrealized_pnl"], label="Unrealized PnL", color="orange", linestyle="--")
    axes[2].set_ylabel("PnL ($)")
    axes[2].set_title("PnL Over Time")
    axes[2].legend()

    plt.xlabel("Time")
    plt.tight_layout()
    plt.show()