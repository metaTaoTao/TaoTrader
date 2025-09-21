#!/usr/bin/env python3
"""
生成币种-板块映射表
支持One-Hot矩阵和长格式，便于数据分析
"""

import csv
import sys
import os
from typing import List

# 添加utils目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data.sector_data import SectorFetcher

def generate_one_hot_matrix(output_file: str, tickers: List[str]):
    """
    生成One-Hot编码矩阵
    每个板块一个列，有该板块为1，没有为0
    """
    fetcher = SectorFetcher()
    
    # 第一步：收集所有数据和所有板块
    coin_data = []
    all_categories = set()
    
    for ticker in tickers:
        print(f"正在处理 {ticker}...")
        info = fetcher.get_coin_info(ticker)
        coin_data.append(info)
        all_categories.update(info['categories'])
    
    # 按字母顺序排序板块
    sorted_categories = sorted(all_categories)
    print(f"\n发现 {len(sorted_categories)} 个不同的板块")
    
    # 第二步：生成矩阵
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        # 基础字段 + 所有板块列
        fieldnames = [
            'ticker', 'base_symbol', 'name', 'coingecko_id',
            'market_cap_rank', 'market_cap', 'fdv', 'volume_24h', 'price_change_24h'
        ] + sorted_categories
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, info in enumerate(coin_data):
            ticker = tickers[i]
            
            # 基础数据
            row_data = {
                'ticker': ticker,
                'base_symbol': info['base_symbol'],
                'name': info['name'],
                'coingecko_id': info['coin_id'],
                'market_cap_rank': info['market_cap_rank'],
                'market_cap': info['market_cap'],
                'fdv': info['fully_diluted_valuation'],
                'volume_24h': info['total_volume'],
                'price_change_24h': info['price_change_24h'],
            }
            
            # 板块One-Hot编码
            for category in sorted_categories:
                row_data[category] = 1 if category in info['categories'] else 0
            
            writer.writerow(row_data)

def generate_long_format(output_file: str, tickers: List[str]):
    """
    生成长格式数据，便于pandas groupby
    每个币种-板块组合一行
    """
    fetcher = SectorFetcher()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'ticker', 'base_symbol', 'name', 'coingecko_id',
            'market_cap_rank', 'market_cap', 'fdv', 'volume_24h',
            'price_change_24h', 'category', 'return_1d', 'score'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for ticker in tickers:
            print(f"正在处理 {ticker}...")
            info = fetcher.get_coin_info(ticker)
            
            # 基础数据
            base_data = {
                'ticker': ticker,
                'base_symbol': info['base_symbol'],
                'name': info['name'],
                'coingecko_id': info['coin_id'],
                'market_cap_rank': info['market_cap_rank'],
                'market_cap': info['market_cap'],
                'fdv': info['fully_diluted_valuation'],
                'volume_24h': info['total_volume'],
                'price_change_24h': info['price_change_24h'],
                'return_1d': 0.0,  # 你可以后续填入真实的return数据
                'score': 0.0       # 你可以后续填入真实的score数据
            }
            
            # 为每个板块创建一行
            if info['categories']:
                for category in info['categories']:
                    row_data = base_data.copy()
                    row_data['category'] = category
                    writer.writerow(row_data)
            else:
                # 如果没有板块信息
                row_data = base_data.copy()
                row_data['category'] = 'Unknown'
                writer.writerow(row_data)


def main():
    if len(sys.argv) < 3:
        print("使用方法:")
        print("python generate_category_matrix.py <format> <ticker1> [ticker2] ...")
        print("")
        print("格式选项:")
        print("  one-hot       - One-Hot矩阵格式 (每个板块一列)")
        print("  long-format   - 长格式 (便于groupby)")
        print("")
        print("示例:")
        print("python generate_category_matrix.py one-hot DEXEUSDT PERPUSDT BTCUSDT")
        print("python generate_category_matrix.py long-format DEXEUSDT PERPUSDT BTCUSDT")
        return 1
    
    format_type = sys.argv[1]
    tickers = sys.argv[2:]
    
    if format_type == 'one-hot':
        output_file = 'coin_category_matrix.csv'
        generate_one_hot_matrix(output_file, tickers)
        print(f"\n✅ One-Hot矩阵已生成: {output_file}")
        print("💡 使用pandas读取: df = pd.read_csv('coin_category_matrix.csv')")
        
    elif format_type == 'long-format':
        output_file = 'coin_category_long_format.csv'
        generate_long_format(output_file, tickers)
        print(f"\n✅ 长格式数据已生成: {output_file}")
        
    else:
        print(f"❌ 不支持的格式: {format_type}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
