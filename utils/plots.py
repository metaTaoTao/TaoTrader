from indicators.base_indicator import BaseIndicator
import mplfinance as mpf
import pandas as pd
class ChartPlotter:
    def __init__(self, indicators=None):
        self.indicators = indicators if indicators else []

    def add_indicator(self, indicator: BaseIndicator):
        self.indicators.append(indicator)

    def plot(self, df: pd.DataFrame, title="K-line", fig_scale=1.5, fig_ratio=(20, 10)):
        df_plot = df.copy()
        if not isinstance(df_plot.index, pd.DatetimeIndex):
            df_plot.index = pd.to_datetime(df_plot.index)

        # Run all calculations
        for indicator in self.indicators:
            df_plot = indicator.calculate(df_plot)

        # Gather addplots
        addplots = []
        for indicator in self.indicators:
            addplots.extend(indicator.plot(df_plot))

        mpf.plot(
            df_plot,
            type='candle',
            volume=False,
            addplot=addplots,
            style='charles',
            title=title,
            ylabel='Price',
            ylabel_lower='Volume',
            figratio=fig_ratio,
            figscale=fig_scale,
            tight_layout=True,
            warn_too_much_data=99999
        )
