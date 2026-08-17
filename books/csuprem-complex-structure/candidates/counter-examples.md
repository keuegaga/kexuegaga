# Counter-Example Candidates — CSuprem 复杂结构设计

> cangjie-skill 阶段 1 产出（反例提取器）。候选未筛选，供阶段 1.5 三重验证与阶段 2 B（Boundary）段素材。

- id: ce01
  title: 忘记定义 exposed 表面（最常见的错误）
  type: counter-example
  source_chapter: 手册第5章 (PDF P84, P110)
  source_quote: |
    "It is important to define the top of the wafer for CSUPREM to correctly simulate these
    actions. Most mistakes are made by ignoring to define the exposed surface." / "Csuprem
    does not assume the top is exposed. Layer depositions, oxidations and impurity
    predepositions only happen on ``exposed'' surfaces, so this statement must not be omitted."
  failure_mode: |
    只写 region/init 却不写 bound exposed，沉积、氧化、预淀积全部不发生在预期表面，
    结构“看起来在”但工艺步骤静默失效。
  mechanism: |
    CSuprem 不会默认把 top 当 exposed（手册明确承认本可默认，但作者选择让用户显式声明
    boundary codes）。所有气体相关工艺（diffuse/deposit/etch）只作用于 exposed 表面，
    漏掉该语句不会报错，只会得到错误结构。
  warning_signs:
    - 输入 deck 中没有 bound exposed 语句
    - 沉积/氧化后结构没有任何变化
    - 表面工艺作用在错误的一侧（y 轴翻转问题叠加）
  bound_to:
    - "结构定义体系：line/region/bound/init"
    - "工艺步骤即结构演化"
  tags: [counter-example, structure-definition, bound, common-mistake]

- id: ce02
  title: 2D 未验证直接上 3D（必然失败）
  type: counter-example
  source_chapter: 手册第3章 (PDF P31)、第6章 (PDF P140)
  source_quote: |
    "If a 2D simulation fails, the 3D simulation would certainly fail. In such a case, it is
    easier to fix the 2D problem first." / "Since the basic idea of performing 3D is to stack
    up many 2D simulation cross sections, it is important that reasonable results are first
    obtain for at least one of the 2D cross sections."
  failure_mode: |
    直接构造 3D 工程并运行，遇到数值发散/崩溃后无从定位，因为错误可能来自任一平面、
    段间耦合或初始网格。
  mechanism: |
    3D 仿真 = 多层 2D 截面堆叠 + z 方向耦合；任何一层的 2D 网格/物理有问题，3D 必然失败，
    且 3D 的调试成本高得多。手册把“先跑通至少一个 2D 截面”当作基本前提。
  warning_signs:
    - 3D 工程里的 xy 平面文件从未单独跑过 2D
    - 第一个 3D 运行就在初期崩溃
    - 不知道问题出在哪个平面
  bound_to:
    - "2D→3D 转换方法论（先 2D 后 3D）"
    - "GDSII 直转 3D 流程"
  tags: [counter-example, 3d-conversion, validation, mesh]

- id: ce03
  title: 跳过 quasi3d 直接 full 3D
  type: counter-example
  source_chapter: 手册第3章 (PDF P30)
  source_quote: |
    "When running a 3D simulation, instead of using 'mode three.dim', it is recommened that
    you use 'mode quasi3d' first. This would let you run through all the planes quickly.
    Sometime, poor initial mesh may cause a crash and it is better to find out while you are
    still doing quasi3d."
  failure_mode: |
    直接 three.dim 全耦合运行，初始网格差导致的崩溃要等很久才发现，排错成本极高。
  mechanism: |
    quasi3d 忽略平面间耦合，能快速验证所有平面的 xy 网格与工艺序列；three.dim 全耦合
    计算量大、慢。手册建议把 quasi3d 当作廉价冒烟测试。
  warning_signs:
    - 尚未用 quasi3d 跑通就直接提交 full 3D 任务
    - 长任务跑到一半才因网格问题崩溃
  bound_to:
    - "2D→3D 转换方法论（先 quasi3d 后 three.dim）"
  tags: [counter-example, 3d-conversion, quasi3d, mesh]

