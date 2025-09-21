# bot_command/help_command.py

from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    TG Bot帮助命令
    显示所有可用的命令和用法
    """
    help_text = """🤖 **TaoTrader Bot 使用指南**

🔍 **币种查询命令**:
• `/ticker ANIMEUSDT` - 查询币种详细信息
  包含市值、板块分类、24h涨跌幅等数据
  ⚡ 数据来源：本地映射表（每日更新，响应极快）

📊 **评分系统命令**:
• `/scan final 1h` - 显示评分排行榜
  可选参数：评分类型 (final/return/ema/volume/rsi/momentum) 和时间周期 (1h/4h/1d)
  
• `/score ETHUSDT 1h` - 查询特定币种的评分
  显示综合评分和各项子评分

🆘 **帮助命令**:
• `/help` - 显示此帮助信息

📍 **支持的ticker格式**:
• Binance格式：`BTCUSDT`, `ETHUSDT`, `ANIMEUSDT`
• OKX格式：`BTC-USDT`, `ETH-USDT`, `ANIME-USDT`

💡 **使用示例**:
• `/ticker MEUSDT` - 查询Magic Eden币种信息
• `/scan final 1h` - 查看1小时综合评分排行
• `/score BTCUSDT 4h` - 查看BTC的4小时评分详情

⚡ **注意事项**:
• ticker查询从本地映射表读取，响应极快
• 映射表数据每日更新，确保信息准确性
• 评分数据基于历史扫描结果
• 所有数据仅供参考，投资需谨慎

🔄 **更新频率**:
• 币种信息：每日更新（本地映射表）
• 评分数据：定时更新

📋 **数据管理**:
• 使用 `python update_mapping_table.py --file tickers.txt` 更新映射表
• 映射表包含市值、板块、价格变动等完整信息

📞 如有问题或建议，请联系管理员。"""

    await update.message.reply_text(help_text, parse_mode="Markdown")
