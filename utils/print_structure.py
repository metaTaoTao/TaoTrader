import os

IGNORE_DIRS = {"venv", ".venv", "__pycache__", ".git", ".ipynb_checkpoints"}

def print_tree(root, indent=""):
    items = sorted(os.listdir(root))
    for i, item in enumerate(items):
        if item in IGNORE_DIRS or any(ignored in item for ignored in IGNORE_DIRS):
            continue
        path = os.path.join(root, item)
        if os.path.isdir(path):
            print(f"{indent}├── {item}/")
            print_tree(path, indent + "│   ")
        else:
            print(f"{indent}├── {item}")

if __name__ == "__main__":
    print("Project structure:\n")
    print_tree(r"C:\Users\tzhang\PycharmProjects\TaoTrader")