- id: ce04
  title: 3D 氧化时 zplanes≠1 / 一段多平面 → 异常崩溃
  type: counter-example
  source_chapter: 3D 教程 (PDF P8)、手册第3章 (PDF P28)
  source_quote: |
    "But we fix ``zplanes'' equals 1 in Csuprem to make an uniform segment between 2 x-y
    planes, which helps preventing abnormal crash when doing simulation of ``oxidation''
    processing." / "it is usually impossible to organize the planes into segments to save
    internal memory. Therefore, we normally define one plane per each segment in CSUPREM
    documents."
  failure_mode: |
    在氧化工艺中把多个 xy 平面塞进同一 segment（zplanes>1），氧化使各平面网格移动，
    段内网格不再一致，导致内存数组冲突或异常崩溃。
  mechanism: |
    segment 的定义要求段内各平面 (x,y) 网格与材料完全相同；氧化会移动网格点、改变材料
    边界，破坏这一前提。Csuprem 的惯例是“每 segment 一个平面”。
  warning_signs:
    - zmesh.zst 中 zplanes 大于 1
    - 工艺序列包含 weto2/dryo2 氧化
    - 氧化步骤附近出现不明崩溃
  bound_to:
    - "zmesh.zst/z_structure 定义"
    - "工艺步骤即结构演化（氧化）"
  tags: [counter-example, zmesh, oxidation, crash]

- id: ce05
  title: 3D 氧化时氧化物区未跨平面耦合（漏 connect_region）
  type: counter-example
  source_chapter: 手册第7章 connect_region (PDF P196-197)
  source_quote: |
    "To allow the correct amount of oxidant diffusion, the oxide region on one plane must be
    fully coupled to the oxide region on the next plane. This may be a problem if the size and
    shape of the oxide regions are vastly different since by default, the mesh on one plane
    only connects to the mesh points nearest to it on the next plane."
  failure_mode: |
    LOCOS 等 3D 氧化中，各平面氧化区尺寸/形状差异大，默认“就近点”耦合使氧化剂无法
    平面间扩散，鸟嘴/氧化扩展被错误抑制。
  mechanism: |
    氧化过程中氧化物区会“出现、合并、消失”，默认网格连接只连最近点；必须用
    connect_region 指定参考点让整块氧化区完全耦合。参考点太少可能漏掉活跃氧化区，
    手册建议拿不准就多用点。
  warning_signs:
    - 3D LOCOS/STI 氧化没有 connect_region
    - 不同平面的氧化区形状差异大
    - 氧化层下（Si3N4 下方）横向扩展缺失
  bound_to:
    - "zmesh.zst/z_structure 段间耦合"
    - "工艺步骤即结构演化（3D 氧化）"
  tags: [counter-example, 3d-oxidation, connect_region, locos]

- id: ce06
  title: 误以为沉积/注入可以逐平面不同
  type: counter-example
  source_chapter: 手册第3章 (PDF P30)
  source_quote: |
    "Please note that deposition and implantation are the same for all planes. Only etching
    can vary from plane to plane (as a result of mask/photolithography)."
  failure_mode: |
    2D→3D 转换时给不同平面写不同的 deposit/implant 命令，得到非预期结构或命令被忽略。
  mechanism: |
    3D 中默认只有刻蚀能按 segm= 逐平面变化；沉积与注入对所有平面一致。手册的转换步骤
    只要求复制 etch 命令（加 segm=），deposit/implant 保持全局。
  warning_signs:
    - 为每个平面单独写 deposit/implant 块
    - 平面间沉积/注入条件不一致
  bound_to:
    - "2D→3D 转换方法论"
    - "工艺步骤即结构演化"
  tags: [counter-example, 3d-conversion, deposit, implant]

- id: ce07
  title: 3D 转换时 etch 命令没有逐平面复制 segm=
  type: counter-example
  source_chapter: 手册第3章 (PDF P29-30)
  source_quote: |
    "Make 2 copies of each etch command and append segm=1,2,3 to all the etch commands,
    respectively. For example: etch oxide all will be converted to etch oxide all segm=1,
    etch oxide all segm=2, etch oxide all segm=3."
  failure_mode: |
    2D deck 转 3D 后只保留一条 etch，结果只有一个平面被刻蚀，或所有平面共用同一个
    刻蚀形状，得不到预期的 3D 结构。
  mechanism: |
    etch 的默认 segm=-1 作用于全部平面；要表达逐平面变化的刻蚀，必须为每个平面显式
    复制一条带 segm=N 的命令。这是 2D→3D 转换手册步骤的第 3 步。
  warning_signs:
    - 2D→3D 后 etch 命令数量仍与 2D 相同
    - 期望逐平面变化的刻蚀形状没有出现
  bound_to:
    - "2D→3D 转换方法论"
    - "刻蚀方法论（etch 命令）"
  tags: [counter-example, 3d-conversion, etch, segm]

