import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

class BacktestEngine:
    """
    Main engine to simulate backtest using a strategy and risk rules.
    Supports both long and short positions.
    """

    def __init__(self, strategy_class, data, context, trade_logger, risk_checker):
        self.strategy = strategy_class(data, config_path=None)
        self.strategy.config = context.strategy_config
        self.data = data
        self.ctx = context
        self.trade_logger = trade_logger
        self.risk_checker = risk_checker

        self.position = None
        self.equity = context.backtest_config['initial_capital']
        self.daily_loss = 0.0
        self.current_day = None
        self.final_unrealized_position = None

    def run(self):
        logger.info("Starting backtest engine run...")
        for i in range(len(self.data)):
            time = self.data.index[i]
            price = self.data['close'].iloc[i]

            if self.current_day != time.date():
                self.current_day = time.date()
                self.daily_loss = 0
                logger.debug(f"New trading day: {self.current_day}")

            # === Exit Logic ===
            if self.position:
                entry_price = self.position['entry_price']
                qty = self.position['qty']
                direction = self.position['direction']

                logger.debug(f"Evaluating exit for position at index {i}, price {price:.2f}")

                take_profit = self.strategy.take_profit(entry_price, price) if direction == 'long' \
                    else self.strategy.take_profit(price, entry_price)
                stop_loss = self.strategy.stop_loss(entry_price, price) if direction == 'long' \
                    else self.strategy.stop_loss(price, entry_price)

                exit_signal = hasattr(self.strategy, "exit_signal") and self.strategy.exit_signal(i, entry_price)

                if take_profit:
                    logger.info(f"Take profit triggered at index {i}")
                    self._exit_trade(i, price, 'take_profit')
                elif stop_loss:
                    logger.info(f"Stop loss triggered at index {i}")
                    self._exit_trade(i, price, 'stop_loss')
                elif exit_signal:
                    logger.info(f"Exit signal triggered at index {i}")
                    self._exit_trade(i, price, 'exit_signal')

            # === Entry Logic ===
            if not self.position:
                signal = self.strategy.entry_signal(i)
                score = self.strategy.entry_score(signal)
                direction = self.strategy.entry_direction(signal)
                if score > 0 and direction in ['long', 'short']:
                    capital = self.equity * score
                    if not self.risk_checker.block_entry(capital):
                        logger.info(f"Opening new position at index {i} with signal {signal}")
                        self._enter_trade(i, price, capital, signal, direction)

        # Check for unrealized position
        if self.position:
            entry_price = self.position['entry_price']
            qty = self.position['qty']
            capital = self.position['capital']
            direction = self.position['direction']
            final_price = self.data['close'].iloc[-1]

            gross_return = (final_price - entry_price) if direction == 'long' else (entry_price - final_price)
            unrealized_pnl = gross_return * qty
            fee_pct = self.ctx.backtest_config.get('commission_pct', 0.001)
            fee_dollar = fee_pct * (entry_price + final_price) / 2 * qty
            net_pnl = unrealized_pnl - fee_dollar

            self.final_unrealized_position = {
                'entry_time': self.position['entry_time'],
                'entry_price': entry_price,
                'current_price': final_price,
                'qty': qty,
                'capital': capital,
                'direction': direction,
                'pnl_dollar': net_pnl,
                'pnl_pct': net_pnl / capital
            }
            logger.info(f"[Unrealized] Holding position at end → {self.final_unrealized_position}")

        logger.info("Backtest engine run completed.")

    def get_unrealized(self):
        return self.final_unrealized_position

    def _enter_trade(self, i, price, capital, signal, direction):
        qty = capital / price
        self.position = {
            'entry_time': self.data.index[i],
            'entry_price': price,
            'capital': capital,
            'qty': qty,
            'signal': signal,
            'direction': direction
        }
        logger.debug(f"Entered trade: {self.position}")

    def _exit_trade(self, i, price, reason):
        entry_price = self.position['entry_price']
        qty = self.position['qty']
        capital = self.position['capital']
        direction = self.position['direction']

        gross_return = (price - entry_price) if direction == 'long' else (entry_price - price)
        pnl_dollar = gross_return * qty
        fee_pct = self.ctx.backtest_config.get('commission_pct', 0.001)
        fee_dollar = fee_pct * (entry_price + price) / 2 * qty
        net_pnl = pnl_dollar - fee_dollar

        self.equity += net_pnl
        self.daily_loss += max(-net_pnl, 0)

        trade_record = {
            'entry_time': self.position['entry_time'],
            'exit_time': self.data.index[i],
            'entry_price': entry_price,
            'exit_price': price,
            'qty': qty,
            'capital': capital,
            'direction': direction,
            'pnl_pct': net_pnl / capital,
            'pnl_dollar': net_pnl,
            'signal': self.position['signal'],
            'exit_reason': reason
        }

        self.trade_logger.record(trade_record)
        logger.debug(f"Exited trade: {trade_record}")
        self.position = None
