param(
    [string[]]$Pairs = @("HYPE/USDT", "ACT/USDT", "WLD/USDT", "AAVE/USDT", "AGLD/USDT", "PEPE/USDT"),
    [string]$Start = "2025-04-01T00:00:00Z",
    [string]$End = "2026-05-28T00:00:00Z",
    [string]$OutputDir = "tmp/okx-swap-1h-csv",
    [int]$Limit = 100,
    [int]$SleepMs = 120
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$outDir = Join-Path $ProjectRoot $OutputDir
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$startMs = ([DateTimeOffset][datetime]$Start).ToUnixTimeMilliseconds()
$endMs = ([DateTimeOffset][datetime]$End).ToUnixTimeMilliseconds()

function Invoke-OkxCandles {
    param(
        [string]$InstId,
        [int64]$After
    )
    $uri = "https://www.okx.com/api/v5/market/history-candles?instId=$InstId&bar=1H&limit=$Limit&after=$After"
    for ($attempt = 1; $attempt -le 4; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri $uri -TimeoutSec 30
            if ($response.code -ne "0") {
                throw "OKX returned code=$($response.code) msg=$($response.msg)"
            }
            return @($response.data)
        } catch {
            if ($attempt -ge 4) {
                throw
            }
            $sleep = [Math]::Min([Math]::Pow(2, $attempt), 10)
            Write-Warning "fetch failed attempt=$attempt retry_in=${sleep}s instId=$InstId after=$After error=$($_.Exception.Message)"
            Start-Sleep -Seconds $sleep
        }
    }
}

$summary = @()
foreach ($pair in $Pairs) {
    $base = ($pair -split "/")[0]
    $instId = "$base-USDT-SWAP"
    $safe = "${base}_USDT_USDT-1h-futures.csv"
    $output = Join-Path $outDir $safe
    Write-Host "Downloading $pair ($instId) -> $output"
    $rowsByTs = @{}
    $after = $endMs
    $pages = 0
    while ($true) {
        $batch = Invoke-OkxCandles -InstId $instId -After $after
        if ($batch.Count -eq 0) {
            break
        }
        $pages++
        $oldest = [int64]::MaxValue
        foreach ($row in $batch) {
            $ts = [int64]$row[0]
            if ($ts -lt $oldest) {
                $oldest = $ts
            }
            if ($ts -ge $startMs -and $ts -lt $endMs -and $row[8] -eq "1") {
                $rowsByTs[[string]$ts] = [pscustomobject]@{
                    date_ms = $ts
                    open = [double]$row[1]
                    high = [double]$row[2]
                    low = [double]$row[3]
                    close = [double]$row[4]
                    volume = [double]$row[6]
                }
            }
        }
        if ($oldest -le $startMs -or $oldest -eq [int64]::MaxValue) {
            break
        }
        $after = $oldest
        if ($pages % 25 -eq 0) {
            Write-Host "  pages=$pages rows=$($rowsByTs.Count) oldest=$([DateTimeOffset]::FromUnixTimeMilliseconds($oldest).UtcDateTime.ToString('s'))Z"
        }
        Start-Sleep -Milliseconds $SleepMs
    }
    $rows = @($rowsByTs.Values | Sort-Object date_ms)
    $rows | Export-Csv -Path $output -NoTypeInformation -Encoding UTF8
    $summary += [pscustomobject]@{
        pair = $pair
        inst_id = $instId
        pages = $pages
        rows = $rows.Count
        output = $output
        start = if ($rows.Count) { ([DateTimeOffset]::FromUnixTimeMilliseconds([int64]$rows[0].date_ms)).UtcDateTime.ToString("o") } else { $null }
        end = if ($rows.Count) { ([DateTimeOffset]::FromUnixTimeMilliseconds([int64]$rows[-1].date_ms)).UtcDateTime.ToString("o") } else { $null }
    }
}

$summary | Format-Table -AutoSize
$summary | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $outDir "download-summary.json") -Encoding UTF8
