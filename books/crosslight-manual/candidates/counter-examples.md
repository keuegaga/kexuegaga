# Counter-Example Candidates — Crosslight 通用手册

> cangjie-skill 阶段 1 产出（反例提取器）。候选未筛选，供阶段 1.5 验证与阶段 2 B 段素材。

- id: ce01
  title: 低阻区网格过细导致电流控制失效
  type: counter-example
  source_chapter: 手册第4章 (P81-82)
  source_quote: |
    "regions with very low resistivity (metals, highly-doped contact regions, etc...) are at
    risk. ... if the whole layer has a very small voltage drop, then the delta-V between
    closely-spaced mesh points can become negligible."
  failure_mode: |
    在金属/重掺杂低阻区放过多网格点，ΔV→0 使 ΔI=ΔV/R 数值不稳定，求解器报"无法准确控制电流"。
  mechanism: |
    有限精度下极小电压差被舍入噪声淹没，电流连续性方程在低阻区变成病态。
  warning_signs:
    - 报错提到 unable to accurately control current
    - 低阻区网格点间距远小于器件尺度
  bound_to:
    - "网格生成与质量检查"
    - "PICS3D 激光仿真标准工作流"
  tags: [counter-example, mesh, convergence]

- id: ce02
  title: 网格过粗导致剧变区欠采样不收敛
  type: counter-example
  source_chapter: 手册第3章 (P58) / 第4章 (P80-81)
  source_quote: |
    "A coarse mesh is a common cause of non-convergence. It is wise to stop the simulation and
    plot the bands, the distribution of potential and the carrier concentrations at the point
    of failure."
  failure_mode: |
    异质结、肖特基、掺杂突变、隧穿结、QW 波函数、光模峰值等剧变区网格太稀，解在节点间跳变，
    Newton 迭代不收敛或收敛到错误解。
  mechanism: |
    有限元在剧变区需要足够采样点才能分辨物理梯度；欠采样等效于"物理被网格抹平"。
  warning_signs:
    - 在界面/结附近能带或载流子浓度图出现明显折线/振荡
    - 局部加密后结果显著变化（网格收敛性未建立）
  bound_to:
    - "网格生成与质量检查"
  tags: [counter-example, mesh, convergence]

- id: ce03
  title: 对激射器件用电压偏置
  type: counter-example
  source_chapter: 手册第4章 (P78)
  source_quote: |
    "It is almost impossible to apply any voltage bias (which is roughly equal to the Fermi
    level splitting at the junction) without disturbing the solution."
  failure_mode: |
    阈值以上用电压控制，载流子/准费米能级被钳位导致电压微小变化引起巨大电流变化，求解发散。
  mechanism: |
    受激复合项使载流子密度与能级劈裂对电压几乎不敏感（钳位），Jacobian 病态。
  warning_signs:
    - 电压扫描越过阈值后发散
    - 日志显示电压几乎不变但电流量级剧跳
  bound_to:
    - "电压/电流偏置选择决策树"
    - "PICS3D 三步偏置"
  tags: [counter-example, bias, laser]

- id: ce04
  title: 把 RTG≥1 当成真实增益使用
  type: counter-example
  source_chapter: 手册第22章 (P445)
  source_quote: |
    "RTG >= 1 is an unphysical situation and should be ignored. It usually indicates a point
    above threshold, which means that the photon density is too strong to be ignored."
  failure_mode: |
    预览或模式搜索越阈后 RTG≥1，被当作真实往返增益用于设计判断，得到错误的阈值/模式结论。
  mechanism: |
    RTG 的推导假设光子密度可忽略（无烧孔/钳位）；越阈后该假设失效，数值无物理意义。
  warning_signs:
    - RTG 谱出现≥1 的平台或尖峰
    - auto_finish=rtgain 搜索窗口落在阈值以上
  bound_to:
    - "RTG 预览定位腔模法"
    - "PICS3D 三步偏置"
  tags: [counter-example, rtg, pics3d]

- id: ce05
  title: 直接修改默认材料宏文件
  type: counter-example
  source_chapter: 手册第3章 (P60) / 附录B (P1280)
  source_quote: |
    "it is STRONGLY recommended that the default macro files not be altered in any way since
    that would affect all the simulations that use these default files."
  failure_mode: |
    改了 crosslight.mac / more.mac 后，所有引用默认宏的仿真（含教程）结果被污染且难以追溯。
  mechanism: |
    宏是全局共享资源，覆盖无隔离；问题通常在很久以后才暴露。
  warning_signs:
    - 需要在多个项目间复现同一"正确"结果却对不上
  bound_to:
    - "材料参数覆盖法（不碰默认宏）"
  tags: [counter-example, material, macro]

