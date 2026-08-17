---
name: material-macros
description: |
  用户在 Crosslight 中需要选择/自定义材料宏（被动/主动宏）、核对单位制（μm、m^-3、eV）、用 use_macrofile
  加载自定义宏、或在 .sol 中覆盖材料参数时。触发信号：材料宏、macro、band_gap、load_macro、get_active_layer、
  自定义材料、掺杂单位、m^-3/cm^-3 换算、材料参数不准想改、use_macrofile 等。
  不适用于：模型物理选择（用 qw-model-selection）、GaN 特有物理（用 gan-wurtzite-mqw）。
source_book: 《Crosslight Device Simulation Software General Manual》 Crosslight Software Inc.
source_chapter: 第3章 (P59-61) / 附录B (P1280-1292)
tags: [material, macro, units, custom]
related_skills:
  - slug: gain-preview-workflow
    relation: composes-with
  - slug: gan-wurtzite-mqw
    relation: composes-with
---

# 材料宏体系、单位与自定义覆盖

## R — 原文 (Reading)

> "A macro is a collection of input statements (or commands). ... it is STRONGLY recommended
> that the default macro files not be altered in any way since that would affect all the
> simulations that use these default files."
>
> — Crosslight Software Inc., 第3章 §3.5 (P59-60)

## I — 方法论骨架 (Interpretation)

Crosslight 把一组材料参数语句（band_gap、electron_mobility、real_index 等）打包成"宏"。命名约定承担语义：小写被动宏（gaas、ingaasp）用 load_macro 加载，管体材料参数；混合大小写主动宏（AlGaAs、InGaN）用 get_active_layer 加载，管量子阱子带与光跃迁；cx- 前缀是复杂 MQW 宏。有源区必须同时有被动+主动宏。两个安全纪律：绝不改默认宏文件（crosslight.mac/more.mac），自定义用 use_macrofile 加载自己的 .mac（放同目录）或在 .sol 里 load_macro 后重发参数语句覆盖（后发覆盖先发）。单位制特殊：长度 μm、能带 eV、掺杂 m^-3、迁移率 m²/(V·s)，混用是最常见错误。四元材料用 Adachi 双线性插值并保证在匹配线与三元端点与实验一致。

## A1 — 书中的应用 (Past Application)

### 案例 1: 自定义宏覆盖
- **问题**: 想调整某材料参数但不影响默认库。
- **方法论的使用**: 在输入文件里 load_macro 之后重发 band_gap 语句；或用 use_macrofile 加载自定义宏文件。
- **结论**: 覆盖只影响当前仿真。
- **结果**: 手册推荐做法（附录B §B.2）。

### 案例 2: InGaAsP 宏选择错误
- **问题**: 教程提醒 InGaAsP 系宏选错（匹配 GaAs 还是 InP、是否应变）是常见问题。
- **方法论的使用**: 读宏头注释、用 LayerBuilder 查宏列表与说明。
- **结论**: 材料系/晶格匹配/组分必须与目标一致。
- **结果**: 避免静默算错（第22章 §22.2）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 新结构要选材料宏（尤其 InGaAsP/InGaN 系）。
2. 手册默认宏参数与实验不符，想安全地自定义。
3. 单位换算出错（cm^-3 vs m^-3）导致结果异常。
4. 需要理解 load_macro/get_active_layer/use_macrofile 语法。

### 语言信号 (用户的话里出现这些就应激活)

- "材料宏 / macro / load_macro / get_active_layer"
- "自定义材料参数 / override bandgap / use_macrofile"
- "掺杂单位 / m^-3 / cm^-3"
- "默认宏能不能改 / custom macro file"

### 与相邻 skill 的区分

- 与 `qw-model-selection` 的区别: 本 skill 管"参数值怎么定义"；模型 skill 管"用哪级近似算子带/增益"。
- 与 `gan-wurtzite-mqw` 的区别: GaN 特有物理（基晶格/极化）由 GaN skill 负责；宏体系是通用机制。

## E — 可执行步骤 (Execution)

1. **选宏与核对单位**
   - 确认材料系、衬底/晶格匹配、组分与应变类型；把 cm^-3 掺杂换算为 m^-3。
   - 完成标准: 宏名称与注释说明匹配目标材料。

2. **自定义（不碰默认库）**
   - 新建 .mac 文件放同目录，use_macrofile 加载；或 .sol 中 load_macro 后重发参数语句。
   - 判停条件: 需要温度相关/组分相关参数时用 variation=function 或 table 语法（附录B 规则）。
   - 完成标准: 覆盖生效（可通过 .gain 预览或输出验证）。

3. **验证与回归**
   - 用 .gain 预览核对修改后的增益/带隙等；确认其他仿真未被影响。
   - 完成标准: 目标参数变化符合预期，无意外副作用。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 模型选择问题（简单 vs 复杂 QW）。
- 器件结构/网格问题。

### 作者在书中警告的失败模式

- 直接改默认宏 → 影响所有仿真（§3.5）。
- 语句行超 80 字符被静默截断、用了 tab 等不可见字符（附录B）。
- 绝缘宏（type=insulator）下隧穿/碰撞电离失效（§4.10.3）。

### 作者的盲点 / 时代局限

- 宏参数（尤其 GaN 系）不确定性大，手册宏库未随最新数据全面更新；自定义时需标注数据来源。

### 容易混淆的邻近方法论

- 覆盖语句"后发覆盖先发"与重复材料号语句的行为一致，都是最后一条生效。

## 相关 skills

- composes-with: `gain-preview-workflow`（.gain include .mater）、`gan-wurtzite-mqw`（纤锌矿宏与基晶格）

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-14
