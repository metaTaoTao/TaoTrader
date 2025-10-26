# Grok API 集成指南

## 📋 如何获取 Grok API Key

### 步骤1: 访问 Grok 官网
1. 打开浏览器，访问 [https://x.ai](https://x.ai)
2. 点击 "Sign Up" 注册账户（需要 OpenAI 账号或 X/Twitter 账号）

### 步骤2: 获取 API Key
1. 登录后，访问 [https://console.x.ai](https://console.x.ai)
2. 点击 "API Keys" 或 "API" 菜单
3. 点击 "Create New Key" 创建新的 API Key
4. 复制 API Key（只显示一次，请妥善保存）

### 步骤3: 设置环境变量

**在本地（Windows）:**
```bash
# 创建 .env 文件
echo GROK_API_KEY=your_api_key_here > .env
```

**在服务器（Linux）:**
```bash
# 编辑环境变量文件
nano ~/.bashrc

# 添加以下行
export GROK_API_KEY="your_api_key_here"

# 重新加载
source ~/.bashrc
```

**或使用 systemd 服务配置:**
编辑 service 文件中的 `Environment` 部分：
```ini
[Service]
Environment="GROK_API_KEY=your_api_key_here"
```

## 🚀 使用方法

### 方法1: 自动调用 Grok API（推荐）

```bash
# 1. 先运行扫描器获取最新数据
python run/event_monitor.py 1h 20

# 2. 自动调用 Grok API 分析
python run/grok_event_analyzer.py 1h --auto
```

### 方法2: 手动复制到 Grok（不需要 API Key）

```bash
# 1. 运行扫描器
python run/event_monitor.py 1h 20

# 2. 生成分析提示词（不调用 API）
python run/grok_event_analyzer.py 1h

# 3. 复制输出内容，到 Grok 官网手动粘贴分析
```

## 📝 安装依赖（如果需要）

```bash
# 如果提示缺少依赖
pip install requests python-dotenv
```

## ⚙️ 定时任务设置

设置每2小时自动扫描和分析：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每2小时运行一次）
0 0,2,4,6,8,10,12,14,16,18,20,22 * * * cd ~/TaoTrader && source venv/bin/activate && python run/event_monitor.py 1h 20 && python run/grok_event_analyzer.py 1h --auto >> ~/grok_analysis.log 2>&1
```

## 🔧 文件说明

- `utils/grok_client.py` - Grok API 客户端
- `run/grok_event_analyzer.py` - 事件分析主程序
- `run/event_monitor.py` - 涨幅榜扫描器

## 💡 输出示例

```
================================================================================
🤖 Grok 分析结果
================================================================================

基于当前的24h涨幅榜数据，我进行了以下分析：

1. **市场催化剂识别**
   - ZEC (+29.52%): 可能受到隐私币板块整体上涨推动
   - ZEN (+21.39%): 同样属于隐私币板块，存在联动效应
   
2. **板块关联性**
   - 前3名均为隐私币（ZEC, ZEN, DASH）
   - 表明隐私币板块正在经历强势上涨
   
3. **趋势可持续性**
   - 成交额较高，有真实资金流入
   - 建议关注后续动量是否延续
   
4. **风险提示**
   - 涨幅过大可能引发回调
   - 请控制仓位，设置止损
```

