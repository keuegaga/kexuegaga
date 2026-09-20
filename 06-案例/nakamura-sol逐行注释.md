---
title: nakamura s2.sol 逐行注释（教学）
type: example
product: PICS3D
version: 2024
status: source
source: 'C:\Users\ciomp\Documents\2024Ver_pics3d_examples\pics3d_examples\blue_LD\nakamura\s2 (3).sol（官方 Nakamura 蓝光 LD 示例原版；另见 s2_original_2024.sol）'
last_verified: 2026-09-15
tags:
  - crosslight
  - example
  - sol
  - tutorial
  - pics3d
  - gan
---

# nakamura s2.sol 逐行注释（教学）

> 目的：给 PICS3D 零基础读者逐行读懂一个真实的 GaN 蓝光激光器求解输入文件。读完你应该能：改波长窗口、改电流目标、改步长与输出密度、判断哪些改动必须重跑网格、哪些改动可以续算。结构文件（`.layer`）的对应篇见 [[06-案例/nakamura-light-layer逐行注释]]。

## 先读懂五件事

1. **`.sol` 是一份命令清单，从上到下逐条执行**——不是"配置文件"。**顺序本身有含义**：
   - `output` 必须在 `restart` 之前（否则报 `Input error:restart/init_sol output not yet used`）；
   - `equilibrium` 必须是最早的偏置语句（手册 §23.656：扫描的初值永远来自平衡态）；
   - **以 `auto_finish=rtgain` 结束的那段扫描，必须紧挨在 `solve_rtg=yes` 之前**；顺序错了会出现"波长跳到 999 nm"这类怪事（详见 [[04-操作流程/PICS3D续算与光耦合初始化]]）。
2. **三种语法**：`$` 开头的整行是注释；`&&` 是续行符（一条语句写不下时用）；其余是 `参数=值`，用空格分隔。
3. **结构不在这个文件里**：层序/材料/掺杂/网格在 `.layer`（或 `.geo`），由 `layer.exe`（或 `geometry.exe`）生成 `.msh` / `.mater` / `.doping`。`.sol` 只负责"怎么算"。
4. **激光器仿真的骨架是"三段偏置"**（这是本文件最重要的一件事）：

```text
1) equilibrium                  解平衡态（无偏置、无光照）——所有扫描的起点
2) scan ... auto_finish=rtgain  电流扫描；往返增益 RTG 到达设定值时自动停
                                此时光子耦合还没打开，用的正是"光子密度约等于 0"的近似
3) scan ... solve_rtg=yes       打开光子耦合，继续扫到目标电流（跨过阈值）
```

   为什么必须这样分段？因为"有多少光子"要靠 RTG 方程解出来，而 RTG 依赖增益分布、增益分布又受光子密度影响——先在下阈值状态把模式位置与光子密度初值算清楚，才能安全地打开耦合（手册 §4.2）。
5. **单位**：长度/波长 µm、电流 A、温度 K、掺杂 m⁻³（`5e24 m^-3 = 5e18 cm^-3`）、损耗 1/m（`1300 /m = 13 /cm`）。

## 语句速查表（本文件用到的全部语句）

