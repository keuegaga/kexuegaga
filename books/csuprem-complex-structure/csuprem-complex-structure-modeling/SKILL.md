---
name: csuprem-complex-structure-modeling
description: |
  用户需要用 Crosslight CSuprem 建立或转换复杂器件结构（工艺仿真：淀积/刻蚀/注入/扩散/氧化、2D/3D 结构定义、GDSII 导入、导出给 APSYS）时使用。
  触发信号：CSuprem/工艺仿真/process simulation、复杂结构/复杂几何建模、etch/deposit/implant/diffuse/mask、
  zmesh.zst、quasi3d/three.dim、3D 结构转换、GDSII、suprem_property/suprem_contact、把工艺结构导入 APSYS。
  不适用于：只定义规则分层器件（用 pics3d-laser-workflow / LayerBuilder / Layer3d / GeoEditor 直接建 .layer/.geo 更快）、
  已发散的仿真调试（用 convergence-debugging）、纯网格优化（用 mesh-quality）、材料宏选择（用 material-macros）。
source_book: 《CSuprem User's Manual V3.0 + CSuprem 2D/3D Tutorial》 Crosslight Software Inc.（源自 Stanford Suprem4）
source_chapter: 手册第 3 章（PDF P27-31）/ 第 6 章（P140-167）/ 第 7 章；2D 教程 P8-29；3D 教程 P4-50
tags: [csuprem, process-simulation, 3d, structure, etch, gdsii, apsys]
related_skills:
  - slug: mesh-quality
    relation: composes-with
  - slug: pics3d-laser-workflow
    relation: contrasts-with
  - slug: material-macros
    relation: composes-with
  - slug: gan-wurtzite-mqw
    relation: contrasts-with
---

# CSuprem 复杂结构设计建模

## R — 原文 (Reading)

> "It is recommended that you initially attempt to reproduce the same results in 2D by using uniform planes. Then, you will be ready to change the conditions of some of the planes to make it real 3D."
>
> "deposition and implantation are the same for all planes. Only etching can vary from plane to plane."
>
> "If a 2D simulation fails, the 3D simulation would certainly fail."
>
> — CSuprem User's Manual V3.0，第 3 章 §3.3-3.5（PDF P29-31）

## I — 方法论骨架 (Interpretation)

CSuprem 用一套"网格线-区域-边界"三段式语法描述结构：先定义 x/y 网格线（tag 作引用句柄、spacing 控密度），再圈矩形材料区域（region），最后声明衬底边界（bound exposed/backside/reflecting）。结构不是一次画完的，而是"初始衬底 + 一串工艺步骤（淀积/掩膜/刻蚀/注入/扩散/氧化）"的演化结果——复杂形貌（沟槽、spacer、坡角、FinFET 鳍）由步骤序列自然产生。

3D 不引入新几何语言，而是"一组 xy 平面文件 + zmesh.zst（z_structure 定义平面位置）"，用 `mode three.dim`（或先 `quasi3d`）加 `3d_mesh` 组装。正确路径是三级验证阶梯：2D 复现 → quasi3d 快速全平面验证 → 逐平面差异化后 three.dim 全耦合。转换本身是清单化操作：复制 xy 平面、etch 命令逐段加 `segm=`、复用示例 zmesh.zst 模板；只有刻蚀可逐平面变化，淀积/注入全平面一致。GDSII 版图由 GDS2MASK 自动切平面生成 zmesh.zst，但每个关键平面必须先过 2D 仿真（"2D 失败则 3D 必然失败"）。

最终用 `export outfile=xxx.aps`（xpsize/triangle.based/repair.mesh）把结构交给 APSYS：.sol 中 `3d_solution_method 3d_flow=yes` + `load_mesh suprem_import=yes`，逐平面 `begin_zmater/end_zmater` 内用 `suprem_property`/`load_macro`/`suprem_contact`/`contact` 建立材料与接触编号契约（必须严格一致）。

## A1 — 书中的应用 (Past Application)

### 案例 1: 3D nMOSFET 14 步流程（3D 教程 P14）
- **问题**: 从零构建一个带 STI、spacer、源漏的完整 3D MOSFET，并交给 APSYS。
- **方法论的使用**: 按"工艺步骤即结构演化"排 14 步（STI 六步 → 栅氧 → 沟道注入 → poly 淀积/退火/刻蚀 → LDD → spacer → 干氧退火 → 源漏注入 → 接触窗 → mirror 镜像 → export）。
- **结论**: 复杂结构 = 衬底 + 有序工艺步骤，而不是一次画完的几何。
- **结果**: 得到完整 3D MOSFET 结构并成功导出，后续 APSYS 器件仿真跑出 Vd-Id 曲线族。

