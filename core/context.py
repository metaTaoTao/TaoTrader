from utils.config_loader import ConfigLoader

class BacktestContext:
    """
    Context holder for all configs: strategy, backtest, and risk control.
    """

    def __init__(self, strategy_config_path: str, backtest_config_path: str, risk_config_path: str):
        """
        Initialize the backtest context with all config files.

        :param strategy_config_path: Path to strategy YAML config.
        :param backtest_config_path: Path to backtest environment YAML config.
        :param risk_config_path: Path to risk control YAML config.
        """
        self.strategy_config = ConfigLoader.load(strategy_config_path)
        self.backtest_config = ConfigLoader.load(backtest_config_path)
        self.risk_config = ConfigLoader.load(risk_config_path)

    def __repr__(self):
        return (
            f"<BacktestContext: "
            f"strategy={list(self.strategy_config.keys())}, "
            f"backtest={list(self.backtest_config.keys())}, "
            f"risk={list(self.risk_config.keys())}>"
        )
