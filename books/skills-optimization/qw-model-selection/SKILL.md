---
name: qw-model-selection
description: |
  用户在 Crosslight 中需要选择量子阱模型等级（简单平带孤立阱 / 复杂耦合 MQW / 自洽 / valence_mixing k.p），
  或子带/增益计算精度与速度权衡、复杂 MQW 宏（cx-）、q_transport 深阱输运时。触发信号：量子阱、QW、
  quantum well、子带、subband、valence mixing、k.p、耦合阱、complex MQW、self-consistent、
  增益谱形状不对、开启电压虚高等。不适用于：GaN 特有物理（用 gan-wurtzite-mqw）、材料参数定义。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第8章 (P135-149) / 第4章 (P84-85)
tags: [quantum-well, kp, valence-mixing, self-consistent]
related_skills:
  - slug: gan-wurtzite-mqw
    relation: composes-with
  - slug: material-macros
    relation: contrasts-with
---

# 量子阱模型分级与选择

## R — 原文 (Reading)

> "By setting valence_mixing=yes in the active_reg or set_active_reg statements, a full
> computation of subbands using k.p theory is performed. Carrier densities and interband
> optical transitions are obtained using numerical integral over the non-parabolic subbands,
> resulting in longer computation time."
>
> — Crosslight Software Inc., 第8章 §8.1.5 (P142-143)

## I — 方法论骨架 (Interpretation)

量子阱模型是一个精度-速度光谱：默认的"简单 QW"假设平带、对称、阱间孤立，用方阱公式与抛物线子带，快但对非对称/耦合/强场/深阱场景失效；"复杂 MQW"（cx- 宏 + begin_complex/end_complex + type=strained_complex）允许非对称势与阱间耦合，波函数重叠时按概率把载流子与跃迁分配到各阱；"自洽 MQW"把 Schrödinger 与 Poisson 迭代，处理强场与电荷再分布（极化器件必选）；"valence_mixing"用 k.p 解非抛物线价带（重/轻空穴反交叉、负有效质量区），应变阱尤其重要但慢。深阱/极化器件默认热化假设还会高估开启电压，需要 q_transport 非局域输运修正。选择原则：先确认物理需求（阱深/耦合/场强/应变），再选最低可用的模型等级。

## A1 — 书中的应用 (Past Application)

### 案例 1: 模型等级谱系
- **问题**: 用户面对不同 QW 结构该选哪级模型。
- **方法论的使用**: 手册给出分级图（简单→复杂→自洽，可选 valence mixing），并说明每级的限制与适用场景。
- **结论**: 默认模型只适合隔离平带阱；耦合/非对称/极化需升级。
- **结果**: 成为所有 QW 仿真选择的起点（第8章 §8.1）。

### 案例 2: 氮化物深阱
- **问题**: 深阱（氮化物）默认模型高估开启电压。
- **方法论的使用**: 加 q_transport 非局域量子输运修正。
- **结论**: 热化假设在深阱失效。
- **结果**: 开启电压修正（第4章 §4.10.4）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 新有源区设计，不确定用简单还是复杂/自洽 QW 模型。
2. 增益谱形状/阈值异常，怀疑子带模型近似不足。
3. 薄垒耦合 MQW、非对称阱、强极化/强场器件。
4. 需要在 valence_mixing 精度与计算时间之间权衡。

### 语言信号 (用户的话里出现这些就应激活)

- "量子阱模型 / quantum well model / subband"
- "耦合阱 / complex MQW / cx-"
- "valence mixing / k.p / 子带"
- "增益谱不对 / 开启电压虚高 / q_transport"

### 与相邻 skill 的区分

- 与 `gan-wurtzite-mqw` 的区别: 本 skill 是通用 QW 模型分级；GaN 的极化/基晶格问题在 GaN skill 中叠加。
- 与 `material-macros` 的区别: 模型选择是"怎么算"，材料宏是"参数是什么"；两者常一起出现但不同问题。

