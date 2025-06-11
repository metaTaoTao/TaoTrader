from data.market_data import OKXDataFetcher
from time import sleep
import pandas as pd


class Scanner:
    def __init__(self):
        self.okx_data_fetcher = OKXDataFetcher()

    def compute_trend_score(self, df):
        """
        Calculate trend score: EMA structure + return + volume change
        """
        df = df.copy()
        # Calculate exponential moving averages
        df["EMA5"] = df["close"].ewm(span=5).mean()
        df["EMA10"] = df["close"].ewm(span=10).mean()
        df["EMA20"] = df["close"].ewm(span=20).mean()
        df["EMA60"] = df["close"].ewm(span=60).mean()

        ema5 = df["EMA5"].iloc[-1]
        ema10 = df["EMA10"].iloc[-1]
        ema20 = df["EMA20"].iloc[-1]
        ema60 = df["EMA60"].iloc[-1]

        # Determine trend structure based on EMA alignment
        if ema5 > ema10 > ema20 > ema60:
            ema_structure = "bullish"
            ema_score = 40
        elif ema5 < ema10 < ema20 < ema60:
            ema_structure = "bearish"
            ema_score = 20  # Optionally give bearish trend some score
        else:
            ema_structure = "sideways"
            ema_score = 0

        # Price return score (last price vs 30 bars ago)
        ret = df["close"].iloc[-1] / df["close"].iloc[0] - 1
        ret_score = min(max(ret * 100, -10), 30)  # clamp -10%~30%

        # Volume strength: last bar volume vs average
        volume_avg = df["volume"].mean()
        volume_last = df["volume"].iloc[-1]
        volume_score = min((volume_last / volume_avg) * 10, 30)

        total_score = ema_score + ret_score + volume_score
        return {
            "score": round(total_score, 2),
            "return_1h": round(ret * 100, 2),
            "volume_change": round((volume_last / volume_avg - 1) * 100, 2),
            "ema_structure": ema_structure
        }

    def scan_strong_symbols(self, volume_threshold=1.0, kline_limit=30, max_symbols=50):
        ticker_df = self.okx_data_fetcher.get_all_tickers()
        filtered_df = ticker_df[ticker_df["volume_usd_million"] > volume_threshold]

        if len(filtered_df) > max_symbols:
            filtered_df = filtered_df.sort_values(by="volume_usd_million", ascending=False).head(max_symbols)

        top_symbols = filtered_df["instId"].tolist()
        results = []

        for symbol in top_symbols:
            try:
                df = self.okx_data_fetcher.get_kline(symbol, bar="1H", limit=kline_limit)
                if len(df) < 10:
                    continue
                score_data = self.compute_trend_score(df)
                results.append({
                    "symbol": symbol,
                    "score": score_data["score"],
                    "1h_return(%)": score_data["return_1h"],
                    "volume_change(%)": score_data["volume_change"],
                    "EMA_structure": score_data["ema_structure"]
                })
                sleep(0.1)
            except Exception as e:
                print(f"Error on {symbol}: {e}")
                continue

        df_result = pd.DataFrame(results).sort_values(by="score", ascending=False)
        return df_result


if __name__ == "__main__":
    s = Scanner()
    res = s.scan_strong_symbols()
    print(res)
