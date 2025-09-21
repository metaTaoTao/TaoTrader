# TaoTrader 服务器部署完整指南

⚠️ **重要说明**: 此版本仅使用CoinGecko API的真实数据，不提供任何模拟或离线数据，确保实盘交易的数据准确性。

## 📋 部署文件清单

### 核心功能文件
- `data/sector_data.py` - 币种数据获取核心模块
- `utils/coingecko_helper.py` - CoinGecko API限流处理工具
- `bot_command/ticker_command.py` - TG Bot ticker查询命令
- `run/pull_coin_info.py` - 服务器定时拉取脚本
- `run/daily_pull.sh` - Linux定时任务脚本

### 配置文件
- `tickers.json` / `tickers.txt` - 币种列表
- `requirements.txt` - Python依赖
- `update_mapping_table.py` - 映射表更新工具
- `generate_category_matrix.py` - 数据分析工具

## 1. 上传文件到服务器

将以下核心文件上传到你的GCP服务器：
- `data/sector_data.py` - 主功能模块
- `utils/coingecko_helper.py` - CoinGecko API限流处理工具
- `generate_category_matrix.py` - 映射表生成器
- `requirements.txt` - Python依赖

## 2. 服务器环境准备

```bash
# 安装Python依赖
pip install requests

# 或者安装完整依赖
pip install -r requirements.txt

# 测试网络连接
curl -I https://api.coingecko.com/api/v3/ping
```

## 3. 测试命令

### 基本测试
```bash
# 测试单个币种
python data/sector_data.py MEUSDT

# 测试多个币种
python data/sector_data.py MEUSDT BTCUSDT ETHUSDT

# JSON格式输出（适合程序调用）
python data/sector_data.py MEUSDT --json
```

### 支持的格式
- Binance格式: `MEUSDT`, `BTCUSDT`, `ETHUSDT`
- OKX格式: `ME-USDT`, `BTC-USDT`, `ETH-USDT`

### 常见币种测试
```bash
python data/sector_data.py MEUSDT    # Magic Eden
python data/sector_data.py BTCUSDT   # Bitcoin  
python data/sector_data.py ETHUSDT   # Ethereum
python data/sector_data.py ARBUSDT   # Arbitrum
python data/sector_data.py SOLUSDT   # Solana
python data/sector_data.py BNBUSDT   # BNB
```

## 4. 集成到Scanner

```python
from data.sector_data import SectorFetcher

# 初始化（只需要一次）
fetcher = SectorFetcher()

# 在scanner循环中使用
for ticker in binance_tickers:
    # 获取完整信息
    coin_info = fetcher.get_coin_info(ticker)
    
    # 使用数据进行评分
    sector_score = calculate_sector_score(coin_info['categories'])
    mcap_score = calculate_mcap_score(coin_info['market_cap_rank'])
    volume_score = calculate_volume_score(coin_info['total_volume'])
    
    # 综合评分
    total_score = sector_score + mcap_score + volume_score
```

## 5. 返回的数据结构

```json
{
  "categories": ["NFT", "Solana Ecosystem", "NFT Marketplace"],
  "market_cap": 121450000,
  "fully_diluted_valuation": 726660000,
  "total_volume": 82280000,
  "market_cap_rank": 467,
  "price_change_24h": 7.20,
  "coin_id": "magic-eden",
  "name": "Magic Eden",
  "symbol": "ME",
  "base_symbol": "me"
}
```

## 6. 核心逻辑

### 智能币种匹配
当输入如`MEUSDT`时：
1. 提取base symbol: `ME`
2. 在CoinGecko中查找所有symbol为`ME`的币种
3. **如果找到多个匹配，自动选择市值最大的（排名最小的）**
4. 获取完整的市场数据和板块信息

### 错误处理
- API限制自动重试（使用coingecko_helper的成熟逻辑）
- 网络超时处理
- 智能币种匹配（基于实时市值选择）

## 7. 性能优化

- 内置缓存机制，避免重复API调用
- 支持批量查询
- 智能匹配算法减少API调用次数

## 8. 故障排除

### API限制问题
如果遇到CoinGecko API限制：
1. 等待几分钟后重试（API有速率限制）
2. 检查服务器IP是否被限制
3. 考虑申请CoinGecko Pro API（更高限制）

### 网络连接问题
```bash
# 测试CoinGecko连接
curl "https://api.coingecko.com/api/v3/ping"
```

### 数据准确性保证
- ✅ 所有数据来源于CoinGecko实时API
- ✅ 不使用任何缓存的静态数据
- ✅ 币种匹配基于实时市值排名
- ✅ 错误时明确提示，不返回模拟数据

### 常见错误码
- `429`: CoinGecko API速率限制，请等待后重试
- `404`: 币种不存在或已下架
- `网络错误`: 检查服务器到CoinGecko的网络连接
