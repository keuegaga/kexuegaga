---
title: Sun2022 变偏压 LDOS、I–V 与激射分析教程
type: tutorial
product: nextnano.NEGF
version: 2025.08.21
status: verified-with-model-caveat
source: D:\03-References\QCLs\MinerU-pdftomarkdown\High-performance quantum cascade lasers at λ~9um grown by MOCVD.md
last_verified: 2026-10-23
tags:
  - qcl
  - sun2022
  - negf
  - ldos
  - population-inversion
  - gain
---

# Sun 2022 变偏压 LDOS、I–V 与激射分析教程

> 后续设计：按本页发现的 10.33 µm 自洽长波分支，见
> [[Sun2022-10p33um第二轮设计与两轮比较]]。

## 1. 本页回答什么

本页针对：

> Sun et al., *Optics Express* **30**, 37272 (2022), DOI `10.1364/OE.469573`

复算有源区的：

1. Local density of states（LDOS）随偏压演化；
2. 电流密度–电压特性；
3. DAU/MS 状态占据与粒子数反转；
4. 9.17 µm 增益、阈值和固定光模下的激射状态。

文献原始 Markdown：

```text
D:\03-References\QCLs\MinerU-pdftomarkdown\High-performance quantum cascade lasers at λ~9um grown by MOCVD.md
```

## 2. 为什么扫描 0–260 mV/周期

该结构一个周期的厚度为：

```text
L = 45.08 nm
```

一个周期的电压降与电场的关系：

```text
F = V_period / L
```

设计场：

```text
48 kV/cm × 45.08 nm = 216.384 mV/period
```

50 级有源区的总电压：

```text
V_total = 50 × V_period
```

所以 216.384 mV/周期 对应：

```text
V_total = 10.8192 V
```

这与论文约 10.1–11.88 V 的工作电压范围相符。故本页扫描：

```text
0, 20, 40, ..., 260 mV/period
对应总电压 0–13.0 V
```

这里没有采用官网 QCL 动画的 0–500 mV/周期，因为 500 mV/周期
对应约 111 kV/cm，明显超出该 MOCVD 器件的工作区间。

## 3. 计算模型

| 项目 | 设置 |
|---|---|
| 材料 | In₀.₅₉₃Ga₀.₄₀₇As / Al₀.₆₃₈In₀.₃₆₂As |
| 周期 | 45.08 nm |
| 温度 | 300 K |
| CBO | 0.773 eV |
| 有效质量 | well 0.043 m₀；barrier 0.089 m₀ |
| 空间网格 | 0.2 nm |
| 能量网格 | 5 meV |
| 相干长度 | 1 period |
| IFR | Δ=0.08 nm，Λ=7 nm |
| 合金散射 | strength=0.06，对应 √term≈0.59/0.66 eV |
| 电子–电子散射 | 开启 |
| 声学声子 | 当前版本未计入 |
| 目标跃迁 | 135.26 meV → 9.17 µm |

为覆盖完整低偏压区，新增 0–120 mV 段采用 `G` 收敛阈值
`5e-3`；140–260 mV 主工作区采用 `1e-3`。固定光模钳制点也使用
`1e-3`。低速段输出用于观察 LDOS 和电流趋势，不用于判断增益精度。

## 4. 输入文件

### 4.1 核心 140–220 mV 扫描

```text
D:\Codex-Obsidian\QCL-nextnano\designs\sun2022_mocvd_9um_alloy006_independent_dv060_biasscan.negf
```

对应已完成的输出：

```text
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\negf_alloy006_biasscan_140_220
```

### 4.2 新增低偏压段

0–60 mV：

```text
D:\Codex-Obsidian\QCL-nextnano\designs\sun2022_mocvd_9um_ldos_low_0_120mV.negf
```

80–120 mV：

```text
D:\Codex-Obsidian\QCL-nextnano\designs\sun2022_mocvd_9um_ldos_low_80_120mV.negf
```

### 4.3 新增高偏压段

