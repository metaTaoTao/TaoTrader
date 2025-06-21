import pandas as pd

class TradeLogger:
    def __init__(self):
        self.records = []

    def record(self, trade: dict):
        self.records.append(trade)

    def to_dataframe(self) -> pd.DataFrame:
        if not self.records:
            return pd.DataFrame()
        return pd.DataFrame(self.records)
