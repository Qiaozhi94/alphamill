param(
    [string]$KronosHostUrl = "http://127.0.0.1:8002",
    [string]$Exchange = $(if ($env:KRONOS_SIGNAL_EXCHANGE) { $env:KRONOS_SIGNAL_EXCHANGE } else { "binance" }),
    [string[]]$Symbols = @("BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT")
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

function ConvertTo-SqlLiteral {
    param([AllowNull()]$Value)
    if ($null -eq $Value) {
        return "NULL"
    }
    return "'" + "$Value".Replace("'", "''") + "'"
}

function ConvertTo-SqlNumber {
    param([AllowNull()]$Value)
    if ($null -eq $Value -or "$Value" -eq "") {
        return "NULL"
    }
    return ([Convert]::ToDouble($Value)).ToString([Globalization.CultureInfo]::InvariantCulture)
}

function Read-DotEnv {
    param([string]$Path)
    $values = @{}
    if (Test-Path $Path) {
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
                $values[$Matches[1]] = $Matches[2].Trim().Trim('"').Trim("'")
            }
        }
    }
    return $values
}

function Invoke-DbSql {
    param([string]$Sql)
    $Sql | docker exec -i quant-timescaledb psql -v ON_ERROR_STOP=1 -U quant -d quant | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Database write failed with exit code $LASTEXITCODE"
    }
}

$dotEnv = Read-DotEnv (Join-Path $projectRoot "deployment/.env")
$snapshotMigration = Join-Path $projectRoot "db/migrations/004_nullable_dryrun_metrics.sql"
if (-not (Test-Path $snapshotMigration)) {
    throw "Runtime snapshot migration is missing: $snapshotMigration"
}
Invoke-DbSql (Get-Content $snapshotMigration -Raw)

$freqtradeUser = if ($dotEnv["FREQTRADE_API_USERNAME"]) { $dotEnv["FREQTRADE_API_USERNAME"] } else { $env:FREQTRADE_API_USERNAME }
$freqtradePassword = if ($dotEnv["FREQTRADE_API_PASSWORD"]) { $dotEnv["FREQTRADE_API_PASSWORD"] } else { $env:FREQTRADE_API_PASSWORD }
if (-not $freqtradeUser -or -not $freqtradePassword) {
    throw "FREQTRADE_API_USERNAME and FREQTRADE_API_PASSWORD must be configured"
}
$credentials = "${freqtradeUser}:${freqtradePassword}"
$auth = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($credentials))
$headers = @{ Authorization = $auth }
$snapshotTime = (Get-Date).ToUniversalTime().ToString("o")

$count = Invoke-RestMethod -Uri "http://127.0.0.1:8080/api/v1/count" -Headers $headers -TimeoutSec 15
$status = @(Invoke-RestMethod -Uri "http://127.0.0.1:8080/api/v1/status" -Headers $headers -TimeoutSec 15)
$profit = Invoke-RestMethod -Uri "http://127.0.0.1:8080/api/v1/profit" -Headers $headers -TimeoutSec 15

$runtimeSql = @"
INSERT INTO dryrun_runtime_snapshots (
    time, open_trades, max_open_trades, total_stake, trade_count, closed_trade_count,
    profit_all_abs, profit_all_pct, winrate, max_drawdown_abs, max_drawdown_ratio, best_pair
) VALUES (
    $(ConvertTo-SqlLiteral $snapshotTime),
    $([int]$count.current),
    $([int]$count.max),
    $(ConvertTo-SqlNumber $count.total_stake),
    $([int]$profit.trade_count),
    $([int]$profit.closed_trade_count),
    $(ConvertTo-SqlNumber $profit.profit_all_coin),
    $(ConvertTo-SqlNumber $profit.profit_all_percent),
    $(ConvertTo-SqlNumber $profit.winrate),
    $(ConvertTo-SqlNumber $profit.max_drawdown_abs),
    $(ConvertTo-SqlNumber $profit.max_drawdown),
    $(ConvertTo-SqlLiteral $profit.best_pair)
);
"@
Invoke-DbSql $runtimeSql

