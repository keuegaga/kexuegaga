# CSuprem 复杂结构设计建模 — 精华 (DIGEST)

> 本文由 cangjie-skill 蒸馏生成，只呈现**通过三重验证**的方法论。
> 想深入时点小节末尾的 skill 链接；想看全貌读 [INDEX.md](./INDEX.md)。
> 作者: Crosslight Software Inc.（源自 Stanford Suprem4）| 手册 2004-2014，教程 2008 | 全文约 3800 字，预计阅读 15 分钟

## 这套文档在讲什么

CSuprem 是 Crosslight 的 2/3 维工艺仿真器，血统可追溯到斯坦福 1970-1990 年代的 Suprem4。它解决的问题是：**现代半导体器件的复杂几何（沟槽隔离、侧墙、坡角、FinFET 鳍、3D 布局）怎么从"工艺步骤"一步步长出来，而不是手工画出来。** 它的答案是一套高度统一的语法——网格线、材料区域、衬底边界三种元素 + 淀积/掩膜/刻蚀/注入/扩散/氧化六类工艺命令，2D 与 3D 共用同一套语言。

这套资料对 Crosslight 用户的价值在于：当器件复杂到 LayerBuilder/GeoEditor 画不动（或必须复现工艺历史时），CSuprem 是唯一能把"版图 → 工艺 → 结构 → 器件仿真"串起来的路径。

---

## 一、结构建模的基本单元：网格线-区域-边界

**它解决什么问题**：任何结构仿真的第一个问题都是"从哪开始"。

**核心逻辑**：所有结构都按固定顺序搭建——先定义 x/y 网格线（`line`，可打 `tag` 供引用、`spacing` 控密度），再用 tag 或坐标圈定矩形材料区域（`region`），最后声明衬底边界（`bound`：exposed 参与工艺、backside 只做缺陷复合、reflecting 是注入镜像）。tag 是这套体系的句柄：后续命令一律引用 tag 而非硬编码坐标，一处改动全局生效。

**书中的用法**：2D/3D 教程里每个平面文件都以同样的 `line → region → bound → init` 开头。

> "Between these flag points, mesh points will be inserted with density controlled by 'spacing'. Smaller 'spacing' means more mesh points."（3D 教程 P5）

**什么时候会失效**：region 必须是网格线围成的矩形；任意多边形结构要先拆成矩形区域或改用 GeoEditor 类工具。

→ 深入: [`csuprem-complex-structure-modeling`](./csuprem-complex-structure-modeling/SKILL.md)

---

## 二、工艺步骤即结构演化

**它解决什么问题**：复杂形貌（沟槽、侧墙、坡角）不是画出来的，是"做"出来的。

**核心逻辑**：把器件看成"初始衬底 + 一串工艺步骤"的演化结果。淀积（deposit）长材料、掩膜（mask）定窗口、刻蚀（etch）去材料、注入（implant）掺杂质、扩散/氧化（diffuse）热处理。spacer 的"正确"建法不是画梯形，而是"保形淀积 + 干法回刻到固定厚度"。

**书中的用法**：3D 教程的 nMOSFET 14 步流程（STI 六步 → 栅氧 → 沟道注入 → poly → spacer → 源漏 → 接触窗 → 镜像 → 导出）完整示范了"步骤序列 = 结构"。

**什么时候会失效**：只想要最终结构、不需要工艺历史时，直接建模更快——这正是本 skill 的边界。

---

## 三、刻蚀：复杂结构设计的主要工具

**它解决什么问题**：把"哪里的材料去掉、去掉成什么形状"表达出来。

**核心逻辑**：刻蚀模式对应形貌——`left/right` 直线刻蚀（p 点定义界线）、`start/cont/done` 多边形顶点序列（任意刻蚀窗口）、`dry` 按厚度垂直下切、`avoidmask` 沿掩膜坡角（`theta`）刻蚀、`physical` 按材料速率。差异化来自掩膜：`mask` 定义光刻窗口（可多窗口、可带坡角），刻蚀跟随掩膜。

**书中的用法**：FinFET 实例用 `etch segm=3 ... start/continue/done` 多次多边形刻蚀，把第 3 段鳍做出精细形状，而其他段整段刻蚀。

**什么时候会失效**：avoidmask 必须先有 mask；纯几何刻蚀不模拟物理形貌（各向同性等效应需 physical 模式）。

---

## 四、3D：同一套语法，多一组 z 方向定义

**它解决什么问题**：把 2D 结构扩展到 3D 而不引入新的几何语言。

**核心逻辑**：3D = 一组 xy 平面文件（每个平面用 2D 语法）+ `zmesh.zst`（`z_structure` 定义平面位置：`zseg_num` 编号、`zplanes` 重复、`taper/bend_xy_plane/cylindrical` 表达斜面/弯曲/旋转）。用 `mode three.dim`（全耦合）或 `quasi3d`（忽略平面间耦合）加 `3d_mesh` 组装。

**书中的用法**：segr3d 用两个平面文件（一个纯硅、一个含 Si/SiO2 界面）演示 z 方向材料差异与隔离。