```text
D:\Codex-Obsidian\QCL-nextnano\designs\sun2022_mocvd_9um_ldos_high_240_260mV.negf
```

### 4.4 一次运行的 0–260 mV 版本

```text
D:\Codex-Obsidian\QCL-nextnano\designs\sun2022_mocvd_9um_ldos_0_260mV.negf
```

### 4.5 固定 9.17 µm 光模

```text
D:\Codex-Obsidian\QCL-nextnano\designs\sun2022_mocvd_9um_9p17um_clamp_216p384mV.negf
D:\Codex-Obsidian\QCL-nextnano\designs\sun2022_mocvd_9um_9p17um_clamp_220mV.negf
D:\Codex-Obsidian\QCL-nextnano\designs\sun2022_mocvd_9um_9p17um_clamp_240mV.negf
```

固定光模设置：

```text
PhotonEnergy = 135.26 meV
CavityLosses = 2.227 cm^-1
OverlapFactor = 0.751
GainClamping = yes
```

生成脚本：

```text
D:\Codex-Obsidian\QCL-nextnano\scripts\gen_sun2022_homepage_style_inputs.py
```

## 5. 输出文件

### 5.1 低偏压输出

```text
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\sun2022_ldos_low_0_120
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\sun2022_ldos_low_80_120
```

### 5.2 核心偏压输出

```text
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\negf_alloy006_biasscan_140_220
```

### 5.3 高偏压输出

```text
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\sun2022_ldos_high_240_260
```

### 5.4 精确设计点和固定光模输出

```text
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\negf_alloy006_216mV
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\sun2022_9p17um_clamp_216p384mV_retry
```

### 5.5 LDOS 原始数据

每个偏压目录：

```text
<Bias>mV\2D_plots\data\DensityOfStates_ZoneCenter.ascii
```

三列为：

```text
position_nm    energy_eV    LDOS_nm^-1_eV^-1
```

导带边：

```text
<Bias>mV\ConductionBandEdge.dat
```

### 5.6 电流、状态占据和增益

```text
<分段目录>\Current_vs_Voltage.dat
<分段目录>\Populations_Eigenstates.dat
<分段目录>\Energy_Eigenstates.dat
<分段目录>\Gain_vs_Voltage.dat
<Bias>mV\EnergyEigenstates\Populations.txt
<Bias>mV\EnergyEigenstates\Lifetimes.dat
<Bias>mV\Gain\Gain_SelfConsistent_vs_Energy.dat
```

### 5.7 固定光模激射输出

```text
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\sun2022_9p17um_clamp_216p384mV_retry\L-I-V.dat
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\sun2022_9p17um_clamp_216p384mV_retry\Gain_vs_Voltage.dat
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\sun2022_9p17um_clamp_216p384mV_retry\216.384mV\Gain\Gain_SelfConsistent_vs_Energy.dat
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\sun2022_9p17um_clamp_220mV\L-I-V.dat
D:\Codex-Obsidian\QCL-nextnano\runs\sun2022_mocvd\sun2022_9p17um_clamp_240mV\L-I-V.dat
```

整理表：

```text
D:\Codex-Obsidian\QCL-nextnano\results\sun2022_homepage_style\fixed_mode_li.csv
```

## 6. 图 1：变偏压 LDOS

![[results/sun2022_homepage_style/figure1_ldos_vs_bias.gif]]

100% 比例的静态 0 mV 图：

![[results/sun2022_homepage_style/figure1_ldos_0mV.png]]

### 阅读方法

- 白色细线是导带边；
- 高亮红／黄区域是二维局域态密度峰；
- 低偏压时能级接近平带，态在单个量子阱内局域；
- 140–180 mV 时，相邻阱中的上、下态逐渐对齐，出现注入共振和
  明显的态混合；
- 高于 200 mV 后，Wannier–Stark 倾斜继续增大；空间波函数逐渐
  从左到右错开；
