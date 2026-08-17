# Glossary Candidates — CSuprem 复杂结构设计建模

> 由主流程按 glossary-extractor.md 串行提取（降级方案）。英文原文引用均来自 _source/ 提取文本。

- id: g01
  term: line / tag / spacing
  type: term
  source_chapter: 3D 教程 P5 / 2D 教程 P8
  author_definition: |
    "'line' command is used to specify a flag point in x or y direction. The point can have a 'tag'
     to be cited in other commands. Between these flag points, mesh points will be inserted with
     density controlled by 'spacing'. Smaller 'spacing' means more mesh points."
  key_distinction: |
    ≠ 结构线/几何边界：line 是网格控制点。
    tag ≠ 普通名称：是供 region/bound/etch 引用的句柄。
    spacing ≠ 线间距：是两点间插入密度（越小越密）。
  why_it_matters: 全部结构语句都建立在 line/tag/spacing 之上，误读会导致网格或引用错误。
  tags: [term, mesh, core]

- id: g02
  term: region
  type: term
  source_chapter: 2D 教程 P10 / 3D 教程 P6
  author_definition: |
    "'region' command specifies a type of material (silicon here) in a rectangular region defined
     by 'xlo','xhi','ylo' and 'yhi', here 'tag' of flag point is used."
  key_distinction: |
    ≠ 任意多边形区域：region 必须是网格线围成的矩形（xlo/xhi/ylo/yhi）。
    材料通过 region 赋予，一个区域一种材料。
  why_it_matters: 复杂结构 = 多个 region 的并集；矩形约束决定了要先规划网格线。
  tags: [term, structure]

- id: g03
  term: bound（exposed / backside / reflecting）
  type: term
  source_chapter: 2D 教程 P10
  author_definition: |
    "Exposed: deposition, etch, oxidation, defect recombination and generation.
     Backside: defect recombination and generation. Reflecting: lateral implant scattering mirrors."
  key_distinction: |
    ≠ 普通"边界条件"：bound 决定哪些工艺步骤作用在该面（exposed 参与工艺、backside 只做缺陷复合、
    reflecting 是注入散射镜像）。漏设 exposed 是教程点名的常见错误。
  why_it_matters: 边界类型直接决定工艺步骤是否作用于该面，影响结构演化。
  tags: [term, boundary]

- id: g04
  term: init / orient
  type: term
  source_chapter: 2D 教程 P11
  author_definition: |
    "init boron conc=1.0e16 [orient=100]. orient: substrate crystal orientation, default 100.
     init sets up grid and background doping level."
  key_distinction: |
    ≠ 初始化"变量"：init 建立衬底网格+背景掺杂（已激活）；orient 决定晶向（默认 100）。
  why_it_matters: 每个仿真从 init 开始，衬底掺杂/晶向影响注入与扩散。
  tags: [term, substrate]

- id: g05
  term: deposit（thick / div / space / conc）
  type: term
  source_chapter: 2D 教程 P13-14 / 手册 §4.2（PDF P32-33）
  author_definition: |
    "deposit oxide thick=1 meshlayer=2 ... deposit poly thick=0.500 div=10 phos conc=1.0e19.
     divisions controls the number of vertical grid spacings in the deposited region ... space
     represents the average spacing between points along the outside edge."
  key_distinction: |
    ≠ 物理淀积形貌：CSuprem 只有纯几何淀积。
    div/space 是淀积区网格控制，conc 可淀积掺杂层（如多晶硅）。
  why_it_matters: 淀积是"长材料"的唯一手段；网格参数影响后续刻蚀/注入精度。
  tags: [term, deposit]

- id: g06
  term: etch（left/right/start/cont/done/dry/avoidmask/physical/segm）
  type: term
  source_chapter: 2D 教程 P16-21 / 手册 §7.22（PDF P208-211）
  author_definition: |
    "etch start x=0.2 y=-2 oxide; etch cont x=0.2 y=0.5; etch done x=1 y=-1
     ... etch dry thick=0.1 ... etch avoidmask depth=0.5 ... physical: specify the etch speed
     in different materials, e.g. speed parameter r.silicon."
  key_distinction: |
    left/right = 以 p 点连线为界的直线刻蚀；start/cont/done = 多边形顶点序列；
    dry = 按厚度垂直下切；avoidmask = 沿掩膜坡角；physical = 按材料速率；segm = 指定 3D 平面。
  why_it_matters: 刻蚀是复杂结构设计的主要工具，模式选择决定形貌。
  tags: [term, etch]

