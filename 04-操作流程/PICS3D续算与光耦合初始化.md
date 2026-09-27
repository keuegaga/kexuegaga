---
title: PICS3D 续算与光耦合初始化
type: workflow
product: PICS3D
version: 2024
status: verified
source: "[[99-原始资料/通用手册/manual.pdf]] §4.2（P84-85）、§23.445 longitudinal（P859-862）、§23.529 output（P983）、ch23.649 restart（P1117-1119）"
last_verified: 2026-09-15
tags:
  - crosslight
  - workflow
  - pics3d
  - restart
  - optical-coupling
---

# PICS3D 续算与光耦合初始化

## 目标

续算后进入**光耦合扫描**（`scan … solve_rtg=yes`）时，避免 RTG 波长搜索跑飞——日志出现 `peak RTG set lambda= 0.99x` 加 `Warning: big change in lambda`，把工作波长从应有的 0.4246 µm 拖到 999 nm。

做完本流程后应得到：续算起点正确、波长全程停在 0.42x µm、光耦合段正常推进。

## 适用版本与环境

| 项 | 值 |
|---|---|
| Crosslight 版本 | 2024.02.01（PICS3D） |
| 操作系统 | Windows 11 |
| 相关产品 | PICS3D，3D 边发射激光器（nakamura 算例：zplanes=10、mode_num=10、88800 网格点） |
| 附加软件 | 无 |

## 现象（真实日志）

进入光耦合扫描的第一段就跳，而且是在**第一个偏置步之前**：

```text
  photon#       lambda            long.mode   lat.mode
  0.000000E+00  0.424646E+00           1           1 phn#      ← 横向模式表本身正确
  ...
 Ignoring LD phase, peak RTG set lambda=  0.999000000000000    ← 跳到 999 nm
 Modal gain (1/m):  -1234.59734248428       wavel=  0.999000000000000
 Warning: big change in lambda                                 ← 程序自己报警
```

此后波长**不会停住，而是按固定比例往下爬**——这是最好认的指纹：

```text
0.999000000000000   0.998001000000000   0.997002999000000   0.996005996001000
0.995009990004999   0.994014980014994   0.993020965034979   0.992027944069944 ...
```

每一步恰好是上一步的 **×0.999**（即 0.999ⁿ）。实测 10 小时只从 0.999 爬到 0.980，要爬到 0.4246 需要约 855 步——**这一段的结果不可用，也不必等它自己爬回去**。

指纹含义：RTG 波长搜索的起点落到了默认的 ~1.0 µm，随后以 0.1% 的相对步长朝"往返增益增大"的方向爬行。起点正确时（健康轮）第一条就是 `0.424646388493990`，之后一直停在那里。

## 根因：手册 §4.2 的硬性要求被跳过了

手册 §4.2 *Special bias considerations for PICS3D*（P84-85）原文：

> "It is therefore required that **the scan preceding the introduction of the photon coupling use the `auto_finish=rtgain` condition to terminate**. This will calculate the positions of the longitudinal modes as well as provide an initial guess of the photon density in each mode."

> 4. Apply current bias with `auto_finish=rtgain`. … 5. Double-check the modes found in the mode search … 6. Apply current bias with `solve_rtg=yes` until desired value is reached.

也就是说，光耦合**不是随时打开都行**：紧挨着它的前一段扫描必须以 `auto_finish=rtgain` 结束，好把"纵模位置 + 各模光子密度初值"算出来。

续算时如果直接从数据集跳进 `solve_rtg=yes` 的扫描（或者虽然插了一段普通扫描、但那段没有 `auto_finish=rtgain`），这个初始化就**从未发生**。光耦合于是带着空初值打开，`ignore_rtg_phase=yes` 的搜索随即落到 ~1 µm 的伪解上。

### 为什么后果这么明显：`ignore_rtg_phase=yes` 是"搜"不是"解"

手册 §23.445 原文：

> `ignore_rtg_phase` is an **experimental model** added in v. 2015. … Instead of solving for multiple longitudinal modes, PICS3D will **search for a single wavelength which maximises the round-trip gain value**…

> `ref_wavel` is the reference wavelength which is **used to fix the search range for the longitudinal modes**. This is **fixed once the coupling of the round-trip gain equations is turned on**…

