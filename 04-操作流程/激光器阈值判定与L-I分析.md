---
title: 激光器阈值判定与调参（PICS3D）
type: workflow
product: PICS3D
version: 2024
status: verified
source: "实测：nakamura 完整版 8 个数据集 + s2.plt 后处理（2026-09-16）；[[99-原始资料/通用手册/manual.pdf]] §4.2（P84-85）、§23.386 init_wave、§23.445 longitudinal、§23.576 plot_data（P1026-1027）"
last_verified: 2026-09-16
tags:
  - crosslight
  - workflow
  - pics3d
  - laser
  - threshold
  - li-curve
---

# 激光器阈值判定与调参（PICS3D）

## 目标

判断器件**是否激射、阈值电流多少**；以及当 L-I 曲线看不到拐点时该怎么处理、怎么把图导出。

## 实测结果（nakamura 完整版，默认参数，2026-09-16）

| 项 | 实测值 |
|---|---|
| **阈值电流** | **≈ 20 mA**（用 30~60 mA 段线性外推：dP/dI = 0.623 W/A，I_th = 20.2 mA） |
| 60 mA 时的双端面输出功率 | **24.53 mW** |
| 60 mA 时的电压 | 3.874 V |
| 20.4 mA 时的电压 | 3.692 V |
| L-I 第一个非零点 | 21.83 mA → 0.551 mW（正好是光耦合扫描的起点） |

**结论：这个示例器件是能正常激射的。**

L-I 数据（从 `jplot024.tmp` 提取，隔点取样）：

| I (mA) | P (mW) | 局部 dP/dI (W/A) |
|---|---|---|
| 20.37 | 0.000 | — |
| 21.73 | 0.000 | — |
| **21.83** | **0.551** | — |
| 28.93 | 4.753 | 0.80 |
| 40.73 | 12.763 | 0.59 |
| 51.23 | 19.404 | 0.61 |
| 60.00 | 24.529 | 0.56 |

## ⚠️ 重要教训：不要用 `.sol.msg` 的 `Modal_gain` 与 `Int._loss` 直接判断阈值

2026-09-16 我曾按"`Modal_gain` < `Int._loss` + 镜面损耗 ⇒ 到不了阈值"来推断，**结论是错的**：

- 60 mA 时 `.sol.msg` 给出 `Modal_gain = 1182 /m`、`Int._loss = 1307 /m`，按简单比较"连透明都没到"；
- 但**同一轮**的 L-I 实测显示：器件在 ~20 mA 就起振，60 mA 输出 24.5 mW。

→ **判断阈值请以 L-I（RTG 双端面功率）或 RTG 本身为准。** `.sol.msg` 里那两列不能这样直接相加比较。

> 待办：为什么那两列与阈值条件不一致（是波长对应关系、还是列的定义不同）尚未查清——查清后回来补这一节。

## 为什么这一轮的 L-I 看不到拐点

`solve_rtg=yes`（打开光子耦合）只在**最后一段扫描**里出现，而它从 21.73 mA 才开始：

- 21.73 mA 之前光子密度被**强制为 0**（不是物理结果）→ 0~21.73 mA 那段"平的 L-I"是**设置造成的假象**；
- 真正的拐点（≈20 mA）刚好落在耦合扫描起点之前，所以没被记录到。

**想让拐点可见**：让光耦合段从**阈值以下**开始。做法是把 RTG 初始化扫描的终止值调低——

```text
scan var=current_1 value_to=300e-3 print_step=50e-3 &&
init_step=1e-5 min_step=1.e-6 max_step=5e-3 var2=time value2_to=10 &&
auto_finish=rtgain auto_until=0.6 auto_within=0.1        $ 0.6 -> 试 0.3~0.4
```

手册 §4.2 的原意正是"终止值取**刚高于透明、且低于阈值**"。（代价：要从头重跑一遍。）

## 出图：`pics3d xxx.plt` 之后还要跑 gnuplot

实测（2026-09-16）：`pics3d s2.plt` 只做两件事——

1. 算出各条曲线的数据，写成 `jplot001.tmp … jplot0NN.tmp`；
2. 写出 gnuplot 脚本 `junkg.tmp`。

