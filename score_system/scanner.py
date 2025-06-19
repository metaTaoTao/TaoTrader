from utils.file_helper import DataIO
from data.market_data import OKXDataFetcher, BinanceDataFetcher
from factors.scorer import EnhancedStrengthScorer
from tqdm import tqdm
import pandas as pd
import time


def get_top_coins(read_cache=False):
    if read_cache:
        return DataIO.load("score_result")
    fetcher = BinanceDataFetcher()
    df_btc = fetcher.get_klines('BTCUSDT', interval="1h", total=100)
    scorer = EnhancedStrengthScorer(df_btc)
    tickers = fetcher.get_all_usdt_pairs()
    results = []

    for symbol in tqdm(tickers, desc="Scoring Tickers"):
        try:
            df = fetcher.get_klines(symbol, interval="1h", total=100)
            score_dict = scorer.score(df, symbol)
            if isinstance(score_dict, dict) and "final_score" in score_dict:
                results.append(score_dict)
            else:
                print(f"{symbol}: no score")
            time.sleep(0.2)

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

    df_result = pd.DataFrame(results).sort_values(by="final_score", ascending=False)
    # 保存评分数据
    DataIO.save(df_result, "score_result")
    return df_result


def get_top_categories(df_score):
    from database.db_manager import DBManager

    # Step 2: 读取 symbol 对应的所有 category 信息（多对多）
    db = DBManager()
    symbol_categories = db.get_all_categories()  # 应该返回 DataFrame: symbol, category
    db.close()

    # Step 3: 合并
    df_merged = df_score.merge(symbol_categories, on="symbol", how="left")  # 多行对应多category

    # Step 4: 按 category 聚合
    df_category = (
        df_merged.groupby("category")
        .agg(
            avg_score=("final_score", "mean"),
            count=("symbol", "count")
        )
        .sort_values(by="avg_score", ascending=False)
        .reset_index()
    )

    return df_category


if __name__ == "__main__":
    print("\n最强势币种:")
    df = get_top_coins()
    print(df)
    # print("\n最强势板块:")
    # print(get_top_categories(df))