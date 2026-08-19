# nextnano 软件体系与 QCL 工作流

> 目标：搞清楚 nextnano 家族里每个软件干什么、QCL 设计该用哪个、完整的仿真链条长什么样。

## 1. 软件家族（本机 2025_08_21 版）

安装根目录：`C:\Program Files\nextnano\2025_08_21`

| 软件 | 输入文件 | 干什么 | QCL 中的角色 |
|---|---|---|---|
| nextnano++ | `.nnp` | 薛定谔-泊松自洽求解、能带、波函数、矩阵元、应变、kp | **主力工具**：设计能级结构与核对跃迁 |
| nextnano³ | `.nn3` | 与 nextnano++ 功能对应的旧版 | 老教程/老语法，可对照 |
| nextnano.NEGF | `.negf` | 非平衡格林函数量子输运，含散射机制 | **进阶主力**：算 I-V、电流密度、增益谱 |
| nextnanomat | GUI | 可视化、模板、批量任务 | 日常操作界面 |
| nextnanoevo | Python | 基于 pymoo 的设计优化 | 自动调参找最优设计 |

## 2. QCL 标准工作流

```
┌─────────────────────────────────────────────────────────────┐
│ 第 1 步：能带结构设计（nextnano++ 1D）                        │
│   输入：层序（阱/垒厚度）、合金组分、电场、温度                │
│   输出：导带边、子带能量、波函数、跃迁矩阵元                   │
├─────────────────────────────────────────────────────────────┤
│ 第 2 步：核对与迭代（nextnano++）                             │
│   目标：ΔE₃₂ = 目标光子能量；z₃₂ 大；注入/去填充能级对准      │
│   手段：调厚度、合金组分、电场                                │
├─────────────────────────────────────────────────────────────┤
│ 第 3 步：自洽与掺杂（nextnano++ poisson + quantum）           │
│   加入掺杂（片密度换算）、泊松自洽、评估能带弯曲               │
├─────────────────────────────────────────────────────────────┤
│ 第 4 步：输运与增益（nextnano.NEGF）                          │
│   输出：I-V 曲线、J-V、增益谱 G(E)、模式分析                  │
├─────────────────────────────────────────────────────────────┤
│ 第 5 步：优化（nextnanoevo）                                  │
│   目标函数：如"270 meV 处增益最大"，变量：阱/垒厚度           │
└─────────────────────────────────────────────────────────────┘
```

## 3. nextnano++ 内部解决什么问题

对每个偏置点：

1. 计算应变（如 InGaAs/AlInAs 应变补偿体系）
2. 计算压电极化/热释电极化电荷（氮化物体系需要，GaAs/InP 体系通常没有）
3. 由泊松方程求导带/价带边（考虑掺杂、极化、应变）
4. 施加外部电场（两种方式见 [[03-输入文件语法入门]]）
5. 解单带有效质量 Schrödinger（或 k.p）方程 → 能量与波函数
6. 输出：能带边、子带能量谱、波函数 |ψ|²、跃迁偶极矩/动量矩阵元、振荡强度、跃迁能量

官方教程强调：**QCL 首轮设计用"加恒定电场 + 不掺杂 + 不泊松自洽"最简单**，先把能级对齐搞对，再逐步加复杂度。

## 4. 本机 QCL 示例文件

### nextnano++（推荐先跑这些）

目录：`C:\Program Files\nextnano\2025_08_21\nextnano++\examples\quantum_cascade_lasers`

| 文件 | 对应文献/用途 |
|---|---|
| `1DQuantumCascadeLaser_nnp.nnp` | Page2001，λ=9 µm GaAs/AlGaAs 中红外 |
| `1DQCL_simple_nnp.nnp` | Capasso1986 简单级联，InGaAs/AlInAs |
| `1DQCL_AlGaAs_Sirtori_APL73_1998_nnp.nnp` | Sirtori1998，λ=9.4 µm |
| `1DQCL_Andrea_Friedrich_NoInjector_InGaAs_APL86_2005_kp_nnp.nnp` | Friedrich2005，λ=10 µm，k.p 版 |
| `1DQCL_Andrea_Friedrich_NoInjector_InGaAs_APL86_2005_sg_nnp.nnp` | 同上，单带版 |
| `1DQCL_Rochat_APL81_2002_nnp.nnp` | Rochat2002，λ=66 µm THz |
| `1DQCL_THz_MIT_Sandia_SemicScTech20_2005_nnp.nnp` | Hu2005，λ=89.2 µm THz |
| `THzQCL_Andrews_Vienna_MatSciEng2008_nnp.nnp` | Andrews2008，λ=107 µm THz，参数化模板 |
| `THzQCL_Andrews_Vienna_MatSciEng2008_nnp_electric_field.nnp` | 同上，电场法变体 |
| `THzQCL_Andrews_Vienna_MatSciEng2008_nnp_no_repeat.nnp` | 同上，手写多层版本 |
| `1DQuantumCascadeLaserSiGe_nnp.nnp` | Dehlinger2000，SiGe 电致发光 |
| `InterbandCascadeLaser_...` | 带间级联激光器（ICL），进阶参考 |

### nextnano³

目录：`C:\Program Files\nextnano\2025_08_21\nextnano3\examples\quantum_cascade_lasers`，同名对应 `.nn3` 文件，另含 `1DQCL_Paiella_APL_92_101112.nn3`、`1DQCL_simple_nn3.nn3` 等。

## 5. 官方在线资料

- QCL 教程页：<https://www.nextnano.com/docu/nextnanoplus/latest/examples/qcl_realistic.html>
- 简单级联教程：<https://www.nextnano.com/docu/nextnano3/tutorials/nnp/1D_simple_cascade_structure.html>
- NEGF 总览：<https://www.nextnano.com/docu/nextnano.NEGF/>
- 增益优化教程（nextnanoevo）：<https://www.nextnano.com/docu/nextnanoevo/tutorials/pymoo/1D_MiDIR_QCL_gain.html>

## 6. 建议的上手路径

1. 在 nextnanomat 中打开 `1DQuantumCascadeLaser_nnp.nnp` 并运行（它是本机默认安装的官方示例）
2. 用 CrosslightView 或 nextnanomat 看图：导带边 + 波函数
3. 打开输出文件 `bias_00000/Quantum/` 下的谱文件，对照 [[04-示例1-Page2001-9um-GaAs-QCL]] 中的期望值
4. 然后复制模板 `templates/QCL输入文件模板.nnp`，改成自己的结构
