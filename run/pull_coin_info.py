#!/usr/bin/env python3
"""
pull_coin_info.py - 币种信息拉取服务
专为服务器定时任务设计，使用超保守的API调用策略
"""

import sys
import os
import time
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from update_mapping_table import MappingTableUpdater, load_tickers_from_file
from data.binance_fetcher import BinanceDataFetcher

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'pull_coin_info_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_default_tickers():
    """加载默认的ticker列表"""
    # 默认的主流币种列表
    default_tickers = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
        'SOLUSDT', 'DOTUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT',
        'UNIUSDT', 'LTCUSDT', 'ATOMUSDT', 'NEARUSDT', 'ALGOUSDT',
        'VETUSDT', 'ICPUSDT', 'FILUSDT', 'TRXUSDT', 'ETCUSDT',
        'XLMUSDT', 'BCHUSDT', 'MANAUSDT', 'SANDUSDT', 'AXSUSDT',
        'THETAUSDT', 'FTMUSDT', 'EGLDUSDT', 'AAVEUSDT', 'EOSUSDT',
        'XTZUSDT', 'FLOWUSDT', 'KLAYUSDT', 'KSMUSDT', 'WAVESUSDT',
        'ZILUSDT', 'BATUSDT', 'ZECUSDT', 'DASHUSDT', 'COMPUSDT',
        'YFIUSDT', 'SNXUSDT', 'MKRUSDT', 'UMAUSDT', 'BALUSDT',
        'CRVUSDT', '1INCHUSDT', 'SUSHIUSDT', 'ENJUSDT', 'CHZUSDT'
    ]
    return default_tickers

def full_rebuild_pull(tickers, output_file='coin_mapping_table.csv'):
    """
    完全重建模式的数据拉取
    每次运行都重新拉取所有币种信息，确保数据完整性和一致性
    """
    logger = logging.getLogger(__name__)
    
    logger.info(f"🚀 开始完全重建模式数据拉取")
    logger.info(f"📊 目标币种数量: {len(tickers)}")
    logger.info(f"💾 输出文件: {output_file}")
    logger.info(f"🔄 模式: 完全重建（覆盖现有数据）")
    
    # 备份现有文件（如果存在）
    if os.path.exists(output_file):
        backup_file = f"{output_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy(output_file, backup_file)
        logger.info(f"💾 已备份现有文件: {backup_file}")
    
    # 初始化更新器（服务器模式）
    updater = MappingTableUpdater(output_file, server_mode=True)
    
    try:
        # 初始化（这步可能需要较长时间）
        logger.info("🔧 正在初始化SectorFetcher...")
        updater.initialize()
        logger.info("✅ SectorFetcher初始化完成")
        
        # 完全重建映射表
        logger.info("🗑️ 清空现有映射表，开始重建...")
        results = updater.rebuild_table(tickers)
        
        # 最终统计
        logger.info(f"🎉 完全重建完成!")
        logger.info(f"📊 总计: {results['total']} 个币种")
        logger.info(f"✅ 成功: {results['updated']}")
        logger.info(f"❌ 失败: {results['failed']}")
        
        if results['total'] > 0:
            success_rate = results['updated'] / results['total'] * 100
            logger.info(f"📈 成功率: {success_rate:.1f}%")
        
        # 显示最终统计
        stats = updater.get_statistics()
        logger.info(f"📋 最终映射表: {stats['total_coins']} 个币种")
        logger.info(f"🕒 更新时间: {stats['last_update']}")
        
        return results['updated'], results['failed']
        
    except Exception as e:
        logger.error(f"❌ 数据拉取过程出现严重错误: {e}")
        return 0, len(tickers)

def main():
    """主函数"""
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("🚀 TaoTrader 币种信息拉取服务启动")
    logger.info(f"📅 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 1. 获取ticker列表
    logger.info("🔍 正在从Binance获取所有USDT交易对...")
    
    try:
        binance_fetcher = BinanceDataFetcher()
        
        # 获取所有USDT交易对
        all_tickers = binance_fetcher.get_all_usdt_pairs()
        
        if not all_tickers:
            logger.error("❌ 无法从Binance获取交易对，使用备用方案")
            # 尝试从文件加载
            ticker_sources = ['tickers.json', 'tickers.txt']
            tickers = None
            for source in ticker_sources:
                if os.path.exists(source):
                    tickers = load_tickers_from_file(source)
                    if tickers:
                        logger.info(f"📄 使用备用文件: {source}")
                        break
            
            if not tickers:
                logger.error("❌ 无法获取任何ticker列表")
                return 2
        else:
            tickers = all_tickers
            logger.info(f"✅ 从Binance获取到 {len(tickers)} 个USDT交易对")
            
            # 保存ticker列表到文件作为备份
            binance_fetcher.save_tickers_to_file(tickers, 'binance_usdt_pairs.json')
            logger.info("💾 已保存ticker列表到 binance_usdt_pairs.json")
    
    except Exception as e:
        logger.error(f"❌ 获取Binance交易对失败: {e}")
        logger.info("🔄 尝试使用本地备份文件...")
        
        # 使用本地备份
        backup_sources = ['binance_usdt_pairs.json', 'tickers.json', 'tickers.txt']
        tickers = None
        for source in backup_sources:
            if os.path.exists(source):
                tickers = load_tickers_from_file(source)
                if tickers:
                    logger.info(f"📄 使用备份文件: {source}")
                    break
        
        if not tickers:
            logger.error("❌ 无法获取任何ticker列表")
            return 2
    
    logger.info(f"🎯 最终币种数量: {len(tickers)}")
    logger.info(f"📋 前10个币种: {tickers[:10]}")
    
    # 2. 执行完全重建拉取
    start_time = datetime.now()
    success_count, failed_count = full_rebuild_pull(tickers)
    end_time = datetime.now()
    
    duration = end_time - start_time
    
    # 3. 最终报告
    logger.info("=" * 60)
    logger.info("📊 执行完成报告")
    logger.info(f"⏱️ 总耗时: {duration}")
    logger.info(f"✅ 成功: {success_count}")
    logger.info(f"❌ 失败: {failed_count}")
    logger.info(f"📈 成功率: {success_count/(success_count+failed_count)*100:.1f}%")
    
    # 4. 创建备份
    try:
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = f"{backup_dir}/coin_mapping_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        if os.path.exists('coin_mapping_table.csv'):
            import shutil
            shutil.copy('coin_mapping_table.csv', backup_file)
            logger.info(f"💾 已创建备份: {backup_file}")
    except Exception as e:
        logger.warning(f"⚠️ 备份创建失败: {e}")
    
    logger.info("=" * 60)
    
    # 5. 返回退出码
    if failed_count == 0:
        logger.info("🎉 所有数据拉取成功!")
        return 0
    elif success_count > 0:
        logger.warning(f"⚠️ 部分数据拉取失败 ({failed_count} 个)")
        return 1
    else:
        logger.error("❌ 所有数据拉取失败!")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
