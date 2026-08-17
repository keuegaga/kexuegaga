---
title: .plt 文件
type: concept
product: Crosslight
version: 2024
status: source
source: "C:\crosslig\lastip_examples\A_tutorial\1D_laser\gaas10.plt；[[99-原始资料/通用手册/manual.pdf]] 第3章；[[99-原始资料/专题/培训总结.pdf]]"
last_verified: 2026-08-17
---

# .plt 文件（绘图设置）

## 这是什么

后处理绘图输入文件：描述如何读取结果（数据集）并绘制曲线/图形。由 GUI 或用户生成，运行时调用 GNUPLOT 输出 Postscript/PDF，也可配合 CrosslightView。

## 结构（来自真实示例 gaas10.plt）

```text
begin_pstprc
plot_data plot_device=postscript
get_data main_input=gaas10.sol sol_inf=gaas10.out && xy_data=(1 1)
plot_1d variable=wave_intensity from=(0.5 0.0) to=(0.5 3.0)
plot_1d variable=band from=(0.5 1.3) to=(0.5 1.7)
get_data main_input=gaas10.sol sol_inf=gaas10.out && scan_data=(1 12)
plot_scan scan_var=voltage_1 variable=current_1 scan_num=2
para_extract type=fit_line fit_vert_from=1 && hori_intercept=8.
plot_scan scan_var=laser_current_1 variable=laser_power scan_num=2
modify_plot show_data_points=yes
ac_voltage log_freq1=6. log_freq2=10.3 && contact_num=1 freq_point=40
plot_ac_laser
plot_ac_curr variable=capacitance_1
end_pstprc
```

## 关键语句速查

| 语句 | 作用 |
|---|---|
| `get_data ... xy_data=(n1 n2)` | 指定结构数据集范围 |
| `get_data ... scan_data=(n1 n2)` | 指定扫描数据集范围 |
| `plot_1d variable=... from=(x y) to=(x y)` | 一维空间分布（能带/光场等） |
| `plot_scan scan_var=... variable=...` | 扫描曲线（IV/L-I 等） |
| `para_extract type=fit_line` | 拟合提取 U0/Rs/Ith/ηslope |
| `modify_plot` | 图形修饰（数据点等） |
| `ac_voltage` / `plot_ac_*` | 交流分析绘图（C-V、AM 响应等） |

## 常见错误

找不到 `xxx.ps`、曲线缺失、数据集超范围、`merge_next=no` 遗漏 → 见 [[07-故障排查/plt运行报错]]。

## 相关链接

[[05-API与命令/std文件|.std 文件]] · [[05-API与命令/命令索引]] · [[07-故障排查/plt运行报错]]
