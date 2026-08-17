---
title: plt 运行报错
type: error
product: Crosslight
version: 2024
status: draft
source: "[[99-原始资料/专题/培训总结.pdf]] §3③；[[99-原始资料/教程与问答/Common_QAs.pdf]]（Output Data Organization）"
---

# plt 运行报错

## 错误信息

- 运行 plt 后找不到 `xxx.ps`，输出目录里只有 `output.ps`
- 部分图像缺失或曲线不对

## 可能原因

- 导入/导出文件名不匹配
- `scan_data` 数据集编号超出 `.std` 文件数
- 一维/二维空间作图 xy 坐标超出实际器件尺寸
- `plot_1d` 与 `lplot_xy` 用错场合
- 曲线合并未在最后一个 `plot_scan` 设 `merge_next=no`

## 排查顺序

1. 打开 `output.ps`，找出缺失图像，定位对应画图语句。
2. 核对数据集编号：equilibrium 默认第 1 scanline、数据集 (1,1)；后续每个 scan 按 `print_step` 生成数据集，编号见 `.sol.msg`（Common_QAs）。
3. 用 Wizard 逐条检查有问题的语句。
4. 仍不行就从例子库复制对应 plt 语句修改。

## 解决方法

- 修正文件名、数据集范围（`xy_data=[n1 n2] scan_data=[n1 n2]`）、坐标范围
- `plot_scan` 合并时最后一条加 `merge_next=no`
- 画扫描曲线时变量名必须与 `.sol` 中 `scan var=` 一致（Common_QAs Q3）

## 需收集的信息

- plt 文件、output.ps、`.sol.msg`、报错文本

## 相关链接

[[05-API与命令/std文件|.std 文件]] · [[05-API与命令/plt文件|.plt 文件]]
