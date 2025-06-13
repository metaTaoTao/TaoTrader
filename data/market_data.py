import pandas as pd
import okx.MarketData as MarketData
import time
from datetime import datetime
from dateutil import tz


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
