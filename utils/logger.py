import logging
import os

# Create logs/ folder if not exists
os.makedirs("logs", exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/backtest.log", mode='w', encoding='utf-8')
    ]
)

# Export module-level logger for reuse
logger = logging.getLogger(__name__)

def get_logger(name: str):
    return logging.getLogger(name)
