import pandas as pd
import numpy as np
import mplfinance as mpf


class BaseIndicator:
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add indicator-specific columns to df"""
        raise NotImplementedError

    def plot(self, df: pd.DataFrame):
        """Return mplfinance addplot list or None"""
        return []