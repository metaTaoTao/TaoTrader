# bot_command/ticker_command.py

from telegram import Update
from telegram.ext import ContextTypes
import sys
import os
import pandas as pd
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_local_mapping_table():
    """加载本地映射表"""
    mapping_file = 'coin_mapping_table.csv'
    
    if not os.path.exists(mapping_file):
        return None, "映射表文件不存在"
    
    try:
        df = pd.read_csv(mapping_file)
        return df, None
    except Exception as e:
        return None, f"读取映射表失败: {str(e)}"

def find_ticker_info(df, ticker):
    """从映射表中查找ticker信息"""
    # 直接匹配ticker
    result = df[df['ticker'].str.upper() == ticker.upper()]
    
    if not result.empty:
        return result.iloc[0].to_dict()
    
    # 如果没找到，尝试匹配base_symbol
    base_symbol = ticker.upper()
    
    # 移除常见的quote currencies
    quote_currencies = ['USDT', 'USDC', 'BTC', 'ETH', 'BNB', 'BUSD', 'FDUSD']
    for quote in quote_currencies:
        if ticker.upper().endswith(quote):
            base_symbol = ticker.upper()[:-len(quote)]
            break
    
    # 通过base_symbol匹配
    result = df[df['base_symbol'].str.upper() == base_symbol]
    if not result.empty:
        return result.iloc[0].to_dict()
    
    return None

async def ticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    TG Bot ticker查询命令（从本地映射表读取）
    用法: /ticker ANIMEUSDT
    """
    try:
        args = context.args
        if len(args) < 1:
            await update.message.reply_text(
                "❗ 用法示例：`/ticker ANIMEUSDT`\n\n"
                "📍 支持格式：\n"
                "• Binance格式：`ANIMEUSDT`, `BTCUSDT`\n"
                "• OKX格式：`ANIME-USDT`, `BTC-USDT`\n\n"
                "💡 示例：`/ticker MEUSDT`\n"
                "⚡ 数据来源：本地映射表（每日更新）", 
                parse_mode="Markdown"
            )
            return

        ticker = args[0].upper()
        
        # 加载本地映射表
        df, error = load_local_mapping_table()
        if error:
            await update.message.reply_text(
                f"❌ 无法读取本地数据：{error}\n\n"
                f"💡 请联系管理员更新映射表",
                parse_mode="Markdown"
            )
            return
        
        # 从本地数据查找ticker信息
        coin_info = find_ticker_info(df, ticker)
        
        if not coin_info:
            await update.message.reply_text(
                f"❌ 未找到 `{ticker}` 的信息\n\n"
                f"🔍 可能原因：\n"
                f"• ticker不存在于映射表中\n"
                f"• 映射表需要更新\n\n"
                f"💡 请检查ticker拼写或联系管理员",
                parse_mode="Markdown"
            )
            return
        
        # 格式化数字显示
        def format_number(value):
            if pd.isna(value) or value is None:
                return "N/A"
            try:
                num = float(value)
                if num >= 1e9:
                    return f"${num/1e9:.2f}B"
                elif num >= 1e6:
                    return f"${num/1e6:.2f}M"
                elif num >= 1e3:
                    return f"${num/1e3:.2f}K"
                else:
                    return f"${num:.2f}"
            except:
                return "N/A"
        
        # 处理categories字段（从分号分隔的字符串转换为列表）
        categories_str = coin_info.get('categories', '')
        if categories_str and isinstance(categories_str, str):
            categories = [cat.strip() for cat in categories_str.split(';') if cat.strip()]
        else:
            categories = []
        
        # 获取数据更新时间
        last_updated = coin_info.get('last_updated', 'N/A')
        
        # 构建回复消息
        message = f"🔍 **{ticker}** 分析结果\n"
        message += "=" * 30 + "\n\n"
        
        message += f"📛 **币种名称**: {coin_info.get('name', 'Unknown')}\n"
        message += f"🆔 **CoinGecko ID**: `{coin_info.get('coingecko_id', 'Unknown')}`\n"
        message += f"🏷️ **Base Symbol**: `{coin_info.get('base_symbol', 'Unknown').upper()}`\n"
        
        # 处理市值排名
        rank = coin_info.get('market_cap_rank')
        if pd.notna(rank) and rank is not None:
            message += f"🏆 **市值排名**: #{int(rank)}\n\n"
        else:
            message += f"🏆 **市值排名**: N/A\n\n"
        
        message += "💰 **市场数据**:\n"
        message += f"• 市值 (MV): `{format_number(coin_info.get('market_cap'))}`\n"
        message += f"• 完全稀释估值 (FDV): `{format_number(coin_info.get('fdv'))}`\n"
        message += f"• 24h交易量: `{format_number(coin_info.get('volume_24h'))}`\n"
        
        # 处理24h涨跌幅
        price_change = coin_info.get('price_change_24h')
        if pd.notna(price_change) and price_change is not None:
            try:
                change = float(price_change)
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                message += f"• 24h涨跌幅: {emoji} `{change:.2f}%`\n"
            except:
                pass
        
        message += "\n🏢 **板块分类**:\n"
        if categories:
            for i, category in enumerate(categories[:10], 1):  # 限制显示前10个
                message += f"{i}. {category}\n"
            if len(categories) > 10:
                message += f"... 还有 {len(categories) - 10} 个板块\n"
        else:
            message += "⚠️ 暂无板块分类数据\n"
        
        message += "\n" + "=" * 30
        message += f"\n⚡ **数据来源**: 本地映射表"
        if last_updated != 'N/A':
            message += f"\n🕒 **更新时间**: {last_updated}"
        message += f"\n💡 使用 `/ticker {ticker}` 再次查询"
        
        # 发送消息（不需要编辑，直接发送）
        await update.message.reply_text(message, parse_mode="Markdown")
        
    except Exception as e:
        error_text = f"❌ 查询出错: `{str(e)}`\n\n💡 请稍后重试或联系管理员"
        await update.message.reply_text(error_text, parse_mode="Markdown")
