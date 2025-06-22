import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bot_command.scan_command import scan_command
from bot_command.score_command import score_command

# 启用日志
logging.basicConfig(level=logging.INFO)

# 启动 Bot
def main():
    from dotenv import load_dotenv
    import os
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CommandHandler("score", score_command))

    app.run_polling()

if __name__ == "__main__":
    main()
