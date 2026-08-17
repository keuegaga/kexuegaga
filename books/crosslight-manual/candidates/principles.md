# Principle Candidates — Crosslight 通用手册

> cangjie-skill 阶段 1 产出（原则提取器）。候选未筛选，供阶段 1.5 三重验证。

- id: p01
  title: 激射后必须电流偏置
  type: principle
  source_chapter: 手册第4章 (P78)
  source_quote: |
    "Once threshold is reached, the carrier concentration and Fermi-level splitting at the
    junction are pinned by the large stimulated recombination term. It is almost impossible
    to apply any voltage bias ... without disturbing the solution."
  summary: |
    激光器阈值以上，受激复合把结处载流子与准费米能级分裂钳死，任何电压微扰都会破坏解。
    因此激射条件下只能用电流控制偏置；电压扫描应止于阈值附近（80-90% 内建电压或 auto_finish）。
  tags: [bias, laser, principle]

- id: p02
  title: auto_finish=rtgain 是开启光子耦合前的强制初始化步骤
  type: principle
  source_chapter: 手册第4章 (P78-79) / 第22章 (P446-447)
  source_quote: |
    "It is therefore required that the scan preceding the introduction of the photon coupling
    use the auto_finish=rtgain condition to terminate."
  summary: |
    PICS3D 中，任何 solve_rtg=yes 之前必须有以 auto_finish=rtgain 终止的扫描，为纵向模式与
    光子密度提供初始猜测。缺少这一步，开启光子耦合后 Newton 求解几乎必然失败。
  tags: [pics3d, rtg, bias, rule]

- id: p03
  title: 开启 solve_rtg 后必须用小偏置步长
  type: principle
  source_chapter: 手册第22章 (P447)
  source_quote: |
    "Once photon coupling is turned on, the user must take care to always use small bias steps
    since the solution state will shift strongly as the threshold region is crossed."
  summary: |
    越过阈值时激射模光子密度增长多个数量级，即使载流子被钳位，解也剧烈变化。solve_rtg=yes
    的扫描要用 init_step 1e-5~1e-4 级别的小步长，避免大步长越过阈值导致发散。
  tags: [pics3d, convergence, rule]

- id: p04
  title: 默认材料宏文件绝不要修改
  type: principle
  source_chapter: 手册第3章 (P60)
  source_quote: |
    "it is STRONGLY recommended that the default macro files not be altered in any way since
    that would affect all the simulations that use these default files."
  summary: |
    crosslight.mac / more.mac 是全局默认材料库，改动会静默影响所有仿真。自定义材料必须走
    use_macrofile 或输入文件内覆盖语句。
  tags: [material, macro, rule]

- id: p05
  title: 绝缘宏下隧穿与碰撞电离失效，需用宽禁带半导体宏替代
  type: principle
  source_chapter: 手册第4章 (P84-85)
  source_quote: |
    "Regions using these macros are special in that the current continuity equation is not
    solved: instead, the current is explicitly set to zero. This means that features that
    enhance the current (tunneling, impact ionization, etc...) will not function."
  summary: |
    material type=insulator 的宏（如 sio2）电流恒为零，任何乘以电流的增强机制都失效。
    需要隧穿/碰撞电离时，把绝缘层改为宽禁带半导体宏（如 s-sio2）。
  tags: [material, tunneling, rule]

- id: p06
  title: 掺杂浓度输入单位是 m^-3
  type: principle
  source_chapter: 手册第3章 (P54)
  source_quote: |
    "doping is defined in m-3 for input purposes; care should be taken to convert from the
    commonly-used cm-3 units as low doping levels can lead to poor convergence."
  summary: |
    n_doping/p_doping 一律用 m^-3（1e24 m^-3 ≈ 1e18 cm^-3）。换算错误（尤其低掺杂）不仅结果
    错，还直接导致收敛差。
  tags: [units, doping, rule]

- id: p07
  title: 长度单位 μm，能带/电位单位 eV 或 V，其余用 MKS
  type: principle
  source_chapter: 附录B (P1286)
  source_quote: |
    "Dimensions are in micron meters. Band parameters and potentials are in eV or volts.
    All others are in MKS units."
  summary: |
    Crosslight 输入的单位体系与常见 TCAD 不同：几何长度 μm、能带 eV、迁移率 m²/(V·s)、
    掺杂 1/m³。混用单位是材料宏与结构定义中最常见的错误来源。
  tags: [units, rule]

