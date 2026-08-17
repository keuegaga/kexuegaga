# Case Candidates — Crosslight 通用手册

> cangjie-skill 阶段 1 产出（案例提取器）。候选未筛选，供阶段 1.5 验证与阶段 2 A1 段素材。

- id: c01
  title: inp13 — 1/4 波长相移 DFB 激光教程
  type: case
  source_chapter: 手册第22章 (P437-448)
  source_quote: |
    "This example is an index-coupled distributed feedback (DFB) laser with a quarter-wave
    phase shift in the middle. This kind of structure is often used to guarantee the device
    lases on a single longitudinal mode."
  summary: |
    PICS3D 入门教程：InP 衬底、InGaAsP 体有源区（1.3 μm），用 .layer 定义 1D 截面，再在
    begin_zsol 中用两个 250 μm section + phase_shift=0.5 构造相移光栅；演示了 3d_solution_method、
    z_structure、rtgain_phase 预览、auto_finish=rtgain 初始化与 solve_rtg=yes 三步偏置完整流程。
  bound_to:
    - "PICS3D 三步偏置初始化流程"
    - "简化 κ 光栅与相移定义"
    - "RTG 预览定位腔模法"
  outcome: |
    教程展示了模式搜索日志中主模 RTG≈0.87 的谱分布，及 L-I、波长-电流、能带与波强度后处理图。
  tags: [case, pics3d, dfb, tutorial]

- id: c02
  title: inp13amp — 3D 光放大器/SOA 教程
  type: case
  source_chapter: 手册第22章 (P449-456)
  source_quote: |
    "PICS3D is ideal for the study of semiconductor optical amplifiers (SOA). The simulation
    approach is similar to that for lasers, with the main difference being the presence of an
    external light source."
  summary: |
    用 3d_amplifier_model 把同一 DFB 结构改成 SOA：外光源从左端面注入（平衡态关闭、用 scan 开启），
    输出功率-输入光曲线、ASE 谱与 ASE-输入光关系。演示了放大器、超辐射发光管（输入≈0）、
    反偏调制器（增益为负）的同一模型框架。
  bound_to:
    - "3D 放大器建模"
    - "外部光源用 scan 开启的偏置法"
  outcome: |
    教程给出输出光功率随输入光增加、ASE 随之下降的典型饱和曲线。
  tags: [case, pics3d, soa, amplifier]

- id: c03
  title: tune1-3 — 三节可调 DBR 激光教程
  type: case
  source_chapter: 手册第22章 (P457-469)
  source_quote: |
    "This example is a tunable edge-emitting laser with a Distributed Bragg Reflector (DBR).
    It consists of three segments: a gain region on the left, a tuner in the middle and a
    Bragg mirror on the right."
  summary: |
    演示纵向变化结构：三个 .layer 文件（previous_layer 连接）、三个 z_structure/load_mesh 段、
    begin_zmater 分段的材料、grating_compos 显式定义 DBR 光栅（软件自动算 κ≈36386 1/m）、
    共享底电极 + 三个独立顶部电极的偏置、调谐电流引起模式跳跃的波长-电流曲线。
  bound_to:
    - "多段器件共享地+分段独立电流偏置法"
    - "显式光栅建模（grating_compos）"
    - "多电极扫描变量设置"
  outcome: |
    教程展示了调谐电流改变纵模位置导致功率波动与模跳（功率下降、波长阶跃）。
  tags: [case, pics3d, dbr, tunable, multi-electrode]

- id: c04
  title: jim_vcsel — 基本 VCSEL 教程
  type: case
  source_chapter: 手册第22章 (P470-481)
  source_quote: |
    "This example is a basic vertical cavity surface emitting laser (VCSEL) ... Since the
    optical propagation takes place perpendicularly to the active region, we will use a
    different method to define segments and sections."
  summary: |
    GaAs 系 MQW VCSEL（0.835 μm）：DBR 用平均材料做电学网格、vcsel_section + vertical_dbr_layer_mater
    显式周期做光学传播；圆柱坐标（cylindrical axis=y）、fiber-like EIM 模式求解；RTG 预览给出
    驻波增益增强因子 gfactor_stdwave≈1.71，演示 spacer 设计、低阈值电流偏置与顶部/底部功率后处理。
  bound_to:
    - "VCSEL spacer 迭代设计法"
    - "VCSEL section/DBR 周期建模"
    - "圆柱坐标与 EIM 模式求解"
  outcome: |
    教程给出顶部（少 DBR 层）输出功率最大、L-I 曲线与驻波-QW 重叠图。
  tags: [case, pics3d, vcsel, tutorial]

