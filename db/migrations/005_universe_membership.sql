-- F008：point-in-time 宇宙台账与质量门判定记录（只追加）。
--
-- 两条独立时间线（spec §5 不变量）：
--   1. universe_membership = 标的**可交易期**的状态迁移（listed / delisted / initial_seed）；
--   2. universe_quality_verdicts = **准入状态**（ACTIVE / QUARANTINED / INCOMPLETE），
--      最新一条（judged_at, id）是当前准入状态，是导出清单的唯一准入通道。
--
-- 两张表都只有 INSERT 路径：UPDATE / DELETE 被触发器拒绝；同一 pair 的 valid_from
-- 严格递增（追加序即时间序）。runner 约束：本文件必须幂等且不含非事务语句。

CREATE TABLE IF NOT EXISTS universe_membership (
    id            BIGSERIAL PRIMARY KEY,
    exchange      TEXT        NOT NULL,
    market_type   TEXT        NOT NULL,
    db_symbol     TEXT        NOT NULL,
    lake_pair     TEXT        NOT NULL,
    valid_from    TIMESTAMPTZ NOT NULL,
    valid_to      TIMESTAMPTZ,
    reason        TEXT        NOT NULL,
    universe_id   TEXT        NOT NULL,
    ingested_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT universe_membership_reason_chk
        CHECK (reason IN ('listed', 'delisted', 'initial_seed')),
    CONSTRAINT universe_membership_window_chk
        CHECK (valid_to IS NULL OR valid_to > valid_from)
);

CREATE INDEX IF NOT EXISTS universe_membership_pair_from_idx
    ON universe_membership (lake_pair, valid_from);

CREATE INDEX IF NOT EXISTS universe_membership_symbol_idx
    ON universe_membership (exchange, market_type, db_symbol, valid_from);

CREATE OR REPLACE FUNCTION universe_membership_reject_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'universe_membership 只追加（%）：历史区间不可改写，变更以新区间表达', TG_OP;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS universe_membership_no_mutation ON universe_membership;
CREATE TRIGGER universe_membership_no_mutation
    BEFORE UPDATE OR DELETE ON universe_membership
    FOR EACH ROW EXECUTE FUNCTION universe_membership_reject_mutation();

CREATE OR REPLACE FUNCTION universe_membership_require_increasing() RETURNS trigger AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM universe_membership m
        WHERE m.lake_pair = NEW.lake_pair
          AND m.valid_from >= NEW.valid_from
    ) THEN
        RAISE EXCEPTION
            'universe_membership 追加序非法：% 已存在 valid_from >= % 的记录（区间不得重叠、不得回填历史）',
            NEW.lake_pair, NEW.valid_from;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS universe_membership_increasing ON universe_membership;
CREATE TRIGGER universe_membership_increasing
    BEFORE INSERT ON universe_membership
    FOR EACH ROW EXECUTE FUNCTION universe_membership_require_increasing();

CREATE TABLE IF NOT EXISTS universe_quality_verdicts (
    id            BIGSERIAL PRIMARY KEY,
    universe_id   TEXT        NOT NULL,
    exchange      TEXT        NOT NULL,
    market_type   TEXT        NOT NULL,
    db_symbol     TEXT        NOT NULL,
    lake_pair     TEXT        NOT NULL,
    verdict       TEXT        NOT NULL,
    reason_code   TEXT,
    metrics       JSONB       NOT NULL,
    judged_at     TIMESTAMPTZ NOT NULL,
    hostname      TEXT        NOT NULL,
    CONSTRAINT universe_quality_verdicts_verdict_chk
        CHECK (verdict IN ('ACTIVE', 'QUARANTINED', 'INCOMPLETE')),
    CONSTRAINT universe_quality_verdicts_reason_chk
        CHECK ((verdict = 'ACTIVE') = (reason_code IS NULL))
);

CREATE INDEX IF NOT EXISTS universe_quality_verdicts_pair_idx
    ON universe_quality_verdicts (lake_pair, judged_at DESC, id DESC);

CREATE OR REPLACE FUNCTION universe_quality_verdicts_reject_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'universe_quality_verdicts 只追加（%）：准入状态以新判定表达', TG_OP;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS universe_quality_verdicts_no_mutation ON universe_quality_verdicts;
CREATE TRIGGER universe_quality_verdicts_no_mutation
    BEFORE UPDATE OR DELETE ON universe_quality_verdicts
    FOR EACH ROW EXECUTE FUNCTION universe_quality_verdicts_reject_mutation();
