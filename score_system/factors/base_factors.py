import numpy as np
from indicators.vol_heatmap import VolumeHeatmapIndicator
from utils.file_helper import DataIO
from data.market_data import OKXDataFetcher
from tqdm import tqdm
import pandas as pd
import time

VOLUME_SCORE_MAP = {
    'extra_high': 1.0,
    'high': 0.75,
    'medium': 0.5,
    'normal': 0.25,
    'low': 0.0,
    'unknown': 0.0
}


class EnhancedStrengthScorer:
    def __init__(self, weights=None):
        self.weights = weights or {
            'return': 0.3,
            'ema': 0.25,
            'volume': 0.15,
            'rsi': 0.15,
            'momentum': 0.15
        }

    def compute_return_score(self, df):
        periods = {'1h': 1, '4h': 4, '24h': 24}
        score = 0
        total_weight = 0
        for label, period in periods.items():
            if len(df) > period:
                ret = (df['close'].iloc[-1] - df['close'].iloc[-period - 1]) / df['close'].iloc[-period - 1]
                weighted_score = np.clip(ret * 10, -1, 1)  # normalize to [-1, 1]
                score += weighted_score
                total_weight += 1
        return (score / total_weight + 1) / 2 if total_weight > 0 else 0.5

    def compute_ema_score(self, df):
        df = df.copy()
        df['ema5'] = df['close'].ewm(span=5).mean()
        df['ema10'] = df['close'].ewm(span=10).mean()
        df['ema20'] = df['close'].ewm(span=20).mean()
        latest = df.iloc[-1]

        if latest['ema5'] > latest['ema10'] > latest['ema20']:
            return 1.0
        elif latest['ema5'] > latest['ema10'] or latest['ema10'] > latest['ema20']:
            return 0.6
        else:
            return 0.2

    def compute_volume_score(self, df: pd.DataFrame, periods: list = [1, 4, 24]) -> float:
        heatmap = VolumeHeatmapIndicator()
        df = heatmap.calculate(df)

        score = 0
        total_weight = 0
        for p in periods:
            if len(df) < p:
                continue
            segment = df.iloc[-p:]
            mapped_scores = segment['volume_category'].map(VOLUME_SCORE_MAP).dropna()
            if not mapped_scores.empty:
                score += mapped_scores.mean()
                total_weight += 1

        return score / total_weight if total_weight > 0 else 0.5

    def compute_rsi_score(self, df, period=14):
        delta = df['close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        avg_gain = pd.Series(gain).rolling(window=period).mean()
        avg_loss = pd.Series(loss).rolling(window=period).mean()

        rs = avg_gain / (avg_loss + 1e-6)
        rsi = 100 - (100 / (1 + rs))
        latest_rsi = rsi.iloc[-1]

        # Score based on RSI value: closer to 70 = stronger
        if latest_rsi >= 70:
            return 1.0
        elif latest_rsi >= 60:
            return 0.8
        elif latest_rsi >= 50:
            return 0.6
        elif latest_rsi >= 40:
            return 0.4
        else:
            return 0.2

    def compute_momentum_score(self, df):
        scores = []
        periods = [1, 4, 24]
        for p in periods:
            if len(df) > p:
                ret = (df['close'].iloc[-1] - df['close'].iloc[-p - 1]) / df['close'].iloc[-p - 1]
                scores.append(np.clip(ret * 10, -1, 1))
        if not scores:
            return 0.5
        avg = np.mean(scores)
        return (avg + 1) / 2

    def score(self, df: pd.DataFrame, symbol: str):
        return_score = self.compute_return_score(df)
        ema_score = self.compute_ema_score(df)
        volume_score = self.compute_volume_score(df)
        rsi_score = self.compute_rsi_score(df)
        momentum_score = self.compute_momentum_score(df)

        total_score = (
            return_score * self.weights['return'] +
            ema_score * self.weights['ema'] +
            volume_score * self.weights['volume'] +
            rsi_score * self.weights['rsi'] +
            momentum_score * self.weights['momentum']
        )

        return {
            'symbol': symbol,
            'return_score': round(return_score, 3),
            'ema_score': round(ema_score, 3),
            'volume_score': round(volume_score, 3),
            'rsi_score': round(rsi_score, 3),
            'momentum_score': round(momentum_score, 3),
            'enhanced_score': round(total_score, 3)
        }

def get_top_coins(read_cache=False):
    if read_cache:
        return DataIO.load("score_result")
    fetcher = OKXDataFetcher()
    scorer = EnhancedStrengthScorer()
    tickers = fetcher.get_all_tickers()['instId'].tolist()[:100]

    results = []

    for symbol in tqdm(tickers, desc="Scoring Tickers"):
        try:
            df = fetcher.get_kline(symbol, bar="1H", total=100)
            score_dict = scorer.score(df, symbol)
            if isinstance(score_dict, dict) and "basic_score" in score_dict:
                results.append(score_dict)
            else:
                print(f"{symbol}: no score")
            time.sleep(0.2)

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

    df_result = pd.DataFrame(results).sort_values(by="basic_score", ascending=False)
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
            avg_score=("basic_score", "mean"),
            count=("symbol", "count")
        )
        .sort_values(by="avg_score", ascending=False)
        .reset_index()
    )

    return df_category


if __name__ == "__main__":
    print("\n最强势币种:")
    df = get_top_coins(True)
    print(df)
    print("\n最强势板块:")
    print(get_top_categories(df))
