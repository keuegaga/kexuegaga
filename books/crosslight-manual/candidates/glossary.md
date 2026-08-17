# Glossary Candidates — Crosslight 通用手册

> cangjie-skill 阶段 1 产出（术语提取器）。候选未筛选，供阶段 1.5 验证与阶段 3 整理为共享词典。

- id: g01
  term: RTG（Round-Trip Gain，往返增益）
  type: term
  source_chapter: 手册第16章 (P318-320) / 第22章 (P444-446)
  author_definition: |
    "The complex roundtrip gain (i.e. phase and amplitude). ... W(omega) = 1 - Rg. In a real
    cavity ... the round-trip gain is always less than one."
  key_distinction: |
    ≠ 单程/材料增益。RTG 是包含相位匹配的复值往返增益；纵模 = Wronskian 零点（RTG=1 极限）。
    阈值下 RTG<1，RTG≥1 无物理意义。
  why_it_matters: |
    PICS3D 一切纵向模式、阈值与光谱判断都以 RTG 为核心量；几乎所有激光仿真 skill 都会引用它。
  tags: [term, pics3d, core-concept]

- id: g02
  term: kappa（耦合系数）
  type: term
  source_chapter: 手册第16章 (P321-324)
  author_definition: |
    "kappa = (omega/c0) * delta(n) ... the magnitude of the index variation (also a complex
    quantity)"（耦合波方程中前向/后向波的耦合强度）
  key_distinction: |
    ≠ 介电常数。kappa 描述 DFB/DBR 光栅把前向波耦合到后向波的强度；实数=折射率耦合，
    复数=增益/损耗耦合；无量纲强度常用 kappa*L。
  why_it_matters: |
    DFB/DBR 设计 skill 的核心参数：决定反射率、模式选择与单模性。
  tags: [term, dfb, dbr]

- id: g03
  term: 宏（macro）/ 被动宏与主动宏
  type: term
  source_chapter: 手册第3章 (P59-60) / 附录B (P1282-1283)
  author_definition: |
    "A macro is a collection of input statements (or commands). ... Bulk material macros are
    given lower case macro names ... Active layer macros are given mixed case macro names."
  key_distinction: |
    ≠ 编程宏。被动宏（小写，load_macro）管带隙/迁移率/折射率等体参数；主动宏（混合大小写，
    get_active_layer）管量子阱子带与光跃迁。有源区必须两者同时定义。
  why_it_matters: |
    材料定义 skill 的核心概念；误用被动/主动宏是常见错误。
  tags: [term, material, core-concept]

- id: g04
  term: section / segment（光学节 / 电学段）
  type: term
  source_chapter: 手册第22章 (P441-443)
  author_definition: |
    "The optical propagation model is tied to the concept of 'sections': these define the
    optical cavity in the same way that 'segments' define the 3D geometry of the electrical
    simulation."
  key_distinction: |
    ≠ 同义词。section 在 begin_zsol 里定义纵向光学传播（腔长/κ/相移）；segment 由 z_structure
    定义 3D 电学体积。多段器件中二者数量一一对应。
  why_it_matters: |
    PICS3D 输入文件的"双分段"体系，混淆即报错或腔定义错误。
  tags: [term, pics3d, geometry]

- id: g05
  term: auto_finish（自动终止条件）
  type: term
  source_chapter: 手册第4章 (P78-79) / 第22章 (P446)
  author_definition: |
    "It is also possible to automatically terminate a voltage scan when a certain current is
    reached by using the auto_finish parameter in the scan statement."（亦可 auto_finish=rtgain）
  key_distinction: |
    ≠ 普通扫描终点。auto_finish 让扫描在到达目标变量之前按物理条件（电流/RTG）提前终止，
    是 PICS3D 光子耦合初始化的强制前置步骤。
  why_it_matters: |
    三步偏置 skill 的关键语句；不会用 auto_finish 就无法初始化 PICS3D 激光仿真。
  tags: [term, pics3d, bias]

- id: g06
  term: solve_rtg（开启光子耦合求解）
  type: term
  source_chapter: 手册第4章 (P79) / 第22章 (P447)
  author_definition: |
    "The photon coupling can be turned on immediately afterwards by using solve_rtg=yes in the
    next scan statement."
  key_distinction: |
    ≠ 默认求解。默认不耦合光子密度；solve_rtg=yes 后 Newton 方程组加入光子方程，必须小步长。
  why_it_matters: |
    "是否开启光子耦合"是 PICS3D 阈值前后仿真的分水岭。
  tags: [term, pics3d, bias]

