# 压力测试结果 — gain-preview-workflow

## darwin round3 full_test（2026-08-18）

**测试方式**: ✅ **full_test**（真实工具端到端，非 dry_run）

**测试场景**: 按本 skill E 段流程真跑 .gain 预览：`pics3d.exe inp13.gain`（VCSEL MQW，include inp13.mater，含 gain_wavel/sp.rate_wavel/index_wavel/current_conc）。

**实测数据**:

| 指标 | 结果 | 合理性 |
|---|---|---|
| 运行状态 | exit 0，生成 .gain.msg / jplot*.tmp / tmp.data / MQW 子带文件 | ✅ |
| 增益峰 | **+4805 1/m @ λ=1.291 µm**（jplot01：波长-增益两列） | ✅ 接近设计波长 1.3 µm |
| 透明波长 | **≈1.31 µm**（增益过零处） | ✅ 与 VCSEL 设计一致 |
| 子带信息 | .gain.msg 每载流子密度点报告 Gamma/L/HH/LH 能级数 | ✅ |
| 复合系数 | tmp.data：a/b/c（SRH/辐射/俄歇） | ✅ |

**结论**: E 段工作流（生成骨架 → 运行 gain_wavel/current_conc 等预览语句 → 供 RTG 使用）可端到端执行，输出物理合理（增益峰对齐 1.3 µm 设计、透明密度可读）。dim8 由 dry_run 升级为 full_test，评分 6→8。

**局限**: 未实测 RTG 预览（rtgain_phase）与 .sol include .gain 的完整对接；增益峰/透明密度为数值文件解析结果，未与 CrosslightView 图形逐点核对。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback（sub-agent 不可用），逐条对照 test-prompts.json 预期。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | 增益谱预览场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | 载流子密度决策场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | RTG 表格化增益准备场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | 纯信息查询不触发 |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | 材料宏选择归 material-macros |
| 6 | edge-01 | 边界 | ✅ | 预览结果 vs 主仿真差异需标注 |

**诱饵容错**: 0。
