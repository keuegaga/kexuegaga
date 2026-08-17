---
title: Layer3d
type: function
product: Crosslight
version: 2024
status: source
source: "[[99-原始资料/GUI与工具/Layer3dDoc.pdf]]（版本 1.56）"
last_verified: 2026-08-17
---

# Layer3d

## 功能用途

构建 3D 仿真 `.layer` 文件的程序。在 LayerBuilder 的 2D `.layer` 能力之上增加 3D 器件与仿真属性；读取 `.sol` 中的 3D 结构信息，每个 z 平面记录在对应的 `.layer` 文件中。

## 工作方式

- 两个视图区：2D-view（当前 z-segment 的 xy 平面层结构）+ 3D-view（整个器件）；
- z-segment：沿 z 方向分段，每段有 From/To 坐标、`zplanes`（z 向网格数，仅 `3d_solution_method=3d_flow` 时有效）、taper 线设置；
- 菜单/图标：新建/删除/切换 z-segment；平行/透视视图。

## 参考示例（Layer3dDoc 第 5 节）

`crosslig\apsys_examples\3d_flow\taper_3f_a`（含新建 z-segment、列/层构建流程）。

## 相关链接

[[01-基础概念/GeoEditor]] · [[01-基础概念/项目结构与文件类型]] · [[03-功能模块/VCSEL仿真配置]]
