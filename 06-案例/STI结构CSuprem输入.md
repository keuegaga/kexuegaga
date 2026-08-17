---
title: STI 结构的 CSuprem 输入
type: example
product: CSuprem
version: "通用"
status: draft
source: "C:\Csuprem\examples\Process_Flow\Process_flow_BCD\BCD.in + testflow2.msk；C:\Csuprem\examples\LDMOS\LDMOS_III_with_Nepi_STI\LDMOS.in；csuprem-complex-structure-modeling 技能"
last_verified: 2026-08-17
---

# STI 结构的 CSuprem 输入

## 目标

用 CSuprem 工艺仿真建一个浅沟槽隔离（STI）结构：衬底 → 垫氧/氮化硅 → 沟槽刻蚀 → 衬垫氧化 → 氧化物填充 → 平面化（CMP 近似）→ 剥离垫层。

## 路线说明

STI 的形貌由工艺历史决定（掩膜+刻蚀+填充），属于复杂结构建模，走 CSuprem 工艺路线（不使用 LayerBuilder 直接画）。本案例为 2D 版；转 3D 的步骤见文末。

## 输入文件（sti.in，自包含）

```text
$file:sti.in
$ ========== 1. 网格骨架（line → region → bound → init） ==========
line x loc=0.0  spacing=0.40 tag=lft
line x loc=3.0  spacing=0.05
line x loc=9.0  spacing=0.05
line x loc=10.0 spacing=0.05
line x loc=34.0 spacing=0.40 tag=rht
line y loc=0.0 spacing=0.125 tag=top
line y loc=1.0 spacing=0.125
line y loc=3.0 spacing=0.416667 tag=bot

region silicon xlo=lft xhi=rht ylo=top yhi=bot
bound exposed xlo=lft xhi=rht ylo=top yhi=top
bound backside xlo=lft xhi=rht ylo=bot yhi=bot

init boron conc=1.0e14 orient=100

option auto.mesh.implant=false
option auto.mesh.diffuse=false
option deposit.mesh.ratio=0.1

$ ========== 2. STI 工艺流程 ==========
$ 2.1 垫氧化层（湿氧）
diffuse temp=900 time=15 weto2
structure outf=01_pad_oxide.str

$ 2.2 氮化硅垫层
deposit nitride thick=0.08 temp=800 meshlayer=2
structure outf=02_nitride_pad.str

$ 2.3 沟槽刻蚀：掩膜（2° 侧墙坡角）→ avoidmask 依次刻氮化硅/氧化硅/硅
mask thick=1. x1.from=0. x1.to=3. x1.left.theta=2. x1.right.theta=2. && x2.from=9. x2.to=10. x2.left.theta=2. x2.right.theta=2.
etch nitride avoidmask depth=0.1
etch oxide   avoidmask depth=0.1
etch silicon avoidmask depth=0.3
etch photoresist all
structure outf=03_trench.str

$ 2.4 STI 衬垫氧化（干氧）
diffuse temp=1000 time=10 dryo2
structure outf=04_liner.str

$ 2.5 HDP 氧化物填充
deposit oxide thick=0.5 meshlayer=5 space=0.01
structure outf=05_fill.str

$ 2.6 CMP 平面化（多边形刻蚀近似，切平到氮化硅顶面附近）
etch start x=0   y=-20
etch continue x=0   y=-4.95
etch continue x=34  y=-4.95
etch done x=34  y=-20
structure outf=06_cmp.str

$ 2.7 剥离垫氧/氮化硅
etch nitride all
structure outf=07_sti_done.str

$ ========== 3. （可选）导出给 APSYS ==========
activation.mode boron fraction=1 force.activation=t
export outf=sti.aps xpsize=0.001
```

## 运行方式

```bat
cd /d D:\projects\sti
C:\Csuprem\Bin\csuprem.exe sti.in
```

或用 SimuCSuprem GUI 打开 `sti.in` 逐句执行。注：命令行调用形式以本机安装版 README 为准（未在本机实测）。

## 预期输出

- 每步生成 `0X_*.str` 结构文件（可用 CrosslightView 打开 `File → Open File` 查看形貌与掺杂）；
- 最终 `07_sti_done.str`：沟槽区被氧化物填充、顶面切平、垫层剥离；
- 若执行导出段，生成 `sti.aps`（APSYS 可读）。

## 验证清单

- [ ] 2D 全流程无报错，逐步结构文件生成
- [ ] 沟槽深度约 0.3 µm、侧墙约 2° 坡角（mask 的 theta）
- [ ] 填充后顶面平整（CMP 段）
- [ ] 垫氧/氮化硅剥离干净
- [ ] 需要 3D 时先按"quasi3d → three.dim"转换（见下）

## 转 3D 的要点（csuprem-complex-structure-modeling 技能）

1. 每个 xy 平面一份 `planeN.in`（本文件第 1 段骨架）；
2. `zmesh.zst`：`z_structure` 定义平面位置（`zplanes=1`），固定行 `output sol_outf=tmp.out` / `export_3dgeo file=xxx.3dgeo` 不改；
3. 主输入加 `mode three.dim`（先 `quasi3d` 验证）+ `3d_mesh nsegm=N infile=plane zstfile=zmesh.zst` + `init`；
4. 只对刻蚀命令逐平面加 `segm=`；淀积/注入只写一次；
5. 导出后 .sol 侧用 `suprem_import=yes` + 逐平面 `begin_zmater/end_zmater`（suprem_property/suprem_contact 编号与 load_macro/contact 一致）。

## 注意事项

- `avoidmask` 型刻蚀必须 `mask` 前置；
- CMP 在 CSuprem 中是**多边形刻蚀近似**（无物理 CMP 模型）；`-4.95` 等数值来自 BCD 示例坐标，请按你的器件高度调整切平位置；
- `$` 开头的行是注释；语句超过 80 字符用 `&&` 续行；
- 本输入脱胎于官方示例（BCD.in / testflow2.msk / LDMOS.in），未在本机实测（status: draft）。

## 相关链接

[[04-操作流程/标准工作流]] · [[01-基础概念/项目结构与文件类型]] · [[07-故障排查/常见错误索引]]
