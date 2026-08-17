# Verified Units — Crosslight 通用手册（阶段 1.5 三重验证通过）

> 合并自 candidates/ 五个提取器产出（96 条候选 → 11 个方法论单元）。全部通过 V1 跨域 / V2 预测力 / V3 独特性。

---

- id: s01
  title: PICS3D 激光仿真标准工作流（三步偏置 + RTG 初始化）
  type: framework
  merged_from: [f01, f02, f06, f07, p02, p03, p10, p11, p22, p25, c01, c02, c03, c04, g04, g05, g06, g15, g21, ce04, ce09, ce13, ce17]
  V1_cross_domain:
    passed: true
    evidence:
      - 第4章 §4.2: 通用偏置策略要求 auto_finish=rtgain 前置
      - 第22章 §22.2 (DFB 相移激光): 完整三步流程 + rtgain_phase 预览
      - 第22章 §22.4 (三节 DBR): 多段场景同一流程
      - 第22章 §22.5 (VCSEL): 低阈值场景同一流程的变体
  V2_predictive_power:
    passed: true
    novel_question: "用户第一次用 PICS3D 仿真 GaN FP 激光器，扫描到阈值附近就发散，最可能漏了什么？"
    derived_answer: "漏了在开启 solve_rtg=yes 之前用 auto_finish=rtgain 的扫描完成纵向模式与光子密度初始化——这是 PICS3D 独有且强制的步骤；应回退到阈值下重建三步流程。"
  V3_exclusivity:
    passed: true
    why_not_common: "RTG 复值模式初始化、阈值下模式搜索与光子耦合开关是 Crosslight PICS3D 的专有方法论，任何通用仿真常识都不会覆盖。"

- id: s02
  title: 收敛故障诊断与对策工具箱
  type: framework
  merged_from: [f03, f11, f13, f14, f15, f17, f18, g18, g19, g20, c11, c12, ce01, ce02, ce03, ce06, ce08, ce15]
  V1_cross_domain:
    passed: true
    evidence:
      - 第4章 §4.1-4.14: 每种技巧独立成节（偏置/网格/变量/瞬态/辅助接触/带隙/宽禁带）
      - 第3章 §3.4.3: 网格排查流程
      - 第22章教程: 各示例的收敛参数设置（damping/max_step/auto_finish）
  V2_predictive_power:
    passed: true
    novel_question: "GaN 激光器在低偏置就报不收敛，且换网格没用，下一步怎么办？"
    derived_answer: "按排查树：先确认网格分布→改基本变量或加慢瞬态（var2=time）恢复位移电流→必要时用 bandgap_reduction 分阶段，最后验证技巧是否污染物理。"
  V3_exclusivity:
    passed: true
    why_not_common: "慢瞬态、易解器件、辅助接触归零、带隙降低分阶段等是 TCAD 数值实践的专门技法，且带物理污染的警告（只取最后一段 IV）。"

- id: s03
  title: GaN 纤锌矿 MQW 建模要点（极化/自洽/基晶格/晶面）
  type: framework
  merged_from: [p15, p16, p17, g09, g10, g11, g12, c06, ce10, ce11, ce12]
  V1_cross_domain:
    passed: true
    evidence:
      - 第13章 §13.1/13.5/13.6: 基晶格、极化、非/半极性晶面
      - 第4章 §4.8/4.10.4: 氮化物 MQW 收敛困难与 slow transient
      - 第8章 §8.2: 自洽载流子密度模型
  V2_predictive_power:
    passed: true
    novel_question: "GaN 激光器仿真出的波长比实验短很多，最可能查哪里？"
    derived_answer: "先查基晶格是否应改为 AlN/AlGaN 缓冲、是否开 self_consistent（QCSE 会红移）、是否独立 MQW 求解；再检查极化界面电荷与阱深设置。"
  V3_exclusivity:
    passed: true
    why_not_common: "纤锌矿基晶格歧义、极化电荷自动生成、每阱独立材料号是 GaN 体系专有且反直觉的坑。"

