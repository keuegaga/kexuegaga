<#
  pics3d_watch_nakamura_LI.ps1
  Quiet watcher for the PICS3D "nakamura_LI v6 wrap-up" run.

  What it checks each pass
    - s2.sol: restart data_set= line + no leftover "ADDED-2026-09-23" block
    - s2.std_0* files: new / updated / truncated (size differs from the expected 37,466,650 B)
    - s2_run.log: last Current, last "Solver converged", scan-number sequence,
      lambda fault fingerprints (Warning: big change in lambda / peak RTG not ~0.4246),
      Solver failed / "Too bad the solver can not go further"
    - pics3d process alive + CPU delta (is it computing or stuck)

  It prints NOTHING on a normal pass (unless -ShowHeartbeat).
  ASCII output only, so it is safe in a GBK console.

  Usage
    # one pass (ideal for a Windows Scheduled Task, run hourly):
    powershell -ExecutionPolicy Bypass -File .\scripts\pics3d_watch_nakamura_LI.ps1 -Once

    # keep watching in this terminal, one pass per hour:
    powershell -ExecutionPolicy Bypass -File .\scripts\pics3d_watch_nakamura_LI.ps1 -IntervalSec 3600

    # every 10 minutes, with a one-line heartbeat every pass:
    powershell -ExecutionPolicy Bypass -File .\scripts\pics3d_watch_nakamura_LI.ps1 -IntervalSec 600 -ShowHeartbeat
#>
param(
    [string]$Dir = 'C:\Users\ciomp\Documents\2024Ver_pics3d_examples\pics3d_examples\blue_LD\nakamura_LI',
    [int]$IntervalSec = 3600,
    [switch]$Once,
    [switch]$ShowHeartbeat,
    [string]$StateFile = (Join-Path $PSScriptRoot 'pics3d_watch_nakamura_LI.state.json'),
    [string]$LogFile = '',
    [double]$StallHours = 6,
    [long]$ExpectedStdBytes = 37466650
)