波长是搜索出来的，所以初值正确与否直接决定结果；手册同时提醒 FP 腔若关掉该选项会面对 "too many longitudinal modes … solver stability often become unmanageable"。

### 实测对照（同一判据点：进入光耦合扫描后的第一次 RTG 搜索）

| 版本 | 做法 | `peak RTG` 波长 / Modal gain | `Warning: big change` |
|---|---|---|---|
| 正常轮（2026-09-10/11） | 程序自己执行 `auto_finish=rtgain` 段，再到耦合段 | 0.424646388493990 / **+256.8 /m** | 无 |
| v1 | `restart data_set=4`，直接进耦合段 | 0.998001000000000 | 有 |
| v1′ | `restart data_set=3`，直接进耦合段 | 0.999000000000000 / −1227.8 /m | 有 |
| v1″ | v1′ + `ref_wavel=0.4246e-6` | 与 v1′ **输出逐字节相同** | 有 |
| v2 | `data_set=3` + **不带** `auto_finish=rtgain` 的暖机扫描 | 暖机段正常（λ=0.420359、12 个收敛点、无 Warning），**暖机段一结束、光耦合一开立刻又跳到 0.999** | 有 |
| v3 | `data_set=4` + 文件里 scan3 就是 `auto_finish=rtgain` 初始化扫描 | 初始化扫描**被 restart 快进跳过**（scan1/2/3 的标记一闪而过），光耦合段第一次搜索即 0.999，随后 0.999ⁿ 递减 | 有 |
| **v4** | `data_set=3` + 初始化扫描放在第 3 段（**快进点之后**）+ `auto_until=0.62 auto_within=0.02` | 初始化段 21.49 → 21.73 mA 正常推进并写出 `Data set #4`；进入 `solve_rtg=yes` 后首次搜索 = **0.424646392144940**，photon# 表 10 个模式都在 0.424646 µm 且光子密度 ~1.0~1.2×10³ | **无** |

v2 是最关键的证据：**"在耦合前随便走一个正常偏置步"不够**——缺的是那次以 RTG 条件结束的初始化。

### 附带观察：恢复态的光学量不完全等价

同一偏置点（21.49 mA）对比"程序自己走到"与"从数据集恢复"：

| 项目 | 程序自己走到 | 从 `data_set=3` 恢复 |
|---|---|---|
| `Select modes with max index` | 2.55804365714688 | 2.63201129791080（≈低偏置量级） |
| 起始 `Direct eigen solver at lambda=` | 0.420358593663849 | 0.420000000000000（回落 `init_wavel`） |
| 横向模式 Im | −6.99e−6 | +4.12e−5 |

加了 v2 的暖机扫描后，`max index` 回到 2.55805（与正常轮一致）——说明暖机扫描**确实修正了折射率状态**，但它替代不了 §4.2 要求的 RTG 初始化。两条要同时满足。

### 已证伪的猜想（保留，避免重复踩坑）

| 猜想 | 试验 | 结论 |
|---|---|---|
| `.sol` 改名导致数据集找不到 | 改成 `s2_restartA.sol` | 真问题（8 秒空转、restart 未加载），但**不是本病的根因**；与 `sol_outf` 同基名（`s2`）即恢复 |
| `ref_wavel` 没锚对 | `0.42e-6` → `0.4246e-6` | 输出逐字节相同 → 与该跳变**无关** |
| 只要在耦合前插一段无耦合扫描即可 | v2 | **不够**，必须带 `auto_finish=rtgain` |
| 只要文件里存在 `auto_finish=rtgain` 初始化扫描即可 | v3 | **不够**——它在快进范围里，等于不存在；必须落在快进点**之后**（见下节） |

### restart 的快进规则：哪几段扫描会被跳过

实测归纳（4 次观测一致）：

> **restart 会跳过前面 N 段扫描，N = 恢复点所在数据集"已经完成"的扫描数；从第 N+1 段扫描开始才真正执行。**

| 恢复点 | 该数据集的来历 | 跳过 | 实际执行的第一段 |
|---|---|---|---|
| `data_set=2` | scan1 结束时落盘（1.0 mA） | 跳 1 段 | scan 2（健康轮：正常） |
| `data_set=3` | scan2 结束时落盘（21.49 mA） | 跳 2 段 | scan 3 |
| `data_set=4` | v2 暖机段结束时落盘（22.0 mA） | 跳 3 段 | scan 4 |