- 这不是“能级整体移动”这么简单，而是每个态与相邻周期态的
  耦合、展宽和占据同时变化。

图中纵轴以每个偏压下的最低导带边为零点，便于比较不同偏压下的
相对能级位置。原始 ASCII 保留 nextnano 的内部能量零点。

## 7. 图 2：电流–电压特性

![[results/sun2022_homepage_style/figure2_current_voltage.png]]

主要数据：

| 每周期偏压 | 50 级总电压 | 电流密度 |
|---:|---:|---:|
| 0 mV | 0 V | ≈−0.03 kA/cm² |
| 80 mV | 4 V | 0.335 kA/cm² |
| 120 mV | 6 V | 0.871 kA/cm² |
| 140 mV | 7 V | 1.121 kA/cm² |
| 160 mV | 8 V | 1.555 kA/cm² |
| 180 mV | 9 V | 1.997 kA/cm² |
| 200 mV | 10 V | 2.371 kA/cm² |
| 216.384 mV | **10.819 V** | **2.578 kA/cm²** |
| 220 mV | 11 V | 2.631 kA/cm² |
| 240 mV | 12 V | 2.782 kA/cm² |
| 260 mV | 13 V | 2.673 kA/cm² |

0 mV 的微小非零数值是电流归一化残差，不是物理漏电。电流在
240 mV 附近达到最大值，随后开始滚降；同时 260 mV 的有效电子
温度约 3495 K，表明高场下热化与泄漏迅速增强。

模型 I–V 达到论文 \(J_{th}=1.52\ \mathrm{kA/cm^2}\) 的位置约为
158.4 mV/周期，即约 7.92 V 的 50 级总压降。这只能说明“电流达到
论文阈值”，不能单独证明同一偏压已经满足光学阈值。

## 8. 粒子数反转

![[results/sun2022_homepage_style/figure3_population_inversion.png]]

这里使用 NEGF 的 14 个周期内 Wannier–Stark 状态作可复现诊断：

```text
上态流形：S6 + S7
下态流形：S8 + S9
反转量：ΔP = P(S6+S7) − P(S8+S9)
```

在 216.384 mV：

```text
S6↔S8 能差 = 137.7 meV，|z| = 1.268 nm
```

这与独立 k·p 的 9.17 µm 主通道：

```text
E3→E1 = 135.26 meV，|z| = 1.287 nm
```

在能量和偶极上同时吻合，因此 `S6→S8` 是当前 NEGF 基组中可追踪的
9 µm 分支代理。其四个 DAU/MS 通道为：

| 通道 | 216.384 mV 时的能量差 | 对应波长 |
|---|---:|---:|
| S6→S8 | 137.7 meV | 9.00 µm |
| S6→S9 | 153.3 meV | 8.09 µm |
| S7→S8 | 100.5 meV | 12.34 µm |
| S7→S9 | 116.1 meV | 10.68 µm |

两个上态到两个下态的多个通道形成宽增益，因此不能只看一对相邻能级。
`S6+S7` 与 `S8+S9` 是流形级诊断量，不是把论文 E1–E5 标签机械照搬到
NEGF 编号。

本计算的流形反转：

| 偏压 | 上态流形 | 下态流形 | ΔP |
|---:|---:|---:|---:|
| 0 mV | 0.0035 | 0.0135 | −0.0100 |
| 120 mV | 0.0508 | 0.1141 | −0.0632 |
| 140 mV | 0.1636 | 0.0538 | +0.1098 |
| 160 mV | 0.2183 | 0.0802 | +0.1382 |
| 180 mV | 0.2447 | 0.0933 | +0.1515 |
| 216.384 mV | 0.2204 | 0.1185 | +0.1020 |
| 240 mV | 0.2249 | 0.1337 | +0.0913 |
| 260 mV | 0.2255 | 0.1432 | +0.0823 |

反转在 180 mV 附近达到最大，超过约 200 mV 后下降。主要原因是下态热
占据、电子温度升高，以及上态向高能态的泄漏增加。高偏压并不自动等于
更高反转。

