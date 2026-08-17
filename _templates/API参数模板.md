---
title: "{{title}}"
type: parameter
product: Crosslight          # LASTIP / APSYS / PICS3D / CSuprem / 通用
parameter: ""               # 参数名，如 bias / temperature / mesh_num
file_type: ""               # 出现在哪个文件中：.sol / .mater / .layer / .geo / 命令行
version: ""
status: draft
source: ""
last_verified: "{{date}}"
tags:
  - crosslight
  - parameter
---

# {{title}}

<!-- 例如：bias 参数（偏置方式） -->

## 含义

<!-- 这个参数控制什么 -->

## 所属文件/位置

<!-- 在哪个配置文件中、GUI 哪个对话框、或命令行哪个选项 -->

## 类型

`string` / `integer` / `float` / `boolean` / `list`（择一）

## 可选值

<!-- 表格列出所有合法值及其含义 -->

| 值 | 含义 | 适用场景 |
|---|---|---|
| `voltage` | 电压偏置 | 常规 IV 扫描 |
| `current` | 电流偏置 | 需要限定电流时 |

## 默认值

<!-- 不设置时使用什么值 -->

## 单位

<!-- 若参数带单位，写明单位，如 K / V / m^-3 -->

## 示例

```yaml
# 示例配置（写真实可用的片段，注明所属文件）
bias: voltage
```

<!-- 或 GUI 操作路径示例 -->

## 约束

> [!warning]
> <!-- 重要：与其他参数的冲突、版本限制、数值范围限制。Codex 生成配置前必须检查此项 -->
> - 不能与 xxx 同时使用
> - 仅 APSYS 支持
> - 取值范围：xxx

## 常见错误

<!-- 该参数设置错误时的典型报错 -->

错误信息示例 → [[07-故障排查/对应错误笔记]]

## 相关参数

- [[bias]]
- [[temperature]]
- [[mesh_num]]

## 版本差异

<!-- 有差异才写，没有则删除本节 -->

| 版本 | 差异说明 |
|---|---|
| 2024 |  |
| 2025 |  |

## 来源

{{source}}
