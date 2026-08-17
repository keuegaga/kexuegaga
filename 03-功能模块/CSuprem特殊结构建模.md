---
title: CSuprem 特殊结构建模
type: function
product: CSuprem
module: CSuprem
version: "通用"
status: source
source: "[[99-原始资料/产品手册/csuprem_manual.pdf]] 第3/6章；[[99-原始资料/教程与问答/CSuprem_2D_tutorial.pdf]]；[[99-原始资料/教程与问答/CSuprem_3D_tutorial.pdf]]；C:\Csuprem\examples"
last_verified: 2026-08-17
tags:
  - crosslight
  - function
  - csuprem
---

# CSuprem 特殊结构建模

<!-- 一句话说明这个功能/模块是什么 -->

CSuprem 是 Crosslight 的 2/3 维工艺仿真器（源自 Stanford Suprem4），用"工艺步骤序列"（淀积/掩膜/刻蚀/注入/扩散/氧化）逐步"长"出复杂器件几何，而非手工绘制最终形状。

## 功能用途

解决 LayerBuilder/GeoEditor 难以表达的**特殊/复杂结构**：浅沟槽隔离（STI）、侧墙 spacer、刻蚀坡角、深沟槽、FinFET 鳍、3D 布局；并可复现工艺历史（掺杂再分布、应力）后导出给 APSYS 做器件仿真。

## 解决的问题

- 沟槽/坡角/悬空等"工艺形貌"无法用矩形图层描述
- 需要按真实工艺顺序复现掺杂分布（注入+退火）
- 3D 器件（MOSFET/FinFET）需要"版图 → 工艺 → 结构 → 器件"闭环
- 2D 已验证的结构需要低成本升级为 3D

## 使用条件

### 适用场景

- 结构形貌由工艺历史决定（STI、spacer、沟槽、坡角）
- 需要 3D 工艺结构并交给 APSYS
- 有 GDSII 版图要转成仿真结构

### 不适用场景

- 规则分层器件（FP 激光器、LED、普通二极管）——用 [[01-基础概念/Layer3d|Layer3d]]/LayerBuilder 直接建 `.layer` 更快更易收敛
- 只需要最终结构、不关心工艺历史

## 输入

| 输入项 | 类型 | 说明 | 示例 |
|---|---|---|---|
| 主输入 | .in | 网格骨架 + 工艺步骤序列 | `sti.in` |
| 平面文件 | .in | 3D 时每个 xy 平面一份 | `plane1.in` |
| z 方向定义 | zmesh.zst | 3D 平面位置（z_structure） | `zmesh.zst` |

## 输出

| 输出项 | 类型 | 说明 |
|---|---|---|
| 结构存档 | .str | 每一步形貌/掺杂（CrosslightView 查看） |
| 器件接口 | .aps | `export` 生成，APSYS 可读 |

## 工作原理

1. **网格线-区域-边界**：`line`（tag 句柄 + spacing 控密度）→ `region`（矩形材料区）→ `bound`（exposed/backside/reflecting 决定工艺作用面）→ `init`（衬底）。
2. **工艺步骤即结构演化**：淀积长材料、掩膜定窗口、刻蚀去材料、注入掺杂质、扩散/氧化热处理；复杂形貌由序列自然产生。
3. **3D = 一组 xy 平面 + z 方向定义**：平面文件用 2D 语法，`zmesh.zst` 的 `z_structure` 定义平面位置（zplanes=1）；`mode quasi3d`（快速验证）→ `three.dim`（全耦合）。
4. **导出链路**：`export` 写 `.aps` → APSYS `suprem_import=yes` + 逐平面 `begin_zmater`（suprem_property/suprem_contact 编号与 load_macro/contact 一致）。

## 关键参数

| 参数 | 含义 | 默认值 | 详见 |
|---|---|---|---|
| `mode` | quasi3d / three.dim 耦合模型 | - | [[05-API与命令/CSuprem结构语句]] |
| `etch` | 刻蚀模式（left/right/avoidmask/dry/segm） | - | [[05-API与命令/CSuprem结构语句]] |
| `zplanes` | 每段平面重复数（恒为 1 防氧化崩溃） | 1 | [[05-API与命令/CSuprem结构语句]] |
| `export xpsize` | 导出材料边界间隙 | 0.001 | [[05-API与命令/CSuprem结构语句]] |

## 最小示例

```text
line x loc=0.0 spacing=0.4 tag=lft
line x loc=34.0 spacing=0.4 tag=rht
line y loc=0.0 spacing=0.125 tag=top
line y loc=3.0 spacing=0.416667 tag=bot
region silicon xlo=lft xhi=rht ylo=top yhi=bot
bound exposed xlo=lft xhi=rht ylo=top yhi=top
bound backside xlo=lft xhi=rht ylo=bot yhi=bot
init boron conc=1.0e14 orient=100
```

完整 STI 示例见 [[06-案例/STI结构CSuprem输入]]。

## 限制与注意事项

> [!warning]
> - 文档面向硅 CMOS 工艺（2004-2014，Suprem4 血统）：无 GaN/光电器件工艺示例，材料宏与工艺参数需自行扩展；
> - 淀积只有纯几何模型，无物理沉积形貌；
> - CMP 无专用命令，用多边形刻蚀近似；
> - "2D 失败则 3D 必然失败"：先 2D 后 3D、先 quasi3d 后 three.dim。

## 与其他功能的关系

- 上游：GDSII 版图（GDS2MASK）/ 2D 已验证结构
- 下游：[[03-功能模块/VCSEL仿真配置|APSYS 器件仿真]]（.aps 导入）
- 相关：[[01-基础概念/GeoEditor]]（直接几何建模的替代路线）· [[01-基础概念/项目结构与文件类型]]

## 相关错误

[[07-故障排查/常见错误索引]]（网格/不收敛）；CSuprem 特有陷阱见 csuprem-complex-structure-modeling 技能的 B 段（etch 漏 segm=、编号不一致、avoidmask 无 mask 前置等）。

## 版本差异

| 版本 | 差异说明 |
|---|---|
| v2.0/v3.0 | 手册 2004-2014 更新；2D/3D 教程为 2008 |
| 2024 安装 | 本机 `C:\Csuprem`（Bin/examples 齐全），examples 含 STI/LDMOS/FinFET 等真实 deck |

## 来源

[[99-原始资料/产品手册/csuprem_manual.pdf]] 第 3/6 章；[[99-原始资料/教程与问答/CSuprem_2D_tutorial.pdf]]；[[99-原始资料/教程与问答/CSuprem_3D_tutorial.pdf]]；C:\Csuprem\examples（Process_flow_BCD、LDMOS STI、Tutorial_NMOS_2D/3D）

验证环境：Windows 本机，C:\Csuprem（Bin\csuprem.exe / SimuCSuprem）
