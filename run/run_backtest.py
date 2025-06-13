import pandas as pd
from data.market_data import OKXDataFetcher
from core.context import BacktestContext
from core.strategy_registry import StrategyRegistry
from backtest.backtest_engine import BacktestEngine
from backtest.performance_metrics import analyze_performance
from execution.trade_logger import TradeLogger
from risk_management.risk_checker import RiskChecker
from utils.plots import plot_pnl_curve, plot_signals_on_price
from backtest.reporter import generate_markdown_report
from core.strategy_loader import load_all_strategies
from utils.logger import get_logger

logger = get_logger(__name__)

def run():
    logger.info("Starting backtest run...")

    # 1. 获取K线数据
    fetcher = OKXDataFetcher()
    df = fetcher.get_kline('BTC-USDT-SWAP', bar='1H')
    logger.info(f"Fetched {len(df)} rows of K-line data.")

    # 2. 加载配置
    ctx = BacktestContext(
        strategy_config_path='configs/strategy/ma_crossover.yaml',
        backtest_config_path='configs/backtest.yaml',
        risk_config_path='configs/risk.yaml'
    )
    logger.info("Loaded backtest context with strategy, backtest, and risk config.")

    # 3. 加载策略类
    strategy_cls = StrategyRegistry.get("MA_Crossover")
    logger.info(f"Loaded strategy class: {strategy_cls.__name__}")

    # 4. 初始化日志和风控
    trade_logger = TradeLogger()
    risk_checker = RiskChecker(ctx)
    logger.info("Initialized trade logger and risk checker.")

    # 5. 初始化并运行回测
    engine = BacktestEngine(
        strategy_class=strategy_cls,
        data=df,
        context=ctx,
        trade_logger=trade_logger,
        risk_checker=risk_checker
    )
    logger.info("Backtest engine initialized. Starting engine run...")
    engine.run()
    unrealized = engine.get_unrealized()

    # 6. 分析绩效
    trades_df = trade_logger.to_dataframe()
    perf = analyze_performance(trades_df, unrealized=unrealized)
    logger.info("Performance analysis complete.")

    # 7. 输出结果
    logger.info("==== Performance Summary ====")
    logger.info(perf)

    # 8. 可视化（买卖点、收益曲线）
    if not trades_df.empty:
        plot_signals_on_price(df, trades_df)
        plot_pnl_curve(trades_df)
        logger.info("Plotted signals and PnL curve.")
        generate_markdown_report(trades_df, perf, engine.get_unrealized())
        logger.info("Generated Markdown performance report.")
        # generate_html_report(trades_df, perf)
    else:
        logger.warning("No trades executed. Skipping plots and reports.")

if __name__ == "__main__":
    load_all_strategies()
    run()
