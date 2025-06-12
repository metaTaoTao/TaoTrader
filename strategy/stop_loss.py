class StopLossStrategy:
    """
    Stop loss logic module supporting multiple methods:
    - atr: based on multiple of ATR (e.g., 0.5 * ATR)
    - structure: based on predefined support levels

    Parameters:
    - config: Dictionary containing strategy parameters
    """
    def __init__(self, config):
        self.method = config.get("stop_loss_method", "atr")
        self.atr_period = config.get("atr_period", 14)
        self.atr_multiplier = config.get("atr_multiplier", 0.5)
        self.support_levels = config.get("support_levels", {})

    def compute_stoploss(self, df, entry_index, entry_price, short=False):
        """
        Compute stop loss level based on selected method.

        Parameters:
        - df: DataFrame of Klines
        - entry_index: int, index where trade opened
        - entry_price: float, entry price
        - short: bool, whether the position is short (True) or long (False)

        Returns:
        - float: stop loss price level
        """
        if self.method == "atr":
            high = df["high"].rolling(window=self.atr_period).max()
            low = df["low"].rolling(window=self.atr_period).min()
            atr = (high - low).rolling(window=self.atr_period).mean()
            if short:
                stop_loss = entry_price + self.atr_multiplier * atr.iloc[entry_index]
            else:
                stop_loss = entry_price - self.atr_multiplier * atr.iloc[entry_index]
            return stop_loss

        elif self.method == "structure":
            if self.support_levels:
                if short:
                    return max(self.support_levels.values())
                else:
                    return min(self.support_levels.values())
            else:
                return entry_price * (1.03 if short else 0.97)

        else:
            raise ValueError("Unknown stop loss method")

