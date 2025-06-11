class ScoreSystem:
    """
    Scoring system for evaluating a crypto asset based on 4 key dimensions:
    sentiment, fundamentals, technical strength, and risk/reward.
    """

    def __init__(self, override_sentiment=None):
        """
        Initialize the score system.

        Parameters:
        - override_sentiment: float or None, allows manual override of sentiment score (0 to 1)
        """
        self.override_sentiment = override_sentiment

    def score_sentiment(self):
        """
        Evaluate current market sentiment. If override is set, use it.

        Returns:
        - float: sentiment score (0 or 1)
        """
        if self.override_sentiment is not None:
            return int(self.override_sentiment >= 0.5)
        # Default: simulate using dummy data or placeholder for future API
        return 1  # Assume strong sentiment for now

    def score_fundamentals(self, coin_name, mentions=100):
        """
        Evaluate coin's narrative and fundamental heat.

        Parameters:
        - coin_name: str, name of the coin
        - mentions: int, how often the coin appears in social data (Twitter, Telegram)

        Returns:
        - float: fundamental score (0 or 1)
        """
        return int(mentions > 50)

    def score_technical(self, df):
        """
        Evaluate technical structure based on EMA trend.

        Parameters:
        - df: pandas DataFrame with close prices and EMA columns

        Returns:
        - float: technical score (0 or 1)
        """
        try:
            latest = df.iloc[-1]
            if latest['EMA5'] > latest['EMA10'] > latest['EMA20'] > latest['EMA60']:
                return 1
        except:
            pass
        return 0

    def score_risk_reward(self, entry_price, stop_loss, target_price):
        """
        Evaluate risk/reward ratio at the entry point.

        Parameters:
        - entry_price: float, intended buy price
        - stop_loss: float, stop loss price
        - target_price: float, expected target price

        Returns:
        - float: risk/reward score (0 or 1)
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(target_price - entry_price)
        if risk == 0:
            return 0
        rr_ratio = reward / risk
        return int(rr_ratio >= 3)

    def total_score(self, df, coin_name, mentions, entry_price, stop_loss, target_price):
        """
        Combine all 4 scores into one total score.

        Returns:
        - int: score between 0 and 4
        """
        s = self.score_sentiment()
        f = self.score_fundamentals(coin_name, mentions)
        t = self.score_technical(df)
        r = self.score_risk_reward(entry_price, stop_loss, target_price)
        return s + f + t + r
