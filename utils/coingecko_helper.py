import requests
import time

def rate_limited_request(url: str, name: str, max_retries=5, base_sleep=20):
    """通用的限流请求函数，使用非常保守的重试间隔"""
    
    # 在第一次请求前添加预热延迟
    if not hasattr(rate_limited_request, '_last_request_time'):
        rate_limited_request._last_request_time = 0
    
    # 确保请求间隔至少5秒
    current_time = time.time()
    time_since_last = current_time - rate_limited_request._last_request_time
    if time_since_last < 5:
        sleep_time = 5 - time_since_last
        print(f"[*] Waiting {sleep_time:.1f}s before request to avoid rate limiting...")
        time.sleep(sleep_time)
    
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=30)
            rate_limited_request._last_request_time = time.time()
            
            if resp.status_code == 429:
                # 使用非常保守的指数退避
                wait = base_sleep * (2 ** attempt)  # 20s, 40s, 80s, 160s, 320s
                print(f"[!] Rate limited for {name}, sleep {wait}s and retrying ({attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(f"{name} API failed after retries") from e
            # 即使非429错误也等待较长时间
            wait = base_sleep + (base_sleep * attempt)  # 20s, 40s, 60s, 80s, 100s
            print(f"[!] Error for {name}, sleep {wait}s before retry ({attempt+1}/{max_retries})")
            time.sleep(wait)
    return None

def query_coin_info_from_coingecko(query: str, max_retries=5, base_sleep=10):
    """通过搜索查询币种信息"""
    # Step 1: Search
    search_url = f"https://api.coingecko.com/api/v3/search?query={query}"
    search_data = rate_limited_request(search_url, f"Search-{query}", max_retries, base_sleep)
    if not search_data or not search_data.get("coins"):
        return None

    coin = search_data["coins"][0]
    coin_id = coin["id"]

    # Step 2: Details
    detail_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    detail_data = rate_limited_request(detail_url, f"Detail-{coin_id}", max_retries, base_sleep)

    return {
        "name": coin["name"],
        "symbol": coin["symbol"],
        "id": coin_id,
        "logo": coin.get("large") or coin.get("thumb"),
        "categories": detail_data.get("categories", []),
        "market_cap": detail_data.get("market_data", {}).get("market_cap", {}).get("usd"),
        "fdv": detail_data.get("market_data", {}).get("fully_diluted_valuation", {}).get("usd"),
        "total_volume": detail_data.get("market_data", {}).get("total_volume", {}).get("usd"),
        "market_cap_rank": detail_data.get("market_data", {}).get("market_cap_rank"),
        "price_change_24h": detail_data.get("market_data", {}).get("price_change_percentage_24h")
    }

def get_coin_list(max_retries=3, base_sleep=15):
    """获取所有币种列表"""
    url = "https://api.coingecko.com/api/v3/coins/list"
    return rate_limited_request(url, "CoinList", max_retries, base_sleep)

def get_coin_details(coin_id: str, max_retries=3, base_sleep=15):
    """获取特定币种的详细信息"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    return rate_limited_request(url, f"CoinDetail-{coin_id}", max_retries, base_sleep)

def get_coin_details_ultra_safe(coin_id: str, max_retries=5, base_sleep=30):
    """获取币种详细信息 - 超保守模式，用于服务器定时任务"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    return rate_limited_request(url, f"CoinDetail-{coin_id}", max_retries, base_sleep)
