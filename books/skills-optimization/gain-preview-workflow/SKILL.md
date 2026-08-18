---
name: gain-preview-workflow
description: |
  用户在用 Crosslight 做激光器/有源器件仿真前，想先预览材料增益谱、自发辐射谱、折射率变化、电流-载流子
  关系或 QW 子带（k.p），或需要生成/检查 .gain 文件、为 RTG 预览准备表格化增益时。触发信号：.gain、
  gain spectrum、增益谱、自发辐射、spontaneous emission、增益预览、gain_wavel、RTG 预览准备、
  材料增益 vs 载流子密度等。不适用于：完整器件仿真（用 pics3d-laser-workflow）、后处理绘图。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第3章 (P63-64) / 第22章 (P445-446)
tags: [gain, spectrum, preview, qw, gain-file]
related_skills:
  - slug: material-macros
    relation: depends-on
  - slug: pics3d-laser-workflow
    relation: composes-with
---

# 增益与光谱预览（.gain 工作流）

## R — 原文 (Reading)

> "An important auxiliary input file that can be used to preview the optical gain spectrum,
> spontaneous emission rate spectrum, quantum well subbands, and other critical physical
> properties. This may be used by the user to do some preliminary estimates before the full
> simulation is performed."
>
> — Crosslight Software Inc., 第3章 §3.2.1 (P43)

## I — 方法论骨架 (Interpretation)

完整器件仿真的物理量大、耗时长，而很多错误（材料宏选错、组分设置错、增益峰与目标波长对不上）在跑全仿真前就能暴露。.gain 文件是专门为此设计的轻量输入：它 include .mater 得到材料参数，用 gain_wavel / sp.rate_wavel / index_wavel / current_conc / alpha_wavel / gain_density 等语句直接算出增益谱、自发辐射谱、折射率变化谱、电流-载流子密度、α 因子与 QW 子带。在 PICS3D 里它还有第二重职责：RTG 预览（rtgain_phase）用 .gain 生成的表格化增益与折射率变化来估计传播常数，因此"先跑 .gain、再跑主仿真"是官方推荐的顺序，还能在跑 RTG 预览前优化增益峰与光栅参考波长的对齐。

## A1 — 书中的应用 (Past Application)

### 案例 1: test1 增益预览
- **问题**: 1D FP 激光跑全仿真前想先看材料特性。
- **方法论的使用**: setuplastip -gain 生成 .gain（0.82 μm、载流子范围 1e23-5e24），包含 gain_wavel/sp.rate_wavel/index_wavel/current_conc/alpha_wavel/gain_density。
- **结论**: 一次跑出增益、自发谱、折射率变化等曲线。
- **结果**: 成为后续 .sol 仿真前的标准预览（第3章 §3.6）。

### 案例 2: inp13 RTG 预览准备
- **问题**: DFB 的 RTG 预览需要表格化增益。
- **方法论的使用**: .sol include inp13.gain 而非 .mater；先处理 .gain 优化增益峰 vs 光栅参考波长。
- **结论**: 预览用表格化数据即可完成模式搜索。
- **结果**: 模式搜索在 RTG≈0.87 找到主模（第22章 §22.2）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 新结构/新材料组分，想快速看增益峰波长是否覆盖目标。
2. PICS3D 的 RTG 预览报错或模式不对，怀疑 .gain 表格数据问题。
3. 需要决定载流子密度（透明/阈值附近）用于 rtgain_phase 的 density 参数。
4. 材料宏改过后想验证增益曲线变化。

### 语言信号 (用户的话里出现这些就应激活)

- ".gain / gain file / 增益文件"
- "先看增益谱 / preview gain spectrum"
- "spontaneous emission / 自发辐射谱"
- "RTG 预览 / gain_wavel / gain_density"

### 与相邻 skill 的区分

- 与 `pics3d-laser-workflow` 的区别: 预览是流程前置步骤；工作流 skill 管整体编排。
- 与 `material-macros` 的区别: 本 skill 用宏参数做光学计算预览；宏 skill 管参数本身怎么定义与覆盖。

## E — 可执行步骤 (Execution)

