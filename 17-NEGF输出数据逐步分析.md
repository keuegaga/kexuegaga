# nextnano.NEGF 输出数据逐步分析（初学者）

> 用本仓库 8 µm QCL 设计 V2/V3 的实际输出，手把手教你怎么从"一堆文件"里读出结论。

## 1. 拿到输出目录先看三件事

顺序：是否收敛 → 是否有正增益 → 哪个能量/偏置发光。

### 第 1 步：日志尾部 `qcl8um_design_v2.log`

找到类似：

```text
Electrostatic potential: Converged
Current density = 962.967 A/cm^2
nextnano.NEGF FINISHED
```

出现 Converged 和 FINISHED 才算数。若 Warnings.log 有内容也要看。

### 第 2 步：`Gain_vs_Voltage.dat`（总增益表）

列：Potential per period[mV] | Maximum gain[1/cm] | Photon energy at maximum gain[meV]。

V2 实测：

```text
160   -9.87   200
240   -7.44   200
300   -2.12   185
320   +5.51   180   <- 唯一正增益点
```

读法：低偏置全负（吸收），只有 320 mV 出现正增益 +5.5 cm⁻¹，峰值在 180 meV。

### 第 3 步：`Current_vs_Voltage.dat`（I-V）

V2 电流：160 mV 处 954 A/cm²，320 mV 处 963 A/cm²。QCL 电流通常在 kA/cm² 量级，这里量级合理。

## 2. 深入单个偏置点（320 mV 为例）

目录 `320mV/` 下最重要的是两个子文件夹。

### 2.1 `Gain/Gain_SelfConsistent_vs_Energy.dat`（增益谱）

两列：光子能量 meV | 增益 cm⁻¹。320 mV 的谱画出来：

![[negf_v2v3_gain_320mV.png]]

- V2（蓝，带阶 0.78 eV）峰值 +5.51 cm⁻¹ @180 meV
- V3（红，带阶 0.69 eV）峰值 +7.89 cm⁻¹ @180 meV
- 180 meV ↔ λ = 1240/180 = 6.89 µm

判断：这个设计能出增益，但波长在 6.9 µm，不是目标的 8 µm。

### 2.2 `EnergyEigenstates/`（能级、占据、偶极）

| 文件 | 读什么 |
|---|---|
| `Populations.txt` | 每个态的电子占据数 |
| `Dipoles.txt` | 态间偶极矩 <i|z|j>（nm） |
| `EigenStates.dat` | 各态波函数沿 x 的空间分布 |
| `Lifetimes.dat` | 态寿命 |
| `ScatteringRate_*.txt` | 各散射通道速率 |
| `SubbandFermiLevel.txt` | 子带准费米能级 |

#### 320 mV 的能级结构（V2，每周期 5 个子带）

```text
lev.1 =  146 meV ─┐
                  ├ 156.7 meV   <- 我们设计的"8 µm"跃迁
lev.2 =  -11 meV ─┤
                  ├ 51.4 meV
lev.3 =  -62 meV ─┤
                  ├ 96.4 meV
lev.4 = -159 meV ─┤
                  ├ 34.8 meV
lev.5 = -193 meV ─┘
```

偶极矩阵元：lev1↔lev2 的 |z|=2.07 nm（最强档）；lev1↔lev3 的 |z|=0.91 nm。

#### 关键结论：为什么发光在 180 meV 而不是 157 meV

占据数（320 mV）：

```text
state1(lev.1)=0.078   state2(lev.2)=0.092
state3(lev.3)=0.081   state4(lev.4)=0.224   state5(lev.5)=0.525
```

lev1↔lev2 跃迁能量 156.7 meV，但上态 lev.1(0.078) 比下态 lev.2(0.092) 占得少，所以是吸收（对应谱里 155 meV 处增益为负）。

正增益出现在 180 meV，来自更高能量跃迁的贡献。也就是说：我们按固定电场设计的 156 meV 跃迁，在自洽输运下并没有反转，真正反转的跃迁落在 ~180 meV。这是"能带设计"与"NEGF 输运"之间常见且必须补的一环。

## 3. 为什么 `L-I-V.dat` 全是 0

因为我们没有配置腔与 EM 模式（没有 cavity losses、没有 EMfield 参数），NEGF 只算了材料增益谱，没算激光器出光功率。要看 L-I 曲线，需要：

- 加 `Gain{ CavityLosses = ... OverlapFactor = ... GainClamping = yes }`
- 或加 `EMfield{ EMmode{ PhotonEnergy=... ElectricField=... } }`

## 4. 一套可复用的分析顺序（建议背下来）

1. 日志确认收敛
2. Gain_vs_Voltage.dat 找正增益偏置与峰值能量
3. Current_vs_Voltage.dat 看电流量级
4. 在正增益偏置读 Gain_vs_Energy.dat 画谱
5. Populations.txt 判断目标跃迁是否"上多下少"（反转）
6. Dipoles.txt 找大偶极跃迁对，核对 ΔE
7. 若和设计不符，回结构/带阶/偏置迭代

## 相关笔记

- 输入文件怎么写的：[[16-NEGF输入文件逐行讲解]]
- 结果与下一步：[[18-结果解读与实验指导]]
