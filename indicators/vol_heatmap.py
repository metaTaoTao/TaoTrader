from indicators.base_indicator import BaseIndicator
import mplfinance as mpf
import pandas as pd
class VolumeHeatmapIndicator(BaseIndicator):
    def __init__(self, length=610, slength=610,
                 threshold_extra_high=4.0, threshold_high=2.5,
                 threshold_medium=1.0, threshold_normal=-0.5):
        self.length = length
        self.slength = slength
        self.thresholds = {
            "extra_high": threshold_extra_high,
            "high": threshold_high,
            "medium": threshold_medium,
            "normal": threshold_normal
        }
        self.color_map = {
            "extra_high": "#FF0000",
            "high": "#FF7800",
            "medium": "#FFCF03",
            "normal": "#A0D6DC",
            "low": "#1F9CAC",
            "unknown": "#AAAAAA"
        }

    def calculate(self, df):
        df["vol_ma"] = df["volume"].rolling(window=self.length, min_periods=1).mean()
        df["vol_std"] = df["volume"].rolling(window=self.slength, min_periods=1).std()
        df["stdbar"] = (df["volume"] - df["vol_ma"]) / df["vol_std"]

        def classify(std):
            if pd.isna(std):
                return "unknown"
            for cat, th in self.thresholds.items():
                if std > th:
                    return cat
            return "low"

        df["volume_category"] = df["stdbar"].apply(classify)
        return df

    def plot(self, df):
        if 'volume_category' not in df.columns:
            return []
        colors = df['volume_category'].map(self.color_map).fillna("#CCCCCC").tolist()
        return [mpf.make_addplot(df['volume'], type='bar', panel=1, color=colors, width=0.5, ylabel='Volume')]

