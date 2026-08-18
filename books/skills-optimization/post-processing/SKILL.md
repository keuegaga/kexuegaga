---
name: post-processing
description: |
  用户在 Crosslight 仿真完成后需要提取/绘图结果（L-I、IV、增益谱、模场、能带），或处理 scan_data/xy_data、
  数据集编号、.plt 文件、get_data/plot_scan/gain_spectrum、变量不可用（more_output）、CrosslightView 时。
  触发信号：.plt、plot、L-I 曲线、绘图、画不出来、变量不存在、scan_data、xy_data、数据集编号、
  more_output、CrosslightView 等。不适用于：仿真前预览（用 gain-preview-workflow）、仿真本身。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第3章 (P72-75) / 附录G (P1357-1373)
tags: [post-processing, plotting, data, plt]
related_skills:
  - slug: pics3d-laser-workflow
    relation: composes-with
---

# 后处理：数据组织、变量与绘图

## R — 原文 (Reading)

> "the output data is divided into two categories: bias-dependent data (scan_data) and
> structural/spectral data (xy_data). ... all output data is assigned a 'data set number'
> for later use."
>
> — Crosslight Software Inc., 第3章 §3.9 (P72-73)

## I — 方法论骨架 (Interpretation)

Crosslight 的输出不是一个大文件，而是一个按"数据集"组织的体系：每个 .out_#### 对应一次数据打印（数据集编号从 equilibrium 的 _0001 递增，可在 .sol.msg 查对应偏置值）；数据分两类——scan_data（偏置相关：电流/电压/功率，逐偏置点累积）与 xy_data（结构/光谱：载流子密度、模场、增益谱，按 print_step 打印）。.plt 文件用 get_data 指定 main_input/sol_inf 与 xy_data/scan_data 的数据集范围，再用 plot_scan（偏置相关）、plot_1d/plot_2d/plot_3d（结构）、gain_spectrum（光谱）、lplot/splot（激光器纵向）等语句出图；绘图由 GNUPLOT 或 CrosslightView 完成。常见坑：某些变量缺省不输出，需在 .sol 加 more_output 重跑才能画；多电极器件画图常需 scale_horizontal=-1。

## A1 — 书中的应用 (Past Application)

### 案例 1: test1 后处理
- **问题**: 1D FP 激光跑完要画 L-I 与波强度。
- **方法论的使用**: setuplastip -plt 生成 .plt，get_data xy_data=[3 3] scan_data=[1 3]，plot_scan variable=laser_power + plot_1d variable=wave_intensity。
- **结论**: 取对数据集与变量即可出图。
- **结果**: 输出 L-I 曲线与波强度剖面（第3章 §3.10）。

### 案例 2: 三节 DBR 调谐绘图
- **问题**: 顶部电极电流方向与惯例相反。
- **方法论的使用**: plot_scan 加 scale_horizontal=-1。
- **结论**: 符号约定影响绘图方向。
- **结果**: 调谐曲线方向正确（第22章 §22.4）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 仿真跑完不知道画什么、怎么画。
2. 画图报"变量不存在"或结果空。
3. 需要跨偏置点提取光谱/模场/能带。
4. 用 CrosslightView 或 .plt 的完整流程。

### 语言信号 (用户的话里出现这些就应激活)

- "L-I / IV 曲线怎么画 / plot"
- "变量画不出来 / variable not available / more_output"
- "scan_data / xy_data / 数据集"
- ".plt / get_data / plot_scan / CrosslightView"

### 与相邻 skill 的区分

- 与 `gain-preview-workflow` 的区别: 预览在仿真前（.gain），后处理在仿真后（.plt）；不要混淆。
- 与 `pics3d-laser-workflow` 的区别: 后处理是流程终点，工作流 skill 负责从结构到收敛。

## E — 可执行步骤 (Execution)