foreach ($trade in @($status | Where-Object { $_ -and $null -ne $_.trade_id -and $_.pair })) {
    $direction = if ($trade.is_short) { "short" } else { "long" }
    $positionSql = @"
INSERT INTO dryrun_open_positions (
    snapshot_time, trade_id, symbol, direction, open_date, open_rate, current_rate,
    profit_abs, profit_ratio, stake_amount
) VALUES (
    $(ConvertTo-SqlLiteral $snapshotTime),
    $([long]$trade.trade_id),
    $(ConvertTo-SqlLiteral $trade.pair),
    $(ConvertTo-SqlLiteral $direction),
    $(ConvertTo-SqlLiteral $trade.open_date),
    $(ConvertTo-SqlNumber $trade.open_rate),
    $(ConvertTo-SqlNumber $trade.current_rate),
    $(ConvertTo-SqlNumber $trade.profit_abs),
    $(ConvertTo-SqlNumber $trade.profit_ratio),
    $(ConvertTo-SqlNumber $trade.stake_amount)
);
"@
    Invoke-DbSql $positionSql
}

foreach ($symbol in $Symbols) {
    $encodedSymbol = [Uri]::EscapeDataString($symbol)
    try {
        $prediction = Invoke-RestMethod -Uri "$KronosHostUrl/predict/$encodedSymbol`?exchange=$Exchange&limit=256" -TimeoutSec 30
    }
    catch {
        $errorMetadata = @{
            error = $_.Exception.Message
        } | ConvertTo-Json -Compress
        $errorSql = @"
INSERT INTO signals_log (time, exchange, symbol, source, signal_type, confidence, metadata)
VALUES (
    $(ConvertTo-SqlLiteral $snapshotTime),
    '$Exchange',
    $(ConvertTo-SqlLiteral $symbol),
    'kronos_error',
    'error',
    0,
    $(ConvertTo-SqlLiteral $errorMetadata)::jsonb
);
"@
        Invoke-DbSql $errorSql
        Write-Warning "Kronos prediction failed symbol=$symbol error=$($_.Exception.Message)"
        continue
    }
    $metadata = @{
        expected_return = $prediction.expected_return
        volatility = $prediction.volatility
        direction_prob = $prediction.direction_prob
        rows_used = $prediction.rows_used
        latest_candle = $prediction.latest_candle
        reason = $prediction.reason
    } | ConvertTo-Json -Compress
    $signalSql = @"
INSERT INTO signals_log (
    time, exchange, symbol, source, signal_type, confidence, metadata,
    latest_candle, expected_return, volatility, direction_prob
)
VALUES (
    $(ConvertTo-SqlLiteral $snapshotTime),
    $(ConvertTo-SqlLiteral $prediction.exchange),
    $(ConvertTo-SqlLiteral $prediction.symbol),
    $(ConvertTo-SqlLiteral $prediction.source),
    $(ConvertTo-SqlLiteral $prediction.signal_type),
    $(ConvertTo-SqlNumber $prediction.confidence),
    $(ConvertTo-SqlLiteral $metadata)::jsonb,
    $(ConvertTo-SqlLiteral $prediction.latest_candle),
    $(ConvertTo-SqlNumber $prediction.expected_return),
    $(ConvertTo-SqlNumber $prediction.volatility),
    $(ConvertTo-SqlNumber $prediction.direction_prob)
);
"@
    Invoke-DbSql $signalSql
}

$evaluationSql = @"
UPDATE signals_log s
SET realized_return_60m = (future.close / current.close) - 1,
    evaluated_at = NOW()
FROM ohlcv_1m current, ohlcv_1m future
WHERE s.source = 'kronos'
  AND s.realized_return_60m IS NULL
  AND s.latest_candle IS NOT NULL
  AND current.exchange = s.exchange
  AND current.symbol = s.symbol
  AND current.time = s.latest_candle
  AND future.exchange = s.exchange
  AND future.symbol = s.symbol
  AND future.time = s.latest_candle + INTERVAL '60 minutes';
"@
Invoke-DbSql $evaluationSql

Write-Host "Runtime snapshot written: $snapshotTime open_trades=$($count.current) trade_count=$($profit.trade_count)" -ForegroundColor Green
