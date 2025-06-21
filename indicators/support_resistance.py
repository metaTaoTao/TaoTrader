from indicators.base_indicator import BaseIndicator
import mplfinance as mpf
import pandas as pd
class SupportResistancePivotIndicator(BaseIndicator):
    def __init__(self, left=15, right=15):
        self.left = left
        self.right = right

    def calculate(self, df):
        highs = df['high']
        lows = df['low']
        df['pivot_high'] = highs[(highs.shift(self.left) < highs) & (highs.shift(-self.right) < highs)]
        df['pivot_low'] = lows[(lows.shift(self.left) > lows) & (lows.shift(-self.right) > lows)]
        return df

    def plot(self, df):
        plots = []
        if 'pivot_high' in df:
            plots.append(mpf.make_addplot(df['pivot_high'], type='line', color='red', width=2))
        if 'pivot_low' in df:
            plots.append(mpf.make_addplot(df['pivot_low'], type='line', color='green', width=2))
        return plots
