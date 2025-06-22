import os
import pickle


class DataIO:
    @staticmethod
    def save(obj, filename, folder="output"):
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{filename}.pkl")

        # 判断对象是否为 DataFrame 或 dict
        if hasattr(obj, "to_pickle"):
            obj.to_pickle(path)
        else:
            with open(path, "wb") as f:
                pickle.dump(obj, f)
        print(f"Saved: {path}")

    @staticmethod
    def load(filename, folder="output"):
        path = os.path.join(folder, f"{filename}.pkl")
        with open(path, "rb") as f:
            print(f"Loaded: {path}")
            return pickle.load(f)


