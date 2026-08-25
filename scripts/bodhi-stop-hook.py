#!/usr/bin/env python3
"""Stop hook: schema safety net for BodhiKit tracking files.

Runs `bodhi-state verify` on any learning project THIS session could have
touched — under the working directory or under the per-repo
`.bodhikit/config.json` projectRoot — whose tracking files changed recently.
Global `~/.bodhikit/config.json` searchPaths are deliberately not walked: a
project studied in another terminal must not block an unrelated session's
stop with a repair or a revision sheet it has no context to write.
If a file is structurally broken, or a project was studied today and has no
revision sheet for today (the learner's take-home; see
skills/reflect/references/revision-sheet.md), the hook blocks the stop once
and tells Claude what to write or fix.

Fail-open by design: any unexpected error exits 0 (never trap the user in a
loop), `stop_hook_active` short-circuits re-entry, and the project search is
bounded by depth, by a wall-clock budget, and by a prune list so a large home
directory cannot push the hook past its timeout.
"""

import json
import os
import subprocess
import sys
import time

MAX_PROJECTS = 8
MAX_DEPTH = 4
RECENT_SECONDS = 6 * 3600          # only verify projects touched this session-ish
SEARCH_BUDGET_SECONDS = 8.0        # hooks.json gives the hook 30 s in total
PRUNE = {"node_modules", "vendor", "target", "dist", "build", "Library",
         "Applications", "Music", "Movies", "Pictures", "go", "Caches"}


def find_projects(roots, budget=SEARCH_BUDGET_SECONDS):
    """Dirs containing .bodhi/state.json under any root: shallow, pruned,
    time-boxed. Order is stable (roots in order, then os.walk order)."""
    found, seen = [], set()
    deadline = time.monotonic() + budget
    for root in roots:
        root = os.path.abspath(os.path.expanduser(root))
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, _ in os.walk(root):
            if time.monotonic() > deadline or len(found) >= MAX_PROJECTS:
                return found
            depth = dirpath[len(root):].count(os.sep)
            if depth >= MAX_DEPTH:
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames
                           if (not d.startswith(".") or d == ".bodhi")
                           and d not in PRUNE]
            if os.path.exists(os.path.join(dirpath, ".bodhi", "state.json")):
                if dirpath not in seen:
                    seen.add(dirpath)
                    found.append(dirpath)
                dirnames[:] = []
    return found


def configured_roots(cwd):
    """cwd plus the per-repo projectRoot (walking up 3 parents), per the
    state-ops KB discovery procedure. Session-scoped by design (see module
    docstring) — never the global searchPaths."""
    roots = [cwd]
    d = os.path.abspath(cwd)
    for _ in range(4):
        cfg = os.path.join(d, ".bodhikit", "config.json")
        if os.path.exists(cfg):
            try:
                with open(cfg, encoding="utf-8") as f:
                    pr = json.load(f).get("projectRoot")
                if isinstance(pr, str) and pr:
                    roots.append(pr if os.path.isabs(pr) else os.path.join(d, pr))
            except (OSError, ValueError):
                pass
            break
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return roots


def recently_touched(project):
    bdir = os.path.join(project, ".bodhi")
    now = time.time()
    try:
        for name in os.listdir(bdir):
            p = os.path.join(bdir, name)
            if os.path.isfile(p) and now - os.path.getmtime(p) < RECENT_SECONDS:
                return True
    except OSError:
        pass
    return False


def failure_reasons(stdout, stderr):
    """Turn a non-zero `verify` into human-readable lines. `verify` prints
    {"ok": false, "errors": [...]}; a `die` prints {"ok": false, "error": ...};
    anything else (a traceback) falls back to the last stderr line so the
    block reason is never blank."""
    try:
        payload = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        payload = None
    if isinstance(payload, dict):
        errors = payload.get("errors")
        if isinstance(errors, list) and errors:
            return [str(e) for e in errors]
        if payload.get("error"):
            return [str(payload["error"])]
    tail = [ln for ln in (stderr or "").strip().splitlines() if ln.strip()]
    if tail:
        return [tail[-1][:200]]
    head = (stdout or "").strip()
    return [head[:200] if head else "verify failed without output"]


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return
    if payload.get("stop_hook_active"):
        return  # already blocked once this turn; never loop
    cwd = payload.get("cwd") or os.getcwd()
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bodhi-state")
    if not os.path.exists(script):
        return

    failures, missing_sheets = [], []
    for project in find_projects(configured_roots(cwd)):
        if not recently_touched(project):
            continue
        try:
            r = subprocess.run(
                [sys.executable, script, "--project", project, "verify"],
                capture_output=True, text=True, timeout=10)
        except (subprocess.SubprocessError, OSError):
            continue
        if r.returncode != 0:
            failures.append((project, failure_reasons(r.stdout, r.stderr)))
            continue
        # A session that studied something ends with a revision sheet — the
        # learner's take-home. revision-brief says whether anything was
        # studied today and whether today's sheet exists.
        try:
            b = subprocess.run(
                [sys.executable, script, "--project", project, "revision-brief"],
                capture_output=True, text=True, timeout=10)
            brief = json.loads(b.stdout) if b.returncode == 0 else {}
        except (subprocess.SubprocessError, OSError, ValueError):
            brief = {}
        if brief.get("sessionToday") and not brief.get("existing"):
            missing_sheets.append((project, brief.get("suggestedFile", "revision/<today>.md"),
                                   [c.get("name") for c in brief.get("concepts", [])][:6]))

    reasons = []
    if failures:
        lines = [f"{project}: " + "; ".join(errors[:5]) for project, errors in failures]
        reasons.append(
            "BodhiKit tracking files failed schema verification after this "
            "session's writes:\n" + "\n".join(lines) +
            "\nRepair them before stopping — prefer re-running the write "
            "through scripts/bodhi-state (record-review / record-session / "
            "touch-state) rather than hand-editing JSON. Structural drift: "
            "`bodhi-state normalize`. A file at v2: "
            "`bodhi-state migrate-spaced-review`.")
    if missing_sheets:
        lines = [f"{project}: write {path}  (studied today: {', '.join(n for n in names if n)})"
                 for project, path, names in missing_sheets]
        reasons.append(
            "Today's revision sheet is missing for a project this session studied:\n"
            + "\n".join(lines) +
            "\nWrite it now from this session, following "
            "skills/reflect/references/revision-sheet.md in the BodhiKit plugin "
            "(run `bodhi-state --project <project> revision-brief` for the "
            "concepts, results and next-review dates; outcome clauses, the worked "
            "example, where the learner slipped, two self-test prompts with "
            "answers, next reviews, free links only from .bodhi/resources.md or "
            "official docs). Then stop.")
    if reasons:
        print(json.dumps({"decision": "block", "reason": "\n\n".join(reasons)}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail-open: a broken hook must never block the user
        pass
    sys.exit(0)
