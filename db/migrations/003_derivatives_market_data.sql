-- ============================================================
-- Derivatives market microstructure data
-- Funding rates, open interest, and mark/index basis
-- ============================================================

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS derivatives_funding_rates (
    time               TIMESTAMPTZ NOT NULL,
    exchange           TEXT NOT NULL,
    symbol             TEXT NOT NULL,
    funding_rate       DOUBLE PRECISION,
    next_funding_time  TIMESTAMPTZ,
    mark_price         DOUBLE PRECISION,
    index_price        DOUBLE PRECISION,
    metadata           JSONB NOT NULL DEFAULT '{}'::JSONB,
    ingested_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (exchange, symbol, time)
);

SELECT create_hypertable(
    'derivatives_funding_rates',
    'time',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_derivatives_funding_rates_symbol_time
    ON derivatives_funding_rates (exchange, symbol, time DESC);

ALTER TABLE derivatives_funding_rates SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'exchange, symbol',
    timescaledb.compress_orderby = 'time DESC'
);

DO $$
BEGIN
    PERFORM add_compression_policy('derivatives_funding_rates', INTERVAL '30 days');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;


CREATE TABLE IF NOT EXISTS derivatives_open_interest (
    time                 TIMESTAMPTZ NOT NULL,
    exchange             TEXT NOT NULL,
    symbol               TEXT NOT NULL,
    timeframe            TEXT NOT NULL,
    open_interest        DOUBLE PRECISION,
    open_interest_value  DOUBLE PRECISION,
    base_volume          DOUBLE PRECISION,
    quote_volume         DOUBLE PRECISION,
    metadata             JSONB NOT NULL DEFAULT '{}'::JSONB,
    ingested_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (exchange, symbol, timeframe, time)
);

SELECT create_hypertable(
    'derivatives_open_interest',
    'time',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_derivatives_open_interest_symbol_time
    ON derivatives_open_interest (exchange, symbol, timeframe, time DESC);

ALTER TABLE derivatives_open_interest SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'exchange, symbol, timeframe',
    timescaledb.compress_orderby = 'time DESC'
);

DO $$
BEGIN
    PERFORM add_compression_policy('derivatives_open_interest', INTERVAL '30 days');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;


CREATE TABLE IF NOT EXISTS derivatives_mark_index_basis (
    time          TIMESTAMPTZ NOT NULL,
    exchange      TEXT NOT NULL,
    symbol        TEXT NOT NULL,
    timeframe     TEXT NOT NULL,
    mark_open     DOUBLE PRECISION,
    mark_high     DOUBLE PRECISION,
    mark_low      DOUBLE PRECISION,
    mark_close    DOUBLE PRECISION,
    index_open    DOUBLE PRECISION,
    index_high    DOUBLE PRECISION,
    index_low     DOUBLE PRECISION,
    index_close   DOUBLE PRECISION,
    basis_close   DOUBLE PRECISION,
    basis_pct     DOUBLE PRECISION,
    metadata      JSONB NOT NULL DEFAULT '{}'::JSONB,
    ingested_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (exchange, symbol, timeframe, time)
);

SELECT create_hypertable(
    'derivatives_mark_index_basis',
    'time',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_derivatives_mark_index_basis_symbol_time
    ON derivatives_mark_index_basis (exchange, symbol, timeframe, time DESC);

ALTER TABLE derivatives_mark_index_basis SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'exchange, symbol, timeframe',
    timescaledb.compress_orderby = 'time DESC'
);

DO $$
BEGIN
    PERFORM add_compression_policy('derivatives_mark_index_basis', INTERVAL '30 days');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;


CREATE TABLE IF NOT EXISTS derivatives_backfill_progress (
    exchange      TEXT NOT NULL,
    symbol        TEXT NOT NULL,
    dataset       TEXT NOT NULL,
    timeframe     TEXT NOT NULL DEFAULT 'none',
    target_start  TIMESTAMPTZ NOT NULL,
    target_end    TIMESTAMPTZ NOT NULL,
    next_since    TIMESTAMPTZ NOT NULL,
    status        TEXT NOT NULL DEFAULT 'running',
    rows_upserted BIGINT NOT NULL DEFAULT 0,
    last_error    TEXT,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at  TIMESTAMPTZ,
    PRIMARY KEY (exchange, symbol, dataset, timeframe, target_start, target_end)
);

CREATE INDEX IF NOT EXISTS idx_derivatives_backfill_progress_status
    ON derivatives_backfill_progress (status, updated_at DESC);
