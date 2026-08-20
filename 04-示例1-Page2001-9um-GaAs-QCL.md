# 示例 1：Page2001 9 µm GaAs/AlGaAs QCL 复现

> 这是 nextnano 官方 QCL 教程的**核心示例**，强烈建议第一个跑通它。
> 官方教程：<https://www.nextnano.com/docu/nextnanoplus/latest/examples/qcl_realistic.html>
> 本地文件：`C:\Program Files\nextnano\2025_08_21\nextnano++\examples\quantum_cascade_lasers\1DQuantumCascadeLaser_nnp.nnp`

## 1. 背景

复现论文：

> 300 K operation of a GaAs-based quantum-cascade laser at λ = 9 µm
> H. Page, C. Becker, A. Robertson, G. Glastre, V. Ortiz, C. Sirtori
> **Appl. Phys. Lett. 78 (22), 3529 (2001)** — <https://doi.org/10.1063/1.1374520>

目标：复现论文 Fig. 1 —— 导带边 + 关键波函数，以及跃迁能量和偶极矩阵元。

## 2. 结构与关键参数

材料：GaAs 阱 / Al₀.₄₅Ga₀.₅₅As 垒

**周期层序（0–45 nm，粗体为垒，单位 nm）**：

`4.6 / 1.9 / 1.1 / 5.4 / 1.1 / 4.8 / 2.8 / 3.4 / 1.7 / 3.0 / 1.8 / 2.8 / 2.0 / 3.0 / 2.6 / 3.0`

| 关键参数 | 值 |
|---|---|
| 导带带阶 CBO | 390 meV（通过 bowing 校准） |
| 电场 | -48.5 kV/cm（-48.5×10⁵ V/m，本地文件值；教程页面写 -48） |
| 参考电势 | 2.1315 V（左端点） |
| 温度 | 300 K |
| 掺杂 | 本示例不掺杂（论文原结构在两段 9.8 nm 区域内 Si 掺杂，片密度 3.8×10¹¹ cm⁻²） |
| 模型 | 单带有效质量（非 8 带 k.p） |
| 边界条件 | Dirichlet（有外加电场，不能用周期边界） |
| 量子区 | 覆盖整个器件，解 20 个本征态 |

## 3. 输入文件要点逐段拆解

### 3.1 电场与参考电势

```python
$electric_field = -48.5e5    # [V/m]
```

```python
poisson{
    electric_field{
        strength            = $electric_field
        reference_potential = 2.1315   # 与 nextnano³ 对齐
    }
    output_potential{ }
    output_electric_field{ }
}
```

### 3.2 层序写法（节选）

```python
region{  # AlGaAs barrier  4.6 nm
    line{ x = [0, 4.6] }
    ternary_constant{ name = "Al(x)Ga(1-x)As"  alloy_x = 0.45 }
}
region{  # GaAs well  1.9 nm
    line{ x = [4.6, 6.5] }
    binary{ name = "GaAs" }
}
```

注意官方文件把完整周期写了两遍（含负坐标一侧），即共 3 个周期左右，且量子区 `x = [-26.1, 49.6]` 覆盖全部。这正对应"算 3 个周期、取中间周期"的建议（见 [[08-边界条件-网格-数值技巧]]）。

### 3.3 带阶校准（390 meV）

```python
database{
    bowing_zb{
        name = "AlGaAs_Bowing_Ga"
        valence = III_V
        valence_bands{ bandoffset = -0.091925 }
    }
    bowing_zb{
        name = "AlGaAs_Bowing_Al"
        valence = III_V
        valence_bands{ bandoffset = -0.091925 }
    }
}
```

### 3.4 量子区

```python
quantum{
    region{
        name = "quantum_region"
        x = [-26.1, 49.6]
        no_density = yes
        boundary{ x = dirichlet }
        Gamma{ num_ev = 20 }
        output_wavefunctions{ max_num = 9999 all_k_points = yes
                              amplitudes = no probabilities = yes }
        momentum_matrix_elements{
            polarization{ name = "component_x" re = [1, 0, 0] }
            Gamma{ }
        }
        transition_energies{ Gamma{ } }
    }
}
```

## 4. 期望结果（对照表）

论文/官方教程给的验证基准：

