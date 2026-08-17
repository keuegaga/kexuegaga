---
title: CrosslightView
type: function
product: Crosslight
version: 2024
status: source
source: "[[99-原始资料/GUI与工具/CrosslightviewDoc.pdf]]；[[99-原始资料/教程与问答/Common_QAs.pdf]]；[[99-原始资料/专题/培训总结.pdf]]"
last_verified: 2026-08-17
---

# CrosslightView

## 功能用途

3D 彩色图形结果查看器，用于查看仿真结果（能带、载流子、电场、光场、IV/L-I 曲线等）。可从 SimuCenter 右键 `.std` 文件启动，或从开始菜单独立启动；无需额外绘图软件。

## 打开文件

File → Open File 支持四种类型（CrosslightviewDoc）：`*.std`、`*.plt`、`*.str`、`*.dat`。

- `.std`：求解器结果（主数据文件）；
- `.plt`：按绘图结果查看；
- `.dat`：两列 XY 数据（格式不合法会报错）；
- `.str`：文档列出可打开，但示例目录与手册第 3 章未出现，本库视为旧格式数据文件（用途未验证）。

## 查看两类数据

- `xy_data`：结构/位置相关数据（能带、载流子浓度、迁移率、电场等），用顶部 `material_num` 菜单切换；
- `scan_data`：扫描变量相关数据（电流、电压、光功率、时间等），View → Scan Bias Data 从 `.std` 导入；
- 光场：`wave_intensity_allmode` 看多模叠加，`wave_intensity` 看单一模式，Tools 下拉选择模式数；
- 温度场：`lattice_temp` 按钮查看器件温度分布。

## 相关链接

[[05-API与命令/std文件|.std 文件]] · [[05-API与命令/plt文件|.plt 文件]] · [[01-基础概念/项目结构与文件类型]]
