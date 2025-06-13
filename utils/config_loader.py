import os
import yaml

class ConfigLoader:
    """
    A simple YAML config loader for strategy, backtest, and risk control configs.
    """

    @staticmethod
    def load(path: str) -> dict:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录
        abs_path = os.path.join(base_path, path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Config file not found: {abs_path}")

        try:
            with open(abs_path, 'r') as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parsing error: {e}")
