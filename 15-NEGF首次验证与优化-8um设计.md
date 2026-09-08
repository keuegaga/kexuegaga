# NEGF 首次验证与优化（8 µm 设计）

> 2026-09-08：qcl8um_design_v1.negf 由用户在本地 nextnano.NEGF 运行成功（无报错，收敛正常），输出目录 `C:\Users\ciomp\Documents\nextnano\Output\qcl8um_design_v1(1)`。本文记录诊断结论与 v2 优化方案。

## 1. v1 运行结果（240 / 250 mV/周期，300 K）

| 量 | 240 mV | 250 mV | 判断 |
|---|---|---|---|
| 电流密度 | 118.0 A/cm² | 113.2 A/cm² | 数值合理（偏低，掺杂偏少） |
| 最大增益 | −0.54 cm⁻¹ @190 meV | −0.56 cm⁻¹ @190 meV | **负增益 = 吸收，不出光** |
| 低能端增益 | −120 cm⁻¹ @120 meV | − | 吸收主导 |
| 电子温度 | ~375 K | ~375 K | 300 K 器件偏热，合理 |

![[negf_v1_gain.png]]

## 2. 诊断：为什么没有增益

### 2.1 本征能级里找不到 156 meV 的设计跃迁

NEGF 自洽势场下每周期保留 4 个能级（240 mV）：

```
lev.1 = 2451 meV ─┐
                  ├ 33.5 meV
lev.2 = 2418 meV ─┤
                  ├ 94.8 meV
lev.3 = 2323 meV ─┤
                  ├ 16.4 meV
lev.4 = 2306 meV ─┘
```

偶极矩阵元最大的跃迁是 **lev.1↔lev.2（|z|=4.54 nm）但能量差只有 33.5 meV**（太赫兹波段，不是 8 µm）；155 meV 附近（lev.1↔lev.4，144.7 meV）偶极只有 0.26 nm，太弱。

占据数（240 mV）：lev.4=0.636、lev.3=0.316、lev.2=0.032、lev.1=0.016 —— **能级越低占据越多，上下态完全反了**，即使有合适跃迁也是吸收而非增益。

### 2.2 根因：两套软件导带带阶不一致

直接从界面能带边实测：

| 来源 | CBO（垒-阱导带边差） |
|---|---|
| nextnano++ kp（我们的设计依据） | **0.775–0.788 eV** |
| nextnano.NEGF v1（默认数据库） | **0.62–0.67 eV** |

差约 0.12–0.15 eV。带阶不同 → 量子阱内能级整体移动 → 我们按 nnp 设计调好的 ~156 meV 反交叉在 NEGF 里根本不存在。这是"能带设计"与"输运仿真"脱节的最常见原因。

### 2.3 次要问题

- 掺杂区域不完整：.nnp 设计掺杂在"注入垒+阱"（0–7.4 nm），v1 只写了阱（3.4–7.4 nm）
- 电流 ~115 A/cm² 偏低（中红外 QCL 通常 kA/cm² 量级），暗示掺杂不足

## 3. v2 优化方案（已生成 `designs/qcl8um_design_v2_negf_calibrated.negf`）

| 改动 | v1 | v2 | 目的 |
|---|---|---|---|
| 材料带阶 | 默认数据库 | `well CBO=0.0 / barrier CBO=0.78 eV`（UseConductionBandOffset=yes） | 与 nnp kp 对齐（0.775–0.788 eV） |
| 掺杂 | 3.4–7.4 nm，1e17 | **0–7.4 nm，1e17**（垒+阱） | 与 .nnp 一致，提高注入电流 |
| 偏置扫描 | 240–250 mV | **160–320 mV，步长 20** | 找反交叉/正增益工作点 |
| 光子窗口 | 120–190 meV | **80–200 meV** | 覆盖所有可能跃迁 |
| 轴向能窗 | 300 meV | 350 meV | 保留更多子带 |

## 4. 怎么跑 v2

```powershell
nextnano.NEGF_win.exe --input-file designs\qcl8um_design_v2_negf_calibrated.negf `
  --license-file <你的.lic> --output-folder runs\negf_v2_out `
  --material-database "...\nextnano.NEGF\database\Material_Database.negf" --threads 8
```

预计 ~9 个偏置点 × ~30 s ≈ 5–8 分钟。跑完请把输出目录路径发我，重点看：

1. `Gain_vs_Voltage.dat` —— 哪个偏置出现正增益、峰值能量在哪
2. 正增益点对应的 `EnergyEigenstates\EigenStates.dat` / `Populations.txt` —— 是否出现"上态多、下态少"的反转
3. `Current_vs_Voltage.dat` —— 电流量级与电压特性

## 5. 如果 v2 仍无增益（预案）

- 反向调节带阶敏感性：把 barrier CBO 在 0.72–0.84 eV 之间扫描（±0.05），找 155 meV 反交叉
- 在正增益候选偏置点附近加密扫描（步长 5 mV）
- 检查掺杂敏感度：1e17 → 2e17 / 5e17
- 若全电压都无反转：需要回 nextnano++ 重新核对态配对，考虑微调 W3.2 阱宽（±0.1 nm）重新对齐
- 后续可打开 ElectronElectronScattering=yes（Bismuto 300 K 模板用它）看散射对反转的影响

## 6. 相关笔记

- 设计来源：[[14-QCL-8um设计-Friedrich-InP平台]]
- 能级设计工具：[[13-命令行运行nextnano-与结果验证]]
- 输运物理背景：[[12-进阶-NEGF输运与增益优化]]