| 语句                          | 一句话作用                                                                                  |
| --------------------------- | -------------------------------------------------------------------------------------- |
| `begin` … `end`             | 主求解段的起止（纵向设置另用 `begin_zsol`）                                                           |
| `3d_solution_method`        | 3D 求解方式（只对"多于一个 mesh plane"的器件有效，手册 §23.6）                                             |
| `z_structure`               | 纵向（腔长方向）如何切平面：腔长、z 段数、z 平面数（手册 §23.828）                                                |
| `load_mesh`                 | 读入网格文件 `.msh`                                                                          |
| `include file=`             | 把另一个文件的内容原样展开进来（这里是 `.gain` 与 `.doping`）                                               |
| `output sol_outf=`          | 定义输出文件基名；数据集后缀 `_0001` 起自动编号（手册 §23.529）                                               |
| `restart data_set=`         | 从已保存的数据集续算（手册 ch23.649）——只在续算版里出现                                                      |
| `polarization_charge_model` | 用压电/自发极化电荷模型算异质结界面固定电荷（手册 §23.594）                                                     |
| `self_consistent`           | 量子阱 Schrödinger + Poisson 自洽迭代（强极化器件必选）                                                |
| `q_transport`               | 量子阱的非局域/量子输运修正（深阱、极化器件默认模型会高估开启电压）                                                     |
| `temperature`               | 仿真温度                                                                                   |
| `set_active_reg`            | 覆盖有源区参数（手册 §23.670：override active region parameters previously defined in active_reg） |
| `wave_boundary`             | 光学波方程的求解窗口；会覆盖 `init_wave` 的对应项（手册 §23.822）                                            |
| `init_wave`                 | 初始光场与波长扫描设置（初始波长、波长范围、背景损耗…，手册 §23.386）                                                |
| `direct_eigen`              | 用重启 Arnoldi 算法求横向光学模式（手册 §23.228）                                                      |
| `multimode`                 | 多横向模式设置（模式个数、光学边界类型，手册 §23.505）                                                        |
| `newton_par`                | 非线性 Newton 求解器参数（手册 §23.516）                                                           |
| `equilibrium`               | 解一次平衡态                                                                                 |
| `rtgain_phase`              | 生成往返增益谱预览，输出到 `.rtd`（手册 §23.653）                                                       |
| `scan`                      | 扫描（改变控制变量并求解，手册 §23.656）                                                               |
| `begin_zsol` … `end_zsol`   | 纵向（腔方向）求解器设置段                                                                          |
| `longitudinal`              | 端面反射率、参考波长、是否忽略纵模相位（手册 §23.445）                                                        |
| `section`                   | 定义一段腔（光栅 κ、长度、相位、纵向网格点数，手册 §23.660）                                                    |
| `lateral_mode3d`            | 每个横向模式各自带一套纵向模式（手册 §23.406）                                                            |
| `mode_srch`                 | 纵模搜索参数（搜索窗口等）                                                                          |

## 逐行注释（完整代码）

> 说明：注释行（`$ ↑ …`）插在对应语句**下方**。`$` 是 Crosslight 原生的注释符，所以这份带注释的版本本身就能当输入文件用。原文件里的对齐空格已规整。

