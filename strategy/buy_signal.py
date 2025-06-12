import pandas as pd


class BuySignal:
    def __init__(self):
        pass

    def detect_pullback_entry(self, df):
        """
        Detect potential entry strategy based on:
        - Prior uptrend
        - 2–3 wave pullback (higher low or double bottom)
        - Bullish reversal candle
        """
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["entry_signal"] = False

        # Calculate simple return over recent trend window
        df["trend_return"] = df["close"].pct_change(periods=20)

        for i in range(25, len(df) - 1):
            # Step 1: Check previous 20-bar trend is up
            recent_trend = df.loc[i - 20:i, "trend_return"].sum()
            if recent_trend < 0.02:  # Require at least 2% gain over 20 bars
                continue

            # Step 2: Check 2-3 pullbacks: last 5 bars form a local support
            lows = df["low"].iloc[i - 5:i]
            low_diff = lows.max() - lows.min()
            if low_diff / lows.min() > 0.02:  # Too wide = not a real support
                continue

            # Step 3: Bullish reversal candle
            open_ = df["open"].iloc[i]
            close = df["close"].iloc[i]
            prev_close = df["close"].iloc[i - 1]

            is_bullish_engulf = close > open_ and close > prev_close and open_ < prev_close
            is_big_bull = close > open_ and (close - open_) > (df["high"].iloc[i] - df["low"].iloc[i]) * 0.6

            if is_bullish_engulf or is_big_bull:
                df.loc[i, "entry_signal"] = True

        return df

    def detect_dizijue_entry(self, df, trend_window=20, pullback_range=0.015):
        """
        Detect Dizijue-style low absorption entries:
        - Identify strong upward trend (A wave)
        - Detect second pullback (B wave) to a key support zone (recent mini bottom)
        - Confirm with bullish candle structure at that support
        """
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["entry_signal"] = False

        # Compute EMA to help identify overall trend
        df["EMA20"] = df["close"].ewm(span=20).mean()

        for i in range(trend_window + 10, len(df)):
            window = df.iloc[i - trend_window - 10:i - 10]

            # Step 1: Check that price has increased significantly over the trend window
            price_start = window["close"].iloc[0]
            price_peak = window["close"].max()
            if price_peak / price_start < 1.05:
                continue  # Skip if no strong trend

            # Step 2: Find local bottom in the A wave
            local_lows = window["low"].rolling(3, center=True).min()
            potential_supports = window["low"][local_lows == window["low"]]
            if potential_supports.empty:
                continue
            support_level = potential_supports.iloc[-1]

            # Step 3: Check if current low revisits support zone
            current_low = df["low"].iloc[i]
            if abs(current_low - support_level) / support_level > pullback_range:
                continue  # Too far from support zone

            # Step 4: Confirm with bullish structure (long body green candle)
            open_ = df["open"].iloc[i]
            close = df["close"].iloc[i]
            high = df["high"].iloc[i]
            low = df["low"].iloc[i]

            is_bullish = close > open_ and (close - open_) > (high - low) * 0.5
            if is_bullish:
                df.loc[df.index[i], "entry_signal"] = True

        return df

