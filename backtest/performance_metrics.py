
def analyze_performance(trades_df, unrealized=None):
    if trades_df.empty and unrealized is None:
        return {"Total Trades": 0, "No trades to analyze": True}

    total_trades = len(trades_df)
    total_pnl = trades_df["pnl_dollar"].sum() if not trades_df.empty else 0

    if unrealized:
        total_pnl += unrealized['pnl_dollar']

    avg_pnl = total_pnl / total_trades if total_trades > 0 else 0

    summary = {
        "Total Trades": total_trades,
        "Total PnL ($)": round(total_pnl, 2),
        "Average PnL ($)": round(avg_pnl, 2),
        "Unrealized Position": unrealized if unrealized else "None"
    }
    return summary
