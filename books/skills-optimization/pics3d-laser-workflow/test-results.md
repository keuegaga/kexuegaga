# 压力测试结果 — pics3d-laser-workflow

## darwin round3 full_test（2026-08-18）

**测试方式**: ⚠️ **full_test（部分）** — FP 三步偏置链路真跑通过；VCSEL/RTG 求解因本机环境崩溃未完成。

**实测数据**:

| 验证项 | 结果 |
|---|---|
| FP 三步偏置（gaas10.sol：equilibrium → 电压 auto_finish=current_1 → 电流） | ✅ 多次真跑通过，12 数据集收敛，L-I 阈值 ~2 mA、λ=0.834 µm |
| RTG 配置审查（inp13.sol：voltage → auto_finish=rtgain auto_until=0.9 → solve_rtg=yes + begin_zsol 纵模） | ✅ 与手册 §4.2 一致 |
| inp13.gain（RTG 预览数据源） | ✅ 已实测（增益峰 1.291 µm、透明密度、子带文件） |
| inp13.sol 3D VCSEL 求解 | ❌ 本机 exit 157（direct eigen solver access violation，疑似 3D/许可组件环境问题，非配置问题） |

**结论**: 三步偏置工作流的"FP 变体"端到端实测通过；RTG/solve_rtg 语句与手册一致。VCSEL 求解受本机环境限制未完成，不夸大评分。dim8 6→7（部分 full_test）。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback，逐条对照 test-prompts.json。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | 搭建 PICS3D 激光器项目场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | 阈值附近发散场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | 从示例改造结构场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | 纯理论问答不触发 |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | 光栅设计归 dfb-dbr-grating-design |
| 6 | edge-01 | 边界 | ✅ | 已有工程微调无需重建流程 |

**诱饵容错**: 0。