```text
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$ 文件头：只说明器件出处（Nakamura 1997 MRS 蓝光激光器），不影响计算
$Device structure from
$MRS Int. Jour. of Nitride Semic. Res.,
$Vol. 2, Articl 5 , 1997;   http://nsr.mij.mrs.org/2/5/
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

begin
$ ↑ 主求解段开始。后面所有指令按顺序执行；对应的结束是最后的 end

3d_solution_method 3d_flow=yes z_connect=no
$ ↑ 3D 求解方式：3d_flow=yes 打开三维电流流动；z_connect=no 表示各 z 平面之间不额外接电阻
$   只对"多于一个 mesh plane"的器件有效，正是本例（zplanes=10）
z_structure uniform_length=550 zseg_num=1 zplanes=10
$ ↑ 纵向（腔长方向）切分：腔长 550 µm，均匀分成 10 个 z-plane；zseg_num=1 表示只有 1 个 z 段
$   z 平面越多，纵向空间烧孔 LSHB 与纵模分辨越好，但每个偏置步都更慢

load_mesh mesh_inf=s2.msh
$ ↑ 读入网格文件 s2.msh（由 layer.exe 从 s2.layer 生成）。改结构就要重新生成它，而且不能再续算

include file=s2.gain
$ ↑ 把 s2.gain 的内容就地展开：增益预览/后处理设置（内部是 begin_gain … end_gain）
include file=s2.doping
$ ↑ 把 s2.doping 展开：各层掺杂与电极接触定义（通常由 layer.exe 自动生成，不要手改）
output sol_outf=s2.out
$ ↑ 输出基名：最终得到 s2.out_0001、s2.std_0001、s2.zp_0001 …
$   数据集编号从 _0001（平衡态）起，每"要求打印一次数据"（扫描结束或到达 print_step）就加一

polarization_charge_model screening=0.5
$ ↑ 启用压电/自发极化电荷模型；screening=0.5 是屏蔽因子（正是手册默认值）
$   配合材料宏里的 polarization_charge / spont_charge 使用，GaN 系必须开
self_consistent
$ ↑ 打开量子阱自洽求解（Schrödinger 与 Poisson 互相迭代）——强极化 GaN 器件的必选项
q_transport
$ ↑ 打开量子阱非局域输运修正：深阱/极化结构下，默认热发射模型会高估开启电压

$
$ ↑ 单独一个 $ 就是空注释行，用来分段，纯粹为了人读
temperature temp=293.
$ ↑ 仿真温度 293 K（等温仿真；要算自热还得另加 heat_flow 一类语句）
set_active_reg  tau_scat= 1.e-13 &&
 valence_mixing=no  mode=te   gain_coulomb=no     &&
 bandgap_renorm=no diel_av=9.5
$ ↑ 覆盖有源区参数（set_active_reg 用来覆盖 active_reg 里已设的项）
$   tau_scat=1.e-13      带内散射时间 [s]，决定增益谱展宽（越小越展宽、峰值越低）
$   valence_mixing=no    是否用 k·p 价带混合算子带。no=简化模型（快）；应变阱/要准的增益谱应改 yes（慢）
$   mode=te              只算 TE 偏振（边发射激光器通常看 TE）
$   gain_coulomb=no      不额外加库仑增益增强项
$   bandgap_renorm=no    不做带隙重整化
$   diel_av=9.5          有源区平均介电常数（影响库仑项与光学计算）
$   && 是续行符：这一条语句其实是上面三行连起来的一整行

wave_boundary point_ll=[ 0.0  3.4] &&
  point_ur=[4.5  4.4]
$ ↑ 光学波方程的求解窗口：左下角 (0.0, 3.4) µm、右上角 (4.5, 4.4) µm
$   手册明确：这条语句会覆盖 init_wave 里的 point_ll/point_ur，
$   而且通常由 layer.exe 自动生成（一般写在 .doping 里）。窗口要刚好罩住波导与有源区
init_wave backg_loss=1300.  &&
  boundary_type=[2 1 1 1] init_wavel= .42 &&
  wavel_range=[0.36 0.44] prn.gain_num=100
$ ↑ 初始光场与波长设置：
$   backg_loss=1300.         活动区之外各层的背景损耗，单位 1/m（1300 /m = 13 /cm）
$                            它直接决定内部损耗、进而决定阈值高低——示例头注释也点名它可调
$   boundary_type=[2 1 1 1]  光学边界类型（四个边界依次设置）
$   init_wavel=.42           初始波长 0.42 µm（=420 nm，蓝光）
$   wavel_range=[0.36 0.44]  波长/增益表的范围（µm）。RTG 搜索也在这个窗口里做，
$                            写错或漏写会让求解器跑到窗口外找模式（默认窗口是 0.5~1.8 µm！）
$   prn.gain_num=100         打印增益谱的点数（默认 50）

direct_eigen
$ ↑ 横向光学模式改用"重启 Arnoldi"算法求解
$   脊形/有横向折射率突变的 3D 结构推荐用它，比默认算法稳
multimode mode_num=10 boundary_type1=(2 1 1 1)  &&
      boundary_type2=(1 1 1 1)
$ ↑ 开启多横向模式：一共求 10 个横向模式；两组 boundary_type 是横向模式求解的边界条件
$   mode_num 决定每步要做多少次特征值求解，是速度的主要控制杆之一（降到 3~5 会快很多）

newton_par damping_step=5000. max_iter=250  &&
  var_tol=1.e-4 res_tol=1.e-4 print_flag=3 stop_iter=100
$ ↑ 第一组 Newton 参数（给平衡态这种"从零开始"的难题用，宽松一些）
$   damping_step=5000.   每次迭代解更新的上限（越大越激进、越小越稳）
$   max_iter=250         单个偏置步允许的最大非线性迭代次数；超过就缩小步长重来
$   var_tol / res_tol    收敛判据：变量变化 / 方程残差 低于此值即认为收敛
$   print_flag=3         日志详细程度（3 最详细，排错时有用）
$   stop_iter=100        迭代超过这个数就判断"没希望"，提前放弃并缩步长
equilibrium
$ ↑ 先解一次平衡态（无偏置、无光照）。所有扫描的初值都来自这里
rtgain_phase  density=2.e25
$ ↑ 生成"往返增益谱"预览，结果写在 .rtd 文件里
$   density=2.e25 是计算用的电子浓度 [m^-3]（默认 3e24）。用它可先判断结构能否给出足够增益

newton_par damping_step=1. var_tol=1.e-4 res_tol=1.e-4 &&
  max_iter=50 stop_iter=30 step_decrease=0.1 step_increase=1.5
$ ↑ 第二组 Newton 参数（给下面的扫描用：初值已经不错，可以更紧凑）
$   damping_step=1.        每步更新限制收紧，避免扫过头
$   max_iter=50 stop_iter=30   迭代上限降低（扫描每步更便宜）
$   step_decrease=0.1      偏置步失败时把步长乘 0.1 重试
$   step_increase=1.5      偏置步成功时把步长乘 1.5（所以扫描会越走越大，直到 max_step）

scan var=current_1 value_to=1e-3 &&
  init_step=1e-9 min_step=1.e-16 max_step=5.0 var2=time value2_to=1
$ ↑ 第 1 段扫描：把电极 1 的电流从 0 扫到 1e-3 A（=1 mA）
$   var=current_1        被扫描的控制变量：1 号电极的电流（写 voltage_1 则是电压）
$   value_to=1e-3        扫到这个值为止（单位 A）
$   init_step=1e-9       起始步长极小：平衡态刚解完，先用极小步把"开启"区走稳
$   min_step / max_step  步长下限与上限
$   var2=time value2_to=1  第二个控制变量是 time，扫到 1（慢瞬态技巧：多给一个"时间"维度更稳）

scan var=current_1 value_to=300e-3 print_step=50e-3 &&
  init_step=1e-5 min_step=1.e-6 max_step=5e-3 var2=time value2_to=10 &&
  auto_finish=rtgain auto_until=0.6 auto_within=0.1
$ ↑ 第 2 段扫描：光子耦合还没打开，用电流把器件带到阈值附近
$   value_to=300e-3      名义目标 300 mA（实际会在下面的 auto_finish 满足时提前结束）
$   print_step=50e-3     每前进 50 mA 落一个数据集（一个数据集约 100 MB 磁盘，别设太小）
$   auto_finish=rtgain   监视往返增益 RTG，满足条件就自动结束这段扫描——手册 §4.2 的硬性要求
$   auto_until=0.6       终止值（手册建议取"刚高于透明、且 <1.0"，避免直接越过阈值）
$   auto_within=0.1      容差带：进入 0.6±0.1 就认账
$   ⚠️ 结束这一段的动作本身，就是在算"纵模位置 + 各模光子密度初值"，下一段要用

scan var=current_1 value_to=300e-3 print_step=50e-3 &&
  init_step=1e-5 min_step=1.e-6 max_step=5e-3 var2=time value2_to=10 &&
  solve_rtg=yes
$ ↑ 第 3 段扫描：打开光子耦合（solve_rtg=yes），继续升电流跨过阈值
$   之后就能从数据集里取 L-I、光场分布、增益谱等结果
end
$ ↑ 主求解段结束

begin_zsol
$ ↑ 纵向（腔方向）求解器设置段开始；它和一维纵向模型有关，与上面的 3D 网格各管一摊
longitudinal left_f_refl=0.5 right_f_refl=0.5 ref_wavel=0.42e-6 &&
  ignore_rtg_phase=yes
$ ↑ 腔端面与参考波长：
$   left_f_refl / right_f_refl   左右端面反射率（按功率计）。真实 GaN 解理面约 0.18，
$                                这里用 0.5 相当于低损耗腔面——想让阈值更高就调小它
$   ref_wavel=0.42e-6            参考波长，用来固定纵模搜索范围；在光耦合打开那一刻固定
$   ignore_rtg_phase=yes         2015 年加入的实验性模型：不解相位匹配，直接搜"往返增益最大的那个波长"
$                                好处是 FP 腔好收敛；代价是搜索依赖初值，初值错了就会跑飞（见续算笔记）
section kappa_real=0. zseg_num=1 sec_num=1  mesh_points=20
$ ↑ 定义第 1 段腔：
$   kappa_real=0.   光栅耦合系数 = 0 → 这是普通 FP 腔（DFB/DBR 才给非零值）
$   zseg_num=1      该段覆盖 1 个 z 段（对应上面 z_structure 的 zseg_num=1）
$   sec_num=1       段编号 1（多段腔依次编号）
$   mesh_points=20  纵向网格点数（纵向分辨率）
lateral_mode3d mode_num=10
$ ↑ 让每个横向模式各自带一套纵向模式，个数与上面的 multimode 对齐
mode_srch omega_xrange=12.
$ ↑ 纵模搜索窗口（示例里用 12~20 这个量级）；调大可覆盖更多纵模，代价是更慢
end_zsol
$ ↑ 纵向设置段结束
```

