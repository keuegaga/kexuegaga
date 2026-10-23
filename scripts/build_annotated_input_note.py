# -*- coding: utf-8 -*-
"""Build the Obsidian line-by-line note from the annotated NEGF input."""

from pathlib import Path


ROOT = Path(r"D:\Codex-Obsidian\QCL-nextnano")
SOURCE = ROOT / "designs/sun2022_mocvd_validation_annotated.negf"
OUTPUT = ROOT / "03-输入与输出/Sun2022验证输入逐行注释.md"


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    text = f"""---
title: Sun2022 验证输入逐行注释
type: example
product: nextnano.NEGF
version: 2025.08.21
status: verified
source: designs/sun2022_mocvd_validation_annotated.negf
last_verified: 2026-10-23
tags:
  - qcl
  - negf
  - input
  - annotation
---

# Sun2022 验证输入逐行注释

本页的核心文件是：

`designs/sun2022_mocvd_validation_annotated.negf`

文件中的注释都是 nextnano 可忽略的 `#` 行；输入主体与已经实际运行的
`sun2022_mocvd_9um_alloy006_independent_dv060_biasscan.negf` 等价。为避免编码问题，运行文件中的注释使用 ASCII。

## 运行方式

```powershell
& 'C:\\Program Files\\nextnano\\2025_08_21\\nextnano.NEGF\\bin\\nextnano.NEGF_win.exe' `
  --input-file 'D:\\Codex-Obsidian\\QCL-nextnano\\designs\\sun2022_mocvd_validation_annotated.negf' `
  --license-file 'D:\\08-Study\\Nextnano\\License_nnNEGF.lic' `
  --output-folder 'D:\\Codex-Obsidian\\QCL-nextnano\\runs\\sun2022_mocvd\\validation_annotated' `
  --material-database 'C:\\Program Files\\nextnano\\2025_08_21\\nextnano.NEGF\\database\\Material_Database.negf' `
  --threads 8
```

## 文件结构总览

| 组 | 作用 | 本案例设置 |
|---|---|---|
| `Header` | 记录作者、来源和模型说明 | Sun 2022 验证基线 |
| `SweepParameters` | 电压扫描 | 140–220 mV/period，步长 20 mV |
| `OverwriteMaterialDatabase` | 覆盖数据库默认参数 | 修正二元形变势 |
| `Temperature` | 晶格温度 | 300 K |
| `Crystal` | 衬底、取向、应变、压电 | InP、Zincblende、开启应变 |
| `Materials` | 独立材料参数 | CBO 0.773 eV、m*=0.043/0.089 |
| `Structure` | 16 层/周期与掺杂 | 周期 45.08 nm，掺杂层 13–14 |
| `Scattering` | LO、IFR、杂质、e-e、合金 | alloy=0.06，IFR=0.08 nm/7 nm |
| `Poisson` | 静电势自洽 | 开启 |
| `LateralDiscretization` | 面内态离散 | Value=50 |
| `SimulationParameter` | 相干长度、网格、能量窗 | 1 period、0.2 nm、5 meV |
| `Output` | 位置/能量分辨输出 | 开启 |
| `Gain` | 自洽增益和 FGR | GainMethod=1，120–155 meV |

## 必须理解的量

### 1. 每周期电压

`SweepParameters` 和 `Gain` 里的电压是 **potential drop per period**。本结构周期为
45.08 nm，因此：

```text
F = V_period / 45.08 nm
216.384 mV / 45.08 nm = 48.0 kV/cm
```

50 个周期在 216.384 mV/period 时的总有源区电压约：

```text
50 × 216.384 mV = 10.819 V
```

### 2. 掺杂片密度

掺杂区从 35.53 nm 到 40.10 nm，厚度 4.57 nm，掺杂 1.5e17 cm-3：

```text
1.5e17 cm-3 × 4.57e-7 cm = 6.855e10 cm-2
```

与论文约 6.8e10 cm-2 一致。

### 3. 合金散射

`AlloyScatteringStrength=0.06` 不是增益调参值，而是：

```text
well:    sqrt(0.06 × 5.836815) = 0.592 eV
barrier: sqrt(0.06 × 7.337601) = 0.664 eV
```

落在 nextnano 推荐约 0.6 eV 和独立实验 0.44–0.70 eV 范围内。

### 4. 宽窗和窄窗

本文件使用 120–155 meV 窄窗，便于做偏压扫描。判断全局峰必须使用配套宽窗文件：

`designs/sun2022_mocvd_9um_alloy006_wide.negf`（60–180 meV）

否则最大值落在 120 meV 左边界的现象会被误判为真正峰值。

## 完整逐语句注释文件

```text
{source}
```

## 重点输出

- `Energy_Eigenstates.dat`：每个扫描偏压的 42 个 Wannier–Stark 状态；
- `Populations_Eigenstates.dat`：各偏压的状态占据；
- `Effective_Temperature.dat`：有效电子温度；
- `(Bias)mV/Gain/Gain_SelfConsistent_vs_Energy.dat`：自洽增益；
- `(Bias)mV/Gain/Gain_FermiGoldenRule_vs_Energy_[0,0,1].dat`：FGR；
- `(Bias)mV/EnergyEigenstates/Lifetimes.dat`：状态寿命；
- `(Bias)mV/EnergyEigenstates/ScatteringRate_mechanisms.dat`：LO/IFR/合金散射；
- `(Bias)mV/Gain/data/Gain_vs_Position_and_Energy_SelfConsistent.ascii`：位置分辨增益。

## 当前运行结论

- 物理归一化后 9.17 µm 有正增益；
- 但自由运行宽窗优先选择 10.8 µm（阈值附近）或 10.33 µm（更高电流）；
- 强制 9.17 µm 光模的阈值约 2.05 kA/cm²；
- 长波自由运行阈值约 1.71 kA/cm²；
- NEGF 绝对阈值与论文 1.52 kA/cm² 仍不完全一致。

详见 [[Sun2022-NEGF完整验证报告]]。

## 相关笔记

- [[16-NEGF输入文件逐行讲解]]
- [[17-NEGF输出数据逐步分析]]
- [[43-Sun2022-9um-v2实验制造基线]]
- [[44-五级验证闸门-Sun2022态映射增益与波导]]
- [[45-合金散射独立归一化与NEGF严格复现结论]]
"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
