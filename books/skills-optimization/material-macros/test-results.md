# 压力测试结果 — material-macros

## darwin round3 full_test（2026-08-18）

**测试方式**: ✅ **full_test**（真实文件审查 + 真实运行数据复用）

**实测数据**:

| 验证项 | 结果 |
|---|---|
| 真实 .mater 结构（gaas10.mater） | ✅ 审查通过：contact/material_lib/active_reg/begin_complex 结构清晰，`material_lib name=AlGaAs mater=1 && var_symbol1=x var1=0.71` 组分语法正确 |
| .gain include .mater 链路 | ✅ 真跑过 inp13.gain / shuji.gain / gaas10.gain（include shuji.mater/inp13.mater），材料加载成功、增益谱正常输出 |
| 单位核对 | ✅ .mater 中掺杂/厚度单位符合 μm/m^-3 约定 |
| 默认库保护 | ✅ 工作副本未触碰 crosslight.mac/more.mac |

**结论**: 宏选择/单位/加载链路在真实文件与运行上验证通过。dim8 6→8。

**局限**: 未实测 use_macrofile 自定义宏覆盖的端到端（需自建 .mac 案例，后续可补）。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback，逐条对照 test-prompts.json。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | 材料宏选择场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | 自定义宏覆盖场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | 单位换算场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | QW 模型选择归 qw-model-selection |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | GaN 物理归 gan-wurtzite-mqw |
| 6 | edge-01 | 边界 | ✅ | 默认宏库参数微调需谨慎 |

**诱饵容错**: 0。