**什么时候会失效**：CSuprem 中氧化仿真要求 `zplanes=1`；3D 成本高，必须先验证。

---

## 五、2D→3D 转换方法论：三级验证阶梯

**它解决什么问题**：3D 的不可调试性。

**核心逻辑**：正确路径是"2D 复现 → quasi3d 快速全平面验证 → 逐平面差异化后 three.dim 全耦合"。转换本身是清单化操作：复制 xy 平面文件、etch 命令逐段加 `segm=`、复用示例 zmesh.zst 模板。**只有刻蚀可逐平面变化，淀积/注入对所有平面一致**——这是最容易踩的设计约束。

**书中的用法**：LDD 3D 实例里 `etch poly right ... segm=1 / segm=2` 写两遍，而 `deposit`/`implant` 只写一次。

> "deposition and implantation are the same for all planes. Only etching can vary from plane to plane."（手册 §3.3.2）

**什么时候会失效**：跳过验证直接全 3D——大概率在某个平面崩溃，且难定位。

---

## 六、GDSII 与导出对接：版图到器件仿真的闭环

**它解决什么问题**：真实芯片版图怎么进仿真、工艺结构怎么给器件仿真。

**核心逻辑**：GDSII 由 `GDS2MASK` 自动切平面并生成 zmesh.zst，但**每个关键平面必须先过 2D 仿真**——"If a 2D simulation fails, the 3D simulation would certainly fail." 工艺结果用 `export outfile=xxx.aps`（`xpsize` 控边界间隙、`triangle.based` 选加点方式、`repair.mesh` 导出前修网格）交给 APSYS；.sol 中 `suprem_import=yes` 读入，逐平面 `begin_zmater/end_zmater` 内用 `suprem_property`/`suprem_contact` 编号，并与 `load_macro`/`contact` 严格一致——编号契约是这条链路最常见的断点。

**书中的用法**：3D 教程把四接触（源/栅/漏/衬底）逐段定义后，用 start_loop + scan 跑出双 Vg 的 Vd-Id 曲线族。

---

## 陷阱与反例

- **跳过验证直接全 3D**：最贵的错误。先 2D、再 quasi3d，最后 three.dim。
- **etch 漏加 `segm=`**：3D 下刻蚀没作用到所有平面（或作用错平面），结构悄悄不对。
- **误以为淀积/注入可逐平面不同**：语法不支持；差异化只能靠 etch。
- **`zplanes≠1` 做氧化**：经验规则警告会崩溃。
- **编号对不上**：suprem_property/load_macro/suprem_contact/contact 不一致 = 静默映射错误。
- **漏设 `bound exposed`**：教程点名的"最常见错误"，工艺步骤不作用于该面。
- **avoidmask 没有前置 mask**：直接报错或乱刻。
- **对规则分层器件用 CSuprem**：FP 激光器/LED 用 LayerBuilder 直接建 .layer 快一个数量级。

## 作者的局限（读这套文档要打的折扣）

- **硅 CMOS 血统**：手册基于 2004-2014 的 ≤1µm 硅工艺（Suprem4），无 GaN/化合物光电器件工艺示例；GaN 材料宏与工艺参数需自行扩展。
- **淀积只有几何模型**：无物理沉积形貌；沟槽填充等形貌问题不能完全指望它。
- **经验规则缺机理**："zplanes=1 防崩溃""2D 失败 3D 必败"是经验结论，基于当时求解器行为。
- **最强的反对意见**：对规则分层器件，LayerBuilder/Layer3d 直接建模更快更易收敛；CSuprem 只在"必须复现工艺历史"时不可替代。

## 关键术语速查

| 术语 | 作者的用法 | 和常识的差异 |
|---|---|---|
| line/tag/spacing | 网格控制点/引用句柄/插入密度 | ≠ 结构线/普通名称/线间距 |
| region | 网格线围成的矩形材料区 | ≠ 任意多边形 |
| bound | exposed/backside/reflecting 决定工艺作用面 | ≠ 普通边界条件 |
| mode | quasi3d（无耦合）/ three.dim（全耦合） | ≠ 精度开关 |
| zmesh.zst | 3D z 方向定义文件 | 固定文件名，只改 z_structure |
| export | 导出 .aps 给 APSYS（xpsize/repair.mesh） | ≠ struct 存档 |
| suprem_property/suprem_contact | 给导入结构的材料/接触编号 | 必须与 load_macro/contact 一致 |

完整词典见 [GLOSSARY.md](./GLOSSARY.md)。

## 如果只带走三句话

1. 结构 = 网格线（tag 句柄）+ 矩形区域 + 边界类型，3D 只是"多组平面 + z 方向定义"。
2. 复杂形貌靠工艺步骤演化：淀积长、掩膜定、刻蚀切、注入掺、扩散热处理；只有刻蚀能逐平面。
3. 永远先 2D 后 3D、先 quasi3d 后 three.dim；导出给 APSYS 前对好材料/接触编号，2D 不过关就别碰 3D。
