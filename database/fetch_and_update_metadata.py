import time
from data.market_data import OKXDataFetcher
from database.db_manager import DBManager
from utils.coingecko_helper import query_coin_info_from_coingecko


def update_all_okx_metadata():
    fetcher = OKXDataFetcher()
    db = DBManager()

    try:
        tickers_df = fetcher.get_all_tickers()
        all_symbols = tickers_df['instId'].tolist()
    except Exception as e:
        print(f"[ERROR] 无法获取 OKX ticker 列表: {e}")
        return

    updated, skipped = 0, 0

    for symbol in all_symbols:
        if not symbol.endswith("USDT-SWAP"):
            continue
        base_asset = symbol.replace("-USDT-SWAP", "")

        # 已存在则跳过
        if db.get_ticker(symbol):
            skipped += 1
            continue

        try:
            info = query_coin_info_from_coingecko(base_asset)
            if not info:
                print(f"[!] 未找到 CoinGecko 信息: {symbol}")
                skipped += 1
                continue

            # 插入主表，category 保持为空
            db.insert_ticker(
                symbol=symbol,
                base_asset=base_asset,
                quote_asset="USDT",
                coingecko_id=info["id"],
                category=None,
                logo_url=info.get("logo")
            )

            # 插入副表 categories
            if info.get("categories"):
                db.insert_categories(symbol, info["categories"])

            print(f"插入: {symbol} -> {info['name']}")
            updated += 1
            time.sleep(1.2)  # 避免 CoinGecko API 限速

        except Exception as e:
            print(f"[ERROR] 插入 {symbol} 时出错: {e}")
            skipped += 1

    db.close()
    print(f"\n✅ 所有 ticker 信息更新完毕，共插入 {updated} 个，跳过 {skipped} 个。")


if __name__ == "__main__":
    update_all_okx_metadata()
