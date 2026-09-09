---
title: nakamura_light s2.layer 逐行注释（教学）
type: example
product: PICS3D
version: 2024
status: source
source: 'C:\Users\ciomp\Documents\2024Ver_pics3d_examples\pics3d_examples\blue_LD\nakamura_light\s2.layer（官方 Nakamura 蓝光 LD 示例）'
last_verified: 2026-09-09
tags:
  - crosslight
  - example
  - layer
  - tutorial
  - gan
---

# nakamura_light s2.layer 逐行注释（教学）

> 目的：给 PICS3D/.layer 零基础读者逐行读懂一个真实的 GaN 蓝光脊形激光器结构文件。原文件来自官方 Nakamura 示例（MRS 1997 结构），本文按行加注，术语先看「速查表」，再通读「逐行注释」。

## 先读懂三件事

1. **`.layer` 是"从下往上"生长**：第 1 层写在最下面（衬底/缓冲），最后写的层在顶面；材料由它前面的 `layer_mater` 指定。
2. **列（column）= 横向分区**：本器件有 3 列（脊体 4 µm + 两侧各 0.5 µm）。某些层只在 column 1 放材料、column 2/3 放 `air`/`void`，用来表示"这里被刻蚀掉了/是空气"，从而做出脊形截面。
3. **数字单位**：厚度/宽度 `µm`；掺杂 `m^-3`（`1e24 m^-3 = 1e18 cm^-3`）；`n=…` 是该层纵向网格点数（不是厚度）；`In 0.15` = In₀.₁₅Ga₀.₈₅N。

## 语句速查表（本文件用到）

| 语句/参数 | 含义 |
|---|---|
| `$` | 注释符：`$` 开头整行被忽略 |
| `&&` | 续行符：一行写不下时用 |
| `begin_layer … end_layer` | `.layer` 文件的起止封装 |
| `independent_mqw` | 多量子阱中每阱用独立材料号（逐阱可不同组分/场，GaN 极化器件常用） |
| `column column_num=1 w=4.0 mesh_num=20 r=-1.1` | 第 1 列：宽 4 µm、横向网格点 20、网格比 r |
| `top_contact column_num=… from=… to=… contact_num=…` | 在该列顶部 x∈[from,to] 放顶部电极并编号 |
| `layer_mater macro_name=gan column_num=1` | 给第 1 列**接下来这一层**指定材料宏 gan（GaN） |
| `macro_name=ingan/algan/air/void` | 材料宏：InGaN/AlGaN；air=空气、void=空（用于刻蚀/绝缘侧区） |
| `layer d=2.3 n=50 r=-1.01 n_doping1=5.e24` | 一层：厚 2.3 µm、纵向网格 50、网格比 r、第 1 列 n 型掺杂 5e24 m^-3 |
| `n_doping1/2/3` | 分别给 column 1/2/3 设 n 掺杂；`p_doping1` 为 p 掺杂 |
| `var_symbol1=x var1=0.05` | 把宏的组分变量设成 x=0.05（如 In₀.₀₅Ga₀.₉₅N） |
| `grade_var=1 grade_from=0 grade_to=0.05` | 组分渐变：x 从 0 渐变到 0.05（避免突变界面） |
| `active_macro=InGaN/InGaN avar1=… avar2=…` | 有源区主动宏：阱/垒组分 |
| `include file=s2.qw / s2.bar` | 把阱/垒定义文件的内容就地展开（循环写出 MQW） |
| `adjust_doping level=0.02` | 按 level 自动调整该层掺杂（示例简化设置用；细节以手册为准） |

## 逐行注释

> 说明：为方便对照，注释行（`$ …`）插在对应语句上方；相同的"air/void 侧列"组合在后续出现时注释从简。

