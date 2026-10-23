# 合金散射独立归一化与 NEGF 严格复现结论

日期：2026-10-23

对象：Sun et al., *Optics Express* 30, 37272 (2022), DOI 10.1364/OE.469573

## 1. 结论

`AlloyScatteringStrength=0.06` 可以由独立材料物理得到，不需要用 9 µm 波长或目标增益反推。

但是，使用该独立归一化后，NEGF 仍不能严格复现论文：

| 判据 | NEGF 结果 | 论文/器件约束 | 判定 |
|---|---:|---:|---|
| 9.17 µm 自洽增益峰位 | 10.33 µm | 9.17 µm | 失败 |
| 阈值电流 | 约 2.05 kA/cm² | 1.52 kA/cm² | 失败，偏高约 35% |
| 9.17 µm 是否有正增益 | 是 | 是 | 通过 |
| 标准衬底温度 300 K | 有效电子温度约 1.0×10³ K（阈值附近） | 未直接给出 | 高风险 |
| 子带寿命 | 约 0.09–0.32 ps | 文献 E3/E4 为 2.02/1.27 ps | 明显不一致 |

因此：

> 当前 NEGF 不能作为 Sun 有源区“严格可激射”的独立证明；它只能说明，在独立归一化的散射参数下，9.17 µm 通道有正增益，但绝对阈值和增益峰位仍不吻合。

这不证明论文结构不可用。它证明的是当前模型不足以裁决该结构，不能把 NEGF 的绝对阈值或峰位当成外延定版依据。

## 2. nextnano 合金散射项是什么

每次 NEGF 运行都会输出：

`Input/AlloyScatteringTerm.dat`

其单位为 eV²。Sun 结构中得到的值是：

| 层 | 组分 | alloy term (eV²) | sqrt(term) (eV) |
|---|---|---:|---:|
| In₀.₅₉₃Ga₀.₄₀₇As well | x=0.593 | 5.836815 | 2.415950 |
| Al₀.₆₃₈In₀.₃₆₂As barrier | x=0.638 | 7.337601 | 2.708801 |

官方说明该量由二元端元带阶计算。nextnano³ 文档明确指出：

- 可显式指定 `alloy-disorder-scattering-potential`；
- InGaAs 推荐约 0.6 eV；
- AlGaAs 推荐约 1.0 eV；
- 不指定时由二元端元 CBO 自动计算。

独立 InGaAs/InAlAs 文献给出的合金势范围：

- Matsuoka 等，Jpn. J. Appl. Phys. 29, 2017 (1990)：约 0.7 eV；
- 现代高 In 组分 InGaAs 迁移率分析：随机合金约 0.44 eV，并指出 0.5 eV 是常用预期值；
- 因此本文采用 0.44–0.70 eV 作为独立允许范围。

参考：

- nextnano³ Monte-Carlo 文档中的 `alloy-disorder-scattering-potential` 说明：
  <https://www.nextnano.com/docu/nextnano3/user_guide/input_syntax/keywords/Monte-Carlo.html>
- T. Matsuoka et al., Jpn. J. Appl. Phys. 29, 2017 (1990):
  <https://doi.org/10.1143/JJAP.29.2017>
- E. Diez et al., Appl. Phys. Lett. 88, 052107 (2006):
  <https://doi.org/10.1063/1.2168666>
- 高 In 组分 InGaAs 数字合金迁移率分析：
  <https://arxiv.org/abs/2403.17166>

## 3. 0.06 的由来

`AlloyScatteringStrength` 对合金自能作线性缩放。实际检查也确认散射率严格线性：

| strength 比例 | state 1 alloy rate | 相对强度 |
|---|---:|---:|
| 1.00 | 18.7131 ps⁻¹ | 1.00000 |
| 0.50 | 9.35655 ps⁻¹ | 0.50000 |
| 0.25 | 4.67828 ps⁻¹ | 0.25000 |
| 0.10 | 1.87131 ps⁻¹ | 0.10000 |

如果把 strength 解释为实际合金势平方相对于 nextnano 输入项的缩放，则：

| strength | well 等效势 | barrier 等效势 |
|---:|---:|---:|
| 0.06 | 0.592 eV | 0.664 eV |
| 0.08 | 0.683 eV | 0.766 eV |
| 1.00 | 2.416 eV | 2.709 eV |

`strength=1.0` 对应约 2.4–2.7 eV，远高于独立实验给出的 0.44–0.70 eV。

`strength=0.06` 同时落在 nextnano 自带的 InGaAs 0.6 eV 推荐值和独立文献范围的中间，因此选作物理中心值。0.08 用作范围上界。

仍需向 nextnano 确认：正式 NEGF 代码是否完整保留了旧版 `alloy-disorder-scattering-potential` 的定义，即 `term=dV²`。当前的比值解释与全部独立数值一致，但在未得到厂商书面确认前，不把它提升为“证明级常数”。

## 4. 独立校准后的 NEGF 结果

固定：

- 独立有效质量 0.043/0.089 m0；
- CBO 0.773 eV；
- IFR Δ=0.08 nm，Λ=7 nm；
- alloy strength=0.06；
- 300 K 晶格温度。

在相同 216.384 mV/period 下，物理范围上界 `strength=0.08` 仍给出 9.17 µm 自洽增益
5.77 cm⁻¹、J=2.718 kA/cm²、Te=1547 K；9.17 µm 的正增益在 0.06–0.08 内不是脆弱点。

