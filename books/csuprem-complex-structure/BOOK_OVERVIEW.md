# CSuprem 复杂结构设计建模 — 整书理解 (阶段 0 产出)

> 本文档是 cangjie-skill 流水线的阶段 0 产出，后续所有 extractor 和 skill 都以此为全局上下文。

## 基本信息

- **标题**: CSuprem 2/3 维工艺仿真：复杂结构设计建模
- **作者**: Crosslight Software Inc.（CSuprem 源自 Stanford Suprem4）
- **出版/发布时间**: 手册 2004-2014（v3.0，2014.4 更新）；教程 2008
- **内容类型**: 实操手册 + 教程资料集（3 份 PDF 合并蒸馏）
- **版本来源**: C:\Csuprem\Doc\PDF\（CSuprem_2D_tutorial.pdf / CSuprem_3D_tutorial.pdf / csuprem_manual.pdf）
- **处理时间**: 2026-08-17

---

## 1. 结构 (Structural)

### 类型
实操手册 + 教程（偏"工艺/结构建模方法论"）

### 一句话主旨
CSuprem 用"网格线 + 区域/边界 + 工艺步骤（淀积/刻蚀/注入/扩散/氧化）"把真实器件结构一步步建出来，并可扩展成 3D（xy 平面 + zmesh.zst）后导出给 APSYS 做器件仿真。

### 骨架 (主要论点及其关系)

1. **CSuprem 是什么**：Stanford Suprem4 的 2D 工艺仿真扩展，覆盖淀积、刻蚀、注入、扩散、氧化、应力；2D/3D 模式兼容（2D 输入可直接转 3D）。
2. **结构建模的基本单元**：`line`（网格线，可打 tag 供引用、spacing 控密度）、`region`（材料区域）、`bound`（exposed/backside/reflecting 边界）、`init`（衬底初始化）。
3. **工艺步骤即结构演化**：`deposit`（几何淀积）、`mask`（光刻胶掩膜）、`etch`（刻蚀，核心操作）、`implant`、`diffuse`（含氧化），每一步都改变几何与掺杂。
4. **刻蚀是复杂结构设计的关键**：left/right 直线刻蚀、start/cont/done 多边形刻蚀、dry 干法、avoidmask（沿掩膜坡角）、physical（按材料速率），以及 imported profile / follow.surface / shift。
5. **3D = 一组 xy 平面 + z 方向定义**：每个 xy 平面一个文件（线/区域/边界同 2D 语法），`zmesh.zst` 用 `z_structure` 定义平面位置（zseg_num/zplanes/taper/bend_xy_plane/cylindrical），`mode three.dim`（或 quasi3d）+ `3d_mesh nsegm=...` 组装。
6. **2D→3D 转换方法论**：先跑通 2D（quasi3d 快速验证）→ 复制 xy 平面文件 → etch 命令逐段加 `segm=` 复制 → 用真实 3D 示例的 zmesh.zst 模板；淀积/注入对所有平面相同，只有刻蚀可随平面变化。
7. **GDSII 布局直转 3D**：GDS2MASK 自动切平面并生成 zmesh.zst；前提是先验证平面级 2D 仿真（"2D 失败则 3D 必然失败"）。
8. **3D→APSYS 器件仿真链路**：`export outfile=xxx.aps`（xpsize/triangle.based/repair.mesh）→ .sol 中 `3d_solution_method 3d_flow=yes` + `load_mesh ... suprem_import=yes` + 逐平面 `begin_zmater/end_zmater`（suprem_property/load_macro/suprem_contact/contact 编号一致）。

**论点之间的关系**: 1→2→3 是 2D 基础（层层递进）；4 是 2D 的难点深化；5-7 是 3D 扩展（并列递进）；8 是完整链路出口。整体呈"基础 → 2D 结构 → 3D 结构 → 器件仿真"的递进骨架。

### 作者要解决的核心问题
如何用工艺仿真手段（而非手工画 .layer/.geo）把现代半导体器件的复杂几何（STI、spacer、FinFET 多栅、3D 沟槽）逐步建出来，并可靠地交给器件仿真。

---

## 2. 解释 (Interpretive)

### 关键术语 (作者本人的用法)

| 术语 | 作者的定义 | 和常识用法的差异 |
|---|---|---|
| line / tag / spacing | 定义网格线的位置；tag 给线命名供 region/bound 引用；spacing 决定两点间插入密度 | "line" 不是结构线，是网格控制点；tag 是引用句柄 |
| region | 用 xlo/xhi/ylo/yhi（可用 tag）圈定一个材料矩形区域 | 必须是矩形（由网格线围成），不是任意多边形 |
| bound | 衬底三类边界：exposed（参与淀积/刻蚀/氧化/缺陷复合）、backside（缺陷复合）、reflecting（注入散射镜像） | 边界类型决定哪些工艺步骤作用于该面 |
| zmesh.zst / z_structure | 定义 3D 各 xy 平面 z 位置的固定文件；zseg_num 编号、zplanes 重复次数 | 3D 中 x-y 平面是"段"的边界；氧化仿真要求 zplanes=1 防崩溃 |
| segment / plane / taper / bending | segment 是两个 xy 平面之间的体；taper 用 z_structure 的 taper 参数定义斜面连接；bend_xy_plane 定义平面弯曲 | "平面"与"段"是两个概念：平面是网格面，段是体 |
| quasi3d / three.dim | quasi3d 忽略平面间耦合（快速验证）；three.dim 全耦合（正式 3D） | 两个模式切换是收敛/性能策略，不是简单开关 |
| GDS2MASK | 把 GDSII 版图自动切成多平面并生成 zmesh.zst 的工具 | 3D 工作流的自动化入口，但仍要求先做 2D 验证 |
| suprem_property / suprem_contact | 给 CSuprem 导入的每种材料/每个接触编号并映射到 APSYS | 编号必须与 load_macro/contact 严格一致，是 3D 链路的对接口 |
| etch start/cont/done | 用顶点序列定义一个刻蚀多边形（多段直线边界） | 不是"开始/继续/完成"的语义，是刻蚀形状定义语法 |
| avoidmask | 沿掩膜边缘以指定角度（theta）向下刻蚀一定深度 | 模拟掩膜坡角引起的各向异性刻蚀 |