### 案例 2: LDD MOSFET 3D（手册第 6 章 §6.2）
- **问题**: 2D 结构转 3D 时刻蚀如何逐平面生效。
- **方法论的使用**: `mode three.dim` + `3d_mesh nsegm=2 infile=geo zstfile=zmesh.zst`；etch 命令对 segm=1、segm=2 各写一份；deposit/implant 只写一次；最后 `struct mirror left` + `export outf=ldd.aps xpsize=0.0001 triangle.based=f`。
- **结论**: 淀积/注入全平面一致、只有刻蚀逐 segm；镜像与导出是标准收尾。
- **结果**: 生成 3D LDD 结构与掺杂分布（图 6.3-6.5），可交 APSYS。

### 案例 3: 独立栅 FinFET 逐段多边形刻蚀（手册第 6 章 §6.4）
- **问题**: 五个 z 段角色不同，需要精细化刻蚀。
- **方法论的使用**: 第 1/2/4/5 段整段刻蚀，第 3 段用 `etch segm=3 ... start/continue/done` 多边形窗口多次刻蚀；逐段淀积 poly/nitride 再逐段去除。
- **结论**: 差异化全部交给"掩膜 + etch 逐 segm"，不触碰全平面步骤。
- **结果**: 生成独立栅 FinFET 结构（图 6.9）。

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 新建 CSuprem 工艺仿真：问"怎么定义结构/淀积/刻蚀/掩膜"、"etch 怎么刻出沟槽/坡角/侧墙"。
2. 把已有 2D 工艺或器件结构转 3D：问"2D 怎么转 3D"、"zmesh.zst 怎么写"、"etch 要不要逐平面"。
3. 从版图/GDSII 建 3D：问"GDSII 怎么导入 CSuprem"、"GDS2MASK 怎么用"。
4. 把工艺结果交给器件仿真：问"怎么导出给 APSYS"、"suprem_property/suprem_contact 怎么设置"、"材料/接触编号对不上"。
5. 3D 仿真失败或想优化：问"3D 不收敛/崩溃怎么办"、"先 quasi3d 还是直接 three.dim"。

### 语言信号 (用户的话里出现这些就应激活)

- "CSuprem / 工艺仿真 / process simulation / 结构建模 / 复杂结构"
- "etch / deposit / implant / diffuse / mask / oxidation"
- "zmesh.zst / z_structure / quasi3d / three.dim / 3d_mesh / segm="
- "GDSII / GDS2MASK / 版图转仿真"
- "suprem_property / suprem_contact / suprem_import / export .aps"

### 与相邻 skill 的区分

- 与 `pics3d-laser-workflow` 的区别: 本 skill 走 CSuprem 工艺路线（需要工艺历史/复杂 3D 几何）；激光器常规结构用 .layer/.sol 工作流直接建，不要引入工艺仿真。
- 与 `mesh-quality` 的区别: 本 skill 负责"结构怎么定义/工艺怎么演化"，网格是其中的步骤之一；纯网格加密/收敛问题交给 mesh-quality。
- 与 `material-macros` 的区别: 本 skill 只在导出链路里引用 load_macro/suprem_property 的编号契约；材料参数本身选宏用 material-macros。
- 与 `gan-wurtzite-mqw` 的区别: CSuprem 文档面向硅 CMOS；GaN 外延/极化物理不在本 skill 范围（除非用户明确要 CSuprem 工艺路线）。

## E — 可执行步骤 (Execution)

当 skill 被激活后，agent 应按以下步骤执行:

1. **判断路线与范围**
   - 确认用户要的是工艺仿真（CSuprem）还是直接结构建模（LayerBuilder/Layer3d/GeoEditor）。
   - 完成标准: 明确写出所选路线与理由；若是规则分层器件，转 `pics3d-laser-workflow` 并说明。

2. **搭 2D 结构骨架（网格线-区域-边界）**
   - 按 `line`（tag/spacing）→ `region` → `bound` → `init` 顺序给出命令；关键界面打 tag。
   - 完成标准: 每个 region/bound 均引用已定义 tag；边界类型（exposed/backside/reflecting）按工艺作用面选择。
   - 判停条件: 若用户只要 2D 结构，跳到步骤 5 导出/验证；否则继续 3D。

