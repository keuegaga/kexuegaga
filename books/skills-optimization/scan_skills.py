import os
import re
import json

root = r"C:\Users\ciomp\.codex\skills"
skip = {".system", "cangjie-skill", "darwin-skill"}

def read(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

rows = []
for name in sorted(os.listdir(root)):
    if name in skip:
        continue
    d = os.path.join(root, name)
    if not os.path.isdir(d) or not os.path.exists(os.path.join(d, "SKILL.md")):
        continue
    t = read(os.path.join(d, "SKILL.md"))
    desc = ""
    m = re.search(r"^description:\s*\|?\s*(.*)$", t, re.M)
    if m:
        desc = m.group(1).strip()[:120]
    rows.append({
        "name": name,
        "len": len(t),
        "desc": desc,
        "checkpoint": "🔴" in t or "STOP" in t,
        "fallback_table": ("触发条件" in t and "一线修复" in t and "兜底" in t),
        "dont_list": "不要在以下情况" in t or "不要" in t,
        "headers": t.count("\n## "),
        "code_fences": t.count("```"),
        "completion": t.count("完成标准"),
        "branch": t.count("判停"),
        "test_prompts": os.path.exists(os.path.join(d, "test-prompts.json")),
    })

print(json.dumps(rows, ensure_ascii=False, indent=1))