- id: ce08
  title: 续跑 stalled 3D 时 restart 命令位置错误
  type: counter-example
  source_chapter: 手册第3章 (PDF P29)
  source_quote: |
    "Restarting a stalled quasi3d or 3D simulation is similar to that for 2D. The only
    difference is that the restart command should be placed right after the 3d_mesh command
    to get the z-plane information."
  failure_mode: |
    3D 续跑时把 restart 放在别处（如 3d_mesh 之前或工艺命令之后），程序没有 z 平面信息，
    续跑失败或结构错乱。
  mechanism: |
    3D 网格信息由 3d_mesh 加载各 xy 平面文件而来；restart 必须紧跟其后才能正确恢复
    z 方向结构，再跳转到 .str 位置继续。
  warning_signs:
    - 3D 续跑 deck 中 restart 与 3d_mesh 不相邻
    - 续跑后结构/结果与中断前不一致
  bound_to:
    - "3D 结构定义与续跑"
    - "2D→3D 转换方法论"
  tags: [counter-example, restart, 3d-conversion, 3d_mesh]

- id: ce09
  title: 设备文件 2D→3D 漏掉 z_structure 复制与 begin_zmater 分组
  type: counter-example
  source_chapter: 手册第3章 (PDF P30-31)
  source_quote: |
    "define the position of the z-planes by copying all the z_structure commands from
    zmesh.zst in the project folder of 3D process simulation to the .sol file" / "You need
    to make one set of ``begin_zmater .... end_zmater'' for each plane since there may be
    variation from plane to plane. For example, some planes may have contacts while others
    may not."
  failure_mode: |
    把 2D .sol 转 3D 时只加 3d_solution_method，却漏了 z_structure 平面定义或不按平面
    分组 begin_zmater，导致平面位置缺失/材料接触错配。
  mechanism: |
    3D 设备仿真需要：3d_solution_method 3d_flow=yes → 从 zmesh.zst 复制全部 z_structure →
    suprem_property/load_macro/suprem_contact/contact 按平面包进 begin_zmater/end_zmater。
    每平面一组，因为平面间接触/材料可能不同。
  warning_signs:
    - .sol 中 z_structure 数量与 zmesh.zst 不一致
    - 所有平面共用同一组材料/接触定义但结构不同
  bound_to:
    - "3D→APSYS 对接（suprem_property/suprem_contact/begin_zmater）"
    - "2D→3D 转换方法论"
  tags: [counter-example, apsys-link, z_structure, zmater]

- id: ce10
  title: 材料/接触编号不一致（suprem_property ↔ load_macro ↔ contact）
  type: counter-example
  source_chapter: 3D 教程 (PDF P37-38)
  source_quote: |
    "material names and numbers defined by ``load_macro'' commands must be accordance with
    those defined by ``suprem_property'' command." / "Please note that the ``num'' in
    ``contact'' should be same as that in ``suprem_contact''."
  failure_mode: |
    suprem_property 里 silicon=1、load_macro 里却把 si 编成 2，或 suprem_contact num=1
    与 contact num=2 不一致，导入 APSYS 后材料属性/接触作用在错误对象上。
  mechanism: |
    CSuprem 导出的 .aps 结构靠编号对接 APSYS：材料号必须与 load_macro 一致、接触号必须
    suprem_contact 与 contact 一致。编号错位不会在导入时报错，而是静默产生错误器件。
  warning_signs:
    - suprem_property 与 load_macro 的 mater 值对不上
    - suprem_contact 与 contact 的 num 对不上
    - 器件仿真中电极/材料行为反常
  bound_to:
    - "3D→APSYS 对接（编号一致性）"
  tags: [counter-example, apsys-link, numbering, load_macro]

- id: ce11
  title: 混淆 contact 与 metal material
  type: counter-example
  source_chapter: 手册第3章 (PDF P30-31)
  source_quote: |
    "Please note there is a difference between ``metal material'' and ``contact.''
    ``Contact'' here means pure geometric boundary condition while a metal material means a
    real material with properties such as resistivity and work function."
  failure_mode: |
    把 contact 当成实际金属层（或反过来把金属层当接触），忽略电阻率/功函数，电极电学
    行为与实物不符。
  mechanism: |
    APSYS 对接语境中 contact 只是几何边界条件；metal material 才带材料属性。二者职责
    不同，不能混用。
  warning_signs:
    - 讨论电极时只提到 contact 而没有金属材料定义
    - 需要金属电阻/功函数效应却只给了 contact
  bound_to:
    - "3D→APSYS 对接"
  tags: [counter-example, apsys-link, contact, metal]

