#!/usr/bin/env python3
"""Checks for the maintainer's guide-writing skill (spec write-guide).

`dev/guide-writer/` is a Claude Code skill that writes personalised guides to
using BodhiKit in Claude and ChatGPT. It is a maintainer tool: it never ships,
and it runs only when typed. What a model does during a run (asking, verifying,
keeping the claim ledger) is checked by hand on a real run, per the spec; this
suite checks what can be checked without one.

Run: python3 dev/eval/test_guide_writer.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "dev" / "guide-writer"
PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"ok    {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def t_output_is_ignored():
    """write-guide/REQ-4: guides hold personal details, and the repo is public."""
    result = git("check-ignore", "-q", "output/any-guide.pdf")
    check("REQ-4 output/ is ignored by git", result.returncode == 0,
          "add `output/` to .gitignore")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    block = text.split("\n---\n", 1)[0][4:]
    fields = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"')
    return fields


def t_typed_only():
    """write-guide/REQ-1: nothing in context until /write-guide is typed."""
    skill = SKILL / "SKILL.md"
    check("REQ-1 dev/guide-writer/SKILL.md exists", skill.is_file())
    if not skill.is_file():
        return
    fields = frontmatter(skill)
    check("REQ-1 frontmatter sets disable-model-invocation: true",
          fields.get("disable-model-invocation") == "true", fields)
    check("REQ-1 frontmatter names the skill write-guide",
          fields.get("name") == "write-guide", fields.get("name"))
    check("REQ-1 frontmatter has a description", bool(fields.get("description")))


def t_not_in_any_package():
    """write-guide/REQ-2: a maintainer tool never reaches a learner."""
    cowork = load_module("cowork_build", REPO / "platforms" / "cowork" / "build_plugin.py")
    shipped = [p.as_posix() for p in cowork.package_files()]
    leaked = [p for p in shipped if "guide-writer" in p or p.startswith("dev/")]
    check("REQ-2 Cowork package carries nothing from dev/guide-writer/", not leaked, leaked[:4])
    openai = load_module("openai_build", REPO / "platforms" / "openai" / "build_plugin.py")
    with tempfile.TemporaryDirectory(prefix="bodhikit-gw-test-") as temp:
        out = Path(temp) / "bodhikit"
        openai.build(out)
        names = [p.relative_to(out).as_posix() for p in out.rglob("*")]
        leaked = [n for n in names if "guide-writer" in n or "write-guide" in n]
        check("REQ-2 OpenAI package carries nothing from dev/guide-writer/", not leaked, leaked[:4])


def main():
    t_output_is_ignored()
    t_typed_only()
    t_not_in_any_package()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
