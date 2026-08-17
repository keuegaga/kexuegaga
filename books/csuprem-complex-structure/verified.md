# 通过三重验证的单元（阶段 1.5 产出）

> 候选池共 72 条（frameworks 10 / principles 10 / cases 8 / glossary 12 / counter-examples 32）。
> 独立成 skill 的只有 1 个单元集（复杂结构设计建模），其余作为该 skill 的 A1/B 证据池。

## 核心单元（进入 skill 的 R/I/A2/E/B）

### U1 网格线-区域-边界三段式建模（f01 + f10 tag 句柄化 合并）

```yaml
V1_cross_domain:
  passed: true
  evidence:
    - 2D 教程 P8-10：line/region/bound 命令演示
    - 3D 教程 P5-6：同一语法用于每个 xy 平面文件
    - 手册第 7 章：line/region/bound 语句参考 + 全部示例 deck
V2_predictive_power:
  passed: true
  novel_question: "拿到一个全新器件（如 GaN 激光器），从哪开始建？"
  derived_answer: "先规划 x/y 网格线（给关键界面打 tag），再圈 region，再声明 bound，最后 init——三步骨架先行。"
V3_exclusivity:
  passed: true
  why_not_common: "这不是'画图'常识，而是 CSuprem 独有的矩形网格-区域语法，tag 句柄化是库内可维护性机制。"
```

### U2 工艺步骤即结构演化（f02）

```yaml
V1_cross_domain:
  passed: true
  evidence:
    - 2D 教程 P13-29：deposit/mask/etch/implant/diffuse 逐步演示
    - 3D 教程 P14：nMOSFET 14 步流程
    - 手册第 1 章：capabilities 清单
V2_predictive_power:
  passed: true
  novel_question: "侧墙 spacer 是怎么来的？"
  derived_answer: "淀积保形层（deposit oxide）+ 干法回刻（etch dry 到固定厚度）两步，而不是'画一个梯形'。"
V3_exclusivity:
  passed: true
  why_not_common: "把结构当工艺历史的结果而非最终几何，是工艺仿真区别于直接建模的核心视角。"
```

### U3 2D→3D 转换方法论（f03 + p02/p08 合并）

```yaml
V1_cross_domain:
  passed: true
  evidence:
    - 手册 §3.3.2：2D 工艺文件转 3D 三步
    - 手册 §3.3.3：2D 器件文件转 3D 五步
    - 3D 教程 P4-13：xy 平面 + zmesh.zst + mode/3d_mesh 组装
    - 手册第 6 章：segr3d/LDD/FinFET 全部先定义平面再 3D
V2_predictive_power:
  passed: true
  novel_question: "已有 gaas10 这类 2D 激光器 .layer/.geo，想转 3D 怎么办？"
  derived_answer: "CSuprem 路径：建 xy 平面文件→zmesh.zst 定义 z 位置→etch 逐 segm 复制→quasi3d 验证→three.dim；这与 LayerBuilder/Layer3d 的 z_segment 路径并存，但工艺历史类结构只能走前者。"
V3_exclusivity:
  passed: true
  why_not_common: "先 quasi3d 后 three.dim、etch 逐 segm、淀积/注入全平面一致——是手册独有的可操作清单，不是常识。"
```

### U4 平面差异化最小化（f04 + p03）

```yaml
V1_cross_domain:
  passed: true
  evidence:
    - 手册 §3.3.2：原文"Only etching can vary from plane to plane"
    - LDD 实例（PDF P147）：etch 逐 segm=1,2 而 deposit/implant 全局一次
    - FinFET 实例（PDF P156-158）：逐段刻蚀 poly/nitride
V2_predictive_power:
  passed: true
  novel_question: "3D 里想让某一段的氧化层更厚，怎么实现？"
  derived_answer: "不能靠 deposit 逐段，只能先全平面淀积再对目标段 etch 差异化（或调整该平面区域），因为淀积/注入语法不支持逐平面。"
V3_exclusivity:
  passed: true
  why_not_common: "明确指出'哪种工艺可逐平面、哪种不能'是可执行约束，避免用户走弯路。"
```

### U5 GDSII 平面先过 2D 验证（f05 + p01）

```yaml
V1_cross_domain:
  passed: true
  evidence:
    - 手册 §3.5：GDS2MASK 建议 + "2D 失败则 3D 必然失败"
    - 手册 §3.3.2：quasi3d 先行建议（同一验证思想的两个场景）
V2_predictive_power:
  passed: true
  novel_question: "GDSII 布局里有个可疑的切面，怎么低成本判断它能不能仿真？"
  derived_answer: "把该平面单独导出为 2D 输入跑一次；不收敛就改网格/结构，而不是直接提交 3D 任务。"
V3_exclusivity:
  passed: true
  why_not_common: "'平面即最小验证单元'把 3D 的不可调试性拆成 2D 问题，是反直觉的务实原则。"
```