## 分块精讲

### ① 文件头与注释（`$`）

`$` 之后整行都被忽略。示例头部那段英文其实是在告诉你"哪几个参数可以调"：`valence_mixing`、`tau_scat`、`mirror reflectivity`、`internal loss`、`q_transport`。**这也解释了为什么默认参数跑不出论文里那条 L-I 曲线**——必须自己调。

### ② 结构 / 网格 / 材料（`load_mesh`、`include`）

`.sol` 不定义结构，只引用结构产物：`.msh`（网格）、`.mater`（材料）、`.doping`（掺杂与电极）。它们由 `layer.exe`（或 `geometry.exe`）从 `.layer` / `.geo` 生成。→ 改结构 = 重新生成 + 从头算，**不能续算**。

### ③ 输出与续算（`output`、`restart`）

```text
output sol_outf=s2.out     $ 基名 -> s2.out_0001 / s2.std_0001 / ...
restart data_set=3         $ 从第 3 个数据集继续（必须放在 output 之后）
```

`restart` 的两个坑（本库实测）：它只恢复数据、**不重建光学状态**；而且会**跳过前面 N 段扫描**（N = 该数据集"已完成"的扫描数）。细节见 [[04-操作流程/PICS3D续算与光耦合初始化]]。

### ④ 物理模型开关（极化 / 自洽 / 输运 / 温度 / 有源区）

