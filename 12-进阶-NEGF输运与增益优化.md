# 进阶：NEGF 输运与增益优化

> 能级设计（Schrödinger）只能回答"结构对不对"；**输运与增益**（NEGF）才能回答"能不能出光、出多少"。本篇介绍 nextnano.NEGF 与 nextnanoevo 优化。

## 1. 为什么要 NEGF

薛定谔-泊松求解假设粒子数由费米分布给出，**无法正确处理非平衡输运**（QCL 恰恰是强非平衡器件）：

- 各子带占据数由注入/散射/逃逸动态决定 → 粒子数反转
- 电流沿级联方向流动 → I-V、J-V
- LO 声子、杂质、界面粗糙度、合金、电子-电子散射 → 线宽与寿命

NEGF 把这些全部纳入，直接输出增益谱。

## 2. nextnano.NEGF 能算什么

官方（<https://www.nextnano.com/docu/nextnano.NEGF/>）：

- 量子输运：电流-电压特性（I-V）
- 增益谱：G(E)，例如 `330mV/Gain/SemiClassical_vs_Energy_[0.0,0.0,1.0].dat`
- 散射机制：LO 声子、声学声子、带电杂质、界面粗糙度、合金、电子-电子
- 应用：QCL、QCD、RTD、QWIP、超晶格、T2SL、ICL

两个版本：

- `nextnano.NEGF_classic`（C#，已停更，仅 Windows）
- `nextnano.NEGF`（C++，2022 起推荐，Windows/Linux）

本机：`C:\Program Files\nextnano\2025_08_21\nextnano.NEGF`

## 3. 从 nextnano++ 设计到 NEGF 的衔接

1. 先用 nextnano++ 把周期结构与能级设计好（[[09-QCL设计流程Checklist]] 阶段 0–5）
2. 把结构（层序、掺杂、偏置）翻译成 `.negf` 输入文件
3. 设偏置（NEGF 用**每周期偏压**，例如 330 mV / 若干周期）
4. 跑输运：检查 I-V 是否合理、各子带占据数是否反转
5. 取增益谱：找峰值位置（应≈目标光子能量）与峰值幅度

## 4. 增益谱输出怎么看

```
330mV/Gain/SemiClassical_vs_Energy_[0.0,0.0,1.0].dat
```

列：光子能量（meV） | 增益（cm⁻¹）

设计判据：

- 峰值增益对应能量 ≈ 目标光子能量（±线宽内）
- 峰值幅度越大越好（实用 QCL 材料增益峰值通常在几十到几百 cm⁻¹）
- 增益带宽与线宽相关（LO 声子、温度）

## 5. 自动优化：nextnanoevo

官方教程：<https://www.nextnano.com/docu/nextnanoevo/tutorials/pymoo/1D_MiDIR_QCL_gain.html>

示例：以 Bai2010 InGaAs/InAlAs 中红外 QCL（峰值目标 275 meV）为起点，**用厚度缩放因子 $thickness_scaling_factor 优化 270 meV 处增益**：

### 5.1 指定输入/输出

```python
from nextnanoevo.io import IO

output_files = [("330mV", "Gain", "SemiClassical_vs_Energy_[0.0,0.0,1.0].dat")]

nn_io = IO(
    input_file_path,
    variable_names=["thickness_scaling_factor"],
    target_output_paths=output_files,
)
```

### 5.2 定义目标函数

```python
import numpy as np

def get_gain_at_270mev(df_list):
    df = df_list[0]
    energy = df.coords["Photon Energy"].value   # meV
    gain   = df.variables["Gain"].value
    mask   = np.isclose(energy, 270, atol=1e-3)
    return -gain[mask]                          # 最大化 → 最小化
```

### 5.3 跑进化算法

```python
from nextnanoevo.metric import Metric
from nextnanoevo.optimizer import Evolution

metric = Metric(input_length=1, output_length=1, extraction_function=get_gain_at_270mev)
evolution = Evolution(nextnanoio=nn_io, metric=metric, bounds=([1.0], [1.1]), size=5)
evolution.run(gen=4, seed=12345)
```

教程结果：$thickness_scaling_factor = 1.060 → 270 meV 增益 161.8 cm⁻¹（起点 199.49 cm⁻¹ @ 目标附近，峰值随缩放移动）。

优化变量可以扩展为：各阱宽、各垒宽、合金组分、掺杂浓度、周期数、偏压。

## 6. 设计闭环（完整版）

```
文献/经验设计
   ↓ nextnano++（快）
能级/矩阵元验证：ΔE、z₃₂、注入/去填充
   ↓ nextnano.NEGF（慢但权威）
输运 + 增益谱：I-V、G(E)
   ↓ nextnanoevo（自动）
厚度/组分/掺杂优化 → 回到 NEGF 验证
   ↓
最终设计归档（层序表 + 仿真参数 + 预测性能）
```

## 7. 阅读材料

- NEGF 官方文档：<https://www.nextnano.com/docu/nextnano.NEGF/>
- 增益优化教程：<https://www.nextnano.com/docu/nextnanoevo/tutorials/pymoo/1D_MiDIR_QCL_gain.html>
- 旧 nextnano.QCL 文档（NEGF 背景）：<https://nextnano-docu.northeurope.cloudapp.azure.com/dokuwiki/>
