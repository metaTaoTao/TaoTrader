# bot_command/discord_help_command.py

import discord
from discord import app_commands

async def help_command(interaction):
    """
    Discord Bot帮助命令
    显示所有可用的命令和用法
    """
    embed = discord.Embed(
        title="🤖 TaoTrader Bot 使用指南",
        description="专业的加密货币分析工具",
        color=0x00ff00
    )
    
    # 币种查询命令
    embed.add_field(
        name="🔍 币种查询命令",
        value=(
            "• `/ticker ANIMEUSDT` - 查询币种详细信息\n"
            "  包含市值、板块分类、24h涨跌幅等数据\n"
            "  ⚡ 数据来源：本地映射表（每日更新，响应极快）"
        ),
        inline=False
    )
    
    # 评分系统命令
    embed.add_field(
        name="📊 评分系统命令",
        value=(
            "• `/scan final 1h` - 显示评分排行榜\n"
            "  可选参数：评分类型 (final/return/ema/volume/rsi/momentum) 和时间周期 (1h/4h/1d)\n\n"
            "• `/score ETHUSDT 1h` - 查询特定币种的评分\n"
            "  显示综合评分和各项子评分"
        ),
        inline=False
    )
    
    # 帮助命令
    embed.add_field(
        name="🆘 帮助命令",
        value="• `/help` - 显示此帮助信息",
        inline=False
    )
    
    # 支持的ticker格式
    embed.add_field(
        name="📍 支持的ticker格式",
        value=(
            "• Binance格式：`BTCUSDT`, `ETHUSDT`, `ANIMEUSDT`\n"
            "• OKX格式：`BTC-USDT`, `ETH-USDT`, `ANIME-USDT`"
        ),
        inline=False
    )
    
    # 使用示例
    embed.add_field(
        name="💡 使用示例",
        value=(
            "• `/ticker MEUSDT` - 查询Magic Eden币种信息\n"
            "• `/scan final 1h` - 查看1小时综合评分排行\n"
            "• `/score BTCUSDT 4h` - 查看BTC的4小时评分详情"
        ),
        inline=False
    )
    
    # 注意事项
    embed.add_field(
        name="⚡ 注意事项",
        value=(
            "• ticker查询从本地映射表读取，响应极快\n"
            "• 映射表数据每日更新，确保信息准确性\n"
            "• 评分数据基于历史扫描结果\n"
            "• 所有数据仅供参考，投资需谨慎"
        ),
        inline=False
    )
    
    # 更新频率
    embed.add_field(
        name="🔄 更新频率",
        value=(
            "• 币种信息：每日更新（本地映射表）\n"
            "• 评分数据：定时更新"
        ),
        inline=False
    )
    
    # 数据管理
    embed.add_field(
        name="📋 数据管理",
        value=(
            "• 使用 `python update_mapping_table.py --file tickers.txt` 更新映射表\n"
            "• 映射表包含市值、板块、价格变动等完整信息"
        ),
        inline=False
    )
    
    # 传统命令支持
    embed.add_field(
        name="💬 传统命令支持",
        value=(
            "• `!help` - 显示帮助信息\n"
            "• `!ticker BTCUSDT` - 查询币种信息\n"
            "• `!score BTCUSDT 1h` - 查询评分\n"
            "• `!scan final 1h` - 显示排行榜"
        ),
        inline=False
    )
    
    embed.set_footer(
        text="📞 如有问题或建议，请联系管理员",
        icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png"
    )
    
    embed.timestamp = discord.utils.utcnow()
    
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.followup.send(embed=embed)
    except Exception as e:
        # 如果embed发送失败，发送纯文本版本
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

💬 **传统命令支持**:
• `!help` - 显示帮助信息
• `!ticker BTCUSDT` - 查询币种信息
• `!score BTCUSDT 1h` - 查询评分
• `!scan final 1h` - 显示排行榜

📞 如有问题或建议，请联系管理员。"""
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(help_text)
            else:
                await interaction.followup.send(help_text)
        except:
            # 最后尝试发送到频道
            await interaction.channel.send(help_text)
