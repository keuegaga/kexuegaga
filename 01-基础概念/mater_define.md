---
title: mater_define
type: concept
product: Crosslight
version: 2024
status: source
source: "[[99-原始资料/通用手册/manual.pdf]] §3.5、附录B；C:\crosslig\lastip_examples\A_tutorial\1D_laser\gaas10.mater；[[99-原始资料/专题/培训总结.pdf]] §1①"
last_verified: 2026-08-17
---

# mater_define（材料参数定义）

## 这是什么

材料参数定义文件。官方扩展名是 `.mater`（2024 版手册全文无 `.mtrl`），通常由处理 `.layer` 自动生成，也可以手写或编辑后由 `.sol`/`.gain` 用 `include file=xxx.mater` 引入。

## 文件内容结构（来自真实示例 gaas10.mater）

- `contact num=1 type=ohmic`：接触定义
- `material_lib name=AlGaAs mater=1 && var_symbol1=x var1=0.71`：材料库引用与组分变量（旧版手册语法为 `load_macro`）
- `mater_var` / `grade_active_mater`：组分/参数渐变
- `active_reg mater=3 thickness=...`：有源区标注
- `begin_complex ... end_complex`：复杂 MQW 区域

## 最小 .mater 示例

```text
contact num=1 type=ohmic
contact num=2 type=ohmic
material_lib name=AlGaAs mater=1 && var_symbol1=x var1=0.71
```

## 单位与纪律

- 单位：长度 µm、能带 eV、掺杂 m^-3、迁移率 m²/(V·s)；cm^-3 需换算成 m^-3
- 不改默认宏库（crosslight.mac/more.mac）；自定义用 `use_macrofile` 或 `load_macro` 后重发语句覆盖（后发覆盖先发）

## 相关链接

[[05-API与命令/核心参数]] · [[01-基础概念/项目结构与文件类型]] · [[07-故障排查/材料参数错误]]
