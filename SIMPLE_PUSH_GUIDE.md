# 简化推送方案使用指南

## 🎯 **方案概述**

### 📊 **推送策略**
- **频率**：每小时推送一次（整点推送）
- **内容**：前10名相对强弱排行
- **时间**：每小时00分推送

### 💬 **命令策略**
- **细粒度查询**：支持15分钟、1小时、4小时等
- **详细分析**：查看具体币种的详细评分

## 🚀 **使用方法**

### 1. **启动命令Bot**
```bash
python run/run_discord_bot.py
```

### 2. **启动推送调度器**
```bash
# 设置推送频道ID
export DISCORD_ALERT_CHANNEL_ID="你的频道ID"

# 启动推送调度器
python run/discord_alert_scheduler.py
```

## 📋 **推送内容示例**

```
📊 相对强弱排行推送
前 10 名币种相对强弱排行

🏆 相对强弱排行
🥇 1. BTCUSDT - 0.856
🥈 2. ETHUSDT - 0.823
🥉 3. ANIMEUSDT - 0.798
📊 4. MEUSDT - 0.765
📊 5. SOLUSDT - 0.742
...

📋 详细信息
• 时间周期: 1h
• 扫描时间: 2025-10-03 11:00:00
• 推送时间: 11:00

💡 快速查询
• /score <symbol> 1h - 查看详细评分
• /ticker <symbol> - 查看币种信息
• /scan final 1h - 查看完整排行
```

## 🔧 **命令支持的时间周期**

### 支持的时间周期
- **15m** - 15分钟
- **1h** - 1小时
- **4h** - 4小时
- **1d** - 1天

### 命令示例
```
/score BTCUSDT 15m    # 查看BTC的15分钟评分
/score ETHUSDT 4h     # 查看ETH的4小时评分
/scan final 1h        # 查看1小时综合排行
/scan return 4h       # 查看4小时涨跌幅排行
```

## ⚙️ **配置选项**

### 推送配置
```python
alert_config = {
    'top_n': 10,                # 推送前10名
    'timeframe': '1h',          # 推送时间周期
    'push_interval': 60         # 推送间隔（分钟）
}
```

### 修改配置
编辑 `run/discord_alert_scheduler.py` 中的配置：
```python
# 推送配置
alert_config = {
    'top_n': 15,                # 改为推送前15名
    'timeframe': '1h',          # 推送时间周期
    'push_interval': 60         # 推送间隔（分钟）
}
```

## 📊 **推送时间表**

| 时间 | 推送内容 |
|------|----------|
| 00:00 | 前10名相对强弱排行 |
| 01:00 | 前10名相对强弱排行 |
| 02:00 | 前10名相对强弱排行 |
| ... | ... |
| 23:00 | 前10名相对强弱排行 |

## 🎯 **优势**

### ✅ **推送优势**
- **定时推送**：每小时自动推送，不错过重要信息
- **相对强弱**：基于相对评分，无绝对阈值
- **简洁明了**：只推送前10名，信息精炼

### ✅ **命令优势**
- **细粒度查询**：支持15分钟到1天的多种时间周期
- **详细分析**：可以查看具体币种的详细评分
- **按需查询**：用户主动查询，不打扰

## 🚀 **启动步骤**

### 1. **准备环境**
```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DISCORD_BOT_TOKEN="你的Bot Token"
export DISCORD_ALERT_CHANNEL_ID="你的频道ID"
```

### 2. **启动服务**
```bash
# 终端1：启动命令Bot
python run/run_discord_bot.py

# 终端2：启动推送调度器
python run/discord_alert_scheduler.py
```

### 3. **测试功能**
- 在Discord中测试命令：`/help`
- 等待整点推送测试

## 📞 **支持**

如有问题或建议，请联系管理员。
