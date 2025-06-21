#!/bin/bash
set -e

MODE=$1

if [ "$MODE" = "run_bot" ]; then
    echo "🚀 Starting Telegram Bot..."
    python run/run_tg_bot.py
elif [ "$MODE" = "run_scan" ]; then
    echo "🔁 Running market scanner..."
    python run/run_scanner.py --once
else
    echo "❌ Unknown mode: $MODE"
    exit 1
fi
