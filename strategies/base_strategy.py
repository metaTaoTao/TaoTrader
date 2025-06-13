from abc import ABC, abstractmethod
from utils.config_loader import ConfigLoader
import pandas as pd

class BaseStrategy(ABC):
    def __repr__(self):
        return f"<{self.__class__.__name__} Strategy | Params: {list(self.config.keys())}>"

    def __init__(self, data: pd.DataFrame, config_path: str = None):
        self.data = data
        self.config = {}
        if config_path:
            self.config = ConfigLoader.load(config_path)

    @abstractmethod
    def entry_signal(self, index: int) -> str:
        pass

    @abstractmethod
    def exit_signal(self, index: int, entry_price: float) -> bool:
        """
        Optional exit signal logic for directional exit (can supplement or replace stop_loss/take_profit).
        Return True if exit condition is met.
        """
        pass

    @abstractmethod
    def stop_loss(self, entry_price: float, current_price: float) -> bool:
        pass

    @abstractmethod
    def take_profit(self, entry_price: float, current_price: float) -> bool:
        pass

    def entry_score(self, signal: str) -> float:
        """
        Convert entry signal like 'long_strong' or 'short_medium' to numeric score.
        """
        if signal is None:
            return 0.0
        strength = signal.split('_')[-1]
        mapping = {'strong': 1.0, 'medium': 0.5}
        return mapping.get(strength, 0.0)

    def entry_direction(self, signal: str) -> str:
        """
        Extract direction from signal: 'long' or 'short'
        """
        if signal is None:
            return None
        return signal.split('_')[0]