| 语句 | 打开后 | 什么时候必须开 | 代价 |
|---|---|---|---|
| `polarization_charge_model` | 界面极化电荷 | GaN/AlGaN/InGaN 异质结与量子阱 | 小 |
| `self_consistent` | Schrödinger + Poisson 自洽 | 强极化、强内建场 | 每个偏置步多算一遍子带 |
| `q_transport` | 量子阱非局域输运 | 深阱（氮化物）、开启电压虚高 | 中 |
| `set_active_reg valence_mixing=yes` | k·p 价带混合 | 应变阱、需要准的增益谱 | 大（明显变慢） |

### ⑤ 光学设置（`wave_boundary` / `init_wave` / `direct_eigen` / `multimode`）

一句话：**求解窗口与波长窗口必须把"光"和"模式"罩住**。

- `wave_boundary` 给窗口（会被 `init_wave` 的 `point_ll/point_ur` 覆盖，实际由 layer.exe 生成）；
- `init_wave` 给初始波长、**波长范围**与背景损耗；
- `direct_eigen` + `multimode` 决定求几个横向模式——**`mode_num` 是速度的主要控制杆**。

### ⑥ Newton 求解器（`newton_par`）

一个偏置步就是反复"装配方程 → 解线性方程组 → 更新变量"，直到收敛：

| 参数 | 含义 | 调它的后果 |
|---|---|---|
| `max_iter` | 单步最大迭代数 | 调大=更可能收敛但更慢；超过就缩步长重来 |
| `opt_iter` | 期望迭代数（默认 15） | 求解器按它自动增/减偏置步长 |
| `stop_iter` | 提前放弃阈值 | 调小=更快放弃难步、更快缩步长 |
| `damping_step` | 解更新上限 | 调小=稳但慢；调大=快但可能振荡 |
| `var_tol` / `res_tol` | 变量/残差收敛判据（默认 1e-5） | 放宽到 1e-4~1e-3 有助于难例 |
| `step_decrease` / `step_increase` | 失败缩 / 成功放大步长的倍数 | 都不写时由程序按 `opt_iter` 自行判断 |
| `print_flag` | 日志详细度 | 排错时用 3 |
| `mf_solver` | 线性求解器档位（默认 3=并行多线程） | 4=GPU；0=串行 |

### ⑦ 偏置流程（`equilibrium` / `rtgain_phase` / `scan`）

`scan` 的参数分五类，好记：

```text
扫什么       var=current_1        [var2=time]
扫到哪       value_to=300e-3      [value2_to=10]
怎么扫       init_step / min_step / max_step / step_increase / step_decrease
何时停/打印  auto_finish / auto_until / auto_within / auto_condition；print_step
开什么       solve_rtg=yes（打开光子耦合）
```

**判断一段扫描设计得好不好，看三点**：① 步长上限够不够小（大了容易不收敛）；② `print_step` 合不合理（数据集体积与数量）；③ 停止条件对不对（`auto_finish` 的变量与目标值）。