- id: p08
  title: 输入输出文件使用同一 basename
  type: principle
  source_chapter: 手册第3章 (P65-66)
  source_quote: |
    "It is generally considered a good idea to use the same base name for input and output
    files ... Using the same base filename is recommended as it ensures that the GUI programs
    can detect and handle the files correctly."
  summary: |
    .sol 的 output 语句与输入同名（test1.sol → test1.out），GUI 工具依赖 basename 匹配来
    关联文件；改名会导致后处理与项目管理混乱。
  tags: [workflow, files, rule]

- id: p09
  title: 多个软件包不要安装在同一目录
  type: principle
  source_chapter: 手册第2章 (P40)
  source_quote: |
    "you should never install multiple software packages in the same directory. This may cause
    version errors between files present in both versions."
  summary: |
    不同版本/产品的 DLL 与文件同名冲突会引发莫名故障；尽量使用默认安装目录。
  tags: [installation, rule]

- id: p10
  title: RTG≥1 的结果无物理意义，应忽略
  type: principle
  source_chapter: 手册第22章 (P445)
  source_quote: |
    "RTG >= 1 is an unphysical situation and should be ignored. It usually indicates a point
    above threshold ... the evaluation of the RTG is not realistic."
  summary: |
    阈值以上 RTG 已不适用（忽略了烧孔与载流子钳位）。看到 RTG≥1 说明预览或搜索位置已越阈，
    不要当作真实增益使用。
  tags: [rtg, pics3d, rule]

- id: p11
  title: 偏置扫描前必须先求 equilibrium 解
  type: principle
  source_chapter: 手册第3章 (P66-67)
  source_quote: |
    "This is a required first step before bias can be applied."
  summary: |
    equilibrium 只解 Poisson 方程、电流为零，是 Newton 求解器的初始猜测基座。任何 scan 之前
    必须有一条 equilibrium 语句。
  tags: [bias, workflow, rule]

- id: p12
  title: 瞬态仿真一旦开始，保持一致使用时间变量
  type: principle
  source_chapter: 手册第3章 (P67)
  source_quote: |
    "if you start a transient simulation, it is a good idea to consistently continue to use
    the time variable as you may otherwise encounter convergence difficulties."
  summary: |
    稳态/瞬态混用变量会让求解器在两种状态之间摇摆；瞬态序列应始终以 time 为主变量续跑。
  tags: [transient, convergence, rule]

- id: p13
  title: 网格必须加密在剧变区而非全局均匀加密
  type: principle
  source_chapter: 手册第3章 (P58) / 第4章 (P80-81)
  source_quote: |
    "the mesh must be dense near sharp material interfaces ... and near other regions where the
    electrical properties change rapidly over a small distance."
  summary: |
    界面、接触、掺杂突变、隧穿结、电流拥挤、QW 波函数与光模峰值处必须加密；全局均匀加密
    浪费时间与内存且并不解决局部采样问题。分布用 r/shift_center 控制。
  tags: [mesh, rule]

- id: p14
  title: 低阻区（金属/重掺杂）网格不要过密
  type: principle
  source_chapter: 手册第4章 (P81-82)
  source_quote: |
    "regions with very low resistivity (metals, highly-doped contact regions, etc...) are at
    risk ... if the whole layer has a very small voltage drop, then the delta-V between
    closely-spaced mesh points can become negligible."
  summary: |
    低阻区 ΔV≈0 时欧姆定律 ΔI=ΔV/R 数值不稳定，软件会报"无法精确控制电流"。调整低阻区
    网格分布即可修复——这是过密网格破坏收敛的典型案例。
  tags: [mesh, convergence, rule]

- id: p15
  title: GaN/纤锌矿 MQW 的极化效应必须用 self_consistent 自洽求解
  type: principle
  source_chapter: 手册第13章 (P265-266)
  source_quote: |
    "To model this effect properly, the user must use the self_consistent statement: this will
    force the solver to iterate between the Poisson drift-diffusion equations and the
    Schrodinger solver so a self-consistent solution can be found."
  summary: |
    自发+压电极化在界面产生固定电荷与局域场（QCSE），波函数与增益随之改变。不开启
    self_consistent，Schrödinger 求解器假设平带，GaN 量子阱结果错误。
  tags: [gan, quantum-well, polarization, rule]

- id: p16
  title: 极化 MQW 中每个阱应分配独立材料号
  type: principle
  source_chapter: 手册第13章 (P266)
  source_quote: |
    "a different material number must be assigned to each well: the independent_mqw statement
    in the layer file can automate this."
  summary: |
    各阱局域场不同，若共享材料号则 Schrödinger 与增益只算一次，结果错误。用 independent_mqw
    自动给每阱独立编号。
  tags: [gan, quantum-well, rule]

