#!/usr/bin/env python3
"""Checks on dev/outcomes.py, the docs/outcomes.md generator (learn-anything).

learn-anything/REQ-41: the report gives delayed recall per evidence kind and
counts Solid concepts resting on the learner's own report separately. Runs
the generator on copies of two eval fixtures (a code project with no kind
recorded, and the performed cooking project) and reads its markdown.

Run: python3 dev/eval/test_outcomes.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIXTURES = os.path.join(HERE, "fixtures")
PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"ok    {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def export(project):
    r = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "bodhi-state"),
                        "--project", project, "export-anonymized"],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def t_recall_per_kind():
    with tempfile.TemporaryDirectory() as root:
        projects = []
        for ws, name in (("v2-project", "sql-deep-dive"), ("performed-project", "cooking")):
            shutil.copytree(os.path.join(FIXTURES, ws), os.path.join(root, ws))
            projects.append(os.path.join(root, ws, name))
        r = subprocess.run([sys.executable, os.path.join(REPO, "dev", "outcomes.py"), *projects],
                           capture_output=True, text=True)
        check("outcomes: runs", r.returncode == 0, r.stderr[-300:])
        md = r.stdout
        section = md.split("## By evidence kind", 1)[1].split("\n## ", 1)[0] if \
            "## By evidence kind" in md else ""
        check("outcomes: has a by-kind section", bool(section), md[:200])
        rows = {m.group(1): [c.strip() for c in m.group(2).split("|")]
                for m in re.finditer(r"^\| `(\w+)` \|(.*)\|\s*$", section, re.M)}
        check("outcomes: one row per kind on record, code and performed",
              set(rows) == {"code", "performed"}, rows)
        sql, cooking = (export(p) for p in projects)
        for kind, e in (("code", sql), ("performed", cooking)):
            ret = e["retention"]["byKind"].get(kind, {})
            rate = ret.get("delayedSuccessRate")
            want = "—" if rate is None else f"{round(rate * 100)}%"
            check(f"outcomes: {kind} delayed recall is the export's",
                  kind in rows and rows[kind][-1] == want
                  and rows[kind][-2] == str(ret.get("delayedReviews", 0)), (rows.get(kind), want))
        check("outcomes: Solid by the learner's account is counted apart",
              kind_cell(rows, "performed", 2) == "1" and kind_cell(rows, "code", 2) == "0"
              and re.search(r"Solid by the learner's account: \*\*1\*\* of 1", section), section)


def kind_cell(rows, kind, i):
    return rows.get(kind, [None] * 6)[i]


def main():
    t_recall_per_kind()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