### ⑧ 纵向设置段（`begin_zsol` … `end_zsol`）

这一段与主求解段**物理上分家**：主段算 3D 电学 + 横向光学，`begin_zsol` 里算纵向传播与纵模。四类内容：端面反射率与参考波长（`longitudinal`）、腔的分段（`section`）、横向模式继承（`lateral_mode3d`）、纵模搜索（`mode_srch`）。

### ⑨ 产出文件速查

| 文件 | 内容 | 什么时候看它 |
|---|---|---|
| `.sol.msg` | **数据集清单**：编号 ↔ 电压/电流，还含各模式增益表 | 找续算起点、查某个电流对应哪个数据集 |
| `.mon` | 每个收敛偏置点的偏置数据 | 判断"跑到哪了"、画 I-V / L-I |
| `.log` | 文本日志（需自己重定向或由 GUI 抓取） | 排错 |
| `.rtd` | `rtgain_phase` 生成的往返增益谱 | 判断结构能否给出足够增益 |
| `.out_####` / `.std_####` / `.zp_####` | 各数据集的结构 / 结果 / 剖面数据（每个约 100 MB） | 后处理：能带、光场、载流子分布 |
| `.plt` | 后处理绘图脚本（CrosslightView 也能画） | 出图 |

## 常见修改场景速查

| 我想… | 改哪一行 | 注意 |
|---|---|---|
| 改目标电流 | 后两段 `scan` 的 `value_to` | 单位 A；`300e-3` = 300 mA |
| 让扫描更稳 | `max_step` 调小（如 5e-3 -> 1e-3）、`step_decrease` 调大 | 越稳越慢 |
| 让扫描更快 | `max_step` 调大、`mode_num` 调小、`zplanes` 调小 | `zplanes` 改了要重跑网格 |
| 改变输出密度 | `print_step` | 每个数据集约 100 MB（`.out`+`.std`+`.zp`） |
| 改波长窗口 | `init_wave` 的 `wavel_range` / `init_wavel` | **必须罩住目标激射波长**，否则 RTG 搜索会跑偏 |
| 改腔面反射率 | `begin_zsol` 的 `left_f_refl` / `right_f_refl` | 按功率计；调小 -> 镜面损耗大 -> 阈值高 |
| 改内部损耗 | `init_wave backg_loss=` | 单位 1/m；阈值高低最直接的旋钮之一 |
| 提高增益模型精度 | `set_active_reg valence_mixing=yes`、`tau_scat` | 明显变慢 |
| 只算 I-V 不关心激光 | 删掉带 `solve_rtg=yes` 的那段扫描 | 不需要光子耦合时就不必写 |
| 换器件 | `.layer` / `.geo` | 必须重新生成 `.msh`，**不能续算** |

## 修改纪律：什么能改、什么要重跑

| 改动 | 要重跑 `layer.exe`？ | 能否 `restart` 续算 |
|---|---|---|
| `.sol` 里扫描目标 / 步长 / Newton 参数 | 否 | 能 |
| `.sol` 里输出密度 `print_step` | 否 | 能 |
| `.sol` 里光学设置（波长窗口、`mode_num`、反射率） | 否 | 能跑，但新旧结果不可混用，建议从头算 |
| `.sol` 里 `output sol_outf` 的基名 | 否 | **不能**（旧数据集"找不到"，等于从头） |
| `.layer` / `.geo`（层厚、材料、掺杂、网格） | **是**（`layer.exe` / `geometry.exe`） | **不能** |

**编码提醒**：`.sol` 里的中文注释请用 **ASCII 或 GBK** 保存；UTF-8 无 BOM 会让 SimuPics3d 显示成乱码（规范见 [[00-入口/知识库规范]]）。

## 当前在跑的"续算版 s2.sol"多了什么（4 处）

算例目录里现在这份 `s2.sol` 是在上面原版基础上改了 4 处（原因与实测过程见 [[04-操作流程/PICS3D续算与光耦合初始化]]）：

