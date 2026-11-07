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

from pathlib import Path
import subprocess
import sys

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


def main():
    t_output_is_ignored()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
