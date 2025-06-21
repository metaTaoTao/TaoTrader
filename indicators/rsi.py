# file: indicators/rsi.py

import pandas as pd

class RSIIndicator:
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        delta = df["close"].diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=self.period, min_periods=self.period).mean()
        avg_loss = loss.rolling(window=self.period, min_periods=self.period).mean()

        rs = avg_gain / (avg_loss + 1e-10)  # 防止除以0
        df["rsi"] = 100 - (100 / (1 + rs))

        return df  # ✅ 保留所有原始列，包括 timestamp