### U6 网格质量杠杆（f06）

```yaml
V1_cross_domain:
  passed: true
  evidence:
    - 2D 教程 P8-9,12：spacing 与 elimine 演示
    - 3D 教程 P5-6：spacing 控制插入密度
    - 手册 §7.20-7.21,7.24：double_mesh/eliminate/extend 语句
V2_predictive_power:
  passed: true
  novel_question: "斜注入导致边缘网格不够怎么办？"
  derived_answer: "用 extend 临时外扩网格包含器件边缘，注入后再收缩——而不是整体加密。"
V3_exclusivity:
  passed: true
  why_not_common: "具体杠杆（spacing/elimine/double_mesh/extend + 矩形区域限定）是 CSuprem 特有工具链。"
```

### U7 掩膜驱动的差异化（f08 + p09）

```yaml
V1_cross_domain:
  passed: true
  evidence:
    - 2D 教程 P15,20-21：mask 多窗口 + avoidmask 坡角
    - 2D 教程 P16-19：left/right/dry 刻蚀
    - FinFET 实例：掩膜决定逐段刻蚀
V2_predictive_power:
  passed: true
  novel_question: "要做一个 V 形沟槽（坡角 30°），命令怎么写？"
  derived_answer: "mask 里给窗口右缘设 right.theta=30，再 etch avoidmask depth=...，而不是手动画三角形刻蚀。"
V3_exclusivity:
  passed: true
  why_not_common: "avoidmask/theta/必须先行 mask 的约束是 CSuprem 特有知识。"
```

### U8 导出-对接链路（f07 + p05/p07）

```yaml
V1_cross_domain:
  passed: true
  evidence:
    - 3D 教程 P35-39：suprem_property/suprem_contact/begin_zmater 全链路
    - 手册 §7.23：export 语句（xpsize/triangle.based/repair.mesh）
    - LDD 实例：export outf=ldd.aps
V2_predictive_power:
  passed: true
  novel_question: "导入 .aps 后器件仿真报'材料未定义'，先查哪里？"
  derived_answer: "核对 suprem_property 的材料编号与 load_macro 是否一致、begin_zmater 是否覆盖所有 zseg_num——编号契约是链路最常见断点。"
V3_exclusivity:
  passed: true
  why_not_common: "suprem_* 系列与 z_structure 逐段 begin_zmater 是 CSuprem↔APSYS 独有的接口契约。"
```

## 证据池（不独立成 skill，供 A1/B 引用）

### 案例池（cases c01-c08，全部通过 V1 佐证）

- c01 nMOSFET 14 步全流程 → U2/U3/U8
- c02 LDD 3D deck（etch 逐 segm + mirror + export）→ U3/U4/U8
- c03 segr3d（z 方向 Si/SiO2 界面）→ U1/U3
- c04 FinFET 逐段多边形刻蚀 → U4/U7
- c05 STI 六步成形 → U2
- c06 2D 直线刻蚀三连 → U7
- c07 淀积+掩膜+avoidmask 组合 → U7
- c08 3D→APSYS 曲线族 → U8

### 反例池（counter-examples 32 条中通过 V1 的核心反例，进 B 段）

- ce-3d-before-2d：不先 2D/quasi3d 验证直接全 3D
- ce-etch-missing-segm：etch 漏 segm= 逐平面复制
- ce-deposit-per-plane：误以为淀积/注入可逐平面不同
- ce-zplanes：zplanes≠1 氧化崩溃
- ce-numbering：suprem_property/load_macro/suprem_contact/contact 编号不一致
- ce-zmesh-fixed：修改 zmesh.zst 固定格式行
- ce-bound-exposed：漏设 bound exposed（教程点名"最常见错误"）
- ce-avoidmask-order：avoidmask 无 mask 前置
- ce-misuse-csuprem：规则分层器件误用 CSuprem（LayerBuilder 更快）

## 淘汰单元（详见 rejected/）

- f10（tag 句柄化）：并入 U1，不独立成 skill
- p04（zplanes=1）：保留为 U3 的判停条件，不独立
- p06（不修改 zmesh.zst 固定行）：并入 U8 清单
- p10（规则分层器件不必用 CSuprem）：作为 B 段边界原则保留，不独立
- 其余 20+ 条反例：重复/过细，合并进上述核心反例
