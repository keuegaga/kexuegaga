---
name: pics3d-laser-workflow
description: |
  用户在用 Crosslight PICS3D/LASTIP 仿真激光器（FP/DFB/DBR/SOA/VCSEL）时，需要搭建或修正完整仿真流程：
  从 .layer/.sol 输入文件、网格加载、增益预览、到 equilibrium→电压→auto_finish=rtgain→solve_rtg 的三步偏置。
  触发信号：提到 PICS3D/LASTIP/Crosslight/激光器仿真、L-I 曲线、阈值、纵向模式、不收敛但不知道流程怎么搭、
  "set up a PICS3D laser simulation" 等。不适用于：纯物理理论问答、APSYS 非激光器件、命令字典查询。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第3章 (P40-75) / 第4章 (P77-79) / 第22章 (P437-481)
tags: [pics3d, laser, workflow, rtg, bias]
related_skills:
  - slug: bias-strategy
    relation: depends-on
  - slug: gain-preview-workflow
    relation: depends-on
  - slug: post-processing
    relation: composes-with
---

# PICS3D 激光仿真标准工作流（三步偏置 + RTG 初始化）

## R — 原文 (Reading)

> "In PICS3D, the coupling of the photon density is more complicated than in LASTIP so it is not
> included by default. ... It is therefore required that the scan preceding the introduction of
> the photon coupling use the auto_finish=rtgain condition to terminate."
>
> — Crosslight Software Inc., 第4章 §4.2 (P78-79)

## I — 方法论骨架 (Interpretation)

激光器仿真的难点不是方程本身，而是光子密度与增益/折射率沿腔长互相依赖（纵向空间烧孔）：不知道光子密度就算不出增益分布，算不出增益分布就定不了模式与光子密度。PICS3D 绕开这个"鸡生蛋"问题的办法是分三步走：先在平衡态求出无光解；再用电压偏置把器件带到阈值附近（内建电压的 80-90%）；随后用电流偏置，并让扫描在往返增益（RTG）达到某个阈值下目标值时自动停止，从而在"光子密度≈0"的近似下完成纵向模式搜索和初始光子密度估计；最后才开启光子耦合（solve_rtg=yes）继续扫描到目标电流。关键纪律：RTG 初始化必须在开启耦合之前完成；开启耦合后必须用小步长跨阈值。

## A1 — 书中的应用 (Past Application)

### 案例 1: inp13 相移 DFB 教程
- **问题**: 1.3 μm 相移 DFB 激光要从头跑出 L-I 曲线与纵模谱。
- **方法论的使用**: equilibrium → 电压扫描（auto_finish=current）→ 电流扫描（auto_finish=rtgain auto_until=0.8）→ 第三个扫描 solve_rtg=yes 小步长推进。
- **结论**: 模式搜索在 RTG≈0.87 处找到主模，越过阈值后光子耦合开启。
- **结果**: 成功输出功率-电流、波长-电流曲线（第22章 §22.2）。

### 案例 2: jim_vcsel 教程
- **问题**: VCSEL 阈值电流极低，RTG 初始化窗口容易越阈。
- **方法论的使用**: 电压扫描直接以 auto_finish=rtgain（auto_until=0.95）终止，再以极小步长开启 solve_rtg。
- **结论**: 短腔模式少，低偏置初始化不会漏模。
- **结果**: 稳定输出顶部/底部功率曲线（第22章 §22.5）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 新建 PICS3D 激光器项目，不知道输入文件怎么组织、偏置怎么分段。
2. 已有仿真在阈值附近发散，怀疑是光子耦合初始化缺失或顺序错误。
3. 想从官方教程示例改造成自己的 GaN/InGaN 激光器结构。
4. 需要 L-I、阈值电流、纵模波长、输出功率等结果但仿真跑不通。

### 语言信号 (用户的话里出现这些就应激活)

- "PICS3D 激光器怎么仿真 / 怎么设置偏置"
- "仿真在阈值附近不收敛 / solve_rtg / auto_finish"
- "从示例开始改自己的激光器结构"
- "set up / run a PICS3D laser simulation"、"L-I curve"、"threshold"

### 与相邻 skill 的区分

- 与 `bias-strategy` 的区别: 本 skill 负责激光器仿真全流程骨架；偏置策略只负责"选电压还是电流、多电极怎么控制"这一环节。
- 与 `dfb-dbr-grating-design` 的区别: 本 skill 不深入光栅 κ/相移设计；那是光栅设计 skill 的职责。
- 与 `gain-preview-workflow` 的区别: 增益预览是流程的前置步骤，本 skill 调用它但不替代它。