偏压扫描：

| 偏压 (mV/period) | J (kA/cm²) | Te (K) | 135 meV 自洽增益 (cm⁻¹) |
|---:|---:|---:|---:|
| 140 | 1.121 | 647 | −2.13 |
| 160 | 1.555 | 826 | +0.07 |
| 180 | 1.997 | 1027 | +2.60 |
| 200 | 2.371 | 1261 | +5.15 |
| 220 | 2.631 | 1528 | +7.57 |

用波导模型得到的材料增益阈值 2.966 cm⁻¹ 插值：

- NEGF 阈值偏压约 **182.9 mV/period**；
- NEGF 阈值电流约 **2.05 kA/cm²**；
- 论文为 **1.52 kA/cm²**。

模型阈值比论文高约 35%。在论文的 1.52 kA/cm² 附近，NEGF 的 9.17 µm 增益只有约 0.07 cm⁻¹，远低于约 3 cm⁻¹ 的阈值。

同一批 NEGF 结果还暴露了方法依赖：

| 增益方法 | 9.17 µm 阈值电流 |
|---|---:|
| 自洽线性响应 `GainMethod=self` | 2.05 kA/cm² |
| Fermi golden rule | 1.72 kA/cm² |
| 论文阈值 | 1.52 kA/cm² |

两种 NEGF 增益方法都没有落在论文值附近；自洽结果与 FGR 相差约 19%，因此不能通过选择“更接近论文”的方法来宣称复现。

## 5. 宽能量窗暴露的第二个失败

若只在 120–155 meV 内寻找最大增益，结果会在窗口左边界 120 meV 报最大值，容易误认为 10.33 µm 是“真峰”。

因此重新计算 60–180 meV 全窗：

| 光子能量 (meV) | 波长 (µm) | 自洽材料增益 (cm⁻¹) |
|---:|---:|---:|
| 100 | 12.40 | +2.22 |
| 110 | 11.27 | +7.09 |
| 120 | 10.33 | +9.93 |
| 130 | 9.54 | +8.56 |
| 135 | 9.18 | +6.83 |
| 140 | 8.86 | +4.89 |

宽窗结果确认：

- 真正全局峰位于约 **120 meV / 10.33 µm**；
- 9.17 µm 处于增益下降肩部；
- 10.33 µm 的模态净增益比 9.17 µm 高约 2.3 cm⁻¹。

这无法解释为什么论文器件在 9 µm 而不是 10.3 µm 先激射。

![NEGF 严格复现检查](results/qcl_validation/sun2022_negf_validation.png)

## 6. 对“Sun 原始有源区”的最终可信度定义

### 可以确认

- 层序和周期正确；
- k.p 在 48 kV/cm 下给出 135.26 meV / 9.17 µm；
- E3→E1 偶极矩阵元为 1.287 nm；
- E5−E4 为 65.85 meV，与论文约 66 meV 相符；
- 在物理归一化散射下，9.17 µm 可在较高电流下获得正增益。

### 不能确认

- NEGF 绝对阈值电流；
- NEGF 对 9 µm 与 10.3 µm 的竞争选择；
- NEGF 的子带寿命；
- “Sun 原始结构一定能在实验中独立复现”这一结论。

### 不应当做

- 不依据当前 NEGF 改阱垒追求 9 µm；
- 不依据当前 NEGF 判定 Sun 结构失败；
- 不把 2.05 kA/cm² 当成真实器件阈值；
- 不把“9.17 µm 有正增益”单独当作激射证明。

## 7. 下一步唯一可靠的验证路线

在进入任何 v3 层序修改前，需要完成以下至少一项外部闭环：

1. 向 nextnano 确认当前 NEGF 合金散射项与 `dV²` 的精确关系，以及为何完整校准后仍出现 10.3 µm 主峰；
2. 用第二种量子输运/增益求解器复算同一结构，或取得该结构的实验 EL 线宽、上态寿命和阈值增益数据；
3. 对 NEGF 状态—增益分解逐项核对，确认 120 meV 主峰由哪一个物理跃迁产生，排除基组/能量截断误差；
4. 只有在两种独立方法都给出同一 9 µm 主峰和相符阈值后，才进入实验定版。

## 相关文件

| 内容 | 文件 |
|---|---|
| 合金项解析 | `scripts/analyze_alloy_scattering.py` |
| 0.06 物理中心值输入 | `designs/sun2022_mocvd_9um_alloy006_independent_dv060.negf` |
| 宽窗输入 | `designs/sun2022_mocvd_9um_alloy006_independent_dv060_wide.negf` |
| 偏压扫描输入 | `designs/sun2022_mocvd_9um_alloy006_independent_dv060_biasscan.negf` |
| 自动复核图 | `scripts/plot_sun2022_validation.py` |
| 数值摘要 | `results/qcl_validation/sun2022_negf_validation.txt` |
| 两种增益方法对比 | `results/qcl_validation/sun2022_gain_method_comparison.csv` |

## 相关笔记

- [[41-文献复现-Sun2022-9um-MOCVD-DAU]]
- [[42-QCL物理约束设计原则与实验鲁棒性]]
- [[43-Sun2022-9um-v2实验制造基线]]
- [[44-五级验证闸门-Sun2022态映射增益与波导]]
