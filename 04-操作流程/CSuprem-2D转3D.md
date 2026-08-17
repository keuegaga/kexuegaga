---
title: CSuprem 2D→3D 转换
type: workflow
product: CSuprem
version: "通用"
status: source
source: "[[99-原始资料/产品手册/csuprem_manual.pdf]] 第3章 §3.3-3.5；[[99-原始资料/教程与问答/CSuprem_3D_tutorial.pdf]]"
last_verified: 2026-08-17
tags:
  - crosslight
  - workflow
  - csuprem
---

# CSuprem 2D→3D 转换

<!-- 例如：把已跑通的 2D CSuprem 工艺/器件输入转成 3D -->

## 目标

把已验证的 2D CSuprem 输入低成本升级为 3D 结构，并（可选）导出给 APSYS 器件仿真。

## 适用版本与环境

| 项 | 值 |
|---|---|
| Crosslight 版本 | CSuprem v2.0/v3.0（本机 C:\Csuprem） |
| 操作系统 | Windows |
| 相关产品 | CSuprem → APSYS |
| 附加软件 | geo3d.exe（zmesh.zst 处理）、SimuCSuprem |

## 前置条件

- [ ] 2D 工艺/器件仿真已跑通（"2D 失败则 3D 必然失败"）
- [ ] 已有 3D 示例的 zmesh.zst 模板可参照
- [ ] 明确各 z 段（zseg_num）的几何分工
- [ ] 项目目录有写权限

## 输入

| 输入项 | 说明 | 示例 |
|---|---|---|
| 2D 主输入 | 已跑通的工艺 deck | `ldd.in` |
| 平面文件 | 每个 xy 平面一份（2D 语法） | `geo1.in`…`geoN.in` |
| zmesh.zst | z 方向定义（固定文件名） | `zmesh.zst` |

## 操作步骤

### 第 1 步：主输入开头加 3D 声明

```text
mode three.dim
3d_mesh nsegm=3 infile=mymesh zstfile=zmesh.zst
```

（先验证阶段把 `three.dim` 换成 `quasi3d`。）

### 第 2 步：准备 xy 平面文件

每个平面一份 `mymeshN.in`，内容与 2D 输入相同：`line → region → bound`（网格/区域/暴露面）。

### 第 3 步：写 zmesh.zst

```text
begin_zst
3d_solution_method 3d_flow=yes
z_structure uniform_zseg_from=0.0 uniform_zseg_to=0.3 && zplanes=1 zseg_num=1
z_structure uniform_zseg_from=0.3 uniform_zseg_to=0.6 && zplanes=1 zseg_num=2
load_mesh mesh_inf=f1.msh zseg_num=1
load_mesh mesh_inf=f2.msh zseg_num=2
output sol_outf=tmp.out
export_3dgeo file=h_cvd.3dgeo
end_zst
```

固定行（`output`/`export_3dgeo`）不要改；taper/bend/cylindrical 按需加在 z_structure 上。

### 第 4 步：etch 命令逐平面加 segm=

```text
etch oxide all segm=1
etch oxide all segm=2
```

淀积/注入只写一次（全平面一致）。

### 第 5 步：quasi3d 验证 → three.dim 收尾

先用 `mode quasi3d` 把所有平面快速跑一遍，修网格/输入问题；全通过后切回 `mode three.dim` 正式计算。

### 第 6 步：（可选）导出并对接 APSYS

```text
export outf=xxx.aps xpsize=0.0001 triangle.based=f repair.mesh=yes
```

.sol 侧：`3d_solution_method 3d_flow=yes` + 复制 z_structure + `load_mesh ... suprem_import=yes`，逐平面 `begin_zmater/end_zmater` 内 `suprem_property`/`suprem_contact` 与 `load_macro`/`contact` 编号一致。

## 预期输出

- 每个平面跑通、quasi3d 全流程无报错；
- `three.dim` 计算完成并生成结构文件（.str）；
- 导出后生成 `.aps`，APSYS 可读取并定义接触/材料。

## 验证方法

- [ ] 各平面独立 2D 仿真通过
- [ ] quasi3d 全平面通过（无崩溃、无网格报错）
- [ ] three.dim 结果与 2D/quasi3d 趋势一致
- [ ] 导出文件能被 APSYS 读取（suprem_import 无报错）

## 常见问题

### 问题 1：etch 没有作用到所有平面

- 原因：漏加 `segm=`（只刻了默认平面）
- 解决：每个刻蚀命令对每个 zseg_num 复制一份
- 详见：[[07-故障排查/常见错误索引]]

### 问题 2：氧化步骤崩溃

- 原因：`zplanes≠1`
- 解决：CSuprem 中 zplanes 恒为 1

### 问题 3：导入 APSYS 后材料/接触错乱

- 原因：suprem_property/load_macro/suprem_contact/contact 编号不一致
- 解决：逐平面核对编号契约

## 相关笔记

[[03-功能模块/CSuprem特殊结构建模]] · [[06-案例/STI结构CSuprem输入]] · [[01-基础概念/项目结构与文件类型]]

## 来源

[[99-原始资料/产品手册/csuprem_manual.pdf]] 第 3 章 §3.3-3.5（PDF P29-31）；[[99-原始资料/教程与问答/CSuprem_3D_tutorial.pdf]] P4-13

验证环境：
