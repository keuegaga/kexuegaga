# nextnano.NEGF 输入文件逐行讲解（.negf）

> 面向初学者的 .negf 文件导读。以 `designs/qcl8um_design_v2_negf_calibrated.negf` 为范本，逐块说明"每一段在算什么"。

## 0. 文件总体结构

一个 .negf 文件只有一个顶层块 `nextnano.NEGF{ ... }`，里面依次是若干子块。`#` 是注释，`=` 左边是关键字、右边是值。单位要自己写进注释，代码不自动换算。

```text
nextnano.NEGF{
    Header{ }               # 元信息（作者、说明，纯注释用途）
    SweepParameters{ }      # 电压扫描范围（每周期 mV）
    OverwriteMaterialDatabase{ }  # 覆盖材料库参数
    Temperature = 300
    Crystal{ }              # 晶格结构、晶向、衬底、应变/极化开关
    Materials{ }            # 用哪些材料、组分、别名、带阶
    Structure{ }            # 层序（垒/阱厚度）+ 掺杂
    Scattering{ }           # 散射机制（决定寿命/线宽）
    Poisson = yes           # 是否自洽解泊松
    LateralDiscretization{ } # 面内（xy）能带如何处理
    SimulationParameter{ }  # 数值收敛与能量窗
    Output{ }               # 输出开关
    Gain{ }                 # 增益计算方式与光子能量窗
}
```

## 1. Header 与 SweepParameters

```python
Header{
    Author = "ciomp + Codex"
    Content = "8 um QCL v2. ..."
}
SweepParameters{
    SweepType = Voltage
    Min = 160      # mV per period
    Max = 320
    Delta = 20
}
```

- `SweepType=Voltage`：扫描"每周期电压降"（单位 mV）
- `Min/Max/Delta`：160 到 320 mV，步长 20 → 共 9 个偏置点
- 每周期电压 V 与电场 F 的关系：`F = V / L_period`。我们的周期 22.5 nm，所以 320 mV ≈ 142 kV/cm

> 新手最容易混淆：这里的电压是每周期，不是整支器件几十 V 的宏观偏压。

## 2. OverwriteMaterialDatabase

```python
OverwriteMaterialDatabase{
    Material{ Name = "In(x)Ga(1-x)As"  DeformationPotential = 0.0 }
    Material{ Name = "Al(x)In(1-x)As"  DeformationPotential = 0.0 }
}
```

覆盖材料库里的形变势。对三元材料置 0，是官方 Bai 示例的做法（让应变不额外移动三元材料导带边，简化带阶控制）。

## 3. Crystal（晶格/衬底/应变）

```python
Crystal{
    CrystalStructure = Zincblende
    Orientation{ zAxis{ h=0 k=0 l=1 }  yAxis{ h=0 k=1 l=0 } }
    MaterialSubstrate{ Name = InP }
    Strain = yes
    Piezoelectricity = yes
    Pyroelectricity = yes
}
```

- 生长方向取 [001]（z 轴）
- 衬底 InP：应变以此为准；In₀.₆Ga₀.₄As 压应变、Al₀.₅₆In₀.₄₄As 张应变（应变平衡）
- 锌闪矿 [001] 净压电极化为 0，开关影响可忽略

## 4. Materials（材料与带阶）

```python
Materials{
    Material{
        Name = "In(x)Ga(1-x)As"
        AlloyComposition = 0.60
        Alias = well
        EffectiveMassFromKpParameters = no
        Overwrite{ ConductionBandOffset = 0.0 }
    }
    Material{
        Name = "Al(x)In(1-x)As"
        AlloyComposition = 0.56
        Alias = barrier
        EffectiveMassFromKpParameters = no
        Overwrite{ ConductionBandOffset = 0.78 }
    }
    NonParabolicity = yes
    InPlaneNonParabolicity = yes
    NumberOfBands = 3
    UseConductionBandOffset = yes
}
```