## E — 可执行步骤 (Execution)

| 步骤 | 输入 | 输出 | 判停/完成标志 |
|---|---|---|---|
| 1 评估物理需求 | 阱深/垒厚/对称性/场强/应变 | 必须升级模型的条件清单 | 列出所有升级触发点 |
| 2 选择模型等级 | 条件清单 + 计算预算 | 模型等级 + 权衡理由 | 等级与物理需求匹配 |
| 3 验证子带与增益 | .gain 子带/增益输出 | 子带间距/反交叉/增益峰对比 | 与实验或文献趋势一致 |

1. **评估物理需求**
   - 检查阱深/垒厚（是否耦合）、对称性、场强（是否自洽）、应变（是否 valence mixing）。
   - 完成标准: 列出必须升级模型的条件清单。
   - 示例: 薄垒耦合 → 复杂 MQW；强场/极化 → self_consistent；应变阱 → valence_mixing=yes；深阱 → q_transport。

   🔴 CHECKPOINT · 🛑 STOP：把"必须升级模型的条件清单"（耦合/非对称/强场/应变/深阱）给用户确认后再选等级。

2. **选择模型等级**
   - 默认简单 QW → 耦合/非对称用复杂 MQW（cx- + begin_complex）→ 强场/极化加 self_consistent → 应变/高精度加 valence_mixing=yes。
   - 深阱加 q_transport。
   - 判停条件: 计算时间不可接受时，退一级并用 .gain 单独算增益、主仿真查表。
   - 完成标准: 模型等级与物理需求匹配，且明确记录了权衡理由。
   - 示例: `active_reg ... valence_mixing=yes`；`self_consistent`；复杂 MQW 用 `begin_complex ... end_complex`（cx- 宏）；深阱加 `q_transport`。

   🔴 CHECKPOINT · 🛑 STOP：把模型等级选择与权衡理由（精度 vs 时间）给用户确认后再改配置。

3. **验证子带与增益**
   - 用 .gain 的 QW subband（k.p）与增益谱检查子带间距、反交叉、增益峰。
   - 完成标准: 子带/增益与实验或文献趋势一致。
   - 示例: 运行 `pics3d.exe xxx.gain` 后检查 mqw_profile 子带文件与增益谱（如 inp13 子带 Gamma/L/HH/LH）。

   🔴 CHECKPOINT · 🛑 STOP：把子带/增益与实验或文献的对比结论给用户确认后才算交付。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 体材料（无量子限制）器件。
- 参数值不准确导致的问题（先查材料宏）。

### 作者在书中警告的失败模式（触发 → 一线修复 → 兜底）

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 薄垒耦合阱被默认模型算错（§8.1.6） | 升级复杂 MQW（cx- + begin_complex/end_complex） | 仍错：核对层数为奇数且 barrier 也调用复杂宏 |
| 强场/极化下平带假设错误（§8.2/§13.5） | .sol 加 self_consistent 自洽迭代 | 仍错：检查 Schrödinger-Poisson 是否真正耦合 |
| 深阱热化高估开启电压（§4.10.4） | 加 q_transport 非局域输运 | 仍高：检查深阱深度与接触 |
| 应变阱子带/增益异常 | 开 valence_mixing=yes（k.p 价带） | 仍异常：核对组分/厚度与 k.p 参数 |
| 计算时间不可接受 | 退一级模型，.gain 单独算增益、主仿真查表 | 仍太慢：检查网格与求解设置 |

### 作者的盲点 / 时代局限

- 手册对 k.p 的实现细节引用 Chuang 等文献，未覆盖最新多体效应扩展；many-body 模型在 §8.5 仅作简介。

### 容易混淆的邻近方法论

- valence_mixing（k.p 子带）与 many-body gain（库仑增强）是两个不同开关，不要混为一谈。

## 相关 skills

- composes-with: `gan-wurtzite-mqw`（GaN 极化叠加自洽）、`material-macros`（对比：模型 vs 参数）

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
