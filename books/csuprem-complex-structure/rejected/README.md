# 被淘汰的候选单元（阶段 1.5 审计）

> 淘汰不是"错"，而是"不独立成 skill"：要么并入核心单元，要么作为证据保留。

## 并入核心单元的候选

| id | 标题 | 去向 |
|---|---|---|
| f10 | tag 句柄化 | 并入 U1 |
| p02 | 先 quasi3d 再 three.dim | 并入 U3 |
| p03 | 淀积/注入全平面一致 | 并入 U4 |
| p01 | 2D 失败则 3D 必然失败 | 并入 U5 |
| p05 | 编号一致性契约 | 并入 U8 |
| p07 | 导出前 repair.mesh | 并入 U8 |
| p04 | zplanes=1 防崩溃 | U3 判停条件 |
| p06 | 不修改 zmesh.zst 固定行 | U8 清单项 |
| p08 | 2D→3D 机械步骤清单 | U3 的 E 段 |
| p09 | avoidmask 必须先有 mask | U7 的 E 段 |
| p10 | 规则分层器件不必用 CSuprem | B 段边界原则 |

## 因重复/过细而合并的反例

以下 counter-examples 条目内容与核心反例重叠或过于具体（单语句级），合并进 verified.md 的反例池：

- 所有"语句参数误用"类（如 ram 单位、流量↔分压换算、ion vs impurity、henry.coeff/theta 乱改）→ 保留在 candidates/counter-examples.md 供查询，不进 skill B 段
- 纯 GUI/环境类（movie 时间步、GUI 异常、suprem.key 修改）→ 保留供查询

## V3 独特性不足的候选

| id | 标题 | 原因 |
|---|---|---|
| f09 | 对称结构镜像复用 | "对称只建一半"接近通用工程常识；保留为 U3/U8 的一个示例动作而非独立框架 |
| g01-g12 | 术语词典 | 术语不独立成 skill，直接整理为 GLOSSARY.md |
