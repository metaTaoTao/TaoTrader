#!/usr/bin/env python3
"""
综合映射表更新工具
每天定时更新币种板块和市场数据的CSV文件
支持增量更新和完整重建
"""

import csv
import sys
import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional
import logging

# 添加utils目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data.sector_data import SectorFetcher

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mapping_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MappingTableUpdater:
    def __init__(self, csv_file: str = 'coin_mapping_table.csv', server_mode: bool = False):
        self.csv_file = csv_file
        self.server_mode = server_mode  # 服务器模式使用更保守的API设置
        self.fetcher = None
        self.existing_data = {}
        
    def initialize(self):
        """初始化SectorFetcher和加载现有数据"""
        logger.info("正在初始化SectorFetcher...")
        try:
            # 根据模式选择不同的缓存文件
            cache_file = 'coingecko_cache_server.pkl' if self.server_mode else 'coingecko_cache.pkl'
            self.fetcher = SectorFetcher(cache_file=cache_file)
            logger.info("SectorFetcher初始化成功")
        except Exception as e:
            logger.error(f"❌ SectorFetcher初始化失败: {e}")
            raise
        
        # 加载现有数据
        self._load_existing_data()
    
    def _load_existing_data(self):
        """加载现有CSV文件中的数据"""
        if not os.path.exists(self.csv_file):
            logger.info(f"CSV文件 {self.csv_file} 不存在，将创建新文件")
            return
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    ticker = row['ticker']
                    self.existing_data[ticker] = row
            logger.info(f"加载了 {len(self.existing_data)} 条现有数据")
        except Exception as e:
            logger.warning(f"加载现有数据失败: {e}")
    
    def _get_csv_fieldnames(self) -> List[str]:
        """获取CSV文件的字段名"""
        return [
            'ticker', 'base_symbol', 'name', 'coingecko_id',
            'market_cap_rank', 'market_cap', 'fdv', 'volume_24h',
            'price_change_24h', 'categories', 'last_updated'
        ]
    
    def _fetch_coin_data(self, ticker: str) -> Optional[Dict]:
        """获取单个币种的数据"""
        try:
            logger.info(f"正在获取 {ticker} 的数据...")
            info = self.fetcher.get_coin_info(ticker)
            
            # 检查是否有错误
            if 'error' in info:
                logger.warning(f"获取 {ticker} 数据失败: {info['error']}")
                return None
            
            # 将categories列表转换为分号分隔的字符串
            categories_str = ';'.join(info['categories']) if info['categories'] else ''
            
            return {
                'ticker': ticker,
                'base_symbol': info['base_symbol'],
                'name': info['name'],
                'coingecko_id': info['coin_id'],
                'market_cap_rank': info['market_cap_rank'],
                'market_cap': info['market_cap'],
                'fdv': info['fully_diluted_valuation'],
                'volume_24h': info['total_volume'],
                'price_change_24h': info['price_change_24h'],
                'categories': categories_str,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"获取 {ticker} 数据时发生异常: {e}")
            return None
    
    def update_tickers(self, tickers: List[str], force_update: bool = False) -> Dict:
        """更新指定tickers的数据"""
        if not self.fetcher:
            raise Exception("请先调用initialize()方法")
        
        results = {
            'updated': 0,
            'failed': 0,
            'skipped': 0,
            'total': len(tickers)
        }
        
        updated_data = self.existing_data.copy()
        
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"[{i}/{len(tickers)}] 处理 {ticker}")
            
            # 检查是否需要更新
            if not force_update and ticker in self.existing_data:
                last_updated = self.existing_data[ticker].get('last_updated', '')
                if last_updated:
                    # 如果今天已经更新过，跳过
                    today = datetime.now().strftime('%Y-%m-%d')
                    if last_updated.startswith(today):
                        logger.info(f"  {ticker} 今天已更新，跳过")
                        results['skipped'] += 1
                        continue
            
            # 获取新数据
            coin_data = self._fetch_coin_data(ticker)
            if coin_data:
                updated_data[ticker] = coin_data
                results['updated'] += 1
                logger.info(f"  {ticker} 数据已更新")
            else:
                results['failed'] += 1
                logger.warning(f"  ❌ {ticker} 数据更新失败")
        
        # 保存更新后的数据
        self._save_data(updated_data)
        
        return results
    
    def _save_data(self, data: Dict):
        """保存数据到CSV文件"""
        fieldnames = self._get_csv_fieldnames()
        
        try:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # 按ticker排序写入
                for ticker in sorted(data.keys()):
                    writer.writerow(data[ticker])
            
            logger.info(f"数据已保存到 {self.csv_file}")
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {e}")
            raise
    
    def rebuild_table(self, tickers: List[str]):
        """完全重建映射表，分批处理以避免API限制"""
        logger.info("开始完全重建映射表...")
        logger.info("🗑️ 清空现有数据...")
        self.existing_data = {}  # 清空现有数据
        
        # 分批处理，每批3个币种，间隔更长
        batch_size = 3
        total_batches = (len(tickers) + batch_size - 1) // batch_size
        
        results = {
            'updated': 0,
            'failed': 0,
            'total': len(tickers)
        }
        
        all_data = {}
        
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            current_batch = (i // batch_size) + 1
            
            logger.info(f"📦 处理第 {current_batch}/{total_batches} 批: {batch}")
            
            # 处理当前批次的每个ticker
            for ticker in batch:
                logger.info(f"🔍 正在处理 {ticker}...")
                
                coin_data = self._fetch_coin_data(ticker)
                if coin_data:
                    all_data[ticker] = coin_data
                    results['updated'] += 1
                    logger.info(f"  ✅ {ticker} 成功")
                else:
                    results['failed'] += 1
                    logger.warning(f"  ❌ {ticker} 失败")
                
                # 每个币种间等待10秒
                if ticker != batch[-1]:  # 不是批次中的最后一个
                    logger.info(f"  ⏳ 等待10秒...")
                    time.sleep(10)
            
            # 批次间等待更长时间
            if current_batch < total_batches:
                wait_time = 90  # 批次间等待90秒
                logger.info(f"⏳ 批次间等待 {wait_time} 秒...")
                time.sleep(wait_time)
        
        # 一次性保存所有数据
        if all_data:
            logger.info(f"💾 保存 {len(all_data)} 个币种的数据...")
            self._save_data(all_data)
        
        return results
    
    def get_statistics(self) -> Dict:
        """获取映射表统计信息"""
        if not os.path.exists(self.csv_file):
            return {'total_coins': 0, 'last_update': None}
        
        total_coins = 0
        latest_update = None
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    total_coins += 1
                    update_time = row.get('last_updated')
                    if update_time and (not latest_update or update_time > latest_update):
                        latest_update = update_time
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
        
        return {
            'total_coins': total_coins,
            'last_update': latest_update,
            'file_size': os.path.getsize(self.csv_file) if os.path.exists(self.csv_file) else 0
        }

def load_tickers_from_file(file_path: str) -> List[str]:
    """从文件加载ticker列表"""
    tickers = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                data = json.load(f)
                if isinstance(data, list):
                    tickers = data
                elif isinstance(data, dict) and 'tickers' in data:
                    tickers = data['tickers']
            else:
                # 文本文件，每行一个ticker
                tickers = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"从文件 {file_path} 加载ticker失败: {e}")
    
    return tickers