```text
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ 文件头：说明结构出处（Shuji Nakamura, MRS 1997 蓝光激光器）
$Device structure from
$MRS Int. Jour. of Nitride Semic. Res.,
$Vol. 2, Articl 5 , 1997;   http://nsr.mij.mrs.org/2/5/
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
begin_layer
$ ↑ .layer 内容开始

independent_mqw
$ ↑ 开启"每阱独立材料号"（多层阱各算各的，GaN 极化 MQW 需要）
column column_num=1 w=4.0  mesh_num=20  r=-1.1
$ ↑ 第 1 列：宽 4 µm（脊体）；横向 20 个网格点；r=-1.1 表示网格间距按 1.1 倍渐变、向一侧加密
column column_num=2 w=0.5  mesh_num=8  r=-1.1
$ ↑ 第 2 列：宽 0.5 µm（脊左侧区）；横向 8 点
column column_num=3 w=0.5  mesh_num=5  r=1.1
$ ↑ 第 3 列：宽 0.5 µm（脊右侧区）；横向 5 点
$
top_contact column_num=1 from=0.0 to=4. contact_num=2
$ ↑ 第 1 列顶部 x∈[0,4] 放电极，编号 2（脊顶，配合上方 p 层做 p 侧电极）
top_contact column_num=3 from=0.0 to=0.5 contact_num=1
$ ↑ 第 3 列顶部 x∈[0,0.5] 放电极，编号 1（与几何/掺杂配合，作另一侧电极）
$
layer_mater macro_name=gan column_num=1
layer_mater macro_name=gan column_num=2
layer_mater macro_name=gan column_num=3
$ ↑ 下面这层：3 列都用 GaN
layer d=2.3 n=50 r=-1.01 n_doping1=5.e24 n_doping2=5.e24 n_doping3=5.e24
$ ↑ 厚 2.3 µm 的 n-GaN（衬底+下限制层）：纵向 50 点；3 列 n 掺杂均 5e24 m^-3（=5e18 cm^-3）

$
layer_mater macro_name=gan column_num=1
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
$ ↑ 下面这层只在第 1 列有 GaN；第 2/3 列放 air/void → 表示侧向已被刻蚀/绝缘，脊形开始
layer d=0.7  n=20   r=-1.1 n_doping1=5.e24
$ ↑ 厚 0.7 µm 的 n-GaN（脊下部分），仅列 1 有材料与掺杂
$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ ↓ 以下一段是 n 侧"波导/限制"区：用 InGaN/AlGaN 组分渐变层把材料从 GaN 平滑过渡到有源区
layer_mater macro_name=ingan column_num=1 var_symbol1=x &&
  grade_var=1 grade_from=0 grade_to=0.05
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.001 n=5  r=-1.1 n_doping1=5.e24
$ ↑ 1 nm 渐变层：In 组分 x 0→0.05（GaN→In₀.₀₅Ga₀.₉₅N），列 2/3 仍是 air/void

layer_mater macro_name=ingan  var1=0.05 column_num=1 var_symbol1=x
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.1 n=10  r=-1.1 n_doping1=5.e24
$ ↑ 100 nm 的 In₀.₀₅Ga₀.₉₅N（n 侧 SCH 波导层）

layer_mater macro_name=ingan column_num=1 var_symbol1=x &&
  grade_var=1 grade_from=0.05 grade_to=0.0
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.001 n=5  r=-1.1 n_doping1=5.e24
$ ↑ 1 nm 渐变层：In 0.05→0（回到 GaN 附近）

layer_mater macro_name=algan column_num=1 var_symbol1=x &&
  grade_var=1 grade_from=0 grade_to=0.08
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.001 n=5  r=-1.1 n_doping1=5.e24
$ ↑ 1 nm 渐变：Al 组分 0→0.08（GaN→Al₀.₀₈Ga₀.₉₂N）

$
layer_mater macro_name=algan var1=0.08 column_num=1 var_symbol1=x
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.5 n=15  r=-1.1 n_doping1=1.e24
$ ↑ 500 nm Al₀.₀₈Ga₀.₉₂N（n 侧限制/刻蚀保护层），n 掺杂 1e24 m^-3

layer_mater macro_name=algan column_num=1 var_symbol1=x &&
  grade_var=1 grade_from=0.08 grade_to=0.0
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.001 n=5  r=-1.1 n_doping1=5.e24
$ ↑ 1 nm 渐变：Al 0.08→0
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$
layer_mater macro_name=gan column_num=1
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.09 n=10  r=-1.1 n_doping1=5.e23
$ ↑ 90 nm GaN（进入有源区前的间隔层），n 掺杂降到 5e23 m^-3
$
$    ***********  MQW x 3 **************
$ 注释写 MQW x 3；实际由下面 include 展开为 5 阱（以文件实行为准）
$ we shall start with barrier.
$
layer_mater macro_name=ingan var1=0.02 column_num=1 var_symbol1=x
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.01 n=10  r=1 n_doping1=0.8e23
$ ↑ 第一个垒：10 nm In₀.₀₂Ga₀.₉₈N（In 2%），n 掺杂 8e22 m^-3
$
include file=s2.qw
$ ↑ 展开 s2.qw（1 个量子阱：In₀.₁₅Ga₀.₈₅N 3.5 nm，见文件下方说明）
include file=s2.bar
$ ↑ 展开 s2.bar（1 个垒：In₀.₀₂Ga₀.₉₈N 7 nm）
include file=s2.qw
include file=s2.bar
include file=s2.qw
include file=s2.bar
include file=s2.qw
include file=s2.bar
include file=s2.qw
$ ↑ qw/bar 交替共展开 5 阱 + 4 垒（连同首尾手写垒 → 5 阱 6 垒）
$
layer_mater macro_name=ingan var1=0.02 column_num=1 var_symbol1=x
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.01 n=10  r=-1.1 n_doping1=0.8e23
$ ↑ 末垒：10 nm In₀.₀₂Ga₀.₉₈N
$    ***********************************
$
$ ↓ 有源区之后进入 p 侧：先渐变回 GaN，再上 AlGaN p 限制层
layer_mater macro_name=ingan column_num=1 var_symbol1=x &&
  grade_var=1 grade_from=0.02 grade_to=0.0
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.001 n=5  r=-1.1 p_doping1=1e24
$ ↑ 1 nm 渐变：In 0.02→0；本层起改为 p 掺杂 1e24 m^-3

layer_mater macro_name=algan column_num=1 var_symbol1=x &&
  grade_var=1 grade_from=0 grade_to=0.2
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.001 n=5  r=-1.1 p_doping1=1.e24
$ ↑ 1 nm 渐变：Al 0→0.2
$
layer_mater macro_name=algan var1=0.2  column_num=1 var_symbol1=x
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.01  n=10  r=-1.1 p_doping1=5e24
$ ↑ 10 nm Al₀.₂Ga₀.₈N（p 侧电子阻挡层 EBL），p 掺杂 5e24 m^-3
$
layer_mater macro_name=algan column_num=1 var_symbol1=x &&
  grade_var=1 grade_from=0.2 grade_to=0.0
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.001 n=5  r=-1.1 p_doping1=5.e24
$ ↑ 1 nm 渐变：Al 0.2→0

layer_mater macro_name=gan  column_num=1
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.1  n=10   r=-1.1 p_doping1=1.e25
$ ↑ 100 nm p-GaN（p 侧波导），p 掺杂 1e25 m^-3
$

layer_mater macro_name=algan column_num=1 var_symbol1=x &&
  grade_var=1 grade_from=0.0 grade_to=0.08
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.001 n=5  r=-1.1 p_doping1=1.e25
$ ↑ 1 nm 渐变：Al 0→0.08

layer_mater macro_name=algan var1=0.08  column_num=1 var_symbol1=x
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.5  n=15  r=-1.1 p_doping1=5.e25
$ ↑ 500 nm Al₀.₀₈Ga₀.₉₂N（p 侧限制层），p 掺杂 5e25 m^-3
$
layer_mater macro_name=algan column_num=1 var_symbol1=x &&
  grade_var=1 grade_from=0.08 grade_to=0.0
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.001 n=5  r=-1.1 p_doping1=5.e25
$ ↑ 1 nm 渐变：Al 0.08→0

$
layer_mater macro_name=gan column_num=1
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.3  n=15  r=-1.1  p_doping1=1.e26
$ ↑ 300 nm p-GaN 盖层（重掺杂 1e26 m^-3 = 1e20 cm^-3，改善 p 接触）
$
end_layer
$ ↑ .layer 内容结束
```

