from typing import Type, Dict
from strategies.base_strategy import BaseStrategy

class StrategyRegistry:
    """
    Central registry for all trading strategies.
    Allows dynamic lookup and instantiation by name.
    """
    _registry: Dict[str, Type[BaseStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[BaseStrategy]):
        if name in cls._registry:
            raise ValueError(f"Strategy '{name}' is already registered.")
        cls._registry[name] = strategy_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseStrategy]:
        if name not in cls._registry:
            raise KeyError(f"Strategy '{name}' not found in registry.")
        return cls._registry[name]

    @classmethod
    def list_strategies(cls):
        return list(cls._registry.keys())