- `AlloyComposition`：三元组分 x
- `Alias`：给材料起别名，后面 Layer 里直接写 `well` / `barrier`
- `Overwrite{ ConductionBandOffset }`：手动指定导带带阶（eV），是本设计校准 NEGF 带阶的关键
- `UseConductionBandOffset = yes`：使用上面的 CBO 数值来排布导带边
- `NumberOfBands = 3`：计入 Γ/L/X 三个导带谷

## 5. Structure（层序与掺杂）

```python
Structure{
    Layer{ Material = barrier  Thickness = 3.4 }
    Layer{ Material = well     Thickness = 4.0 }
    Layer{ Material = barrier  Thickness = 1.3 }
    Layer{ Material = well     Thickness = 5.2 }
    Layer{ Material = barrier  Thickness = 0.9 }
    Layer{ Material = well     Thickness = 2.6 }
    Layer{ Material = barrier  Thickness = 1.9 }
    Layer{ Material = well     Thickness = 3.2 }

    Doping{
        DopingStart = 0.0
        DopingEnd = 7.4
        DopingSpecification = 1     # 1 = 体密度 cm^-3
        DopingDensity = 1.0e17
    }
}
```

- `Layer` 按生长方向列出，程序自动把这一串层当一个周期重复
- 周期 = 3.4+4.0+1.3+5.2+0.9+2.6+1.9+3.2 = 22.5 nm
- `DopingSpecification=1` 表示 DopingDensity 是体浓度（cm⁻³）；`=0` 则是面密度（cm⁻²）
- 掺杂区 [0, 7.4 nm] = 注入垒(3.4) + 第一阱(4.0)

## 6. Scattering（散射机制）

```python
Scattering{
    MaterialForScatteringParameters = well
    InterfaceRoughness{
        AmplitudeInZ = 0.07        # nm
        InterfaceAutoCorrelationType = 0
        CorrelationLengthInXY = 8  # nm
    }
    AcousticPhononScattering = no
    ScreeningTemperatureType = 1
    TemperatureOffsetParameter = 200
    ImpurityScatteringStrength = 1.0
    ElectronElectronScattering = no
    AlloyScattering = yes
    AlloyScatteringStrength = 0.5
}
```

- LO 声子散射默认始终开启（没列出来不等于没有）
- 界面粗糙度、合金无序、杂质散射是 QCL 展宽与下态寿命的主要来源
- `ElectronElectronScattering=no` 是省时间做法；300 K 精确计算建议后续开 yes

## 7. 数值与输出控制

```python
Poisson = yes
LateralDiscretization{
    MaterialForLateralMotion = well
    Value = 50
}
SimulationParameter{
    CoherenceLengthInPeriods = 1
    SpatialGridSpacing = 0.2
    nLateralPeriodsForBandStructure = 1
    EnergyGridSpacing = 5
    EnergyRangeLateral = 200
    EnergyRangeAxial = 350
    ConvergenceValueGF = 1e-4
    ConvergenceValueCurrent = 1e-4
    NMaxIterations = 500
    BiasForInitialElectronicModes = 240
}
Output{
    EnergyResolvedPlots = yes
    EnergyResolvedGain = yes
}
```

## 8. Gain（增益计算）

```python
Gain{
    GainMethod = 1
    dEPhotSelfConsistent = 5
    EphotonMinSelfConsistent = 80
    EphotonMaxSelfConsistent = 200
    Vmin = 150
    Vmax = 330
    FermiGoldenRule{ Linewidth = 10 }
}
```

- 光子能量窗 80–200 meV 对应 6.2–15.5 µm
- `GainMethod=1` 自洽算增益（含光子引起的布居变化）；另有费米黄金规则快速近似

## 9. 本仓库实测踩过的语法坑

1. `Content` / 字符串里不要写 `++` 或 `;`（会报"以引号开头的意外字符"）
2. `ConductionBandOffset` 必须放进 `Material{ Overwrite{ ... } }`，不能直接放 Material 下
3. 注释只能 `#`；数值单位不会自动换算，务必自己核对

## 相关笔记

- 输出怎么读：[[17-NEGF输出数据逐步分析]]
- 本设计结果：[[18-结果解读与实验指导]]
- 之前 v1 的带阶诊断：[[15-NEGF首次验证与优化-8um设计]]
