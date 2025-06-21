# file: utils/io_helper.py

import os
import pandas as pd
import config

class DataIO:
    @staticmethod
    def save(df: pd.DataFrame, name: str):
        """
        Save DataFrame to a pickle file (overwrites if exists).
        """
        output_dir = config.OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"{name}.pkl")
        df.to_pickle(path)
        print(f"✅ Saved: {path}")

    @staticmethod
    def load(name: str) -> pd.DataFrame:
        """
        Load DataFrame from a pickle file.
        """
        output_dir = config.OUTPUT_DIR
        path = os.path.join(output_dir, f"{name}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"No such file: {path}")
        print(f"📦 Loaded: {path}")
        return pd.read_pickle(path)
