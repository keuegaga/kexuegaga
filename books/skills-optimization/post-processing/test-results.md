# 压力测试结果 — post-processing

## darwin round3 full_test（2026-08-18）

**测试方式**: ✅ **full_test**（真实工具端到端）

**测试场景**: 按本 skill E 段流程对 gaas10 真跑完整后处理：确认数据集 → 运行 .plt → 生成 PS。

**实测数据**:

| 步骤 | 结果 |
|---|---|
| E1 确认数据 | ✅ gaas10.sol.msg / .out_0001-0012 齐全，scanline=1 为 equilibrium |
| E2 编写 .plt | ✅ gaas10.plt（get_data/plot_1d/plot_scan/para_extract/ac_voltage）运行 exit 0 |
| E3 检查输出 | ✅ 生成 jplot/junktmp.ac_* 绘图数据 → psplot（gnuplot）→ **gaas10.ps 52.8KB** 新生成 |

**结论**: 数据集→.plt→GNUPLOT→PS 全链路可端到端执行。dim8 6→8。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback，逐条对照 test-prompts.json。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | L-I/IV 绘图场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | 变量画不出来场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | 跨偏置提取场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | 仿真前预览归 gain-preview-workflow |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | 仿真本身归 pics3d-laser-workflow |
| 6 | edge-01 | 边界 | ✅ | bandgap 技巧只画最后一段 IV |

**诱饵容错**: 0。
