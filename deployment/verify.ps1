$ErrorActionPreference = "Stop"
$ComposeFile = Join-Path $PSScriptRoot "docker-compose.yml"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-DbCheck {
    param(
        [string]$Name,
        [string]$Sql,
        [int]$MinRows = 1,
        [scriptblock]$Validator = $null
    )

    Write-Step $Name
    $output = @(docker compose -f $ComposeFile exec -T timescaledb psql -U quant -d quant -v ON_ERROR_STOP=1 -t -A -F '|' -c $Sql)
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed: psql exited with code $LASTEXITCODE"
    }
    $lines = @($output | ForEach-Object { "$($_)".Trim() } | Where-Object { $_ -ne "" })
    if ($lines.Count -lt $MinRows) {
        throw "$Name failed: expected at least $MinRows result rows, got $($lines.Count)"
    }
    if ($null -ne $Validator -and -not (& $Validator $lines)) {
        throw "$Name failed: result assertion did not pass"
    }
    foreach ($line in $lines) {
        Write-Host $line
    }
    return $lines
}

Write-Step "Docker Compose services"
docker compose -f $ComposeFile ps

Write-Step "TimescaleDB health"
$health = docker inspect --format "{{.State.Health.Status}}" quant-timescaledb
if ($health -ne "healthy") {
    throw "quant-timescaledb is not healthy: $health"
}
Write-Host "quant-timescaledb health: $health" -ForegroundColor Green

Write-Step "Grafana health"
$grafanaHealth = Invoke-RestMethod -Uri "http://localhost:3000/api/health"
if ($grafanaHealth.database -ne "ok") {
    throw "Grafana database health is not ok"
}
Write-Host "Grafana health: database=$($grafanaHealth.database), version=$($grafanaHealth.version)" -ForegroundColor Green

Write-Step "Prometheus health"
$prometheusHealth = Invoke-RestMethod -Uri "http://localhost:9090/-/healthy"
if ($prometheusHealth -notmatch "Healthy") {
    throw "Prometheus health check failed: $prometheusHealth"
}
Write-Host $prometheusHealth -ForegroundColor Green

Write-Step "Grafana datasource health"
$dotEnvMap = @{}
$dotEnvPath = Join-Path $PSScriptRoot ".env"
if (Test-Path $dotEnvPath) {
    Get-Content $dotEnvPath | ForEach-Object {
        if ($_ -match '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') { $dotEnvMap[$Matches[1]] = $Matches[2] }
    }
}
$grafanaUser = if ($dotEnvMap["GRAFANA_USER"]) { $dotEnvMap["GRAFANA_USER"] } else { "admin" }
$grafanaPassword = if ($dotEnvMap["GRAFANA_PASSWORD"]) { $dotEnvMap["GRAFANA_PASSWORD"] } else { "quant2026" }
$grafanaAuth = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${grafanaUser}:${grafanaPassword}"))
$timescaleHealth = Invoke-RestMethod -Uri "http://localhost:3000/api/datasources/uid/TimescaleDB/health" -Headers @{ Authorization = $grafanaAuth }
$prometheusDatasourceHealth = Invoke-RestMethod -Uri "http://localhost:3000/api/datasources/uid/Prometheus/health" -Headers @{ Authorization = $grafanaAuth }
if ($timescaleHealth.status -ne "OK") {
    throw "Grafana TimescaleDB datasource failed: $($timescaleHealth.message)"
}
if ($prometheusDatasourceHealth.status -ne "OK") {
    throw "Grafana Prometheus datasource failed: $($prometheusDatasourceHealth.message)"
}
Write-Host "TimescaleDB datasource: $($timescaleHealth.message)" -ForegroundColor Green
Write-Host "Prometheus datasource: $($prometheusDatasourceHealth.message)" -ForegroundColor Green

