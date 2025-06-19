import pandas as pd
import numpy as np
from indicators.vol_heatmap import VolumeHeatmapIndicator
from indicators.rsi import RSIIndicator

VOLUME_SCORE_MAP = {
    'extra_high': 1.0,
    'high': 0.75,
    'medium': 0.5,
    'normal': 0.25,
    'low': 0.0,
    'unknown': 0.0
}

class EnhancedStrengthScorer:
    def __init__(self, benchmark_df: pd.DataFrame = None, weights=None):
        self.benchmark_df = benchmark_df  # benchmark (e.g., BTC) data for relative momentum
        self.weights = weights or {
            'return': 0.3,
            'ema': 0.2,
            'volume': 0.15,
            'rsi': 0.15,
            'momentum': 0.2
        }

    def compute_log_return_score(self, df, benchmark_df=None):
        df = df.copy()
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))

        returns = {
            '1h': df['log_return'].iloc[-1],
            '4h': df['close'].iloc[-1] / df['close'].iloc[-5] - 1 if len(df) >= 5 else 0,
            '24h': df['close'].iloc[-1] / df['close'].iloc[-25] - 1 if len(df) >= 25 else 0
        }

        score = 0
        weight = {'1h': 0.5, '4h': 0.3, '24h': 0.2}
        for k, v in returns.items():
            score += np.clip(v * 10, -1, 1) * weight[k]
        return (score + 1) / 2

    def compute_ema_score(self, df):
        df['ema5'] = df['close'].ewm(span=5).mean()
        df['ema10'] = df['close'].ewm(span=10).mean()
        df['ema20'] = df['close'].ewm(span=20).mean()
        latest = df.iloc[-1]
        if latest['ema5'] > latest['ema10'] > latest['ema20']:
            return 1.0
        elif latest['ema5'] > latest['ema10'] or latest['ema10'] > latest['ema20']:
            return 0.6
        else:
            return 0.2

    def compute_volume_score(self, df: pd.DataFrame, periods: list = [1, 4, 24]) -> float:
        heatmap = VolumeHeatmapIndicator()
        df = heatmap.calculate(df)
        score = 0
        total_weight = 0
        for p in periods:
            if len(df) < p:
                continue
            segment = df.iloc[-p:]
            mapped_scores = segment['volume_category'].map(VOLUME_SCORE_MAP).dropna()
            if not mapped_scores.empty:
                score += mapped_scores.mean()
                total_weight += 1
        return score / total_weight if total_weight > 0 else 0.5

    def compute_rsi_score(self, df):
        rsi_calc = RSIIndicator(period=14)
        df = rsi_calc.calculate(df)
        rsi = df.iloc[-1]['rsi']
        if rsi >= 70:
            return 0.3
        elif rsi <= 30:
            return 1.0
        elif 50 <= rsi < 70:
            return 0.8
        elif 30 < rsi < 50:
            return 0.6
        else:
            return 0.5

    def compute_relative_momentum(self, df, benchmark_df):
        if benchmark_df is None or len(df) < 25 or len(benchmark_df) < 25:
            return 0.5

        log_return = lambda x: np.log(x / x.shift(1))
        asset_return = log_return(df['close'])
        bench_return = log_return(benchmark_df['close'])

        merged = pd.DataFrame({
            'asset': asset_return,
            'bench': bench_return
        }).dropna()

        if len(merged) < 10:
            return 0.5

        cov = merged['asset'].cov(merged['bench'])
        var = merged['bench'].var()
        beta = cov / var if var != 0 else 0
        alpha = merged['asset'].mean() - beta * merged['bench'].mean()
        return np.clip(alpha * 100, -1, 1) * 0.5 + 0.5

    def score(self, df: pd.DataFrame, symbol: str):
        try:
            return_score = self.compute_log_return_score(df)
            ema_score = self.compute_ema_score(df)
            volume_score = self.compute_volume_score(df)
            rsi_score = self.compute_rsi_score(df)
            momentum_score = self.compute_relative_momentum(df, self.benchmark_df)

            total_score = (
                return_score * self.weights['return'] +
                ema_score * self.weights['ema'] +
                volume_score * self.weights['volume'] +
                rsi_score * self.weights['rsi'] +
                momentum_score * self.weights['momentum']
            )

            return {
                'symbol': symbol,
                'return_score': round(return_score, 3),
                'ema_score': round(ema_score, 3),
                'volume_score': round(volume_score, 3),
                'rsi_score': round(rsi_score, 3),
                'momentum_score': round(momentum_score, 3),
                'final_score': round(total_score, 3)
            }
        except Exception as e:
            print(f"Error scoring {symbol}: {e}")
            return None