- id: p17
  title: 纤锌矿材料必须按实际生长条件设定基晶格
  type: principle
  source_chapter: 手册第13章 (P256-257)
  source_quote: |
    "if a thick bulk layer of AlGaN or AlN is grown on a sapphire substrate before the MQW is
    placed on top, the base lattice constant should be that of bulk AlGaN or AlN instead of GaN."
  summary: |
    默认基晶格是 GaN，但缓冲层可能弛豫、衬底可能是 AlN/AlGaN 系。基晶格决定应变张量，
    错设会让能带、极化与增益全部偏移。
  tags: [gan, strain, rule]

- id: p18
  title: 留空区域用 vacuum/air 而非 void
  type: principle
  source_chapter: 手册第3章 (P54)
  source_quote: |
    "If no material is to be defined in a particular column, use the 'void' macro; this will
    prevent any mesh from being allocated ... In some cases, this will affect the physics of
    the simulation by shifting the position of the boundaries."
  summary: |
    void 不分配网格会移动边界影响物理；需要绝缘但保留网格/边界时用 vacuum 或 air 宏
    （分配网格但无电流）。
  tags: [geometry, mesh, rule]

- id: p19
  title: 绝缘宏的材料号必须大于半导体宏
  type: principle
  source_chapter: 手册第3章 (P56)
  source_quote: |
    "as a rule, an insulator macro must be given a larger material number than a semiconductor."
  summary: |
    .geo 中材料编号约定：绝缘体用更大的材料号，保证边界识别与网格处理正确。
  tags: [geometry, mesh, rule]

- id: p20
  title: 输入语句每行 ≤80 字符，续行用 &&，注释以 $ 开头
  type: principle
  source_chapter: 手册第3章 (P45)
  source_quote: |
    "Each line can only have a maximum of 80 characters and any information after this limit
    will be ignored during processing."
  summary: |
    超过 80 字符的内容被静默忽略，是隐蔽错误来源；长语句用 && 续行；禁用 tab 等不可见字符
    （附录B 强调）。
  tags: [syntax, input-files, rule]

- id: p21
  title: 重复语句以最后一条为准
  type: principle
  source_chapter: 手册第3章 (P46) / 附录B (P1282)
  source_quote: |
    "A statement for material parameters overrides a previous statement with the same keyword."
  summary: |
    材料参数可多次定义，后发覆盖先发。这是"在 .sol 中覆盖宏参数"机制的基础，也是调试时
    需注意的优先级规则。
  tags: [syntax, material, rule]

- id: p22
  title: .gain 表格化折射率与主仿真结果可能有差异
  type: principle
  source_chapter: 手册第16章 (P324-326)
  source_quote: |
    "during the preview of the round-trip gain provided by rtgain_phase, tabulated index change
    values are used to evaluate the propagation constant. This may differ from results in the
    main simulation."
  summary: |
    RTG 预览用 .gain 的表格化 index change；主仿真用逐偏置计算值。两者可能不同（尤其越阈后），
    不要拿预览的绝对数值当最终结果。
  tags: [gain, rtg, rule]

- id: p23
  title: VCSEL 的 section 标签不允许交错
  type: principle
  source_chapter: 手册第22章 (P473)
  source_quote: |
    "care must be taken not to interleave section labels: it is not supported by the software
    at this time ... assigning a particular section label to the barrier region and another
    to the well region may result in an error and produce incorrect section lengths."
  summary: |
    VCSEL 的 vcsel_type 标签序列若出现 b/w/b 交错会产生错误腔长。整个 MQW 区应使用单一
    section 标签；复制粘贴层时标签会随层复制，需在完成后统一设置。
  tags: [vcsel, geometry, rule]

- id: p24
  title: 输出中某些变量需先 more_output 才能绘图
  type: principle
  source_chapter: 手册第3章 (P75)
  source_quote: |
    "certain seldom-used variables are not (by default) available for plotting. To make them
    available, you may need to use the more_output statement in the .sol file and re-run the
    simulation."
  summary: |
    画不到某变量时先查附录 G 变量表，缺省未输出的变量要在 .sol 加 more_output 并重跑。
    这是后处理最常见的"为什么画不出来"答案。
  tags: [post-processing, output, rule]

- id: p25
  title: 教程示例会随版本更新而改变，结果以当前版本为准
  type: principle
  source_chapter: 手册第22章 (P437-438)
  source_quote: |
    "all examples are subject to change as the software is updated. Between each release,
    there are often bugfixes, material macro changes, new models and other improvements
    which can affect the results."
  summary: |
    手册示例（多数标注 2009 更新）的数值结果可能与本机版本有偏差；看到不一致时先怀疑版本
    差异，再考虑自己设置错误。
  tags: [versioning, expectation, rule]
