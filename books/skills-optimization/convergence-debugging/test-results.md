# 压力测试结果 — convergence-debugging

## darwin round3 full_test（2026-08-18）

**测试方式**: ✅ **full_test**（真实工具端到端，非 dry_run）

**测试场景**: gaas10 1D 量子阱激光器全流程求解，按本 skill E 段演示"分级定位"与"验证"两步：读取 .log 误差表判断收敛、对比关键输出。

**实测数据**:

| 步骤 | 演示内容 | 结果 |
|---|---|---|
| E1 分级定位 | 读取 `Error report for equations and variables: it# eqns potential elec hole other` 误差表 | ✅ 每步误差单调下降：eqns 1.08e-3 → 2.8e-5 → 2.08e-12（收敛到机器精度） |
| E2 按排查树修复 | 收敛案例无需修复（定位即确认无数值问题） | ✅ 12 数据集全部收敛 |
| E3 验证无污染 | 最终数据集 light=9.141 mW | ✅ 与历次基线一致（9.141 mW），输出可复现 |

**结论**: E 段"读误差表定位 → 判定收敛 → 验证输出"链路可端到端执行；误差表列（eqns/potential/elec/hole/other）是收敛判定的直接依据。dim8 由 dry_run 升级为 full_test，评分 6→8。

**局限**: 本次为收敛案例，未实测"诱导发散 → 排查树修复"的失败路径（低阻区/偏置/RTG 等修复分支依赖真实失败案例，后续可用刻意坏参数复现）。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback（sub-agent 不可用），逐条对照 test-prompts.json 预期。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | 不收敛诊断场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | 宽禁带低偏场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | KCL 不守恒场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | 流程搭建归 pics3d-laser-workflow |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | 纯网格问题归 mesh-quality |
| 6 | edge-01 | 边界 | ✅ | 收敛但结果物理错误 → 模型问题非数值问题 |

**诱饵容错**: 0。
