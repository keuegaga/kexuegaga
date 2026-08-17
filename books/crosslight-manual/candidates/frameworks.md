# Framework Candidates — Crosslight 通用手册

> cangjie-skill 阶段 1 产出（框架提取器）。候选未筛选，供阶段 1.5 三重验证。

- id: f01
  title: PICS3D 三步偏置初始化流程
  type: framework
  source_chapter: 手册第4章 (P77-79) / 第22章 (P444-447)
  source_quote: |
    "It is therefore required that the scan preceding the introduction of the photon coupling
    use the auto_finish=rtgain condition to terminate. This will calculate the positions of the
    longitudinal modes as well as provide an initial guess of the photon density in each mode."
  summary: |
    激光仿真必须按三步初始化：1) equilibrium 求平衡解；2) 电压扫描到内建电压的 80-90%（或用
    auto_finish 电流条件终止）；3) 电流扫描并以 auto_finish=rtgain 在阈值下终止（RTG 峰值略低于 1），
    然后才用 solve_rtg=yes 开启光子耦合继续扫描。原因：光子密度与增益/折射率分布（LSHB）互为因果，
    只能在光子密度≈0 的阈值下状态先定出纵向模式，再开启耦合。开启后必须用小偏置步长。
  tags: [pics3d, laser, workflow, convergence]

- id: f02
  title: 从示例项目出发逐步修改法
  type: framework
  source_chapter: 手册第3章 (P41)
  source_quote: |
    "it is preferable to use an existing project as a basis for your own simulations.
    Whenever possible, you should modify existing designs step by step to fit your needs
    rather than making an entirely new simulation from scratch."
  summary: |
    不要每次从空白搭建仿真。先在示例库找一个结构最接近的工程，用 SimuCenter 打开，逐层/逐参数
    修改成自己的设计。这样能复用已验证的网格、材料宏与偏置设置，避免重复踩坑，且每个改动点
    可单独验证。适用于所有 Crosslight 产品。
  tags: [workflow, best-practice, learning]

- id: f03
  title: 收敛调试的"简化-复现-加回"法
  type: framework
  source_chapter: 手册第4章 (P77)
  source_quote: |
    "the simpler the structure, the easier it is to debug. If possible, start from a simplified
    1D device that works and progressively iterate towards your final design until the
    convergence problem appears."
  summary: |
    遇到不收敛时，不要直接在复杂结构上试各种技巧。先把设备简化（降维 3D→2D→1D、去流阻层、
    关掉高级模型），找到一个能收敛的基线；然后逐步加回复杂度（材料、掺杂、几何、模型），
    直到问题复现，就能精确定位是哪个改动破坏了收敛。这是手册推荐的收敛排查总纲。
  tags: [convergence, debugging, workflow]

- id: f04
  title: 电压/电流偏置选择决策树
  type: framework
  source_chapter: 手册第4章 (P77-78)
  source_quote: |
    "Use voltage bias for devices with high resistance. Use current bias for devices with low
    resistance. ... under lasing conditions, the only way to perform the simulation properly
    is to use current controlled bias."
  summary: |
    偏置方式的选择：高阻区（反向、低偏、OLED/宽禁带、大接触电阻、太阳能/光电探测器）用电压偏置；
    低阻区（正向导通后）用电流偏置；任何激射器件必须电流偏置（载流子被钳位）。正偏二极管的标准
    策略：equilibrium → 电压到 80-90% 内建电压 → 检查 KCL → 电流偏置到目标。
  tags: [bias, decision, convergence]

- id: f05
  title: 网格"先看分布，再局部加密"流程
  type: framework
  source_chapter: 手册第3章 (P58) / 第4章 (P80-81)
  source_quote: |
    "An unsatisfactory mesh is a major cause of non-convergence. The first step to
    troubleshooting a mesh is to plot it as above and check that the mesh distribution is OK."
  summary: |
    网格调试流程：1) 用 .mplt 绘制网格目检；2) 找出剧变区（异质结、肖特基、掺杂突变、隧穿结、
    电流拥挤区、QW 波函数采样区、光模式峰值区）是否足够密；3) 用 r/ratio/shift_center 控制
    分布，用 double_mesh/half_mesh 局部加密；4) 仍不够再用 regrid 按材料参数变化自动加密；
    5) 若加密无效，简化结构复现问题。避免全器件均匀加密。
  tags: [mesh, convergence, workflow]

- id: f06
  title: ".gain 预览先行法"
  type: framework
  source_chapter: 手册第3章 (P63-64) / 第22章 (P446)
  source_quote: |
    "It is a good idea to process this file before the main simulation to optimize the gain
    curve peak vs. the grating's reference wavelength."
  summary: |
    在跑完整仿真前，先建立 .gain 文件预览增益谱、自发辐射谱、折射率变化谱、电流-载流子密度、
    alpha 因子与 QW 子带（k.p），并据此优化增益峰与光栅参考波长的对齐。PICS3D 的 RTG 预览
    直接使用 .gain 中的表格化增益数据；先跑 .gain 还能提前发现材料宏/成分设置错误。
  tags: [gain, preview, workflow, pics3d]

