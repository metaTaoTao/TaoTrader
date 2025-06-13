import os
import pandas as pd
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_markdown_report(trades_df: pd.DataFrame, perf: dict, unrealized: dict = None, output_path: str = "reports"):
    """
    Generate a Markdown report from trade data, performance, and final unrealized position.
    """
    if trades_df.empty and unrealized is None:
        logger.warning("No trades to report.")
        return

    os.makedirs(output_path, exist_ok=True)
    today = datetime.today().strftime("%Y%m%d")
    filename = f"backtest_report_{today}.md"
    filepath = os.path.join(output_path, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# Backtest Summary Report\n\n")

        f.write("## Performance Overview\n\n")
        for key, value in perf.items():
            f.write(f"- **{key}**: {value}\n")

        f.write("\n## Trades Overview\n\n")
        f.write(f"Total Trades: {len(trades_df)}\n\n")

        if not trades_df.empty:
            f.write(
                "| Entry Time | Exit Time | Direction | Entry Price | Exit Price | Qty | Capital | PnL (%) | PnL ($) | Reason |\n")
            f.write(
                "|------------|-----------|-----------|--------------|-------------|-----|----------|----------|---------|--------|\n")
            for _, row in trades_df.iterrows():
                f.write(
                    f"| {row['entry_time']} | {row['exit_time']} | {row['direction']} | "
                    f"{row['entry_price']:.2f} | {row['exit_price']:.2f} | {row['qty']:.4f} | {row['capital']:.2f} | "
                    f"{row['pnl_pct'] * 100:.2f}% | {row['pnl_dollar']:.2f} | {row['exit_reason']} |\n"
                )

        if unrealized and isinstance(unrealized, dict):
            f.write("\n## Unrealized Position at End\n\n")
            f.write(f"- **Entry Time**: {unrealized.get('entry_time')}\n")
            f.write(f"- **Entry Price**: {unrealized.get('entry_price'):.2f}\n")
            f.write(f"- **Qty**: {unrealized['qty']:.4f}\n")
            f.write(f"- **Capital**: {unrealized['capital']:.2f}\n")
            f.write(f"- **Current Price**: {unrealized.get('current_price'):.2f}\n")
            f.write(f"- **Direction**: {unrealized.get('direction')}\n")
            f.write(f"- **Unrealized PnL (%)**: {unrealized.get('pnl_pct') * 100:.2f}%\n")
            f.write(f"- **Unrealized PnL ($)**: {unrealized.get('pnl_dollar'):.2f}\n")

        f.write("\n---\n")
        f.write(f"Report generated at {datetime.now()}\n")

    logger.info(f"Markdown report saved to: {filepath}")
