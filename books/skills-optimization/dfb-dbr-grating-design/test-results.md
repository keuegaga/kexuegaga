# 压力测试结果 — dfb-dbr-grating-design

## darwin round3 full_test（2026-08-18）

**测试方式**: ⚠️ **full_test（部分）** — 配置审查 + 增益/RTG 数据实测；3D 主仿真受本机环境限制。

**实测数据**:

| 验证项 | 结果 |
|---|---|
| inp13 相移 DFB 配置审查 | ✅ 两个 250 µm section、κ≈2000（κL=1）、第一段末尾 phase_shift=0.5，与手册 §22.2 一致 |
| RTG 序列 | ✅ .sol：voltage → `auto_finish=rtgain auto_until=0.9 auto_within=0.05` → `solve_rtg=yes` + begin_zsol（longitudinal/mode_srch） |
| 增益谱数据（inp13.gain 真跑） | ✅ 增益峰 1.291 µm（1.3 µm 设计）、透明密度 ≈1.31 µm，与光栅参考波长对齐前提成立 |
| 主仿真求解 | ❌ inp13 3D 求解本机崩溃（direct eigen solver access violation，环境限制，配置审查为准） |

**结论**: 光栅参数/相移/RTG 序列设计链路的配置与增益数据验证通过；主仿真受环境限制未完成，不夸大评分。dim8 6→7。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback，逐条对照 test-prompts.json。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | 新建 DFB/DBR 设计场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | 双模/跳模诊断场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | 简化 κ 升级显式光栅场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | FP 无光栅归 pics3d-laser-workflow |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | VCSEL DBR 归 vcsel-modeling |
| 6 | edge-01 | 边界 | ✅ | RTG 谱异常需先查增益/参考波长 |

**诱饵容错**: 0。