- id: s04
  title: DFB/DBR 纵向模式与光栅设计
  type: framework
  merged_from: [f10, g02, g22, c01, c03, ce17]
  V1_cross_domain:
    passed: true
    evidence:
      - 第16章 §16.5-16.8: 耦合波/传输矩阵/二阶光栅理论
      - 第22章 §22.2: 简化 κ + 相移；§22.4: grating_compos 显式光栅
      - 第16章 §16.11: 器件结构分类（FP/DFB/相移/啁啾/DBR/增益耦合）
  V2_predictive_power:
    passed: true
    novel_question: "DFB 激光器出现双模，想压边模应该动什么？"
    derived_answer: "增大 κL 或引入 1/4 波相移；若相移位置不对则用显式光栅法核对 κ 实虚部；用 RTG 谱确认主模在增益峰与光栅布拉格窗口内。"
  V3_exclusivity:
    passed: true
    why_not_common: "复值 κ 的增益耦合效应、相移/啁啾/增益耦合的等价性（都移动主模到带隙内）是手册的专门论述。"

- id: s05
  title: 电压/电流偏置策略与多电极控制
  type: framework
  merged_from: [f04, f08, p01, c03, ce03, ce08]
  V1_cross_domain:
    passed: true
    evidence:
      - 第4章 §4.1: 高阻/低阻、激射钳位
      - 第4章 §4.2: PICS3D 专用流程
      - 第22章 §22.4: 多电极共享地+分段电流
  V2_predictive_power:
    passed: true
    novel_question: "三电极 DBR 激光器同时调增益段和调谐段，电流符号和参考地怎么处理？"
    derived_answer: "先对共享底电极加小电压抬参考地，再对顶部电极用多个 scan 变量同时电流偏置（p 侧为负）；省略某电极变量则保持其电压。"
  V3_exclusivity:
    passed: true
    why_not_common: "激射钳位必须电流偏置、共享地技巧、auto_finish 双条件（auto2_finish）是手册级专有经验。"

- id: s06
  title: 增益与光谱预览（.gain 工作流）
  type: framework
  merged_from: [f06, p22, c01, ce13]
  V1_cross_domain:
    passed: true
    evidence:
      - 第3章 §3.6: .gain 预览全部物理量
      - 第22章 §22.2: RTG 预览依赖 .gain 表格化增益
      - 第16章 §16.7: tabulated index 与主仿真的差异警告
  V2_predictive_power:
    passed: true
    novel_question: "想快速评估新 InGaN 阱组分的增益峰波长，不跑完整仿真怎么办？"
    derived_answer: "生成 .gain 文件（include .mater），gain_wavel/sp.rate_wavel/index_wavel 预览增益与自发谱，必要时加 gain_density 找透明载流子密度；注意预览的 index 是表格化的。"
  V3_exclusivity:
    passed: true
    why_not_common: "先用专门输入文件做物理量预览再跑主仿真的两段式流程，及表格化 index 与主仿真差异的警告，是 Crosslight 特有。"

- id: s07
  title: 材料宏体系、单位与自定义覆盖
  type: framework
  merged_from: [f12, p04, p05, p06, p07, p20, p21, g03, g13, ce05]
  V1_cross_domain:
    passed: true
    evidence:
      - 第3章 §3.5: 被动/主动宏、默认宏不要改
      - 附录B: 宏语法、单位、覆盖规则、四元插值
      - 第22章教程: 宏选择错误是 InGaAsP 常见问题
  V2_predictive_power:
    passed: true
    novel_question: "用户的 AlGaN 宏参数比库里的新实验数据更准，怎么安全地用？"
    derived_answer: "复制宏到自定义 .mac 文件，use_macrofile 加载（放同目录），或在 .sol 中 load_macro 后重发 band_gap 等语句覆盖；绝不改默认宏。"
  V3_exclusivity:
    passed: true
    why_not_common: "被动/主动宏双轨体系、后发覆盖语义、m^-3/μm 单位制是 Crosslight 专有约定。"

