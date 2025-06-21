import requests
import pandas as pd
from datetime import datetime, timedelta

class FundFlowScorer:
    BASE_URL = "https://api.llama.fi"

    def fetch_chains_data(self) -> pd.DataFrame:
        url = f"{self.BASE_URL}/v2/chains"
        resp = requests.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch /v2/chains: {resp.status_code}")
        data = resp.json()
        df = pd.DataFrame(data)
        df['change_1d'] = None  # Placeholder as not present in API response
        df['change_7d'] = None
        return df[['name', 'tvl', 'change_1d', 'change_7d']]

    def fetch_protocols_data(self) -> pd.DataFrame:
        url = f"{self.BASE_URL}/protocols"
        resp = requests.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch protocols data: {resp.status_code}")
        df = pd.DataFrame(resp.json())
        df['change_1d'] = df.get('change_1d', pd.Series([None] * len(df)))
        df['change_7d'] = df.get('change_7d', pd.Series([None] * len(df)))
        return df

    def fetch_protocol_tvl_history(self, slug: str) -> pd.DataFrame:
        url = f"{self.BASE_URL}/protocol/{slug}"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Failed to fetch history for {slug}")
            return None
        data = resp.json().get("tvl", [])
        df = pd.DataFrame(data)
        if df.empty:
            return None
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df = df.sort_values('date')
        return df

    def compute_tvl_change(self, df: pd.DataFrame) -> tuple:
        if df is None or len(df) < 8:
            return None, None
        today_tvl = df.iloc[-1]['totalLiquidityUSD']
        day_ago_tvl = df[df['date'] <= (df.iloc[-1]['date'] - timedelta(days=1))]['totalLiquidityUSD'].iloc[-1]
        week_ago_tvl = df[df['date'] <= (df.iloc[-1]['date'] - timedelta(days=7))]['totalLiquidityUSD'].iloc[-1]
        change_1d = (today_tvl - day_ago_tvl) / day_ago_tvl * 100
        change_7d = (today_tvl - week_ago_tvl) / week_ago_tvl * 100
        return change_1d, change_7d

    def score_chain(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['raw_score'] = df['change_1d'].fillna(0) + 0.5 * df['change_7d'].fillna(0)
        df['fund_flow_score'] = self._normalize_score(df['raw_score'])
        return df[['name', 'tvl', 'change_1d', 'change_7d', 'fund_flow_score']]

    def score_protocol(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['raw_score'] = df['change_1d'].fillna(0) + 0.5 * df['change_7d'].fillna(0)
        df['fund_flow_score'] = self._normalize_score(df['raw_score'])
        return df[['name', 'symbol', 'tvl', 'change_1d', 'change_7d', 'fund_flow_score']]

    def _normalize_score(self, series: pd.Series) -> pd.Series:
        min_val, max_val = series.min(), series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return 100 * (series - min_val) / (max_val - min_val)

    def match_token_to_protocol(self, token_symbol: str, protocol_df: pd.DataFrame) -> str:
        match = protocol_df[protocol_df['symbol'].str.upper() == token_symbol.upper()]
        if not match.empty:
            return match.iloc[0]['name']
        return None

if __name__ == "__main__":
    scorer = FundFlowScorer()

    protocol_df = scorer.fetch_protocols_data().head(50)  # Limit to top 50 for testing
    for _, row in protocol_df.iterrows():
        slug = row.get('slug')
        if not slug:
            continue
        history_df = scorer.fetch_protocol_tvl_history(slug)
        change_1d, change_7d = scorer.compute_tvl_change(history_df)
        protocol_df.loc[protocol_df['slug'] == slug, 'change_1d'] = change_1d
        protocol_df.loc[protocol_df['slug'] == slug, 'change_7d'] = change_7d

    scored_protocols = scorer.score_protocol(protocol_df)
    print("Top Protocols by TVL Momentum:")
    print(scored_protocols.sort_values(by="fund_flow_score", ascending=False).head())