# bot_commands/score_command.py

from telegram import Update
from telegram.ext import ContextTypes
from utils.file_helper import DataIO
import pandas as pd

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 1:
            await update.message.reply_text("❗用法示例：`/score ETHUSDT 1h`，参数为【币名】【时间周期】（可省略，默认为1h）", parse_mode="Markdown")
            return

        symbol = args[0].upper()
        timeframe = str.lower(args[1]) if len(args) >= 2 else "1h"

        data = DataIO.load(f'scores_{timeframe}')
        if isinstance(data, dict) and "data" in data:
            df = data["data"]
            timestamp = data.get("timestamp", "")
        else:
            df = data
            timestamp = ""

        row = df[df["symbol"] == symbol]

        if row.empty:
            await update.message.reply_text(f"⚠️ 未找到 `{symbol}` 在 `{timeframe}` 时间段的评分数据。", parse_mode="Markdown")
            return

        row = row.iloc[0]
        message = f"""📈 `{symbol}` 在 `{timeframe.upper()}` 时间段的评分：

🧠 综合评分 (final_score): `{row['final_score']:.3f}`
📈 涨跌幅评分 (return_score): `{row['return_score']:.3f}`
📊 趋势评分 (ema_score): `{row['ema_score']:.3f}`
📉 成交量评分 (volume_score): `{row['volume_score']:.3f}`
📉 RSI 反转信号 (rsi_score): `{row['rsi_score']:.3f}`
🧮 Alpha评分 (momentum_score): `{row['momentum_score']:.3f}`

🕒 最新评分时间戳: `{timestamp}`

📎 示例：`/score ETHUSDT 4h`
"""
        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
