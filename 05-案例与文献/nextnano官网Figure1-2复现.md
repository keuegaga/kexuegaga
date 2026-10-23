---
title: nextnano 官网 Figure 1/2 复现
type: example
product: nextnano.NEGF
version: 2025.08.21
status: computed-with-caveat
source: designs/nextnano_home_figures_bai_0_500mV.negf
last_verified: 2026-10-23
tags:
  - qcl
  - nextnano
  - bai2011
  - ldos
  - iv
---

# nextnano 官网 Figure 1/2 复现

## 结论摘要

官网首页的两幅动画：

- Figure 1：`Local density of states in a QCL structure for varying bias`
- Figure 2：`Current-voltage characteristics of the same QCL structure`

均包含 26 帧，对应：

```text
每个周期的电压降 = 0, 20, 40, ..., 500 mV
```

官网页面只给图，没有直接标明所用输入文件。根据层厚序列、43.48 nm
周期、AlAs/InAlAs 复合垒形成的双高度尖峰、以及 440 mV 附近的
约 4.6 kA/cm² 电流峰值，图中结构与安装包中的 **Bai APL 2011
高功率 QCL** 案例吻合。旧版 `nextnano.NEGF_classic` 中对应文件为：

```text
C:\Program Files\nextnano\2025_08_21\nextnano.NEGF_classic\examples\MidIR_QCL_InGaAs_InAlAs_Bai_APL2011_GainClamping_21subbbands.xml
```

当前 C++ 版 nextnano.NEGF 中的对应母本为：

```text
C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\examples\MidIR_QCL_InGaAs_InAlAs_Bai_APL2011_GainClamping.negf
```

## 本次计算输入

额定 0–500 mV 单文件版本：

```text
D:\Codex-Obsidian\QCL-nextnano\designs\nextnano_home_figures_bai_0_500mV.negf
```

为缩短总墙钟时间，实际运行分成多个互不重叠的电压段；层序、材料、
温度、散射、掺杂及空间/能量网格保持与官方案例一致，仅调整分段与
收敛停机条件：

