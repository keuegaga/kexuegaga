# Framework Candidates — CSuprem 复杂结构设计建模

> 由主流程按 framework-extractor.md 串行提取（子代理消息投递失败，降级方案）。英文原文引用均来自 _source/ 提取文本。

- id: f01
  title: 网格线-区域-边界三段式建模
  type: framework
  source_chapter: 2D 教程 P8-10 / 3D 教程 P5-6 / 手册第 7 章 line/region/bound
  source_quote: |
    "line x loc=0.0 tag=lft spacing=0.04 ... line y loc=2. tag=bot spacing=0.3
     region silicon xlo=lft xhi=rht ylo=top yhi=bot
     bound exposed xlo=lft xhi=rht ylo=top yhi=top"
  summary: |
    任何 CSuprem 结构都按固定顺序搭建：先定义 x/y 网格线（可打 tag 供引用、spacing 控密度），
    再用 tag 或坐标圈定矩形 region（材料区域），最后用 bound 声明衬底三类边界。
    这是 2D 与 3D 平面文件共用的同一套语法，是"复杂结构"的唯一入口。
  tags: [framework, structure, mesh, region]

- id: f02
  title: 工艺步骤即结构演化
  type: framework
  source_chapter: 2D 教程 P13-29 / 3D 教程 P14 / 手册第 1 章
  source_quote: |
    "Deposit, etch, implant, diffusion, oxidation, stress analysis."
  summary: |
    把器件结构看成"初始衬底 + 一串工艺步骤"的演化结果，而不是一次画完的最终几何。
    每一步（deposit/etch/implant/diffuse）同时改变几何与掺杂；复杂形貌由步骤序列自然产生
    （如 spacer = 淀积 + 干法回刻），这决定了建模时"先想工艺顺序，再写命令"的思考顺序。
  tags: [framework, process, structure-evolution]

- id: f03
  title: 2D→3D 转换方法论（先 2D，后 quasi3d，再 three.dim）
  type: framework
  source_chapter: 手册第 3 章 §3.3（PDF P29-31）
  source_quote: |
    "it is recommended that you initially attempt to reproduce the same results in 2D by using
     uniform planes. Then, you will be ready to change the conditions of some of the planes to make it real 3D.
     ... it is recommended that you use 'mode quasi3d' first."
  summary: |
    3D 建模的三级验证阶梯：先在 2D 复现结果 → 用 uniform planes 快速跑准 3D（quasi3d）→
    再逐个平面差异化进入全耦合 three.dim。每级失败都在本级修，绝不直接跳全 3D。
    转换本身是机械步骤：复制 xy 平面文件、etch 命令逐段加 segm=、复制 zmesh.zst 模板。
  tags: [framework, 3d, verification, migration]

- id: f04
  title: 平面差异化最小化原则（只有刻蚀可逐平面变化）
  type: framework
  source_chapter: 手册第 3 章 §3.3.2（PDF P30）
  source_quote: |
    "deposition and implantation are the same for all planes. Only etching can vary from plane
     to plane (as a result of mask/photolithography)."
  summary: |
    3D 中淀积/注入对所有 xy 平面一致，只有刻蚀（源于掩膜/光刻）可以逐平面不同。
    因此设计 3D 结构时，先想"哪些步骤全平面统一、哪些必须逐 segm 差异化"，
    差异化只交给 etch + segm=，避免在 deposit/implant 上错误地逐平面折腾。
  tags: [framework, 3d, etch, segm]

- id: f05
  title: GDSII 平面先过 2D 验证
  type: framework
  source_chapter: 手册第 3 章 §3.5（PDF P31）
  source_quote: |
    "Ideally, we recommend at least some of the planes cut from GDSII pass a 2D simulation test
     before submitting for a 3D simulation job. ... If a 2D simulation fails, the 3D simulation
     would certainly fail."
  summary: |
    GDSII→GDS2MASK 切平面后，先把关键切割平面单独跑 2D 仿真；2D 能收敛才允许进入 3D。
    这个"平面即最小验证单元"的思路把 3D 的不可调试性拆成可逐平面定位的 2D 问题。
  tags: [framework, gdsii, verification, 3d]

- id: f06
  title: 网格质量杠杆（spacing/elimine/double_mesh/extend）
  type: framework
  source_chapter: 2D 教程 P8-9,12 / 3D 教程 P5-6 / 手册 §7.20-7.21,7.24
  source_quote: |
    "Between these flag points, mesh points will be inserted with density controlled by 'spacing'.
     Smaller 'spacing' means more mesh points."（3D 教程 P5）
  summary: |
    网格密度是结构分辨率也是计算成本：spacing 控插入密度、elimine 按区域减半、
    double_mesh 局部加倍、extend 为斜注入临时外扩网格。
    思路是"该密的地方密、该稀的地方稀"，且大区域网格操作只影响指定矩形（xlo/xhi/ylo/yhi）。
  tags: [framework, mesh, resolution]

- id: f07
  title: 导出-对接链路（export → suprem_* → begin_zmater）
  type: framework
  source_chapter: 3D 教程 P35-39 / 手册 §7.23 export（PDF P211）
  source_quote: |
    "export outfile=mydevice.aps xpsize=0.0001 ... suprem_property silicon_mater=1 oxide_mater=2 poly_mater=3
     load_macro name=si mater=1 ... suprem_contact num=1 xrange=(-1.5 -1.4) side=upper touch_mater=1"
  summary: |
    工艺结构进入器件仿真的标准链路：CSuprem 用 export（xpsize/triangle.based/repair.mesh）写出 .aps；
    APSYS 用 suprem_import=yes 读入，再逐平面 begin_zmater/end_zmater 内用 suprem_property 给材料编号、
    suprem_contact 给接触编号，并与 load_macro/contact 严格对应。编号一致性是这条链路的接口契约。
  tags: [framework, export, apsys, interface]

- id: f08
  title: 掩膜驱动的差异化（mask/avoidmask/逐段刻蚀）
  type: framework
  source_chapter: 2D 教程 P15,20-21 / 手册 §7.44 mask、§7.22 etch
  source_quote: |
    "mask thick=1 x1.from=0.1 x1.to=0.5 x2.from=1 x2.to=1.2 ... etch avoidmask depth=0.5 nitride"
  summary: |
    结构差异化源自掩膜：mask 定义光刻区域，etch avoidmask 沿掩膜坡角（theta）刻蚀，
    多边形 etch start/cont/done 定义任意刻蚀形状。思考框架是"掩膜决定哪里动、刻蚀决定怎么动"。
  tags: [framework, mask, etch, pattern]

- id: f09
  title: 对称结构镜像复用（struct mirror）
  type: framework
  source_chapter: 3D 教程 P14,33 / 手册第 6 章 LDD 实例（PDF P148）
  source_quote: |
    "struct mirror left"（LDD 实例，PDF P148）
  summary: |
    对对称器件只建一半结构，仿真与网格都省一半；最终用 struct mirror 复制出完整器件。
    这是从工艺建模到器件仿真都在用的降维技巧。
  tags: [framework, symmetry, mesh]

- id: f10
  title: 语句引用契约（tag 句柄化）
  type: framework
  source_chapter: 2D 教程 P8,10 / 3D 教程 P5
  source_quote: |
    "The point can have a 'tag' to be cited in other commands."（3D 教程 P5）
  summary: |
    用 tag 给网格线/位置命名，后续 region/bound/etch 一律引用 tag 而不是硬编码坐标：
    一处改动全局生效，避免坐标不一致。这是复杂结构里可维护性的关键机制。
  tags: [framework, maintainability, tag]