- id: ce12
  title: GDSII 直转 3D，却把瓶颈误判为版图切割
  type: counter-example
  source_chapter: 手册第3章 (PDF P31)
  source_quote: |
    "In many cases, the bottleneck is not how good the cuts are made in the GDSII files, but
    the construction of a reasonable 2D mesh for the planes used in the simulation. Ideally,
    we recommend at least some of the planes cut from GDSII pass a 2D simulation test before
    submitting for a 3D simulation job."
  failure_mode: |
    花大量精力调 GDS2MASK 切割参数，3D 仍发散/失败——真正的问题在某个平面的 2D 网格
    不合理。
  mechanism: |
    GDS2MASK 只是自动切平面+生成 zmesh.zst；平面的网格质量决定 3D 成败。手册明确建议
    至少部分 GDSII 切出的平面先过 2D 仿真测试。
  warning_signs:
    - GDSII 平面从未单独 2D 验证
    - 反复调切割参数但 3D 依旧失败
  bound_to:
    - "GDSII 直转 3D（GDS2MASK）"
    - "2D→3D 转换方法论"
  tags: [counter-example, gds2mask, gdsii, mesh]

- id: ce13
  title: 忘记 taper 默认关闭：不同尺寸 segment 只“垂直接触”
  type: counter-example
  source_chapter: 手册第3章 (PDF P28)
  source_quote: |
    "When mesh points couple between segment perpendicularly, we call it having no taper.
    If the points couple with an angle, we define it as coupling with taper. By default, no
    taper connect is used by the simulation program. Suppose segment A has x=(0 5) and B has
    x=(0 6). By default ... for segment B, only mesh points from 0 to 5 are coupled to
    segment A."
  failure_mode: |
    期望相邻不同尺寸 segment 自动斜连成真实 3D 形貌，实际默认只做垂直接触，超出部分
    完全不耦合。
  mechanism: |
    taper（斜向连接）不是默认行为；需要在 z_structure 中用 taper 参数显式开启。未开时
    段间仅按最近网格点垂直接触。
  warning_signs:
    - 相邻 segment 的 xy 尺寸不同却没有 taper 参数
    - 3D 形貌出现阶梯而非斜面
  bound_to:
    - "zmesh.zst/z_structure（segment/plane/taper/bend）"
  tags: [counter-example, zmesh, taper, segment]

- id: ce14
  title: 升温速率单位混淆（°/s vs 时间单位分钟）
  type: counter-example
  source_chapter: 手册第7章 diffuse (PDF P202)
  source_quote: |
    "One should be careful about the units of the ramp rates since many use degree per second
    while the time here is in minutes. By default, this parameter is not used and diffuse
    means constant temperature annealing."
  failure_mode: |
    按习惯写 ramp_rate 为 °/s，但 diffuse 的 time 是分钟，实际升温曲线偏差几个数量级。
  mechanism: |
    ramp_rate=(final_temp-temp)/time 的 time 是分钟；用户常按 °/s 直觉给值，导致升温
    过快或过慢。手册提醒换算单位。
  warning_signs:
    - ramp 参数来自 °/s 习惯
    - 升温结果与预期曲线明显不符
  bound_to:
    - "工艺步骤即结构演化（diffuse 退火/氧化）"
  tags: [counter-example, diffuse, units, ramp]

- id: ce15
  title: continue 续跑扩散时重置关键状态
  type: counter-example
  source_chapter: 手册第7章 diffuse (PDF P203)
  source_quote: |
    "This specifies a continuing diffusion. Do not reset the total time to 0, do not reset
    the analytic oxide thickness to the default value of ``initial'' on the oxide command,
    and do not initialize the defects."
  failure_mode: |
    用 continue 续跑多步扩散时把总时间清零、把氧化层厚度重置为 initial、或重新 init
    缺陷，导致前序扩散/氧化状态丢失。
  mechanism: |
    continue 的含义是“延续上一步的扩散”，总时间、氧化物厚度、缺陷分布都应是累积状态；
    重置任何一项都会让结果从头算或状态错乱。
  warning_signs:
    - 续跑语句中出现 time=0 或 oxide initial
    - 续跑后缺陷/氧化历史消失
  bound_to:
    - "工艺步骤即结构演化（diffuse 多步退火）"
  tags: [counter-example, diffuse, continue, state]

