<#
    通用 nextnano.NEGF 批量运行 + 增益汇总脚本

    用途：把一批 .negf 输入文件依次跑完，自动汇总每个偏置点的
          "最大增益"和"峰值光子能量"，输出 CSV。

    用法：
        .\scripts\run_negf_batch.ps1 -LicenseFile "D:\...\License_nnNEGF.lic" `
            -InputFiles .\designs\qcl8um_scan_*.negf `
            -OutputRoot .\runs\batch1

    参数：
        -InputFiles   输入文件（支持通配符，多个用逗号分隔）
        -OutputRoot   输出根目录（每个输入文件一个子目录）
        -LicenseFile  nextnano.NEGF 许可证路径（必填）
        -Threads      并行线程数（默认 8）
#>

param(
    [Parameter(Mandatory = $true)][string]$LicenseFile,
    [Parameter(Mandatory = $true)][string[]]$InputFiles,
    [string]$OutputRoot = '.\runs\batch',
    [int]$Threads = 8,
    [string]$NEGFExe = 'C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\bin\nextnano.NEGF_win.exe',
    [string]$Database = 'C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\database\Material_Database.negf'
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $LicenseFile)) { throw "找不到许可证文件：$LicenseFile" }
if (-not (Test-Path -LiteralPath $NEGFExe))     { throw "找不到 NEGF 可执行文件：$NEGFExe" }
if (-not (Test-Path -LiteralPath $Database))    { throw "找不到材料数据库：$Database" }

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$summary = @()

foreach ($file in $InputFiles) {
    if (-not (Test-Path -LiteralPath $file)) { Write-Warning "跳过不存在的文件：$file"; continue }
    $case = [System.IO.Path]::GetFileNameWithoutExtension($file)
    $outDir = Join-Path $OutputRoot $case

    Write-Host ('=' * 70)
    Write-Host "输入：$file"
    Write-Host "输出：$outDir"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $NEGFExe --input-file $file --license-file $LicenseFile `
        --output-folder $outDir --material-database $Database --threads $Threads `
        *> (Join-Path $OutputRoot "$case.log")
    $sw.Stop()
    Write-Host ("[$case] 结束，耗时 {0:N1} 分钟" -f $sw.Elapsed.TotalMinutes)

    $gainFile = Join-Path $outDir 'Gain_vs_Voltage.dat'
    if (-not (Test-Path -LiteralPath $gainFile)) {
        Write-Warning "[$case] 没有 Gain_vs_Voltage.dat，跳过汇总"
        continue
    }
    foreach ($row in (Get-Content -LiteralPath $gainFile | Select-Object -Skip 1)) {
        $p = ($row -split '\s+') | Where-Object { $_ }
        if ($p.Count -lt 3) { continue }
        $bias = [double]$p[0]; $gain = [double]$p[1]; $photon = [double]$p[2]
        $summary += [pscustomobject]@{
            Case               = $case
            Bias_mV_per_period = $bias
            MaxGain_per_cm     = [math]::Round($gain, 3)
            PhotonEnergy_meV   = $photon
            Wavelength_um      = if ($photon -gt 0) { [math]::Round(1240 / $photon, 3) } else { $null }
        }
    }
}

$csv = Join-Path $OutputRoot 'batch_summary.csv'
$summary | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8

Write-Host ('=' * 70)
Write-Host "只看 MaxGain > 0 的行："
$summary | Where-Object { $_.MaxGain_per_cm -gt 0 } |
    Sort-Object Case, Bias_mV_per_period |
    Format-Table Case, Bias_mV_per_period, MaxGain_per_cm, PhotonEnergy_meV, Wavelength_um -AutoSize
Write-Host "完整结果：$csv"