**PDF 本身要由 gnuplot 生成**。本例 gnuplot 那一步没有自动执行，所以目录里没有 PDF（但有全套数据和脚本）。手动补上：

```powershell
cd <算例目录>
& 'C:\Program Files\Crosslight Software\pics3d_2024\pics3d\GNUPLOT.EXE' junkg.tmp
```

生成的 **`output.pdf`** 就在算例目录里（多页）。注意脚本里写的是 `set output "output.pdf"`，所以文件名是 **`output.pdf`**，不是 `s2.pdf`。

各 `jplot` 文件与图的对应关系（取自 `junkg.tmp`）：

| 文件 | 图 |
|---|---|
| jplot001-003 / 005-007 | 能带（全结构与有源区放大） |
| jplot009-012 | 电子/空穴浓度（对数与线性） |
| jplot013-014 | 电子/空穴电流密度 |
| jplot015-016 | 总电流密度分布（二维） |
| jplot017-022 | 3 个横向模式的光强分布 |
| **jplot023** | **I-V（电压-电流）** |
| **jplot024** | **L-I（电流-双端面总功率）** |
| jplot025-027 | L-I（各纵模） |
| jplot028 | 增益谱 |

> 小技巧：`jplot*.tmp` 是纯文本两列数据，可以直接用 Excel/Python 读出来自己画（本笔记的 L-I 表就是这么来的）。若报"找不到 s2.pdf"，把 `.plt` 里 `plot_device=pdf` 改成 `postscript` 或直接照上面手动跑 gnuplot。

## 调参试验：已从计划中划掉（2026-09-16）

原计划的四个参数敏感度试验**取消**：

| 原编号 | 原计划改动 | 状态 |
|---|---|---|
| T1 | `init_wave backg_loss=1300.` → `500.` | ❌ 划掉 |
| T2 | `set_active_reg gain_coulomb=no` → `yes` | ❌ 划掉 |
| T3 | `left_f_refl/right_f_refl` 0.5 → 0.9 | ❌ 划掉 |
| T4 | T1 + T3 组合 | ❌ 划掉 |

**取消理由**：这组试验是建立在"器件到不了阈值"的**误判**之上的；实测 L-I 证明默认参数本来就能激射（阈值 ≈20 mA、60 mA 出 24.5 mW）。四份试验文件已归档到 `06-案例/_未使用_阈值调参试验/`，保留备查、平时不用跑，要删随时可删。

将来若确实要**主动调设计**（而不是解决"不激射"），方向与判据如下——判据一律用 L-I，不要再用 `Modal_gain` 与 `Int._loss` 的比较：

| 想要的效果 | 可调的旋钮 |
|---|---|
| 阈值电流下降 | `init_wave backg_loss` 调小；`left_f_refl/right_f_refl` 调大（并注意真实解理面约 0.18） |
| 增益抬高 | `set_active_reg gain_coulomb=yes`；`valence_mixing=yes`（更真实、明显更慢） |
| 波长调整 | 有源区组分/厚度 + `init_wave wavel_range`（并保持窗口罩住目标波长） |

## 结果记录

| 项 | 默认参数实测 | 备注 |
|---|---|---|
| 阈值电流 | ≈ 20.2 mA | 线性外推 |
| 60 mA 双端面功率 | 24.53 mW | |
| 微分效率 dP/dI（30~60 mA） | 0.623 W/A | |
| 60 mA 电压 | 3.874 V | |

## 相关笔记

- [[04-操作流程/PICS3D续算与光耦合初始化]]（三段偏置与 RTG 初始化）
- [[06-案例/nakamura-sol逐行注释]]
- [[05-API与命令/核心参数]]
- [[00-入口/知识库规范]]

## 来源

实测：nakamura 完整版（PICS3D 2024.02.01，Windows 11），8 个数据集 #1~#8（0 → 60.00 mA），后处理脚本 `s2.plt`（本库改写版见 `06-案例/nakamura_analysis.plt`），L-I/I-V 数据取自 `jplot024.tmp` / `jplot023.tmp`。

手册：[[99-原始资料/通用手册/manual.pdf]] §4.2（P84-85，RTG 终止值应低于阈值）、§23.386 `init_wave`、§23.445 `longitudinal`、§23.576 `plot_data`（P1026-1027，`plot_device=pdf/postscript/windows/data_file`）。
