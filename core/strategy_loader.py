import os
import importlib
from pathlib import Path

def load_all_strategies():
    """
    Dynamically import all strategy modules from the strategies/ directory
    to ensure their registration code executes.
    """
    strategies_path = Path(__file__).resolve().parent.parent / "strategies"

    for file in os.listdir(strategies_path):
        if file.endswith(".py") and file != "__init__.py" and not file.startswith("base"):
            module_name = file[:-3]  # remove .py
            import_path = f"strategies.{module_name}"
            try:
                importlib.import_module(import_path)
            except Exception as e:
                print(f"Failed to load {import_path}: {e}")