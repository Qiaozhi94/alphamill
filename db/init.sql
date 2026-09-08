-- ============================================================
-- 量化交易系统 — TimescaleDB Schema
-- 自动执行于容器首次启动
-- ============================================================

-- 启用 TimescaleDB 扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================
-- 1. 核心 OHLCV 数据表 (hypertable)
-- ============================================================
CREATE TABLE ohlcv_1m (
    time          TIMESTAMPTZ NOT NULL,
    exchange      TEXT NOT NULL,
    symbol        TEXT NOT NULL,
    open          DOUBLE PRECISION NOT NULL,
    high          DOUBLE PRECISION NOT NULL,
    low           DOUBLE PRECISION NOT NULL,
    close         DOUBLE PRECISION NOT NULL,
    volume        DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (exchange, symbol, time)
);

-- 转为 hypertable, 按 1 天分区
SELECT create_hypertable('ohlcv_1m', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 加速按交易对+时间查询
CREATE INDEX idx_ohlcv_1m_symbol_time
    ON ohlcv_1m (exchange, symbol, time DESC);

-- 7 天后自动压缩, 节省 ~90% 存储
ALTER TABLE ohlcv_1m SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'exchange, symbol',
    timescaledb.compress_orderby = 'time DESC'
);
SELECT add_compression_policy('ohlcv_1m', INTERVAL '7 days');


-- ============================================================
-- 2. 多周期连续聚合视图
-- ============================================================

-- 5 分钟 K 线
CREATE MATERIALIZED VIEW ohlcv_5m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS bucket,
    exchange,
    symbol,
    FIRST(open, time)     AS open,
    MAX(high)             AS high,
    MIN(low)              AS low,
    LAST(close, time)     AS close,
    SUM(volume)           AS volume
FROM ohlcv_1m
GROUP BY bucket, exchange, symbol;

SELECT add_continuous_aggregate_policy('ohlcv_5m',
    start_offset    => INTERVAL '30 minutes',
    end_offset      => INTERVAL '5 minutes',
    schedule_interval=> INTERVAL '5 minutes'
);

-- 15 分钟 K 线
CREATE MATERIALIZED VIEW ohlcv_15m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('15 minutes', time) AS bucket,
    exchange,
    symbol,
    FIRST(open, time)     AS open,
    MAX(high)             AS high,
    MIN(low)              AS low,
    LAST(close, time)     AS close,
    SUM(volume)           AS volume
FROM ohlcv_1m
GROUP BY bucket, exchange, symbol;

SELECT add_continuous_aggregate_policy('ohlcv_15m',
    start_offset    => INTERVAL '1 hour',
    end_offset      => INTERVAL '15 minutes',
    schedule_interval=> INTERVAL '15 minutes'
);

-- 1 小时 K 线
CREATE MATERIALIZED VIEW ohlcv_1h
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    exchange,
    symbol,
    FIRST(open, time)     AS open,
    MAX(high)             AS high,
    MIN(low)              AS low,
    LAST(close, time)     AS close,
    SUM(volume)           AS volume
FROM ohlcv_1m
GROUP BY bucket, exchange, symbol;

SELECT add_continuous_aggregate_policy('ohlcv_1h',
    start_offset    => INTERVAL '6 hours',
    end_offset      => INTERVAL '1 hour',
    schedule_interval=> INTERVAL '1 hour'
);

-- 4 小时 K 线
CREATE MATERIALIZED VIEW ohlcv_4h
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('4 hours', time) AS bucket,
    exchange,
    symbol,
    FIRST(open, time)     AS open,
    MAX(high)             AS high,
    MIN(low)              AS low,
    LAST(close, time)     AS close,
    SUM(volume)           AS volume
FROM ohlcv_1m
GROUP BY bucket, exchange, symbol;

SELECT add_continuous_aggregate_policy('ohlcv_4h',
    start_offset    => INTERVAL '12 hours',
    end_offset      => INTERVAL '4 hours',
    schedule_interval=> INTERVAL '4 hours'
);

-- 日 K 线
CREATE MATERIALIZED VIEW ohlcv_1d
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    exchange,
    symbol,
    FIRST(open, time)     AS open,
    MAX(high)             AS high,
    MIN(low)              AS low,
    LAST(close, time)     AS close,
    SUM(volume)           AS volume
FROM ohlcv_1m
GROUP BY bucket, exchange, symbol;

SELECT add_continuous_aggregate_policy('ohlcv_1d',
    start_offset    => INTERVAL '3 days',
    end_offset      => INTERVAL '1 day',
    schedule_interval=> INTERVAL '1 day'
);


-- ============================================================
-- 3. 信号日志表 (审计追踪)
-- ============================================================
CREATE TABLE signals_log (
    time          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    exchange      TEXT NOT NULL,
    symbol        TEXT NOT NULL,
    source        TEXT NOT NULL,         -- 'kronos' / 'freqai' / 'technical' / 'fusion'
    signal_type   TEXT NOT NULL,         -- 'buy' / 'sell' / 'neutral'
    confidence    DOUBLE PRECISION,
    metadata      JSONB
);

CREATE INDEX idx_signals_log_time
    ON signals_log (time DESC, symbol);