## E — 可执行步骤 (Execution)

当 skill 被激活后，agent 应按以下步骤执行:

1. **建立项目基础（从示例出发）**
   - 在官方示例库找结构最接近的工程（FP→A_tutorial；DFB→inp13；DBR→3section_tunable；VCSEL→jim_vcsel）。
   - 完成 .layer → .geo → 网格 → .mater/.doping 的生成与检查。
   - 完成标准: 网格可生成、材料宏加载无错误、.gain 预览通过。

   🔴 CHECKPOINT · 🛑 STOP：把选定的示例工程与"网格/材料/.gain 预览"检查结论告诉用户确认后再写 .sol——选错基底工程会浪费整轮流程。

2. **编写 .sol 的三段式偏置**
   - 先 `equilibrium`；再电压扫描到 80-90% 内建电压（可 auto_finish=current）；再电流扫描 `auto_finish=rtgain`（RTG 目标建议 0.8-0.95）；最后 `solve_rtg=yes` 小步长扫描。
   - 完成标准: 每个 scan 之间有明确的终止条件与步长设置。
   - 判停条件: 若器件是 VCSEL（低阈值），把电压段与 RTG 初始化合并，用 auto2_finish 加电流下限。

   🔴 CHECKPOINT · 🛑 STOP：逐段向用户确认扫描顺序（equilibrium → 电压 80-90% → auto_finish=rtgain → solve_rtg）与各段终止条件/步长；VCSEL 低阈值走合并分支。

3. **验证并迭代**
   - 跑通后检查模式搜索日志（纵模波长/RTG 列表）、L-I 曲线与波强度分布。
   - 若发散: 回到第 2 步检查是否缺 auto_finish=rtgain，或把 solve_rtg 的 init_step 再调小 1-2 个数量级。
   - 完成标准: 目标偏置范围内收敛，L-I/波长曲线物理合理。

   🔴 CHECKPOINT · 🛑 STOP：把模式搜索日志（纵模波长/RTG 列表）与 L-I 曲线检查结论给用户确认后才算交付；曲线异常先回到第 2 步核对偏置顺序。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 非激光器件（LED/太阳能/HEMT）→ 用 APSYS 流程，没有 RTG/光子耦合概念。
- 纯理论问答（如"纵向模式的定义是什么"）→ 这是知识查询，不是仿真任务。
- 已有完整可运行工程只差参数微调 → 不需要重建流程。

### 作者在书中警告的失败模式（触发 → 一线修复 → 兜底）

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| RTG≥1（越阈假象，第22章 P445） | 把 auto_until 降到 0.8-0.95 重跑 RTG 扫描 | 仍越阈：减小电流步长并核对密度取值 |
| PICS3D 里 init_wave 设腔长/反射率被忽略（第22章 P444） | 改用 longitudinal/cavity 语句定义腔参数 | 仍不生效：对照版本手册确认语句支持 |
| RTG 终止值太高（光子密度不准）或太低（漏模）（第4章 P79） | 终止值取 0.8-0.95 且高于透明密度 | 模式仍不对：扩大 mode_srch 搜索范围 |
| 阈值附近发散 | 确认 auto_finish=rtgain 在开启耦合前已前置 | 把 solve_rtg 的 init_step 调小 1-2 个数量级 |
| VCSEL 低阈值漏模/越阈 | 电压段与 RTG 初始化合并，auto2_finish 加电流下限 | 仍异常：再缩小步长并核对 auto_until |
| 找不到结构最接近的示例 | 按器件类型选官方示例（FP/DFB/DBR/VCSEL） | 仍不合适：从 Workbook 最小案例逐步改造 |
| 材料宏加载错误 | 按 material-macros 核对宏名/组分/单位 | 重跑 .gain 预览验证材料加载 |

### 作者的盲点 / 时代局限

- 手册教程多数停留在 2009 年更新，示例输入文件可能与当前版本有差异；结果以本机版本为准。
- 假设读者已懂半导体激光物理；新手应先补载流子统计与速率方程基础。

### 容易混淆的邻近方法论

- "先电压后电流"看似与 `convergence-debugging` 的调试技巧重叠，但本 skill 是正常流程，调试技巧只在流程跑不通时介入。

## 相关 skills

- depends-on: `bias-strategy`（电压/电流选择与多电极控制）、`gain-preview-workflow`（RTG 预览依赖 .gain 表格化增益）
- composes-with: `post-processing`（跑完后用 .plt 取 L-I/谱/模场）

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
