import pandas as pd

def calculate_volume_heatmap(df, length=610, slength=610,
                              threshold_extra_high=4.0,
                              threshold_high=2.5,
                              threshold_medium=1.0,
                              threshold_normal=-0.5):
    df = df.copy()
    df["vol_ma"] = df["volume"].rolling(window=length, min_periods=1).mean()
    df["vol_std"] = df["volume"].rolling(window=slength, min_periods=1).std()
    df["stdbar"] = (df["volume"] - df["vol_ma"]) / df["vol_std"]

    def classify_volume(stdbar):
        if pd.isna(stdbar):
            return "unknown", -1
        elif stdbar > threshold_extra_high:
            return "extra_high", 4
        elif stdbar > threshold_high:
            return "high", 3
        elif stdbar > threshold_medium:
            return "medium", 2
        elif stdbar > threshold_normal:
            return "normal", 1
        else:
            return "low", 0

    result = df["stdbar"].apply(lambda x: classify_volume(x))
    df["volume_category"] = result.apply(lambda x: x[0])
    df["volume_rank"] = result.apply(lambda x: x[1])
    return df

import pandas as pd
import numpy as np

def generate_luxalgo_sr_breaks(df, left_bars=15, right_bars=15, volume_thresh=20):
    """
    Reimplementation of LuxAlgo's Support/Resistance + Break Detection logic in Python.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'open', 'high', 'low', 'close', 'volume' columns with datetime index.
    left_bars : int
        Number of bars to the left of pivot.
    right_bars : int
        Number of bars to the right of pivot.
    volume_thresh : float
        Volume oscillator threshold to confirm breakout.

    Returns
    -------
    df_result : pd.DataFrame
        Original DataFrame with added columns:
            - pivot_high, pivot_low
            - vol_osc (volume oscillator %)
            - resistance_break, support_break (bool)
    """
    df = df.copy()

    def find_pivot_high(series):
        return series == series.rolling(window=left_bars + right_bars + 1, center=True).max()

    def find_pivot_low(series):
        return series == series.rolling(window=left_bars + right_bars + 1, center=True).min()

    # Compute pivots
    df['pivot_high'] = np.where(find_pivot_high(df['high']), df['high'], np.nan)
    df['pivot_low'] = np.where(find_pivot_low(df['low']), df['low'], np.nan)

    # Shift pivots to align with final bar of the pattern
    df['pivot_high'] = df['pivot_high'].shift(right_bars + 1)
    df['pivot_low'] = df['pivot_low'].shift(right_bars + 1)

    # Volume oscillator
    short_vol = df['volume'].ewm(span=5).mean()
    long_vol = df['volume'].ewm(span=10).mean()
    df['vol_osc'] = 100 * (short_vol - long_vol) / long_vol

    # Break conditions
    df['resistance_break'] = (
        (df['close'] > df['pivot_high']) &
        (df['open'] - df['low'] <= df['close'] - df['open']) &
        (df['vol_osc'] > volume_thresh)
    )

    df['support_break'] = (
        (df['close'] < df['pivot_low']) &
        (df['open'] - df['close'] <= df['high'] - df['open']) &
        (df['vol_osc'] > volume_thresh)
    )

    return df