- id: c05
  title: test1 — 1D FP 激光 setup 全流程演示
  type: case
  source_chapter: 手册第3章 (P46-75)
  source_quote: |
    "To start the software ... click on 'PICS3D-20** SimuCenter' in the Start menu. This is
    the main Graphical User Interface for the program and most simulation tasks can be
    accomplished from within this interface."
  summary: |
    AlGaAs/GaAs 1D 激光的完整入门演示：setuplayer 交互生成 .layer → layer.exe 生成 .geo/.mater/.doping
    → geometry.exe 生成 .msh → setuplastip 生成 .gain/.sol → pics3d.exe 运行 → .plt 画 L-I 与
    波强度。展示了仿真文件体系与命令行/SimuCenter 双路径。
  bound_to:
    - "从示例项目出发逐步修改法"
    - "文件体系与标准流程"
  outcome: |
    示例输出显示 equilibrium 收敛、电压/电流扫描与 66.6 mW 光功率数据点。
  tags: [case, workflow, fp-laser, tutorial]

- id: c06
  title: LED_GaN_MQW — InGaN/GaN MQW LED 教程
  type: case
  source_chapter: 手册第20章 (P388-400)
  source_quote: |
    "20.3 LED_GaN_MQW 2d InGaN"
  summary: |
    APSYS 的 GaN 系 MQW LED 二维示例：InGaN 阱/GaN 垒材料系，示范纤锌矿材料宏、极化/自洽
    相关设置与 LED 自发辐射谱、IV 特性分析。是用户 GaN 方向最贴近的官方示例。
  bound_to:
    - "GaN 纤锌矿 MQW 建模（极化/自洽）"
    - "APSYS LED 仿真工作流"
  outcome: |
    官方支持示例（附录 H 列出），用于学习 GaN 材料宏调用与 LED 仿真设置。
  tags: [case, apsys, gan, led, tutorial]

- id: c07
  title: solar_cell_Si_simple — 晶体硅太阳能电池教程
  type: case
  source_chapter: 手册第20章 (P402-408)
  source_quote: |
    "This example is a simple bulk crystalline silicon solar cell with contact lines on
    the front and back."
  summary: |
    APSYS 硅太阳能电池入门示例：体硅、前后接触线、light_power 光泵浦定义与扫描、IV/效率分析。
    示范非激光器件的 APSYS 光注入工作流（与激光器偏置完全不同）。
  bound_to:
    - "APSYS 光泵浦（light_power）工作流"
    - "电压偏置适用场景"
  outcome: |
    官方支持示例，用于学习光产生-复合与扫描设置。
  tags: [case, apsys, solar-cell, tutorial]

- id: c08
  title: 1D_laser — GaAs/AlGaAs 单量子阱 GRINSCH 激光教程
  type: case
  source_chapter: 手册第21章 (P412-419)
  source_quote: |
    "This example is a simple GaAs/AlGaAs laser with a single quantum well and a GRINSCH
    structure. It also shows how to define layers with composition gradings."
  summary: |
    LASTIP 1D 激光教程：GRINSCH 渐变 Al 组分层、单量子阱；强调在渐变层加掺杂可平滑载流子注入、
    消除 I-V 曲线扭结、降低阈值并提高谐振频率——一个"材料设置影响器件性能"的实证。
  bound_to:
    - "FP 激光 2D/1D 建模"
    - "组分渐变层定义（grading）"
  outcome: |
    教程明确指出渐变层掺杂消除了 I-V 扭结并改善阈值与频率响应。
  tags: [case, lastip, qw-laser, tutorial]