-- ============================================================
-- 4. 数据质量标记表
-- ============================================================
CREATE TABLE IF NOT EXISTS ohlcv_quality_flags (
    time          TIMESTAMPTZ NOT NULL,
    exchange      TEXT NOT NULL,
    symbol        TEXT NOT NULL,
    timeframe     TEXT NOT NULL DEFAULT '1m',
    flag_type     TEXT NOT NULL,         -- 'missing_candle' / 'abnormal_price_move'
    severity      TEXT NOT NULL DEFAULT 'warning',
    observed_value DOUBLE PRECISION,
    expected_value DOUBLE PRECISION,
    metadata      JSONB NOT NULL DEFAULT '{}'::JSONB,
    detected_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at   TIMESTAMPTZ,
    PRIMARY KEY (exchange, symbol, time, timeframe, flag_type)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_quality_flags_time
    ON ohlcv_quality_flags (time DESC, symbol, flag_type);

CREATE INDEX IF NOT EXISTS idx_ohlcv_quality_flags_unresolved
    ON ohlcv_quality_flags (detected_at DESC, symbol, flag_type)
    WHERE resolved_at IS NULL;


-- ============================================================
-- 5. 历史回补进度表
-- ============================================================
CREATE TABLE IF NOT EXISTS backfill_progress (
    exchange      TEXT NOT NULL,
    symbol        TEXT NOT NULL,
    timeframe     TEXT NOT NULL,
    target_start  TIMESTAMPTZ NOT NULL,
    target_end    TIMESTAMPTZ NOT NULL,
    next_since    TIMESTAMPTZ NOT NULL,
    status        TEXT NOT NULL DEFAULT 'running',
    rows_upserted BIGINT NOT NULL DEFAULT 0,
    last_error    TEXT,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at  TIMESTAMPTZ,
    PRIMARY KEY (exchange, symbol, timeframe, target_start, target_end)
);

CREATE INDEX IF NOT EXISTS idx_backfill_progress_status
    ON backfill_progress (status, updated_at DESC);


-- ============================================================
-- 6. 交易记录表
-- ============================================================
CREATE TABLE trades_log (
    entry_time    TIMESTAMPTZ NOT NULL,
    exit_time     TIMESTAMPTZ,
    exchange      TEXT NOT NULL,
    symbol        TEXT NOT NULL,
    direction     TEXT NOT NULL,         -- 'long' / 'short'
    entry_price   DOUBLE PRECISION,
    exit_price    DOUBLE PRECISION,
    quantity      DOUBLE PRECISION,
    pnl           DOUBLE PRECISION,
    pnl_pct       DOUBLE PRECISION,
    exit_reason   TEXT,
    signals_used  JSONB
);

CREATE INDEX idx_trades_log_time
    ON trades_log (entry_time DESC);

-- ============================================================
-- 7. Dry-run 运行快照
-- ============================================================
CREATE TABLE IF NOT EXISTS dryrun_runtime_snapshots (
    time                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    open_trades         INTEGER NOT NULL,
    max_open_trades     INTEGER NOT NULL,
    total_stake         DOUBLE PRECISION NOT NULL DEFAULT 0,
    trade_count         INTEGER NOT NULL DEFAULT 0,
    closed_trade_count  INTEGER NOT NULL DEFAULT 0,
    profit_all_abs      DOUBLE PRECISION NOT NULL DEFAULT 0,
    profit_all_pct      DOUBLE PRECISION NOT NULL DEFAULT 0,
    winrate             DOUBLE PRECISION NOT NULL DEFAULT 0,
    max_drawdown_abs    DOUBLE PRECISION NOT NULL DEFAULT 0,
    max_drawdown_ratio  DOUBLE PRECISION NOT NULL DEFAULT 0,
    best_pair           TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_dryrun_runtime_snapshots_time
    ON dryrun_runtime_snapshots (time DESC);

CREATE TABLE IF NOT EXISTS dryrun_open_positions (
    snapshot_time       TIMESTAMPTZ NOT NULL,
    trade_id            BIGINT NOT NULL,
    symbol              TEXT NOT NULL,
    direction           TEXT NOT NULL,
    open_date           TIMESTAMPTZ,
    open_rate           DOUBLE PRECISION,
    current_rate        DOUBLE PRECISION,
    profit_abs          DOUBLE PRECISION,
    profit_ratio        DOUBLE PRECISION,
    stake_amount        DOUBLE PRECISION,
    metadata            JSONB NOT NULL DEFAULT '{}'::JSONB,
    PRIMARY KEY (snapshot_time, trade_id)
);

CREATE INDEX IF NOT EXISTS idx_dryrun_open_positions_time
    ON dryrun_open_positions (snapshot_time DESC, symbol);

ALTER TABLE signals_log
    ADD COLUMN IF NOT EXISTS latest_candle TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS expected_return DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS volatility DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS direction_prob DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS realized_return_60m DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS evaluated_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_signals_log_evaluation
    ON signals_log (latest_candle DESC, symbol)
    WHERE source = 'kronos';

UPDATE signals_log
SET latest_candle = COALESCE(latest_candle, (metadata->>'latest_candle')::timestamptz),
    expected_return = COALESCE(expected_return, (metadata->>'expected_return')::double precision),
    volatility = COALESCE(volatility, (metadata->>'volatility')::double precision),
    direction_prob = COALESCE(direction_prob, (metadata->>'direction_prob')::double precision)
WHERE source = 'kronos';


-- ============================================================
-- 初始化完成标记
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE 'TimescaleDB schema initialized successfully';
END $$;
