import sqlite3
import pandas as pd
import os
from typing import Optional
from datetime import datetime


class DBManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 自动定位到 database 文件夹里的数据库
            db_path = os.path.join(os.path.dirname(__file__), "taotrader.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_ticker(self, symbol: str) -> Optional[dict]:
        self.cursor.execute("SELECT * FROM tickers WHERE symbol = ?", (symbol,))
        row = self.cursor.fetchone()
        if row:
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, row))
        return None

    def get_all_categories(self) -> pd.DataFrame:
        query = "SELECT symbol, category FROM categories"
        return pd.read_sql_query(query, self.conn)

    def insert_ticker(self, symbol, base_asset, quote_asset, coingecko_id, category=None, logo_url=None):
        now = datetime.utcnow().isoformat()
        self.cursor.execute("""
            INSERT OR IGNORE INTO tickers (symbol, base_asset, quote_asset, coingecko_id, category, logo_url, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (symbol, base_asset, quote_asset, coingecko_id, category, logo_url, now))
        self.conn.commit()

    def insert_ticker_if_missing(self, symbol, base_asset, quote_asset, coingecko_id, categories=None, logo_url=None):
        existing = self.get_ticker(symbol)
        if existing:
            return
        now = datetime.utcnow().isoformat()
        self.cursor.execute("""
            INSERT INTO tickers (symbol, base_asset, quote_asset, coingecko_id, logo_url, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (symbol, base_asset, quote_asset, coingecko_id, logo_url, now))
        self.conn.commit()

        # Insert into ticker_category if categories exist
        if categories:
            for cat in categories:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO ticker_category (symbol, category)
                    VALUES (?, ?)
                """, (symbol, cat))
            self.conn.commit()

    def get_tickers_missing_category(self):
        self.cursor.execute("SELECT symbol, base_asset FROM tickers WHERE category IS NULL")
        rows = self.cursor.fetchall()
        return [dict(zip([desc[0] for desc in self.cursor.description], row)) for row in rows]

    def update_last_updated(self, symbol: str):
        now = datetime.utcnow().isoformat()
        self.cursor.execute("UPDATE tickers SET last_updated = ? WHERE symbol = ?", (now, symbol))
        self.conn.commit()

    def insert_categories(self, symbol: str, categories: list[str]):
        for category in categories:
            self.cursor.execute("""
                INSERT OR IGNORE INTO categories (symbol, category)
                VALUES (?, ?)
            """, (symbol, category))
        self.conn.commit()

    def get_symbols_by_category(self, category: str) -> list[str]:
        self.cursor.execute("""
            SELECT symbol FROM categories WHERE category = ?
        """, (category,))
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def insert_kline(self, symbol: str, interval: str, df: pd.DataFrame):
        df["symbol"] = symbol
        df["interval"] = interval
        df.to_sql("kline_data", self.conn, if_exists="append", index=False)

    def query_kline(self, symbol: str, interval: str) -> pd.DataFrame:
        query = """
            SELECT * FROM kline_data
            WHERE symbol = ? AND interval = ?
            ORDER BY timestamp ASC
        """
        return pd.read_sql_query(query, self.conn, params=(symbol, interval))

    def insert_score(self, symbol: str, factor_name: str, score: float):
        self.cursor.execute("""
            INSERT INTO coin_scores (symbol, factor_name, score, timestamp)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (symbol, factor_name, score))
        self.conn.commit()

    def get_categories_for_symbol(self, symbol: str) -> list:
        self.cursor.execute("SELECT category FROM ticker_category WHERE symbol = ?", (symbol,))
        rows = self.cursor.fetchall()
        return [r[0] for r in rows]

    def get_symbols_for_category(self, category: str) -> list:
        self.cursor.execute("SELECT symbol FROM ticker_category WHERE category = ?", (category,))
        rows = self.cursor.fetchall()
        return [r[0] for r in rows]

    def close(self):
        self.conn.close()
