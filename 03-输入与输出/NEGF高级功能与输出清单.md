---
title: NEGF 高级功能与输出清单
type: reference
product: nextnano.NEGF
version: 2025.08.21
status: verified
source: C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\examples
last_verified: 2026-10-23
tags:
  - qcl
  - negf
  - outputs
  - advanced
---

# NEGF 高级功能与输出清单

## 本库已经实际使用

| 功能/输出 | 输入或文件 | 用途 |
|---|---|---|
| 电压扫描 | `SweepParameters{ SweepType=Voltage }` | 阈值、I-V、粒子数反转 |
| NEGF 自洽 | `Poisson=yes` | 电荷与静电势耦合 |
| 3-band 非抛物性 | `NumberOfBands=3` | 中红外导带 |
| LO / IFR / alloy / impurity / e-e | `Scattering{ }` | 寿命、线宽、电流 |
| 状态占据 | `Populations_Eigenstates.dat` | 粒子数反转动画 |
| 密度矩阵 | `DensityMatrix_elements.txt` | 对角占据与周期间相干 |
| 状态寿命 | `Lifetimes.dat` | 上/下态寿命 |
| 散射分解 | `ScatteringRate_mechanisms.dat` | LO/IFR/alloy 来源 |
| 面内色散 | `InplaneDispersion.dat` | 非抛物性与态密度 |
| 谱函数 | `SpectralFunctions.dat` | 展宽和态分布 |
| 自洽增益 | `GainMethod=1` | 最可靠的中红外净响应 |
| FGR 增益 | `FermiGoldenRule{ }` | 第二种方法与跃迁分解 |
| 宽窗增益 | 60–180 meV | 防止边界最大值误判 |
| 位置分辨增益 | `Gain/data/*.ascii` | 判断增益来自哪一层 |
| 空间波函数 | `EigenStates.dat` | 态定位 |
| 偶极/振子强度 | `Dipoles.txt`、`Oscillator_Strength.txt` | 光学跃迁 |

## 已测试但不能使用

| 功能 | 结论 |
|---|---|
| `AcousticPhononScattering=yes` | 2025-05-23 引擎提示尚未实现，自动置零 |
| 8-band NEGF 生产计算 | 当前官方说明仅限准平衡，不能替代本案例 3-band 输运 |

## 可继续开发

| 功能 | 条件 |
|---|---|
| 增益钳制与 L-I | 配置损耗、重叠因子和 EM mode |
| 光子辅助输运 | 合理设置 `EMfield{ EMmode{ } }` |
| Tight-binding 对照 | 增加 `AnalysisSeparator{ }` |
| 温度扫描 | 扩展 `SweepParameters` |
| 8-band k·p 光学对照 | 使用 nextnano++ 做能带/偶极二次校验 |

## 禁止项

- 不使用 alloy strength 等隐藏参数作为设计自由度数拟合目标波长；
- 不把 acoustic keyword 被接受等同于物理散射已实现；
- 不把单个 transition decomposition 编号未经基组核对就当作物理态编号。
