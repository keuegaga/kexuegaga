# 贡献与提交规范

## 提交信息格式

单行主题：`<type>: <subject>`，subject 用中文描述，指向具体改动（可含 `[[笔记名]]`）：

```text
feat: 新增材料参数速查笔记
fix: 修正 .str 文件说明中的版本错误
docs: 更新总览中的入口链接
test: 记录第 9 轮 Codex 测试结果
chore: 统一 YAML 元数据，新增模板与检查脚本
```

常用 type：

- `feat`：新增笔记/功能
- `fix`：修正错误内容
- `docs`：文档/链接/说明更新
- `test`：测试记录
- `chore`：工具、配置、元数据等维护

## 操作习惯

```bash
git add -A
git commit -m "docs: 更新总览中的入口链接"
git push
```

- 一次提交只做一件事，主题单一；
- 提交前保证工作区干净（`git status` 无未预期文件）；
- 新笔记提交前跑一次完整性检查：`python scripts/check_notes.py .`，输出 `0 errors`；
- 新笔记必须带 YAML 元数据（六字段）、指向 `99-原始资料/` 的来源、标注验证状态；
- 分支命名建议使用 `codex/` 前缀（如 `codex/add-material-cheatsheet`）。

## 回滚

- 已推送、保留历史：`git revert <commit>`（生成反向提交）；
- 仅本地未推送：`git reset --hard <commit>`（慎用，会丢弃之后改动）；
- 查看演变历史：`git log --oneline`；
- 误删文件：`git checkout -- <path>` 或从历史提交恢复。

## 本仓库说明

- 仓库根目录同时是 Obsidian vault 和 Git 仓库；
- 本机 Codex 沙盒对 `.git` 目录只读，由 Codex 执行的 git 写操作会以你的账户提权运行（你本人在终端操作不受影响）；
- `git push` 需要先配置远程仓库（`git remote add origin <url>`），当前仓库尚未配置 remote。