def main():
    parser = argparse.ArgumentParser(
        description="币种映射表更新工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 从命令行参数更新
  python update_mapping_table.py BTCUSDT ETHUSDT MEUSDT
  
  # 从文件加载ticker列表
  python update_mapping_table.py --file tickers.txt
  python update_mapping_table.py --file tickers.json
  
  # 强制更新所有数据
  python update_mapping_table.py --file tickers.txt --force
  
  # 完全重建表
  python update_mapping_table.py --file tickers.txt --rebuild
  
  # 查看统计信息
  python update_mapping_table.py --stats
  
  # 指定输出文件
  python update_mapping_table.py --output my_mapping.csv BTCUSDT ETHUSDT
        """
    )
    
    parser.add_argument(
        'tickers',
        nargs='*',
        help='要更新的交易对列表'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='从文件加载ticker列表 (支持.txt和.json格式)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='coin_mapping_table.csv',
        help='输出CSV文件名 (默认: coin_mapping_table.csv)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制更新所有数据，忽略缓存'
    )
    
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='完全重建映射表'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='显示映射表统计信息'
    )
    
    args = parser.parse_args()
    
    # 初始化更新器
    updater = MappingTableUpdater(args.output)
    
    # 如果只是查看统计信息
    if args.stats:
        stats = updater.get_statistics()
        print(f"映射表统计信息:")
        print(f"   文件: {args.output}")
        print(f"   币种数量: {stats['total_coins']}")
        print(f"   最后更新: {stats['last_update'] or 'N/A'}")
        if 'file_size' in stats:
            print(f"   文件大小: {stats['file_size']} 字节")
        return 0
    
    # 获取ticker列表
    tickers = []
    if args.file:
        tickers = load_tickers_from_file(args.file)
        if not tickers:
            logger.error(f"从文件 {args.file} 未能加载到任何ticker")
            return 1
    elif args.tickers:
        tickers = args.tickers
    else:
        logger.error("请提供ticker列表或使用--file参数")
        parser.print_help()
        return 1
    
    logger.info(f"准备处理 {len(tickers)} 个ticker")
    
    try:
        # 初始化
        updater.initialize()
        
        # 执行更新
        if args.rebuild:
            results = updater.rebuild_table(tickers)
        else:
            results = updater.update_tickers(tickers, args.force)
        
        # 显示结果
        logger.info(f"更新完成!")
        logger.info(f"   总计: {results['total']}")
        logger.info(f"   更新: {results['updated']}")
        logger.info(f"   失败: {results['failed']}")
        logger.info(f"   跳过: {results['skipped']}")
        
        # 显示统计信息
        stats = updater.get_statistics()
        logger.info(f"当前映射表包含 {stats['total_coins']} 个币种")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("⚠️ 用户中断操作")
        return 1
    except Exception as e:
        logger.error(f"❌ 更新失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
