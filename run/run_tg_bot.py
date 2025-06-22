import sys
import os

# 自动将项目根路径添加到 sys.path 中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from utils.file_helper import DataIO

# 启用日志
logging.basicConfig(level=logging.INFO)

# 处理 /scan 指令
from tabulate import tabulate
import tempfile

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        sort_key = args[0] + '_score' if len(args) >= 1 else "final_score"
        timeframe = str.lower(args[1]) if len(args) >= 2 else "1h"

        data_obj = DataIO.load(f'scores_{timeframe}')
        timestamp = data_obj.get("timestamp", "N/A")
        df = data_obj['data']

        if sort_key not in df.columns:
            await update.message.reply_text(
                f"⚠️ Invalid score key: `{sort_key}`\n\n可选项包括：\n"
                 'return_score', 'ema_score', 'volume_score', 'rsi_score',
          'momentum_score', 'final_score'
            )
            return

        df_sorted = df.sort_values(sort_key, ascending=False).reset_index(drop=True)
        df_sorted.index += 1  # Rank starts from 1

        # 📋 Top 30 as preview
        preview_table = tabulate(
            df_sorted[["symbol", sort_key]].head(10),
            headers=["Symbol", sort_key],
            tablefmt="github",
            showindex=True,
            floatfmt=".3f"
        )
        preview_message = f"""📊 Top 10 Tokens by {timeframe.upper()} `{sort_key}`:
📅 扫描时间：{timestamp}

{preview_table}

🧠 当前评分维度：`{sort_key}`
🧩 可用评分维度：
- `final`：综合评分
- `return`：涨跌幅评分
- `ema`：趋势评分, EMA 多头排列（ema5 > ema10 > ema20）代表趋势强劲，否则弱
- `volume`：成交量评分, 利用 VolumeHeatmap 对近期交易量进行分类评分，衡量资金活跃度
- 'rsi': RSI 反转预警机制：超买弱（<0.5），超卖强（>0.5），中间地带为中性
- `momentum`：Alpha收益评分, 计算相对动量（alpha）：剥离beta后的超额收益，衡量是否跑赢BTC
- `narrative`：叙事热度评分, 还未实现

📎 示例：`/scan return 1h`
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
