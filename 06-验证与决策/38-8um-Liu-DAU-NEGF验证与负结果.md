# 8 µm Liu-DAU NEGF 验证与负结果

> 2026-10-22。对 [[37-8um-Liu-DAU能带筛选与设计]] 的候选结构完成 300 K、270 mV/周期的 NEGF 诊断。结论：FGR 有正增益，但自洽增益为负，**当前版本判定不激射**。

## 1. 输入模型

| 项目 | 值 |
|---|---:|
| 输入 | `designs/liu2022_dau_8um_fgr.negf` |
| 温度 | 300 K |
| 偏压 | 270 mV/周期 |
| 实际电场 | 43.97 kV/cm |
| 周期长度 | 61.4 nm |
| 掺杂 | 42.6–53.1 nm，2.5×10¹⁷ cm⁻³ |
| 片密度 | 2.625×10¹¹ cm⁻² |
| 导带带阶 | 0.72 eV（nextnano 模型） |
| 数值 | 横向 400 meV / 25 meV，轴向 500 meV，0.2 nm |
| 收敛判据 | GF/电流均 1×10⁻³ |

该运行已明确报告：

```text
Green's functions: Converged
Current: Converged
Charge normalization: Close to 1
Electrostatic potential: Converged
```

因此以下结论不是未收敛造成的。

## 2. 输运结果

| 量 | NEGF 结果 | 文献/物理解读 |
|---|---:|---|
| 电流密度 | **1.031×10⁴ A/cm²** | 远高于 Liu 器件阈值约 1.4 kA/cm² |
| 平均电子速度 | 15.05 nm/ps | 电流对应穿过一个周期 4.08 ps |
| 平均电子温度 | **1347.5 K** | 强烈电子过热 |
| 每周期电子数 | 1.116 | 与片密度同量级 |
| L-I 输出功率 | **0** | 无激光输出 |

子带温度从 831 K 到 2170 K，全部远高于晶格 300 K。该状态下热回填和上态漏电会严重破坏可持续反转。

## 3. 增益的两个层级

| 光子能量 | 波长 | FGR 材料增益 | 自洽增益 | 自洽模态增益（×0.5） |
|---:|---:|---:|---:|---:|
| 145 meV | 8.55 µm | +9.20 cm⁻¹ | −7.48 cm⁻¹ | −3.74 cm⁻¹ |
| 150 meV | 8.27 µm | +17.23 cm⁻¹ | −8.54 cm⁻¹ | −4.27 cm⁻¹ |
| **155 meV** | **8.00 µm** | **+28.87 cm⁻¹** | **−9.52 cm⁻¹** | **−4.76 cm⁻¹** |
| 160 meV | 7.75 µm | +36.18 cm⁻¹ | −10.32 cm⁻¹ | −5.16 cm⁻¹ |
| 165 meV | 7.52 µm | +19.66 cm⁻¹ | −10.81 cm⁻¹ | −5.41 cm⁻¹ |

在 145–165 meV 窗口，FGR 最大值为 **36.86 cm⁻¹ @159 meV（7.80 µm）**。

但自洽增益全部为负，且 FGR 与自洽增益符号相反。按 [[29-第1步-腔损耗与钳制验证]] 建立的判据：

```text
modal gain = self-consistent gain × overlap
           = -9.52 × 0.5
           = -4.76 cm^-1

-4.76 cm^-1 < cavity loss 5 cm^-1
```

所以本候选不满足激射条件。

![[fig_liu2022_dau_gain_fgr_vs_selfconsistent.png]]

## 4. 为什么不能把 +28.9 cm⁻¹ 当成功

FGR 计算的是给定电子分布下的小信号光学响应，允许局部跃迁产生正增益；它没有完整约束：

- 光场反馈；
- 激光钳制；
- 电流连续性下的可持续占据；
- 局部焦耳热与电子温度；
- 吸收区与增益区的净平衡。

本次结果中 FGR 正、自洽负，说明 155 meV 附近的局部辐射跃迁不足以抵消同一输运状态下的净吸收，或者当前电子分布并非真实器件的工作分布。

## 5. 最可疑的模型环节

按优先级：

### 5.1 工作点