- id: f07
  title: RTG 预览定位腔模法
  type: framework
  source_chapter: 手册第22章 (P444-446)
  source_quote: |
    "PICS3D requires a preview of the RTG and longitudinal mode search with the rtgain_phase
    statement. ... it must be used before any actual bias is applied but after the equilibrium
    calculations."
  summary: |
    建立激光腔后，在 equilibrium 之后、加偏置之前用 rtgain_phase 以某个载流子密度做 RTG 预览：
    检查纵向模式波长与 RTG 分布（plot_rtgain），确认主模位置、相位、DBR 左右反射平衡等。
    可用 stop 语句停在预览后检查。这是"先验证腔设计、再跑完整仿真"的关键关口。
  tags: [rtg, mode-search, pics3d, debugging]

- id: f08
  title: 多段器件的"共享地 + 分段独立电流"偏置法
  type: framework
  source_chapter: 手册第22章 (P466-468)
  source_quote: |
    "we apply a small bias to the bottom shared electrode (#1) instead. This method shifts the
    reference ground and is equivalent to biasing all the top electrodes simultaneously."
  summary: |
    多电极/多段器件（如三节 DBR）：底部共享电极编号统一，顶部电极分段独立编号。先对共享底电极
    加小电压（等效整体抬参考地），避免电流流向最短路径；之后对每个顶部电极用多个 scan 变量
    同时电流偏置。省略某个电极变量时它保持上一状态电压。注意 p 侧电流为负号、画图时常需
    scale_horizontal=-1。
  tags: [pics3d, multi-electrode, bias, workflow]

- id: f09
  title: VCSEL spacer 迭代设计法
  type: framework
  source_chapter: 手册第22章 (P475-476)
  source_quote: |
    "it is common to use a quick rule (thickness = wavelength/n) when designing VCSELs.
    However, this approximation does not include the phase contribution from the DBR mirrors
    (penetration depth) ... choosing the spacer thickness is an iterative process."
  summary: |
    VCSEL 腔长由 spacer 厚度决定，先按 λ/n 估算，再用 RTG 预览（.sol）验证纵模位置与
    驻波增益增强因子（gfactor_stdwave），迭代调整 spacer 厚度与 DBR 周期，使纵模对准增益峰。
    DBR 用平均材料做电学网格、显式周期层做光学传播，可大幅省网格。
  tags: [vcsel, design, iteration, pics3d]

- id: f10
  title: 光栅建模的"简化 κ 与显式光栅"选择法
  type: framework
  source_chapter: 手册第22章 (P442, 459-463)
  source_quote: |
    "This method of defining the grating is the simplest and most convenient way available in
    PICS3D. More accurate models are available but they require an explicit definition of the
    grating composition in the layer file."
  summary: |
    DFB/DBR 光栅有两种建模路径：1) 简化法——在 section 里直接给 kappa_real/imag 与相移，
    快、适合初步设计与单模评估；2) 显式法——用 grating_compos/grating_model 定义高低折射率
    材料与厚度，让软件从折射率分布与模式重叠自动算 κ，适合精确设计、啁啾/增益耦合等。
    选择依据是需要的精度与对光栅物理细节的关注程度。
  tags: [grating, dfb, dbr, modeling, pics3d]

- id: f11
  title: 收敛问题三级排查树
  type: framework
  source_chapter: 手册第4章 (P75-89)
  source_quote: |
    "There are several possible causes of convergence difficulties: we have tried to discuss
    the most common problems and their solution in the following sections."
  summary: |
    不收敛时按顺序排查：第一级边界与网格（4.3-4.6：边界是否物理、网格疏密）；第二级偏置策略
    （4.1-4.2：电压/电流选择、PICS3D 的 RTG 初始化）；第三级数值技巧（4.7-4.14：基本变量切换、
    慢瞬态、初始猜测、辅助接触、带隙降低、迁移率模型、宽禁带 minority carrier）。先排除简单原因，
    再上技巧；技巧会改变物理，用后要验证结果。
  tags: [convergence, debugging, decision]

- id: f12
  title: 材料参数覆盖法（不碰默认宏）
  type: framework
  source_chapter: 手册第3章 (P60-61) / 附录B (P1280-1282)
  source_quote: |
    "it is STRONGLY recommended that the default macro files not be altered in any way since
    that would affect all the simulations that use these default files."
  summary: |
    需要自定义材料参数时：1) 用 use_macrofile 加载自己的宏文件（放同目录）；2) 或在 .sol 里
    load_macro 之后重新发出具体参数语句覆盖（后发覆盖先发）。绝不直接改 crosslight.mac / more.mac
    默认文件，否则影响所有仿真且难以追踪。改参数前先读宏头注释确认材料系与晶格匹配关系。
  tags: [material, macro, workflow, best-practice]

