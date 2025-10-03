# TaoTrader

专业的加密货币交易分析系统，提供币种评分、板块分析、回测和实时交易功能。

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 数据准备

1. **更新币种映射表**（每日运行）：
```bash
python run/pull_coin_info.py
```

2. **手动更新特定币种**：
```bash
python update_mapping_table.py --tickers BTCUSDT ETHUSDT
```

### 启动服务

#### Telegram Bot
```bash
export TELEGRAM_BOT_TOKEN="your_token"
python run/run_tg_bot.py
```

#### Discord Bot
```bash
export DISCORD_BOT_TOKEN="your_token"
python run/run_discord_bot.py
```

#### 扫描器
```bash
python run/run_scanner.py
```

#### 回测
```bash
python run/run_backtest.py
```

## 📋 主要功能

### 1. 币种分析
- **板块分类**：自动识别币种所属板块
- **市场数据**：市值、FDV、交易量、涨跌幅
- **评分系统**：多维度综合评分

### 2. Bot命令
- `/ticker <symbol>` - 查询币种信息
- `/score <symbol> [timeframe]` - 查询评分
- `/scan [type] [timeframe]` - 排行榜
- `/help` - 帮助信息

### 3. 评分维度
- **综合评分**：平衡所有因素
- **涨跌幅评分**：基于价格变动
- **趋势评分**：基于EMA趋势
- **成交量评分**：基于交易热度
- **RSI评分**：超买/超卖信号
- **Alpha评分**：相对收益评分

## 🏗️ 项目结构

```
TaoTrader/
├── bot_command/          # Bot命令模块
├── data/                 # 数据获取模块
├── execution/            # 交易执行模块
├── indicators/           # 技术指标模块
├── strategies/           # 交易策略模块
├── score_system/         # 评分系统
├── run/                  # 运行脚本
├── configs/              # 配置文件
└── utils/                # 工具函数
```

## ⚙️ 配置

### 环境变量
- `TELEGRAM_BOT_TOKEN` - Telegram Bot Token
- `DISCORD_BOT_TOKEN` - Discord Bot Token
- `OKX_API_KEY` - OKX API密钥
- `OKX_SECRET_KEY` - OKX Secret密钥
- `OKX_PASSPHRASE` - OKX Passphrase

### 配置文件
- `configs/strategy/` - 策略配置
- `configs/execution/` - 交易配置
- `configs/risk.yaml` - 风控配置

## 📊 数据源

- **CoinGecko API**：币种信息、板块分类、市场数据
- **Binance API**：交易对信息、实时价格
- **OKX API**：交易执行、账户管理

## 🔧 开发

### 添加新策略
1. 在 `strategies/` 创建策略文件
2. 继承 `BaseStrategy` 类
3. 实现 `generate_signals` 方法
4. 在配置文件中注册策略

### 添加新指标
1. 在 `indicators/` 创建指标文件
2. 继承 `BaseIndicator` 类
3. 实现 `calculate` 方法

## 📝 日志

- Bot日志：`bot.log`
- 扫描日志：`scanner.log`
- 回测日志：`backtest.log`
- 数据拉取日志：`pull_coin_info_*.log`

## ⚠️ 注意事项

- 所有数据仅供参考，投资需谨慎
- 请妥善保管API密钥
- 建议在测试环境充分验证后再用于实盘
- 定期更新币种映射表以确保数据准确性

## 📞 支持

如有问题或建议，请联系管理员。
