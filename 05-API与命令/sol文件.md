---
title: .sol 文件
type: concept
product: Crosslight
version: 2024
status: source
source: "C:\crosslig\lastip_examples\A_tutorial\1D_laser\gaas10.sol；[[99-原始资料/通用手册/manual.pdf]] 第3章；[[99-原始资料/教程与问答/Common_QAs.pdf]]"
last_verified: 2026-08-17
---

# .sol 文件（求解设置）

## 这是什么

主求解器的输入文件：加载网格与材料、设定偏置扫描、Newton 数值参数、光波导/模式求解与输出。由 GUI（SimuCenter 向导）或用户手写，求解器读取。

## 结构（来自真实示例 gaas10.sol）

```text
begin
use_macrofile macro1=my.mac
load_mesh mesh_inf=gaas10.msh
output sol_outf=gaas10.out
include file=gaas10.doping
include file=gaas10.mater
more_output ac_data=yes
direct_eigen
init_wave length=400 backg_loss=500. && boundary_type=(2 2 1 1) init_wavel=0.83 mirror_ref=0.32
newton_par damping_step=5. max_iter=100 print_flag=3
equilibrium
scan var=voltage_1 value_to=-2 && init_step=1e-3 max_step=0.1 && auto_finish=current_1 auto_until=1e-3
scan var=current_1 value_to=20. print_step=2. && init_step=1e-3 max_step=0.2
end
```

## 关键语句速查

| 语句 | 作用 | 详见 |
|---|---|---|
| `load_mesh mesh_inf=xxx.msh` | 载入网格 | [[04-操作流程/标准工作流]] |
| `include file=xxx.doping/.mater` | 引入掺杂/材料 | [[01-基础概念/mater_define]] |
| `newton_par` | Newton 阻尼/容差/迭代 | [[05-API与命令/核心参数]] |
| `equilibrium` | 平衡态求解（scanline 1） | [[05-API与命令/核心参数]] |
| `scan var=voltage_1/current_1` | 偏置扫描 | [[05-API与命令/核心参数]] |
| `auto_finish=current_1/rtgain` | 扫描终止条件 | [[05-API与命令/核心参数]] |
| `solve_rtg=yes` | PICS3D 打开 RTG 求解 | [[03-功能模块/VCSEL仿真配置]] |

## 数据集编号

`equilibrium` 默认第 1 个 scanline（数据集 1,1）；每个 `scan` 按 `print_step` 生成若干数据集；各数据集对应的偏置见 `.sol.msg` 文件。

## 相关链接

[[05-API与命令/核心参数]] · [[05-API与命令/std文件|.std 文件]] · [[04-操作流程/标准工作流]]
