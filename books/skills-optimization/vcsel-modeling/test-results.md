# 压力测试结果 — vcsel-modeling

## darwin round3 full_test（2026-08-18）

**测试方式**: ⚠️ **full_test（部分）** — 配置审查 + 增益数据实测；3D 主仿真受本机环境限制。

**实测数据**:

| 验证项 | 结果 |
|---|---|
| inp13 VCSEL 配置审查 | ✅ .sol：3d_solution_method 3d_flow=yes + z_structure（zplanes=1）+ begin_zmater include inp13.gain/.doping；begin_zsol（longitudinal ref_wavel=1.3e-6 / mode_srch omega_xrange=20） |
| RTG 初始化序列 | ✅ equilibrium → rtgain_phase density=1.25e24 → voltage（auto_finish=current_1）→ current（auto_finish=rtgain auto_until=0.9）→ solve_rtg=yes |
| 增益数据（inp13.gain 真跑） | ✅ 增益峰 1.291 µm、透明密度 ≈1.31 µm（1.3 µm 设计），驻波增强评估的前提成立 |
| 主仿真求解 | ❌ inp13 3D 求解本机崩溃（direct eigen solver access violation，环境限制，配置审查为准） |

**结论**: VCSEL 腔定义（z_structure/begin_zsol/rtgain_phase）与低阈值 RTG 初始化序列的配置审查通过；主仿真受环境限制未完成，不夸大评分。dim8 6→7。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback，逐条对照 test-prompts.json。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | 新建 VCSEL 仿真场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | RTG 纵模偏离场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | 驻波增强评估场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | 边缘发射 DFB/DBR 归 dfb-dbr-grating-design |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | 通用三步偏置归 pics3d-laser-workflow |
| 6 | edge-01 | 边界 | ✅ | GaN VCSEL 需叠加 gan-wurtzite-mqw |

**诱饵容错**: 0。
