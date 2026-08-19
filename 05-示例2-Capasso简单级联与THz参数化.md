# 示例 2：Capasso 简单级联与 THz 参数化模板

> 两个补充示例，覆盖另外两种输入写法：**接触偏压法**与**全参数化 + 周期重复**。

## 1. Capasso 简单级联（InGaAs/AlInAs）

官方教程：<https://www.nextnano.com/docu/nextnano3/tutorials/nnp/1D_simple_cascade_structure.html>

本地文件：`C:\Program Files\nextnano\2025_08_21\nextnano++\examples\quantum_cascade_lasers\1DQCL_simple_nnp.nnp`

### 1.1 物理

来自 Capasso 等 1986 年的早期方案（IEEE JQE 22, 1853）：

- Al₀.₄₈In₀.₅₂As 垒 / In₀.₅₃Ga₀.₄₇As 阱（InP 衬底，晶格匹配）
- 每个阱 13.9 nm，共 5 个阱 + 6 个垒
- 电场 -89 kV/cm
- 设计意图：**3→2 辐射跃迁（发光），2→1 通过共振隧穿快速去填充**
- 每个阱的基态与下一阱第 3 激发态共振 → 基态被"抽走" → 粒子数反转

### 1.2 输入要点

**加电场用接触偏压法**：

```python
contacts{
    charge_neutral{
        name = "leftgate"
        bias = 0.0
    }
    charge_neutral{
        name = "rightgate"
        bias = 1.36081   # 1.36081 V / 152.9 nm ≈ -89 kV/cm
    }
}
```

**必须同时解泊松**（否则能带被抬到费米能级以上）：

```python
run{
    poisson{ }   # 必须解
    quantum{ }
}
```

**40 个本征态**：

```python
quantum{
    region{
        name = "quantum_region"
        x = [0, 152.9]
        no_density = yes
        boundary{ x = dirichlet }
        Gamma{ num_ev = 40 }
        ...
```

**矩阵元输出**（旧版关键字 `intraband_matrix_elemets`，注意拼写）：

```python
intraband_matrix_elemets{
    Gamma{ }
    output_matrix_elements = yes
    output_transition_energies = yes
    output_oscillator_strengths = yes
}
```

输出：`bias_00000/Quantum/momentum_matrix_elements_quantum_region_Gamma_100.txt`、`transition_energies_quantum_region_Gamma_Gamma.txt`。

## 2. THz QCL 参数化模板（Andrews2008）

本地文件：`C:\Program Files\nextnano\2025_08_21\nextnano++\examples\quantum_cascade_lasers\THzQCL_Andrews_Vienna_MatSciEng2008_nnp.nnp`

对应论文：Andrews et al., *Mater. Sci. Eng. B* **147**, 152 (2008)，λ≈107 µm（2.8 THz）LO 声子去填充 THz QCL。

### 2.1 全参数化：所有设计量都是 `$变量`

```python
$Material_well        = "GaAs"
$Material_barrier     = "Al(x)Ga(1-x)As"
$NumberOfEigenvalues  = 30
$ElectricField        = -9.8e5        # -9.8 kV/cm
$Temperature          = 20            # K
$DopingConcentration  = 0.0           # cm^-3
$AlloyContent_barrier = 0.15
$CBO                  = 0.1518        # Al0.15Ga0.85As 的导带带阶 [eV]
$GridSpacing          = 0.1
$LENGTH_OF_PERIOD     = 54.6          # 周期长度，也是 array_x 的 shift
$ThicknessBarrier_1   = 3.0
$ThicknessWell_1      = 9.2
...
```

这种写法可以直接在 nextnanomat 的模板界面里改参数（文件里有 `(HighlightInUserInterface)` 标注）。

### 2.2 周期重复：`array_x`

写一个周期的层，再用 `array_x` 复制：

```python
region{
    line{ x = [ $Barrier1_left, $Barrier1_right ] }
    ternary_constant{ name = $Material_barrier  alloy_x = $AlloyContent_barrier }
    array_x{
        max   = 3               # 总共重复 3 次
        shift = $LENGTH_OF_PERIOD
    }
}
```

掺杂层也可以带 `array_x` 逐周期重复：

```python
region{
    line{ x = [ $Doping1_left, $Doping1_right ] }
    doping{ constant{ name = "fully-ionized" conc = $DopingConcentration } }
    array_x{ max = 3  shift = $LENGTH_OF_PERIOD }
}
```

### 2.3 掺杂：片密度 ↔ 体浓度换算

文件注释里给了换算示例：

```
Sample A:  2.80e15 cm^-3 × 15.5 nm = 0.43×10^10 cm^-2
Sample E: 25.00e15 cm^-3 × 15.5 nm = 3.88×10^10 cm^-2
```

公式：**n_sheet [cm⁻²] = n_vol [cm⁻³] × 掺杂层厚度 [cm]**，其中 15.5 nm = 1.55×10⁻⁶ cm。

### 2.4 变体文件

- `THzQCL_Andrews_Vienna_MatSciEng2008_nnp_electric_field.nnp`：改用 `poisson.electric_field` 加场
- `THzQCL_Andrews_Vienna_MatSciEng2008_nnp_no_repeat.nnp`：不用 `array_x`，逐层手写（适合想看清全部坐标时对照）

## 3. 三个示例的写法对比

| 写法 | Page2001 | Capasso 简单级联 | THz Andrews |
|---|---|---|---|
| 材料 | GaAs/AlGaAs | InGaAs/AlInAs | GaAs/AlGaAs (x=0.15) |
| 加电场 | `poisson.electric_field` | `contacts` 偏压 | `contacts` 偏压（另有电场版） |
| 解泊松 | 否（`run{ quantum{} }`） | 是（`run{ poisson{} quantum{} }`） | 视 doping 而定 |
| 周期处理 | 手写 3 个周期 | 手写 1 个超晶格 | `array_x` 参数化 |
| 掺杂 | 无 | 无 | 可调 `$DopingConcentration` |
| 本征态 | 20 | 40 | 30 |

## 4. 实操建议

- 想快速理解能级结构 → 先跑 Page2001
- 想理解"接触 + 泊松"流程 → 跑 Capasso 简单级联
- 想建自己的参数化模板做厚度扫描 → 以 THz Andrews 为蓝本
- 想自动扫描厚度/合金 → 用 nextnanomat 的 Template 功能，或 nextnanoevo（见 [[12-进阶-NEGF输运与增益优化]]）
