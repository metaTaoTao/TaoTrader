from database.db_manager import DBManager
import pandas as pd
import datetime

db = DBManager()

# 插入测试 coin metadata
db.insert_coin_metadata(
    symbol="BTC-USDT",
    base_asset="BTC",
    quote_asset="USDT",
    coingecko_id="bitcoin",
    category="Layer 1",
    logo_url="https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
)

# 插入测试 K 线数据
df = pd.DataFrame({
    "timestamp": [datetime.datetime.now().replace(second=0, microsecond=0).isoformat()],
    "open": [30000],
    "high": [30500],
    "low": [29900],
    "close": [30400],
    "volume": [1234.56],
    "quote_volume": [30400 * 1234.56]
})
db.insert_kline("BTC-USDT", "1H", df)

# 查询刚才写入的 K 线
df_kline = db.query_kline("BTC-USDT", "1H")
print(df_kline)

# 插入测试得分
scan_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0).isoformat()
db.insert_score(
    scan_time=scan_time,
    symbol="BTC-USDT",
    return_score=0.83,
    trend_score=0.7,
    vol_score=0.9,
    final_score=0.81,
    notes="Strong trend observed"
)

# 关闭数据库连接
db.close()
