import pandas as pd
import okx.MarketData as MarketData
import time
from datetime import datetime
from dateutil import tz
from binance.client import Client


class OKXDataFetcher:
    """
    A class to interact with OKX Market Data API for fetching K-line and ticker information.
    """

    def __init__(self, flag="0"):
        """
        Initialize the OKX Market Data API.

        Parameters:
        - flag (str): "0" for real trading, "1" for demo environment
        """
        self.marketDataAPI = MarketData.MarketAPI(flag=flag)

    def list_of_dicts_to_df(self, data):
        if not isinstance(data, list) or len(data) == 0:
            print("Input data is not a non-empty list.")
            return pd.DataFrame()
        if not isinstance(data[0], dict):
            print("List elements are not dictionaries.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass

        for time_col in ['ts', 'timestamp']:
            if time_col in df.columns:
                df[time_col] = pd.to_datetime(df[time_col].astype(float), unit='ms')
        return df

    def parse_okx_kline(self, data):
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close",
            "volume", "turnover", "confirm", "status"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"].astype("int64"), unit="ms")
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df = df.sort_values("timestamp").reset_index(drop=True)
        df = df.set_index("timestamp")
        return df

    def get_hist_kline(self, instId, bar='1m'):
        result = self.marketDataAPI.get_history_candlesticks(instId=instId, bar=bar)
        return self.parse_okx_kline(result["data"])

    def get_kline(self, instId, bar='1m', total=300):
        """
        Fetch recent K-line data, supports pagination beyond 300.

        Parameters:
        - instId (str): Instrument ID
        - bar (str): Time interval (e.g., '1m', '5m', '1H')
        - total (int): Total number of candles to fetch

        Returns:
        - pd.DataFrame: Combined K-line data
        """
        all_data = []
        next_end = None
        fetched = 0
        max_batch = 300

        while fetched < total:
            limit = min(max_batch, total - fetched)
            params = {"instId": instId, "bar": bar, "limit": limit}
            if next_end:
                params["after"] = next_end

            result = self.marketDataAPI.get_candlesticks(**params)
            batch = result.get("data", [])

            if not batch:
                break

            all_data += batch
            fetched += len(batch)

            next_end = batch[-1][0]  # 最后一条的 timestamp
            time.sleep(0.2)  # 防止频率限制

        return self.parse_okx_kline(all_data)

    def get_all_tickers(self, instType="SWAP"):
        result = self.marketDataAPI.get_tickers(instType=instType)
        data = result["data"]
        df = self.list_of_dicts_to_df(data)
        df = df[df['instId'].str.contains('USDT')].copy()

        df['last'] = pd.to_numeric(df['last'], errors='coerce')
        df['vol24h'] = pd.to_numeric(df['vol24h'], errors='coerce')

        if 'volCcyQuote24h' in df.columns:
            df['volume_usd_million'] = pd.to_numeric(df['volCcyQuote24h'], errors='coerce') / 1e6
        else:
            df['volCcy24h'] = pd.to_numeric(df['volCcy24h'], errors='coerce')
            df['volume_usd_million'] = df['last'] * df['volCcy24h'] / 1e6

        df = df.sort_values(by='volume_usd_million', ascending=False)
        return df

class BinanceDataFetcher:
    def __init__(self):
        self.client = Client()

    def get_all_usdt_pairs(self):
        info = self.client.get_exchange_info()
        symbols = [s['symbol'] for s in info['symbols'] if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING']
        return symbols

    def get_klines(self, symbol: str, interval: str = '1h', total: int = 300):
        limit_per_call = 1000
        klines_all = []
        end_time = None

        while len(klines_all) < total:
            limit = min(limit_per_call, total - len(klines_all))
            data = self.client.get_klines(symbol=symbol, interval=interval, endTime=end_time, limit=limit)

            if not data:
                break

            klines_all.extend(data)
            end_time = data[0][0] - 1  # 下一轮以当前最早时间往前翻
            time.sleep(0.5)  # 防止速率限制

        # 转为 DataFrame
        df = pd.DataFrame(klines_all, columns=[
            "timestamp", "open", "high", "low", "close",
            "volume", "close_time", "quote_asset_volume",
            "number_of_trades", "taker_buy_base_volume",
            "taker_buy_quote_volume", "ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df.set_index("timestamp", inplace=True)
        df.sort_index(inplace=True)
        return df
    def get_top_usdt_pairs_by_volume(self, top_n=50):
        tickers = self.client.get_ticker()
        df = pd.DataFrame(tickers)
        df = df[df['symbol'].str.endswith('USDT')].copy()
        df['quoteVolume'] = pd.to_numeric(df['quoteVolume'], errors='coerce')
        df = df.sort_values(by='quoteVolume', ascending=False)
        return df[['symbol', 'quoteVolume']].head(top_n)


if __name__ == "__main__":
    fetcher = BinanceDataFetcher()
    all_tickers = fetcher.get_all_usdt_pairs()

    top_pairs = fetcher.get_top_usdt_pairs_by_volume(10)
    print("Top 10 USDT pairs by volume:")
    print(top_pairs)

    symbol = top_pairs.iloc[0]['symbol']
    df = fetcher.get_klines(symbol=symbol, interval='1h', total=1000)
    print(f"\nLatest 1h Klines for {symbol}:")
    print(df.tail())