| 物理量 | nextnano 计算 | Page2001 |
|---|---|---|
| 跃迁偶极矩 ⟨ψ₁₀\|z\|ψ₆⟩ | 1.6655 nm | 1.7 nm |
| 跃迁能量 ΔE₁₀₋₆ | 147.7 meV | 160 meV |

官方还给出关键波函数编号：基态 4（红）、下激光态 6（蓝）、激发态 10（粉）、注入态 8（绿）。**注意这些编号依赖本征态排序，你自己的结构编号会不同**，要按空间位置和能量分布人工识别。

## 5. 跑通后的检查清单

- [ ] 导带边呈现均匀斜坡（-48.5 kV/cm 电场）
- [ ] 中间周期的波函数左右两端衰减到零（边界伪态在两端，中间态干净）
- [ ] 找到成对的"发射阱"波函数（|3⟩ 与 |2⟩），二者 ΔE ≈ 138 meV（λ≈9 µm）
- [ ] 矩阵元文件里对应跃迁的 z ≈ 1.7 nm 量级
- [ ] 注入态与上激光态在空间上重叠、能量上接近

## 6. 本机实测结果（2026-08-20，nextnano++ 2.2.6）

已在本机用命令行完整跑通本示例，输出目录：`runs/page2001/out_z`。实测与教程基准对照：

| 物理量 | 本机实测 | 教程基准 | 说明 |
|---|---|---|---|
| 跃迁能量 ΔE₁₀₋₆ | 147.4 meV | 147.7 meV | 吻合 |
| 偶极矩 z₁₀₋₆ | 1.231 e·nm | 1.6655 nm | 同量级，见下方敏感性分析 |
| 带阶 CBO | 0.390 eV | 390 meV | 校准生效，从 bandedges.dat 界面台阶读出 |

![[page2001_bandstructure.png]]

*Page2001 结构实测：导带边（黑）+ 能量平移后的 |ψ|²：态 4（红，基态）、态 6（蓝，下激光态）、态 8（绿，注入态）、态 10（品红，上激光态）。*

## 7. 参数敏感性实验（为什么 z 与教程有出入）

教程页基准值来自旧版文档/旧参数集。用本机文件做三个变体对比：

| 变体 | ΔE₁₀₋₆ | z₁₀₋₆ | 说明 |
|---|---|---|---|
| 本地 2025 版文件（-48.5 kV/cm + bowing） | 147.4 meV | 1.231 e·nm | 默认 |
| 教程页参数（-48 kV/cm，ref=0.092） | 146.8 meV | 1.434 e·nm | 电场变 1%，z 变 16% |
| 去掉 bowing 校准（默认带阶） | 143.9 meV | 0.851 e·nm | 带阶不校准，ΔE 偏 4 meV，z 大幅变小 |

结论：

1. **跃迁能量对带阶校准敏感**（±4 meV），复现实验必须校准 CBO（本示例 390 meV）
2. **偶极矩 z 对电场与带阶都很敏感**（1.2→1.4 e·nm），设计迭代时应固定一致的参数集
3. 教程的 1.6655 nm 出自旧版软件默认参数，本机新版给出 1.2–1.4 e·nm，量级一致、可作设计判断

> 补充：nextnano 输出的振荡强度 f 用的是自由电子质量 m₀ 约定（本机 f₁₀,₆ = 5.86 对应 m* = m₀），不要直接与教材里 m* 定义的 f-sum 规则（Σf=1）比较。

## 8. 如何把它改成自己的设计

1. 复制该文件（或仓库模板 `templates/QCL输入文件模板.nnp`）
2. 替换层序：把 `line{ x = [...] }` 的坐标与材料名改成目标结构
3. 修改 `alloy_x`、`database` 中的带阶校准（对应材料的 CBO）
4. 修改 `$electric_field`、`reference_potential`、`temperature`
5. 增大 `num_ev` 直到覆盖中间周期的所有相关能级
6. 重新跑 → 用跃迁能量判断波长是否对准 → 微调阱宽

命令行运行方法与验证流程见 [[13-命令行运行nextnano-与结果验证]]。

## 9. 相关链接

- nextnano³ 版教程（含 flow-scheme 说明）：<https://www.nextnano.com/nextnano3/tutorial/1Dtutorial_QuantumCascadeLaser.htm>
- 简单级联版教程：[[05-示例2-Capasso简单级联与THz参数化]]
