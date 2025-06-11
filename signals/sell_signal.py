import pandas as pd

class SellSignal:
    def __init__(self):
        pass

    def detect_exit_signal_full(
            self,
            df,
            volume_window=20,
            price_jump_threshold=0.03,
            volume_spike_multiplier=2
    ):
        """
        Detect three types of exit signals in a price time series DataFrame.

        Parameters:
        ----------
        df : pd.DataFrame
            Candlestick data with at least the following columns:
            ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        volume_window : int, default=20
            The lookback window for calculating the average volume (used for signals 1 and 2 comparisons)

        price_jump_threshold : float, default=0.03
            The minimum open-to-close percentage increase to qualify as a sharp price spike (e.g., 0.03 means 3%)

        volume_spike_multiplier : float, default=2
            A multiplier on average volume to define what counts as a volume spike

        Returns:
        -------
        pd.DataFrame
            The original DataFrame with additional boolean columns:
            - 'exit_signal_1' : True when sharp price rise + volume spike occurs
            - 'exit_signal_2' : True when price breaks previous high but closes below (2B reversal)
            - 'exit_signal_3' : True when price makes higher highs with lower volume (volume-price divergence)
            - 'exit_signal'   : True if any of the above conditions are met
        """
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["exit_signal_1"] = False
        df["exit_signal_2"] = False
        df["exit_signal_3"] = False
        df["exit_signal"] = False

        # Rolling average volume for comparisons
        df["avg_volume"] = df["volume"].rolling(window=volume_window).mean()

        highs = df["high"].values
        volumes = df["volume"].values

        for i in range(volume_window, len(df)):
            open_ = df["open"].iloc[i]
            close = df["close"].iloc[i]
            high = df["high"].iloc[i]
            volume = df["volume"].iloc[i]
            avg_vol = df["avg_volume"].iloc[i]

            # --- Signal 1: Sharp price spike + high volume ---
            price_jump = (close - open_) / open_
            volume_spike = volume > volume_spike_multiplier * avg_vol
            if price_jump > price_jump_threshold and volume_spike:
                df.loc[df.index[i], "exit_signal_1"] = True

            # --- Signal 2: Breakout then close below recent high ---
            recent_high = df["high"].iloc[i - volume_window:i].max()
            if high > recent_high and close < recent_high:
                df.loc[df.index[i], "exit_signal_2"] = True

            # --- Signal 3: Higher highs with lower volume ---
            if i >= volume_window + 2:
                if highs[i] > highs[i - 1] > highs[i - 2] and volumes[i] < volumes[i - 1] < volumes[i - 2]:
                    df.loc[df.index[i], "exit_signal_3"] = True

            # Combine any signals
            if df.loc[df.index[i], ["exit_signal_1", "exit_signal_2", "exit_signal_3"]].any():
                df.loc[df.index[i], "exit_signal"] = True

        return df
