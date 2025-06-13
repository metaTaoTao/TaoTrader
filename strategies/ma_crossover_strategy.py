from strategies.base_strategy import BaseStrategy
from core.strategy_registry import StrategyRegistry
from utils.logger import get_logger

logger = get_logger(__name__)

class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    策略名称：MA Crossover 策略（双均线金叉策略）

    策略逻辑：
    - 当短期均线从下向上穿越长期均线（即金叉），触发买入信号；
    - 若该交叉点成交量大于过去10根K线均值的若干倍（volume_multiplier），认为是强买入；
    - 若没有成交量放大，但仍满足金叉，则认为是中等强度买入；
    - 止损与止盈按照固定比例（配置文件中设定）触发。

    信号返回格式：
    - 'long_strong' 表示强买入
    - 'long_medium' 表示中等买入
    - None 表示无信号（观望）

    注意：当前版本仅支持做多，后续可扩展做空逻辑。
    """

    def __init__(self, data, config_path=None):
        super().__init__(data, config_path)

    def entry_signal(self, index: int) -> str:
        if index < self.config['long_window']:
            return None

        short_ma = self.data['close'].rolling(self.config['short_window']).mean()
        long_ma = self.data['close'].rolling(self.config['long_window']).mean()
        vol = self.data['volume']
        vol_mean = vol.rolling(10).mean()

        logger.debug(
            f"[index={index}] short_ma={short_ma.iloc[index]:.2f}, long_ma={long_ma.iloc[index]:.2f}, vol={vol.iloc[index]:.2f}, mean_vol={vol_mean.iloc[index]:.2f}"
        )

        if (short_ma.iloc[index - 1] < long_ma.iloc[index - 1] and
                short_ma.iloc[index] > long_ma.iloc[index] and
                vol.iloc[index] > vol_mean.iloc[index] * self.config['volume_multiplier']):
            logger.info(f"[Signal] Strong crossover at index {index} → long_strong")
            return 'long_strong'

        if (short_ma.iloc[index - 1] < long_ma.iloc[index - 1] and
                short_ma.iloc[index] > long_ma.iloc[index]):
            logger.info(f"[Signal] Medium crossover at index {index} → long_medium")
            return 'long_medium'

        return None

    def stop_loss(self, entry_price: float, current_price: float) -> bool:
        loss_triggered = current_price < entry_price * (1 - self.config['stop_loss_pct'])
        if loss_triggered:
            logger.info(f"[Stop Loss] Triggered at price {current_price:.2f} (entry={entry_price:.2f})")
        return loss_triggered

    def take_profit(self, entry_price: float, current_price: float) -> bool:
        profit_triggered = current_price > entry_price * (1 + self.config['take_profit_pct'])
        if profit_triggered:
            logger.info(f"[Take Profit] Triggered at price {current_price:.2f} (entry={entry_price:.2f})")
        return profit_triggered

    def exit_signal(self, index: int, entry_price: float) -> bool:
        # 当前策略不使用额外的出场信号逻辑
        return False

# 注册到策略中心
StrategyRegistry.register("MA_Crossover", MovingAverageCrossoverStrategy)
