# 服务器上配置 Grok API 完整指南

## 📋 前置条件

1. 已经获取了 Grok API Key（从 https://console.x.ai 获取）
2. 已经克隆项目到服务器上

## 🚀 快速设置（推荐）

```bash
# 在本地下载并上传 setup 脚本
# 或直接在服务器上创建

# 复制并运行设置脚本
bash server_setup_grok.sh <your_grok_api_key>
```

**示例：**
```bash
bash server_setup_grok.sh grok-xxxxxxxxxxxxxxxxxxxxxxxxx
```

## 📝 手动设置步骤

### 步骤 1: SSH 连接到服务器

```bash
ssh taozhangquant1@taotrader-scanner-sg
```

### 步骤 2: 设置环境变量

```bash
# 编辑 bashrc
nano ~/.bashrc

# 在文件末尾添加以下行（替换为你的真实 API Key）
export GROK_API_KEY="grok-xxxxxxxxxxxxxxxxxxxxxxxxx"

# 保存并退出（Ctrl+O, Enter, Ctrl+X）

# 重新加载配置
source ~/.bashrc

# 验证
echo $GROK_API_KEY
```

### 步骤 3: 测试 API 连接

```bash
cd ~/TaoTrader
source venv/bin/activate

# 测试连接
python test_grok_api.py
```

如果看到 "✅ API 连接成功！"，说明配置正确。

### 步骤 4: 运行自动分析

```bash
# 先运行扫描器获取最新涨幅榜
python run/event_monitor.py 1h 20

# 然后运行 Grok 自动分析
python run/grok_event_analyzer.py 1h --auto

# 或者分析前20名
python run/grok_event_analyzer.py 1h --auto 20
```

## 🕒 设置定时任务

设置每2小时自动扫描和分析：

```bash
# 编辑 crontab
crontab -e

# 添加以下行
0 0,2,4,6,8,10,12,14,16,18,20,22 * * * cd ~/TaoTrader && source venv/bin/activate && python run/event_monitor.py 1h 20 && python run/grok_event_analyzer.py 1h --auto >> ~/grok_analysis.log 2>&1

# 查看日志
tail -f ~/grok_analysis.log
```

## 📁 输出文件位置

- 涨幅榜数据：`output/leaders_1h.pkl`
- 分析结果：`output/grok_analysis_YYYYMMDD_HHMMSS.txt`

## 🔍 故障排查

### 问题1: "未设置 GROK_API_KEY 环境变量"

```bash
# 检查环境变量
echo $GROK_API_KEY

# 如果没有输出，重新加载
source ~/.bashrc

# 或者在命令前直接设置
GROK_API_KEY="grok-xxx" python run/grok_event_analyzer.py 1h --auto
```

### 问题2: "API 连接失败"

```bash
# 测试网络连接
curl https://api.x.ai/v1

# 检查 API Key 是否有效
python test_grok_api.py

# 查看详细错误
python run/grok_event_analyzer.py 1h --auto 2>&1 | tee debug.log
```

### 问题3: "没有找到数据"

```bash
# 先运行扫描器
python run/event_monitor.py 1h 20

# 检查数据文件是否存在
ls -lh output/leaders_1h.pkl

# 如果文件不存在，检查扫描日志
```

## 💡 使用技巧

### 临时分析（不保存结果）

```bash
python run/grok_event_analyzer.py 1h --auto
```

### 分析更多币种

```bash
python run/grok_event_analyzer.py 1h --auto 50  # 分析前50名
```

### 查看最新分析结果

```bash
ls -lt output/grok_analysis_*.txt | head -1
cat $(ls -t output/grok_analysis_*.txt | head -1)
```

## 📊 完整的自动化工作流

```bash
#!/bin/bash
# 完整的自动化脚本

cd ~/TaoTrader
source venv/bin/activate

# 1. 扫描涨幅榜
echo "📊 开始扫描涨幅榜..."
python run/event_monitor.py 1h 20

# 2. Grok 分析
echo "🤖 开始 Grok 事件驱动分析..."
python run/grok_event_analyzer.py 1h --auto

# 3. 发送通知（可选）
# 可以结合 Discord Bot 发送分析结果
```

## 🔗 相关文档

- [Grok API 文档](https://docs.x.ai/)
- [获取 API Key](https://console.x.ai/)
- [项目 README](../README.md)

