# 命令行运行 nextnano++ 与结果验证

> 本机实测验证的工作流：不用图形界面，直接命令行跑仿真，适合批量调参和脚本化。2026-08-20 用此流程跑通了 Page2001 示例（见 [[04-示例1-Page2001-9um-GaAs-QCL]]）。

## 1. 可执行文件与数据库

```text
可执行：C:\Program Files\nextnano\2025_08_21\nextnano++\bin\nextnano++_Intel_64bit.exe
数据库：C:\Program Files\nextnano\2025_08_21\nextnano++\database\database.nnp
```

版本：nextnano++ 2.2.6（2025-08-21）。

## 2. 基本命令

```powershell
& '...\nextnano++_Intel_64bit.exe' -d '...\database.nnp' -o '<输出目录>' '<输入文件.nnp>'
```

常用模式：

| 模式/选项 | 作用 |
|---|---|
| （无 runmode） | 完整运行仿真 |
| `-p` | 只解析输入文件（快速查语法错误） |
| `-s` | 解析并生成结构后停止 |
| `-d 数据库` | 指定材料数据库 |
| `-o 目录` | 指定输出目录 |
| `-l licfile` | 指定许可证文件（本机无需显式指定） |

注意：`-p` 等 runmode 要放在选项之前：`-p -d db input.nnp`。

## 3. 输出目录结构（v2.2.6 实测）

与旧版教程路径略有不同，新版结构如下：

```text
<out>/<输入文件名>/
├── bias_00000/
│   ├── bandedges.dat                    # 导带/价带边（x + Gamma/L/X/HH/LH/SO 各列）
│   ├── potential.dat / electric_field.dat
│   ├── density_electron.dat
│   └── Quantum/quantum_region/
│       ├── Gamma/
│       │   ├── energy_spectrum_k00000.dat      # 本征能量
│       │   ├── probabilities_k00000.dat        # |ψ|²
│       │   └── probabilities_shift_k00000.dat  # 能量平移后的 |ψ|²（画图用）
│       └── Gamma_Gamma/
│           ├── transition_energies_k00000.txt
│           ├── momentum_matrix_elements_k00000_component_x.txt
│           ├── dipole_moment_matrix_elements_k00000_component_x.txt
│           └── dipole_moment_oscillator_strengths_k00000_component_x.txt
└── Structure/                              # 材料、区域、接触信息
```

## 4. 偶极矩输出的正确写法（v2.2.6）

放在 `quantum{ region{ ... } }` 内：

```python
dipole_moment_matrix_elements{
    polarization{ name = "component_x" re = [1, 0, 0] }
    Gamma{ }
    output_matrix_elements = yes
    output_oscillator_strengths = yes
}
```

注意：

- **必须**有 `polarization`（name + re 向量）
- **没有** `output_transition_energies` 子项（2.2.6 会报 validation error；旧教程里的 `intraband_matrix_elemets{ output_transition_energies=yes }` 是旧语法）
- 偶极矩输出单位是 `e*nm`（电荷 × 长度），跃迁能量另见 `transition_energies_*.txt`

## 5. 验证工作流（照着做一遍）

1. 运行仿真 → 看 `energy_spectrum_k00000.dat` 找到激光跃迁两态（例：态 10 与态 6）
2. 算 ΔE = E₁₀ − E₆（例：0.936209 − 0.788770 = 147.4 meV）
3. 在 `transition_energies_*.txt` 里核对同一跃迁
4. 在 `dipole_moment_matrix_elements_*.txt` 里读 z（例：态 6→10 = 1.2307 e·nm）
5. 从 `bandedges.dat` 的界面台阶读带阶 CBO（例：x=4.6 处垒/阱 Gamma 边之差 = 0.390 eV）
6. 画图：`bandedges.dat` 的 Gamma 列 + `probabilities_shift_*.dat` 的能量平移波函数列（见 `runs/plot_page2001.py`）

## 6. 批量调参建议

- 用 `$变量` 参数化输入文件（THz 模板就是范例，见 [[05-示例2-Capasso简单级联与THz参数化]]）
- 写循环脚本：改参数 → 跑 → 从输出 grep ΔE/z → 汇总表格
- 网格收敛性：把 grid spacing 从 0.1 改 0.05 重跑，ΔE 变化 < 1 meV 即收敛（[[08-边界条件-网格-数值技巧]]）
- 输出目录用 `-o` 分开管理，避免同名文件覆盖
