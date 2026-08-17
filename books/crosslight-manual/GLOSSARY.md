# GLOSSARY — Crosslight 通用手册共享术语词典

> 所有 skill 共用的术语基准（整理自 candidates/glossary.md，22 条核心术语）。
> 作者用法 ≠ 字典/常识用法，使用前先核对。

## 一、PICS3D 激光仿真核心

| 术语 | 作者的用法 | 和常识的差异 |
|---|---|---|
| RTG（往返增益） | 复值往返增益，纵模 = Wronskian 零点（RTG=1 极限）；阈值下 RTG<1，≥1 无物理意义 | ≠ 单程/材料增益；含相位匹配 |
| kappa（耦合系数） | 光栅把前向波耦合到后向波的复强度：实部=折射率耦合，虚部=增益/损耗耦合 | ≠ 介电常数；无量纲强度常用 κL |
| section / segment | section 定义光学腔（begin_zsol），segment 定义 3D 电学体积（z_structure） | ≠ 同义词；多段器件一一对应 |
| auto_finish | 扫描按物理条件（电流/RTG）提前终止；PICS3D 开启光子耦合前的强制步骤 | ≠ 普通扫描终点 |
| solve_rtg | 在扫描中开启光子密度耦合求解，必须小步长 | ≠ 默认求解；阈值前后的分水岭 |
| LSHB（纵向空间烧孔） | 纵向光子分布不均→增益/折射率纵向不均→RTG 与光子密度互锁 | ≠ 一般空间烧孔；三步偏置的物理根源 |
| mode_srch | 定义纵向模式搜索窗口（wavel_xrange/omega_xrange、adjust_range） | ≠ 模式求解器；搜索对象是 RTG 零点 |
| begin_zsol | 纵向模式会话块（longitudinal/section/mode_srch） | 与 begin 块的 z_structure 电学段区分 |

## 二、材料与输入体系

| 术语 | 作者的用法 | 和常识的差异 |
|---|---|---|
| 宏（macro） | 一组材料参数语句的集合；小写被动宏（load_macro）+ 混合大小写主动宏（get_active_layer），cx- 为复杂 MQW 宏 | ≠ 编程宏；有源区必须双宏 |
| 基晶格（base lattice） | 应变计算的参考晶格，缓冲层可能弛豫，未必等于衬底；默认 GaN | ≠ 衬底晶格 |
| material number | .geo 中给每个多边形分配的材料编号，绝缘宏编号应大于半导体 | 与宏名称通过 .mater 关联 |
| use_macrofile | 加载自定义宏文件（放输入文件同目录）的语句 | 默认宏库之外的安全扩展途径 |
| basic variables | 默认求解变量=势+准费米能级；可切换为载流子浓度（change_variable） | 不是固定不变的 |

## 三、量子阱与 GaN 物理

| 术语 | 作者的用法 | 和常识的差异 |
|---|---|---|
| valence_mixing | 用 k.p 全解非抛物线价带子带（反交叉、负质量区） | ≠ 默认抛物线近似；慢但准 |
| self_consistent | Schrödinger 与 Poisson 迭代自洽求解（强场/极化必选） | ≠ 平带假设 |
| independent_mqw | 每阱独立材料号逐阱求解（极化 MQW 各阱场不同） | ≠ 默认共享材料号只算一次 |
| set_polarization | 按 InGaN/AlGaN 组分自动生成自发+压电极化界面电荷 | ≠ 手工 interface 电荷 |
| QCSE | 极化局域场分离载流子、改变波函数与增益的量子限制斯塔克效应 | 不加 self_consistent 就看不到 |

## 四、波导与模式

| 术语 | 作者的用法 | 和常识的差异 |
|---|---|---|
| EIM（有效折射率法） | 求横向/侧向模式与复模折射率，是 RTG 中 k(z) 的来源；VCSEL 用 fiber-like EIM | ≠ 纵向模式求解 |
| PML（完美匹配层） | 复坐标拉伸的吸收边界，截断尺寸不足会失真 | ≠ 普通吸收边界 |
| 参考波长 vs 布拉格波长 | λ_ref 由固定参考折射率定义（与偏置无关）；λ_Br=2·n_eff·L_g 随偏置变化 | 两者不同，别混用 |

## 五、数据与收敛

| 术语 | 作者的用法 | 和常识的差异 |
|---|---|---|
| scan_data / xy_data | 偏置相关数据（逐点累积）与结构/光谱数据（按 print_step 打印） | ≠ 横轴纵轴之分 |
| 数据集编号 | .out_#### 按打印请求编号，_0001 为 equilibrium，可在 .sol.msg 查偏置 | ≠ 偏置步编号 |
| slow transient | 电压随时间缓升的收敛技巧（利用位移电流），不是真实瞬态仿真 | ≠ 瞬态仿真 |
| bandgap_reduction | 临时缩小带隙跑出目标电流再恢复的收敛技巧；被改写的 IV 段不可用 | ≠ 物理带隙 |

---

完整候选与出处见 [candidates/glossary.md](./candidates/glossary.md)。
