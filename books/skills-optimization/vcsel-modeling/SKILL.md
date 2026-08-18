---
name: vcsel-modeling
description: |
  用户在 Crosslight PICS3D 中仿真 VCSEL（垂直腔面发射激光器）时，处理 vcsel_section/DBR 周期定义、
  spacer 厚度迭代设计、驻波增益增强、圆柱坐标与 fiber-like EIM 模式求解、低阈值 RTG 初始化。
  触发信号：VCSEL、垂直腔、DBR 周期、spacer、standing wave、驻波、gfactor_stdwave、vcsel_type、
  cylindrical 等。不适用于：边缘发射 DFB/DBR（用 dfb-dbr-grating-design）、非激光垂直腔器件。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第17章 (P353-360) / 第22章 (P470-481)
tags: [vcsel, dbr, standing-wave, cylindrical]
related_skills:
  - slug: pics3d-laser-workflow
    relation: depends-on
  - slug: qw-model-selection
    relation: composes-with
  - slug: dfb-dbr-grating-design
    relation: contrasts-with
---

# VCSEL 建模要点（section/驻波/圆柱坐标）

## R — 原文 (Reading)

> "Since the light propagation takes place in the vertical direction, the .layer file of a VCSEL
> must also define the optical cavity. ... groups of layers are assigned to the same section by
> assigning them a vcsel_type label in the layer statement."
>
> — Crosslight Software Inc., 第22章 §22.5 (P471-472)

## I — 方法论骨架 (Interpretation)

VCSEL 的光传播垂直于有源区，腔长极短，建模与边发射激光器有三处根本不同：第一，光学腔由层文件里的 vcsel_type 标签定义（每个标签对应 vcsel_section 指定的传播模型），DBR 用平均材料做电学网格、显式周期层（vertical_dbr_layer_mater）做光学传播，省网格但光学期必须真实；第二，腔长由 spacer 厚度决定，λ/n 只是初值——DBR 穿透深度与有源区厚度贡献相位，必须用 RTG 预览迭代调 spacer 使纵模对准增益峰，并看驻波增益增强因子（gfactor_stdwave）；第三，旋转对称器件用圆柱坐标（cylindrical axis=y），模式求解用 fiber-like EIM（vcsel_model），此时 init_wave 只给初始波长/背景损耗。偏置上 VCSEL 阈值电流极低，RTG 初始化可以在电压扫描段直接以 auto_finish=rtgain 完成，再小步长开启 solve_rtg。

## A1 — 书中的应用 (Past Application)

### 案例 1: jim_vcsel 教程
- **问题**: 0.835 μm GaAs 系 MQW VCSEL 全流程。
- **方法论的使用**: 五个 vcsel_section（n-DBR/n-spacer/mqw_active/p-spacer/p-DBR），DBR 平均材料+29/20 周期显式层；cylindrical axis=y + fiber-like EIM；RTG 预览得到 gfactor_stdwave≈1.71；spacer 按 λ/n 初值迭代。
- **结论**: 驻波增强显著，顶部（少 DBR 层）输出最大。
- **结果**: 成功输出顶部 L-I 曲线与驻波-QW 重叠图（第22章 §22.5）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 新建 VCSEL 仿真（GaN/GaAs 系）不确定 vcsel_section 怎么设。
2. RTG 预览纵模离增益峰远，需要调 spacer/DBR。
3. 想评估驻波增益增强或顶部/底部功率分配。
4. 圆柱坐标与 fiber-like EIM 模式求解设置。

### 语言信号 (用户的话里出现这些就应激活)

- "VCSEL 怎么仿真 / vertical cavity"
- "spacer 厚度 / DBR 周期 / standing wave"
- "驻波增强 / gfactor / 顶部底部功率"
- "vcsel_section / vcsel_type / cylindrical"

### 与相邻 skill 的区分

- 与 `dfb-dbr-grating-design` 的区别: VCSEL 用垂直薄膜传输矩阵，DBR 是纵向腔的一部分；边发射 DFB/DBR 用耦合波理论，光栅在传播方向。
- 与 `pics3d-laser-workflow` 的区别: 本 skill 是 VCSEL 专属建模路径；通用三步偏置流程由工作流 skill 提供。

## E — 可执行步骤 (Execution)