证据：v3 文件里 scan3 是初始化扫描、scan4 是光耦合扫描，用 `data_set=4` 运行时日志中 `scan number-> 1/2/3/4` 的标记**相邻出现**（一瞬即过），紧接着就是光耦合段的求解——说明 scan1/2/3 全被跳过，初始化扫描从未执行。

**结论（本流程的核心约束）**：把"以 `auto_finish=rtgain` 结束的初始化扫描"放在**第 N+1 段**的位置上，紧跟其后才是 `solve_rtg=yes`。等价做法是选一个 N 更小的恢复点（如 `data_set=3`，跳 2 段，把初始化扫描放在 scan 3）。

> ⚠️ **尚未验证的情形：恢复点是"扫描中途"落盘的数据集**。上面四次观测里，每个数据集都恰好落在某段扫描的结尾，"已完成扫描数"与"data_set − 1"两种规则完全等价，无法区分。2026-09-16 的 nakamura 长跑出现了第一个反例：`#5/#6/#7` 是 scan 4（打印步长 10 mA）**中途**落盘的数据集（30/40/50 mA），而 `#8` 是 scan 4 的终点（60 mA）——此时
>
> | 规则 | 从 `data_set=8` 续算应跳过的段数 |
> |---|---|
> | (A) 该数据集**已完成**的扫描数 | 4 段 → 执行第 5 段 |
> | (B) `data_set − 1` | 7 段 → 全部跳过、程序立刻收工 |
>
> 判别方法（2 分钟）：按 (A) 构造文件跑一次，看日志里第 5 段之后**有没有出现** `Changing: current_1 with step` / `Solver converged`。有 → (A) 成立；几秒内 `Finish Simulation` → 是 (B)，需要在前面补占位扫描把初始化扫描推到第 `data_set` 段。**这一条待补齐后再把本笔记对应内容改成确定结论。**

## 前置条件

- [ ] 中断前已有完整落盘的数据集（`s2.out_#` / `s2.std_#`），见 [[04-操作流程/PICS3D中断续算]]
- [ ] 网格 / 结构未改动（不重跑 layer/geometry、不改 `.msh`）
- [ ] 已知续算起点偏置（查 `s2.sol.msg` 的 `Data set #` 段）
- [ ] 光耦合扫描前面**能插入一段扫描**（本流程的前提）

## 输入

| 输入项 | 说明 | 示例 |
|---|---|---|
| 项目目录 | 算例目录，所有相对路径以此为基准 | `C:\Users\ciomp\Documents\2024Ver_pics3d_examples\pics3d_examples\blue_LD\nakamura` |
| 求解输入 | 含 `restart` 的 `.sol` | `s2.sol` |
| 网格 / 材料 | 与原运行一致 | `s2.msh`、`s2.gain`、`s2.doping` |
| 续算模板 | 已按本流程写好（复制到算例目录并改名为 `s2.sol`） | `06-案例/nakamura_resume_s2_v4.sol` |

## 操作步骤

### 第 1 步：确认续算起点

```powershell
Select-String -Path .\s2.sol.msg -Pattern 'Data set|Current:' | Select-Object -Last 10
```

预期：形如 `Data set # 4 printed at … Current: 0.2200E-01`（22.0 mA）。

### 第 2 步：写 `restart`（必须在 `output` 之后）

```text
include file=s2.doping
output sol_outf=s2.out

restart data_set=4
```

数据集文件名由 `output sol_outf` 的基名决定（手册 §23.529：`output` defines the base name of the output data files; extensions are added … data set number）。**`sol_outf` 与原运行一致，且 `.sol` 用同一基名**（本例都叫 `s2`）。

### 第 3 步（关键）：把"以 RTG 条件结束"的扫描补回来

在 `scan … solve_rtg=yes` **之前**放一段**光耦合仍关闭**、且**以 `auto_finish=rtgain` 结束**的扫描：

```text
$ RTG 初始化扫描：§4.2 要求它紧邻光耦合之前，并以 rtgain 结束
scan var=current_1 value_to=60e-3 print_step=10e-3 &&
init_step=1e-5 min_step=1.e-6 max_step=1.e-3 var2=time value2_to=10 &&
auto_finish=rtgain auto_until=0.6 auto_within=0.1

$ 光耦合扫描
scan var=current_1 value_to=60e-3 print_step=10e-3 &&
init_step=1e-4 min_step=1.e-6 max_step=1.e-3 var2=time value2_to=10 &&
solve_rtg=yes
```

