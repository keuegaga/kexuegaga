# GLOSSARY — CSuprem 复杂结构设计建模（共享术语词典）

> 由 glossary-extractor 提取并经阶段 3 整理。author_definition 引用保留英文原文（≤100 词），附中文译释。

## 结构建模基础

| 术语 | 作者的用法 | 和常识的差异 | 为什么重要 |
|---|---|---|---|
| line / tag / spacing | 网格控制点；tag 供引用；spacing 控插入密度 | ≠ 结构线；tag ≠ 普通名称；spacing ≠ 线间距 | 一切结构语句的基石 |
| region | 用 xlo/xhi/ylo/yhi（可 tag）圈定的矩形材料区 | ≠ 任意多边形；必须由网格线围成矩形 | 复杂结构 = region 并集 |
| bound（exposed/backside/reflecting） | 决定工艺步骤作用面：exposed 参与工艺、backside 缺陷复合、reflecting 注入镜像 | ≠ 普通边界条件 | 漏设 exposed 是教程点名常见错误 |
| init / orient | 建立衬底网格+背景掺杂；orient=100 默认晶向 | ≠ 变量初始化 | 每个仿真从 init 开始 |
| struct / mirror | 存档（outf=）与镜像复制（mirror left） | export ≠ struct：前者是跨软件接口 | 对称结构省一半网格 |

## 工艺步骤

| 术语 | 作者的用法 | 和常识的差异 | 为什么重要 |
|---|---|---|---|
| deposit（thick/div/space/conc） | 纯几何淀积；div/space 控网格、conc 可掺杂 | ≠ 物理沉积形貌 | "长材料"的唯一手段 |
| etch（left/right/start/cont/done/dry/avoidmask/physical/segm） | 多种刻蚀模式：直线/多边形/干法/掩膜坡角/材料速率/逐平面 | 模式决定形貌 | 复杂结构设计的主要工具 |
| mask / avoidmask | mask 定义光刻窗口（可带 theta 坡角）；avoidmask 沿掩膜刻蚀 | avoidmask 必须先有 mask | 结构差异化的来源 |
| implant（dose/energy/Pearson/Gauss/SIMS） | 分析模型/表格/SIMS 导入 | dose 单位 1/cm² | 掺杂控制的入口 |
| diffuse（dry/wet/flow.control） | 退火与氧化；dry/wet 对应干/湿氧化 | 氧化同时消耗硅 | 退火序列编排 |
| method（fermi/two.dim/full.cpl/vert/compr/viscous） | 扩散/氧化模型选择 | 不同模型成本与精度不同 | 决定物理正确性 |

## 3D 与器件对接

| 术语 | 作者的用法 | 和常识的差异 | 为什么重要 |
|---|---|---|---|
| mode（quasi3d / three.dim） | 是否考虑 xy 平面间耦合 | ≠ 精度开关，是耦合模型选择 | 3D 流程"先 quasi3d 后 three.dim" |
| zmesh.zst / z_structure | 3D z 方向定义文件；zseg_num/zplanes/uniform_zseg_from/to/taper | 固定文件名；用户只改 z_structure | 3D 与 2D 的差异集中点 |
| bend_xy_plane / cylindrical | 平面弯曲 / 绕轴旋转定义 | 表达真实 3D 形貌 | 非平面器件必需 |
| GDS2MASK | 自动把 GDSII 版图切平面并生成 zmesh.zst | ≠ 直接导入跑 3D | 真实芯片 3D 建模入口 |
| export（xpsize/triangle.based/mat.priority/repair.mesh） | 把网格+掺杂导出为 APSYS 可读 .aps | 参数影响导入后网格 | 工艺→器件唯一出口 |
| suprem_property / suprem_contact | 给导入结构的材料/接触编号 | 必须与 load_macro/contact 一致 | 3D 器件仿真对接口 |
| begin_zmater / end_zmater | 按 zseg_num 分组打包每平面的物理/结构语句 | 每平面一组 | 不同平面可定义不同接触 |

## 网格管理

| 术语 | 作者的用法 | 和常识的差异 | 为什么重要 |
|---|---|---|---|
| elimine / double_mesh / loose_mesh | 按矩形区域减半 / 局部加倍 / 松散化 | 只影响指定区域 | 网格质量杠杆 |
| extend | 斜注入前临时外扩网格包围器件边缘 | 注入后自动收缩 | 提高边缘注入精度 |
