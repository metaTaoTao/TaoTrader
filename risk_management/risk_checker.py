class RiskChecker:
    def __init__(self, context):
        self.max_loss_pct = context.risk_config.get("max_single_trade_loss_pct", 0.02)
        self.max_drawdown_pct = context.risk_config.get("max_total_drawdown_pct", 0.2)
        self.max_daily_loss_pct = context.risk_config.get("max_daily_loss_pct", 0.05)

    def block_entry(self, size: float) -> bool:
        # 暂时简化，只实现单笔最大亏损
        # 实际应接入账户总权益、当日损失、累计回撤等
        return False  # 不拦截任何交易，后续可增强