**放置位置是硬约束**（见上节"快进规则"）：设恢复点跳过了 N 段扫描，这段初始化扫描必须是**第 N+1 段**，即"程序实际执行的第一段"，`solve_rtg=yes` 的那段紧随其后。

说明：

- 续算点通常已在 `auto_until` 附近，这段可能**几步内就结束**——这正是期望行为（结束动作本身完成了初始化）；
- 为避免"零步就退出"，可把 `auto_until` 定得比当前 RTG 略高一点（例如当前约 0.6 时用 `auto_until=0.62 auto_within=0.02`），强制它至少真实评估/推进一两步；仍远低于 1.0，不会越过阈值；
- `value_to=60e-3` 只是兜底上限，防止 RTG 迟迟不达标（也避免一路跑进阈值）；
- `auto_until` 按 §4.2 取"刚高于透明密度、且小于 1.0（避免越过阈值）"。

### 第 4 步：运行并同时落盘日志

```powershell
cd C:\Users\ciomp\Documents\2024Ver_pics3d_examples\pics3d_examples\blue_LD\nakamura
& 'C:\Program Files\Crosslight Software\pics3d_2024\pics3d\pics3d.exe' s2.sol 2>&1 |
  Tee-Object -FilePath s2_run.log
```

### 第 5 步：几分钟内判定

```powershell
Select-String -Path .\s2_run.log -Pattern 'Direct eigen solver|peak RTG|Warning|Data set #'
```

判据见下节；不满足就 Ctrl+C 停掉，别浪费几十小时。

### 第 5.1 步：**怎么确认 restart 真的跳到了你想要的那一段**（2026-09-23 更正）

> ⚠️ **更正**：日志里的 `Info: ref active segment number= 1` **不是**扫描快进的段数——那是**空间上的参考段号**（对应 `ref_active_point`）。用它判断"从第几段开始执行"会判错。

**正确判据**：看 `Statement` 序列里 `scan number -> N` 之后**哪一段才出现 `Solving equations with bias.`**——那一段才是真正被执行的扫描段。

```powershell
$L = Get-Content .\s2_run.log
for ($i=0; $i -lt $L.Count; $i++) { if ($L[$i] -match 'Statement:\s*(\S+)|scan number->|Solving equations with bias') { '{0,5}: {1}' -f ($i+1),$L[$i].Trim() } }
```

**实测样例（2026-09-23，`nakamura_LI` 用 `restart data_set=6` 续算）**：

```text
  123: ======Statement: restart======
  126:  Info: ref active segment number=           1     <- 空间参考段，别拿它判断
  129: ======Statement: equilibrium======                <- 扫描 0
  133: ======Statement: rtgain_phase======
  136: ======Statement: scan======      scan number-> 1  <- 宣告但被跳过
  140: ======Statement: scan======      scan number-> 2  <- 宣告但被跳过
  144: ======Statement: scan======      scan number-> 3  <- 真正执行
  148:  Solving equations with bias.                    <- ★ 判据：求解从 scan 3 开始
```

→ 说明程序把"恢复点所在数据集"记为**已完成 2 段**（scan1、scan2），跳过 2 段后执行 scan3。
**这条实测把抽象规则钉死了：即使在某段扫描"中途"落盘的数据集（本例 DS6 写在 scan3 里），也算成该段之前的段数（2 段），不会多跳一段。**

**同时要看的"健康信号"**（与成功跑完 8 个数据集的 v4 续算轮逐项一致）：

| 检查项 | 健康值（v4 成功轮 / 本次 v6 续算） |
|---|---|
| 耦合段起始 `Direct eigen solver at lambda=` | `0.420000000000000`（**续算时回落 `init_wavel` 是正常现象**，两轮完全一样）|
| `photon#` 表里的 `lambda` | **0.424646** µm（不是 0.99x）|
| `Warning: big change in lambda` | **不出现**（只有无害的 `Warning: empty entry in zip archive`）|
| 新数据集 | 按 `print_step` 推进，出现 `Data set #N printed at` + `Completed .std file` |

### 第 6 步：再次续算时的注意

