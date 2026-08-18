# 压力测试结果 — qw-model-selection

## darwin round3 full_test（2026-08-18）

**测试方式**: ✅ **full_test**（真实运行数据复用）

**实测数据**:

| 验证项 | 结果 |
|---|---|
| 子带输出（inp13.gain 真跑） | ✅ .gain.msg 报告 MQW 能级 Gamma=2 / L=5 / HH=4 / LH=1（含 k.p 复杂模型路径） |
| 子带数据文件 | ✅ mqw_profile_set_1_cmplx_1.txt（76 个采样点，波函数/能级数据）随载流子密度扫描逐点输出 |
| 增益峰与模型一致性 | ✅ inp13 增益峰 1.291 µm（1.3 µm 设计），透明密度 ≈1.31 µm |
| 模型等级链条 | ✅ 简单（默认）→ 复杂 MQW → 自洽 → valence_mixing 的分级判断可落地为语句（active_reg/begin_complex/self_consistent/valence_mixing=yes） |

**结论**: 子带/增益输出链路可端到端运行，模型分级决策可落地。dim8 6→8。

**局限**: 未实测 valence_mixing=yes 与 self_consistent 在完整激光器仿真中的计算时间差异（需专门算例）。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback，逐条对照 test-prompts.json。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | 新有源区选模型场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | 增益谱异常场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | 耦合/非对称阱场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | 材料参数定义归 material-macros |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | GaN 极化物理归 gan-wurtzite-mqw |
| 6 | edge-01 | 边界 | ✅ | 体材料无量子限制不适用 |

**诱饵容错**: 0。
