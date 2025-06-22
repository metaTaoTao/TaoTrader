# bot_main.py

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from score_system.scanner import get_top_coins  # 假设你已有打分模块
from utils.file_helper import DataIO

# 启用日志
logging.basicConfig(level=logging.INFO)

# 处理 /scan 指令
from tabulate import tabulate
import tempfile

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        timeframe = str.lower(args[0]) if len(args) >= 1 else "1h"
        sort_key = args[1]+'_score' if len(args) >= 2 else "final_score"

        data_obj = DataIO.load(f'scores_{timeframe}')
        timestamp = data_obj.get("timestamp", "N/A")
        df = data_obj['data']

        if sort_key not in df.columns:
            await update.message.reply_text(
                f"⚠️ Invalid score key: `{sort_key}`\n\n可选项包括：\n"
                "`final_score`, `return_score`, `trend_score`, `volume_score`, `alpha_score`, `narrative_score`"
            )
            return

        df_sorted = df.sort_values(sort_key, ascending=False).reset_index(drop=True)
        df_sorted.index += 1  # Rank starts from 1

        # 📋 Top 30 as preview
        preview_table = tabulate(
            df_sorted[["symbol", sort_key]].head(30),
            headers=["Symbol", sort_key],
            tablefmt="github",
            showindex=True,
            floatfmt=".3f"
        )
        preview_message = f"""📊 Top 30 Tokens by {timeframe.upper()} `{sort_key}`:
📅 扫描时间：{timestamp}

{preview_table}

🧠 当前评分维度：`{sort_key}`
🧩 可用评分维度：
- `final`：综合评分
- `return`：涨跌幅评分
- `trend`：趋势评分
- `volume`：成交量评分
- `alpha`：Alpha收益评分
- `narrative`：叙事热度评分

📎 示例：`/scan trend 4h`
📎 完整榜单已附加为文件发送。
"""

        await update.message.reply_text(preview_message)

        # 📎 附加完整榜单为 txt 文件
        full_table = tabulate(
            df_sorted[["symbol", sort_key]],
            headers=["Symbol", sort_key],
            tablefmt="plain",
            showindex=True,
            floatfmt=".3f"
        )

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tmp_file:
            tmp_file.write(full_table)
            tmp_file_path = tmp_file.name

        await update.message.reply_document(
            document=open(tmp_file_path, "rb"),
            filename=f"top_{sort_key}_{timeframe}.txt",
            caption=f"📎 Full Ranking by `{sort_key}` ({timeframe})"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")



# 启动 Bot
def main():
    from dotenv import load_dotenv
    import os
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("scan", scan_command))

    app.run_polling()

if __name__ == "__main__":
    main()
