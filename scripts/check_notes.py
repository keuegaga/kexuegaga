#!/usr/bin/env python3
"""检查知识库笔记的 YAML 元数据、命令代码块与双链完整性。

用法: python scripts/check_notes.py [vault_root]

检查范围: 00-09 编号目录下的全部 .md（跳过 _templates/、99-原始资料/、books/、.obsidian/、.git/）。
规则:
1. frontmatter 必须包含 title/type/status/version/source/last_verified 六字段;
2. status 取值必须为 draft|source|verified|deprecated|conflict;
3. 以 Crosslight 输入语句关键字开头的命令行必须位于代码块内;
4. 双链 [[target]] 必须能解析到已有文件（按文件名或相对路径，支持 .pdf）。
退出码 0 = 无错误。
"""

import re
import sys
from pathlib import Path

REQUIRED = ["title", "type", "status", "version", "source", "last_verified"]
VALID_STATUS = {"draft", "source", "verified", "deprecated", "conflict"}
SKIP_DIRS = {".git", ".obsidian", "books", "_templates", "99-原始资料"}

# 以这些关键字开头的行视为 Crosslight 输入语句，必须放在代码块内
KEYWORDS = {
    "scan", "equilibrium", "newton_par", "bias", "temperature", "include",
    "load_macro", "get_active_layer", "use_macrofile", "gain_wavel",
    "sp.rate_wavel", "gain_density", "plot_scan", "plot_1d", "lplot_xy",
    "get_data", "put_mesh", "double_mesh", "half_mesh", "regrid",
    "heat_flow", "contact", "begin_layer", "end_layer", "begin_gain",
    "end_gain", "begin_sol", "end_sol", "begin_zsol", "end_zsol",
    "begin_zmater", "end_zmater", "begin_meshgen", "end_meshgen",
    "load_mesh", "output", "more_output", "solve_rtg", "q_transport",
    "cylindrical", "vcsel_model", "longitudinal", "mode_srch",
    "begin_cavity", "end_cavity", "start_loop", "define_alias",
}
LINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")


def parse_frontmatter(text):
    """返回 (字段字典, 匹配对象) 或 (None, None)。"""
    if not text.startswith("---"):
        return None, None
    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return None, None
    fields = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if mm:
            fields[mm.group(1)] = mm.group(2).strip()
    return fields, m


def check_commands(text, rel):
    errors = []
    in_fence = False
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not s or s[0] in "|-*#":
            continue
        head = s.split(None, 1)[0].rstrip("=,;")
        if head.lower() in KEYWORDS:
            errors.append(f"{rel}:{i}: 命令行出现在代码块外: {s[:60]}")
    return errors


def check_links(text, rel, all_stems, vault):
    errors = []
    for m in LINK_RE.finditer(text):
        target = m.group(1).split("|")[0].strip()
        if not target:
            continue
        if target.endswith(".pdf"):
            if not (vault / target).exists():
                errors.append(f"{rel}: 双链目标不存在: {target}")
            continue
        if target.endswith(".md"):
            if (vault / target).exists():
                continue
            base = target[:-3]
        else:
            base = target.rsplit("/", 1)[-1]
        if base not in all_stems:
            errors.append(f"{rel}: 双链目标不存在: {target}")
    return errors


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    notes = []
    for p in sorted(root.rglob("*.md")):
        parts = p.relative_to(root).parts
        if any(part in SKIP_DIRS for part in parts):
            continue
        if not re.match(r"^\d{2}-", parts[0]):
            continue
        notes.append(p)

    def is_indexed(p):
        return not any(part in SKIP_DIRS | {".git", ".obsidian"} for part in p.relative_to(root).parts)

    all_stems = set()
    for p in list(root.rglob("*.md")) + list(root.rglob("*.pdf")):
        if is_indexed(p):
            all_stems.add(p.stem)

    errors = []
    for p in notes:
        rel = str(p.relative_to(root)).replace("\\", "/")
        text = p.read_text(encoding="utf-8")
        fields, _ = parse_frontmatter(text)
        if fields is None:
            errors.append(f"{rel}: 缺少 YAML frontmatter")
            continue
        for key in REQUIRED:
            if key not in fields:
                errors.append(f"{rel}: frontmatter 缺少字段 '{key}'")
        status = fields.get("status")
        if status is not None and status not in VALID_STATUS:
            errors.append(
                f"{rel}: status 取值 '{status}' 非法（应为 draft|source|verified|deprecated|conflict）"
            )
        errors.extend(check_commands(text, rel))
        errors.extend(check_links(text, rel, all_stems, root))

    for e in errors:
        print("ERROR:", e)
    print(f"checked {len(notes)} notes, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
