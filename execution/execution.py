import pandas as pd
from utils.config_loader import load_strategy_config
from strategy.stop_loss import StopLossStrategy
from strategy.take_profit import TakeProfitStrategy

class ExecutionEngine:
    """
    Simulates trading execution using buy/sell strategy and tracks positions, PnL, and risk control.
    Automatically calculates dynamic stop loss and take profit. Supports both long and short trades.
    """

    def __init__(self):
        self.config = load_strategy_config()

        self.starting_capital = self.config["starting_capital"]
        self.current_capital = self.starting_capital
        self.position = 0
        self.entry_price = None
        self.realized_pnl = 0
        self.trade_log = []

        self.stop_loss_strategy = StopLossStrategy(self.config)
        self.take_profit_strategy = TakeProfitStrategy(self.config)

        self.stop_loss_price = None
        self.take_profit_price = None
        self.side = None  # 'long' or 'short'

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
        df["executed_entry"] = False
        df["executed_exit"] = False

        max_capital = self.starting_capital
        max_drawdown = 0.0

        for i in range(len(df)):
            row = df.iloc[i]
            price = row["close"]
            high = row["high"]
            low = row["low"]

            # Entry logic
            if row.get("entry_signal", False) and self.position == 0:
                self.entry_price = price
                self.position = self.current_capital / price
                self.side = "long"
                self.current_capital = 0
                self.stop_loss_price = self.stop_loss_strategy.compute_stoploss(df, i, price, short=False)
                self.take_profit_price = self.take_profit_strategy.compute_take_profit(df, i, price, short=False)
                df.at[df.index[i], "executed_entry"] = True

            elif row.get("exit_signal", False) and self.position == 0:
                self.entry_price = price
                self.position = self.current_capital / price
                self.side = "short"
                self.current_capital = 0
                self.stop_loss_price = self.stop_loss_strategy.compute_stoploss(df, i, price, short=True)
                self.take_profit_price = self.take_profit_strategy.compute_take_profit(df, i, price, short=True)
                df.at[df.index[i], "executed_entry"] = True

            # Exit logic
            if self.position > 0:
                if self.side == "long":
                    if low <= self.stop_loss_price:
                        sell_price = self.stop_loss_price
                        self.current_capital = self.position * sell_price
                        self.realized_pnl += self.current_capital - self.starting_capital
                        self.trade_log.append(("SL", row["timestamp"], sell_price))
                        df.at[df.index[i], "executed_exit"] = True
                        self.position = 0
                        self.entry_price = None
                        self.side = None
                    elif row.get("exit_signal", False):
                        sell_price = price
                        self.current_capital = self.position * sell_price
                        self.realized_pnl += self.current_capital - self.starting_capital
                        self.trade_log.append(("TP", row["timestamp"], sell_price))
                        df.at[df.index[i], "executed_exit"] = True
                        self.position = 0
                        self.entry_price = None
                        self.side = None

                elif self.side == "short":
                    if high >= self.stop_loss_price:
                        buy_price = self.stop_loss_price
                        self.current_capital = self.starting_capital + (self.entry_price - buy_price) * self.position
                        self.realized_pnl += self.current_capital - self.starting_capital
                        self.trade_log.append(("SL", row["timestamp"], buy_price))
                        df.at[df.index[i], "executed_exit"] = True
                        self.position = 0
                        self.entry_price = None
                        self.side = None
                    elif row.get("entry_signal", False):
                        buy_price = price
                        self.current_capital = self.starting_capital + (self.entry_price - buy_price) * self.position
                        self.realized_pnl += self.current_capital - self.starting_capital
                        self.trade_log.append(("TP", row["timestamp"], buy_price))
                        df.at[df.index[i], "executed_exit"] = True
                        self.position = 0
                        self.entry_price = None
                        self.side = None

            # Track values
            unrealized = self.position * (price - self.entry_price) if self.position > 0 and self.side == "long" else \
                         self.position * (self.entry_price - price) if self.position > 0 and self.side == "short" else 0
            df.at[df.index[i], "unrealized_pnl"] = unrealized
            df.at[df.index[i], "realized_pnl"] = self.realized_pnl
            df.at[df.index[i], "capital"] = self.current_capital + unrealized
            df.at[df.index[i], "position"] = self.position if self.side == "long" else -self.position if self.side == "short" else 0

            total_equity = self.current_capital + unrealized
            max_capital = max(max_capital, total_equity)
            drawdown = max_capital - total_equity
            max_drawdown = max(max_drawdown, drawdown)

        final_capital = self.current_capital + (self.position * df.iloc[-1]["close"] if self.position > 0 else 0)
        total_return = final_capital - self.starting_capital

        print("\n=== Performance Summary ===")
        print(f"Final Capital: ${final_capital:.2f}")
        print(f"Total Return: ${total_return:.2f}")
        print(f"Max Drawdown: ${max_drawdown:.2f}")
        print(f"Trades Executed: {len(self.trade_log)}")
        if len(self.trade_log) > 0:
            wins = sum(1 for t in self.trade_log if t[0] == "TP")
            win_rate = wins / len(self.trade_log)
            print(f"Win Rate: {win_rate:.2%}")

        return df
