-- 币种基础信息表
CREATE TABLE IF NOT EXISTS tickers (
    symbol TEXT PRIMARY KEY,
    base_asset TEXT,
    quote_asset TEXT,
    coingecko_id TEXT,
    category TEXT,
    logo_url TEXT,
    last_updated TEXT
);

-- 本地缓存的 K 线数据
CREATE TABLE IF NOT EXISTS kline_data (
    symbol TEXT,
    interval TEXT,
    timestamp TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    quote_volume REAL,
    PRIMARY KEY (symbol, interval, timestamp)
);

-- 币种评分结果
CREATE TABLE IF NOT EXISTS score_result (
    scan_time TEXT,
    symbol TEXT,
    return_score REAL,
    trend_score REAL,
    vol_score REAL,
    final_score REAL,
    notes TEXT,
    PRIMARY KEY (scan_time, symbol)
);

-- 每次选出的强势币
CREATE TABLE IF NOT EXISTS selected_tokens (
    scan_time TEXT,
    symbol TEXT,
    rank INTEGER,
    PRIMARY KEY (scan_time, symbol)
);

-- 回测记录表（可选）
CREATE TABLE IF NOT EXISTS backtest_log (
    run_id TEXT PRIMARY KEY,
    strategy_name TEXT,
    param_json TEXT,
    start_time TEXT,
    end_time TEXT,
    pnl REAL,
    win_rate REAL
);

-- 币种与分类的多对多关系表
CREATE TABLE IF NOT EXISTS categories (
    symbol TEXT,
    category TEXT,
    PRIMARY KEY (symbol, category)
);