| 分段 | 电压范围 | 输入文件 |
|---|---|---|
| p0 | 0 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\nextnano_home_figures_bai_p0_fast.negf` |
| p1a | 20–60 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\bai_p1_phys.negf` |
| p1b | 80–140 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\bai_p1_rest.negf` |
| p2a | 160–200 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\bai_p2_phys.negf` |
| p2b | 220–280 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\bai_p2_rest.negf` |
| p3a | 300 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\nextnano_home_figures_bai_p3.negf` |
| p3b | 320–340 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\bai_p3_phys.negf` |
| p3c | 360–420 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\bai_p3_rest.negf` |
| p4a | 440 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\nextnano_home_figures_bai_p4.negf` |
| p4b | 460 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\bai_p4_phys.negf` |
| p4c | 480 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\bai_p4_480.negf` |
| p4d | 500 mV | `D:\Codex-Obsidian\QCL-nextnano\designs\bai_p4_last.negf` |

相对官方输入仅做以下操作：

1. 扫描改为 `0:20:500 mV/period`；
2. 删除 `Gain` 和 `EMfield` 块，因为 Figure 1/2 是不含激光钳制的
   LDOS 与 I–V；
3. 0–280 mV 低偏压段把电流相对阈值放宽到 1%–10%，同时把 `G`
   自洽阈值放宽到 `1e-3` 至 `5e-3`；300、320、440 mV 保留
   `1e-4` 级严格验证，其余高偏压帧采用 `1e-3` 级阈值。

本机许可证：

```text
D:\08-Study\Nextnano\License_nnNEGF.lic
```

## 本次输出位置

计算输出根目录：

```text
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p0_fast
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p1_phys
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p1_rest
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p2_phys
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p2_rest
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p3
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p3_phys
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p3_rest
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p4
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p4_phys
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p4_480
D:\Codex-Obsidian\QCL-nextnano\runs\nextnano_negf_home_figures\bai_p4_last
```

### Figure 1 的原始数据

每个偏压目录下：

```text
<Bias>mV\2D_plots\data\DensityOfStates_ZoneCenter.ascii
```

三列依次为：

```text
position_nm    energy_eV    LDOS_nm^-1_eV^-1
```

对应导带边：

```text
<Bias>mV\ConductionBandEdge.dat
```

### Figure 2 的原始数据

各分段的汇总文件：

```text
<分段输出目录>\Current_vs_Voltage.dat
<分段输出目录>\Current_vs_EField.dat
```

每行的第一个数是一个周期的电压降，第二个数是电流密度。

### 收敛与运行诊断

```text
<分段输出目录>\_ConvergenceFactors.dat
<分段输出目录>\_Iterations.dat
<分段输出目录>\<Bias>mV\_ConvergenceFactors.dat
<分段输出目录>\.stdout.log
```

## 重绘结果

统一重绘目录：

```text
D:\Codex-Obsidian\QCL-nextnano\results\nextnano_home_figures_bai
```

主要文件：

- `figure1_ldos_vs_bias.gif`
- `figure2_current_voltage.png`
- `figure2_current_sweep.gif`
- `figure2_current_voltage_valid_range.png`
- `nextnano_home_figures_reproduction.gif`
- `figure1_figure2_static_0mV.png`
- `figure1_figure2_static_300mV.png`
- `current_comparison.png`
- `current_comparison.csv`

绘图脚本：

```text
D:\Codex-Obsidian\QCL-nextnano\scripts\plot_nextnano_home_figures.py
```

## 本次复算结果

26 个电压点的原始 LDOS 和电流文件均已生成。关键工作区电流：

| 每周期偏压 | 本次计算 \(J\) | 官网旧图数字化 \(J\) |
|---:|---:|---:|
| 300 mV | 1399.6 A/cm² | 1153.4 A/cm² |
| 320 mV | 1729.6 A/cm² | 1674.1 A/cm² |
| 340 mV | 2059.1 A/cm² | 2601.1 A/cm² |
| 360 mV | 2482.9 A/cm² | 3339.3 A/cm² |
| 400 mV | 2904.3 A/cm² | 4285.2 A/cm² |
| 440 mV | 3310.6 A/cm² | 4596.4 A/cm² |
| 480 mV | 3586.8 A/cm² | 4526.6 A/cm² |
| 500 mV | 3862.6 A/cm² | 4437.5 A/cm² |

全体 26 点的 I–V 均方根偏差约为 **805 A/cm²**。因此：

- Figure 1 的层序、周期、垒高和量子态空间分布可以作为结构复现依据；
- Figure 2 不能视为官网旧图的逐点精确复现；
- 当前 C++ NEGF 下，高偏压电流比旧动画低约 15%–30%；
- 0–140 mV 的电流受近零相对收敛判据影响，出现明显异常的负值，
  不应据此校核阈值电流或串联电阻；这部分 LDOS 仍可用于观察态演化，
  160–300 mV 也受不同分段初始态的影响；定量 I–V 应优先读取
  320–500 mV 的严格区。

## 与官网图的差异

层界面和量子态位置可用于确认案例来源，但不应期待逐像素一致：

- 官网动画来自较早版本的展示计算；
- 当前版本加入了更新的 k·p、应变、极化、散射和收敛实现；
- 官网没有发布该动画的原始 ASCII 数据或完整输入；
- 因此应把本次结果作为 **同案例的现代版本复算**，而不是把官网 GIF
  当作定量仿真基准。

## 输入文件关键项

```text
SweepType = Voltage
Min = 0
Max = 500
Delta = 20
```

表示横轴 `Potential drop per period [mV]`，不是整支 QCL 的总偏压。

```text
CoherenceLengthInPeriods = 1
```

表示相邻一个周期之间保持相干；二维图会重复显示两个周期以便观察输运。

```text
EnergyResolvedPlots = yes
```

输出 LDOS、载流子密度和能流密度等二维文件。

```text
SpatialGridSpacing = 0.2 nm
EnergyGridSpacing = 5 meV
```

空间和能量网格；过粗会使窄垒失去物理意义，过细则显著增加计算量。

```text
InterfaceRoughness
AlloyScattering
ElectronElectronScattering
```

三者决定中红外 QCL 的展宽、峰形和电流平台，是定量复现中不可随意关闭的
物理项。

## 相关笔记

- [[案例文献索引]]
- [[17-NEGF输出数据逐步分析]]
