#!/usr/bin/env python3
"""Stop hook: schema safety net for BodhiKit tracking files.

Runs `bodhi-state verify` on any learning project under the session's working
directory whose tracking files were touched recently. If a tracking file is
structurally broken (invalid JSON, non-canonical sessionHistory type, missing
v3 fields), the hook blocks the stop once and tells Claude what to fix —
the structural answer to the 1.10.12 "computed everything, persisted a broken
state" failure class.

Fail-open by design: any unexpected error exits 0 (never trap the user in a
loop), and `stop_hook_active` short-circuits re-entry.
"""

import json
import os
import subprocess
import sys
import time

MAX_PROJECTS = 8
RECENT_SECONDS = 6 * 3600  # only verify projects touched this session-ish


def find_projects(root):
    """Find dirs containing .bodhi/state.json, shallow walk, bounded."""
    found = []
    root = os.path.abspath(root)
    for dirpath, dirnames, _ in os.walk(root):
        depth = dirpath[len(root):].count(os.sep)
        if depth >= 4:
            dirnames[:] = []
            continue
        # Skip heavy/irrelevant trees.
        dirnames[:] = [d for d in dirnames
                       if not d.startswith(".") or d == ".bodhi"
                       if d not in ("node_modules", "vendor", "target", "dist")]
        if os.path.exists(os.path.join(dirpath, ".bodhi", "state.json")):
            found.append(dirpath)
            dirnames[:] = []
        if len(found) >= MAX_PROJECTS:
            break
    return found


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

    failures = []
    for project in find_projects(cwd):
        if not recently_touched(project):
            continue
        try:
            r = subprocess.run(
                [sys.executable, script, "--project", project, "verify"],
                capture_output=True, text=True, timeout=10)
        except (subprocess.SubprocessError, OSError):
            continue
        if r.returncode != 0:
            try:
                errors = json.loads(r.stdout).get("errors", [])
            except json.JSONDecodeError:
                errors = [r.stdout[:200]]
            failures.append((project, errors))

    if failures:
        lines = []
        for project, errors in failures:
            lines.append(f"{project}: " + "; ".join(errors[:5]))
        print(json.dumps({
            "decision": "block",
            "reason": (
                "BodhiKit tracking files failed schema verification after this "
                "session's writes:\n" + "\n".join(lines) +
                "\nRepair them before stopping — prefer re-running the write "
                "through scripts/bodhi-state (record-review / record-session / "
                "touch-state) rather than hand-editing JSON. If a file is at "
                "v2, run `bodhi-state migrate-spaced-review`."
            ),
        }))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail-open: a broken hook must never block the user
        pass
    sys.exit(0)