function Write-Alert([string]$msg) {
    Write-Host ("ALERT [{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm'), $msg)
}

function Read-Log([string]$path) {
    # the log is held by the running solver -> Get-Content uses shared read, ReadAllBytes would fail
    if (-not (Test-Path $path)) { return @() }
    try { return @(Get-Content -LiteralPath $path -ErrorAction Stop) } catch { return @() }
}

function Prop-Names($obj) {
    # ConvertFrom-Json gives PSCustomObject: it has no .ContainsKey(), so read the property names instead
    if ($null -eq $obj) { return @() }
    return @($obj.PSObject.Properties.Name)
}

function Snapshot {
    $snap = [ordered]@{}
    $snap.nowUnix = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

    # --- input file sanity ---
    $sol = Join-Path $Dir 's2.sol'
    $solText = if (Test-Path $sol) { Get-Content -LiteralPath $sol -Raw } else { '' }
    $m = [regex]::Match($solText, '(?m)^\s*restart data_set=(\d+)')
    $snap.restart = if ($m.Success) { [int]$m.Groups[1].Value } else { -1 }
    $snap.hasAddedBlock = $solText -match 'ADDED-2026-09-23'

    # --- datasets ---
    $std = Get-ChildItem -LiteralPath $Dir -Filter 's2.std_0*' -File -ErrorAction SilentlyContinue |
           Where-Object { $_.Name -notmatch 'STALE' } | Sort-Object Name
    $snap.std = @{}
    foreach ($f in $std) { $snap.std[$f.Name] = @{ size = $f.Length; time = $f.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss') } }

    # --- log ---
    $log = Read-Log (Join-Path $Dir 's2_run.log')
    $snap.logLines = $log.Count

    $cur = $null
    $curTime = $null
    $lambdas = @()
    $scans = @()
    for ($i = 0; $i -lt $log.Count; $i++) {
        $l = $log[$i]
        if ($l -match 'Current: \(A\)\s+(\S+)') { $cur = [double]$matches[1] * 1000.0 }
        if ($l -match 'peak RTG set lambda=\s+([0-9.]+)') { $lambdas += [double]$matches[1] }
        if ($l -match 'scan number->\s+(\d+)') { $scans += [int]$matches[1] }
    }
    $snap.lastCurrentMA = if ($cur -ne $null) { [math]::Round($cur, 4) } else { $null }
    $snap.scanSeq = ($scans -join ',')
    $snap.lastLambdas = @($lambdas | Select-Object -Last 3)
    $snap.cntBigLambda = (@($log | Select-String -Pattern 'Warning: big change in lambda' -AllMatches).Count)
    $snap.cntSolverFailed = (@($log | Select-String -Pattern 'Solver failed' -AllMatches).Count)
    $snap.cntTooBad = (@($log | Select-String -Pattern 'Too bad the solver can not go further' -AllMatches).Count)
    $snap.cntExceeding = (@($log | Select-String -Pattern 'Exceeding auto_finish' -AllMatches).Count)
    $snap.cntCompleted = (@($log | Select-String -Pattern 'Completed \.std file' -AllMatches).Count)

    # --- process ---
    $p = Get-Process pics3d -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($p) {
        $c1 = $p.CPU
        Start-Sleep -Seconds 6
        $p.Refresh()
        $snap.procAlive = $true
        $snap.procCpuDelta = [math]::Round($p.CPU - $c1, 2)
        $snap.procCpuHours = [math]::Round($p.CPU / 3600, 2)
    } else {
        $snap.procAlive = $false
        $snap.procCpuDelta = 0
        $snap.procCpuHours = 0
    }
    return $snap
}

function Compare-And-Alert($prev, $now) {
    # baseline pass
    if ($null -eq $prev) {
        Write-Host ("BASELINE [{0}] restart=data_set={1}  std={2}  datasets='{3}'  log={4} lines  proc={5} (CPU {6} h)" -f `
            (Get-Date -Format 'yyyy-MM-dd HH:mm'), $now.restart, @($now.std.Keys).Count, (($now.std.Keys) -join ','), $now.logLines, $now.procAlive, $now.procCpuHours)
        if (@($now.std.Keys).Count -eq 0) { Write-Alert 'baseline recorded, but no s2.std_* dataset exists yet' }
        $now.lastLogGrowUnix = $now.nowUnix
        return $now
    }

    $prevStdNames = Prop-Names $prev.std

    # 1) input file sanity
    if ($now.restart -ne 2) { Write-Alert ("s2.sol restart=data_set={0} (expected 2) - the proven-safe start point" -f $now.restart) }
    if ($now.hasAddedBlock) { Write-Alert 's2.sol contains the ADDED-2026-09-23 block again (must NOT be there)' }

    # 2) datasets
    foreach ($k in $now.std.Keys) {
        $isNew = $prevStdNames -notcontains $k
        $changed = (-not $isNew) -and ($prev.std.$k.time -ne $now.std[$k].time)
        if ($isNew) {
            $sz = $now.std[$k].size
            $flag = if ($sz -lt $ExpectedStdBytes) { 'TRUNCATED?!' } else { 'ok' }
            Write-Alert ("NEW dataset {0}  {1:N0} B ({2})  written {3}" -f $k, $sz, $flag, $now.std[$k].time)
        } elseif ($changed) {
            Write-Alert ("dataset {0} rewritten  {1:N0} B  at {2}" -f $k, $now.std[$k].size, $now.std[$k].time)
        }
    }

    # 3) fault fingerprints
    if ($now.cntBigLambda -gt $prev.cntBigLambda) {
        Write-Alert ("lambda fault: 'Warning: big change in lambda' +{0} (total {1}) - the RTG wavelength search ran away" -f `
            ($now.cntBigLambda - $prev.cntBigLambda), $now.cntBigLambda)
    }
    $bad = @($now.lastLambdas | Where-Object { $_ -lt 0.41 -or $_ -gt 0.44 })
    if ($bad.Count -gt 0 -and (@($prev.lastLambdas | Where-Object { $_ -lt 0.41 -or $_ -gt 0.44 }).Count -eq 0)) {
        Write-Alert ("lambda fault: last peak RTG wavelengths = {0} (expected ~0.4246)" -f (($now.lastLambdas) -join ', '))
    }
    if ($now.cntSolverFailed -gt $prev.cntSolverFailed) {
        Write-Alert ("Solver failed +{0} (total {1})" -f ($now.cntSolverFailed - $prev.cntSolverFailed), $now.cntSolverFailed)
    }
    if ($now.cntTooBad -gt $prev.cntTooBad) {
        Write-Alert ("'Too bad the solver can not go further' +{0} - the run is dying" -f ($now.cntTooBad - $prev.cntTooBad))
    }

    # 4) progress / stall: use "log has grown" as the progress signal
    #    (the last Current value can legitimately sit still for hours inside one big bias step)
    if ($now.logLines -gt $prev.logLines) {
        $now.lastLogGrowUnix = $now.nowUnix
    } else {
        if ($prev.lastLogGrowUnix) { $now.lastLogGrowUnix = $prev.lastLogGrowUnix } else { $now.lastLogGrowUnix = $now.nowUnix }
        $quiet = ($now.nowUnix - [long]$now.lastLogGrowUnix) / 3600.0
        if ($quiet -ge $StallHours -and $now.procAlive) {
            Write-Alert ("log has not grown for {0:N1} h (stuck at I = {1} mA, {2} lines, CPU delta {3} s) - check whether it is stalled" -f `
                $quiet, $now.lastCurrentMA, $now.logLines, $now.procCpuDelta)
        }
    }

    # 5) process
    if ($prev.procAlive -and -not $now.procAlive) {
        $last = ($now.std.Keys | Sort-Object | Select-Object -Last 1)
        Write-Alert ("pics3d process is GONE. last dataset = {0}. If it was not a normal finish, check s2_run.log tail." -f $last)
    }
    if ($now.procAlive -and $now.procCpuDelta -le 0.2) {
        Write-Alert ("pics3d alive but CPU delta is only {0} s / 6 s - possibly stalled (e.g. waiting on a license seat)" -f $now.procCpuDelta)
    }

    # 6) completion
    if (($now.std.Keys -contains 's2.std_0009') -and ($prevStdNames -notcontains 's2.std_0009')) {
        Write-Alert 'v6 run looks COMPLETE: s2.std_0009 (79.7 mA) landed. Next: run the L-I post-processing.'
    }

    if ($ShowHeartbeat) {
        Write-Host ("HB [{0}] restart={1} std={2} I={3} mA log={4} proc={5} CPUdelta={6}s" -f `
            (Get-Date -Format 'MM-dd HH:mm'), $now.restart, @($now.std.Keys).Count, $now.lastCurrentMA, $now.logLines, $now.procAlive, $now.procCpuDelta)
    }
    return $now
}

if (-not (Test-Path $Dir)) { Write-Alert ("case directory not found: {0}" -f $Dir); exit 1 }

# optional: append everything (including Write-Host alerts) to a log file,
# so the watcher can run without a visible window
$transcriptOn = $false
if ($LogFile) {
    try { Start-Transcript -Path $LogFile -Append -ErrorAction Stop | Out-Null; $transcriptOn = $true }
    catch { Write-Alert ("could not start transcript: {0}" -f $_.Exception.Message) }
}

try {
    while ($true) {
        $prev = $null
        if (Test-Path $StateFile) {
            try { $prev = (Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json) } catch { $prev = $null }
        }
        $now = Snapshot
        $state = Compare-And-Alert $prev $now
        try { ($state | ConvertTo-Json -Depth 5) | Set-Content -LiteralPath $StateFile -Encoding UTF8 } catch { }
        if ($Once) { break }
        Start-Sleep -Seconds ([Math]::Max(60, $IntervalSec))
    }
} finally {
    if ($transcriptOn) { try { Stop-Transcript | Out-Null } catch { } }
}