- id: c09
  title: 1D_therm — 激光器热效应教程
  type: case
  source_chapter: 手册第21章 (P420-426)
  source_quote: |
    "21.3 A_tutorial 1D_therm"
  summary: |
    LASTIP 热仿真示例：在激光结构上加热边界/热沉与 self-heating，分析温度分布对器件特性的影响。
    示范热方程、热边界（4.3 提到的热阻/自热区距离问题）与温度相关参数设置。
  bound_to:
    - "热效应建模与热边界设置"
    - "温度相关材料参数"
  outcome: |
    官方支持示例，用于学习激光器自热分析。
  tags: [case, lastip, thermal, tutorial]

- id: c10
  title: basic_ridge — 脊形波导激光教程
  type: case
  source_chapter: 手册第21章 (P428-435)
  source_quote: |
    "21.4 A_tutorial basic_ridge"
  summary: |
    LASTIP 2D 脊形波导激光示例：刻蚀脊、侧向电流限制与横向光限制，示范 2D 模式求解与脊结构
    的 .layer/.geo 定义。是 FP 激光从 1D 走向横向结构的关键示例。
  bound_to:
    - "2D FP 激光横向模式建模"
    - "脊形结构定义"
  outcome: |
    官方支持示例，用于学习脊形激光器建模。
  tags: [case, lastip, ridge, tutorial]

- id: c11
  title: p-n-i-p-n 反偏击穿 + 辅助欧姆接触案例
  type: case
  source_chapter: 手册第4章 (P84-86)
  source_quote: |
    "we wish to reverse bias to breakdown at about 10 volts. We can simultaneously ramp up the
    voltages at the auxiliary contact to about 5 volts to ensure convergence."
  summary: |
    反偏 p-n-i-p-n 结构的 i 区远离电极、变量漂移。方案：i 区单网格点加辅助欧姆接触，电压拉至
    约 5 V 稳定求解；总偏置到 ~10 V 击穿后，用电流控制把辅助接触电流归零，消除其对器件的
    影响。是"辅助接触法"的完整工作案例。
  bound_to:
    - "辅助欧姆接触固定浮置区法"
  outcome: |
    手册指出没有辅助接触该器件难以偏置到击穿；加接触后成功达到击穿。
  tags: [case, convergence, technique]

- id: c12
  title: GaAs 负微分迁移率（Γ-L 转移）收敛案例
  type: case
  source_chapter: 手册第4章 (P87-88)
  source_quote: |
    "The steady state solution can be driven into non-convergence because of the negative
    differential resistance due to the special field dependence mobility ... as defined by the
    'n.gaas' velocity model."
  summary: |
    GaAs 在强场下电子从 Γ 带转移到 L/X 带产生负微分迁移率（图 4.2 的 n.gaas 模型），高偏置下
    稳态求解发散（真实器件可能 Gunn 振荡）。对策：换用 beta 迁移率模型，或用瞬态仿真。
  bound_to:
    - "迁移率模型选择（n.gaas vs beta）"
    - "负微分电阻下的收敛处理"
  outcome: |
    手册建议 beta 模型可绕过负阻峰实现稳态收敛。
  tags: [case, mobility, convergence, gaas]

- id: c13
  title: A_tutorial — APSYS 骆驼二极管（n-p-n 多数载流子器件）
  type: case
  source_chapter: 手册第20章 (P380-388)
  source_quote: |
    "This example is a camel diode, which is related to the planar doped barrier diode.
    It is a n-p-n majority carrier diode which finds applications in high-speed switches."
  summary: |
    APSYS 入门示例：i 区中埋一层极薄高掺杂 p 层（掺杂/网格分布关键），演示多数载流子器件的
    .layer 定义、网格处理与 I-V 分析。薄层结构对网格敏感，是网格-收敛关联的教材案例。
  bound_to:
    - "薄掺杂层的网格处理"
    - "APSYS 基础工作流"
  outcome: |
    官方支持示例（改编自文献[120]），用于学习 APSYS 基础操作。
  tags: [case, apsys, diode, tutorial]
