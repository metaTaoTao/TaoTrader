# bot_command/discord_alert_command.py

import discord
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_helper import DataIO

async def send_scan_alerts(bot, channel_id, alert_config=None):
    """
    发送扫描结果推送
    """
    if not alert_config:
        alert_config = {
            'top_n': 10,       # 推送前N名
            'timeframe': '1h'  # 时间周期
        }
    
    try:
        # 加载评分数据
        import os
        print(f"当前工作目录: {os.getcwd()}")
        print(f"正在加载: scores_{alert_config['timeframe']}")
        
        data_obj = DataIO.load(f'scores_{alert_config["timeframe"]}')
        if isinstance(data_obj, dict) and "data" in data_obj:
            df = data_obj["data"]
            timestamp = data_obj.get("timestamp", "N/A")
        else:
            # 如果数据直接是DataFrame
            df = data_obj
            timestamp = "N/A"
        
        print(f"数据形状: {df.shape}")
        print(f"前3名币种: {df.nlargest(3, 'final_score')['symbol'].tolist()}")
        
        # 获取前N名币种（相对强弱排行）
        top_coins = df.nlargest(alert_config['top_n'], 'final_score')
        
        if top_coins.empty:
            return
        
        # 构建推送消息
        embed = discord.Embed(
            title="📊 相对强弱排行推送",
            description=f"前 {len(top_coins)} 名币种相对强弱排行",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        # 添加排行榜
        top_list = []
        for i, (_, row) in enumerate(top_coins.iterrows(), 1):
            score = row['final_score']
            symbol = row['symbol']
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
            top_list.append(f"{emoji} **{i}.** `{symbol}` - `{score:.3f}`")
        
        embed.add_field(
            name="🏆 相对强弱排行",
            value="\n".join(top_list),
            inline=False
        )
        
        # 添加详细信息
        embed.add_field(
            name="📋 详细信息",
            value=(
                f"• 时间周期: `{alert_config['timeframe']}`\n"
                f"• 扫描时间: `{timestamp}`\n"
                f"• 推送时间: `{datetime.now().strftime('%H:%M')}`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 快速查询",
            value=(
                "• `/score <symbol> {timeframe}` - 查看详细评分\n"
                "• `/ticker <symbol>` - 查看币种信息\n"
                "• `/scan final {timeframe}` - 查看完整排行"
            ).format(timeframe=alert_config['timeframe']),
            inline=False
        )
        
        embed.set_footer(
            text="TaoTrader Bot | 数据仅供参考，投资需谨慎",
            icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png"
        )
        
        # 发送到指定频道
        channel = bot.get_channel(channel_id)
        if channel:
            print(f"📤 正在发送推送到频道: {channel.name} (ID: {channel_id})")
            await channel.send(embed=embed)
            print(f"✅ 推送发送成功")
        else:
            print(f"❌ 找不到频道 ID: {channel_id}")
            
    except Exception as e:
        print(f"❌ 推送失败: {e}")
        import traceback
        traceback.print_exc()