- id: ce16
  title: 一次扩散步骤指定多种气体
  type: counter-example
  source_chapter: 手册第7章 diffuse (PDF P202)
  source_quote: |
    "Only one gas type may be specified per diffusion step. There is currently no difference
    between nitrogen, argon, and ammonia."
  failure_mode: |
    在同一条 diffuse 里同时开 dry/wet/氮气等多种气体，命令行为未定义/按单气体处理，
    气氛与预期不符。
  mechanism: |
    手册规定每次扩散只能指定一种气体类型；多气氛应拆成多条 diffuse 步骤。
  warning_signs:
    - 单条 diffuse 含多个气体开关
    - 期望混合气氛却得到单一气体结果
  bound_to:
    - "工艺步骤即结构演化（diffuse 气氛控制）"
  tags: [counter-example, diffuse, gas, syntax]

- id: ce17
  title: 气体流量与分压换算错误
  type: counter-example
  source_chapter: 手册第7章 diffuse (PDF P202-203)
  source_quote: |
    "In many process flow description, the gas flow of different gas species are defined
    instead of partial pressure. In such as case, one needs to use the following formula to
    convert gas flow rate into oxidant partial pressure: partial_oxidant_pressure =
    furnace_total_pressure x O2_or_H2O_flow_rate / (O2_or_H2O_flow_rate + other_flow_rate)."
  failure_mode: |
    工艺卡给的是气体流量，却直接把流量当压力（或忽略总压），氧化速率/分压错误。
  mechanism: |
    diffuse 的 pressure 是活性物种分压（默认 1 atm）；流量描述必须先按总压与各气体
    流量换算分压，否则 wet/dry 氧化速率偏差。
  warning_signs:
    - 输入来自气体流量而非分压
    - 氧化厚度与预期系统性偏差
  bound_to:
    - "工艺步骤即结构演化（氧化）"
    - "材料与模型（氧化模型）"
  tags: [counter-example, diffuse, pressure, units]

- id: ce18
  title: 擅自修改 suprem.key / Modelrc / sup4gs.imp
  type: counter-example
  source_chapter: 手册第2章 (PDF P24)
  source_quote: |
    "This file contains the actual commands used by the current version of Csuprem. The
    program reads this file every time it runs. ... IMPORT: please do not revise this file or
    Csuprem may not run." / "It is advised that revision of this Modelrc file be reserved for
    Csuprem experts."
  failure_mode: |
    为“加命令/改默认参数”直接编辑 suprem.key、Modelrc 或 sup4gs.imp，导致程序无法启动
    或所有仿真默认值被污染。
  mechanism: |
    suprem.key 是当前版本命令表（每次运行都读）；Modelrc/sup4gs.imp 是物理默认参数。
    三者都是全局关键文件，改错影响所有工程且难以排查。
  warning_signs:
    - 想“加参数”先想到改 suprem.key
    - 修改后其他工程行为全部改变
  bound_to:
    - "安装与文件结构"
    - "材料与模型（默认模型参数）"
  tags: [counter-example, install, suprem.key, modelrc]

- id: ce19
  title: GUI 异常时不用命令行实时输出调试
  type: counter-example
  source_chapter: 手册第2章 (PDF P25)
  source_quote: |
    "If the GUI is bothering you or not functioning due to installation problems, you can
    always go back to the basics and use the MS-DOS prompt. ... It is always recommended to
    use MS-DOS prompt as a debug tool if there is something wrong with the simulation program,
    since it will always give you the real time display of what is going on."
  failure_mode: |
    仿真异常时只看 GUI 报错/日志文件，拿不到实时输出，无法定位是哪条命令、哪一步发散。
  mechanism: |
    MS-DOS/Linux shell 直接运行 csuprem.exe 会实时显示每一步运行信息，是作者推荐的
    调试入口；GUI 反而遮蔽了这些信息。
  warning_signs:
    - 报错信息不完整
    - 不知道崩溃发生在哪条命令
  bound_to:
    - "运行与调试"
  tags: [counter-example, debugging, cli, gui]

