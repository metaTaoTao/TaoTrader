import pandas as pd
import okx.MarketData as MarketData
import time
from datetime import datetime
from dateutil import tz
from binance.client import Client


class OKXDataFetcher:
    """
    Binance-compatible data fetcher for OKX.
    Interface parity (same method names and signatures as BinanceDataFetcher):
      - get_all_usdt_pairs() -> List[str]  (e.g., ["BTCUSDT", "ETHUSDT", ...])
      - get_klines(symbol: str, interval: str = '1h', total: int = 300) -> DataFrame
      - get_top_usdt_pairs_by_volume(top_n: int = 50) -> DataFrame with columns ['symbol','quoteVolume']
    Notes:
      - By default, uses OKX SWAP instruments (perpetual futures). Pass instType='SPOT' for spot.
      - Symbol translation:
          Binance-like "BTCUSDT" <-> OKX instId:
            SPOT: "BTC-USDT"
            SWAP: "BTC-USDT-SWAP"
      - Interval mapping: '1m','5m','15m','30m','1h','4h','12h','1d','1w' -> OKX '1m','5m','15m','30m','1H','4H','12H','1D','1W'
    """

    def __init__(self, flag: str = "0", instType: str = "SWAP"):
        """
        :param flag: "0" for real, "1" for demo
        :param instType: "SWAP" for perpetuals (default) or "SPOT"
        """
        self.market = MarketData.MarketAPI(flag=flag)
        self.instType = instType.upper()

    # ------------- Symbol & interval translation -------------
    @staticmethod
    def _interval_to_okx(interval: str) -> str:
        m = {
            "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1H", "2h": "2H", "4h": "4H", "6h": "6H", "12h": "12H",
            "1d": "1D", "3d": "3D", "1w": "1W", "1M": "1M"
        }
        if interval not in m:
            raise ValueError(f"Unsupported interval '{interval}'.")
        return m[interval]

    def _binance_to_okx_instid(self, symbol: str) -> str:
        """
        Convert Binance-like symbol 'BTCUSDT' -> OKX instId based on instType.
        SPOT: 'BTC-USDT'; SWAP: 'BTC-USDT-SWAP'
        """
        if not symbol.endswith("USDT"):
            raise ValueError(f"Only *USDT symbols are supported. Got: {symbol}")
        base = symbol[:-4]   # strip 'USDT'
        if self.instType == "SPOT":
            return f"{base}-USDT"
        elif self.instType == "SWAP":
            return f"{base}-USDT-SWAP"
        else:
            raise ValueError(f"Unsupported instType '{self.instType}'. Use 'SPOT' or 'SWAP'.")

    @staticmethod
    def _okx_to_binance_symbol(instId: str) -> str:
        """
        Convert OKX instId back to Binance-like symbol.
        'BTC-USDT' or 'BTC-USDT-SWAP' -> 'BTCUSDT'
        """
        if instId.endswith("-SWAP"):
            instId = instId[:-5]
        parts = instId.split("-")
        if len(parts) >= 2 and parts[1] == "USDT":
            return f"{parts[0]}USDT"
        # Fallback: remove dashes
        return instId.replace("-", "")

    # ------------- Public Binance-compatible methods -------------

    def get_all_usdt_pairs(self):
        """
        Return a list of Binance-like symbols, e.g., ["BTCUSDT", "ETHUSDT", ...]
        Uses OKX tickers by instType (SWAP or SPOT).
        """
        res = self.market.get_tickers(instType=self.instType)
        data = res.get("data", []) or []
        symbols = []
        for d in data:
            instId = d.get("instId", "")
            if self.instType == "SWAP":
                # Keep only USDT perpetuals
                if instId.endswith("-USDT-SWAP"):
                    symbols.append(self._okx_to_binance_symbol(instId))
            else:
                # SPOT: keep USDT quote
                if instId.endswith("-USDT"):
                    symbols.append(self._okx_to_binance_symbol(instId))
        # Deduplicate and sort for stability
        symbols = sorted(list(set(symbols)))
        return symbols

    def get_klines(self, symbol: str, interval: str = '1h', total: int = 300):
        """
        Fetch historical klines and return a pandas DataFrame with:
        index = timestamp (UTC), columns = ['open','high','low','close','volume'] as float
        Matches BinanceDataFetcher.get_klines() structure.
        """
        instId = self._binance_to_okx_instid(symbol)
        okx_bar = self._interval_to_okx(interval)

        # OKX get_candlesticks returns up to 300 bars per call, newest-first order.
        # We'll paginate backward using the 'after' cursor.
        all_rows = []
        fetched = 0
        next_after = None
        max_batch = 300

        while fetched < total:
            limit = min(max_batch, total - fetched)
            params = {"instId": instId, "bar": okx_bar, "limit": limit}
            if next_after is not None:
                params["after"] = next_after  # fetch older

            out = self.market.get_candlesticks(**params)
            batch = out.get("data", []) or []
            if not batch:
                break

            # OKX rows are [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
            # but for SWAP volCcy/volCcyQuote fields may differ; we only need OHLCV.
            all_rows.extend(batch)
            fetched += len(batch)

            # 'after' uses the oldest ts in this batch to go further back
            oldest_ts = batch[-1][0]
            next_after = oldest_ts
            time.sleep(0.2)  # simple rate limit

        if not all_rows:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        # Build DataFrame
        df = pd.DataFrame(all_rows, columns=[
            "timestamp", "open", "high", "low", "close",
            "volume", "volCcy", "volCcyQuote", "confirm"
        ])

        # Convert
        df["timestamp"] = pd.to_datetime(df["timestamp"].astype("int64"), unit="ms", utc=True)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

        # Normalize to Binance-like structure
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df = df.sort_values("timestamp").set_index("timestamp")
        return df

    def get_top_usdt_pairs_by_volume(self, top_n: int = 50):
        """
        Return a DataFrame sorted by 24h quote volume (USD-like) with columns:
          ['symbol', 'quoteVolume']
        'quoteVolume' approximated from OKX fields:
           - Prefer 'volCcyQuote24h' when present (already in quote currency)
           - Fallback: last * volCcy24h
        """
        res = self.market.get_tickers(instType=self.instType)
        data = res.get("data", []) or []
        rows = []

        for d in data:
            instId = d.get("instId", "")
            if self.instType == "SWAP":
                if not instId.endswith("-USDT-SWAP"):
                    continue
            else:
                if not instId.endswith("-USDT"):
                    continue

            # Try to use volCcyQuote24h directly (already quote-cur)
            qv = d.get("volCcyQuote24h")
            if qv is not None:
                try:
                    quote_volume = float(qv)
                except:
                    quote_volume = None
            else:
                # Fallback: last * volCcy24h
                try:
                    last = float(d.get("last"))
                    volCcy24h = float(d.get("volCcy24h"))
                    quote_volume = last * volCcy24h
                except:
                    quote_volume = None

            if quote_volume is None:
                continue

            binance_like = self._okx_to_binance_symbol(instId)
            rows.append({"symbol": binance_like, "quoteVolume": quote_volume})

        if not rows:
            return pd.DataFrame(columns=["symbol", "quoteVolume"])

        df = pd.DataFrame(rows).sort_values("quoteVolume", ascending=False).reset_index(drop=True)
        return df.head(top_n)

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

