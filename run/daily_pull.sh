#!/bin/bash
# daily_pull.sh - 每日币种信息拉取脚本
# 专为服务器定时任务设计

set -e  # 遇到错误立即退出

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$SCRIPT_DIR/logs"
BACKUP_DIR="$PROJECT_DIR/backups"

# 创建必要目录
mkdir -p "$LOG_DIR"
mkdir -p "$BACKUP_DIR"

# 切换到项目目录
cd "$PROJECT_DIR"

# 设置日志文件
LOG_FILE="$LOG_DIR/daily_pull_$(date +%Y%m%d).log"
echo "========================================" | tee -a "$LOG_FILE"
echo "🚀 TaoTrader 每日币种信息完全重建开始" | tee -a "$LOG_FILE"
echo "📅 开始时间: $(date)" | tee -a "$LOG_FILE"
echo "📁 工作目录: $PROJECT_DIR" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 检查Python环境
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到Python环境" | tee -a "$LOG_FILE"
    exit 1
fi

echo "🐍 使用Python: $PYTHON_CMD" | tee -a "$LOG_FILE"

# 激活虚拟环境（如果存在）
if [ -f "venv/bin/activate" ]; then
    echo "🔧 激活虚拟环境..." | tee -a "$LOG_FILE"
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    echo "🔧 激活虚拟环境..." | tee -a "$LOG_FILE"
    source .venv/bin/activate
fi

# 检查依赖
echo "📦 检查依赖..." | tee -a "$LOG_FILE"
$PYTHON_CMD -c "import requests, pandas" 2>/dev/null || {
    echo "❌ 缺少必要依赖，尝试安装..." | tee -a "$LOG_FILE"
    pip install requests pandas >> "$LOG_FILE" 2>&1 || {
        echo "❌ 依赖安装失败" | tee -a "$LOG_FILE"
        exit 1
    }
}

# 执行完全重建
echo "🔄 开始完全重建映射表..." | tee -a "$LOG_FILE"
start_time=$(date +%s)

$PYTHON_CMD run/pull_coin_info.py >> "$LOG_FILE" 2>&1
exit_code=$?

end_time=$(date +%s)
duration=$((end_time - start_time))

# 记录结果
echo "========================================" | tee -a "$LOG_FILE"
echo "📊 执行结果:" | tee -a "$LOG_FILE"
echo "⏱️ 总耗时: ${duration}秒 ($(($duration / 60))分钟)" | tee -a "$LOG_FILE"
echo "🔢 退出码: $exit_code" | tee -a "$LOG_FILE"

if [ $exit_code -eq 0 ]; then
    echo "🎉 映射表完全重建成功!" | tee -a "$LOG_FILE"
    
    # 检查生成的文件
    if [ -f "coin_mapping_table.csv" ]; then
        line_count=$(wc -l < coin_mapping_table.csv)
        file_size=$(du -h coin_mapping_table.csv | cut -f1)
        echo "📋 映射表统计: $((line_count - 1)) 个币种, 文件大小: $file_size" | tee -a "$LOG_FILE"
    fi
    
elif [ $exit_code -eq 1 ]; then
    echo "⚠️ 映射表重建部分成功，有部分失败" | tee -a "$LOG_FILE"
    
else
    echo "❌ 映射表重建失败!" | tee -a "$LOG_FILE"
    
    # 可选：发送告警通知
    # echo "TaoTrader数据拉取失败，请检查日志: $LOG_FILE" | mail -s "TaoTrader Alert" admin@example.com
fi

# 清理旧日志（保留最近7天）
find "$LOG_DIR" -name "pull_coin_info_*.log" -mtime +7 -delete 2>/dev/null || true

# 清理旧备份（保留最近30天）
find "$BACKUP_DIR" -name "coin_mapping_*.csv" -mtime +30 -delete 2>/dev/null || true

echo "🕒 结束时间: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 显示最后几行日志作为摘要
echo ""
echo "📋 执行摘要:"
tail -n 20 "$LOG_FILE" | grep -E "(成功|失败|错误|完成|统计)"

exit $exit_code