| 步骤 | 输入 | 输出 | 判停/完成标志 |
|---|---|---|---|
| 1 定义光学腔 | 层结构 + DBR 周期/材料 | vcsel_type 标签 + .vcsel 文件 | section 起止与层位置一致、无标签交错 |
| 2 RTG 预览调腔 | λ/n 初值 + spacer 厚度 | rtgain 谱 + gfactor_stdwave | 主模在增益窗口、驻波增强合理 |
| 3 偏置与后处理 | RTG 结论 + .sol | auto_finish=rtgain → solve_rtg + 功率曲线 | L-I 阈值/功率合理、顶部输出符合设计 |

1. **定义光学腔**
   - 层文件给每层/层组贴 vcsel_type 标签（n-DBR/spacer/MQW/p-DBR），DBR 用平均材料+vertical_dbr_layer_mater 周期；MQW 区用单一标签。
   - 处理 .layer 生成 .vcsel 文件并 include 进 .sol。
   - 完成标准: .vcsel 的 section 起止与层位置一致，标签无交错。
   - 示例: 层文件给每层贴 `vcsel_type` 标签（n-DBR/spacer/MQW/p-DBR）；.sol `include file=xxx.vcsel`；DBR 用平均材料 + `vertical_dbr_layer_mater` 周期。

   🔴 CHECKPOINT · 🛑 STOP：把 vcsel_type 标签布局（section 起止/无交错）给用户确认后再进 RTG 预览。

2. **RTG 预览调腔**
   - cylindrical axis=y + vcsel_model（fiber-like EIM）→ equilibrium → rtgain_phase。
   - 检查纵模位置与 gfactor_stdwave；按 λ/n 初值迭代 spacer 厚度。
   - 判停条件: 纵模未对准增益峰时先调 spacer/DBR 再进偏置，不要直接跑 solve_rtg。
   - 完成标准: 主模在增益窗口内，驻波增强因子合理。
   - 示例: `cylindrical axis=y` + `vcsel_model`（fiber-like EIM）→ `equilibrium` → `rtgain_phase density=...`；检查 gfactor_stdwave 并按 λ/n 迭代 spacer 厚度。

   🔴 CHECKPOINT · 🛑 STOP：把 RTG 纵模位置与 gfactor_stdwave 结论给用户确认后再进偏置。

3. **偏置与后处理**
   - 电压扫描 auto_finish=rtgain（低阈值可合并初始化）→ solve_rtg=yes 小步长。
   - 用 .plt 画顶部/底部功率、L-I 与驻波图。
   - 完成标准: L-I 曲线阈值/功率合理，顶部输出方向符合设计。
   - 示例: 电压扫描 `auto_finish=rtgain`（低阈值可合并初始化，`auto2_finish` 加电流下限）→ `solve_rtg=yes` 小步长；.plt 画顶部/底部功率与驻波图。

   🔴 CHECKPOINT · 🛑 STOP：把 L-I/功率/驻波核对结论给用户确认后才算交付。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 边缘发射 DFB/DBR 激光器。
- 非激光垂直腔器件（RCLED 等另有模型）。

### 作者在书中警告的失败模式（触发 → 一线修复 → 兜底）

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| vcsel_type 标签交错（b/w/b）导致腔长错（§22.5） | 重排标签使 section 起止连续、无交错 | 仍错：核对 .vcsel 生成文件的 section 边界 |
| 复制粘贴层复制标签产生交错（§22.5） | 检查 MQW 区内标签并修正 | 仍交错：从官方示例重建层结构 |
| spacer 只按 λ/n 不迭代（相位误差，§22.5） | 用 RTG 预览迭代 spacer 厚度使纵模对准增益峰 | 仍偏：核对 DBR 穿透深度与有源区相位贡献 |
| 纵模离增益峰远 | 先调 spacer/DBR 再进偏置 | 仍偏：检查增益谱与参考波长 |
| 低阈值越阈/漏模 | 电压段合并 RTG 初始化 + auto2_finish 电流下限 | 仍异常：缩小步长并核对 auto_until |

### 作者的盲点 / 时代局限

- 手册的 VCSEL 示例基于 GaAs 系；GaN VCSEL 的极化 MQW 还需叠加 gan-wurtzite-mqw 的 self_consistent 与基晶格设置。

### 容易混淆的邻近方法论

- init_wave 在 VCSEL 里只定初始波长/背景损耗，腔参数由 .vcsel section 定义（与 LASTIP 习惯不同）。

## 相关 skills

- depends-on: `pics3d-laser-workflow`（三步偏置与 RTG 初始化）
- composes-with: `qw-model-selection`（MQW 有源区模型）
- contrasts-with: `dfb-dbr-grating-design`

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
