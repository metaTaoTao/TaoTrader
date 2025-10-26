#!/bin/bash
# 服务器上设置 Grok API Key 的脚本

echo "=========================================="
echo "🚀 Grok API 设置脚本"
echo "=========================================="
echo ""

# 检查是否提供了 API Key
if [ -z "$1" ]; then
    echo "❌ 请提供 Grok API Key"
    echo ""
    echo "使用方法:"
    echo "  bash server_setup_grok.sh <your_grok_api_key>"
    echo ""
    echo "示例:"
    echo "  bash server_setup_grok.sh grok-xxxxxxxxxxxx"
    exit 1
fi

API_KEY=$1

echo "📝 设置步骤："
echo ""
echo "步骤 1: 设置环境变量"
echo "----------------------------------------"

# 检查 ~/.bashrc 是否已有该配置
if grep -q "GROK_API_KEY" ~/.bashrc; then
    echo "⚠️  检测到已有 GROK_API_KEY 配置，将更新..."
    sed -i '/export GROK_API_KEY=.*/d' ~/.bashrc
fi

# 添加 API Key 到 ~/.bashrc
echo "export GROK_API_KEY=\"$API_KEY\"" >> ~/.bashrc

echo "✅ 已添加到 ~/.bashrc"
echo ""

echo "步骤 2: 重新加载环境变量"
echo "----------------------------------------"
source ~/.bashrc
echo "✅ 环境变量已加载"
echo ""

echo "步骤 3: 验证配置"
echo "----------------------------------------"
if [ -z "$GROK_API_KEY" ]; then
    echo "❌ 环境变量加载失败"
    exit 1
else
    echo "✅ GROK_API_KEY 已设置"
    echo "📋 Key: ${GROK_API_KEY:0:20}..."
fi
echo ""

echo "步骤 4: 测试 API 连接"
echo "----------------------------------------"
cd ~/TaoTrader
source venv/bin/activate

python test_grok_api.py

echo ""
echo "=========================================="
echo "✅ 设置完成！"
echo "=========================================="
echo ""
echo "现在可以使用以下命令进行自动分析了："
echo "  python run/grok_event_analyzer.py 1h --auto"
echo ""

