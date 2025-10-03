# bot_command/discord_score_command.py

import discord
import sys
import os
import pandas as pd

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_helper import DataIO

async def score_command(interaction, symbol: str, timeframe: str = "1h"):
    """
    Discord Bot score查询命令
    用法: /score ETHUSDT 1h 或 !score ETHUSDT 1h
    """
    try:
        if not symbol:
            embed = discord.Embed(
                title="❗ 用法示例",
                description="`/score ETHUSDT 1h` 或 `!score ETHUSDT 1h`",
                color=0xff0000
            )
            embed.add_field(
                name="📝 参数说明",
                value=(
                    "• 第一个参数：币种符号（如：ETHUSDT）\n"
                    "• 第二个参数：时间周期（可选，默认为1h）"
                ),
                inline=False
            )
            embed.add_field(
                name="💡 示例",
                value="`/score BTCUSDT 4h`",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return

        symbol = symbol.upper()
        timeframe = timeframe.lower()

        # 加载评分数据
        try:
            data_obj = DataIO.load(f'scores_{timeframe}')
            if isinstance(data_obj, dict) and "data" in data_obj:
                df = data_obj["data"]
                timestamp = data_obj.get("timestamp", "")
            else:
                # 如果数据直接是DataFrame
                df = data_obj
                timestamp = ""
        except Exception as e:
            embed = discord.Embed(
                title="❌ 数据加载失败",
                description=f"无法加载 {timeframe} 时间段的评分数据",
                color=0xff0000
            )
            embed.add_field(
                name="🔍 可能原因",
                value=(
                    "• 评分数据文件不存在\n"
                    "• 数据文件格式错误\n"
                    "• 文件路径问题"
                ),
                inline=False
            )
            embed.add_field(
                name="💡 解决方案",
                value="请联系管理员检查评分数据",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return

        # 查找指定币种的评分
        row = df[df["symbol"] == symbol]

        if row.empty:
            embed = discord.Embed(
                title=f"⚠️ 未找到 {symbol} 的评分数据",
                description=f"在 `{timeframe.upper()}` 时间段未找到该币种的评分",
                color=0xffaa00
            )
            embed.add_field(
                name="🔍 可能原因",
                value=(
                    "• 该币种不在评分列表中\n"
                    "• 评分数据未更新\n"
                    "• 币种符号拼写错误"
                ),
                inline=False
            )
            embed.add_field(
                name="💡 建议",
                value=(
                    "• 检查币种符号是否正确\n"
                    "• 尝试其他时间周期\n"
                    "• 使用 `/scan` 查看所有评分"
                ),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return

        row = row.iloc[0]
        
        # 构建Discord Embed
        embed = discord.Embed(
            title=f"📈 {symbol} 评分详情",
            description=f"时间周期：`{timeframe.upper()}`",
            color=0x00ff00
        )
        
        # 综合评分（突出显示）
        final_score = row['final_score']
        score_color = 0x00ff00 if final_score >= 0.7 else 0xffaa00 if final_score >= 0.4 else 0xff0000
        embed.add_field(
            name="🧠 综合评分",
            value=f"`{final_score:.3f}`",
            inline=True
        )
        
        # 各项子评分
        embed.add_field(
            name="📈 涨跌幅评分",
            value=f"`{row['return_score']:.3f}`",
            inline=True
        )
        embed.add_field(
            name="📊 趋势评分",
            value=f"`{row['ema_score']:.3f}`",
            inline=True
        )
        embed.add_field(
            name="📉 成交量评分",
            value=f"`{row['volume_score']:.3f}`",
            inline=True
        )
        embed.add_field(
            name="📉 RSI 反转信号",
            value=f"`{row['rsi_score']:.3f}`",
            inline=True
        )
        embed.add_field(
            name="🧮 Alpha评分",
            value=f"`{row['momentum_score']:.3f}`",
            inline=True
        )
        
        # 评分说明
        embed.add_field(
            name="📋 评分说明",
            value=(
                "• **综合评分**：平衡所有因素的最终评分\n"
                "• **涨跌幅评分**：基于价格变动的评分\n"
                "• **趋势评分**：基于EMA趋势的评分\n"
                "• **成交量评分**：基于交易热度的评分\n"
                "• **RSI评分**：基于超买/超卖信号的评分\n"
                "• **Alpha评分**：剥离Beta后的相对收益评分"
            ),
            inline=False
        )
        
        # 数据时间戳
        if timestamp:
            embed.add_field(
                name="🕒 最新评分时间",
                value=f"`{timestamp}`",
                inline=True
            )
        
        embed.add_field(
            name="💡 再次查询",
            value=f"`/score {symbol} {timeframe}`",
            inline=True
        )
        
        embed.set_footer(
            text="TaoTrader Bot | 评分仅供参考，投资需谨慎",
            icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png"
        )
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ 查询出错",
            description=f"```{str(e)}```",
            color=0xff0000
        )
        error_embed.add_field(
            name="💡 解决方案",
            value="请稍后重试或联系管理员",
            inline=False
        )
        
        try:
            await interaction.response.send_message(embed=error_embed)
        except:
            await interaction.response.send_message(f"❌ 查询出错: {str(e)}\n\n💡 请稍后重试或联系管理员")
