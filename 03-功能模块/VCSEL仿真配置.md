---
title: VCSEL 仿真配置
type: reference
product: Crosslight
version: 2024
status: draft
source: "C:\crosslig\pics3d_examples\A_tutorial\MQW_active\inp13.sol；[[99-原始资料/专题/培训总结.pdf]]（VCSEL 节）；[[99-原始资料/通用手册/manual.pdf]] §4.2"
last_verified: 2026-08-17
---

# VCSEL 仿真配置（PICS3D）

## 参考示例

真实可运行示例：`C:\crosslig\pics3d_examples\A_tutorial\MQW_active\inp13`（含 `.layer`/`.gain`/`.sol`/`.plt` 全套与 README）。

## 结构要点（培训总结 VCSEL 节）

- 用 LayerBuilder 沿半径方向建立外延结构，绕 y 轴旋转成圆柱；
- 每层都要设置 vcsel 参数（mesh points 用于光学腔计算，不是物理网格）；
- 有源区（阱、垒）设 `active=yes`，其余层 `active=no`；
- DBR 可用 `start_loop` 循环语句生成（LayerBuilder 不显示循环结构）。

## sol 关键语句（来自 inp13.sol）

```text
begin
3d_solution_method 3d_flow=yes
z_structure uniform_length=0 zseg_num=1 zplanes=1
load_mesh mesh_inf=inp13.msh zseg_num=1
output sol_outf=inp13.out
begin_zmater zseg_num=1
include file=inp13.gain
include file=inp13.doping
end_zmater
init_wave backg_loss=0.5E+3 init_wavel=1.3 boundary_type=[2 2 1 1] && wavel_range=[1.28 1.32]
direct_eigen
newton_par damping_step=3. var_tol=1.e-8 res_tol=1.e-8 max_iter=100 print_flag=3
equilibrium
rtgain_phase density=1.25e24
scan var=voltage_1 value_to=-5. init_step=1e-3 max_step=0.1 && auto_finish=current_1 auto_until=1.e-4
scan var=current_1 value_to=20e-3 init_step=1e-4 max_step=1e-3 && auto_finish=rtgain auto_until=0.9 auto_within=0.05
scan var=current_1 value_to=20e-3 init_step=1e-5 max_step=5e-4 && print_step=50e-3 solve_rtg=yes
end
begin_zsol
longitudinal ref_wavel=1.3e-6 left_f_refl=0 right_f_refl=0
mode_srch omega_xrange=20 adjust_range=yes
end_zsol
```

## 关键点

- `auto_finish=rtgain` 是 PICS3D 专属：引入光子耦合前的扫描必须以它终止，完成纵模与光子密度初始化（manual §4.2）；
- RTG 终止值取略高于透明密度、且小于 1.0，避免提前进入激射阈值；
- 低阈值 VCSEL 可把电压段与 RTG 初始化合并，用 `auto2_finish` 加电流下限（manual §4.2）；
- 运行后才可查看 rtgain 图像，数据在 `.rtd`/`.stw` 文件中。

## 预期输出与验证

- 生成 `.std_#`、`.rtd`、`.stw`；rtgain 谱显示模式位置；
- L-I 曲线给出阈值电流（inp13 约 50 mA，培训总结示例）；
- CrosslightView 可显示模式谱与驻波。

## 相关链接

[[05-API与命令/核心参数]]（bias/auto_finish）· [[06-案例/最小可运行案例]] · [[07-故障排查/不收敛]]