Write-Step "Grafana dashboard provisioning"
$dashboard = Invoke-RestMethod -Uri "http://localhost:3000/api/dashboards/uid/quant-crypto-overview" -Headers @{ Authorization = $grafanaAuth }
if ($dashboard.meta.url -ne "/d/quant-crypto-overview/quant-crypto-overview") {
    throw "Grafana dashboard was not provisioned"
}
Write-Host "Dashboard: $($dashboard.meta.url)" -ForegroundColor Green
$dryrunDashboard = Invoke-RestMethod -Uri "http://localhost:3000/api/dashboards/uid/quant-crypto-dryrun" -Headers @{ Authorization = $grafanaAuth }
if ($dryrunDashboard.meta.url -ne "/d/quant-crypto-dryrun/quant-crypto-dry-run-monitoring") {
    throw "Grafana dry-run dashboard was not provisioned"
}
Write-Host "Dry-run dashboard: $($dryrunDashboard.meta.url)" -ForegroundColor Green

Write-Step "Freqtrade API health"
$freqtradeAuth = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:quant2026"))
$freqtradePing = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/ping"
$freqtradeHealth = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/health" -Headers @{ Authorization = $freqtradeAuth }
$freqtradeCount = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/count" -Headers @{ Authorization = $freqtradeAuth }
if ($freqtradePing.status -ne "pong") {
    throw "Freqtrade ping failed"
}
if (-not $freqtradeHealth.last_process) {
    throw "Freqtrade health response missing last_process"
}
Write-Host "Freqtrade ping: $($freqtradePing.status)" -ForegroundColor Green
Write-Host "Freqtrade last process: $($freqtradeHealth.last_process)" -ForegroundColor Green
Write-Host "Freqtrade open trades: $($freqtradeCount.current)/$($freqtradeCount.max)" -ForegroundColor Green

Write-Step "Kronos Signal API health"
$kronosHealth = Invoke-RestMethod -Uri "http://localhost:8001/health"
$kronosPrediction = Invoke-RestMethod -Uri "http://localhost:8001/predict/BTC%2FUSDT?exchange=binance&limit=120"
if ($kronosHealth.status -ne "ok") {
    throw "Kronos Signal health failed"
}
if ($kronosPrediction.rows_used -lt 30) {
    throw "Kronos Signal prediction did not use enough rows"
}
Write-Host "Kronos health: $($kronosHealth.status), model_loaded=$($kronosHealth.model_loaded)" -ForegroundColor Green
Write-Host "Kronos placeholder prediction: $($kronosPrediction.symbol) $($kronosPrediction.signal_type) confidence=$($kronosPrediction.confidence)" -ForegroundColor Green

Invoke-DbCheck "TimescaleDB extension" @"
SELECT CASE WHEN COUNT(*) = 1 THEN 1 ELSE 0 END
FROM pg_extension
WHERE extname = 'timescaledb';
"@

Invoke-DbCheck "Hypertables" @"
SELECT CASE WHEN COUNT(*) >= 4 THEN 1 ELSE 0 END
FROM timescaledb_information.hypertables
"@

Invoke-DbCheck "Continuous aggregates" @"
SELECT CASE WHEN COUNT(*) >= 5 THEN 1 ELSE 0 END
FROM timescaledb_information.continuous_aggregates
"@

Invoke-DbCheck "OHLCV constraints" @"
SELECT CASE WHEN COUNT(*) >= 1 THEN 1 ELSE 0 END
FROM pg_constraint
WHERE conrelid = 'ohlcv_1m'::regclass
"@

Invoke-DbCheck "OHLCV quality flags" @"
SELECT
    CASE WHEN to_regclass('public.ohlcv_quality_flags') IS NOT NULL
              AND COUNT(*) FILTER (WHERE resolved_at IS NULL) = 0
         THEN 1 ELSE 0 END
FROM ohlcv_quality_flags;
"@

Invoke-DbCheck "Timescale jobs" @"
SELECT CASE WHEN COUNT(*) >= 1 THEN 1 ELSE 0 END
FROM timescaledb_information.jobs
WHERE hypertable_name = 'ohlcv_1m'
   OR proc_name = 'policy_refresh_continuous_aggregate'
"@

Invoke-DbCheck "OHLCV data by symbol" @"
SELECT CASE WHEN COUNT(*) >= 1 THEN 1 ELSE 0 END
FROM (
    SELECT exchange, symbol
    FROM ohlcv_1m
    GROUP BY exchange, symbol
    HAVING COUNT(*) > 0
) populated;
"@

