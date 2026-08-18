# 压力测试结果 — gan-wurtzite-mqw

## darwin round3 full_test（2026-08-18）

**测试方式**: ✅ **full_test**（真实工具端到端，非 dry_run）

**测试场景**: 按本 skill E 段流程真跑 GaN 蓝光激光器增益预览：`pics3d.exe shuji.gain`（`C:\crosslig\pics3d_examples\blue_LD`，InGaN QW，含 gain_wavel/sp.rate_wavel/index_wavel/current_conc，波长范围 0.43–0.45 µm）。

**实测数据**:

| 指标 | 结果 | 合理性 |
|---|---|---|
| 运行状态 | exit 0，生成 .gain.msg / jplot*.tmp / tmp.data / MQW 子带文件 | ✅ |
| 增益峰 | **0.43 µm（蓝光）**，随载流子密度 1e24→5e25 m⁻³ 由负转正（-8.7 → +6.7 1/m） | ✅ 与 blue_LD 示例一致 |
| 透明密度 | 增益过零约 **1.7e25 m⁻³（≈1.7e19 cm⁻³）** | ✅ InGaN 蓝光量级合理 |
| 子带信息 | .gain.msg：Gamma/HH/LH 能级，**CH=0（纤锌矿特征）** | ✅ 与 wurtzite 预期一致 |
| 复合系数 | tmp.data：a=2.8e9、b=4.6e-16、c=-4.2e-42（c 为负，拟合点注意） | ⚠️ 高密度拟合伪影，如实记录 |

**结论**: E 段工作流（基晶格核对 → 极化/自洽设置 → .gain 验证）端到端可执行；蓝光增益峰与透明密度物理合理，纤锌矿能级特征（CH=0）正确出现。dim8 由 dry_run 升级为 full_test，评分 6→8。

**局限**: 本示例为增益预览；未实测 self_consistent/independent_mqw/q_transport 在完整激光器仿真中的设置路径（依赖完整 blue_LD 主仿真，后续可补）。

## 原有记录（cangjie 阶段 4，2026-08-14）

**方式**: 主流程自测 fallback（sub-agent 不可用），逐条对照 test-prompts.json 预期。

**通过率**: 100%（6/6）

| # | id | 类型 | 结果 | 备注 |
|---|---|---|---|---|
| 1 | should-trigger-01 | 应触发 | ✅ | GaN 激光器建模场景激活 |
| 2 | should-trigger-02 | 应触发 | ✅ | 波长偏差诊断场景激活 |
| 3 | should-trigger-03 | 应触发 | ✅ | 开启电压虚高场景激活 |
| 4 | should-not-trigger-01 | 诱饵 | ✅ 不触发 | 闪锌矿器件归 qw-model-selection |
| 5 | should-not-trigger-02 | 跨 skill 诱饵 | ✅ 不触发 | 材料宏定义归 material-macros |
| 6 | edge-01 | 边界 | ✅ | 非极性晶面场景需单独处理 |

**诱饵容错**: 0。
