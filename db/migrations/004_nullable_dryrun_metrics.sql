-- F001: Freqtrade returns NULL for metrics without closed trades.
-- Preserve unknown values instead of coercing them to a misleading zero.
ALTER TABLE IF EXISTS dryrun_runtime_snapshots
    ALTER COLUMN total_stake DROP NOT NULL,
    ALTER COLUMN total_stake DROP DEFAULT,
    ALTER COLUMN trade_count DROP NOT NULL,
    ALTER COLUMN trade_count DROP DEFAULT,
    ALTER COLUMN closed_trade_count DROP NOT NULL,
    ALTER COLUMN closed_trade_count DROP DEFAULT,
    ALTER COLUMN profit_all_abs DROP NOT NULL,
    ALTER COLUMN profit_all_abs DROP DEFAULT,
    ALTER COLUMN profit_all_pct DROP NOT NULL,
    ALTER COLUMN profit_all_pct DROP DEFAULT,
    ALTER COLUMN winrate DROP NOT NULL,
    ALTER COLUMN winrate DROP DEFAULT,
    ALTER COLUMN max_drawdown_abs DROP NOT NULL,
    ALTER COLUMN max_drawdown_abs DROP DEFAULT,
    ALTER COLUMN max_drawdown_ratio DROP NOT NULL,
    ALTER COLUMN max_drawdown_ratio DROP DEFAULT;
