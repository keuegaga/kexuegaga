# 官方 Bai APL 2011 NEGF 工作流校准

> 2026-10-22。按 [[39-8um-NEGF校准-偏压掺杂与CBO]] 的建议，使用 nextnano 自带、具有已知激射行为的 InGaAs/InAlAs 中红外案例做二次校准。

## 1. 校准对象

官方输入：

```text
MidIR_QCL_InGaAs_InAlAs_Bai_APL2011_GainClamping.negf
```

文献：

- Y. Bai et al., Appl. Phys. Lett. **98**, 181102 (2011)
- DOI：`10.1063/1.3586773`
- 设计：室温 QCL，27% wall-plug efficiency

本次只把官方扫描的 280–420 mV 改为已知激射单点 **360 mV**，材料、层序、散射、掺杂、腔损耗和钳制设置均保持官方值。

文件：

- 生成脚本：`scripts/gen_official_bai_calibration.py`
- 单点输入：`designs/bai2011_official_360mV_calibration.negf`
- 输出：`runs/official_calibration/bai2011_360mV_fresh/`

## 2. 收敛结果

| 判据 | 结果 | 状态 |
|---|---:|---|
| Green 函数收敛因子 | 6.135×10⁻⁵ | 通过 |
| 电流收敛因子 | 9.459×10⁻⁵ | 通过 |
| 电荷归一化偏差 | 7.311×10⁻⁴ | 通过 |
| Poisson 收敛因子 | −1.090×10⁻⁴ | 通过 |

NEGF 明确报告：

```text
Simulation has fully converged
Green's functions: Converged
Current: Converged
Charge normalization: Close to 1
Electrostatic potential: Converged
```

## 3. 激射校验

目标光模能量：**253 meV**

| 量 | 结果 |
|---|---:|
| 材料增益 | 5.52056 cm⁻¹ |
| 光限制因子 | 0.5 |
| 模态增益 | **2.76028 cm⁻¹** |
| 腔损耗 | **2.76 cm⁻¹** |
| 钳制误差 | \|2.76028 − 2.76\| = **0.00028 cm⁻¹** |
| 腔电场 | 8.60528×10⁶ V/m |
| 电流密度 | 5789.5 A/cm² |
| 电子温度 | 922.738 K |
| 净内部输出功率 | 1.7768×10⁸ W/cm³ |
| Internal WPE | 37.07% |

`GainFromEmittedPower.dat` 报告：

```text
Photon energy      = 253 meV
Material gain      = 5.52056 cm^-1
Modal gain         = 2.76028 cm^-1
Cavity loss        = 2.76 cm^-1
Cavity field       = 8.60528e6 V/m
Net emitted power  = 1.7768e8 W/cm^3
```

结论：官方案例在当前 nextnano 2025_08_21、当前许可证和当前 NEGF 工作流下，能够稳定复现“模态增益 = 腔损耗”的钳制条件，并产生非零激光输出。

## 4. 子阈值端对照

把同一官方结构先放在扫描首点 280 mV：

- 初始材料增益约 2 cm⁻¹；
- 模态增益约 1 cm⁻¹；
- 低于 2.76 cm⁻¹ 腔损耗；
- 腔场启动后衰减，未形成稳定激光态。

这符合物理预期，说明“低于损耗不激射、高于损耗钳制”的控制逻辑没有反转。

## 5. 对本项目 Liu 结构的含义

已验证通过：

| 系统层级 | 状态 |
|---|---|
| nextnano.NEGF 可执行程序 | 通过 |
| NEGF 许可证 | 通过 |
| GainClamping 光场反馈 | 通过 |
| 收敛判据 | 通过 |
| L-I 输出功率 | 通过 |

因此 Liu 结构在 8 µm 附近持续给出负自洽增益，不能归因于：

- 程序安装错误；
- 许可证问题；
- `GainClamping=yes` 的使用方式；
- 自洽增益文件本身失效；
- 钳制路径无法产生正输出。

问题已定位到 Liu 模型本身，优先级调整为：

1. In₀.₆Ga₀.₄As/Al₀.₅₈In₀.₄₂As 的有效质量、非抛物性和带阶；
2. 官方案例启用的压电/热释电设置；
3. 多周期重建、周期边界和掺杂区解释；
4. 论文主动区层序或材料组分是否存在未识别的排版/转录误差；
5. 原文计算所用模型参数与本机数据库版本差异。

## 6. 压电/热释电单变量实验（已执行）

官方与当前 Liu 输入之间此前剩余的一项设置差异：

```text
官方 Bai: Piezoelectricity = yes, Pyroelectricity = yes
当前 Liu: Piezoelectricity = no,  Pyroelectricity = no
```

保持 Liu 结构、240 mV、低掺杂和 CBO 0.72 eV，只打开这两项后：

| 量 | 关闭 | 开启 |
|---|---:|---:|
| 电流 | 2315.95 A/cm² | 2315.95 A/cm² |
| 电子温度 | 1203.22 K | 1203.22 K |
| 自洽155 | −4.723848 cm⁻¹ | −4.723848 cm⁻¹ |
| L-I 输出 | 0 | 0 |

两份 `Gain_SelfConsistent_vs_Energy.dat` 的 SHA256 均为：

```text
75AE2EB480503F6E673BE5F9DF5A75E2302DA1F4485250413870F830A1091E3F
```

因此对当前 (100) 生长模型，打开压电/热释电没有数值影响。该项已被排除。

输入：

- `designs/liu2022_dau_240mV_lowdoping_piezo.negf`
- `runs/liu2022_dau_negf/lowdoping_240mV_piezo/`

## 7. 下一项单变量实验

下一轮应保持层序、偏压和低掺杂不变，转向：

1. 从能带来源统一校准 In₀.₆Ga₀.₄As 与 Al₀.₅₈In₀.₄₂As 的电子有效质量；
2. 检查非抛物性与带阶是否必须成套调整，避免只改 CBO；
3. 将一个完整的多周期结构送入 NEGF，排查单周期边界与周期平均的影响。

不应继续同时调整层厚、掺杂和偏压来“追正增益”。

## 8. 当前结论

```text
NEGF 工作流：已验证
官方已知器件：成功复现钳制与非零输出
Liu 8 µm 重建：仍未复现正自洽增益
压电/热释电：对 (100) 模型无影响，已排除
下一根因：有效质量/非抛物性、多周期边界或层序转录
```

## 相关笔记

- [[39-8um-NEGF校准-偏压掺杂与CBO]]
- [[38-8um-Liu-DAU-NEGF验证与负结果]]
- [[29-第1步-腔损耗与钳制验证]]