- id: g07
  term: LSHB（纵向空间烧孔）
  type: term
  source_chapter: 手册第16章 (P319-321) / 第4章 (P78-79)
  author_definition: |
    "the photon density can only be known by evaluating the RTG but evaluating the RTG requires
    knowledge of the photon density because of its impact on the longitudinal gain profile
    (i.e. spatial hole burning)."
  key_distinction: |
    ≠ 一般空间烧孔。特指沿腔纵向光子分布不均导致增益/折射率纵向不均，形成 RTG 与光子密度的
    互锁，是三步偏置的物理根源。
  why_it_matters: |
    解释"为什么 PICS3D 初始化那么麻烦"，也是 DFB 边模抑制分析的背景。
  tags: [term, pics3d, physics]

- id: g08
  term: valence_mixing（价带混合，k.p）
  type: term
  source_chapter: 手册第8章 (P140-143)
  author_definition: |
    "By setting valence_mixing=yes in the active_reg or set_active_reg statements, a full
    computation of subbands using k.p theory is performed."
  key_distinction: |
    ≠ 默认的抛物线近似。默认用各向异性抛物线拟合价带（快）；valence_mixing 用 k.p 全解，
    捕获重/轻空穴反交叉，慢但更准，应变阱尤其重要。
  why_it_matters: |
    量子阱增益 skill 的精度-速度权衡点。
  tags: [term, quantum-well, kp]

- id: g09
  term: self_consistent（自洽求解）
  type: term
  source_chapter: 手册第8章 (P143-144) / 第13章 (P265-266)
  author_definition: |
    "This will force the solver to iterate between the Poisson drift-diffusion equations and
    the Schrodinger solver so a self-consistent solution can be found."
  key_distinction: |
    ≠ 平带近似。默认 Schrödinger 用平带势；自洽把电荷密度与势耦合迭代，极化 MQW（QCSE）必选。
  why_it_matters: |
    GaN 量子阱 skill 的必选开关；漏掉则增益与波长全错。
  tags: [term, quantum-well, gan]

- id: g10
  term: independent_mqw（每阱独立求解）
  type: term
  source_chapter: 手册第13章 (P266)
  author_definition: |
    "a different material number must be assigned to each well: the independent_mqw statement
    in the layer file can automate this."
  key_distinction: |
    ≠ 默认共享材料号。共享时 Schrödinger/增益只算一次；极化 MQW 各阱场不同，必须独立。
  why_it_matters: |
    GaN MQW skill 的层文件设置项。
  tags: [term, gan, quantum-well]

- id: g11
  term: set_polarization（自动极化界面电荷）
  type: term
  source_chapter: 手册第13章 (P266)
  author_definition: |
    "Interface charges can be defined manually with the interface statement. For the InGaN
    and AlGaN material system, this process has been automated in the layer file with the
    set_polarization statement."
  key_distinction: |
    ≠ 手工 interface 电荷。set_polarization 按 InGaN/AlGaN 组分自动生成自发+压电极化电荷。
  why_it_matters: |
    GaN 层文件 skill 的关键语句。
  tags: [term, gan, polarization]

- id: g12
  term: 基晶格（base lattice）
  type: term
  source_chapter: 手册第13章 (P256-257)
  author_definition: |
    "The default lattice base constant in our software is that of GaN, but it may not be true
    for all devices. ... the base lattice constant should be that of bulk AlGaN or AlN."
  key_distinction: |
    ≠ 衬底晶格。应变以"基晶格"为参考；缓冲层可能弛豫，基晶格未必等于衬底。
  why_it_matters: |
    GaN 应变/极化/能带计算的前提；错设全链错误。
  tags: [term, gan, strain]

- id: g13
  term: EIM（Effective Index Method，有效折射率法）
  type: term
  source_chapter: 手册第12章 (P244-251) / 第17章 (P355-356)
  author_definition: |
    "Enhanced Effective Index Method ... used to obtain the lateral mode profile"（横向模式求解方法）
  key_distinction: |
    ≠ 纵向模式。EIM 求横向/侧向模式与复模折射率，是 RTG 计算中 k(z) 的来源之一；
    VCSEL 用 fiber-like EIM（圆柱）。
  why_it_matters: |
    波导模式 skill 的核心方法，也影响 PICS3D 模式求解精度。
  tags: [term, waveguide, mode]

- id: g14
  term: PML（Perfectly Matched Layer，完美匹配层）
  type: term
  source_chapter: 手册第12章 (P251-254) / 附录A
  author_definition: |
    "Perfectly Matched Layer Boundary"（吸收边界，消除人工反射）
  key_distinction: |
    ≠ 普通吸收边界。PML 通过复坐标拉伸匹配阻抗；截断尺寸不足会导致模式解失真。
  why_it_matters: |
    波导/模式 skill 的边界设置项。
  tags: [term, waveguide, boundary]

