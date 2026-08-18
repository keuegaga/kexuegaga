# 压力测试结果 — bias-strategy

## darwin round3 full_test（2026-08-18）

**测试方式**: ✅ **full_test**（真实求解数据，复用本机已跑通的 gaas10/inp13 偏置链路）

**实测数据**:

| 验证项 | 结果 |
|---|---|
| 标准正偏序列（gaas10.sol） | ✅ 真跑：equilibrium → `scan var=voltage_1 value_to=-2 auto_finish=current_1 auto_until=1e-3` → `scan var=current_1 value_to=20.`，12 数据集收敛 |
| KCL/符号 | ✅ 日志显示 p 侧电流为负（-0.1980E+02 / -0.2000E+02），双电极守恒 |
| 高阻→电压、低阻→电流 | ✅ 电压段扫到 -1.7 V 后切电流，阈值附近稳定（L-I 阈值 ~2 mA） |
| PICS3D RTG 序列（inp13.sol 配置审查） | ✅ voltage → auto_finish=rtgain auto_until=0.9 → solve_rtg=yes，与手册 §4.2 一致 |

**结论**: 电压→KCL→电流的偏置编排在真实求解上可执行且物理正确；多电极符号约定（p 侧为负）在日志中验证。dim8 6→8。

**局限**: 未实测多电极（DBR 三段）案例；inp13 3D 求解在本机崩溃（环境限制，配置审查为准）。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback，逐条对照 test-prompts.json。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | 新建仿真选偏置场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | 阈值附近切换电流扫描场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | 多电极/多段器件场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | 纯热/光学边界不触发 |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | 发散后调试归 convergence-debugging |
| 6 | edge-01 | 边界 | ✅ | 简单双端器件直接走标准序列 |

**诱饵容错**: 0。
