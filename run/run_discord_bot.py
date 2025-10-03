#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot 主运行文件
实现与Telegram Bot相同的命令交互功能
"""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import discord
from discord.ext import commands
from discord import app_commands

from bot_command.discord_help_command import help_command
from bot_command.discord_ticker_command import ticker_command
from bot_command.discord_score_command import score_command
from bot_command.discord_scan_command import scan_command
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaoTraderBot(commands.Bot):
    """TaoTrader Discord Bot"""
    
    def __init__(self):
        intents = discord.Intents.default()
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
    
    async def setup_hook(self):
        """Bot启动时的初始化"""
        logger.info("🚀 TaoTrader Discord Bot 正在启动...")
        
        # 同步slash命令
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ 已同步 {len(synced)} 个slash命令")
        except Exception as e:
            logger.error(f"❌ 同步slash命令失败: {e}")
    
    
    
    async def on_command_error(self, ctx, error):
        """命令错误处理"""
        if isinstance(error, commands.CommandNotFound):
            return  # 忽略未知命令
        
        logger.error(f"❌ 命令错误: {error}")
        
        embed = discord.Embed(
            title="❌ 命令执行错误",
            description=f"```{str(error)}```",
            color=0xff0000
        )
        embed.add_field(
            name="💡 提示",
            value="使用 `!help` 查看可用命令",
            inline=False
        )
        
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send(f"❌ 命令执行错误: {str(error)}")

# 创建Bot实例
bot = TaoTraderBot()

@bot.event
async def on_ready():
    """Bot准备就绪事件"""
    logger.info(f"✅ {bot.user} 已上线!")
    logger.info(f"📊 已连接到 {len(bot.guilds)} 个服务器")
    
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="加密货币市场 | !help"
    )
    await bot.change_presence(activity=activity)

# 注册slash命令
@bot.tree.command(name="help", description="显示所有可用的命令和用法")
async def slash_help(interaction: discord.Interaction):
    """Slash命令版本的help"""
    await help_command(interaction)

@bot.tree.command(name="ticker", description="查询币种详细信息")
@app_commands.describe(symbol="币种符号，如: BTCUSDT, ETHUSDT")
async def slash_ticker(interaction: discord.Interaction, symbol: str):
    """Slash命令版本的ticker查询"""
    await ticker_command(interaction, symbol)

@bot.tree.command(name="score", description="查询特定币种的评分")
@app_commands.describe(
    symbol="币种符号，如: BTCUSDT, ETHUSDT",
    timeframe="时间周期: 15m, 1h, 4h, 1d"
)
async def slash_score(interaction: discord.Interaction, symbol: str, timeframe: str = "1h"):
    """Slash命令版本的score查询"""
    await score_command(interaction, symbol, timeframe)

@bot.tree.command(name="scan", description="显示评分排行榜")
@app_commands.describe(
    score_type="评分类型: final, return, ema, volume, rsi, momentum",
    timeframe="时间周期: 15m, 1h, 4h, 1d"
)
async def slash_scan(interaction: discord.Interaction, score_type: str = "final", timeframe: str = "1h"):
    """Slash命令版本的scan查询"""
    await scan_command(interaction, score_type, timeframe)

# 传统命令支持（以!开头）
@bot.command(name='help')
async def cmd_help(ctx):
    """传统命令版本的help"""
    await help_command(ctx)

@bot.command(name='ticker')
async def cmd_ticker(ctx, *, symbol: str = None):
    """传统命令版本的ticker查询"""
    if not symbol:
        await ctx.send("❗ 用法示例：`!ticker BTCUSDT`")
        return
    await ticker_command(ctx, symbol)

@bot.command(name='score')
async def cmd_score(ctx, symbol: str = None, timeframe: str = "1h"):
    """传统命令版本的score查询"""
    if not symbol:
        await ctx.send("❗ 用法示例：`!score BTCUSDT 1h`")
        return
    await score_command(ctx, symbol, timeframe)

@bot.command(name='scan')
async def cmd_scan(ctx, score_type: str = "final", timeframe: str = "1h"):
    """传统命令版本的scan查询"""
    await scan_command(ctx, score_type, timeframe)

def main():
    """主函数"""
    # 从环境变量获取Discord Bot Token
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        logger.error("❌ 未找到DISCORD_BOT_TOKEN环境变量")
        logger.error("💡 请设置环境变量: export DISCORD_BOT_TOKEN='your_bot_token'")
        sys.exit(1)
    
    try:
        logger.info("🚀 启动TaoTrader Discord Bot...")
        bot.run(token)
    except discord.LoginFailure:
        logger.error("❌ Discord Bot Token无效")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Bot启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