## 9. 状态占据图

![[results/sun2022_homepage_style/figure3_population_occupation_map.png]]

该图把 14 个周期内状态的归一化占据排成二维矩阵：

- 底部的低能态始终占据较高；
- 100–140 mV 之间状态排序和流形组成会发生明显重排；
- 160–220 mV 区间可看到上态流形被选择性地填充；
- 240–260 mV 时，下态流形与高能泄漏态占据增加。

## 10. 增益、阈值与激射过程

![[results/sun2022_homepage_style/figure4_gain_vs_bias.png]]

导波模型的材料增益阈值：

```text
Γcore = 0.751
镜面损耗 + 无源损耗 = 2.227 cm^-1
g_material,th = 2.227 / 0.751 = 2.97 cm^-1
```

9.17 µm 的材料增益：

| 偏压 | gain@135.26 meV |
|---:|---:|
| 140 mV | −2.17 cm⁻¹ |
| 160 mV | +0.02 cm⁻¹ |
| 180 mV | +2.55 cm⁻¹ |
| 200 mV | +5.07 cm⁻¹ |
| 216.384 mV | +6.73 cm⁻¹ |
| 240 mV | +9.46 cm⁻¹ |
| 260 mV | +10.12 cm⁻¹ |

插值得到阈值偏压：

```text
固定 9.17 µm 的材料增益阈值约 183.3 mV/period
```

更精确按图上电流插值为：

```text
J_th,model(9.17 µm) ≈ 2.06 kA/cm²
```

论文脉冲阈值：

```text
J_th,paper = 1.52 kA/cm²
```

因此当前 NEGF 阈值比实验高约 35%，但仍处于同一量级。模型在 160 mV
时电流约 1.555 kA/cm²，已经达到论文阈值电流，但 9 µm 材料增益才刚好
跨零，说明模型仍低估了真实器件的增益/载流子约束。

## 11. 为什么模型优先选择长波

![[results/sun2022_homepage_style/figure5_gain_heatmap.png]]

虽然 9.17 µm 增益为正，但自由运行峰始终位于更长波长：

- 140–220 mV：全局峰约 120 meV，即 10.33 µm；
- 240–260 mV：峰移到约 125 meV，即 9.92 µm；
- 图 1 的长波黑线代表 9.17 µm 目标，不是全局峰。

因此只用无波长选择的 FP 腔时，模型会优先在 10 µm 附近激射。
要得到论文报告的 9 µm，必须有足够的波长选择，例如增益谱本身、
外腔选择或 DFB 光栅。

## 12. 固定 9.17 µm 光模的阈值检查

在 216.384 mV、固定 135.26 meV 光模下重新进行增益钳制：

```text
J = 2.57796 kA/cm²
内部净输出功率 = 3090.4 W/cm³
材料增益（自洽钳制）≈ 2.87 cm^-1
模态增益 ≈ 2.155 cm^-1
腔损耗 = 2.227 cm^-1
腔内光场 = 48593 V/m
内部 WPE ≈ 2.50×10^-5
```

扩展固定光模计算：

| 每周期偏压 | 总电压 | 电流密度 | 净内部光功率 | 内部 WPE |
|---:|---:|---:|---:|---:|
| 216.384 mV | 10.82 V | 2.578 kA/cm² | 3.09 kW/cm³ | 2.50×10⁻⁵ |
| 220 mV | 11.00 V | 2.638 kA/cm² | 96.9 kW/cm³ | 7.52×10⁻⁴ |
| 240 mV | 12.00 V | 2.839 kA/cm² | 3.81 MW/cm³ | 2.52×10⁻² |

![[results/sun2022_homepage_style/figure7_fixed_mode_lasing.png]]

物理含义：

