---
title: PICS3D 中断续算（restart）
type: workflow
product: PICS3D
version: 2024
status: source
source: "[[99-原始资料/通用手册/manual.pdf]] ch23.649（P1117-1119）"
last_verified: 2026-09-09
tags:
  - crosslight
  - workflow
  - pics3d
  - restart
---

# PICS3D 中断续算（restart）

## 目标

求解被中断（进程被杀、终端关闭、断电、崩溃）后，从**已保存的最后一个数据集**继续计算，避免整段重跑。

## 适用前提

- 中断前已有**完整落盘的数据集**（`.std_#` / `.out_#`）；
- **两次运行之间没有改动网格/结构**（改网格会让旧数据无法载入，不能续算）；
- 需要改动的只是继续跑的扫描目标/步长/Newton 参数等（允许）。

## 步骤

### 1. 确认已保存到第几个数据集

打开 `xxx.sol.msg` 查数据集编号与对应偏置（equilibrium 为 1；每个 scan 按 `print_step` 递增）：

```powershell
Select-String -Path xxx.sol.msg -Pattern 'Data set|Current:|Voltage:' | Select-Object -Last 12
```

### 2. 确认没有改动网格

续算前**不要重新生成 .geo/.msh**（不要跑 layer/geo）；只改 `.sol` 文本。

### 3. 在 .sol 中加入 restart

```text
restart data_set=4
```

表示从第 4 个数据集续算（超出可用数时自动用最高可用数据集）。可选加 `stop_at_data_set=10`：续算到第 10 个数据集后自动停，适合分段检查。

### 4. 重新运行

```powershell
C:\crosslig\pics3d\pics3d.exe xxx.sol > xxx.log
```

### 5. 验证

- 日志出现从第 4 个数据集继续的求解过程；
- 新生成的数据集编号从 5 递增（`.std_0005` 出现且时间戳推进）；
- 对照 `.sol.msg` 确认续算起点偏置与中断点一致。

## 约束

- **网格/结构不能变**（manual 原文：改动会让"载入之前仿真数据"失效的参数不允许，如改 mesh）；
- 中断发生在某个数据集**内部**（Newton 步未完成）时，从**上一个完整落盘的数据集**续，不从半成品续；
- `data_set` 超过已有数据集数 → 自动用最高可用（先核对 `.sol.msg` 别弄错起点）。

## 判断"是否中断"还是"已跑完"

- 进程不存在 ≠ 一定中断：先看日志末尾。若最后数据集停在某 scan 的 `value_to` 目标且出现 `Completed .std file`、无错误 → 正常跑完；
- 若日志在中途偏置点戛然而止且进程消失 → 中断，按上述续算。

## 相关笔记

[[05-API与命令/核心参数]]（restart/scan）· [[05-API与命令/std文件|.std 文件]] · [[06-案例/最小可运行案例]]

## 来源与实测说明

[[99-原始资料/通用手册/manual.pdf]] ch23.649 restart（P1117-1119）；nakamura_light 轻量版实测：首次运行 15:26→18:46 生成 4 个数据集并正常结束（非中断），未触发 restart；如需实测可在中断场景按上述步骤执行。
