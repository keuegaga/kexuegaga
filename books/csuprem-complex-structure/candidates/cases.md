# Case Candidates — CSuprem 复杂结构设计建模

> 由主流程按 case-extractor.md 串行提取（降级方案）。英文原文引用均来自 _source/ 提取文本。

- id: c01
  title: 3D 教程完整 nMOSFET 14 步流程
  type: case
  source_chapter: 3D 教程 P14（步骤清单）、P15-33（图形演示）
  source_quote: |
    "1. 3D-STI 2. deposit gate oxide 3. channel implant 4. deposit gate poly 5. anneal after deposit
     6. etch some poly 7. anneal after deposit 8. ldd implant for source/drain 9. make spacer
     10. anneal in dry O2 atmosphere 11. final implant for source/drain 12. etch off oxide on source/drain
     13. ... left-mirror copy the structure to get a full MOSFET 14. export final structure to an APSYS-supported file"
  summary: |
    展示了从衬底到可导出的完整 3D 工艺流程：STI 六步（cover/decover/etch trench/pullback/fill/CMP）→
    栅氧 → 沟道注入 → poly 淀积/退火/刻蚀 → LDD → spacer → 干氧退火 → 源漏注入 → 接触窗 →
    mirror 镜像 → export。是"工艺步骤即结构演化"与"2D→3D→APSYS 链路"的完整示范。
  bound_to:
    - "工艺步骤即结构演化"
    - "2D→3D 转换方法论"
  outcome: 得到完整 MOSFET 结构并成功导出给 APSYS（教程后续演示 3D 器件仿真）。
  tags: [case, nmos, 3d, full-flow]

- id: c02
  title: LDD MOSFET 3D 输入 deck（etch 逐 segm + mirror + export）
  type: case
  source_chapter: 手册第 6 章 §6.2（PDF P146-148）
  source_quote: |
    "etch poly right p1.x=0.55 p1.y=-0.020 p2.x=0.45 p2.y=-0.55 segm=1
     etch poly right p1.x=0.55 p1.y=-0.020 p2.x=0.45 p2.y=-0.55 segm=2
     ...
     struct mirror left
     export outf=ldd.aps xpsize=0.0001 triangle.based=f"
  summary: |
    真实 LDD 3D 流程：3d_mesh nsegm=2 + zmesh.zst，栅氧/沟道注入/多晶硅淀积/退火，
    刻蚀多晶硅和 spacer 时对每个 segm 重复 etch 命令，最终 mirror + export ldd.aps。
    证明"淀积/注入全平面一致 + 刻蚀逐 segm + 镜像 + 导出"的标准组合。
  bound_to:
    - "平面差异化最小化原则"
    - "导出-对接链路"
    - "对称结构镜像复用"
  outcome: 生成 3D LDD 结构与掺杂分布图（图 6.3-6.5），可交 APSYS 器件仿真。
  tags: [case, ldd, segm, export]

- id: c03
  title: segr3d（z 方向 Si/SiO2 界面与隔离）
  type: case
  source_chapter: 手册第 6 章 §6.1.2（PDF P143-145）
  source_quote: |
    "mode three.dim
     3d_mesh nsegm=2 infile=gs zstfile=zmesh.zst
     init
     implant boron dose=3.0e14 energy=80.0
     struct outf=segr3d_1.str
     diff temp=1000 time=30"
  summary: |
    用两个 xy 平面文件（gs1.in 全硅、gs2.in 含 Si/SiO2 界面）演示 z 方向材料差异：
    界面平面产生隔离，30 分钟退火后硼分布与参考结构除旋转外一致，验证 3D 扩散/隔离实现正确。
  bound_to:
    - "3D = xy 平面 + z 方向定义"
    - "网格线-区域-边界三段式建模"
  outcome: 验证了 3D 扩散与隔离效应（图 6.1-6.2）。
  tags: [case, segregation, 3d]

