---
title: GeoEditor
type: function
product: Crosslight
version: 2024
status: source
source: "[[99-原始资料/GUI与工具/GeoEditorDoc.pdf]]（版本 1.60，2002）"
last_verified: 2026-08-17
---

# GeoEditor

## 功能用途

2D 图形化绘图软件，直接创建/修改 `.geo` 文件，供 LASTIP / PICS3D / APSYS / Procom 使用。当器件结构不是规整的层/列布局（如非平面、不规则形状）时，用它替代 LayerBuilder。

## 基本概念

- polygon 是结构的基本组成块，只能是三角形或四边形；所有结构必须细分为角点互连的三角形/四边形；
- 错误画法：一个 polygon 的角点落在相邻 polygon 的边上（不共享角点）；
- 收敛性：优先四边形/矩形，避免两相邻角同时大于 90°；
- 坐标：X 向右、Y 向上。

## 使用流程

1. 工具栏选 [Rectangle]（或 Triangle/Polygon），按顺序点击角点；
2. 属性对话框设置尺寸（Height/Width）；
3. [Mater Info] 选择材料宏并设置组分（如 AlGaAs，X=0.3）；
4. 设置掺杂、接触；
5. 生成网格并保存 `.geo`。

## 参考示例（GeoEditorDoc 第 7.5 节）

简单量子阱激光器（LASTIP）、多模仿真、2D 脊波导激光器、埋沟异质结构（BH）激光器、衬底辐射。

## 相关链接

[[01-基础概念/项目结构与文件类型]] · [[01-基础概念/Layer3d]] · [[07-故障排查/网格划分误差]]
