class PositionManager:
    """
    Class for managing position sizing based on a four-factor scoring system:
    sentiment, fundamentals, technical strength, and risk/reward.
    """

    def __init__(self, min_position=0.01, max_position=1.0):
        """
        Initialize the position manager.

        Parameters:
        - min_position: Minimum position size (as a fraction, e.g., 0.01 for 1%)
        - max_position: Maximum position size (as a fraction, e.g., 1.0 for 100%)
        """
        self.min_position = min_position
        self.max_position = max_position

    def calculate_position_size(self, score):
        """
        Calculate the recommended position size based on score (0–4).

        Parameters:
        - score: Integer score from 0 to 4

        Returns:
        - float: recommended position size (between min_position and max_position)
        """
        score = max(0, min(score, 4))  # ensure score is within bounds
        if score < 2:
            return self.min_position
        elif score == 2:
            return 0.05
        elif score == 3:
            return 0.25
        else:  # score == 4
            return self.max_position

    def explain_position(self, score):
        """
        Generate explanation text for the position score and sizing decision.

        Parameters:
        - score: Integer score from 0 to 4

        Returns:
        - str: Explanation of decision
        """
        explanations = {
            0: "Only 0 factors aligned. Sit on cash or minimal exposure.",
            1: "1 factor aligned. Light test position only if confident.",
            2: "2 factors aligned. Small exploratory position allowed.",
            3: "3 factors aligned. Opportunity detected, deploy moderate position.",
            4: "All 4 factors aligned. Deploy maximum position size with confidence.",
        }
        return explanations.get(score, "Unknown score level.")

