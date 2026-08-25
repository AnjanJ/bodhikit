#!/usr/bin/env python3
"""Deterministic tests for scripts/bodhi-stop-hook.py (1.18.0). Same
conventions as test_bodhi_state.py: black-box subprocess runs, asserting on
what the hook prints. Run by dev/check.sh."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOOK = os.path.join(REPO, "scripts", "bodhi-stop-hook.py")
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


def run_hook(payload, env=None):
    r = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                       capture_output=True, text=True, timeout=60,
                       env=env or os.environ.copy())
    assert r.returncode == 0, f"hook must always exit 0: {r.stderr}"
    return r.stdout.strip()


def make_project(root, name, sr=None):
    proj = os.path.join(root, "learningWithBodhi", name)
    os.makedirs(os.path.join(proj, ".bodhi"))
    with open(os.path.join(proj, ".bodhi", "state.json"), "w") as f:
        json.dump({"version": 2, "projectName": name, "sessionDates": []}, f)
    with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
        json.dump(sr or {"version": 3, "concepts": [], "sessionHistory": []}, f)
    return proj


BROKEN_SR = {"version": 3, "sessionHistory": [], "concepts": [
    {"name": "Joins", "module": "A", "box": "three", "bloomLevel": 0,
     "feynmanPassed": False, "consecutiveCorrectAtL4Plus": 0,
     "reviewHistory": [], "nextReview": "2026-01-01"}]}


def t_block_on_broken():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, "sql", BROKEN_SR)
        out = run_hook({"cwd": root, "hook_event_name": "Stop"})
        check("hook: broken project blocks the stop", out.startswith("{"), out[:80])
        d = json.loads(out) if out else {}
        check("hook: decision is block", d.get("decision") == "block", d)
        check("hook: reason names the project and the field",
              proj in d.get("reason", "") and "box" in d.get("reason", ""), d)
        # a clean project does not block
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump({"version": 3, "concepts": [], "sessionHistory": []}, f)
        out = run_hook({"cwd": root})
        check("hook: clean project is silent", out == "", out)


def t_reentry_and_stale():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, "sql", BROKEN_SR)
        out = run_hook({"cwd": root, "stop_hook_active": True})
        check("hook: stop_hook_active short-circuits", out == "", out)
        old = time.time() - 8 * 3600
        for name in os.listdir(os.path.join(proj, ".bodhi")):
            os.utime(os.path.join(proj, ".bodhi", name), (old, old))
        out = run_hook({"cwd": root})
        check("hook: a project untouched for 8h is not verified", out == "", out)


def t_configured_roots():
    """Projects reachable only through ~/.bodhikit/config.json searchPaths
    or a per-repo .bodhikit/config.json projectRoot are verified too."""
    with tempfile.TemporaryDirectory() as root:
        home = os.path.join(root, "home")
        elsewhere = os.path.join(root, "elsewhere")
        cwd = os.path.join(root, "repo")
        os.makedirs(os.path.join(home, ".bodhikit"))
        os.makedirs(cwd)
        proj = make_project(elsewhere, "sql", BROKEN_SR)
        with open(os.path.join(home, ".bodhikit", "config.json"), "w") as f:
            json.dump({"searchPaths": ["$PWD", elsewhere]}, f)
        env = os.environ.copy()
        env["HOME"] = home
        out = run_hook({"cwd": cwd}, env=env)
        check("hook: global searchPaths root is verified",
              proj in (json.loads(out).get("reason", "") if out else ""), out[:120])
        # per-repo projectRoot
        os.makedirs(os.path.join(cwd, ".bodhikit"))
        with open(os.path.join(cwd, ".bodhikit", "config.json"), "w") as f:
            json.dump({"projectRoot": os.path.join(root, "study")}, f)
        proj2 = make_project(os.path.join(root, "study"), "rust", BROKEN_SR)
        out = run_hook({"cwd": os.path.join(cwd)}, env={**env, "HOME": os.path.join(root, "nohome")})
        check("hook: per-repo projectRoot is verified",
              proj2 in (json.loads(out).get("reason", "") if out else ""), out[:120])


def t_bounded_search():
    """A wide, deep tree with no projects must finish inside the budget."""
    with tempfile.TemporaryDirectory() as root:
        for a in range(12):
            for b in range(12):
                for c in range(6):
                    os.makedirs(os.path.join(root, f"a{a}", f"b{b}", f"c{c}", "d", "e"))
        # a project below MAX_DEPTH is ignored; one at depth 2 is found
        make_project(os.path.join(root, "a0", "b0", "c0", "d"), "deep", BROKEN_SR)
        proj = make_project(root, "shallow", BROKEN_SR)
        t0 = time.monotonic()
        out = run_hook({"cwd": root})
        elapsed = time.monotonic() - t0
        check("hook: bounded search finishes quickly", elapsed < 15, f"{elapsed:.1f}s")
        reason = json.loads(out).get("reason", "") if out else ""
        check("hook: shallow project found", proj in reason, reason[:120])
        check("hook: project beyond MAX_DEPTH not walked", "deep" not in reason)


def t_failure_reasons():
    spec = importlib.util.spec_from_file_location("hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    check("reasons: verify errors list",
          mod.failure_reasons('{"ok": false, "errors": ["a", "b"]}', "") == ["a", "b"])
    check("reasons: die error field",
          mod.failure_reasons('{"ok": false, "error": "boom"}', "") == ["boom"])
    check("reasons: traceback falls back to last stderr line",
          mod.failure_reasons("", "Traceback...\nKeyError: 'name'\n") == ["KeyError: 'name'"])
    check("reasons: never blank",
          mod.failure_reasons("", "") == ["verify failed without output"])


def main():
    for t in (t_block_on_broken, t_reentry_and_stale, t_configured_roots,
              t_bounded_search, t_failure_reasons):
        t()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