- id: ce20
  title: 以为 etch 会“仿真出”刻蚀形状
  type: counter-example
  source_chapter: 手册第7章 etch (PDF P209)
  source_quote: |
    "The etch shape can be described in several different ways. The user must specify the
    final shape of the region to be etched, there is no capability at present to simulate the
    etch region shape."
  failure_mode: |
    只给 etch 一个“刻蚀意图”（如某深度某材料），期待程序自己演化出沟槽形状；实际
    必须逐点描述最终形状，否则刻蚀结果错误。
  mechanism: |
    CSuprem 的 etch 是几何操作：left/right 直线、start/cont/done 多边形、dry 复制表面、
    avoidmask 掩膜角、physical 按材料速率，全部要求用户指定最终区域形状，没有形状演化
    求解能力。
  warning_signs:
    - 只给了材料+深度就想得到任意截面
    - 没有指定 p1/p2 或 start/cont/done 顶点序列
  bound_to:
    - "刻蚀方法论"
  tags: [counter-example, etch, geometry, capability]

- id: ce21
  title: avoidmask 刻蚀前未先定义 mask
  type: counter-example
  source_chapter: 2D 教程 (PDF P20)
  source_quote: |
    "etch avoidmask depth=0.9 nitride — Must follow mask"
  failure_mode: |
    直接发 etch avoidmask 而没有前置 mask 命令，程序没有掩膜几何信息，刻蚀角度/形状
    无法计算。
  mechanism: |
    mask 命令会存储掩膜几何（x.from/x.to/theta 等）供后续 etch 使用；avoidmask 沿掩膜
    边缘按角度向下刻蚀，必须先有 mask 定义。
  warning_signs:
    - 使用 avoidmask 或 physical 前没有 mask 命令
    - 掩膜边缘刻蚀形状缺失
  bound_to:
    - "刻蚀方法论（avoidmask）"
  tags: [counter-example, etch, avoidmask, mask]

- id: ce22
  title: 混淆 ion 与 impurity、新杂质乱用已有名字
  type: counter-example
  source_chapter: 手册第4章 (PDF P38)
  source_quote: |
    "Please note the use of ``ion'' and ``impurity''. The former refers to the ion
    implantation profile model while the latter to the diffusion model. For example, BF2 is
    implanted as ion BF2 but diffused as B." / "New impurites not implemented in CSuprem
    should use generic, iigeneric, iiigeneric, ivgeneric and vgeneric."
  failure_mode: |
    用错误离子/杂质索引（如把 BF2 当扩散物种、或把未实现杂质硬套在硅/磷上），注入或
    扩散模型参数全部错位。
  mechanism: |
    注入模型按“ion”查 sup4gs.imp 表，扩散模型按“impurity”查扩散参数，二者索引独立；
    新杂质必须用 generic 系列扩展，不能占用已知杂质索引。
  warning_signs:
    - 注入与扩散物种混用同一索引
    - 新掺杂剂直接套用硅/砷等既有名字
  bound_to:
    - "材料与模型（注入/扩散模型）"
  tags: [counter-example, implant, impurity, doping]

- id: ce23
  title: 同一条命令的参数跨行放置
  type: counter-example
  source_chapter: 手册第5章 (PDF P90)
  source_quote: |
    "A remark ``#continued'' is used to indicate that an original long command line has been
    broken and continued onto the next line for the purpose of this document. In a simulation
    input file, all parameters belonging to the same command should be planced within a single
    command line."
  failure_mode: |
    把文档里为了排版拆行的命令原样复制进输入文件（带 #continued），参数被截断，命令
    解析失败或参数丢失。
  mechanism: |
    文档中的 #continued 只是排版标注，不是合法续行语法；输入文件里一条命令必须在一行。
  warning_signs:
    - deck 中出现 #continued
    - 复制手册长命令后报解析错误
  bound_to:
    - "输入文件语法"
  tags: [counter-example, syntax, input-deck]

- id: ce24
  title: 直接改氧化模型中的 henry.coeff / theta
  type: counter-example
  source_chapter: 手册第7章 oxide (PDF P269)
  source_quote: |
    "Henry's coefficient is the solubility of oxidant in material 1 at one atmosphere ...
    Theta is the number of oxygen atoms incorporated in a cubic centimeter of oxide. Note:
    Don't change these unless you really know what you are doing. Change the Deal-Grove
    coefficients instead."
  failure_mode: |
    为调氧化速率直接改亨利系数/氧原子数，氧化速率、体积膨胀比与物理意义全部破坏。
  mechanism: |
    henry.coeff/theta 是溶解度与氧原子密度等底层物理量，与 Deal-Grove 系数（扩散/界面
    反应）纠缠；作者明确建议调 Deal-Grove 系数而非这些常数。
  warning_signs:
    - 调氧化行为时先动 henry.coeff/theta
    - 氧化厚度变化方式不符合物理
  bound_to:
    - "材料与模型（氧化模型）"
  tags: [counter-example, oxidation, model-params]

