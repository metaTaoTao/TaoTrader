import pandas as pd
import okx.MarketData as MarketData

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
        """
        Convert a list of dictionaries to a pandas DataFrame.

        Parameters:
        - data (list): List of dictionaries from OKX API

        Returns:
        - pd.DataFrame: Formatted DataFrame with numeric types and timestamp conversion
        """
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
        """
        Parse K-line (candlestick) data returned by OKX.

        Parameters:
        - data (list): List of lists containing OHLCV + meta fields

        Returns:
        - pd.DataFrame: Cleaned K-line dataframe
        """
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
        return df

    def get_hist_kline(self, instId, bar='1m'):
        """
        Fetch historical candlestick data from OKX.

        Parameters:
        - instId (str): Instrument ID (e.g. BTC-USDT-SWAP)
        - bar (str): Interval of K-line (e.g. '1m', '5m', '4h')

        Returns:
        - pd.DataFrame: K-line historical data
        """
        result = self.marketDataAPI.get_history_candlesticks(instId=instId, bar=bar)
        return self.parse_okx_kline(result["data"])

    def get_kline(self, instId, bar='1m', limit=300):
        """
        Fetch recent K-line data.

        Parameters:
        - instId (str): Instrument ID
        - bar (str): Time interval
        - limit (int): Number of records to retrieve

        Returns:
        - pd.DataFrame: Recent K-line data
        """
        result = self.marketDataAPI.get_candlesticks(instId=instId, bar=bar, limit=limit)
        return self.parse_okx_kline(result["data"])

    def get_all_tickers(self, instType="SWAP"):
        """
        Get all tickers of a certain instrument type and estimate 24H USD volume.

        Parameters:
        - instType (str): Instrument type, e.g. 'SPOT', 'SWAP', 'FUTURES'

        Returns:
        - pd.DataFrame: Sorted by 24h USD volume
        """
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
