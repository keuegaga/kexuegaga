# -*- coding: utf-8 -*-
"""Check Obsidian wikilinks and local Markdown links in the QCL vault."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote


WIKILINK = re.compile(r"!?\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()

    markdown_files = [
        path
        for path in root.rglob("*.md")
        if (
            ".git" not in path.parts
            and "_scratch" not in path.parts
            and "QCL_references" not in path.parts
            and "99-原始资料" not in path.parts
        )
    ]
    note_targets = {path.stem for path in markdown_files}
    asset_targets = {
        path.name
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".gif", ".jpg", ".jpeg"}
    }

    errors = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in WIKILINK.finditer(text):
            target = match.group(1).strip()
            target_name = Path(target).name.removesuffix(".md")
            if target_name not in note_targets and Path(target).name not in asset_targets:
                errors.append(f"{path.relative_to(root)}: unresolved wikilink [[{target}]]")

        for match in MARKDOWN_LINK.finditer(text):
            target = unquote(match.group(1).strip())
            if target.startswith(
                ("http://", "https://", "mailto:", "data:", "#", "codex://")
            ):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(
                    f"{path.relative_to(root)}: missing Markdown target {target}"
                )

    print(f"Markdown notes: {len(markdown_files)}")
    print(f"Errors: {len(errors)}")
    for error in errors:
        print(error)
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
