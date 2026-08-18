---
name: gan-wurtzite-mqw
description: |
  用户用 Crosslight 仿真 GaN/InGaN/AlGaN 纤锌矿系器件（激光器/LED/HEMT 有源区）时，处理基晶格、自发/压电极化、
  QCSE 自洽求解、每阱独立材料号、非/半极性晶面、外部应力等 GaN 特有建模要点。触发信号：GaN/InGaN/氮化物、
  wurtzite、极化、QCSE、量子限制斯塔克效应、波长偏蓝/偏红、开启电压虚高、缓冲层/基晶格等。
  不适用于：GaAs/InP 等闪锌矿器件、非 GaN 系的量子阱模型选择（用 qw-model-selection）。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第13章 (P255-268) / 第4章 (P82-85) / 第8章 (P143-144)
tags: [gan, wurtzite, polarization, mqw, qcse]
related_skills:
  - slug: qw-model-selection
    relation: depends-on
  - slug: material-macros
    relation: composes-with
---

# GaN 纤锌矿 MQW 激光器建模要点

## R — 原文 (Reading)

> "One of the most troublesome properties of the wurtzite material system is that its most common
> compounds have spontaneous and strain-induced polarization terms. This manifests itself as a
> fixed interface charge at heterojunction interfaces."
>
> — Crosslight Software Inc., 第13章 §13.5 (P265)

## I — 方法论骨架 (Interpretation)

纤锌矿（GaN 系）与闪锌矿（GaAs/InP 系）的建模差异集中在四件事：第一，应变参考不是衬底而是"基晶格"——缓冲层可能弛豫，默认 GaN 基晶格在 AlN/AlGaN 缓冲下会算错应变；第二，自发+压电极化在界面产生固定电荷，形成局域场（QCSE），弯曲能带、分离载流子、改变增益与波长，必须用 self_consistent 让 Schrödinger 与 Poisson 迭代，且每阱分配独立材料号（independent_mqw）逐阱计算；第三，深阱/极化下默认漂移-扩散+简单 QW 模型高估开启电压，需要 q_transport 等非局域输运修正；第四，非极性/半极性晶面（m/a/r-plane）需要完整 6×6 k.p 与方向平均，耗时建议单独算增益再查表。参数不确定性比闪锌矿大，对结果精度期望要下调。

## A1 — 书中的应用 (Past Application)

### 案例 1: LED_GaN_MQW 教程
- **问题**: APSYS 的 InGaN/GaN MQW LED 二维示例。
- **方法论的使用**: 纤锌矿材料宏 + 极化/自洽相关设置，输出自发辐射谱与 IV。
- **结论**: GaN 系器件必须走纤锌矿专用模型路径。
- **结果**: 官方支持示例（第20章 §20.3 / 附录 H）。

### 案例 2: 氮化物 MQW 收敛困难
- **问题**: 强极化界面电荷的氮化物 MQW 低偏置难收敛。
- **方法论的使用**: slow transient（电压随时间缓升）。
- **结论**: 位移电流恢复被稳态方程抹掉的物理路径。
- **结果**: 手册确认该技巧有效（第4章 §4.8）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 建立 GaN/InGaN 激光器或 LED 仿真，不确定材料宏与极化设置。
2. 仿真波长/增益与实验系统性偏差（偏蓝/偏红）。
3. 开启电压虚高或低偏置不收敛的氮化物器件。
4. 做非极性/半极性晶面（m/a-plane）器件。

### 语言信号 (用户的话里出现这些就应激活)

- "GaN / InGaN / AlGaN / 氮化物激光器仿真"
- "wurtzite / polarization / QCSE / 极化"
- "波长不对 / 开启电压太高"
- "buffer / base lattice / semi-polar / non-polar"

### 与相邻 skill 的区分

- 与 `qw-model-selection` 的区别: 本 skill 是 GaN 特有问题（极化/基晶格）；模型分级（简单/复杂/自洽/k.p）是通用问题，本 skill 依赖它。
- 与 `material-macros` 的区别: 本 skill 讲 GaN 物理建模决策；材料宏 skill 讲怎么安全地定义/覆盖参数。

## E — 可执行步骤 (Execution)

| 步骤 | 输入 | 输出 | 判停/完成标志 |
|---|---|---|---|
| 1 核对材料体系与基晶格 | 衬底/缓冲层材料与弛豫状态 | lattice_base 设置 + 应变参考结论 | 用户确认基晶格 |
| 2 开启极化自洽与独立阱 | 层文件 + .sol 参数 | set_polarization / self_consistent / independent_mqw 语句 + 能带图 | QCSE 弯曲可见 |
| 3 验证与收敛处理 | .gain 预览 + 实验数据 | 波长/增益对比 + 收敛语句 | 关键输出与实验趋势一致 |

