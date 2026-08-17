---
name: convergence-debugging
description: |
  用户的 Crosslight (APSYS/LASTIP/PICS3D) 仿真不收敛或数值异常（报错、发散、变量振荡）时，按手册第4章的系统方法排查修复：
  网格→偏置→基本变量→慢瞬态→辅助接触→带隙降低→宽禁带技巧。触发信号：不收敛/non-convergence、发散、
  报错看不懂、KCL 不守恒、GaN 极化结构难收敛、leakage current 算不出、Newton 迭代失败等。
  不适用于：仿真流程从头搭建（用 pics3d-laser-workflow）、纯网格优化（用 mesh-quality）、结果解读。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第4章 (P75-89)
tags: [convergence, debugging, newton, gan]
related_skills:
  - slug: mesh-quality
    relation: composes-with
  - slug: bias-strategy
    relation: composes-with
---

# 收敛故障诊断与对策工具箱

## R — 原文 (Reading)

> "There are several possible causes of convergence difficulties ... the simpler the structure,
> the easier it is to debug. If possible, start from a simplified 1D device that works and
> progressively iterate towards your final design until the convergence problem appears."
>
> — Crosslight Software Inc., 第4章 (P75-77)

## I — 方法论骨架 (Interpretation)

不收敛很少是求解器坏了，而是"方程组在某偏置点不可解或解不稳定"。手册给出一套按代价递增的排查顺序：先确认网格（过粗欠采样剧变区、过细破坏低阻区）；再检查偏置策略（高阻用电压、低阻/激射用电流、PICS3D 是否完成 RTG 初始化）；仍不行就换数值变量（准费米能级→载流子浓度）；再上"带物理技巧"——慢瞬态（加时间变量恢复位移电流）、辅助欧姆接触（钉住浮置高阻区再归零）、易解器件（轻掺杂版先冲到高偏置再升掺杂）、带隙降低（临时缩小带隙跑出目标电流再恢复）、宽禁带少数载流子垫高。纪律：任何技巧都会改变物理，用后必须验证结果（如带隙技巧只取最后一段 IV）。

## A1 — 书中的应用 (Past Application)

### 案例 1: p-n-i-p-n 反偏击穿 + 辅助接触
- **问题**: i 区远离电极、变量漂移，难以偏置到 10 V 击穿。
- **方法论的使用**: 在 i 区单网格点加辅助欧姆接触，电压拉到约 5 V 稳定求解；击穿后用电流控制把辅助接触电流归零。
- **结论**: 浮置高阻区被钉住，Newton 收敛。
- **结果**: 成功达到击穿偏置（第4章 §4.11）。

### 案例 2: GaAs 负微分迁移率
- **问题**: 高偏置下 n.gaas 迁移率模型产生负微分电阻，稳态求解发散。
- **方法论的使用**: 换用 beta 迁移率模型（或改瞬态仿真）。
- **结论**: 绕过负阻峰即可稳态收敛。
- **结果**: 手册推荐 beta 模型（第4章 §4.13）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 仿真在某个偏置点反复发散，报错信息看不懂。
2. GaN/SiC 等宽禁带器件低偏置/泄漏电流算不出来。
3. 电流偏置时各电极电流不守恒（KCL 违反）。
4. 教程能跑、改了自己的结构就不收敛。

### 语言信号 (用户的话里出现这些就应激活)

- "不收敛 / 发散 / non-convergence"
- "Newton 迭代失败 / 报错 / error"
- "GaN 仿真难收敛 / leakage current"
- "KCL / current conservation"、"failed to converge"

### 与相邻 skill 的区分

- 与 `mesh-quality` 的区别: 网格 skill 只解决"网格该长什么样"；本 skill 先排除网格再处理偏置/数值/技巧。
- 与 `bias-strategy` 的区别: 偏置 skill 讲正常设计时怎么选偏置；本 skill 在已经发散后做诊断。

## E — 可执行步骤 (Execution)

1. **分级定位问题**
   - 检查报错信息、失败偏置点、方程/变量误差表（eqns/potential/elec/hole/other）。
   - 用简化结构（降维/去流阻层）复现问题，锁定触发改动。
   - 完成标准: 找到"哪一步改动让仿真从收敛变发散"。

2. **按排查树修复**
   - 第一级: 网格（加密剧变区/低阻区减密）。
   - 第二级: 偏置（电压/电流切换、PICS3D 的 auto_finish=rtgain 前置）。
   - 第三级: 变量与技巧（change_variable、slow transient、辅助接触、bandgap_reduction 等）。
   - 判停条件: 若问题出在 PICS3D 阈值附近，直接转 `pics3d-laser-workflow` 的三步偏置检查。
   - 完成标准: 目标偏置点收敛且误差表单调下降。

3. **验证技巧没有污染物理**
   - 对比技巧前后结果（如 bandgap_reduction 只取最后一段 IV；辅助接触电流已归零）。
   - 完成标准: 关键输出（IV/L-I/能带）在技巧引入前后一致或差异可解释。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 仿真还没开始搭（先走标准工作流）。
- 收敛但结果明显物理错误（这是模型/参数问题，不是数值问题）。
- 纯后处理/绘图问题。

### 作者在书中警告的失败模式

- 低阻区网格过细 → ΔV≈0 电流失稳（§4.6）。
- 总电流极小时用电流偏置 → KCL 违反（§4.1）。
- bandgap reduction 改写的 IV 段不可用（§4.12）。
- 绝缘宏下隧穿/碰撞电离失效（§4.10.3）。

### 作者的盲点 / 时代局限

- 手册的收敛技巧面向 2020 年前后求解器；新版（如 Arnoldi/direct_eigen 替代）行为可能变化。
- "能收敛≈正确"是手册的隐含假设；物理模型选择错误时收敛得再好也是错的。

### 容易混淆的邻近方法论

- 慢瞬态与真实瞬态仿真不同：慢瞬态是收敛技巧，时间只作数值辅助。

## 相关 skills

- composes-with: `mesh-quality`（网格修复）、`bias-strategy`（偏置修复）
- 使用时配合 `pics3d-laser-workflow` 排查 PICS3D 特有的 RTG 初始化问题

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
