#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot 推送调度器
定时推送扫描结果和重要发现
"""

import asyncio
import logging
import os
import sys
import time
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import discord
from discord.ext import commands

from bot_command.discord_alert_command import send_scan_alerts

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_alert.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlertScheduler:
    """推送调度器"""
    
    def __init__(self, bot_token, channel_id, alert_config=None):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.alert_config = alert_config or {
            'top_n': 10,
            'timeframe': '1h',
            'push_interval': 60
        }
        self.bot = None
        
    async def start_bot(self):
        """启动Bot"""
        intents = discord.Intents.default()
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        @self.bot.event
        async def on_ready():
            logger.info(f"✅ 推送Bot已上线: {self.bot.user}")
            logger.info(f"📋 推送频道: {self.channel_id}")
            
        await self.bot.start(self.bot_token)
    
    
    async def send_regular_alert(self):
        """发送常规推送"""
        try:
            await send_scan_alerts(
                self.bot, 
                self.channel_id, 
                self.alert_config
            )
            logger.info("✅ 常规推送已发送")
        except Exception as e:
            logger.error(f"❌ 常规推送失败: {e}")
    
    
    async def run_scheduler(self):
        """运行调度器"""
        logger.info("🚀 启动推送调度器...")
        logger.info(f"📊 推送频率: 每{self.alert_config['push_interval']}分钟")
        logger.info(f"📋 推送内容: 前{self.alert_config['top_n']}名相对强弱排行")
        
        # 启动Bot
        bot_task = asyncio.create_task(self.start_bot())
        
        # 等待Bot启动
        await asyncio.sleep(5)
        
        try:
            while True:
                current_time = datetime.now()
                
                # 每小时推送一次（整点推送）
                if current_time.minute == 0:
                    await self.send_regular_alert()
                    logger.info(f"✅ {current_time.strftime('%H:%M')} 推送完成")
                
                # 等待1分钟
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("⚠️ 用户中断调度器")
        except Exception as e:
            logger.error(f"❌ 调度器错误: {e}")
        finally:
            if self.bot:
                await self.bot.close()

def main():
    """主函数"""
    # 从环境变量获取配置
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    channel_id = int(os.getenv('DISCORD_ALERT_CHANNEL_ID', '0'))
    
    if not bot_token:
        logger.error("❌ 未设置DISCORD_BOT_TOKEN环境变量")
        return 1
    
    if not channel_id:
        logger.error("❌ 未设置DISCORD_ALERT_CHANNEL_ID环境变量")
        return 1
    
    # 推送配置
    alert_config = {
        'top_n': 10,                # 推送前N名
        'timeframe': '1h',          # 推送时间周期
        'push_interval': 60         # 推送间隔（分钟）
    }
    
    # 创建调度器
    scheduler = AlertScheduler(bot_token, channel_id, alert_config)
    
    # 运行调度器
    try:
        asyncio.run(scheduler.run_scheduler())
    except Exception as e:
        logger.error(f"❌ 调度器启动失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
