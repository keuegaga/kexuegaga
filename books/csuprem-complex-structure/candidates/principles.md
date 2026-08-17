# Principle Candidates — CSuprem 复杂结构设计建模

> 由主流程按 principle-extractor.md 串行提取（降级方案）。英文原文引用均来自 _source/ 提取文本。

- id: p01
  title: 2D 失败则 3D 必然失败
  type: principle
  source_chapter: 手册第 3 章 §3.5（PDF P31）
  source_quote: |
    "If a 2D simulation fails, the 3D simulation would certainly fail. In such a case, it is easier
     to fix the 2D problem first."
  summary: |
    3D 之前必须保证对应 2D（或关键平面）能收敛；2D 的问题必须先修完，不要在 3D 里定位 2D 错误。
  tags: [principle, verification, 3d]

- id: p02
  title: 先 quasi3d 快速验证，再 three.dim 全耦合
  type: principle
  source_chapter: 手册第 3 章 §3.3.2（PDF P30）
  source_quote: |
    "it is recommended that you use 'mode quasi3d' first. This would let you run through all the
     planes quickly. Sometime, poor initial mesh may cause a crash and it is better to find out
     while you are still doing quasi3d."
  summary: |
    全 3D 之前先用 quasi3d 把所有平面快速跑一遍，暴露网格/输入问题；性能与安全优先于精度。
  tags: [principle, 3d, verification]

- id: p03
  title: 淀积/注入全平面一致，刻蚀才逐平面
  type: principle
  source_chapter: 手册第 3 章 §3.3.2（PDF P30）
  source_quote: |
    "deposition and implantation are the same for all planes. Only etching can vary from plane to plane."
  summary: |
    设计 3D 工艺序列时默认淀积/注入统一执行；需要平面差异时只能靠 etch 加 segm=。
  tags: [principle, 3d, etch]

- id: p04
  title: zplanes=1 防氧化崩溃
  type: principle
  source_chapter: 3D 教程 P8 / 手册第 6 章
  source_quote: |
    "But we fix 'zplanes' equals 1 in Csuprem to make an uniform segment between 2 x-y planes,
     which helps preventing abnormal crash when doing simulation of 'oxidation' processing."
  summary: |
    CSuprem 中每个 z 段只放一个平面（zplanes=1），氧化等工艺才稳定；这是经验规则，不要随意改。
  tags: [principle, 3d, oxidation]

- id: p05
  title: 编号一致性契约（suprem_property ↔ load_macro ↔ suprem_contact ↔ contact）
  type: principle
  source_chapter: 3D 教程 P37-38
  source_quote: |
    "material names and numbers defined by 'load_macro' commands must be accordance with those
     defined by 'suprem_property' command."
  summary: |
    从 CSuprem 导入 APSYS 时，材料编号（suprem_property/load_macro）与接触编号（suprem_contact/contact）
    必须逐一对上；对不上就是静默映射错误。
  tags: [principle, apsys, interface]

- id: p06
  title: 不修改 zmesh.zst 的固定格式行
  type: principle
  source_chapter: 3D 教程 P9 / 手册第 6 章
  source_quote: |
    "output sol_outf=tmp.out
     export_3dgeo file=h_cvd.3dgeo
     These 2 lines are of fixed format, please do not modify them."
  summary: |
    zmesh.zst 中 output/export_3dgeo 两行是系统约定格式，用户只改 z_structure 与 load_mesh。
  tags: [principle, 3d, zmesh]

- id: p07
  title: 导出前检查网格（repair.mesh）
  type: principle
  source_chapter: 手册 §7.23 export（PDF P212）
  source_quote: |
    "repair.mesh: Csumpre will check whether it is necessary to repair mesh before export,
     so that it can make sure the mesh is correct"
  summary: |
    导出 .aps 前让程序自查网格完整性，避免把坏网格带进器件仿真。
  tags: [principle, export, mesh]

- id: p08
  title: 2D→3D 转换的机械步骤清单
  type: principle
  source_chapter: 手册第 3 章 §3.3.2-3.3.3（PDF P29-31）
  source_quote: |
    "1) use the following lines at the beginning: mode three.dim 3d_mesh nsegm=3 infile=mymesh
     2) find an existing template of zmesh.zst ... 3) Make 2 copies of each etch command and
     append segm=1,2,3 to all the etch commands"
  summary: |
    2D→3D 是清单化操作：开头加 mode/3d_mesh、准备 zmesh.zst、etch 逐 segm 复制；
    器件侧加 3d_solution_method、复制 z_structure、逐平面 begin_zmater。按清单做不会漏。
  tags: [principle, checklist, 3d]

- id: p09
  title: avoidmask 必须先有 mask
  type: principle
  source_chapter: 2D 教程 P20 / 手册 §7.22
  source_quote: |
    "etch avoidmask depth=0.9 nitride
     Must follow mask"
  summary: |
    avoidmask 型刻蚀依赖掩膜定义刻蚀窗口，必须先执行 mask 命令。
  tags: [principle, etch, mask]

- id: p10
  title: 规则分层器件不必用 CSuprem
  type: principle
  source_chapter: BOOK_OVERVIEW 批判 / 手册第 1 章
  source_quote: |
    "For an existing design, it is preferable to modify existing examples rather than starting from scratch."（BOOK_OVERVIEW 转述，见总览使用规则）
  summary: |
    CSuprem 的价值在"必须复现工艺历史"的结构；规则分层器件（激光器/LED）直接用 LayerBuilder/Layer3d
    定义 .layer 更快更易收敛，不应为了"复杂"而引入工艺仿真。
  tags: [principle, boundary, tool-choice]