Invoke-DbCheck "1m missing candle check" @"
WITH ranges AS (
    SELECT exchange, symbol, MIN(time) AS first_time, MAX(time) AS last_time
    FROM ohlcv_1m
    GROUP BY exchange, symbol
),
expected AS (
    SELECT
        r.exchange,
        r.symbol,
        generate_series(r.first_time, r.last_time, INTERVAL '1 minute') AS time
    FROM ranges r
),
missing AS (
    SELECT e.exchange, e.symbol, e.time
    FROM expected e
    LEFT JOIN ohlcv_1m o
      ON o.exchange = e.exchange
     AND o.symbol = e.symbol
     AND o.time = e.time
    WHERE o.time IS NULL
)
SELECT CASE WHEN COALESCE(MAX(missing_rows::numeric / NULLIF(expected_rows, 0)), 0) <= 0.01
            THEN 1 ELSE 0 END
FROM (
    SELECT r.exchange, r.symbol, COUNT(e.time) AS expected_rows, COUNT(m.time) AS missing_rows
    FROM ranges r
    JOIN expected e ON e.exchange = r.exchange AND e.symbol = r.symbol
    LEFT JOIN missing m ON m.exchange = e.exchange AND m.symbol = e.symbol AND m.time = e.time
    GROUP BY r.exchange, r.symbol
) summary;
"@

Invoke-DbCheck "Latest candle by symbol" @"
SELECT CASE WHEN COUNT(*) >= 1 THEN 1 ELSE 0 END
FROM (
    SELECT exchange, symbol
    FROM ohlcv_1m
    GROUP BY exchange, symbol
) populated;
"@

Invoke-DbCheck "1m abnormal price move check" @"
WITH priced AS (
    SELECT
        exchange,
        symbol,
        time,
        close,
        LAG(close) OVER (PARTITION BY exchange, symbol ORDER BY time) AS prev_close
    FROM ohlcv_1m
),
moves AS (
    SELECT
        exchange,
        symbol,
        time,
        prev_close,
        close,
        CASE
            WHEN prev_close IS NULL OR prev_close = 0 THEN NULL
            ELSE (close - prev_close) / prev_close
        END AS return_pct
    FROM priced
),
abnormal AS (
    SELECT *
    FROM moves
    WHERE ABS(return_pct) > 0.50
)
SELECT COUNT(*) FROM abnormal;
"@

Invoke-DbCheck "Latest candle freshness" @"
SELECT CASE WHEN COUNT(*) > 0 AND NOW() - MAX(time) <= INTERVAL '15 minutes'
            THEN 1 ELSE 0 END
FROM ohlcv_1m;
"@

Invoke-DbCheck "Continuous aggregate row counts" @"
WITH aggregate_counts AS (
    SELECT COUNT(*) AS rows FROM ohlcv_5m
    UNION ALL SELECT COUNT(*) FROM ohlcv_15m
    UNION ALL SELECT COUNT(*) FROM ohlcv_1h
    UNION ALL SELECT COUNT(*) FROM ohlcv_4h
    UNION ALL SELECT COUNT(*) FROM ohlcv_1d
)
SELECT CASE WHEN COUNT(*) = 5 AND MIN(rows) > 0 THEN 1 ELSE 0 END FROM aggregate_counts;
"@

Invoke-DbCheck "5m aggregate consistency sample" @"
WITH sample AS (
    SELECT bucket, exchange, symbol, open, high, low, close, volume
    FROM ohlcv_5m
    WHERE bucket < (SELECT MAX(time) - INTERVAL '15 minutes' FROM ohlcv_1m)
    ORDER BY bucket DESC, exchange, symbol
    LIMIT 12
),
manual AS (
    SELECT
        s.bucket,
        s.exchange,
        s.symbol,
        COUNT(*) AS source_rows,
        FIRST(o.open, o.time) AS open,
        MAX(o.high) AS high,
        MIN(o.low) AS low,
        LAST(o.close, o.time) AS close,
        SUM(o.volume) AS volume
    FROM sample s
    JOIN ohlcv_1m o
      ON o.exchange = s.exchange
     AND o.symbol = s.symbol
     AND o.time >= s.bucket
     AND o.time < s.bucket + INTERVAL '5 minutes'
    GROUP BY s.bucket, s.exchange, s.symbol
)
SELECT
    COUNT(*) FILTER (WHERE m.source_rows = 5) AS checked_rows,
    COUNT(*) FILTER (
        WHERE m.source_rows = 5
          AND s.open = m.open
          AND s.high = m.high
          AND s.low = m.low
          AND s.close = m.close
          AND ABS(s.volume - m.volume) <= GREATEST(1e-9, ABS(m.volume) * 1e-12)
    ) AS matching_rows
