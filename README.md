# QCL-nextnano 知识仓库

量子级联激光器设计、nextnano++ / nextnano.NEGF 计算、文献复现与实验决策知识库。

## 从这里开始

在 Obsidian 中打开本目录后，从：

- `00-入口/知识库首页.md`
- `00-入口/当前验证状态与结论.md`
- `06-验证与决策/Sun2022-NEGF完整验证报告.md`

开始阅读。

## 当前结论

- Sun 2022 有源区的 k·p 9.17 µm 跃迁已复现。
- 物理归一化 NEGF 的实际宽窗首选分支为 10.8 µm（阈值附近）至 10.33 µm（较高电流）。
- 强制使用 9.17 µm 光模的模型阈值约 2.05 kA/cm²。
- 自由运行长波峰阈值约 1.71 kA/cm²；论文阈值为 1.52 kA/cm²。
- 当前 NEGF 尚不能认证 Sun 结构一定按论文 9 µm 激射，因此尚未修改 v3 层序。

## 目录

```text
00-入口/             首页、规范、当前结论
01-基础理论/         QCL 物理、子带、能带设计
02-软件与安装/       nextnano 产品、安装、CLI
03-输入与输出/       语法、材料、NEGF 输入和输出
04-设计流程/         设计 Checklist、实验流程
05-案例与文献/       官方例子、Fei/Liu/Sun 文献复现
06-验证与决策/       校准、鲁棒性、波导、完整报告
07-故障排查/         FAQ 和错误排查
08-术语与索引/       文献库、术语、总索引
09-历史迭代/         8 µm / Fei2021 / Liu2022 历史路线
_templates/          Obsidian 模板
attachments/         图片与动画
designs/             .nnp / .negf 输入
scripts/             可复现分析脚本
results/             小型结果、图像和 CSV
runs/                本地 nextnano 原始输出，不入 Git
QCL_references/      文献与参考资料
```

## 推荐路线

```text
基础理论
→ 输入语法
→ nextnano++ 能带
→ nextnano.NEGF 输运
→ 宽窗增益和位置分辨增益
→ 波导和热学
→ 鲁棒性与独立验证
→ 外延定版
```

## 本地软件

- nextnano++：
  `C:\Program Files\nextnano\2025_08_21\nextnano++\bin\nextnano++_Intel_64bit.exe`
- nextnano.NEGF：
  `C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\bin\nextnano.NEGF_win.exe`
- NEGF database：
  `C:\Program Files\nextnano\2025_08_21\nextnano.NEGF\database\Material_Database.negf`
- NEGF license：
  `D:\08-Study\Nextnano\License_nnNEGF.lic`

## 快速入口

- `00-入口/知识库首页.md`
- `03-输入与输出/Sun2022验证输入逐行注释.md`
- `03-输入与输出/变电压粒子数反转动画.md`
- `06-验证与决策/Sun2022-NEGF完整验证报告.md`
- `06-验证与决策/45-合金散射独立归一化与NEGF严格复现结论.md`