- id: ce25
  title: 以为 movie 输出间隔可由用户直接指定
  type: counter-example
  source_chapter: 手册第5章 (PDF P91)
  source_quote: |
    "Please note that the time step in a movie plot is determined by the solver according to
    the initial time step in method command, convergence condition in the diffuse command.
    To achieve control of time interval of concentration profile plotting, you may experiment
    with different settings of initial time interval and maximum time step."
  failure_mode: |
    想固定每隔 Δt 输出一帧浓度剖面，结果输出间隔完全不由自己控制。
  mechanism: |
    movie 在每个求解器时间步开头执行；时间步由 method 初始步长与 diffuse 收敛条件决定，
    只能通过调整初始/最大时间步间接控制输出密度。
  warning_signs:
    - 期望精确等间隔的 movie 帧
    - 输出的剖面时间点不规律
  bound_to:
    - "工艺步骤即结构演化（扩散）"
  tags: [counter-example, diffuse, movie, output]

- id: ce26
  title: zmesh.zst 位置/格式错误（必须与主输入同目录、固定格式）
  type: counter-example
  source_chapter: 手册第2章 (PDF P24)、3D 教程 (PDF P9)
  source_quote: |
    "For 3D-simulation, the mesh planes positions in the z-direction are defined in a file
    named zmesh.zst. It must be located in the same directory as the main input file." /
    "output sol_outf=tmp.out / export_3dgeo file=h_cvd.3dgeo — These 2 lines are of fixed
    format, please do not modify them."
  failure_mode: |
    把 zmesh.zst 放在别的目录、改名，或修改其中的固定输出行，3D 网格生成失败/无结构
    输出。
  mechanism: |
    zmesh.zst 是固定文件名、必须与主输入同目录，由 geo3d.exe 自动引用；文件内 output/
    export_3dgeo 两行是固定格式，教程明确禁止修改。
  warning_signs:
    - zmesh.zst 不在主输入同目录
    - 修改了 zmesh.zst 中的固定行
  bound_to:
    - "zmesh.zst/z_structure 定义"
    - "3D 文件结构"
  tags: [counter-example, zmesh, file-layout]

- id: ce27
  title: eliminate/double_mesh 区域超出 region 范围
  type: counter-example
  source_chapter: 手册第7章 eliminate (PDF P208)
  source_quote: |
    "These are the low and high coordinates of an area within which mesh elimination is to
    happen. Please note that this area should be within the region as defined by the region
    command."
  failure_mode: |
    eliminate/double_mesh 指定的矩形区域超出 region 定义范围，网格操作作用于意外区域
    或无效。
  mechanism: |
    网格控制命令按矩形区域选择网格线；区域必须落在 region 材料区内，越界会造成网格
    密度错误。
  warning_signs:
    - xlo/xhi/ylo/yhi 与 region 边界不一致
    - 加密/粗化后网格出现在错误位置
  bound_to:
    - "网格管理（eliminate/double_mesh）"
  tags: [counter-example, mesh, eliminate, region]

- id: ce28
  title: 3D 注入忽略 lateral.angle（z 平面不垂直掩膜边）
  type: counter-example
  source_chapter: 手册第7章 3d.implant.method (PDF P168-169)
  source_quote: |
    "This command should be used if the z-plane is not perpendicular to the implant mask edge
    but makes a 30 degree angle with the plane normal to the mask edge."
  failure_mode: |
    3D 结构 z 平面与掩膜边缘不垂直时按默认处理，横向注入散射/阴影方向错误。
  mechanism: |
    lateral.angle 定义 z 平面与掩膜边法向的夹角，决定 3D 注入的横向散射修正；不设该
    角度，斜切结构下的注入分布失真。
  warning_signs:
    - z 平面与掩膜边不垂直且无 lateral.angle
    - 3D 注入分布与 2D 截面不对称
  bound_to:
    - "3D 注入建模"
  tags: [counter-example, implant, 3d, lateral-angle]