- id: c04
  title: FinFET 逐段多边形刻蚀（独立栅）
  type: case
  source_chapter: 手册第 6 章 §6.4（PDF P156-158）
  source_quote: |
    "etch segm=2 oxide start x=0 y=-0.68
     etch segm=2 oxide continue x=0 y=0.
     etch segm=2 oxide continue x=2.6 y=0.
     etch segm=2 oxide done x=2.6 y=-0.68
     ...
     etch segm=3 poly start x=2.4 y=-0.98 ... done x=2.6 y=-0.98"
  summary: |
    独立栅 FinFET 把 5 个 z 段按角色分组（1/2/4/5 段整体刻蚀、第 3 段做精细多边形刻蚀），
    用 start/continue/done 定义矩形/多边形刻蚀窗口，逐段淀积 poly/nitride 再逐段去除。
    是"掩膜驱动的差异化 + 逐 segm 控制"的最复杂实例。
  bound_to:
    - "掩膜驱动的差异化"
    - "平面差异化最小化原则"
  outcome: 生成独立栅 FinFET 结构（图 6.9）。
  tags: [case, finfet, etch, segm]

- id: c05
  title: STI（浅沟槽隔离）六步成形
  type: case
  source_chapter: 3D 教程 P16-21（STI_01_cover 至 STI_06_CMP）
  source_quote: |
    "Step 1 STI_01_cover / STI_02_decover / STI_03_etch_trench / STI_04_pullback / STI_05_fill / STI_06_CMP"
  summary: |
    3D-STI 用"覆盖掩膜→揭开窗口→刻蚀沟槽→拉回→填充→CMP"六步造出隔离结构；
    沟槽形貌完全由掩膜+刻蚀+填充序列决定，是工艺步骤演化的典型。
  bound_to:
    - "工艺步骤即结构演化"
  outcome: 沟槽隔离结构成形，为后续栅氧/注入铺路。
  tags: [case, sti, isolation]

- id: c06
  title: 2D 教程直线刻蚀三连（left/right/dry）
  type: case
  source_chapter: 2D 教程 P16-19
  source_quote: |
    "etch oxide right p1.x=0.5
     etch oxide left p1.x=0.5
     etch dry nitride thick=1.5"
  summary: |
    用左/右直线刻蚀（p1 点定义线）和干法刻蚀（按厚度下切）快速得到台阶/窗口结构，
    演示最常用刻蚀组合的语义差异。
  bound_to:
    - "刻蚀是复杂结构设计的关键"
  outcome: 得到刻蚀台阶结构（教程图）。
  tags: [case, etch, 2d]

- id: c07
  title: 2D 教程淀积+掩膜+avoidmask 组合
  type: case
  source_chapter: 2D 教程 P13-15,20-21
  source_quote: |
    "deposit nitride thick=1 space=0.1
     mask thick=1 x1.from=0.1 x1.to=0.5 ...
     etch avoidmask depth=0.9 nitride"
  summary: |
    淀积（控制 space 密度）→ 光刻胶掩膜（多个窗口、右缘角度 theta）→ avoidmask 刻蚀，
    得到带坡角的刻蚀轮廓；演示"掩膜决定哪里动、刻蚀决定怎么动"。
  bound_to:
    - "掩膜驱动的差异化"
  outcome: 带 ±30° 坡角的刻蚀结构。
  tags: [case, mask, avoidmask]

- id: c08
  title: 3D→APSYS 器件仿真（suprem_contact 四接触 + 曲线族）
  type: case
  source_chapter: 3D 教程 P35-50
  source_quote: |
    "suprem_contact num=1 xrange=(-1.5 -1.4) side=upper touch_mater=1 ...
     contact num=1
     ... bias scan ... curve family"
  summary: |
    导入 .aps 后按段循环 begin_zmater 定义材料/接触，用 start_loop+scan 做双 Vg 的 Vd-Id 扫描，
    CrosslightView 画曲线族（负号与电流方向相关，Flip Y-Axis 调整）。完整跑通"工艺→器件→绘图"。
  bound_to:
    - "导出-对接链路"
  outcome: 得到两个 Vg 下的 Vd-Id 曲线族（教程图）。
  tags: [case, apsys, contact, curve-family]