| 步骤 | 输入 | 输出 | 判停/完成标志 |
|---|---|---|---|
| 1 确认数据存在 | .sol.msg + 附录 G 变量表 | 数据集编号 + 变量/数据类型清单 | 明确"画哪个数据集、哪个变量" |
| 2 编写 .plt | 数据集范围 + 目标图清单 | get_data/plot_scan/plot_1d 语句 | .plt 无语法错误、覆盖目标图 |
| 3 检查并迭代 | .plt 输出图 | 修正方向/单位/数据集后的图 | 物理合理、标签完整 |

1. **确认数据存在**
   - 查 .sol.msg 确认数据集编号与对应偏置；查附录 G 确认变量名与类型（scan_data 还是 xy_data）。
   - 完成标准: 明确"要画哪个数据集、哪个变量、哪类数据"。
   - 示例: 查 `gaas10.sol.msg` 看数据集编号；`equilibrium` 为 scanline 1（数据集 1,1），后续 scan 按 print_step 递增。

   🔴 CHECKPOINT · 🛑 STOP：把"数据集编号 + 变量 + 数据类型（scan_data/xy_data）"清单给用户确认后再写 .plt。

2. **编写 .plt**
   - get_data 指定 main_input/sol_inf、xy_data/scan_data 范围；plot_scan/plot_1d/gain_spectrum 选变量。
   - 判停条件: 变量缺省未输出 → .sol 加 more_output 重跑，回到步骤 1。
   - 完成标准: .plt 无语法错误，目标图全部覆盖。
   - 示例: `get_data main_input=gaas10.sol sol_inf=gaas10.out xy_data=(1 1) scan_data=(1 12)`；`plot_scan scan_var=voltage_1 variable=current_1 scan_num=2`；`plot_1d variable=band from=(0.5 1.3) to=(0.5 1.7)`（gaas10.plt 真实语句）。

   🔴 CHECKPOINT · 🛑 STOP：把 .plt 语句与数据集范围给用户确认后再运行；变量缺省时回到步骤 1 加 more_output 重跑。

3. **检查并迭代**
   - 运行 .plt（GNUPLOT/PDF/PS）或 CrosslightView；核对方向/单位/数据集。
   - 多电极器件注意 scale_horizontal=-1。
   - 完成标准: 输出图物理合理、标签完整。
   - 示例: 运行 `pics3d.exe gaas10.plt` 生成 `gaas10.ps`；对称结构电流/功率按需 x2、多电极用 `scale_horizontal=-1` 纠正方向。

   🔴 CHECKPOINT · 🛑 STOP：把输出图的方向/单位/数据集核对结论给用户确认后才算交付。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 仿真尚未完成（先跑通主仿真）。
- 需要改物理模型/参数（不是绘图问题）。

### 作者在书中警告的失败模式（触发 → 一线修复 → 兜底）

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 变量画不出来（不默认输出，§3.10） | .sol 加 `more_output` 后重跑仿真 | 仍缺：核对附录 G 变量名与数据类型 |
| bandgap 技巧下 IV 只取最后一段（§4.12） | 只画恢复带隙后的数据集 | 曲线仍错：核对数据集范围 |
| .out 文件手改（§3.2.1） | 从原始 .sol 重跑生成 | 数据异常：核对 sol_inf 路径与数据集 |
| 数据集/scanline 取错范围 | 查 .sol.msg 校正 xy_data/scan_data | 仍错：用 plot_scan scan_num 指定 scanline |
| 多电极电流方向相反 | plot_scan 加 scale_horizontal=-1 | 仍反：核对电极编号与电流符号 |

### 作者的盲点 / 时代局限

- GNUPLOT 依赖外部程序；CrosslightView 更省事但功能有限，新版本绘图行为可能有变。

### 容易混淆的邻近方法论

- scan_data 与 xy_data 不是"横轴纵轴"之分，而是数据类别；取错范围会画错点。

## 相关 skills

- composes-with: `pics3d-laser-workflow`（跑完用 .plt 出图）

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