- id: f13
  title: 慢瞬态数值恢复法
  type: framework
  source_chapter: 手册第4章 (P82-83)
  source_quote: |
    "scan var=voltage_1 value=-3.5 var2=time value2_to=1.0 ... the time step is also small enough
    that the displacement current makes a numerically significant contribution to the current
    continuity equations."
  summary: |
    高阻/高掺杂复杂结构（尤其 GaN 极化 MQW）低偏置不收敛时，把偏置扫描加上时间变量
    （var2=time）：在 1 秒内缓慢升压，瞬态位移电流在数值上帮助电流连续性方程收敛到正确的
    稳态。原理：高绝缘区存在多个相似稳态，位移电流恢复了被稳态方程抹掉的物理路径。
  tags: [convergence, transient, technique]

- id: f14
  title: 辅助欧姆接触固定浮置区法
  type: framework
  source_chapter: 手册第4章 (P85-86)
  source_quote: |
    "we may add an auxiliary ohmic contact to be attached to a single mesh point in the isolated
    high resistant region. When we use voltage control on the auxiliary contact, the solver
    should be easier to converge."
  summary: |
    对远离边界的高阻浮置区（如反偏 p-n-i-p-n 的 i 区），变量会漂移导致不收敛。加一个接在单
    网格点上的辅助欧姆接触，用电压控制把它拉到合理电位稳定求解；达到目标偏置后改用电流控制
    把辅助接触电流归零，消除其对器件的真实影响。适用于击穿/高阻器件。
  tags: [convergence, contact, technique]

- id: f15
  title: 带隙降低分阶段法
  type: framework
  source_chapter: 手册第4章 (P86-87)
  source_quote: |
    "One technique is to artificially reduce the bandgap first, achieve the desired bias current
    and finally increase the semiconductor bandgap back to its original value."
  summary: |
    宽禁带材料（反向/泄漏电流极低）难以收敛时：先用 bandgap_reduction=0.2 降低带隙跑出目标
    电流，再保持电流不变把带隙恢复原值（电压会自动调整），最后单独做一段干净的电压回扫以获得
    正确的 IV。注意：带隙被改动过的扫描段 IV 是错的，只能画最后一段。
  tags: [convergence, wide-bandgap, technique]

- id: f16
  title: 输出数据组织导航法
  type: framework
  source_chapter: 手册第3章 (P72-73)
  source_quote: |
    "the output data is divided into two categories: bias-dependent data (scan_data) and
    structural/spectral data (xy_data). ... all output data is assigned a 'data set number'."
  summary: |
    理解 .out_#### 组织方式：偏置相关量（电流/电压/功率）在 scan_data，逐偏置点累积；结构与
    光谱量在 xy_data，按 print_step 间隔打印。数据集编号从 equilibrium 的 _0001 递增，可在
    .sol.msg 查每个数据集对应的偏置。取图前先确定要 scan_data 还是 xy_data 与编号，避免画错。
  tags: [post-processing, data, workflow]

- id: f17
  title: 宽禁带低漏电的"载流子垫高再还原"法
  type: framework
  source_chapter: 手册第4章 (P88-89)
  source_quote: |
    "One possible method ... would be to use set_minority_carrier to artificially increase the
    minority carrier until a high-current region can be reached. Later on, the current could be
    rescaled back to the original small value."
  summary: |
    GaN/SiC 等宽禁带材料的泄漏/反向电流比开启电流小 10 个数量级以上，双精度下矩阵病态。
    用 set_minority_carrier 人为抬高少数载流子跑出高流区，再按先前收敛参考重新标定电流；
    金属接触处电流守恒破坏时，可人为增大金属电阻率（对总电阻影响可忽略）。
  tags: [convergence, gan, wide-bandgap, technique]

- id: f18
  title: "易解器件"高偏置初始化法
  type: framework
  source_chapter: 手册第4章 (P83-85)
  source_quote: |
    "solve for an 'easy device' at high bias first. Then the solution from the 'easy device' is
    used to initialize the solution for the 'target device' at high bias."
  summary: |
    高掺杂流阻层结构（BH 激光器 n-p-n/p-n-p）低偏置本身就难收敛。构造网格/几何相同但流阻层
    轻掺杂的"易解器件"，把偏置直接冲到高值；再逐步把流阻层掺杂（new_doping）升到目标值，
    最后用电流偏置继续。避免"慢慢爬低偏置"这个本身失败的路径。
  tags: [convergence, current-blocking, technique]