> ### ❌ 反例实测（2026-09-23）：续算点之后**不能**直接是光耦合扫描
>
> **做法**：把 `nakamura_LI`(v6) 的 `restart` 从 `data_set=2` 改成 **`data_set=6`**（想省掉重算 DS3–DS6 的 38 小时），其余不动。
>
> **结果**：**λ 又跳到 0.999 µm**——完全复现老毛病：
>
> ```text
>  L 178: Ignoring LD phase, peak RTG set lambda=  0.999000000000000
>  L 180: Warning: big change in lambda
>  之后 0.999 → 0.998001 → … 每步 ×0.999 爬行（2 小时只爬到 0.998，Data set # = 0）
> ```
>
> **原因**：v6 的扫描段是 `scan1(1 mA) → scan2(auto_finish=rtgain 0.4) → scan3(solve_rtg=yes)`。
> `data_set=6` 使 **scan1 和 scan2 都被快进跳过**，于是 **紧邻光耦合之前没有任何 `auto_finish=rtgain` 扫描**，
> 违反了手册 §4.2 的硬要求（"the scan preceding the introduction of the photon coupling must use the `auto_finish=rtgain` condition to terminate"）。
> 那条扫描负责**算出纵模位置并给出各模光子数初值**；缺了它，RTG 波长搜索就从默认的 **~1.0 µm** 起步，然后在耦合扫描里以 0.1 %/步爬行。
>
> **结论（判据升级）**：`restart data_set=N` 的安全性**不只是"会不会空转"**，关键看**跳过若干段之后，紧随其后的第一段是什么**：
>
> | 跳过后的第一段 | 结果 |
> |---|---|
> | `auto_finish=rtgain` 的初始化扫描 | ✅ 健康（v4 的 `data_set=3`、v6 原来的 `data_set=2` 都是这样）|
> | 直接 `solve_rtg=yes` 的光耦合扫描 | ❌ λ 跳到 ~1.0 µm 并爬行（本次实测）|
>
> **正确做法**：若续算点已经吃掉了原有的初始化段，就必须在 `.sol` 里**补插一段 `auto_finish=rtgain` 的扫描**（放在耦合扫描之前），或者在更早的数据集上续算。
>
> ### ❌❌ 第二次实测（2026-09-23 晚）：**补插初始化段也不行** —— RTG 初始化段无法在"已激射"的偏置上就地完成
>
> **做法**：保持 `restart data_set=6`，在耦合扫描前**补插一段** `scan … auto_finish=rtgain auto_until=1.0 auto_within=0.3`（想法：DS6 已在阈值以上，RTG 已钳在 ≈1.0，应当"评估一次就落带内"）。
>
> **结果**：插入段**被正确执行**了、也**写出了 DS7**（49.71 mA，V = −3.810 V），但那一段**始终满足不了 auto_finish 条件**，最后步长崩到 3.9e-8 A 而退出：
>
> ```text
>  144: ======Statement: scan======   scan number-> 3      <- 补插的 RTG 初始化段，确实被执行
>  148:  Solving equations with bias.
>  247:  Exceeding auto_finish limit.                        <- 第 1 次：值高于带上限
>  305:  Exceeding auto_finish limit.                        <- 第 2 次
>  363:  Exceeding auto_finish limit.                        <- 第 3 次
>  421:  Exceeding auto_finish limit.                        <- 第 4 次
>  ...
> 1693: Changing: current_1 with step:   0.3906E-07         <- 步长已缩到 0.039 µA
> 1697:  Too bad the solver can not go further
> 1698:  Save bias and structure data before exit
> ```
>
> 之后写 DS7 并退出；全日志 `peak RTG set lambda` = 0（耦合段从未启动）、`Warning: big change in lambda` = 0、数据集时间戳只多了 `s2.std_0007`。
>
> **根因（关键结论）**：`auto_finish=rtgain` 的语义是"从亚阈值往上爬，直到 RTG 进入目标带"。而 **DS6 = 49.71 mA 已在阈值以上很远，RTG 已高于任何取在 1.0 附近的带上限** → 目标带永远"Exceeding" → 求解器只能一次次减半步长，最终爬不动而退出。
> **所以：RTG 初始化段不可能在"已激射"的偏置点上就地完成。**
>
> | 续算点 | 所处状态 | 跳过后第一段 | 结果 |
> |---|---|---|---|
> | `data_set=2`（1 mA，**亚阈值**） | 亚阈值 | scan2 = RTG 初始化 | ✅ 健康（09-16 的 v6 原轮就是这样跑出 DS3–DS6 的）|
> | `data_set=3`（19.71 mA，RTG 初始化段终点，**亚阈值**） | 亚阈值 | 下一段 RTG 初始化 | ✅ 预期健康（与 v4 成功轮同构，未实测）|
> | `data_set=6`（49.71 mA，**已激射**） | 阈值以上 | 耦合段 | ❌ λ 跳到 0.999 并爬行 |
> | `data_set=6` + 补插 RTG 初始化段 | 阈值以上 | 补插的 RTG 初始化段 | ❌ 目标带永远 Exceeding → 步长崩溃退出 |
>
> **铁律**：**续算点必须落在亚阈值数据集上**（即"以 `auto_finish=rtgain` 结束的那段扫描的终点"，或更早）。一旦落在耦合段产出的数据集上，无论是否补插初始化段都不行。

