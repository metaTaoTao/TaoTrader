# position_manager.py

class PositionSizer:
    """
    PositionSizer helps decide position size based on four trading opportunity criteria:
    1. Market sentiment
    2. Fundamental attention
    3. Technical strength
    4. Risk-reward ratio

    Usage:
        sizer = PositionSizer(max_position=1.0)
        score = sizer.score_opportunity(signals)
        position = sizer.decide_position_size(score)
    """

    def __init__(self, max_position=1.0):
        """
        Parameters:
        ----------
        max_position : float
            Maximum position size (e.g., 1.0 = 100% of risk capital)
        """
        self.max_position = max_position

    def score_opportunity(self, signal_dict):
        """
        Score the trade opportunity quality from 0 to 4.

        Parameters:
        ----------
        signal_dict : dict
            {
                'market_sentiment': bool,
                'fundamental_attention': bool,
                'technical_strength': bool,
                'risk_reward': bool
            }

        Returns:
        ----------
        score : int
            Number of satisfied conditions
        """
        return sum([
            signal_dict.get('market_sentiment', False),
            signal_dict.get('fundamental_attention', False),
            signal_dict.get('technical_strength', False),
            signal_dict.get('risk_reward', False)
        ])

    def decide_position_size(self, score):
        """
        Recommend position size based on the score.

        Parameters:
        ----------
        score : int
            Number of satisfied opportunity conditions

        Returns:
        ----------
        position_size : float
            Recommended position size (e.g., 0.25 = 25%)
        """
        if score >= 4:
            return self.max_position
        elif score == 3:
            return self.max_position * 0.25
        elif score == 2:
            return self.max_position * 0.10
        else:
            return 0.0


# Example usage
if __name__ == "__main__":
    sizer = PositionSizer(max_position=1.0)
    signal = {
        'market_sentiment': True,
        'fundamental_attention': False,
        'technical_strength': True,
        'risk_reward': True
    }
    score = sizer.score_opportunity(signal)
    size = sizer.decide_position_size(score)
    print(f"Score = {score}, Recommended Position Size = {size:.0%}")
