import requests
import time

class SectorFetcher:
    def __init__(self):
        self.symbol_to_id = self._fetch_coin_list()

    def _fetch_coin_list(self):
        """Fetches the list of all coins from CoinGecko"""
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url)
        response.raise_for_status()
        coins = response.json()

        # Build mapping from lowercase symbol to list of ids (可能重复)
        mapping = {}
        for coin in coins:
            symbol = coin['symbol'].lower()
            mapping.setdefault(symbol, []).append(coin['id'])
        return mapping

    def get_categories(self, ticker):
        """Given a ticker like 'ARB-USDT', return the CoinGecko categories"""
        base_symbol = ticker.split("-")[0].lower()
        possible_ids = self.symbol_to_id.get(base_symbol, [])

        for coin_id in possible_ids:
            try:
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                response = requests.get(url)
                if response.status_code == 429:
                    print("Rate limited. Sleeping...")
                    time.sleep(2)
                    continue
                response.raise_for_status()
                data = response.json()
                return data.get("categories", [])
            except Exception as e:
                continue  # Try next id if this one fails

        return ["Unknown"]

if __name__ == "__main__":
    fetcher = SectorFetcher()
    ticker = "ARB-USDT"
    categories = fetcher.get_categories(ticker)
    print(f"{ticker} belongs to: {categories}")
    s=1