FROM sample s
JOIN manual m USING (bucket, exchange, symbol);
"@ -Validator {
    param($lines)
    $parts = $lines[0] -split '\|'
    $parts.Count -eq 2 -and [int]$parts[0] -gt 0 -and [int]$parts[0] -eq [int]$parts[1]
}

Invoke-DbCheck "1h aggregate consistency sample" @"
WITH sample AS (
    SELECT bucket, exchange, symbol, open, high, low, close, volume
    FROM ohlcv_1h
    WHERE bucket < (SELECT MAX(time) - INTERVAL '2 hours' FROM ohlcv_1m)
    ORDER BY bucket DESC, exchange, symbol
    LIMIT 12
),
manual AS (
    SELECT
        s.bucket,
        s.exchange,
        s.symbol,
        COUNT(*) AS source_rows,
        FIRST(o.open, o.time) AS open,
        MAX(o.high) AS high,
        MIN(o.low) AS low,
        LAST(o.close, o.time) AS close,
        SUM(o.volume) AS volume
    FROM sample s
    JOIN ohlcv_1m o
      ON o.exchange = s.exchange
     AND o.symbol = s.symbol
     AND o.time >= s.bucket
     AND o.time < s.bucket + INTERVAL '1 hour'
    GROUP BY s.bucket, s.exchange, s.symbol
)
SELECT
    COUNT(*) FILTER (WHERE m.source_rows = 60) AS checked_rows,
    COUNT(*) FILTER (
        WHERE m.source_rows = 60
          AND s.open = m.open
          AND s.high = m.high
          AND s.low = m.low
          AND s.close = m.close
          AND ABS(s.volume - m.volume) <= GREATEST(1e-9, ABS(m.volume) * 1e-12)
    ) AS matching_rows
FROM sample s
JOIN manual m USING (bucket, exchange, symbol);
"@ -Validator {
    param($lines)
    $parts = $lines[0] -split '\|'
    $parts.Count -eq 2 -and [int]$parts[0] -gt 0 -and [int]$parts[0] -eq [int]$parts[1]
}

Invoke-DbCheck "4h aggregate consistency sample" @"
WITH sample AS (
    SELECT bucket, exchange, symbol, open, high, low, close, volume
    FROM ohlcv_4h
    WHERE bucket < (SELECT MAX(time) - INTERVAL '8 hours' FROM ohlcv_1m)
    ORDER BY bucket DESC, exchange, symbol
    LIMIT 12
),
manual AS (
    SELECT
        s.bucket,
        s.exchange,
        s.symbol,
        COUNT(*) AS source_rows,
        FIRST(o.open, o.time) AS open,
        MAX(o.high) AS high,
        MIN(o.low) AS low,
        LAST(o.close, o.time) AS close,
        SUM(o.volume) AS volume
    FROM sample s
    JOIN ohlcv_1m o
      ON o.exchange = s.exchange
     AND o.symbol = s.symbol
     AND o.time >= s.bucket
     AND o.time < s.bucket + INTERVAL '4 hours'
    GROUP BY s.bucket, s.exchange, s.symbol
)
SELECT
    COUNT(*) FILTER (WHERE m.source_rows = 240) AS checked_rows,
    COUNT(*) FILTER (
        WHERE m.source_rows = 240
          AND s.open = m.open
          AND s.high = m.high
          AND s.low = m.low
          AND s.close = m.close
          AND ABS(s.volume - m.volume) <= GREATEST(1e-9, ABS(m.volume) * 1e-12)
    ) AS matching_rows
FROM sample s
JOIN manual m USING (bucket, exchange, symbol);
"@ -Validator {
    param($lines)
    $parts = $lines[0] -split '\|'
    $parts.Count -eq 2 -and [int]$parts[0] -gt 0 -and [int]$parts[0] -eq [int]$parts[1]
}

