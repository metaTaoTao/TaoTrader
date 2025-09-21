# TaoTrader 项目结构说明

## 📁 核心币种数据模块

```
TaoTrader/
├── data/
│   └── sector_data.py              # 🎯 币种板块和市值数据获取
├── utils/
│   └── coingecko_helper.py         # 🔧 CoinGecko API限流处理
├── bot_command/
│   ├── ticker_command.py           # 📱 TG Bot ticker查询命令
│   ├── help_command.py             # 📱 TG Bot帮助命令
│   ├── scan_command.py             # 📱 TG Bot扫描命令（原有）
│   └── score_command.py            # 📱 TG Bot评分命令（原有）
└── run/
    ├── pull_coin_info.py           # 🕒 服务器定时拉取脚本
    ├── daily_pull.sh               # 🐧 Linux定时任务脚本
    └── run_tg_bot.py               # 📱 TG Bot启动脚本
```

## 🔧 工具和配置文件

```
├── update_mapping_table.py         # 🛠️ 映射表更新工具
├── generate_category_matrix.py     # 📊 数据分析矩阵生成器
├── tickers.json                    # 📄 币种列表（JSON格式）
├── tickers.txt                     # 📄 币种列表（文本格式）
├── requirements.txt                # 📦 Python依赖
└── coin_mapping_table.csv          # 📊 生成的映射表（运行时创建）
```

## 📚 文档文件

```
├── SERVER_DEPLOYMENT.md            # 🚀 服务器部署指南
├── SERVER_PULL_GUIDE.md            # 📋 定时拉取详细指南
└── PROJECT_STRUCTURE.md            # 📁 项目结构说明（本文件）
```

## 🚀 主要功能流程

### 1. 数据获取流程
```
ticker输入 → sector_data.py → coingecko_helper.py → CoinGecko API
                ↓
         智能匹配（选市值最大） → 缓存 → 返回完整数据
```

### 2. 服务器定时更新流程
```
Linux Cron → daily_pull.sh → pull_coin_info.py → update_mapping_table.py
                                    ↓
                            coin_mapping_table.csv（本地映射表）
```

### 3. TG Bot查询流程
```
/ticker命令 → ticker_command.py → 读取本地映射表 → 瞬间返回结果
```

## 💡 使用场景

### 开发测试
```bash
# 单个币种查询
python data/sector_data.py ANIMEUSDT

# 生成分析矩阵
python generate_category_matrix.py one-hot BTCUSDT ETHUSDT ANIMEUSDT
```

### 服务器部署
```bash
# 设置定时任务
0 2 * * * /path/to/TaoTrader/run/daily_pull.sh

# 启动TG Bot
python run/run_tg_bot.py
```

### 数据分析
```python
import pandas as pd

# 加载映射表
df = pd.read_csv('coin_mapping_table.csv')

# 按板块分组分析
sectors = df['categories'].str.split(';').explode()
sector_stats = sectors.value_counts()
```

## 🎯 核心优势

- ✅ **模块化设计**: 功能清晰分离
- ✅ **缓存优化**: 避免重复API调用
- ✅ **稳定可靠**: 超保守的API调用策略
- ✅ **用户友好**: TG Bot即时响应
- ✅ **易于维护**: 清晰的文件结构和文档

## 📦 依赖关系

```
sector_data.py ← coingecko_helper.py
     ↑
update_mapping_table.py
     ↑
pull_coin_info.py
     ↑
daily_pull.sh

ticker_command.py ← coin_mapping_table.csv
     ↑
run_tg_bot.py
```

这个结构确保了功能的独立性和可维护性，同时提供了完整的数据获取和查询解决方案。
