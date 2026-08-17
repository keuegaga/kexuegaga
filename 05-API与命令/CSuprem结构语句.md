---
title: CSuprem 结构语句
type: reference
product: CSuprem
version: "通用"
status: source
source: "[[99-原始资料/教程与问答/CSuprem_2D_tutorial.pdf]]；[[99-原始资料/教程与问答/CSuprem_3D_tutorial.pdf]]；[[99-原始资料/产品手册/csuprem_manual.pdf]] 第7章"
last_verified: 2026-08-17
tags:
  - crosslight
  - reference
  - csuprem
---

# CSuprem 结构语句

> 每条按六要素：含义 / 类型 / 可选值 / 默认值 / 约束 / 相关错误。默认值未明示处标注「手册未给出」。

## line / region / bound（结构骨架）

- 含义：`line` 定义网格控制点（tag 供引用、spacing 控插入密度）；`region` 圈定矩形材料区；`bound` 声明 exposed/backside/reflecting 三类衬底边界。
- 类型：语句（浮点坐标 + string tag）
- 可选值：`line x/y loc= tag= spacing=`；`region silicon xlo=xhi=ylo=yhi=`；`bound exposed/backside/reflecting ...`
- 默认值：spacing 默认按两线距离取小者；orient 默认 100
- 约束：region 必须是网格线围成的矩形；漏设 `bound exposed` 是教程点名常见错误
- 相关错误：区域越界、tag 未定义就引用

## init（衬底初始化）

- 含义：建立衬底网格与背景掺杂（杂质已激活），`orient` 指定晶向。
- 类型：语句
- 可选值：`init boron/arsenic/phosphorus conc=... [orient=100]`
- 默认值：orient=100
- 约束：每个仿真从 init 开始；浓度单位 1/cm³
- 相关错误：浓度单位（cm^-3 vs m^-3）混用

## deposit（淀积）

- 含义：纯几何淀积一层材料，可带掺杂（如多晶硅）。
- 类型：语句
- 可选值：`deposit oxide/nitride/poly thick= [div=] [space=] [conc=] [meshlayer=]`
- 默认值：div（子层数）默认 1
- 约束：无物理沉积形貌；`space` 控外缘点密度、`div` 控垂向分层
- 相关错误：淀积网格过稀导致后续刻蚀/氧化形貌失真

## mask（掩膜）

- 含义：定义光刻胶掩膜窗口，可带侧墙坡角。
- 类型：语句
- 可选值：`mask thick= x1.from= x1.to= [x1.left.theta= x1.right.theta=] [x2...]`
- 默认值：theta 默认 0（垂直侧墙）
- 约束：avoidmask 刻蚀必须 mask 前置
- 相关错误：坡角 theta 乱改导致刻蚀轮廓异常

## etch（刻蚀，特殊结构核心）

- 含义：去除指定材料，模式决定形貌。
- 类型：语句
- 可选值：`left/right`（p1/p2 直线）、`start/cont/done`（多边形顶点）、`dry`（按厚度下切）、`avoidmask`（沿掩膜坡角）、`physical`（按材料速率）、`segm=`（3D 指定平面）
- 默认值：手册未给出
- 约束：3D 下每个刻蚀命令必须对每个 zseg_num 复制（漏 segm= 只作用默认平面）；avoidmask 需 mask 前置
- 相关错误：顶点顺序/坐标错误；`zplanes≠1` 氧化崩溃

## implant（注入）

- 含义：离子注入掺杂，可用分析模型（Gauss/Pearson/Dual Pearson）、表格或 SIMS 导入。
- 类型：语句
- 可选值：`implant boron/arsenic/phosphorus dose= energy= [pearson/gauss] [angle=] [rot=]`
- 默认值：模型按 suprem.key；angle/rot 默认 0
- 约束：dose 单位 1/cm²；斜注入边缘需 `extend` 临时外扩网格
- 相关错误：模型/表格缺失、剂量能量单位错误

## diffuse（扩散/氧化）

- 含义：退火扩散与氧化（干/湿），改变掺杂分布与几何。
- 类型：语句
- 可选值：`diffuse time= temp= [dry/wet/steam] [pres=] [flow.control=t ...]`
- 默认值：pres=1；模型由 `method` 决定（fermi/two.dim/full.cpl；vert/compr/viscous）
- 约束：湿氧消耗硅、生长更快；温度过高/步长过大导致后续不收敛
- 相关错误：ramp 单位、一次只允许一种氧化气体

## mode / 3d_mesh（3D 组装）

- 含义：`mode` 选择平面耦合模型（quasi3d 无耦合 / three.dim 全耦合）；`3d_mesh` 加载 xy 平面文件。
- 类型：语句
- 可选值：`mode quasi3d|three.dim`；`3d_mesh nsegm=N infile=xxx zstfile=zmesh.zst`
- 默认值：手册未给出
- 约束：先 quasi3d 验证再 three.dim；3D 用 zmesh.zst（自动引用）
- 相关错误：不先 2D 验证直接 3D → 必然在个别平面失败

## z_structure（zmesh.zst 内）

- 含义：定义 3D 各 xy 平面在 z 方向的位置与重复次数。
- 类型：语句（zmesh.zst 内）
- 可选值：`z_structure uniform_zseg_from= uniform_zseg_to= zplanes= zseg_num= [taper 参数]`
- 默认值：手册未给出
- 约束：CSuprem 中 zplanes 恒为 1（防氧化崩溃）；固定行 `output`/`export_3dgeo` 不可改；taper/bend_xy_plane/cylindrical 表达斜面/弯曲/旋转
- 相关错误：平面位置错位、zplanes≠1 氧化崩溃

## export（导出 APSYS）

- 含义：把网格与掺杂导出为 APSYS 可读 `.aps`。
- 类型：语句
- 可选值：`export outf=xxx.aps xpsize= [triangle.based=] [mat.priority=] [repair.mesh=]`
- 默认值：triangle.based=false；repair.mesh=false
- 约束：xpsize 决定材料边界间隙；导出前建议 repair.mesh=yes；只导出最终结构（工艺已完成）
- 相关错误：坏网格带进器件仿真、边界间隙过小导致材料重叠

## suprem_property / suprem_contact（APSYS 对接）

- 含义：给 CSuprem 导入结构的每种材料/每个接触编号，映射到 APSYS。
- 类型：语句（.sol 的 begin_zmater 内）
- 可选值：`suprem_property silicon_mater=1 oxide_mater=2 ...`；`suprem_contact num=1 xrange=(...) side=upper touch_mater=1`
- 默认值：手册未给出
- 约束：编号必须与 `load_macro`/`contact` 严格一致；逐平面 begin_zmater/end_zmater 分组
- 相关错误：编号不一致 = 静默映射错误（材料/接触错乱）

## 相关链接

[[03-功能模块/CSuprem特殊结构建模]] · [[04-操作流程/CSuprem-2D转3D]] · [[06-案例/STI结构CSuprem输入]]
