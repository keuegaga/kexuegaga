# QCL-nextnano 知识仓库

> 量子级联激光器（Quantum Cascade Laser, QCL）设计与 nextnano 仿真学习笔记。
> 内容基于 nextnano 官方文档与本地安装（2025_08_21 版）的示例文件整理。

## 这个仓库是什么

一个 **Obsidian 笔记仓库**（vault），用于系统学习：

1. QCL 的工作原理与设计物理
2. nextnano++ / nextnano³ / nextnano.NEGF 的用法
3. 从文献复现到自主设计完整 QCL 的流程

## 如何使用

- 在 Obsidian 中打开文件夹：`C:\Users\ciomp\Documents\QCL-nextnano`
- 建议按编号顺序阅读（01 → 12），中途可随时跳到感兴趣的主题
- 笔记中所有双链（wikilink）均指向仓库内其他笔记
- 本地 nextnano 示例文件路径在笔记中以 `C:\Program Files\nextnano\2025_08_21\...` 给出

## 学习路线（MOC）

### 第一站：原理
- [[01-QCL工作原理与物理基础]]

### 第二站：工具
- [[02-nextnano软件体系与工作流]]
- [[03-输入文件语法入门]]

### 第三站：复现官方示例（最有效的入门方式）
- [[04-示例1-Page2001-9um-GaAs-QCL]]
- [[05-示例2-Capasso简单级联与THz参数化]]

### 第四站：设计物理与数值
- [[06-材料体系与能带参数]]
- [[07-子带间跃迁-矩阵元-增益]]
- [[08-边界条件-网格-数值技巧]]

### 第五站：动手设计
- [[09-QCL设计流程Checklist]]
- [[10-常见问题FAQ]]

### 第六站：进阶
- [[11-文献库]]
- [[12-进阶-NEGF输运与增益优化]]

## 一句话设计流程

> 定目标波长 → 选材料体系 → 查/设计周期层序（阱/垒厚度）→ 在 nextnano++ 中建立 1D 结构并加偏置电场 → 解 Schrödinger 方程 → 核对跃迁能量与偶极矩阵元 → 加掺杂做自洽求解 → 用 nextnano.NEGF 算输运与增益 → 迭代优化。

详见 [[09-QCL设计流程Checklist]]。

## 本地 nextnano 安装

- 安装根目录：`C:\Program Files\nextnano\2025_08_21`
- QCL 示例（nextnano++）：`C:\Program Files\nextnano\2025_08_21\nextnano++\examples\quantum_cascade_lasers`
- QCL 示例（nextnano³）：`C:\Program Files\nextnano\2025_08_21\nextnano3\examples\quantum_cascade_lasers`
- NEGF：`C:\Program Files\nextnano\2025_08_21\nextnano.NEGF`

## 官方资料链接

- QCL 教程页：<https://www.nextnano.com/docu/nextnanoplus/latest/examples/qcl_realistic.html>
- 示例总览：<https://www.nextnano.com/docu/nextnanoplus/latest/examples/index.html>
- nextnano.NEGF：<https://www.nextnano.com/docu/nextnano.NEGF/>

## 我的 QCL 设计项目（占位）

- [ ] 确定目标波长 / 光子能量
- [ ] 选择材料体系
- [ ] 找到/设计参考周期层序
- [ ] 建立并跑通第一个 nextnano++ 输入文件
- [ ] 核对跃迁能量与偶极矩阵元
- [ ] 完成自洽计算与增益估算
- [ ] （进阶）NEGF 输运与优化