1. **核对材料体系与基晶格**
   - 确认衬底/缓冲层材料与弛豫状态，用宏中的 lattice_base 语句设对基晶格。
   - 完成标准: 应变张量依据的参考晶格与生长条件一致。
   - 示例: 材料宏内 `lattice_base` 设为缓冲层材料（如 AlN/AlGaN 缓冲则设对应晶格）；语句细节以手册第 13 章为准。

   🔴 CHECKPOINT · 🛑 STOP：把基晶格/应变参考结论（衬底+缓冲层材料、lattice_base 取值）告诉用户确认后再进入极化设置——基晶格错则后续全部白算。

2. **开启极化自洽与独立阱**
   - 层文件用 set_polarization 自动生成界面电荷；.sol 加 self_consistent；MQW 每阱独立材料号（independent_mqw）。
   - 判停条件: 非极性晶面器件（极化≈0）可跳过 set_polarization，但仍需 6×6 k.p 方向设置。
   - 完成标准: 能带图中 QCSE 弯曲可见，波函数重叠合理。
   - 示例: 层文件加 `set_polarization` 自动生成界面电荷；.sol 加 `self_consistent`（Schrödinger-Poisson 迭代）+ `independent_mqw`（每阱独立材料号）。

   🔴 CHECKPOINT · 🛑 STOP：用能带图确认 QCSE 弯曲与波函数重叠后再进入验证；看不到弯曲先检查 self_consistent 与 independent_mqw 是否生效。

3. **验证与收敛处理**
   - 对比 .gain 预览与实验波长/增益峰；若开启电压虚高加 q_transport，低偏置难收敛用 slow transient。
   - 完成标准: 关键输出（波长/L-I/能带）与实验趋势一致。
   - 示例: 深阱加 `q_transport`（手册 §4.10.4）；低偏置收敛用 `scan var=voltage_1 value=-3.5 var2=time value2_to=1.0`（慢瞬态，§4.8）；用 .gain 预览对比增益峰与实验波长。

   🔴 CHECKPOINT · 🛑 STOP：把波长/增益与实验的对比结论给用户确认后才算交付；系统性偏差（偏蓝/偏红）需先定位基晶格/组分/极化再继续。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 闪锌矿系（GaAs/InP/AlGaAs）器件。
- 非 GaN 系 LED 的自发辐射谱问题。

### 作者在书中警告的失败模式（触发 → 一线修复 → 兜底）

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| 基晶格用错（AlN/AlGaN 缓冲仍按 GaN，§13.1） | 宏中 lattice_base 改为缓冲层材料后重跑 | 应变/能带仍错：核对缓冲层弛豫状态与组分 |
| 不开 self_consistent（QCSE 缺失，§13.5） | .sol 加 self_consistent 让 Schrödinger-Poisson 迭代 | 能带仍平带：检查是否只开了自洽未开耦合 |
| 共享材料号的多个极化阱只算一次（§13.5） | independent_mqw 每阱独立材料号 | 仍错：逐阱核对材料号与组分/厚度 |
| 开启电压虚高 | .sol 加 q_transport 非局域输运 | 仍高：检查深阱深度与接触设置 |
| 低偏置不收敛（强极化界面电荷） | slow transient（scan 加 var2=time） | 仍不收敛：转 convergence-debugging |
| 波长/增益系统性偏蓝或偏红 | 核对组分/厚度/温度/极化参数后重跑 .gain | 仍偏：检查基晶格与 exch_coef/tau_scat |
| 非极性/半极性晶面设置错误 | 跳过 set_polarization 并设 6×6 k.p 方向 | 方向仍不对：核对晶面定义与方向平均设置 |

### 作者的盲点 / 时代局限

- GaN 系能带/极化/迁移率参数不确定性大，手册宏未随最新实验数据全面更新。
- 手册对 GaN 激光器（相对 LED）的专门指导较少，依赖通用 PICS3D 流程。

### 容易混淆的邻近方法论

- 极化界面电荷与普通固定电荷不同：它由组分/应变自动决定，不要手工乱加。

## 相关 skills

- depends-on: `qw-model-selection`（先决定 QW 模型等级再叠加 GaN 特有问题）
- composes-with: `material-macros`（纤锌矿宏与基晶格参数定义）

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
