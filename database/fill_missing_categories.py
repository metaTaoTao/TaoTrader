import time
from database.db_manager import DBManager
from utils.coingecko_helper import query_coin_info_from_coingecko

def fill_missing_categories():
    db = DBManager()
    missing = db.get_tickers_missing_category()

    print(f"共找到 {len(missing)} 个缺失分类的币种\n")

    updated = 0
    for row in missing:
        symbol = row['symbol']
        base_asset = row['base_asset']

        try:
            info = query_coin_info_from_coingecko(base_asset)
            if not info or not info.get("categories"):
                print(f"[跳过] 未找到分类: {symbol}")
                continue

            db.insert_categories(symbol, info["categories"])
            db.update_last_updated(symbol)
            print(f"[更新] {symbol} -> 插入 {len(info['categories'])} 个分类")
            updated += 1
            time.sleep(10)  # 避免触发 CoinGecko 限流

        except Exception as e:
            print(f"[错误] {symbol}: {e}")
            continue

    db.close()
    print(f"\n已完成：成功插入 {updated} 个币种的分类信息")

if __name__ == "__main__":
    fill_missing_categories()