每段扫描结束都会推进数据集体号（v2 的暖机段写出 `Data set #4 = 22.0 mA`，覆盖了旧 #4）。**下次续算仍要把第 3 步补回来**——续算点之后必须紧跟一段以 `auto_finish=rtgain` 结束的扫描，再进 `solve_rtg=yes`。

## 预期输出

### 第 5.2 步：无人值守巡检脚本（`scripts/pics3d_watch_nakamura_LI.ps1`）

一个"**只在有事时才出声**"的巡检脚本（默认每小时一次）：

```powershell
# 单次巡检 —— 适合放进 Windows 计划任务（每小时触发一次）
powershell -ExecutionPolicy Bypass -File .\scripts\pics3d_watch_nakamura_LI.ps1 -Once

# 在终端里常驻，每小时一次（安静模式）
powershell -ExecutionPolicy Bypass -File .\scripts\pics3d_watch_nakamura_LI.ps1 -IntervalSec 3600

# 想看每次心跳（调试用）
powershell -ExecutionPolicy Bypass -File .\scripts\pics3d_watch_nakamura_LI.ps1 -IntervalSec 3600 -ShowHeartbeat
```

它每次检查：`restart data_set` 是否为 2、`s2.std_*` 是否新增/被截断、日志中的 λ 故障指纹
（`Warning: big change in lambda`、`peak RTG set lambda=` 偏离 0.4246）、`Solver failed` /
`Too bad the solver can not go further`、pics3d 进程是否消失、日志是否长时间不再增长（默认 8 小时）。

- 正常时**不输出任何内容**；异常时打印 `ALERT [时间] …`；
- 状态存在 `scripts/pics3d_watch_nakamura_LI.state.json`（可安全删除，删掉后下一次重建基线）；
- 首轮会打印一行 `BASELINE …`，之后才进入安静模式。

RTG 初始化段（正常）：

```text
 Direct eigen solver at lambda=  0.420358593663849
 Ignoring LD phase, peak RTG set lambda=  0.4246...
 Modal gain (1/m):  -7xxx.xx       wavel=  0.420358593663849
 Solver converged at
 Current: (A)     0.22xxE-01 -0.22xxE-01
```

随后进入光耦合段时，`peak RTG` 仍应在 0.4246 附近，且**不出现** `Warning: big change in lambda`。

## 验证方法

- [ ] `Direct eigen solver at lambda=` 全程停在 **0.42x** µm，不出现 0.99x
- [ ] 光耦合段第一次 RTG 搜索的 `peak RTG set lambda=` 在 **0.4246** µm 附近
- [ ] **绝不出现** `Warning: big change in lambda`
- [ ] RTG 初始化段结束后写出新数据集（`s2.out_#` / `s2.std_#` 时间戳推进）
- [ ] 按 §4.2 第 5 条人工核对模式表：`photon# lambda long.mode lat.mode` 中相关纵模都在 0.42x µm

## 常见问题

### 问题 1：已经把无耦合扫描插在耦合段前面，仍然跳 0.99x

- 原因：那段扫描**没有以 `auto_finish=rtgain` 结束**，等于没做初始化（本库 v2 实测）。
- 解决：加上 `auto_finish=rtgain auto_until=0.6 auto_within=0.1`；仍不行则回退到"光耦合开启之前"的数据集续算，让程序自己从 `auto_finish=rtgain` 段走到耦合段。
- 详见：[[07-故障排查/常见错误索引]]

