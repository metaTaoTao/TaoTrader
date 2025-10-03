import requests
import time
import argparse
import json
import sys
import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 添加utils目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.coingecko_helper import get_coin_list, get_coin_details

class SectorFetcher:
    def __init__(self, cache_file: str = 'coingecko_cache.pkl'):
        self.cache_file = cache_file
        self.cache = self._load_cache()  # 加载持久化缓存
        self.symbol_to_coins = self._fetch_coin_list()
        
    def _load_cache(self) -> Dict:
        """加载持久化缓存"""
        if not os.path.exists(self.cache_file):
            return {}
        
        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查缓存数据的有效性（24小时内的数据认为有效）
            valid_cache = {}
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for coin_id, data in cache_data.items():
                if isinstance(data, dict) and 'cached_at' in data:
                    cached_time = datetime.fromisoformat(data['cached_at'])
                    if cached_time > cutoff_time:
                        valid_cache[coin_id] = data
                        
            print(f"加载了 {len(valid_cache)} 个有效的缓存数据")
            return valid_cache
            
        except Exception as e:
            print(f"加载缓存失败: {e}")
            return {}
    
    def _save_cache(self):
        """保存缓存到文件"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def _fetch_coin_list(self):
        """使用coingecko_helper获取币种列表"""
        try:
            coins = get_coin_list(max_retries=3, base_sleep=15)
            if not coins:
                raise Exception("无法获取币种列表")
                
            # Build mapping from lowercase symbol to list of coin info
            mapping = {}
            for coin in coins:
                symbol = coin['symbol'].lower()
                mapping.setdefault(symbol, []).append({
                    'id': coin['id'],
                    'name': coin['name'],
                    'symbol': coin['symbol']
                })
            return mapping
        except Exception as e:
            print(f"❌ 无法获取币种列表: {e}")
            raise Exception("无法连接到CoinGecko API，请检查网络连接或稍后重试")



    def _find_best_match(self, base_symbol: str) -> Optional[str]:
        """
        找到最佳匹配的CoinGecko coin_id
        如果有多个匹配，选择市值最大的（排名最小的）
        同时缓存获取到的数据，避免重复API调用
        """
        possible_coins = self.symbol_to_coins.get(base_symbol, [])
        if not possible_coins:
            return None
            
        if len(possible_coins) == 1:
            return possible_coins[0]['id']
        
        print(f"发现 {len(possible_coins)} 个匹配的币种，选择市值最大的...")
        
        best_coin = None
        best_rank = float('inf')
        
        for coin in possible_coins:
            try:
                # 先检查缓存
                if coin['id'] in self.cache:
                    market_data = self.cache[coin['id']]
                    print(f"  {coin['name']}: 使用缓存数据")
                else:
                    # 在API调用前等待，避免过于频繁的请求
                    time.sleep(5)  # 增加到5秒间隔
                    market_data = get_coin_details(coin['id'], max_retries=2, base_sleep=20)
                    if market_data:
                        # 立即缓存数据，避免后续重复调用，添加时间戳
                        market_data['cached_at'] = datetime.now().isoformat()
                        self.cache[coin['id']] = market_data
                
                if market_data:
                    rank = market_data.get('market_data', {}).get('market_cap_rank', float('inf'))
                    
                    print(f"  {coin['name']}: 市值排名 #{rank if rank != float('inf') else 'N/A'}")
                    
                    # 选择排名最小的（市值最大的）
                    if rank < best_rank:
                        best_coin = coin['id']
                        best_rank = rank
                else:
                    print(f"  {coin['name']}: 无法获取数据")
            except Exception as e:
                print(f"  {coin['name']}: 无法获取数据")
                continue
        
        if best_coin:
            return best_coin
        
        # 如果都无法获取数据，返回第一个
        return possible_coins[0]['id']

    def _get_market_data(self, coin_id: str) -> Optional[Dict]:
        """使用coingecko_helper获取币种的市场数据，带缓存"""
        if coin_id in self.cache:
            print(f"使用缓存数据获取 {coin_id} 的详细信息")
            return self.cache[coin_id]
        
        print(f"从API获取 {coin_id} 的详细信息...")
        try:
            data = get_coin_details(coin_id, max_retries=3, base_sleep=20)
            if data:
                # 添加时间戳并缓存
                data['cached_at'] = datetime.now().isoformat()
                self.cache[coin_id] = data
                print(f"已缓存 {coin_id} 的数据")
                # 立即保存到文件
                self._save_cache()
            return data
        except Exception as e:
            print(f"获取 {coin_id} 数据失败: {e}")
            return None

    def get_coin_info(self, ticker: str) -> Dict:
        """
        获取币种的完整信息，包括板块、市值、FDV、换手率等
        支持多种ticker格式：
        - Binance格式: MEUSDT, BTCUSDT
        - OKX格式: ME-USDT, BTC-USDT  
        """
        # 处理不同的ticker格式
        if "-" in ticker:
            # OKX格式: ME-USDT
            base_symbol = ticker.split("-")[0].lower()
        else:
            # Binance格式: MEUSDT -> ME
            # 移除常见的quote currencies
            quote_currencies = ['USDT', 'USDC', 'BTC', 'ETH', 'BNB', 'BUSD', 'FDUSD']
            base_symbol = ticker.upper()
            for quote in quote_currencies:
                if ticker.upper().endswith(quote):
                    base_symbol = ticker.upper()[:-len(quote)]
                    break
            base_symbol = base_symbol.lower()
        
        # 找到最佳匹配的coin_id
        coin_id = self._find_best_match(base_symbol)
        if not coin_id:
            print(f"❌ 未找到币种 {base_symbol.upper()} 的数据")
            return {
                'categories': [],
                'market_cap': None,
                'fully_diluted_valuation': None,
                'total_volume': None,
                'market_cap_rank': None,
                'coin_id': None,
                'name': None,
                'base_symbol': base_symbol,
                'error': f'未找到币种 {base_symbol.upper()}'
            }
        
        # 获取详细数据
        data = self._get_market_data(coin_id)
        if not data:
            print(f"❌ 无法获取币种 {base_symbol.upper()} 的市场数据")
            return {
                'categories': [],
                'market_cap': None,
                'fully_diluted_valuation': None,
                'total_volume': None,
                'market_cap_rank': None,
                'coin_id': coin_id,
                'name': None,
                'base_symbol': base_symbol,
                'error': f'无法获取币种 {base_symbol.upper()} 的市场数据'
            }
        
        market_data = data.get('market_data', {})
        
        categories = data.get('categories', [])
        if not categories:
            categories = []  # 返回空列表而不是['Unknown']，让调用方决定如何处理
            
        return {
            'categories': categories,
            'market_cap': market_data.get('market_cap', {}).get('usd'),
            'fully_diluted_valuation': market_data.get('fully_diluted_valuation', {}).get('usd'),
            'total_volume': market_data.get('total_volume', {}).get('usd'),
            'market_cap_rank': market_data.get('market_cap_rank'),
            'price_change_24h': market_data.get('price_change_percentage_24h'),
            'coin_id': coin_id,
            'name': data.get('name'),
            'symbol': data.get('symbol'),
            'base_symbol': base_symbol
        }

    def get_categories(self, ticker: str) -> List[str]:
        """保持向后兼容的方法"""
        info = self.get_coin_info(ticker)
        return info['categories']

def format_number(num):
    """格式化数字显示"""
    if num is None:
        return "N/A"
    if num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"

def print_coin_info(ticker: str, coin_info: Dict, format_type: str = "pretty"):
    """打印币种信息"""
    if format_type == "json":
        print(json.dumps(coin_info, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*50}")
        print(f"🔍 分析结果: {ticker.upper()}")
        print(f"{'='*50}")
        print(f"📛 币种名称: {coin_info['name'] or 'Unknown'}")
        print(f"🆔 CoinGecko ID: {coin_info['coin_id'] or 'Unknown'}")
        print(f"🏷️  Base Symbol: {coin_info['base_symbol'].upper()}")
        print(f"🏆 市值排名: #{coin_info['market_cap_rank'] or 'N/A'}")
        
        # 显示错误信息（如果有）
        if 'error' in coin_info:
            print(f"⚠️ 警告: {coin_info['error']}")
        
        print(f"\n💰 市场数据:")
        print(f"   市值 (MV): {format_number(coin_info['market_cap'])}")
        print(f"   完全稀释估值 (FDV): {format_number(coin_info['fully_diluted_valuation'])}")
        print(f"   24h交易量: {format_number(coin_info['total_volume'])}")
        
        if coin_info['price_change_24h']:
            change = coin_info['price_change_24h']
            emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            print(f"   24h涨跌幅: {emoji} {change:.2f}%")
        
        print(f"\n🏢 板块分类:")
        categories = coin_info['categories']
        if categories:
            for i, category in enumerate(categories, 1):
                print(f"   {i}. {category}")
        else:
            print("   ⚠️ 暂无板块分类数据")
        
        print(f"{'='*50}")

def main():
    parser = argparse.ArgumentParser(
        description="获取加密货币的板块和市场数据信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  使用示例:
  python sector_data.py MEUSDT              # 分析ME币
  python sector_data.py BTCUSDT             # 分析BTC
  python sector_data.py ME-USDT             # 支持OKX格式
  python sector_data.py MEUSDT --json       # JSON格式输出
  python sector_data.py MEUSDT ETHUSDT      # 批量分析多个币种
        """
    )
    
    parser.add_argument(
        'tickers', 
        nargs='+',
        help='要分析的交易对，支持币安格式(MEUSDT)和OKX格式(ME-USDT)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='以JSON格式输出结果'
    )
    
    args = parser.parse_args()
    
    try:
        fetcher = SectorFetcher()
        results = []
        
        for ticker in args.tickers:
            coin_info = fetcher.get_coin_info(ticker)
            results.append({
                'ticker': ticker,
                'info': coin_info
            })
            
            if args.json:
                if len(args.tickers) == 1:
                    print_coin_info(ticker, coin_info, "json")
            else:
                print_coin_info(ticker, coin_info, "pretty")
        
        if args.json and len(args.tickers) > 1:
            output = {result['ticker']: result['info'] for result in results}
            print(json.dumps(output, indent=2, ensure_ascii=False))
            
    except KeyboardInterrupt:
        return 1
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())