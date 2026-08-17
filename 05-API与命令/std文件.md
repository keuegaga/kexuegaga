---
title: .std 文件
type: concept
product: Crosslight
version: 2024
status: source
source: "[[99-原始资料/通用手册/manual.pdf]] 第3章；[[99-原始资料/教程与问答/Workbook03.pdf]]；[[99-原始资料/教程与问答/Common_QAs.pdf]]"
last_verified: 2026-08-17
---

# .std 文件（结果数据）

## 这是什么

求解器输出的数值结果文件，带数值后缀（`.std_0001`、`.std_0002`…），是 CrosslightView 的输入；`.plt` 绘图通常读取同信息的 `.out_#` 文件。仿真正常结束的标志是生成 `*.std` 文件（Workbook03）。

## 数据集与偏置的对应

- 每个 `.std_#` 对应一个数据集；数据集编号由 `equilibrium`（第 1 个 scanline）与各 `scan` 的 `print_step` 决定；
- 想查某个输出文件对应的偏置：打开 `xxx.sol.msg`（Common_QAs Q4），或在 `xxx.log` 中 Ctrl+F 搜 `std`；
- `.plt` 中用 `get_data ... xy_data=(n1 n2) / scan_data=(n1 n2)` 引用。

## 使用方式

- SimuCenter 右键 `.std` → CrosslightView（或菜单 Action → View Results → CrosslightView）；
- 独立启动 CrosslightView → File → Open File 选择 `.std`；
- 仿真运行中可查看已生成的 `std01/std02`，但当前正在写的 `std03` 不能打开（培训总结技巧）。

## 相关链接

[[03-功能模块/CrosslightView]] · [[05-API与命令/plt文件|.plt 文件]] · [[05-API与命令/sol文件|.sol 文件]]
