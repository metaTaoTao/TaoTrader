#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grok事件分析器 - 集成Grok API进行事件驱动分析
"""

import sys
import os
import json

# 自动添加项目根目录到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from utils.file_helper import DataIO
from utils.grok_client import get_grok_client
from utils.format_discord_message import format_simple_discord, format_for_discord, parse_grok_table, format_json_for_discord
from data.market_data import BinanceDataFetcher
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# 加载环境变量
load_dotenv()


def load_leaders_data(tf='1h'):
    """加载涨幅榜数据"""
    filename = f"leaders_{tf}"
    try:
        data = DataIO.load(filename)
        return data
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        return None


def format_data_for_grok(data, top_n=10):
    """格式化数据为Grok友好的格式 - 简化为币种列表"""
    if data is None:
        return None
    
    df = data['data']
    timestamp = data.get('timestamp', 'N/A')
    
    # 先取前N行，然后迭代
    df_top = df.head(top_n)
    
    # 只返回币种列表
    coin_list = []
    for i, (_, row) in enumerate(df_top.iterrows(), 1):
        coin_list.append({
            'rank': i,
            'symbol': row['symbol'],
            'return_24h_pct': float(row['ret_pct'])
        })
    
    return {
        'timestamp': timestamp,
        'coin_list': coin_list
    }


def get_additional_context(symbols, max_symbols=10):
    """获取额外上下文信息（从Binance获取）"""
    fetcher = BinanceDataFetcher()
    context = {
        'market_info': {},
        'general_trend': ''
    }
    
    print("📊 获取市场上下文信息...")
    
    # 获取BTC/ETH等主要币种的价格作为市场基准
    for symbol in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']:
        try:
            df = fetcher.get_klines(symbol, interval='1h', total=100)
            if df is not None and len(df) >= 25:
                price_24h_ago = float(df['close'].iloc[-25])
                current_price = float(df['close'].iloc[-1])
                change_pct = (current_price / price_24h_ago - 1) * 100
                
                context['market_info'][symbol] = {
                    'current_price': current_price,
                    'change_24h': round(change_pct, 2)
                }
        except Exception as e:
            print(f"⚠️ 获取 {symbol} 信息失败: {e}")
    
    return context


def analyze_with_grok_integration(data, auto_call=False, top_n=10):
    """集成Grok进行事件驱动分析"""
    
    # 格式化数据 - 简化版
    formatted_data = format_data_for_grok(data, top_n=top_n)
    
    # 提取币种列表
    coin_symbols = [coin['symbol'] for coin in formatted_data['coin_list']]
    symbols_text = ", ".join(coin_symbols)
    
    print("\n" + "="*80)
    print("📊 准备事件驱动分析")
    print("="*80)
    print(f"时间戳: {formatted_data['timestamp']}")
    print(f"候选币种 ({len(coin_symbols)}个): {symbols_text}")
    
    # 优化后的提示词
    prompt = f"""分析以下币种在过去72小时的事件驱动因素：

{symbols_text}

规则：
- 事件类型：listing,delisting,airdrop,unlock,partnership,hack,regulatory,product_release,liquidity,whale,lawsuit,rumor,other
- 板块（中文）：隐私币/AI/DeFi/Meme/L2/预言机/支付币/RWA等
- 所有文本用中文
- 来源链接尽量真实

返回JSON数组：
[{{"symbol":"XXUSDT","event_type":"type","event_summary":"中文事件","time_utc":"2024-10-26 12:00","heat_score":50,"sector":"隐私币","importance_score":60,"comprehensive_score":55,"source_links":["链接"]}}]

必须返回至少一些数据，不要返回空数组[]。"""
    
    if auto_call:
        # 自动调用Grok API
        client = get_grok_client()
        if client:
            print("\n🤖 正在调用 Grok API 进行事件驱动分析...")
            
            # 直接使用提示词调用
            messages = [{"role": "user", "content": prompt}]
            response = client.chat(messages)
            
            # 解析响应
            if 'choices' in response and len(response['choices']) > 0:
                analysis_content = response['choices'][0]['message']['content']
                
                print("\n" + "="*80)
                print("🤖 事件驱动分析结果（原始JSON）")
                print("="*80)
                print(analysis_content)
                
                # 尝试解析 JSON
                json_data = None
                try:
                    # 尝试提取 JSON（移除可能的 Markdown 代码块）
                    json_text = analysis_content.strip()
                    if json_text.startswith('```json'):
                        json_text = json_text[7:]  # 移除 ```json
                    if json_text.startswith('```'):
                        json_text = json_text[3:]  # 移除 ```
                    if json_text.endswith('```'):
                        json_text = json_text[:-3]  # 移除结尾的 ```
                    json_text = json_text.strip()
                    
                    json_data = json.loads(json_text)
                    
                    # 保存 JSON 格式
                    output_file = f"output/grok_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    print(f"\n💾 JSON 分析结果已保存到: {output_file}")
                    
                    # 转换为 Discord 友好格式（显示全部，不限制数量）
                    discord_msg = format_json_for_discord(json_data, max_items=10)
                    
                    # 保存 Discord 格式
                    discord_output_file = f"output/grok_analysis_discord_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(discord_output_file, 'w', encoding='utf-8') as f:
                        f.write(discord_msg)
                    print(f"💾 Discord 格式已保存到: {discord_output_file}")
                    
                    print("\n" + "="*80)
                    print("📱 Discord 友好格式预览")
                    print("="*80)
                    print(discord_msg)
                    
                except json.JSONDecodeError as e:
                    print(f"\n⚠️ 无法解析为 JSON，使用原始文本格式: {e}")
                    # 回退到原始格式
                    discord_msg = format_simple_discord(analysis_content)
                    print(discord_msg)
                
                return json_data or analysis_content
            else:
                print("❌ 未收到有效响应")
                return None
        else:
            print("\n⚠️ 无法连接到 Grok，请检查 API Key")
            print("提示：可以手动复制下面的提示词到 Grok 官网使用")
    else:
        # 输出给用户手动复制
        print("\n" + "="*80)
        print("📤 以下提示词可以复制到 Grok 或 ChatGPT 进行分析")
        print("="*80 + "\n")
        print(prompt)
    
    return prompt


if __name__ == "__main__":
    timeframe = sys.argv[1] if len(sys.argv) > 1 else '1h'
    auto_call = len(sys.argv) > 2 and sys.argv[2] == '--auto'
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    print(f"🔍 加载涨幅榜数据 (timeframe: {timeframe})...")
    
    data = load_leaders_data(timeframe)
    
    if data is None:
        print("❌ 未找到数据，请先运行 event_monitor.py")
        sys.exit(1)
    
    print(f"✅ 已加载 {len(data['data'])} 个币种的数据")
    
    # 执行分析
    result = analyze_with_grok_integration(data, auto_call=auto_call, top_n=top_n)
    
    if result:
        print("\n✅ 分析完成！")

