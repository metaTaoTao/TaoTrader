# 服务器定时拉取指南

## 🎯 概述

`run/pull_coin_info.py` 是专为服务器定时任务设计的币种信息拉取工具，采用**完全重建模式**，每次运行都重新拉取所有币种信息，确保数据的完整性和一致性。

## 📁 相关文件

```
TaoTrader/
├── run/
│   ├── pull_coin_info.py           # 🎯 主拉取脚本
│   ├── daily_pull.sh               # 🐧 Linux定时任务脚本
│   └── logs/                       # 📝 日志目录
├── update_mapping_table.py         # 🔧 映射表更新工具
├── tickers.json                    # 📄 币种列表
├── coin_mapping_table.csv          # 📊 生成的映射表
└── backups/                        # 💾 备份目录
```

## 🚀 部署步骤

### 1. 上传文件到服务器
```bash
# 核心文件
scp data/sector_data.py user@server:/path/to/TaoTrader/data/
scp utils/coingecko_helper.py user@server:/path/to/TaoTrader/utils/
scp update_mapping_table.py user@server:/path/to/TaoTrader/
scp run/pull_coin_info.py user@server:/path/to/TaoTrader/run/
scp run/daily_pull.sh user@server:/path/to/TaoTrader/run/
scp tickers.json user@server:/path/to/TaoTrader/
scp requirements.txt user@server:/path/to/TaoTrader/
```

### 2. 服务器环境准备
```bash
cd /path/to/TaoTrader

# 安装依赖
pip3 install requests pandas

# 设置执行权限
chmod +x run/daily_pull.sh
chmod +x run/pull_coin_info.py

# 创建必要目录
mkdir -p run/logs
mkdir -p backups
```

### 3. 首次手动执行测试
```bash
# 测试拉取脚本
python3 run/pull_coin_info.py

# 或使用shell脚本
./run/daily_pull.sh
```

### 4. 设置定时任务
```bash
# 编辑crontab
crontab -e

# 添加每日凌晨2点执行
0 2 * * * /path/to/TaoTrader/run/daily_pull.sh

# 或者每12小时执行一次
0 */12 * * * /path/to/TaoTrader/run/daily_pull.sh
```

## ⚙️ 超保守API策略

### 1. 时间间隔设置
```
基础等待: 20秒
API调用间隔: 5秒
批次间隔: 60秒
重试间隔: 20s → 40s → 80s → 160s → 320s
```

### 2. 分批处理
- **批次大小**: 5个币种/批
- **批次间隔**: 60秒
- **失败重试**: 最多5次

### 3. 缓存策略
- **缓存文件**: `coingecko_cache_server.pkl`
- **有效期**: 24小时
- **立即保存**: 每次成功获取数据后立即保存

## 📊 执行流程

### 1. 初始化阶段
```
🚀 启动拉取服务
📄 加载ticker列表 (tickers.json)
🔧 初始化SectorFetcher
💾 加载现有缓存
```

### 2. 完全重建阶段
```
🗑️ 清空现有映射表
📦 分批处理 (每批3个币种)
⏳ 币种间等待10秒，批次间等待90秒
🔍 智能匹配 (选择市值最大的)
💾 批量保存所有成功数据
📝 详细日志记录
```

### 3. 完成阶段
```
📊 生成统计报告
💾 创建数据备份
🧹 清理旧日志文件
📋 输出执行摘要
```

## 📋 生成的文件

### 1. 映射表文件
```csv
ticker,base_symbol,name,coingecko_id,market_cap_rank,market_cap,fdv,volume_24h,price_change_24h,categories,last_updated
BTCUSDT,btc,Bitcoin,bitcoin,1,1000000000000,1000000000000,50000000000,2.5,Store of Value;Digital Gold,2025-01-21 02:30:00
ANIMEUSDT,anime,Animecoin,anime,592,87600000,158170000,13110000,-0.88,NFT;Meme;Arbitrum Ecosystem,2025-01-21 02:31:00
```

### 2. 日志文件
```
run/logs/pull_coin_info_20250121.log
```

### 3. 备份文件
```
backups/coin_mapping_20250121_0230.csv
```

## 🔧 监控和维护

### 1. 检查执行状态
```bash
# 查看最新日志
tail -f run/logs/pull_coin_info_$(date +%Y%m%d).log

# 检查cron执行
tail -f /var/log/cron

# 查看映射表统计
python3 update_mapping_table.py --stats
```

### 2. 手动重新拉取
```bash
# 强制更新所有数据
python3 run/pull_coin_info.py

# 或者更新特定币种
python3 update_mapping_table.py BTCUSDT ETHUSDT --force
```

### 3. 故障排除
```bash
# 检查网络连接
curl -I "https://api.coingecko.com/api/v3/ping"

# 检查磁盘空间
df -h

# 检查Python环境
python3 -c "import requests, pandas; print('✅ 依赖正常')"
```

## 🎯 TG Bot集成

### 1. 确保映射表存在
```bash
ls -la coin_mapping_table.csv
```

### 2. 启动TG Bot
```bash
python3 run/run_tg_bot.py
```

### 3. 测试ticker查询
```
/ticker ANIMEUSDT    # 应该瞬间返回结果
/ticker BTCUSDT      # 从本地映射表读取
```

## 📈 性能指标

### 预期执行时间（100个币种）
- **初始化**: 2-5分钟
- **完全重建**: 60-120分钟（每批3个币种，间隔90秒）
- **总耗时**: 65-125分钟

### 时间计算公式
```
总时间 ≈ 初始化时间 + (币种数量 ÷ 3) × 90秒 + API调用时间
例如100个币种 ≈ 5分钟 + 34批 × 90秒 + 30分钟 ≈ 86分钟
```

### 成功率目标
- **目标成功率**: >95%
- **可接受成功率**: >90%
- **告警阈值**: <80%

## ⚡ 关键优势

### 1. 稳定性
- ✅ 超保守的API调用策略
- ✅ 完善的错误处理和重试机制
- ✅ 分批处理避免长时间阻塞

### 2. 可靠性
- ✅ 详细的日志记录
- ✅ 自动备份机制
- ✅ 缓存机制减少失败影响

### 3. 可维护性
- ✅ 清晰的执行流程
- ✅ 完善的监控工具
- ✅ 灵活的配置选项

现在你可以在服务器上安心地设置定时任务，每天自动拉取最新的币种信息，TG Bot用户将享受极快的查询响应！🎉
