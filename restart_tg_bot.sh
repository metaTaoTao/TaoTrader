#!/bin/bash

echo "🔁 Restarting TG Bot..."

# 设置虚拟环境的 Python 路径
PYTHON_BIN="/home/tzhangfmz/TaoTrader/venv/bin/python"
BOT_SCRIPT="run/run_tg_bot.py"
LOG_FILE="run/logs/log_bot.txt"

# 杀掉旧的 TG Bot 进程（如果有）
echo "🛑 Killing old bot process (if any)..."
pkill -f $BOT_SCRIPT

# 启动新的 TG Bot
echo "🚀 Starting new bot process..."
nohup $PYTHON_BIN $BOT_SCRIPT > $LOG_FILE 2>&1 &

# 输出启动状态
sleep 2
ps aux | grep $BOT_SCRIPT | grep -v grep

echo "✅ TG Bot restarted successfully."