- id: g15
  term: mode_srch（纵向模式搜索）
  type: term
  source_chapter: 手册第22章 (P444-445)
  author_definition: |
    "The longitudinal mode search is controlled by the mode_srch statement. This statement
    defines the search range for the longitudinal modes."
  key_distinction: |
    ≠ 模式求解器。mode_srch 只定义搜索窗口（wavel_xrange/omega_xrange）与 adjust_range；
    搜索对象是 RTG 的零点。
  why_it_matters: |
    RTG 预览 skill 的配套语句；窗口设置决定是否漏模。
  tags: [term, pics3d, mode]

- id: g16
  term: scan_data / xy_data（两类输出数据）
  type: term
  source_chapter: 手册第3章 (P72-73)
  author_definition: |
    "bias-dependent data (scan_data) and structural/spectral data (xy_data). The former
    includes bias current, voltage, laser power, etc... The latter includes position-dependent
    data like the carrier densities and certain spectral values."
  key_distinction: |
    ≠ 同一个数据。scan_data 逐偏置点累积；xy_data 按 print_step 打印结构/光谱量。
  why_it_matters: |
    后处理 skill 必须先分清这两类，否则 get_data 取错。
  tags: [term, post-processing, data]

- id: g17
  term: 数据集编号（data set number）
  type: term
  source_chapter: 手册第3章 (P73)
  author_definition: |
    "all output data is assigned a 'data set number' for later use ... The extension is always
    _0001 for the initial equilibrium calculations and increases by one every time printing of
    the data is requested."
  key_distinction: |
    ≠ 偏置步编号。数据集按打印请求编号，可在 .sol.msg 查对应偏置值。
  why_it_matters: |
    画图/取数时定位"哪个偏置点的数据"。
  tags: [term, post-processing]

- id: g18
  term: basic variables（基本求解变量）
  type: term
  source_chapter: 手册第4章 (P81-82)
  author_definition: |
    "The default basic variables in our simulator are the potential and quasi-Fermi levels.
    ... The choice of electron and hole concentrations as the basic solution variable avoids
    the fluctuation problem."
  key_distinction: |
    ≠ 固定不变。默认是势+准费米能级；高阻/流阻结构可切换为载流子浓度（newton_par
    change_variable），各有数值代价。
  why_it_matters: |
    收敛技巧 skill 的开关之一，解释低偏置不收敛的机制。
  tags: [term, numerics, convergence]

- id: g19
  term: slow transient（慢瞬态）
  type: term
  source_chapter: 手册第4章 (P82-83)
  author_definition: |
    "scan var=voltage_1 value=-3.5 var2=time value2_to=1.0 ... the displacement current makes
    a numerically significant contribution to the current continuity equations."
  key_distinction: |
    ≠ 真实瞬态仿真。慢瞬态只是把电压随时间缓升（如 1 s），利用数值位移电流帮助高阻结构收敛，
    瞬态物理效应可忽略。
  why_it_matters: |
    GaN 极化 MQW 等难收敛结构的首选技巧。
  tags: [term, convergence, transient]

- id: g20
  term: bandgap_reduction（带隙降低）
  type: term
  source_chapter: 手册第4章 (P86-87)
  author_definition: |
    "One technique is to artificially reduce the bandgap first, achieve the desired bias
    current and finally increase the semiconductor bandgap back to its original value."
  key_distinction: |
    ≠ 物理带隙。它是收敛技巧：临时缩小带隙提高载流子密度，恢复后需保持电流偏置，且被改写的
    IV 段不可用。
  why_it_matters: |
    宽禁带器件收敛 skill 的武器，但用错会产出假数据。
  tags: [term, convergence, wide-bandgap]

- id: g21
  term: z_structure / begin_zsol（电学三维段 / 光学纵向块）
  type: term
  source_chapter: 手册第22章 (P441-444)
  author_definition: |
    "3d_solution_method ... and one or more segments are defined. These segments combine
    multiple 2D mesh planes and define a 3D volume for the simulation."（begin_zsol 为纵向模式会话）
  key_distinction: |
    ≠ 同层。z_structure 在 begin 块定义电学段（长度/平面数）；begin_zsol 块定义光学腔
    （longitudinal/section/mode_srch）。
  why_it_matters: |
    PICS3D 输入文件的顶层结构，必须成对出现。
  tags: [term, pics3d, geometry]

- id: g22
  term: grating_compos / grating_model（显式光栅定义）
  type: term
  source_chapter: 手册第22章 (P459-463)
  author_definition: |
    "the grating_compos statement: the original layer material is replaced by a virtual
    embedded structure and two sets of material macros are used for the same material."
  key_distinction: |
    ≠ 简化 section kappa。显式定义高低折射率/增益材料与厚度，软件自动算 κ（含增益耦合）与
    辐射损耗；简化法直接给 κ。
  why_it_matters: |
    DFB/DBR 精确设计 skill 的建模路径选择。
  tags: [term, grating, dfb, dbr]