- 216.384 mV 时已有很小光场，腔接近阈值；
- 216.4→220 mV 之间内部光功率跳升约 31 倍，是明显的过阈值特征；
- 240 mV 时内部 WPE 达约 2.5%，说明固定 9.17 µm 光模已进入较强激射区；
- 216.384 mV 的钳制模态增益约 2.155 cm⁻¹，仍略低于 2.227 cm⁻¹
  腔损耗；
- 216.384 mV 不能解释成高效率、强 CW 工作点；
- 论文的 1.52 kA/cm² 阈值来自真实器件，当前 NEGF 仍高估阈值并压低增益。

线性增益外推给出的阈值约 2.06 kA/cm²，而带光场钳制的动态过阈值
发生在约 2.58–2.64 kA/cm²。两者使用不同的增益输出归一化，不能混成
一个数值；在 nextnano 确认 `Gain_SelfConsistent` 与
`gain from emitted power` 的精确定义前，应以固定光模的功率跃升作为
“是否出现受激辐射”的更直接证据。

## 13. 粒子数反转到激射的完整物理链

![[results/sun2022_homepage_style/figure6_lasing_process.png]]

1. **注入共振**：场把 injector 基态与 E3/E4 上态拉近，电子通过
   共振隧穿进入上态流形。
2. **选择性抽取**：下态通过 LO 声子快速排空，上态寿命较长，形成
   `ΔP>0`。
3. **宽谱增益**：两个上态到两个下态形成四通道；各通道能量和偶极不同，
   因而增益峰宽，不集中在一个 delta-like 能级对。
4. **阈值前**：材料增益随偏压升高，但 `Γg < α_i+α_m`。自发辐射和
   非辐射散射占主导。
5. **阈值处**：`Γg = α_i+α_m`。光场不再衰减，开始自持放大。
6. **阈值上**：受激复合钳制反转与增益，电流继续增加而增益接近饱和，
   输出功率上升；若热化/泄漏过强，则出现电流滚降。
7. **本模型的风险**：自由运行峰偏长波。即使 9 µm 有正增益，也需要
   波长选择；否则真实 FP 腔可能先在其他模式达到阈值。

## 14. 结论

- 该结构确实形成双上态、多下态的宽增益体系；
- 约 140 mV 后流形反转明显建立，180 mV 附近达到最大；
- 9.17 µm 在 160 mV 附近增益跨零，约 183 mV 达到材料阈值；
- 模型阈值约 2.06 kA/cm²，高于论文 1.52 kA/cm²；
- 固定 9.17 µm 光模在 216.384 mV 出现近阈值光场，并在 220–240 mV
  给出快速上升的内部光功率与 WPE；
- 自由运行增益峰在 10.3 → 9.9 µm，模型仍偏好长波；
- 因而不把这次计算认定为“严格复现论文 9 µm 激射”，而认定为
  “结构、波长分支和反转趋势已复现，绝对阈值与自由运行峰位仍冲突”。

## 15. 一键复现

```powershell
C:\Users\ciomp\anaconda3\python.exe scripts\gen_sun2022_homepage_style_inputs.py
C:\Users\ciomp\anaconda3\python.exe scripts\plot_sun2022_bias_figures.py
```

绘图脚本：

```text
D:\Codex-Obsidian\QCL-nextnano\scripts\plot_sun2022_bias_figures.py
```

汇总图和表：

```text
D:\Codex-Obsidian\QCL-nextnano\results\sun2022_homepage_style\
```

为进行第二轮 10.33 µm 设计而不覆盖本轮展示结果，本目录已冻结为：

```text
D:\Codex-Obsidian\QCL-nextnano\results\sun2022_round1_9p17um_and_freerun
```

## 相关笔记

- [[Sun2022-10p33um第二轮设计与两轮比较]]
- [[41-文献复现-Sun2022-9um-MOCVD-DAU]]
- [[44-五级验证闸门-Sun2022态映射增益与波导]]
- [[Sun2022-NEGF完整验证报告]]
- [[Sun2022验证输入逐行注释]]
- [[变电压粒子数反转动画]]
- [[nextnano官网Figure1-2复现]]
