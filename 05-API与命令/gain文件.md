---
title: .gain 文件
type: concept
product: Crosslight
version: 2024
status: source
source: "[[99-原始资料/通用手册/manual.pdf]]（gain_wavel）；[[99-原始资料/教程与问答/Workbook03.pdf]]；C:\crosslig\lastip_examples\A_tutorial\1D_laser\gaas10.gain；[[99-原始资料/专题/培训总结.pdf]] §1②"
last_verified: 2026-08-17
---

# .gain 文件（增益谱预览）

## 这是什么

正式仿真前预览材料增益谱、自发辐射谱、折射率变化、电流-载流子关系的输入文件（LASTIP/PICS3D 共用）。由用户生成（无 `.gain` 时可右键 `.mater` 生成模板），独立运行，不需要先跑 `.sol`。

## 语句骨架（来自真实示例 gaas10.gain）

```text
begin_gain
plot_data plot_device=postscript
get_active_layer name=AlGaAs/AlGaAs var1=0. var2=0.33 && mater=2 var_symbol1=xw var_symbol2=xb
active_reg type=macro thickness=0.0076 mater=2
gain_wavel wavel_range=(0.7 0.9) && conc_range=(5.e23 5.e24) curve_number=5
gain_density wavel_range=(0.8 0.85) && conc_range=(5.e23 5.e24) data_point=20
end_gain
```

## 常用语句（inp13.gain 补充）

- `temperature temp= 0.3000E+03`：温度
- `include file=xxx.mater`：引入材料参数
- `gain_wavel` / `sp.rate_wavel` / `index_wavel`：增益谱 / 自发辐射谱 / 折射率谱
- `current_conc conc_range=... data_point=30 use_macro=yes fit_outfile=tmp.data`：电流-载流子关系

## 使用流程

1. 生成模板：无 `.gain` 时右键 `.mater` → 生成 gain 模板；
2. 编辑范围：`wavel_range` 覆盖目标波长，`conc_range` 覆盖目标载流子密度；
3. 运行：右键 `.gain` → Process Gain（快捷键 Alt+P），或命令行 `pics3d.exe xxx.gain`；
4. 检查：目标波长处增益为正、透明载流子密度合理（gaas10 约 1.7e18 cm⁻³）。

## 排查

- 增益峰与目标波长差 >50 nm：查量子阱材料/组分/厚度/温度、`exch_coef`（库仑能带收缩）、`tau_scat`（增益谱展宽）（培训总结 §1②）；
- 增益为负：载流子密度不足或波长偏离增益峰。

## 相关链接

[[05-API与命令/核心参数]]（gain_wavel）· [[01-基础概念/mater_define]] · [[06-案例/最小可运行案例]]