- id: ce06
  title: bandgap reduction 后误用被改写的 IV 曲线
  type: counter-example
  source_chapter: 手册第4章 (P87)
  source_quote: |
    "since the bandgap was altered during when the bias was ramped up, the IV curve is
    incorrect for this region. In this situation, care should be taken to only plot data
    from the last scan statement."
  failure_mode: |
    带隙降低技巧跑出的升压段 IV 曲线被当成真实特性画进论文/报告，结果错误。
  mechanism: |
    带隙被人为缩小 20% 时阈值/开启电压偏离真实物理；只有恢复带隙后的回扫段才有效。
  warning_signs:
    - 仿真文件里有 bandgap_reduction 语句
    - 绘制的 IV 来自带隙被修改的扫描段
  bound_to:
    - "带隙降低分阶段法"
  tags: [counter-example, convergence, wide-bandgap, caution]

- id: ce07
  title: 在绝缘宏区域期望隧穿/碰撞电离工作
  type: counter-example
  source_chapter: 手册第4章 (P84-85)
  source_quote: |
    "Regions using these macros are special in that the current continuity equation is not
    solved: instead, the current is explicitly set to zero."
  failure_mode: |
    用 sio2 等 insulator 宏后，隧穿、碰撞电离、陷阱辅助等乘电流的机制全部失效，器件特性错误。
  mechanism: |
    电流被显式置零，任何"电流×增强因子"的贡献恒为零。
  warning_signs:
    - 结构含 type=insulator 材料但预期有隧穿电流
  bound_to:
    - "材料宏体系与单位"
    - "偏置策略决策"
  tags: [counter-example, material, tunneling]

- id: ce08
  title: 总电流极小时用电流偏置（违反 KCL）
  type: counter-example
  source_chapter: 手册第4章 (P77)
  source_quote: |
    "the actual current amount may fluctuate due to lack of numerical precision, making it
    difficult to use current bias. This situation can be detected by observing the net current
    over all the electrodes: if the sum is not zero, then Kirchoff's Current Law is violated."
  failure_mode: |
    器件总电流极小时电流控制量被数值噪声淹没，各电极电流不满足 KCL，求解发散。
  mechanism: |
    双精度下极小电流的表示误差与解的量级可比。
  warning_signs:
    - 各电极电流之和不为零
    - 电流值在 1e-15 A 以下
  bound_to:
    - "电压/电流偏置选择决策树"
  tags: [counter-example, bias, precision]

- id: ce09
  title: RTG 终止值设太高或太低导致模式初始化失败
  type: counter-example
  source_chapter: 手册第4章 (P79)
  source_quote: |
    "If it is too high, then the photon density may not be as close to zero as originally
    thought and the initial guess may be inaccurate ... On the other hand, if the ending value
    is too low, then some modes critical to the simulation may be missing."
  failure_mode: |
    auto_finish=rtgain 的终止 RTG 过高（接近 1）时初始光子密度假设失效；过低时模式搜索漏掉
    关键纵模，开启光子耦合后发散或丢失激射模。
  mechanism: |
    RTG 终止点决定"阈值下状态"的近似质量与模式覆盖；折中点是略高于增益材料透明密度。
  warning_signs:
    - solve_rtg 开启后立即发散
    - 仿真输出缺预期的边模/主模
  bound_to:
    - "PICS3D 三步偏置初始化流程"
  tags: [counter-example, rtg, pics3d, convergence]

- id: ce10
  title: GaN 系用错基晶格导致应变错误
  type: counter-example
  source_chapter: 手册第13章 (P256-257)
  source_quote: |
    "through dislocations and defects, the buffer layer may relax and it is not clear what the
    base lattice constant of the layers grown above this buffer layer should be."
  failure_mode: |
    默认基晶格=GaN，但实际缓冲层为 AlN/AlGaN（或已弛豫），应变张量、极化与能带全部算错。
  mechanism: |
    应变由层晶格相对基晶格失配决定；基晶格错选直接污染应变与所有应变相关物理。
  warning_signs:
    - 紫外器件 AlGaN/AlN 缓冲
    - 仿真增益/波长与实验系统性偏差
  bound_to:
    - "GaN 纤锌矿 MQW 建模"
  tags: [counter-example, gan, strain]

- id: ce11
  title: 极化 MQW 不开 self_consistent 当平带算
  type: counter-example
  source_chapter: 手册第13章 (P265-266)
  source_quote: |
    "Without this, the Schrodinger solver will assume a flat band profile."
  failure_mode: |
    GaN/InGaN 阱被 QCSE 弯曲却不自洽求解，波函数、增益谱、发射波长全部错误。
  mechanism: |
    极化界面电荷产生强局域场；忽略后能带平直，载流子重叠积分与跃迁能量失真。
  warning_signs:
    - 极化材料 MQW 仿真文件中无 self_consistent
  bound_to:
    - "GaN 纤锌矿 MQW 建模"
  tags: [counter-example, gan, quantum-well]

