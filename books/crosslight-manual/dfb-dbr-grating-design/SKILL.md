---
name: dfb-dbr-grating-design
description: |
  用户在 Crosslight PICS3D 中设计或调试 DFB/DBR 激光器时，处理纵向模式、光栅耦合系数 κ、相移、啁啾、
  增益/损耗耦合、布拉格波长与 RTG 谱分析。触发信号：DFB/DBR、光栅、kappa、相移、quarter-wave shift、
  单模/边模抑制、Bragg wavelength、grating_compos、RTG 谱、mode_srch 等。
  不适用于：FP 无光栅激光器（用 pics3d-laser-workflow）、VCSEL 的 DBR 腔（用 vcsel-modeling）。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第16章 (P315-352) / 第22章 (P437-448, P457-469)
tags: [dfb, dbr, grating, longitudinal-mode, kappa]
related_skills:
  - slug: pics3d-laser-workflow
    relation: depends-on
  - slug: vcsel-modeling
    relation: contrasts-with
---

# DFB/DBR 纵向模式与光栅设计

## R — 原文 (Reading)

> "In DFB and DBR lasers, corrugations are made along the waveguides which introduce coupling
> between the forward and backward waves ... the purpose of this is to perturb the propagation
> constant k(z) to achieve desirable scattering effects of the propagating waves."
>
> — Crosslight Software Inc., 第16章 §16.5 (P319)

## I — 方法论骨架 (Interpretation)

DFB/DBR 的物理核心是光栅把前向波耦合到后向波，耦合强度由复值 κ 描述：实部来自折射率起伏（折射率耦合），虚部来自增益/损耗起伏（增益耦合）。纵向模式是复频率平面上往返增益方程（Wronskian 零点）的解，模式位置由光栅布拉格波长与增益谱的相对关系决定。设计自由度：κL 强度（决定反射率与模式选择）、相移（1/4 波相移把主模放到增益峰中心，保证单模）、啁啾（周期渐变移动模式）、增益耦合（等效于相移/啁啾，把主模推入光谱带隙）。PICS3D 提供两种实现：简化法（section 里直接给 kappa_real/imag 与 phase_shift）和显式法（grating_compos/grating_model 定义高低折射率材料，软件从模式重叠自动算 κ，含二阶光栅辐射损耗）。

## A1 — 书中的应用 (Past Application)

### 案例 1: inp13 相移 DFB
- **问题**: 需要单纵模 1.3 μm DFB。
- **方法论的使用**: 两个 250 μm section，κ=2000（κL=1），第一段末尾 phase_shift=0.5（π 的倍数）。
- **结论**: 相移把主模置于增益峰，边模被抑制。
- **结果**: RTG 谱显示主模 RTG≈0.87 的清晰单峰（第22章 §22.2）。

### 案例 2: 三节 DBR 显式光栅
- **问题**: 需要 DBR 反射镜与调谐段，κ 要求精确。
- **方法论的使用**: grating_compos 定义 InGaAs(0.5)P/InP 高低温区与厚度，软件自动算 κ≈36386 1/m（κL≈109 高反射）。
- **结论**: 显式法能给出折射率耦合与增益耦合分离（虚部 κ≈0，符合"mildly active"假设）。
- **结果**: 成功实现可调谐 DBR 激光（第22章 §22.4）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 设计新的 DFB/DBR 激光器（波长、κL、相移位置）。
2. 现有设计双模/跳模，需要边模抑制分析。
3. 需要把光栅从"简化 κ"升级为"显式材料光栅"。
4. RTG 谱异常（主模不在增益峰、模式缺失）。

### 语言信号 (用户的话里出现这些就应激活)

- "DFB / DBR / 光栅设计 / grating"
- "kappa / 耦合系数 / 相移 / phase shift"
- "边模抑制 / single mode / mode hopping"
- "Bragg wavelength / grating_compos / RTG 谱"

### 与相邻 skill 的区分

- 与 `pics3d-laser-workflow` 的区别: 本 skill 专攻光栅/纵向模式设计；整体流程与偏置设置由工作流 skill 负责。
- 与 `vcsel-modeling` 的区别: VCSEL 的 DBR 是垂直腔、薄膜传输矩阵，不是边缘发射的耦合波理论；两者建模路径不同。

## E — 可执行步骤 (Execution)

1. **确定设计参数**
   - 由目标波长与有效折射率定光栅周期（λ_Br=2·n_eff·L_g）；用简化法先给 κL 初值（如 1-2）。
   - 完成标准: 参考波长/周期/κ 初值明确，决定是否加相移。

2. **选择建模路径并验证 RTG**
   - 简化法: section 给 kappa_real/imag、mesh_points、phase_shift；显式法: 层文件 grating_compos 定义材料与厚度。
   - 跑 rtgain_phase 预览，检查主模位置与 RTG 谱（plot_rtgain）。
   - 判停条件: 若主模不在增益峰附近，调整 κL/相移/参考波长后重预览，不要直接进主仿真。
   - 完成标准: 模式搜索日志显示预期单模，RTG<1。

3. **进入主仿真并核对**
   - 用 auto_finish=rtgain 初始化 → solve_rtg=yes 扫描；核对波长-电流与功率。
   - 完成标准: 单模稳定，边模抑制与设计目标一致。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 无光栅 FP 激光器（κ=0 极限，用工作流 skill）。
- VCSEL 的 DBR 设计（垂直腔，见 vcsel-modeling）。
- 二阶光栅辐射损耗的严格推导（手册附录，只作原理参考）。

### 作者在书中警告的失败模式

- 在 PICS3D 用 init_wave 设腔长/反射率被静默忽略（§22.2）。
- 简化法 κ 与显式法结果可能差异大；显式法需正确高低材料组分。
- 增益耦合、啁啾与相移都会移动主模，三者的效果容易混淆。

### 作者的盲点 / 时代局限

- 手册理论推导基于经典耦合波文献（McCall/Platzman 等），未覆盖最新光栅设计（如高阶/非对称光栅的完整处理）。
- "mildly active"光栅的近似假设（增益耦合≈0）在强增益耦合器件中不成立。

### 容易混淆的邻近方法论

- κ 实部（折射率耦合）与虚部（增益/损耗耦合）不能混为一谈；显式法日志会分别打印 Real/Imag kappa。

## 相关 skills

- depends-on: `pics3d-laser-workflow`（RTG 预览与三步偏置是设计验证的前提）
- contrasts-with: `vcsel-modeling`（边缘发射耦合波 vs 垂直腔薄膜传输矩阵）

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