270 mV/周期使模型电流达到 10.3 kA/cm²，电子气过热到 1348 K。真实 1.4 kA/cm² 阈值远低于此，说明应该先做低偏压扫描，而不是把 270 mV 当作阈值点。

### 5.2 输运散射参数

当前使用了从 Fei 项目继承的散射设置：

```text
AcousticPhononScattering = no
ElectronElectronScattering = no
AlloyScatteringStrength = 0.5
```

官方高场 QCL 钳制示例使用：

```text
ElectronElectronScattering = yes
AlloyScatteringStrength = 1.0
LateralDiscretization = 50 meV
EnergyRangeLateral = 500 meV
EnergyRangeAxial = 550 meV
```

电子-电子散射缺失可能使高场电子分布过热，必须先校准。

### 5.3 带阶

nextnano++ 的应变模型给出约 0.72 eV。需要以 Liu 的实测 7.4 µm 为锚点，对比 0.60–0.72 eV 的 CBO 敏感性；不能假定数据库值就是实验器件值。

### 5.4 掺杂解释

PDF 矢量下划线确实跨越第 16–19 层，但从扫描版式解释“连续下划线”为四层均匀掺杂仍应做一次低掺杂对照。建议设置 `0.7×10¹¹` 与 `2.63×10¹¹ cm⁻²` 两档。

## 6. 已排除的解释

| 解释 | 状态 |
|---|---|
| 输入语法错误 | 排除；完整运行通过 |
| NEGF 未收敛 | 排除；GF、电流、势均已收敛 |
| 8 µm 附近没有 FGR 峰 | 排除；155–160 meV 有清晰峰 |
| 8 µm 附近没有轴向态 | 排除；第二微带 156.85 meV |
| 只是缺少一个很小的数值修正 | 不太可能；自洽增益与损耗差 9.8 cm⁻¹ |

## 7. 下一轮实验顺序

### 必做 A：低偏压与散射校准

建议点：

| 偏压 mV | 目的 |
|---:|---|
| 220 | 检查低场注入与电流 |
| 240 | 接近可能的阈值区 |
| 260 | 逼近设计共振 |

首轮只计算 155–160 meV，避免宽能量后处理。

### 必做 B：文献锚点回算

在 Liu 原设计 48 kV/cm（约 295 mV）计算 7.4 µm/163 meV：

- 若自洽增益可正，说明偏压/能量映射可用；
- 若同样为负，说明材料、散射或掺杂模型仍需校准；
- 在任何 8 µm 优化前，必须先复现已有器件的量级。

### 条件分支

| 低偏压结果 | 下一步 |
|---|---|
| 电流降到 1–3 kA/cm²，自洽增益转正 | 扫 250–290 mV 找阈值与 8 µm 工作点 |
| 电流降低但增益仍负 | 校准 CBO、掺杂和 e-e 散射 |
| 只在偏离 155 meV 时正 | 微调第 4 层或其他有源阱后重新锁定波长 |

## 8. 设计结论

k·p 筛选通过：

```text
155.5 meV / 7.98 µm / |z|=1.39 nm
```

NEGF 激射判据未通过：

```text
modal gain -4.76 cm^-1 versus loss 5 cm^-1
```

因此保留 Liu-DAU 作为材料与能带基线，**不把当前 270 mV 版本视为可制造最终设计**。

## 文件

- NEGF 输入：`designs/liu2022_dau_8um_fgr.negf`
- 收敛运行：`runs/liu2022_dau_negf/fgr_270_final/`
- 自洽增益：`runs/liu2022_dau_negf/fgr_270_final/270mV/Gain/Gain_SelfConsistent_vs_Energy.dat`
- FGR 增益：`runs/liu2022_dau_negf/fgr_270_final/270mV/Gain/Gain_FermiGoldenRule_vs_Energy_[0,0,1].dat`
- 占据：`runs/liu2022_dau_negf/fgr_270_final/270mV/EnergyEigenstates/Populations.txt`

## 相关笔记

- [[39-8um-NEGF校准-偏压掺杂与CBO]]
- [[37-8um-Liu-DAU能带筛选与设计]]
- [[35-QCL能带设计谱系-从BB到STA-RE]]
- [[36-QCL设计法则与全外延结构权衡]]
- [[29-第1步-腔损耗与钳制验证]]