### 问题 2：`restart` 之后几秒就 `Finish Simulation`，什么都没算

- 原因：数据集没被加载——最常见是 `.sol` 基名与数据集基名（`output sol_outf`）不一致。
- 解决：`.sol` 与 `sol_outf` 用同一基名（本例 `s2`）。
- 详见：[[04-操作流程/PICS3D中断续算]]

### 问题 3：`Tee-Object` 的日志很长时间不刷新

- 原因：stdout 走管道是块缓冲，日志一段一段跳；屏幕比文件新。
- 解决：用进程 CPU 增量判断是否在算（见 [[04-操作流程/PICS3D中断续算]]）。
- **更可靠的做法**：进度看 `s2.mon`（每个收敛偏置点重写一次），不要看 `.log`。仓库里提供了一个监控脚本 `scripts/pics3d_watch_stop60.ps1`，它每 5 分钟读一次 `s2.mon`、把电流写进 `watch_stop.log`，并在电流到达阈值（默认 60 mA）时等 3 分钟让数据集落盘后自动停掉 `pics3d.exe`：

```powershell
powershell -ExecutionPolicy Bypass -File "D:\Codex-Obsidian\GaN-laser-pics3d\scripts\pics3d_watch_stop60.ps1"
```

  带参数示例：`-Dir 'C:\...\nakamura' -LimitMA 60 -IntervalSec 300 -GraceSec 180`（只读 `s2.mon`，只写 `watch_stop.log`）。

## 相关笔记

- [[04-操作流程/PICS3D中断续算]]
- [[05-API与命令/核心参数]]
- [[01-基础概念/项目结构与文件类型]]
- [[04-操作流程/标准工作流]]

## 来源

手册：[[99-原始资料/通用手册/manual.pdf]] §4.2 *Special bias considerations for PICS3D*（P84-85，`auto_finish=rtgain` 是开启光耦合的前置要求）、§23.445 `longitudinal`（P859-862，`ignore_rtg_phase` / `ref_wavel`）、§23.529 `output`（P983，数据集命名）、ch23.649 `restart`（P1117-1119）。

实测：2026-09-14，nakamura 算例（PICS3D 2024.02.01，Windows 11）

- v1：`restart data_set=4` → `peak RTG = 0.998001000000000`
- v1′：`restart data_set=3` → `peak RTG = 0.999000000000000` + `Warning: big change in lambda`
- v1″：v1′ + `ref_wavel=0.4246e-6` → 与 v1′ 输出逐字节相同
- v2：`data_set=3` + 无 `auto_finish=rtgain` 的暖机扫描 → 暖机段 12 个收敛点正常（λ=0.420359、`max index` 回到 2.55805、无 Warning），但光耦合一开立刻 0.999 + Warning
- v3：`data_set=4` + 文件 scan3 为 `auto_finish=rtgain` 初始化扫描 → 该段被快进跳过；光耦合段首次搜索 0.999 + Warning，随后按 0.999ⁿ 递减（10 小时 0.999 → 0.980）
- v4（**已通过**）：`data_set=3` + 初始化扫描放在第 3 段（快进点之后）+ `auto_until=0.62 auto_within=0.02`
  → 初始化段 21.49 → 21.73 mA 收敛并写出 `Data set #4`；进入 `solve_rtg=yes` 后首次 `peak RTG set lambda= 0.424646392144940`，`Warning: big change in lambda` 0 次，photon# 10 个模式均 @ 0.424646 µm 且光子密度 ~1.0~1.2×10³

验证环境：Windows 11，Crosslight 2024.02.01（Commercial User），PICS3D，`C:\Program Files\Crosslight Software\pics3d_2024\pics3d\pics3d.exe`

**验证状态：已实测通过（2026-09-15）**。v4 在判据点给出 `peak RTG set lambda= 0.424646392144940`（健康轮为 0.424646388493990），全程 `Warning: big change in lambda` 出现 **0 次**，耦合段 photon# 表 10 个模式均在 0.424646 µm 且光子密度非零。此前四次失败（v1/v1′/v1″/v2/v3）也已逐条复现并定位原因。
