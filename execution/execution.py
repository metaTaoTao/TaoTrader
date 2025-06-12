from utils.config_loader import load_strategy_config
import pandas as pd


class ExecutionEngine:
    """
    Simulates trading execution using buy/sell strategy and tracks positions, PnL, and risk control.

    Parameters:
    - config_path (str): Path to JSON config file.
    """

    def __init__(self, config_path: str):

        self.config = load_strategy_config()

        self.starting_capital = self.config["starting_capital"]
        self.stop_loss_pct = self.config["stop_loss_pct"]
        self.current_capital = self.starting_capital
        self.position = 0
        self.entry_price = None
        self.realized_pnl = 0
        self.trade_log = []

    def run_backtest(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run backtest on DataFrame with buy/sell strategy.

        Assumes columns: ['timestamp', 'open', 'high', 'low', 'close', 'entry_signal', 'exit_signal']

        Returns:
        - DataFrame with unrealized/realized pnl and capital
        """
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["realized_pnl"] = 0.0
        df["unrealized_pnl"] = 0.0
        df["capital"] = self.starting_capital
        df["position"] = 0

        for i in range(len(df)):
            row = df.iloc[i]
            price = row["close"]
            high = row["high"]
            low = row["low"]

            # Entry
            if row.get("entry_signal", False) and self.position == 0:
                self.entry_price = price
                self.position = self.current_capital / price
                self.current_capital = 0

            # Stop loss
            if self.position > 0 and low <= self.entry_price * (1 - self.stop_loss_pct):
                sell_price = self.entry_price * (1 - self.stop_loss_pct)
                self.current_capital = self.position * sell_price
                self.realized_pnl += self.current_capital - self.starting_capital
                self.trade_log.append(("SL", row["timestamp"], sell_price))
                self.position = 0
                self.entry_price = None

            # Exit
            elif row.get("exit_signal", False) and self.position > 0:
                sell_price = price
                self.current_capital = self.position * sell_price
                self.realized_pnl += self.current_capital - self.starting_capital
                self.trade_log.append(("TP", row["timestamp"], sell_price))
                self.position = 0
                self.entry_price = None

            # Track values
            unrealized = self.position * price if self.position > 0 else 0
            df.at[df.index[i], "unrealized_pnl"] = unrealized - (self.position * self.entry_price if self.entry_price else 0)
            df.at[df.index[i], "realized_pnl"] = self.realized_pnl
            df.at[df.index[i], "capital"] = self.current_capital + unrealized
            df.at[df.index[i], "position"] = self.position

        return df