- id: ce12
  title: 默认简单 QW 模型处理深阱/极化器件高估开启电压
  type: counter-example
  source_chapter: 手册第4章 (P85) / 第8章 (P136-137)
  source_quote: |
    "Very deep and shallow QWs such as those found in nitride-based devices may block current
    if we assume that all carriers are thermalized (i.e. Drift-Diffusion model). This can
    manifest itself as an unrealistically high turn-on voltage."
  failure_mode: |
    默认假设载流子完全热化、阱孤立，深阱（氮化物）器件注入被低估，开启电压虚高。
  mechanism: |
    漂移-扩散 + 简单 QW 模型缺少非局域量子输运；需要 q_transport 或 complex/自洽模型。
  warning_signs:
    - 仿真开启电压远高于实验
    - 阱深/极化强的器件
  bound_to:
    - "量子阱模型选择"
    - "GaN 纤锌矿 MQW 建模"
  tags: [counter-example, quantum-well, gan]

- id: ce13
  title: 把 .gain 表格化折射率结果直接当主仿真结果
  type: counter-example
  source_chapter: 手册第16章 (P324-326)
  source_quote: |
    "during the preview of the round-trip gain provided by rtgain_phase, tabulated index change
    values are used to evaluate the propagation constant. This may differ from results in the
    main simulation."
  failure_mode: |
    用 .gain 预览的 RTG/波长数值断言最终器件特性，与主仿真（逐偏置计算）对不上。
  mechanism: |
    预览用表格化 index，主仿真用自洽计算的 index；越阈后偏差扩大。
  warning_signs:
    - 预览与主仿真波长/阈值明显不同
  bound_to:
    - ".gain 预览先行法"
  tags: [counter-example, gain, rtg, caution]

- id: ce14
  title: VCSEL section 标签交错导致腔长错误
  type: counter-example
  source_chapter: 手册第22章 (P473)
  source_quote: |
    "assigning a particular section label (e.g. 'b') to the barrier region and another to the
    well region (e.g. 'w') may result in the label sequence 'b w b' which would be an error and
    produce incorrect section lengths."
  failure_mode: |
    MQW 中每层各贴不同 vcsel_type 标签，软件不支持交错，产生错误 section 长度与纵模。
  mechanism: |
    section 按连续标签段聚合；交错标签无法正确聚合层组。
  warning_signs:
    - 复制粘贴层后标签交错
  bound_to:
    - "VCSEL 建模要点"
  tags: [counter-example, vcsel, geometry]

- id: ce15
  title: 热沉接触离自热区太近
  type: counter-example
  source_chapter: 手册第4章 (P80)
  source_quote: |
    "Another common case of non-convergence is in thermal simulations where an external heat
    resistor is attached to a contact which is too close to the self-heating region."
  failure_mode: |
    热仿真中外加热阻接触紧贴自热区，温度/边界突变导致不收敛。
  mechanism: |
    边界条件与热源在空间上冲突，解在接触点附近震荡。
  warning_signs:
    - 热仿真在接触-有源区附近发散
  bound_to:
    - "热效应建模"
  tags: [counter-example, thermal, convergence]

- id: ce16
  title: 多个软件版本安装同一目录
  type: counter-example
  source_chapter: 手册第2章 (P40)
  source_quote: |
    "you should never install multiple software packages in the same directory. This may cause
    version errors between files present in both versions."
  failure_mode: |
    DLL/同名文件被旧版覆盖，软件启动失败或行为异常。
  mechanism: |
    共享文件版本冲突，Windows 按目录解析依赖。
  warning_signs:
    - 升级后原有仿真无法运行
  bound_to:
    - "从示例项目出发逐步修改法"
  tags: [counter-example, installation]

- id: ce17
  title: 把 PICS3D 的 init_wave 当 LASTIP 用（设腔长/反射率）
  type: counter-example
  source_chapter: 手册第22章 (P444)
  source_quote: |
    "the two statements above replace some of the functionality provided by init_wave in LASTIP.
    If the user attempts to use it to define the cavity length or mirror strength, it will be
    ignored by the software."
  failure_mode: |
    PICS3D 中在 init_wave 里设腔长/镜面反射率，被软件静默忽略，腔参数仍来自 longitudinal/section。
  mechanism: |
    PICS3D 腔由 begin_zsol 的 longitudinal/section 定义；init_wave 只负责背景损耗与横向模式。
  warning_signs:
    - 修改 init_wave 的 cavity/reflection 后结果不变
  bound_to:
    - "PICS3D 激光仿真标准工作流"
    - "DFB/DBR 纵向模式"
  tags: [counter-example, pics3d, syntax]

- id: ce18
  title: 耦合量子阱当孤立阱算
  type: counter-example
  source_chapter: 手册第8章 (P143-145)
  source_quote: |
    "Quantum wells in an MQW system do not couple with each other. This is a reasonable
    approximation if the wells are far apart and the wave function decays significantly in
    the barriers."
  failure_mode: |
    阱间距小时默认模型忽略波函数重叠/耦合，子带分裂与载流子分配错误。
  mechanism: |
    默认简单 QW 模型假设孤立阱；近耦合阱必须用 complex MQW 宏（cx- 前缀）与 begin_complex。
  warning_signs:
    - 极薄垒层（<~5nm）MQW
  bound_to:
    - "量子阱模型选择"
  tags: [counter-example, quantum-well, coupling]
