import pandas as pd
import numpy as np
import mplfinance as mpf
from indicators.vol_heatmap import VolumeHeatmapIndicator
from indicators.base_indicator import BaseIndicator

class BulldozerV2Pattern(BaseIndicator):
    def __init__(self):
        self.heatmap = VolumeHeatmapIndicator()
        self.init_segments = []
        self.consolidation_segments = []
        self.breakout_points = []

    def calculate_atr(self, df, period=14):
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def calculate(self, df):
        df = df.copy()
        df = self.heatmap.calculate(df)
        df['return'] = df['close'].pct_change()
        df['atr'] = self.calculate_atr(df, period=14)
        df['is_bullish'] = df['close'] > df['open']
        df['is_strong_up'] = (
            (df['return'] > 2 * df['atr'] / df['close'].shift(1)) &
            (df['is_bullish'])
        )
        df['is_volume_hot'] = df['volume_category'].isin(["medium", "high", "extra_high"])

        # 启动段识别
        self.init_segments = []
        for i in range(len(df) - 4):
            window = df.iloc[i:i+4]
            bullish_count = window['is_bullish'].sum()
            strong_up_count = window['is_strong_up'].sum()
            hot_vol_count = window['is_volume_hot'].sum()

            if bullish_count >= 3 and hot_vol_count >= 2 and strong_up_count >= 3:
                self.init_segments.append((i, i+3))

        # 整理段识别（结构型整理段）
        self.consolidation_segments = []
        for (start_idx, end_idx) in self.init_segments:
            init_high = df.iloc[start_idx:end_idx+1]['high'].max()
            init_low = df.iloc[start_idx:end_idx+1]['low'].min()
            resistance = init_high
            max_length = 100
            cons_start = end_idx + 1
            cons_end = cons_start

            for i in range(cons_start, min(len(df), cons_start + max_length)):
                bar = df.iloc[i]
                if bar['high'] > resistance*1.1 and bar['is_volume_hot'] and bar['is_bullish']:
                    break  # 整理结束
                if bar['low'] < init_low * 0.9:
                    break  # 跌太深，不算整理
                cons_end = i

            if cons_end > cons_start:
                self.consolidation_segments.append((cons_start, cons_end))

        return df

    def plot(self, df):
        apds = []
        y1 = pd.Series(np.nan, index=df.index)
        y2 = pd.Series(np.nan, index=df.index)

        for seg in self.init_segments:
            start_idx, end_idx = seg
            high = df.iloc[start_idx:end_idx+1]["high"].max()
            low = df.iloc[start_idx:end_idx+1]["low"].min()
            y1.iloc[start_idx:end_idx+1] = high
            y2.iloc[start_idx:end_idx+1] = low

        if not y1.dropna().empty and not y2.dropna().empty:
            apds.append(mpf.make_addplot(
                y1,
                panel=0,
                fill_between=dict(
                    y1=y1.values,
                    y2=y2.values,
                    alpha=0.25,
                    color='green'
                )
            ))

        # 绘制整理段（橙色）
        y3 = pd.Series(np.nan, index=df.index)
        y4 = pd.Series(np.nan, index=df.index)
        for seg in self.consolidation_segments:
            start_idx, end_idx = seg
            high = df.iloc[start_idx:end_idx+1]['high'].max()
            low = df.iloc[start_idx:end_idx+1]['low'].min()
            y3.iloc[start_idx:end_idx+1] = high
            y4.iloc[start_idx:end_idx+1] = low

        if not y3.dropna().empty and not y4.dropna().empty:
            apds.append(mpf.make_addplot(
                y3,
                panel=0,
                fill_between=dict(
                    y1=y3.values,
                    y2=y4.values,
                    alpha=0.2,
                    color='orange'
                )
            ))

        return apds


if __name__ == "__main__":
    from data.market_data import OKXDataFetcher
    from utils.plots import ChartPlotter
    from indicators.vol_heatmap import VolumeHeatmapIndicator

    fetcher = OKXDataFetcher()
    symbol = 'BTCpip install python-binance-USDT'
    df = fetcher.get_kline(symbol, bar="4H", total=400)
    plotter = ChartPlotter(indicators=[BulldozerV2Pattern(), VolumeHeatmapIndicator()])
    plotter.plot(df, title="ETH-USDT")