| # | 改动 | 为什么 |
|---|---|---|
| 1 | `output` 之后加 `restart data_set=3` | 从 21.49 mA 的数据集继续，省掉前面约 30 小时 |
| 2 | 新加一组稳定化 `newton_par`（`recover_prev_mqw=yes`、`step_decrease=0.5`、`step_increase=1.3`、`max_iter=100`） | 原设置的 `step_decrease=0.1` 会在难步上把步长一路压到 0.25 µA |
| 3 | 把原来那段光耦合扫描**拆成两段**（先 60 mA、再 300 mA），并把 `max_step` 降到 1e-3、`print_step` 降到 10e-3 | 步长更小、检查点更密，出问题最多丢 10 mA |
| 4 | 在光耦合扫描之前**保留一段以 `auto_finish=rtgain` 结束的扫描** | 手册 §4.2 的硬性要求：紧邻光耦合之前的那段必须以 RTG 条件结束，否则波长会跑到 999 nm |

> 学习建议：先把上面这份"原版"读透、能自己改；续算相关的规则等你要做长任务时再回头查那篇笔记。

## 学习路径与练习

**读法（建议顺序）**：

1. 先看「先读懂五件事」，建立"三段偏置 + 顺序有含义"的直觉；
2. 对照「逐行注释」通读一遍——只求看懂每行在干什么，不用背；
3. 要改东西时查「常见修改场景速查」；
4. 动手前先扫一眼「修改纪律」，确认不会白跑 30 小时。

**四道练习**（每题都按"改一行 → 先预测 → 再跑起来验证"做。建议在 `nakamura_light` 上练，跑完一轮约 3 小时；正式算例一轮要 30 小时以上）：

| # | 改什么 | 先预测会发生什么 | 观察点 |
|---|---|---|---|
| 1 | `multimode mode_num=10` 改成 `3` | 每步只需 3 次横向模式特征值求解而非 10 次 → 明显变快；横向模式更少，结果与 10 模式版有差异 | 同一电流步所需的墙钟时间；日志里 `photon#` 表的行数 |
| 2 | `init_wave` 的 `wavel_range=[0.36 0.44]` 改成默认值 `[0.5 1.8]` | RTG 波长搜索窗口变大，可能落到 ~1 µm 的伪解上 | 日志出现 `peak RTG set lambda= 0.99x` 与 `Warning: big change in lambda`（这正是本库 2026-09-14 踩过的坑） |
| 3 | `temperature temp=293.` 改成 `323` | 带隙变窄 → 增益峰与激射波长红移，阈值略升 | `.sol.msg` 里各数据集的 `Modal_gain` 与模式波长 |
| 4 | `init_wave backg_loss=1300.` 改成 `500.` | 内部损耗从约 1350 /m 降到约 700 /m → 同样注入电流下更容易接近阈值 | `.sol.msg` 的 `Int._loss` 列与 `Modal gain` 列对比 |

第 2 题特别值得做：它用一个很短的试验让你亲眼看到"窗口写错会怎样"。做完四题，你对 `.sol` 的控制力就不一样了——第 4 题也正是当前要解决的"到不了阈值"问题的方向（详见 [[04-操作流程/PICS3D续算与光耦合初始化]] 的轨 B 部分）。

## 相关笔记

- [[06-案例/nakamura-light-layer逐行注释]]（结构文件 `.layer` 的对应篇）
- [[04-操作流程/PICS3D续算与光耦合初始化]]
- [[04-操作流程/PICS3D中断续算]]
- [[05-API与命令/核心参数]]
- [[01-基础概念/项目结构与文件类型]]
- [[06-案例/最小可运行案例]]

## 来源

- 文件：`C:\Users\ciomp\Documents\2024Ver_pics3d_examples\pics3d_examples\blue_LD\nakamura\s2 (3).sol`（2023 原版）与同目录 `s2_original_2024.sol`
- 手册：[[99-原始资料/通用手册/manual.pdf]]——§4.2（P84-85，三段偏置与 `auto_finish=rtgain`）、§23.6 `3d_solution_method`、§23.228 `direct_eigen`、§23.386 `init_wave`、§23.406 `lateral_mode3d`、§23.445 `longitudinal`、§23.505 `multimode`、§23.516 `newton_par`、§23.529 `output`、§23.594 `polarization_charge_model`、§23.604 `q_transport`、§23.653 `rtgain_phase`、§23.656 `scan`、§23.660 `section`、§23.666 `self_consistent`、§23.670 `set_active_reg`、§23.822 `wave_boundary`、§23.828 `z_structure`、ch23.649 `restart`
- 实测：2026-09-09 ~ 09-15，nakamura 算例（PICS3D 2024.02.01，Windows 11）
