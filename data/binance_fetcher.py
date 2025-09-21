#!/usr/bin/env python3
"""
Binance数据获取器
用于获取所有活跃的USDT交易对
"""

import requests
import time
from typing import List, Dict, Optional

class BinanceDataFetcher:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        
    def _make_request(self, endpoint: str, max_retries: int = 3) -> Optional[Dict]:
        """发送请求到Binance API"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"❌ Binance API请求失败: {e}")
                    return None
                time.sleep(2 ** attempt)  # 指数退避
        return None
    
    def get_all_usdt_pairs(self) -> List[str]:
        """获取所有活跃的USDT交易对"""
        print("🔍 正在从Binance获取所有USDT交易对...")
        
        data = self._make_request("/exchangeInfo")
        if not data:
            print("❌ 无法获取Binance交易对信息")
            return []
        
        usdt_pairs = []
        for symbol_info in data.get('symbols', []):
            symbol = symbol_info.get('symbol', '')
            status = symbol_info.get('status', '')
            quote_asset = symbol_info.get('quoteAsset', '')
            
            # 只获取活跃的USDT交易对
            if (status == 'TRADING' and 
                quote_asset == 'USDT' and 
                symbol.endswith('USDT')):
                usdt_pairs.append(symbol)
        
        # 按字母顺序排序
        usdt_pairs.sort()
        
        print(f"✅ 找到 {len(usdt_pairs)} 个活跃的USDT交易对")
        return usdt_pairs
    
    def get_filtered_usdt_pairs(self, min_volume_usdt: float = 1000000) -> List[str]:
        """
        获取过滤后的USDT交易对
        过滤条件：24小时交易量 > min_volume_usdt
        """
        print(f"🔍 正在获取24小时交易量 > ${min_volume_usdt:,.0f} 的USDT交易对...")
        
        # 获取24小时统计数据
        ticker_data = self._make_request("/ticker/24hr")
        if not ticker_data:
            print("❌ 无法获取24小时统计数据，返回所有USDT交易对")
            return self.get_all_usdt_pairs()
        
        filtered_pairs = []
        for ticker in ticker_data:
            symbol = ticker.get('symbol', '')
            volume = float(ticker.get('quoteVolume', 0))
            
            if symbol.endswith('USDT') and volume >= min_volume_usdt:
                filtered_pairs.append(symbol)
        
        # 按交易量排序（从大到小）
        volume_map = {ticker['symbol']: float(ticker['quoteVolume']) 
                     for ticker in ticker_data if ticker['symbol'].endswith('USDT')}
        
        filtered_pairs.sort(key=lambda x: volume_map.get(x, 0), reverse=True)
        
        print(f"✅ 找到 {len(filtered_pairs)} 个高交易量的USDT交易对")
        return filtered_pairs
    
    def get_top_market_cap_pairs(self, limit: int = 200) -> List[str]:
        """
        获取市值排名前N的USDT交易对
        这个方法需要结合CoinGecko数据
        """
        print(f"🔍 正在获取市值排名前 {limit} 的USDT交易对...")
        
        all_pairs = self.get_all_usdt_pairs()
        
        # 简单按交易量排序作为市值的代理指标
        ticker_data = self._make_request("/ticker/24hr")
        if not ticker_data:
            return all_pairs[:limit]
        
        # 创建交易量映射
        volume_map = {}
        for ticker in ticker_data:
            symbol = ticker.get('symbol', '')
            if symbol.endswith('USDT'):
                volume_map[symbol] = float(ticker.get('quoteVolume', 0))
        
        # 按交易量排序
        sorted_pairs = sorted(all_pairs, key=lambda x: volume_map.get(x, 0), reverse=True)
        
        result = sorted_pairs[:limit]
        print(f"✅ 返回交易量排名前 {len(result)} 的USDT交易对")
        return result
    
    def save_tickers_to_file(self, tickers: List[str], filename: str = 'binance_tickers.json'):
        """保存ticker列表到文件"""
        import json
        
        data = {
            "tickers": tickers,
            "source": "Binance API",
            "total_count": len(tickers),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "从Binance API获取的所有活跃USDT交易对"
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ ticker列表已保存到 {filename}")
        except Exception as e:
            print(f"❌ 保存ticker列表失败: {e}")

if __name__ == "__main__":
    # 测试功能
    fetcher = BinanceDataFetcher()
    
    print("=" * 50)
    print("🧪 测试BinanceDataFetcher")
    print("=" * 50)
    
    # 获取所有USDT交易对
    all_tickers = fetcher.get_all_usdt_pairs()
    print(f"\n📊 所有USDT交易对数量: {len(all_tickers)}")
    print(f"📋 前10个: {all_tickers[:10]}")
    
    # 获取高交易量的交易对
    high_volume_tickers = fetcher.get_filtered_usdt_pairs(min_volume_usdt=5000000)  # 500万USDT
    print(f"\n📊 高交易量交易对数量: {len(high_volume_tickers)}")
    print(f"📋 前10个: {high_volume_tickers[:10]}")
    
    # 获取前100名
    top_tickers = fetcher.get_top_market_cap_pairs(limit=100)
    print(f"\n📊 前100名交易对数量: {len(top_tickers)}")
    print(f"📋 前10个: {top_tickers[:10]}")
    
    # 保存到文件
    fetcher.save_tickers_to_file(all_tickers, 'all_binance_usdt_pairs.json')
    fetcher.save_tickers_to_file(high_volume_tickers, 'high_volume_usdt_pairs.json')
    fetcher.save_tickers_to_file(top_tickers, 'top_100_usdt_pairs.json')
    
    print("\n🎉 测试完成！")