| 步骤 | 输入 | 输出 | 判停/完成标志 |
|---|---|---|---|
| 1 生成 .gain 骨架 | 材料宏/组分/温度/波长/载流子范围 | .gain 文件（begin_gain…end_gain） | 语法无误、材料加载成功、用户确认范围 |
| 2 选择并运行预览语句 | .gain + include 的 .mater | 增益/自发谱/折射率/电流-载流子曲线 | 增益峰与目标波长一致、透明密度合理 |
| 3 供主仿真/RTG 使用 | 预览结论 + .sol | .sol include .gain / rtgain_phase density | RTG 模式位置合理 |

1. **生成 .gain 骨架**
   - 右键 .mater 生成模板，或用 setuplastip/setuppics3d -gain 交互生成。
   - 包含 temperature、include .mater、波长范围、载流子浓度范围。
   - 完成标准: .gain 语法无误、材料加载成功。
   - 示例: `temperature temp=0.3E+03` + `include file=gaas10.mater`（真实 gaas10.gain 骨架）；`setuplastip -gain` 可交互生成。

   🔴 CHECKPOINT · 🛑 STOP：把生成的 .gain 骨架与关键范围（wavel_range/conc_range/temperature）给用户确认后再运行预览；不要跳过确认直接跑。

2. **选择并运行预览语句**
   - gain_wavel（增益谱）、sp.rate_wavel（自发谱）、index_wavel（折射率变化）、current_conc（I-载流子）、gain_density（增益-密度）。
   - 多活性区用 gain_module 指定区域。
   - 判停条件: 若增益峰远离目标波长，先修材料/组分再重跑，不要带病进主仿真。
   - 完成标准: 关键曲线（增益峰/透明密度/自发谱）与预期一致。
   - 示例: `gain_wavel wavel_range=(0.7 0.9) conc_range=(5.e23 5.e24) curve_number=5`；`sp.rate_wavel wavel_range=... conc_range=... curve_number=20`；`current_conc conc_range=... data_point=30 use_macro=yes fit_outfile=tmp.data`（inp13.gain）。

   🔴 CHECKPOINT · 🛑 STOP：把预览结论（增益峰波长/透明载流子密度）告诉用户确认；增益峰偏离目标波长时，先修材料/组分重跑，得到确认后才允许进入主仿真/RTG。

3. **供主仿真/RTG 使用**
   - 主仿真 include .gain（而非 .mater）；RTG 预览的 density 取 .gain 算出的合理载流子密度。
   - 完成标准: RTG 预览正常，模式位置合理。
   - 示例: .sol 中 `include file=inp13.gain`（替代 include .mater）；`rtgain_phase density=1.25e24`（density 来自 current_conc 曲线）。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 纯后处理已有结果（用 post-processing）。
- 非有源器件（无增益概念的器件）。

### 作者在书中警告的失败模式（触发 → 一线修复 → 兜底）

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 增益峰远离目标波长 | 核对 QW 材料/组分/厚度/温度后重跑 .gain | 仍不对：检查 exch_coef（能带收缩）/ tau_scat（增益展宽） |
| 增益峰与光栅参考波长不对齐，RTG 模式偏 | 调整 .gain 的 wavel_range 或材料组分重跑预览 | 仍偏：核对光栅参考波长（ref_wavel）设置 |
| 把预览数值当最终结果（预览 index 与主仿真有差异，§16.7） | 预览只用于趋势判断，最终结果以主仿真逐偏置计算为准 | 需要精确 index 时在主仿真中输出核对 |
| 材料宏选错/单位错误导致增益异常 | 按 material-macros 核对宏名/组分/单位 | 重跑 .gain 验证曲线，仍异常检查宏文件 |
| 把 .gain 当后处理绘图（与 .plt 混淆） | 明确阶段：.gain 是仿真前预览、.plt 是仿真后绘图 | 需要绘图走 post-processing |

### 作者的盲点 / 时代局限

- 预览基于固定温度（isothermal），自热/温度分布场景的增益需在主仿真中重算。

### 容易混淆的邻近方法论

- .gain 与 .plt 不同：.gain 是物理量预览（仿真前），.plt 是结果绘图（仿真后）。

## 相关 skills

- depends-on: `material-macros`（.gain include .mater）
- composes-with: `pics3d-laser-workflow`（RTG 预览依赖 .gain 表格）

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
