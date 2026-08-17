---
title: Crosslight 知识库总览
type: index
product: Crosslight
version: 2024
status: source
source: -
last_verified: 2026-08-17
---
# Crosslight 知识库总览

## 这是什么

Crosslight 器件仿真软件（LASTIP / APSYS / PICS3D / CSuprem）
的使用知识库。服务于人工查阅与 Codex 辅助生成配置、排错。

## 核心产品

| 产品 | 用途 | 关键词 |
|---|---|---|
| LASTIP | 边发射激光器仿真 | in-plane laser, gain, waveguide |
| APSYS | 通用器件/LED/OLED 仿真 | LED, RC-LED, ray tracing |
| PICS3D | 3D 仿真 / VCSEL | 3D, vertical-cavity laser |
| CSuprem | 工艺仿真（复杂结构建模） | process, doping, diffusion，详见 [[03-功能模块/CSuprem特殊结构建模]] |
| LayerBuilder/Layer3d/GeoEditor | 结构/网格构建 | .str, .geo, mesh |
| CrosslightView | 结果可视化 | .std, .plt, .str, .dat |

## 资料优先级（Codex 必须遵守）

1. `status: verified` 的实践笔记
2. 对应版本的官方文档（`99-原始资料/00-索引.md` 可查）
3. 官方示例（Workbook03）
4. 未验证的个人记录（必须标注）

## 核心工作流（详见 [[04-操作流程/标准工作流]]）

定义结构 → 生成网格 → 设置材料 → 设定仿真 → 运行 → 分析结果

## 关键文件类型（详见 [[01-基础概念/项目结构与文件类型]]）

`.layer`(结构) `.geo`(几何) `.mater`(材料) `.sol`(求解设置)
`.plt`(绘图) `.std`(结果) `.dat`(XY数据)

## 常用入口

- [[01-基础概念/核心概念]]
- [[02-安装与配置/安装]]
- [[06-案例/最小可运行案例]]
- [[07-故障排查/常见错误索引]]

## 使用规则

- 回答前先确认 Crosslight 版本；
- 不同版本参数不得混用；
- 不确定的内容必须标注"未验证"；
- 生成配置前先检查参数约束；
- 失败时必须收集完整错误日志；
- 不得编造命令、参数或输出。