- id: ce29
  title: 沉积到凹坑/台阶结构时水平网格继承失效
  type: counter-example
  source_chapter: 手册第7章 deposit (PDF P200)
  source_quote: |
    "On a flat surface, deposited layer lets the mesh line to extend upwards from the mesh
    layer below and the horizontal mesh spacing inheritates from below. Such extension is not
    possible is deposit is performed to fill a dent between two horizontal step structures.
    In such a case, a curved surface is formed between the two steps and this mesh spacing
    takes effect on the curved outer surface."
  failure_mode: |
    在台阶/凹坑上沉积时仍指望网格像平面沉积那样从下层继承，曲面外沿网格过疏或过密，
    后续工艺失真。
  mechanism: |
    平面沉积可垂直延伸并继承下方水平网格；填充台阶间凹坑会形成曲面，水平间距由 space
    参数控制，需要显式设置。
  warning_signs:
    - 非平面表面沉积未设 space
    - 填充凹坑后曲面网格异常
  bound_to:
    - "工艺步骤即结构演化（沉积）"
    - "网格管理"
  tags: [counter-example, deposit, mesh, space]

- id: ce30
  title: rectangle.based 沉积时初始网格过密且未控制
  type: counter-example
  source_chapter: 手册第7章 rectangle_deposit_method (PDF P282-283)
  source_quote: |
    "The initial normal mesh play an important role for the final deposit layer. ... Sometimes
    the mesh points on the surface lines are too dense, which caused smaller distance between
    points in x direction." / "If the space between two adjacent points is less than
    min_delta_x in the x direction, then it will be set as min_delta_x. In order to apply this
    funtion, one must set x.auto=false."
  failure_mode: |
    rectangle.based 沉积得到的沉积层网格畸变，因为表面线上网格点过密导致 x 向间距过小，
    min_delta_x 又因 x.auto 默认 true 而失效。
  mechanism: |
    rectangle_deposit_method 用初始矩形网格“先建后蚀”生成沉积层；表面线过密会形成不
    合理初始网格，必须配合 rectangle_deposit_mesh 定义 xy 网格，并关掉 x.auto 才能让
    min_delta_x 生效。
  warning_signs:
    - 沉积层内网格过密/畸形
    - 设了 min_delta_x 却没设 x.auto=false
  bound_to:
    - "工艺步骤即结构演化（沉积）"
    - "网格管理"
  tags: [counter-example, deposit, rectangle-based, mesh]

- id: ce31
  title: contour 在 plot.2d 之前调用
  type: counter-example
  source_chapter: 手册第7章 contour (PDF P197-198)
  source_quote: |
    "This statement assumes a plot.2d has been specified and the screen has been set up for
    plotting a two dimensional picture. If this has not been done, the routine will probably
    produce garbage on the screen." / "This should probably check to make sure a plot.2d has
    been done. It is conceivable that this statement could produce floating point exceptions
    when a plot.2d has not been done."
  failure_mode: |
    未先 plot.2d 就 contour，输出垃圾图形甚至浮点异常（作者在 Bugs 段承认）。
  mechanism: |
    contour 依赖 plot.2d 建立的绘图坐标系与网格；缺少前置绘图设置时例程行为未定义。
  warning_signs:
    - 脚本中 contour 前没有 plot.2d
    - 等值线图形异常或程序崩溃
  bound_to:
    - "绘图与后处理"
  tags: [counter-example, plot, contour, order]

- id: ce32
  title: 忽略“Y 轴翻转”约定导致结构上下颠倒
  type: counter-example
  source_chapter: 2D 教程 (PDF P10)
  source_quote: |
    "Note: Y axis is flipped. region silicon xlo=lft xhi=rht ylo=top yhi=bot / bound exposed
    xlo=lft xhi=rht ylo=top yhi=top / bound backside xlo=lft xhi=rht ylo=bot yhi=bot"
  failure_mode: |
    按直觉把 y=0 当底部，region/bound 上下颠倒，exposed 表面跑到衬底侧。
  mechanism: |
    CSuprem 约定 y 轴翻转：top 通常位于 y=0、bot 位于大 y，bound exposed 在 top。
    教程明确标注该约定，忽略它则所有表面工艺作用位置错误（常与漏 bound 叠加）。
  warning_signs:
    - 用 y=0 表示衬底底部
    - exposed 定义在 yhi 一侧
  bound_to:
    - "结构定义体系：line/region/bound/init"
  tags: [counter-example, structure-definition, y-axis, convention]
