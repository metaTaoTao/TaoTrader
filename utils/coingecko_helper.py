import requests
import time

def query_coin_info_from_coingecko(query: str, max_retries=5, base_sleep=10):
    def rate_limited_request(url, name):
        for attempt in range(max_retries):
            try:
                resp = requests.get(url)
                if resp.status_code == 429:
                    wait = base_sleep * (attempt + 1)
                    print(f"[!] Rate limited for {name}, sleep {wait}s and retrying ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"{name} API failed after retries for {query}") from e
                time.sleep(base_sleep * (attempt + 1))
        return None

    # Step 1: Search
    search_url = f"https://api.coingecko.com/api/v3/search?query={query}"
    search_data = rate_limited_request(search_url, "Search")
    if not search_data or not search_data.get("coins"):
        return None

    coin = search_data["coins"][0]
    coin_id = coin["id"]

    # Step 2: Details
    detail_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    detail_data = rate_limited_request(detail_url, "Detail")

    return {
        "name": coin["name"],
        "symbol": coin["symbol"],
        "id": coin_id,
        "logo": coin.get("large") or coin.get("thumb"),
        "categories": detail_data.get("categories", []),
        "market_cap": detail_data.get("market_data", {}).get("market_cap", {}).get("usd"),
        "fdv": detail_data.get("market_data", {}).get("fully_diluted_valuation", {}).get("usd")
    }
