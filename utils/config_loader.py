# utils/config_loader.py
import os
import json5

def load_strategy_config(filename="strategy_config.jsonc"):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, filename)

    with open(config_path, 'r') as f:
        return json5.load(f)
