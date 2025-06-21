class TakeProfitStrategy:
    """
    Take profit logic module supporting multiple methods:
    - atr: based on multiple of ATR (e.g., 1.5 * ATR)
    - fixed_pct: fixed % target (e.g., 10%)
    - structure: based on predefined resistance levels

    Parameters:
    - config: Dictionary containing strategies parameters
    """
    def __init__(self, config):
        self.method = config.get("take_profit_method", "atr")
        self.atr_period = config.get("atr_period", 14)
        self.atr_multiplier = config.get("take_profit_multiplier", 1.5)
        self.resistance_levels = config.get("resistance_levels", {})
        self.fixed_pct = config.get("take_profit_pct", 0.1)

    def compute_take_profit(self, df, entry_index, entry_price, short=False):
        """
        Compute take profit level based on selected method.

        Parameters:
        - df: DataFrame of Klines
        - entry_index: int, index where trade opened
        - entry_price: float, entry price
        - short: bool, whether the position is short (True) or long (False)

        Returns:
        - float: take profit price level
        """
        if self.method == "atr":
            high = df["high"].rolling(window=self.atr_period).max()
            low = df["low"].rolling(window=self.atr_period).min()
            atr = (high - low).rolling(window=self.atr_period).mean()
            if short:
                take_profit = entry_price - self.atr_multiplier * atr.iloc[entry_index]
            else:
                take_profit = entry_price + self.atr_multiplier * atr.iloc[entry_index]
            return take_profit

        elif self.method == "fixed_pct":
            return entry_price * (1 - self.fixed_pct) if short else entry_price * (1 + self.fixed_pct)

        elif self.method == "structure":
            if self.resistance_levels:
                if short:
                    return min(self.resistance_levels.values())
                else:
                    return max(self.resistance_levels.values())
            else:
                return entry_price * (0.97 if short else 1.03)

        else:
            raise ValueError("Unknown take profit method")