3. **编排工艺步骤序列**
   - 按"淀积→掩膜→刻蚀→注入→扩散/氧化"逐条给出命令；刻蚀形状用 left/right 或 start/cont/done 多边形，坡角用 mask 的 theta + avoidmask。
   - 完成标准: 每个步骤说明它改变什么几何/掺杂；掩膜类刻蚀确认 mask 前置。

4. **3D 化（若需要）**
   - 生成 xy 平面文件（每个平面一份）、zmesh.zst（z_structure 定义 zseg_num/zplanes，zplanes=1，taper/bend/cylindrical 按需）、`mode quasi3d` 先验证、`3d_mesh nsegm=... infile=... zstfile=zmesh.zst`、`init`。
   - 把 etch 命令逐平面加 `segm=`；淀积/注入只写一次。
   - 完成标准: 每个平面文件能独立通过 2D 仿真；quasi3d 全平面跑通后再切换 `mode three.dim`。

5. **导出与对接（若需要器件仿真）**
   - `export outfile=xxx.aps xpsize=... triangle.based=... repair.mesh=yes`；在 .sol 中加 `3d_solution_method 3d_flow=yes`、复制 z_structure、`load_mesh ... suprem_import=yes`，逐平面 `begin_zmater/end_zmater` 内用 suprem_property/suprem_contact 编号并与 load_macro/contact 一致。
   - 完成标准: 材料/接触编号逐一核对；导出文件能被 APSYS 读取。

6. **验证与交付**
   - 给出预期输出（生成的结构文件/掺杂分布/可导入的 .aps）与验证步骤（2D 复现 → quasi3d → three.dim；错误时按"先 2D 后 3D"定位）。
   - 完成标准: 用户拿到可运行的输入 deck + 明确的自检清单。

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 规则分层器件（FP 激光器、LED、普通二极管）——直接用 LayerBuilder/Layer3d/GeoEditor 或 .layer 工作流更快、更易收敛；
- 仿真已发散（走 convergence-debugging）、纯网格优化（mesh-quality）、材料宏选择（material-macros）；
- 只需结果解读/绘图（post-processing）。

### 作者在书中警告的失败模式

- 不先 2D/quasi3d 验证直接全 3D：耗时且必然在个别平面处崩溃；
- etch 漏加 `segm=`：3D 下刻蚀没有作用到所有平面（或作用错平面）；
- 误以为淀积/注入可逐平面不同（语法不支持）；
- `zplanes≠1` 时氧化仿真崩溃（经验规则：CSuprem 中恒为 1）；
- suprem_property / load_macro / suprem_contact / contact 编号不一致：静默映射错误；
- 修改 zmesh.zst 固定格式行（output/export_3dgeo）；
- 漏设 `bound exposed`：教程点名的"最常见错误"，工艺步骤不作用于该面；
- avoidmask 型刻蚀没有前置 mask；
- 网格过稀导致刻蚀/氧化形貌失真。

### 作者的盲点 / 时代局限

- 手册基于 2004-2014 的硅 CMOS 工艺（Suprem4 血统，≤1µm 时代假设）；先进节点（GAA、应变工程细节）未必覆盖；
- 淀积只有纯几何模型（无物理沉积形貌）；
- 无 GaN/化合物光电器件工艺示例——材料宏与工艺参数需用户自行扩展；
- "2D 失败则 3D 必然失败"等经验结论基于当时求解器行为，新版行为可能变化。

### 容易混淆的邻近方法论

- 直接结构建模（LayerBuilder/Layer3d/GeoEditor）与工艺仿真（CSuprem）：前者快、后者能复现工艺历史，按器件类型选；
- `quasi3d` 与 `three.dim`：不是精度开关，是平面间耦合模型的选择；
- export 的 `triangle.based` 与 `mat.priority`：加点策略不同，影响导入后网格。

## 相关 skills

- composes-with: `mesh-quality`（结构里的网格步骤）、`material-macros`（导出链路的材料编号）
- contrasts-with: `pics3d-laser-workflow`（规则分层激光器直接 .layer 路线）、`gan-wurtzite-mqw`（GaN 外延物理，非 Si 工艺）

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓（核心单元 U1-U8，见 verified.md）
- **测试通过率**: 见 test-results.md
- **蒸馏时间**: 2026-08-17