- id: g07
  term: mask / avoidmask
  type: term
  source_chapter: 2D 教程 P15,20-21 / 手册 §7.44
  author_definition: |
    "mask thick=1 x1.from=0.1 x1.to=0.5 x2.from=1 x2.to=1.2 ... etch avoidmask depth=0.9 nitride
     Must follow mask."
  key_distinction: |
    mask 定义光刻窗口（可多窗口、可带 right.theta 坡角）；avoidmask 是"沿掩膜刻蚀"的 etch 模式，
    必须先执行 mask。
  why_it_matters: 掩膜是结构差异化的来源，avoidmask 还原坡角形貌。
  tags: [term, mask]

- id: g08
  term: mode（quasi3d / three.dim）
  type: term
  source_chapter: 3D 教程 P11 / 手册 §3.3.2（PDF P30）
  author_definition: |
    "This command tells simulator the dimensionality and if to consider interaction between
     x-y planes (three.dim) or not to (quasi3D) for 3D simulation."
  key_distinction: |
    quasi3d 忽略平面间耦合（快、用于验证）；three.dim 全耦合（正式计算）。不是开关精度，是耦合模型。
  why_it_matters: 3D 流程按"quasi3d 先行、three.dim 收尾"使用。
  tags: [term, 3d, mode]

- id: g09
  term: zmesh.zst / z_structure（zseg_num / zplanes / uniform_zseg_from/to / taper）
  type: term
  source_chapter: 3D 教程 P8-9 / 手册 §3.4（PDF P31）
  author_definition: |
    "'z_structure' command is used to specify position of a x-y plane ... x-y planes are numbered
     by 'zseg_num' and located by 'uniform_zseg_from' and 'uniform_zseg_to'. 'zplanes' tells how
     many times this x-y plane will be repeated before next x-y plane."
  key_distinction: |
    zmesh.zst 是 3D 结构在 z 方向的定义文件（固定名）；z_structure 是唯一需要用户细看的命令；
    taper/bend_xy_plane/cylindrical 分别表达斜面/弯曲/旋转。
  why_it_matters: 3D 与 2D 的全部差异集中在这里；改错就是结构错位。
  tags: [term, 3d, zmesh]

- id: g10
  term: GDS2MASK
  type: term
  source_chapter: 手册 §3.5（PDF P31）
  author_definition: |
    "It makes sense to use the GDS2MASK utility for 3D simulation because the utility automatically
     cuts up the layout into multiple planes and produces the zmesh.zst file for 3D simulation."
  key_distinction: |
    ≠ 直接导入版图跑 3D：GDS2MASK 把版图切成平面+生成 zmesh.zst；瓶颈在平面 2D 网格质量。
  why_it_matters: 真实芯片 3D 建模的自动入口，但必须先做平面 2D 验证。
  tags: [term, gdsii, 3d]

- id: g11
  term: struct / mirror / export
  type: term
  source_chapter: 3D 教程 P9,14,33 / 手册 §7.23（PDF P211-212）
  author_definition: |
    "struct mirror left ... export outfile=mydevice.aps xpsize=0.0001"
  summary: |
    struct 保存/镜像结构（outf=、mirror left）；export 把网格与掺杂写为 APSYS 可读的 .aps
    （xpsize 控制材料边界间隙、triangle.based 控制加点方式、repair.mesh 导出前修网格）。
  key_distinction: |
    export ≠ struct：struct 是 CSuprem 自身存档，export 是跨软件接口。
  why_it_matters: 工艺→器件仿真的唯一出口，参数影响导入后的网格质量。
  tags: [term, export, interface]

- id: g12
  term: suprem_property / suprem_contact / begin_zmater
  type: term
  source_chapter: 3D 教程 P37-38
  author_definition: |
    "suprem_property command gives a number for each material ... suprem_contact command specifies
     position and size of a contact for the imported Csuprem structure ... begin_zmater and end_zmater
     pack some statements to specify physical and structural information in the x-y planes."
  key_distinction: |
    三者必须与 load_macro/contact 编号严格对应；begin_zmater/end_zmater 按平面（zseg_num）分组，
    不同平面可定义不同接触（如只给 MOSFET 区加栅极接触）。
  why_it_matters: 3D 器件仿真的对接口，编号错=静默映射错。
  tags: [term, apsys, interface]
