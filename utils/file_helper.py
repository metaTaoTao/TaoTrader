# file: utils/io_helper.py

import os
import pandas as pd

class DataIO:
    @staticmethod
    def save(df: pd.DataFrame, name: str, output_dir: str = "output"):
        """
        Save DataFrame to a pickle file (overwrites if exists).
        """
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"{name}.pkl")
        df.to_pickle(path)
        print(f"✅ Saved: {path}")

    @staticmethod
    def load(name: str, output_dir: str = "output") -> pd.DataFrame:
        """
        Load DataFrame from a pickle file.
        """
        path = os.path.join(output_dir, f"{name}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"No such file: {path}")
        print(f"📦 Loaded: {path}")
        return pd.read_pickle(path)