### 核心命题 (用自己的话)

1. 一切复杂结构都从"网格线网格"开始：线密度 = 结构分辨率，先定义线再定义区域。
2. 结构演化 = 工艺步骤序列；每一步都改变几何（deposit/etch）和掺杂（implant/diffuse）。
3. 刻蚀是 2D 复杂结构设计的主要手段，支持直线/多边形/干法/掩膜坡角/物理速率多种模式。
4. 3D 不引入新几何语言，而是"重复 xy 平面 + z 方向定位"：单个平面用 2D 语法，平面间用 zmesh.zst。
5. 2D→3D 的正确路径是"先 2D 后 3D、先 quasi3d 后 three.dim"——逐级验证，绝不直接上全 3D。
6. 只有刻蚀需要逐平面（segm=）复制；淀积与注入默认对所有平面一致。
7. 平面间可用 taper（斜面）、bend（弯曲）、cylindrical（旋转）表达真实 3D 形貌。
8. GDSII 版图是 3D 复杂结构的天然输入，但每个切割平面必须先过 2D 仿真这一关。
9. 导出的 .aps 结构通过 suprem_property/suprem_contact + begin_zmater 逐段映射进 APSYS。
10. 网格管理是贯穿始终的质量杠杆：line spacing、elimine、double_mesh、extend（注入边缘）、loose_mesh。

### 论证链
作者用 2D 教程（命令逐条演示）→ 3D 教程（完整 nMOSFET 14 步流程）→ 手册第 6 章（真实 3D 输入 deck：segr3d/LDD/STI/FinFET）逐步展示"同一套 2D 语法如何承载 3D 复杂度"，并以 GDS2MASK 和 APSYS 导出完成"版图→工艺→器件"闭环。

---

## 3. 批判 (Critical) ★

### 作者的时代局限
- 手册基于 2004-2014 的 CSuprem v2.0/v3.0，技术前提停留在 ≤1µm 硅 CMOS（Suprem4 血统）；先进节点（FinFET 之后的 GAA、应变工程细节）未必覆盖。
- 淀积只有纯几何模型（无物理沉积形貌）；"2D 失败则 3D 必然失败"等经验结论基于当时网格/求解器行为。
- 教程全程使用 nMOSFET/FinFET（硅集成电路工艺），几乎没有光电器件（GaN 外延、激光器）的工艺示例。

### 作者的立场盲点
- Crosslight 生态以 Si 工艺仿真见长；化合物半导体（GaN/InGaN 外延、刻蚀）需要用户自行扩展材料宏与工艺参数。
- 对"只需最终结构、不需要工艺历史"的场景，文档隐含假设 CSuprem 是正解，但 LayerBuilder/GeoEditor 直接建 .layer/.geo 往往更快。

### 未被证明的假设
- 假设用户已具备工艺知识（刻蚀选择比、掩膜、退火序列），文档只教命令不教工艺本身。
- "zplanes=1 防崩溃"等建议缺少机理说明，属于经验规则。

### 最强反对意见
对规则分层器件（激光器、LED、普通二极管），用 LayerBuilder/Layer3d 直接定义 .layer 并让 layer.exe 生成网格，比 CSuprem 工艺步骤模拟快一个数量级且更易收敛；CSuprem 的价值只在"必须复现工艺历史"（如 STI 形貌、应力、掺杂再分布）时才成立。

> **以上批判会直接成为下游 skill 的 Boundary (B) 字段来源**

---

## 4. 应用潜力 (Applicability)

### 可 skill 化的内容
- [x] **复杂结构设计建模主流程**：2D 网格-区域-边界体系 → 工艺步骤（淀积/刻蚀/注入/扩散）→ 3D 转换（xy 平面 + zmesh.zst + mode/3d_mesh）→ APSYS 导出链路
- [x] **刻蚀方法论**（多边形/干法/avoidmask/physical/逐 segm）
- [x] **2D→3D 转换检查清单**（先 quasi3d、etch 逐 segm、deposit/implant 全平面一致、GDSII 平面先过 2D）
- [x] **3D→APSYS 对接清单**（export 参数、suprem_property/suprem_contact/load_macro 编号一致、begin_zmater 逐段）

### 不适合 skill 化的内容
- 扩散/氧化/应力/注入的物理模型公式（第 4 章）— 保留为术语与引用，不独立成 skill
- 每种杂质的语句细节（硼/砷/磷等条目）— 查询性质，非方法论

### 预估 skill 数量
**约 1 个**（用户需求为单一"复杂结构设计建模"技能；刻蚀/3D 转换/APSYS 对接作为该 skill 的 E/B 内部分节）

### 优先级排序 (按"最能赋能普通人"的角度)
1. csuprem-complex-structure-modeling（复杂结构设计建模：2D/3D 结构定义 + 工艺步骤 + 3D 转换 + APSYS 导出）

---

## ✅ 质量门检查

- [x] 主旨能用一句话说清
- [x] 骨架列出 3–7 个一级论点（8 个）
- [x] 关键术语词典 ≥5 条（12 条）
- [x] 批判阶段列出 ≥3 条作者局限（4 条）
- [ ] 已向用户展示并得到确认（待确认）

**用户确认时间**: {{ }}
