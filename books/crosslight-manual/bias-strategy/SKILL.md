---
name: bias-strategy
description: |
  用户在 Crosslight 仿真中需要决定用电压还是电流偏置、多电极/多段器件如何控制各电极、以及 PICS3D 的
  auto_finish/auto2_finish 条件设置时。触发信号：电压偏置还是电流偏置、bias、electrode、多电极、
  current_1/voltage_1、KCL、auto_finish、共享电极、p 侧电流为负等。不适用于：已经发散后的调试
  （用 convergence-debugging）、非偏置的物理模型选择。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第4章 (P76-79) / 第22章 (P464-468)
tags: [bias, electrode, convergence, multi-electrode]
related_skills:
  - slug: pics3d-laser-workflow
    relation: composes-with
  - slug: convergence-debugging
    relation: composes-with
---

# 电压/电流偏置策略与多电极控制

## R — 原文 (Reading)

> "Use voltage bias for devices with high resistance. Use current bias for devices with low
> resistance. ... under lasing conditions, the only way to perform the simulation properly is
> to use current controlled bias."
>
> — Crosslight Software Inc., 第4章 §4.1 (P77-78)

## I — 方法论骨架 (Interpretation)

Newton 求解器要求"偏置的小变化→解的小变化"。电压偏置适合高阻状态（反向、低偏、OLED/宽禁带、大接触电阻、太阳能电池），因为电压-电流关系平缓；电流偏置适合低阻状态（正向导通、激光器激射后），因为此时电压-电流关系近乎指数，电压微扰会引发电流巨变，而激光器激射后载流子与准费米能级被受激复合钳死，电压偏置几乎必然失败。标准正偏策略：equilibrium → 电压扫到内建电压 80-90% → 检查 KCL → 电流偏置到目标。PICS3D 进一步要求电流扫描以 auto_finish=rtgain 终止来完成模式初始化。多电极器件：共享底部电极统一编号，先加小电压抬参考地，再对顶部电极用多个 scan 变量同时电流偏置；省略某电极变量则保持其电压不变；p 侧电流按惯例为负。

## A1 — 书中的应用 (Past Application)

### 案例 1: 标准二极管正偏流程
- **问题**: 二极管正偏如何设置才保证收敛。
- **方法论的使用**: 电压扫到 80-90% 内建电压（或 auto_finish=current），验证 KCL，再切电流偏置。
- **结论**: 避开"高阻低偏+低阻高偏"两难区。
- **结果**: 手册推荐的标准策略（第4章 §4.1）。

### 案例 2: 三节 DBR 多电极
- **问题**: 增益段/调谐段/DBR 段三个顶部电极要独立控制。
- **方法论的使用**: 底电极共享编号，先加 -0.8 V 抬参考地，再对 current_2/3/4 多变量同时扫描（p 侧为负），最后以调谐电流扫 current_3。
- **结论**: 避免电流流向最短路径，逐段独立控制。
- **结果**: 调谐曲线与模跳现象成功复现（第22章 §22.4）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 新建仿真时纠结"这个器件用电压还是电流偏置"。
2. 激光器阈值附近电压扫描发散，需要切换到电流扫描策略。
3. 多电极/多段器件（DBR、双段 DFB）需要同时控制多个电极。
4. 需要设置 auto_finish / auto2_finish 终止条件。

### 语言信号 (用户的话里出现这些就应激活)

- "用电压还是电流偏置 / voltage or current bias"
- "多电极怎么加偏置 / multiple electrodes"
- "auto_finish / current_1 / voltage_1"
- "KCL 不守恒 / 电流为负 / shared electrode"

### 与相邻 skill 的区分

- 与 `pics3d-laser-workflow` 的区别: 本 skill 是偏置决策子技能；工作流 skill 把偏置作为三步流程的一环整体编排。
- 与 `convergence-debugging` 的区别: 本 skill 在仿真设计期选对偏置；调试 skill 在发散后诊断。

## E — 可执行步骤 (Execution)

1. **判断偏置类型**
   - 高阻器件（反向/OLED/宽禁带/大接触电阻/太阳能）→ 电压偏置；低阻/激射 → 电流偏置。
   - 完成标准: 明确写出所选偏置变量与理由。

2. **编排正偏序列**
   - equilibrium → 电压到内建电压 80-90% → KCL 校验 → 电流偏置。
   - PICS3D: 电流扫描加 auto_finish=rtgain（阈值下初始化），再 solve_rtg=yes。
   - 判停条件: 若 VCSEL 低阈值，把电压段与 RTG 初始化合并，用 auto2_finish 加电流下限。
   - 完成标准: 每个 scan 的终止条件明确、步长合理。

3. **多电极控制**
   - 共享电极先抬参考地；顶部电极多变量同时电流偏置；检查符号（p 侧为负）。
   - 完成标准: 各电极电流符合物理预期，绘图方向正确。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 纯热/光学边界设置（与偏置无关）。
- 器件已经发散且原因不明（先走收敛诊断）。

### 作者在书中警告的失败模式

- 总电流极小时用电流偏置 → 数值精度不足、KCL 违反（§4.1）。
- 电压远高于开启电压 → 指数型电流变化导致不收敛（§4.1）。
- 激射后用电压偏置 → 钳位导致无解（§4.1）。

### 作者的盲点 / 时代局限

- 手册的"高阻用电压"建议对超低漏电 GaN 反向偏置也未必够用，常需叠加 §4.14 的 minority carrier 技巧。

### 容易混淆的邻近方法论

- auto_finish=rtgain 是 PICS3D 专属；LASTIP/APSYS 没有 RTG，只有电流/电压条件。

## 相关 skills

- composes-with: `pics3d-laser-workflow`、`convergence-debugging`

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
