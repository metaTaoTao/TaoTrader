# Discord Bot 使用指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 创建Discord Bot

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 点击 "New Application" 创建新应用
3. 在 "Bot" 页面创建Bot
4. 复制Bot Token
5. 在 "OAuth2" > "URL Generator" 中生成邀请链接

### 3. 设置环境变量

```bash
# Windows (PowerShell)
$env:DISCORD_BOT_TOKEN="your_bot_token_here"

# Linux/Mac
export DISCORD_BOT_TOKEN="your_bot_token_here"
```

### 4. 启动Bot

```bash
# 使用启动脚本
./run/discord_bot_start.sh

# 或直接运行
python run/run_discord_bot.py
```

## 📋 命令列表

### Slash命令（推荐）

- `/help` - 显示帮助信息
- `/ticker <symbol>` - 查询币种信息
- `/score <symbol> [timeframe]` - 查询币种评分
- `/scan [score_type] [timeframe]` - 显示评分排行榜

### 传统命令

- `!help` - 显示帮助信息
- `!ticker <symbol>` - 查询币种信息
- `!score <symbol> [timeframe]` - 查询币种评分
- `!scan [score_type] [timeframe]` - 显示评分排行榜

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DISCORD_BOT_TOKEN` | Discord Bot Token | ✅ |

### 配置文件

配置文件位于 `configs/discord_bot.yaml`，包含以下设置：

- Bot基本设置
- 日志配置
- 数据文件路径
- 错误处理
- 消息格式
- 功能开关

## 📊 功能特性

### 1. 币种查询 (`/ticker`)

- 查询币种基本信息
- 显示市值、FDV、交易量
- 展示板块分类
- 24小时涨跌幅

**示例：**
```
/ticker BTCUSDT
/ticker ETHUSDT
```

### 2. 评分查询 (`/score`)

- 查询特定币种的详细评分
- 显示各项子评分
- 支持多个时间周期

**示例：**
```
/score BTCUSDT 1h
/score ETHUSDT 4h
```

### 3. 排行榜 (`/scan`)

- 显示币种评分排行榜
- 支持多种评分维度
- 提供完整榜单文件下载

**示例：**
```
/scan final 1h
/scan return 4h
/scan momentum 1d
```

### 4. 帮助信息 (`/help`)

- 显示所有可用命令
- 提供使用示例
- 说明支持的格式

## 🛠️ 开发说明

### 项目结构

```
bot_command/
├── discord_help_command.py    # 帮助命令
├── discord_ticker_command.py  # 币种查询命令
├── discord_score_command.py   # 评分查询命令
└── discord_scan_command.py    # 排行榜命令

run/
├── run_discord_bot.py         # Bot主文件
└── discord_bot_start.sh       # 启动脚本

configs/
└── discord_bot.yaml           # 配置文件
```

### 添加新命令

1. 在 `bot_command/` 目录创建新命令文件
2. 在 `run/run_discord_bot.py` 中注册命令
3. 更新帮助信息

### 错误处理

- 所有命令都有完整的错误处理
- 错误信息会记录到日志文件
- 用户友好的错误提示

## 📝 日志记录

日志文件：`discord_bot.log`

包含：
- Bot启动/停止信息
- 命令执行记录
- 错误信息
- 性能统计

## 🔒 安全建议

1. **保护Bot Token**
   - 不要将Token提交到代码仓库
   - 使用环境变量存储Token
   - 定期轮换Token

2. **权限控制**
   - 只给Bot必要的权限
   - 限制Bot访问的服务器
   - 监控Bot活动

3. **数据安全**
   - 定期备份数据文件
   - 保护敏感配置信息
   - 监控异常活动

## 🚨 故障排除

### 常见问题

1. **Bot无法启动**
   - 检查Token是否正确
   - 确认依赖已安装
   - 查看日志文件

2. **命令无响应**
   - 检查Bot权限
   - 确认命令格式正确
   - 查看错误日志

3. **数据查询失败**
   - 确认数据文件存在
   - 检查文件权限
   - 验证数据格式

### 调试模式

设置环境变量启用详细日志：

```bash
export DISCORD_BOT_DEBUG=true
```

## 📞 支持

如有问题或建议，请联系管理员或查看项目文档。

---

**注意：** 所有数据仅供参考，投资需谨慎。
