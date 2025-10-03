# bot_command/discord_scan_command.py

import discord
import sys
import os
import io
from tabulate import tabulate

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_helper import DataIO

async def scan_command(interaction, score_type: str = "final", timeframe: str = "1h"):
    """
    Discord Bot scan查询命令
    用法: /scan final 1h 或 !scan final 1h
    """
    try:
        # 验证评分类型
        valid_score_types = ['final', 'return', 'ema', 'volume', 'rsi', 'momentum']
        if score_type not in valid_score_types:
            embed = discord.Embed(
                title="⚠️ 无效的评分类型",
                description=f"`{score_type}` 不是有效的评分类型",
                color=0xffaa00
            )
            embed.add_field(
                name="📋 可选的评分类型",
                value="\n".join([f"• `{t}`" for t in valid_score_types]),
                inline=False
            )
            embed.add_field(
                name="💡 示例",
                value="`/scan final 1h`",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return

        sort_key = score_type + '_score'
        
        # 加载评分数据
        try:
            data_obj = DataIO.load(f'scores_{timeframe}')
            if isinstance(data_obj, dict) and "data" in data_obj:
                df = data_obj["data"]
                timestamp = data_obj.get("timestamp", "N/A")
            else:
                # 如果数据直接是DataFrame
                df = data_obj
                timestamp = "N/A"
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

        # 验证评分列是否存在
        if sort_key not in df.columns:
            embed = discord.Embed(
                title="⚠️ 无效的评分键",
                description=f"`{sort_key}` 不存在于数据中",
                color=0xffaa00
            )
            embed.add_field(
                name="📋 可用的评分列",
                value="\n".join([f"• `{col}`" for col in df.columns if col.endswith('_score')]),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return

        # 排序数据
        df_sorted = df.sort_values(sort_key, ascending=False).reset_index(drop=True)
        df_sorted.index += 1  # 排名从1开始

        # 创建预览表格（前10名）
        preview_table = tabulate(
            df_sorted[["symbol", sort_key]].head(10),
            headers=["Rank", "Symbol", "Score"],
            tablefmt="plain",
            showindex=True,
            floatfmt=".3f"
        )

        # 构建Discord Embed
        embed = discord.Embed(
            title=f"📊 Top 10 币种评分排行",
            description=f"评分类型：`{score_type}` | 时间周期：`{timeframe.upper()}`",
            color=0x00ff00
        )
        
        # 添加预览表格
        embed.add_field(
            name="🏆 排行榜预览",
            value=f"```\n{preview_table}\n```",
            inline=False
        )
        
        # 评分维度说明
        score_descriptions = {
            'final': '综合打分，平衡趋势、量能、情绪与基本面',
            'return': '涨跌幅评分（近 1h/4h/1d）',
            'ema': '趋势评分（EMA 多头排列判定）',
            'volume': '成交量评分（基于交易热度）',
            'rsi': 'RSI 反转信号（超买/超卖分数）',
            'momentum': 'Alpha评分（剥离Beta后的相对收益）'
        }
        
        embed.add_field(
            name="📌 当前评分维度",
            value=f"`{score_type}` - {score_descriptions.get(score_type, '未知评分类型')}",
            inline=False
        )
        
        # 数据时间戳
        if timestamp != "N/A":
            embed.add_field(
                name="🕒 扫描时间",
                value=f"`{timestamp}`",
                inline=True
            )
        
        embed.add_field(
            name="💡 再次查询",
            value=f"`/scan {score_type} {timeframe}`",
            inline=True
        )
        
        embed.set_footer(
            text="TaoTrader Bot | 完整榜单已作为文件发送",
            icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png"
        )
        embed.timestamp = discord.utils.utcnow()
        
        # 发送预览消息
        await interaction.response.send_message(embed=embed)

        # 创建完整榜单文件
        full_table = tabulate(
            df_sorted[["symbol", sort_key]],
            headers=["Symbol", sort_key],
            tablefmt="plain",
            showindex=True,
            floatfmt=".3f"
        )
        
        # 创建文件内容
        file_content = f"""TaoTrader Bot - 币种评分排行榜
评分类型: {score_type}
时间周期: {timeframe.upper()}
扫描时间: {timestamp}

{full_table}

---
TaoTrader Bot | 数据仅供参考，投资需谨慎
"""
        
        # 创建文件对象
        file_obj = discord.File(
            io.StringIO(file_content),
            filename=f"top_{score_type}_{timeframe}.txt"
        )
        
        # 发送完整榜单文件
        followup_embed = discord.Embed(
            title="📎 完整排行榜",
            description=f"已附加完整榜单文件：`top_{score_type}_{timeframe}.txt`",
            color=0x0099ff
        )
        followup_embed.add_field(
            name="📊 统计信息",
            value=f"• 总币种数：{len(df_sorted)}\n• 评分类型：{score_type}\n• 时间周期：{timeframe.upper()}",
            inline=False
        )
        
        await interaction.followup.send(embed=followup_embed, file=file_obj)

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