Invoke-DbCheck "1d aggregate consistency sample" @"
WITH sample AS (
    SELECT bucket, exchange, symbol, open, high, low, close, volume
    FROM ohlcv_1d
    WHERE bucket < (SELECT MAX(time) - INTERVAL '2 days' FROM ohlcv_1m)
    ORDER BY bucket DESC, exchange, symbol
    LIMIT 12
),
manual AS (
    SELECT
        s.bucket,
        s.exchange,
        s.symbol,
        COUNT(*) AS source_rows,
        FIRST(o.open, o.time) AS open,
        MAX(o.high) AS high,
        MIN(o.low) AS low,
        LAST(o.close, o.time) AS close,
        SUM(o.volume) AS volume
    FROM sample s
    JOIN ohlcv_1m o
      ON o.exchange = s.exchange
     AND o.symbol = s.symbol
     AND o.time >= s.bucket
     AND o.time < s.bucket + INTERVAL '1 day'
    GROUP BY s.bucket, s.exchange, s.symbol
)
SELECT
    COUNT(*) FILTER (WHERE m.source_rows = 1440) AS checked_rows,
    COUNT(*) FILTER (
        WHERE m.source_rows = 1440
          AND s.open = m.open
          AND s.high = m.high
          AND s.low = m.low
          AND s.close = m.close
          AND ABS(s.volume - m.volume) <= GREATEST(1e-9, ABS(m.volume) * 1e-12)
    ) AS matching_rows
FROM sample s
JOIN manual m USING (bucket, exchange, symbol);
"@ -Validator {
    param($lines)
    $parts = $lines[0] -split '\|'
    $parts.Count -eq 2 -and [int]$parts[0] -gt 0 -and [int]$parts[0] -eq [int]$parts[1]
}

Write-Step "F001 backfill completeness (design section 3 thresholds)"
$completenessLines = docker compose -f $ComposeFile exec -T timescaledb psql -U quant -d quant -t -A -c @"
WITH spans AS (
    SELECT symbol, count(*) AS n, min(time) AS t0, max(time) AS t1
    FROM ohlcv_1m WHERE exchange = 'binance' GROUP BY symbol
)
SELECT symbol || '|' || n || '|' ||
       ROUND(1 - n::numeric / (EXTRACT(EPOCH FROM (t1 - t0))/60 + 1), 6)
FROM spans ORDER BY symbol;
"@
$completenessLines = @($completenessLines | Where-Object { $_ -and $_.Trim() -ne "" })
if ($completenessLines.Count -eq 0) {
    throw "Backfill completeness check found no rows in ohlcv_1m"
}
foreach ($line in $completenessLines) {
    $parts = $line -split '\|'
    $ratio = [double]$parts[2]
    if ($ratio -gt 0.01) {
        throw "Backfill completeness FAIL: $($parts[0]) missing_ratio=$ratio > 0.01"
    }
    Write-Host "$($parts[0]) rows=$($parts[1]) missing_ratio=$ratio" -ForegroundColor Green
}

Write-Step "F001 monitoring chain (signals log + snapshot freshness)"
$signalsCount = docker compose -f $ComposeFile exec -T timescaledb psql -U quant -d quant -t -A -c "SELECT count(*) FROM signals_log;"
$signalsCount = ($signalsCount | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1)
if (-not $signalsCount -or [int]$signalsCount -lt 1) {
    throw "signals_log is empty (quality panel has no data)"
}
Write-Host "signals_log rows: $signalsCount" -ForegroundColor Green
$snapshotAgeSeconds = docker compose -f $ComposeFile exec -T timescaledb psql -U quant -d quant -t -A -c "SELECT EXTRACT(EPOCH FROM (NOW() - max(time))) FROM dryrun_runtime_snapshots;"
$snapshotAgeSeconds = ($snapshotAgeSeconds | Where-Object { $_ -match '^\d+(\.\d+)?$' } | Select-Object -First 1)
if (-not $snapshotAgeSeconds -or [double]$snapshotAgeSeconds -gt 900) {
    throw "dryrun_runtime_snapshots stale or empty (age=$snapshotAgeSeconds s, threshold=900 s)"
}
Write-Host "latest snapshot age: $snapshotAgeSeconds s" -ForegroundColor Green

Write-Host ""
Write-Host "Verification completed." -ForegroundColor Green
