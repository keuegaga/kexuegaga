---
name: mesh-quality
description: |
  用户在 Crosslight 仿真中需要生成/检查/优化有限元网格（.layer 网格参数、put_mesh、regrid、.mplt 目检），
  或怀疑网格过粗/过细导致结果异常时。触发信号：网格、mesh、加密、regrid、put_mesh、网格不收敛、
  mesh density、电流拥挤区网格、界面加密等。不适用于：已发散的全面调试（用 convergence-debugging）、
  结构定义本身（.layer 层序/接触）。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第3章 (P54-58) / 第4章 (P79-82)
tags: [mesh, fem, convergence, regrid]
related_skills:
  - slug: convergence-debugging
    relation: composes-with
---

# 网格生成与质量检查

## R — 原文 (Reading)

> "An unsatisfactory mesh is a major cause of non-convergence. The first step to troubleshooting
> a mesh is to plot it as above and check that the mesh distribution is OK."
>
> — Crosslight Software Inc., 第3章 §3.4.3 (P58)

## I — 方法论骨架 (Interpretation)

有限元网格是仿真的"分辨率"：物理在网格点之间变化，网格必须能采样这些变化。核心原则不是"越密越好"，而是"该密的地方密、该稀的地方稀"。必须加密的区域：尖锐材料界面（异质结/肖特基/掺杂突变）、隧穿结、电流拥挤区、量子阱波函数采样区、光模式峰值区；必须避免过密的区域：低阻区（金属/重掺杂接触），那里 ΔV≈0 会让电流控制数值失稳。控制手段：.layer 的 n/mesh_num（数量）与 r/shift_center（分布），.geo 的 put_mesh（每条边点数与 ratio）、double_mesh/half_mesh（局部加倍/减半），以及 regrid（按相邻网格点材料参数变化自动加密生成新网格）。没有系统误差分析能告诉你网格够不够密——用绘图+加密对比（网格收敛性）来判断。

## A1 — 书中的应用 (Past Application)

### 案例 1: 网格故障排查流程
- **问题**: 仿真不收敛，怀疑网格。
- **方法论的使用**: 先 .mplt 画网格目检 → 找剧变区是否欠采样 → 局部加密 → 仍不行用 regrid。
- **结论**: 网格分布比总量更重要。
- **结果**: 手册推荐的标准排查顺序（§3.4.3）。

### 案例 2: 低阻区过密
- **问题**: 低阻层过密网格导致电流失稳。
- **方法论的使用**: 调整低阻区网格分布（减密）。
- **结论**: ΔV→0 时欧姆定律数值不稳定。
- **结果**: 手册确认调整分布即可修复（§4.6）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 新结构跑前想确认网格合理。
2. 电流拥挤/界面附近结果可疑或振荡。
3. 需要 regrid 自动加密或局部 double_mesh。
4. 3D 仿真内存/时间爆炸，想智能分配网格。

### 语言信号 (用户的话里出现这些就应激活)

- "网格怎么加密 / mesh refinement"
- "界面/结附近结果不对"
- "regrid / put_mesh / .mplt"
- "网格太密太稀 / mesh too coarse / too fine"

### 与相邻 skill 的区分

- 与 `convergence-debugging` 的区别: 网格是收敛排查的第一级；本 skill 专精网格，调试 skill 编排整体排查。

## E — 可执行步骤 (Execution)

1. **目检网格**
   - 生成 .mplt 并绘图，检查剧变区（界面/接触/隧穿/电流拥挤/QW/光模峰）采样。
   - 完成标准: 明确指出哪些区域可能欠采样/过密。

2. **调整数量与分布**
   - 用 n/mesh_num、r/shift_center 或 put_mesh 控制分布；局部用 double_mesh/half_mesh。
   - 判停条件: 若无法手工定位剧变区，用 regrid 按材料参数变化自动加密。
   - 完成标准: 剧变区有足够点、低阻区不密集。

3. **网格收敛性验证**
   - 加密后重跑关键量（能带/载流子/增益/模场），若结果大幅变化说明网格未收敛，继续加密。
   - 完成标准: 关键量随网格加密变化 < 可接受阈值。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 结构定义错误（层序/材料/接触）被误认为网格问题。
- 已确认是偏置/模型问题。

### 作者在书中警告的失败模式

- 过粗网格在剧变区欠采样（§4.5）。
- 过细网格在低阻区电流失稳（§4.6）。
- 全器件均匀加密浪费时间内存且不解决局部问题（§3.4.3）。

### 作者的盲点 / 时代局限

- 手册承认"没有系统误差分析能判定网格够不够密"，只能靠经验与收敛对比。

### 容易混淆的邻近方法论

- double_mesh 是局部加倍，不等于全局加密；regrid 是自动加密但不是万能的。

## 相关 skills

- composes-with: `convergence-debugging`（网格修复是收敛调试第一级）

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