- id: s08
  title: 网格生成与质量检查
  type: framework
  merged_from: [f05, p13, p14, p18, p19, ce01, ce02]
  V1_cross_domain:
    passed: true
    evidence:
      - 第3章 §3.4: 网格定义与故障排查
      - 第4章 §4.5/4.6: 过粗与过细两种失败模式
      - 第22章教程: 各示例网格参数（n/r/ratio）
  V2_predictive_power:
    passed: true
    novel_question: "脊形 GaN 激光器在电流拥挤区结果可疑，怎么定位是网格问题？"
    derived_answer: "先 .mplt 目检网格，确认脊角/界面/模式峰值区密度；局部 double_mesh 或 regrid 后重跑对比；若结果大幅变化说明网格未收敛。"
  V3_exclusivity:
    passed: true
    why_not_common: "低阻区过密网格导致 ΔV→0 电流失稳、void 与 vacuum 的边界物理差异是有限元实践的专业坑。"

- id: s09
  title: VCSEL 建模要点（section/驻波/圆柱坐标）
  type: framework
  merged_from: [f09, g13, c04, p23, ce14]
  V1_cross_domain:
    passed: true
    evidence:
      - 第17章: VCSEL 理论（横向/纵向/有效折射率）
      - 第22章 §22.5: 完整 VCSEL 教程与驻波增强
      - 第12章 §12.5: EIM
  V2_predictive_power:
    passed: true
    novel_question: "VCSEL 仿真 RTG 预览显示纵模离增益峰很远，改什么？"
    derived_answer: "按 λ/n 估算后迭代调 spacer 厚度，用 RTG 预览看 gfactor_stdwave 驻波增益增强，同时检查 DBR 周期层厚与反射率；避免 section 标签交错。"
  V3_exclusivity:
    passed: true
    why_not_common: "DBR 平均材料电学网格+显式周期光学传播、驻波增益增强因子、section 标签聚合限制是专有方法。"

- id: s10
  title: 量子阱模型分级与选择
  type: framework
  merged_from: [g08, g09, ce12, ce18]
  V1_cross_domain:
    passed: true
    evidence:
      - 第8章 §8.1: 简单/复杂/自洽三级 + valence mixing
      - 第8章 §8.2: 自洽模型
      - 第4章 §4.10.4: 深阱输运与 q_transport
      - 第13章: 纤锌矿 k.p
  V2_predictive_power:
    passed: true
    novel_question: "薄垒耦合 MQW 的增益谱形状不对，默认模型够吗？"
    derived_answer: "默认模型假设阱孤立；薄垒需 complex MQW（cx- 宏 + begin_complex/end_complex + type=strained_complex），极化体系再叠 self_consistent 与 valence_mixing。"
  V3_exclusivity:
    passed: true
    why_not_common: "模型分级（平带孤立→耦合→自洽）与每级适用/失效场景是器件物理的专业知识。"

- id: s11
  title: 后处理：数据组织、变量与绘图
  type: framework
  merged_from: [f16, p24, g16, g17]
  V1_cross_domain:
    passed: true
    evidence:
      - 第3章 §3.9/3.10: scan_data/xy_data 与数据集编号
      - 附录G: 变量表
      - 第22章教程: 各 .plt 文件（get_data/plot_scan/gain_spectrum）
  V2_predictive_power:
    passed: true
    novel_question: "用户想画纵向光子密度随电流的变化，但 plot_scan 里没有这个变量怎么办？"
    derived_answer: "查附录 G 确认变量名（如 rtg_2facet_power_allmode、wave_intensity）；若为缺省未输出变量，在 .sol 加 more_output 重跑；取数时注意 scan_data 与 xy_data 选择与数据集编号。"
  V3_exclusivity:
    passed: true
    why_not_common: "数据集编号体系、scan_data/xy_data 二分法与 more_output 开关是 Crosslight 的独特数据约定。"
