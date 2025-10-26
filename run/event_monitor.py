#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件监控模块 - 监控24h涨幅榜
与 run_scanner.py 平级
"""

import sys
import os

# 自动添加项目根目录到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from data.market_data import BinanceDataFetcher
from utils.file_helper import DataIO
import pandas as pd
import numpy as np


def compute_24h_return(df):
    """计算24h涨幅"""
    if df is None or len(df) < 25:
        return np.nan
    
    c = df['close']
    ret_24h = float(c.iloc[-1] / c.iloc[-25] - 1.0)
    return ret_24h


def get_24h_leaders(top_n=20):
    """
    获取24h涨幅榜前N名
    返回DataFrame，包含：symbol, ret_24h, ret_pct, notional_24h
    """
    fetcher = BinanceDataFetcher()
    tickers = fetcher.get_all_usdt_pairs()
    results = []
    
    print(f"📊 开始扫描24h涨幅榜...")
    print(f"📋 总币种数: {len(tickers)}")
    
    # 扫描所有币种，但只记录涨幅最大的币种
    for symbol in tickers:
        try:
            df = fetcher.get_klines(symbol, interval='1h', total=100)
            
            # 计算24h涨幅
            ret_24h = compute_24h_return(df)
            
            if not np.isnan(ret_24h):
                # 计算24h成交额（简化版）
                last_24 = df.iloc[-24:] if len(df) >= 24 else df
                if 'volume' in last_24.columns:
                    notional_24h = (last_24['close'] * last_24['volume']).sum()
                else:
                    notional_24h = 0
                
                results.append({
                    'symbol': symbol,
                    'ret_24h': ret_24h,
                    'ret_pct': round(ret_24h * 100, 2),  # 百分比
                    'notional_24h': float(round(notional_24h, 2))
                })
            
        except Exception as e:
            print(f"⚠️ {symbol}: {e}")
            continue
    
    # 按涨幅排序
    if not results:
        print("❌ 没有找到有效数据")
        return pd.DataFrame()
    
    df_result = pd.DataFrame(results).sort_values(by='ret_24h', ascending=False)
    
    # 取前N名
    top_leaders = df_result.head(top_n)
    
    print(f"✅ 扫描完成，共 {len(results)} 个有效币种")
    print(f"📈 涨幅前{top_n}名:")
    for i, (_, row) in enumerate(top_leaders.iterrows(), 1):
        sign = "+" if row['ret_pct'] >= 0 else ""
        print(f"   {i}. {row['symbol']}: {sign}{row['ret_pct']:.2f}%")
    
    return top_leaders


def save_leaders(tf='1h', top_n=20):
    """保存涨幅榜数据"""
    leaders = get_24h_leaders(top_n=top_n)
    
    if leaders.empty:
        print("⚠️ 没有数据可保存")
        return None
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "timestamp": timestamp,
        "data": leaders,
        "type": "24h_leaders"
    }
    
    filename = f"leaders_{tf}"
    DataIO.save(data, filename)
    print(f"💾 已保存到 {filename}.pkl")
    
    return leaders


if __name__ == "__main__":
    if len(sys.argv) > 1:
        timeframe = sys.argv[1]
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    else:
        timeframe = '1h'
        top_n = 10

    try:
        leaders = save_leaders(timeframe, top_n)
        if leaders is not None:
            print(f"✅ 完成！已保存 {len(leaders)} 个币种")
    except Exception as e:
        import traceback
        traceback.print_exc()

