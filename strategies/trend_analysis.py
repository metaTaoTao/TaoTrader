# trend_analysis.py
import pandas as pd

class TrendAnalyzer:
    def __init__(self, df):
        """
        Initialize with OHLCV DataFrame.
        df: DataFrame with columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        self.df = df.copy()

    def compute_emas(self, df):
        """Calculate EMA5, EMA10, EMA20, EMA60."""
        for span in [5, 10, 20, 60]:
            df[f'EMA{span}'] = df['close'].ewm(span=span, adjust=False).mean()
        return df

    def determine_ema_trend(self, latest_row):
        """
        Determine trend from latest EMA values.
        Returns: 'Bull', 'Bear', or 'Sideways'
        """
        print(f"EMA5:{latest_row['EMA5']}")
        print(f"EMA10:{latest_row['EMA10']}")
        print(f"EMA20:{latest_row['EMA20']}")
        print(f"EMA60:{latest_row['EMA60']}")
        if latest_row['EMA5'] > latest_row['EMA10'] > latest_row['EMA20'] > latest_row['EMA60']:
            return 'Bull'
        elif latest_row['EMA5'] < latest_row['EMA10'] < latest_row['EMA20'] < latest_row['EMA60']:
            return 'Bear'
        else:
            return 'Sideways'

    def get_trend_from_recent(self, n=100):
        """
        Analyze the trend from the most recent n candles.
        Returns: 'Bull', 'Bear', or 'Sideways'
        """
        if len(self.df) < n:
            raise ValueError("Not enough data to compute trend.")
        df_recent = self.df[-n:].copy()
        df_recent = self.compute_emas(df_recent)
        return self.determine_ema_trend(df_recent.iloc[-1])


if __name__ == "__main__":
    from data.market_data import get_kline
    df = get_kline("BTC-USDT-SWAP",'1h')
    trend = TrendAnalyzer(df)
    print(trend.get_trend_from_recent(100))