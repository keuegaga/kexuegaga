<#
    8 µm QCL 阱宽扫描：批量运行 nextnano.NEGF 并汇总增益结果

    用途：把 designs 目录里的 qcl8um_scan_w32/w34/w36.negf 依次跑完，
          自动提取每个偏置点的"最大增益"和"峰值光子能量"，汇总成 CSV。

    用法（在 PowerShell 里执行）：

        cd D:\Codex-Obsidian\QCL-nextnano
        .\scripts\run_well_width_scan.ps1 -LicenseFile "C:\path\to\your\License_nnNEGF.lic"

    常用可选参数：
        -Threads 8              并行线程数（默认 8）
        -OutputRoot "D:\Codex-Obsidian\QCL-nextnano\runs\scan_w"   输出根目录
        -NEGFExe "...\nextnano.NEGF_win.exe"                     可执行文件路径
        -Database "...\Material_Database.negf"                   材料数据库路径
#>

param(
    [Parameter(Mandatory = $true)][string]$LicenseFile,
    [int]$Threads = 8,
    [string]$OutputRoot = 'D:\Codex-Obsidian\QCL-nextnano\runs\scan_w',
    [string]$NEGFExe = 'C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\bin\nextnano.NEGF_win.exe',
    [string]$Database = 'C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\database\Material_Database.negf'
)

$ErrorActionPreference = 'Stop'
$vaultRoot = Split-Path -Parent $PSScriptRoot
$designs = Join-Path $vaultRoot 'designs'

# --- 前置检查 -------------------------------------------------------------
if (-not (Test-Path $LicenseFile)) { throw "找不到许可证文件：$LicenseFile" }
if (-not (Test-Path $NEGFExe))     { throw "找不到 NEGF 可执行文件：$NEGFExe" }
if (-not (Test-Path $Database))    { throw "找不到材料数据库：$Database" }

$cases = @(
    @{ Name = 'w32'; File = 'qcl8um_scan_w32.negf'; Well = 3.2; Period = 22.5 },
    @{ Name = 'w34'; File = 'qcl8um_scan_w34.negf'; Well = 3.4; Period = 22.7 },
    @{ Name = 'w36'; File = 'qcl8um_scan_w36.negf'; Well = 3.6; Period = 22.9 }
)

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$summary = @()

foreach ($case in $cases) {
    $inputFile = Join-Path $designs $case.File
    $outDir    = Join-Path $OutputRoot $case.Name

    Write-Host ("=" * 70)
    Write-Host ("[{0}] 上态阱宽 {1} nm，周期 {2} nm" -f $case.Name, $case.Well, $case.Period)
    Write-Host ("输入：{0}" -f $inputFile)
    Write-Host ("输出：{0}" -f $outDir)

    if (Test-Path $outDir) { Remove-Item $outDir -Recurse -Force }

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $NEGFExe --input-file $inputFile --license-file $LicenseFile `
        --output-folder $outDir --material-database $Database --threads $Threads
    $sw.Stop()
    Write-Host ("[{0}] 运行结束，耗时 {1:N1} 分钟" -f $case.Name, $sw.Elapsed.TotalMinutes)

    # --- 提取增益结果 ----------------------------------------------------
    $gainFile = Join-Path $outDir 'Gain_vs_Voltage.dat'
    if (-not (Test-Path $gainFile)) {
        Write-Warning ("[{0}] 没有找到 Gain_vs_Voltage.dat，跳过汇总" -f $case.Name)
        continue
    }

    $rows = Get-Content $gainFile | Select-Object -Skip 1
    foreach ($row in $rows) {
        $parts = ($row -split '\s+') | Where-Object { $_ }
        if ($parts.Count -lt 3) { continue }
        $bias   = [double]$parts[0]
        $gain   = [double]$parts[1]
        $photon = [double]$parts[2]
        $summary += [pscustomobject]@{
            Case              = $case.Name
            WellWidth_nm      = $case.Well
            Period_nm         = $case.Period
            Bias_mV_per_period= $bias
            MaxGain_per_cm    = [math]::Round($gain, 3)
            PhotonEnergy_meV  = $photon
            Wavelength_um     = [math]::Round(1240 / $photon, 3)
        }
    }
}

# --- 汇总输出 -------------------------------------------------------------
$csv = Join-Path $OutputRoot 'scan_summary.csv'
$summary | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8

Write-Host ("=" * 70)
Write-Host "汇总表（只看 MaxGain > 0 的行）："
$summary | Where-Object { $_.MaxGain_per_cm -gt 0 } |
    Sort-Object Case, Bias_mV_per_period |
    Format-Table Case, WellWidth_nm, Bias_mV_per_period, MaxGain_per_cm, PhotonEnergy_meV, Wavelength_um -AutoSize

Write-Host ("完整结果已写入：{0}" -f $csv)
Write-Host "把 scan_summary.csv 和三个输出目录发给我，我来判断哪个阱宽落在 8 µm。"