## s2.qw / s2.bar（被 include 的阱/垒定义）

```text
===== s2.qw（一个量子阱）=====
layer_mater macro_name=ingan var1=0.15 column_num=1 &&   ← 阱材料 In₀.₁₅Ga₀.₈₅N
  var_symbol1=x &&
  active_macro=InGaN/InGaN  avar1=0.15 avar2=0.02 &&      ← 有源区宏：阱组分 0.15、垒组分 0.02
  avar_symbol1=xw avar_symbol2=xb
adjust_doping level=0.02                                  ← 自动调整掺杂（示例简化用）
layer_mater macro_name=air column_num=2
layer_mater macro_name=void column_num=3
layer d=0.0035 n=10  r=1 n_doping1=0.8e23                 ← 阱厚 3.5 nm

===== s2.bar（一个垒）=====
layer_mater macro_name=ingan var1=0.02 column_num=1 ...   ← 垒材料 In₀.₀₂Ga₀.₉₈N
adjust_doping level=0.02
layer d=0.007 n=10  r=1 n_doping1=0.8e23                  ← 垒厚 7 nm
```

## 结构纵览（自底向上）

```text
p-GaN 0.3 µm (1e20)            ← 顶
AlGaN 0.5 µm (p, EBL→p-clad)
GaN 0.1 µm (p)
AlGaN EBL / 渐变层
MQW：5×(InGaN 阱 3.5nm / InGaN 垒 7nm)
n-GaN 0.09 µm + 渐变/SCH 层
n-AlGaN 0.5 µm / n-InGaN 0.1 µm（波导）
n-GaN 2.3 µm（衬底/缓冲）      ← 底（第 1 层）
```

## 运行与验证

```bat
cd /d C:\Users\ciomp\Documents\2024Ver_pics3d_examples\pics3d_examples\blue_LD\nakamura_light
c:\crosslig\pics3d\layer.exe s2.layer        → 生成 s2.geo/.mater/.doping/.mplt
c:\crosslig\pics3d\pics3d.exe s2.gain        → 增益预览
c:\crosslig\pics3d\pics3d.exe s2.geo         → 生成网格 s2.msh
c:\crosslig\pics3d\pics3d.exe s2.sol         → 主求解
```

验证：`s2.geo`/`s2.msh` 正常生成、CrosslightView 打开结构可见脊形与 MQW、求解日志无错误。

## 相关笔记

[[01-基础概念/项目结构与文件类型]] · [[01-基础概念/mater_define]] · [[03-功能模块/CSuprem特殊结构建模|CSuprem 复杂结构建模]]（对照：本文件是 LayerBuilder 直接定义，非工艺仿真）
