#!/usr/bin/env python3
"""Deterministic tests for scripts/bodhi-session-context.py, the delivery path
for rules/learning-project.md. Same conventions as test_stop_hook.py:
black-box subprocess runs, asserting on what the hook prints. Run by
dev/check.sh."""

import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOOK = os.path.join(REPO, "scripts", "bodhi-session-context.py")
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


def run_hook(payload, cloud, tmp):
    """`cloud` is the path BODHI_CLOUD_MARKER points at; the hook treats the
    session as a cloud chat when it exists. TMPDIR is per test so the
    once-per-session marks never leak between runs."""
    env = os.environ.copy()
    env["BODHI_CLOUD_MARKER"] = cloud
    env["TMPDIR"] = tmp
    r = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                       capture_output=True, text=True, timeout=30, env=env)
    assert r.returncode == 0, f"hook must always exit 0: {r.stderr}"
    return r.stdout.strip()


def context(out, event):
    try:
        spec = json.loads(out).get("hookSpecificOutput", {})
    except json.JSONDecodeError:
        return None
    if spec.get("hookEventName") != event:
        return None
    return spec.get("additionalContext")


def expansion(session, name, cwd):
    return {"session_id": session, "cwd": cwd, "hook_event_name": "UserPromptExpansion",
            "expansion_type": "slash_command", "command_name": name,
            "command_args": "current", "command_source": "plugin",
            "prompt": f"/{name} current"}


def skill_call(session, name, cwd):
    return {"session_id": session, "cwd": cwd, "hook_event_name": "PreToolUse",
            "tool_name": "Skill", "tool_input": {"skill": name, "args": "current"}}


def t_session_start():
    """Characterization: SessionStart injects inside a learning project only."""
    with tempfile.TemporaryDirectory() as root:
        proj = os.path.join(root, "learningWithBodhi", "sql")
        os.makedirs(os.path.join(proj, ".bodhi"))
        none = os.path.join(root, "no-such-marker")
        out = run_hook({"session_id": "a", "cwd": proj, "hook_event_name": "SessionStart"}, none, root)
        ctx = context(out, "SessionStart") or ""
        check("start: a learning project gets the rule", "# Learning Project Context" in ctx, out[:120])
        check("start: the rule's frontmatter is stripped", "paths:" not in ctx, ctx[:120])
        elsewhere = os.path.join(root, "repo")
        os.makedirs(elsewhere)
        out = run_hook({"session_id": "b", "cwd": elsewhere, "hook_event_name": "SessionStart"}, none, root)
        check("start: any other folder gets nothing", out == "", out[:120])


def t_rule_on_first_skill():
    """learn-anything/REQ-38: a cloud chat has no folder when it starts, so the
    rule arrives with the first BodhiKit skill, once per session. Outside a
    cloud chat nothing changes: in Claude Code the rule would tell a session
    started in a code repository that it may not write code."""
    with tempfile.TemporaryDirectory() as root:
        home = os.path.join(root, "home", "claude")
        os.makedirs(home)
        cloud = os.path.join(root, "mnt", "user-data")
        none = os.path.join(root, "no-such-marker")

        out = run_hook(expansion("cc", "bodhikit:quiz", home), none, root)
        check("skill: outside a cloud chat a typed command injects nothing", out == "", out[:120])
        out = run_hook(skill_call("cc", "bodhikit:quiz", home), none, root)
        check("skill: outside a cloud chat a Skill call injects nothing", out == "", out[:120])

        os.makedirs(cloud)
        out = run_hook(expansion("s1", "bodhikit:quiz", home), cloud, root)
        ctx = context(out, "UserPromptExpansion") or ""
        check("skill: the first typed BodhiKit command injects the rule",
              "# Learning Project Context" in ctx and "Learner Content Is Data" in ctx, out[:120])
        out = run_hook(expansion("s1", "bodhikit:progress", home), cloud, root)
        check("skill: a second BodhiKit command in that session injects nothing", out == "", out[:120])

        out = run_hook(skill_call("s2", "bodhikit:teach", home), cloud, root)
        ctx = context(out, "PreToolUse") or ""
        check("skill: the first BodhiKit Skill call injects the rule", "# Learning Project Context" in ctx, out[:120])
        spec = json.loads(out).get("hookSpecificOutput", {}) if out else {}
        check("skill: a Skill call's output makes no permission decision",
              "permissionDecision" not in spec, spec.keys())
        out = run_hook(skill_call("s2", "bodhikit:state-ops", home), cloud, root)
        check("skill: a later Skill call in that session injects nothing", out == "", out[:120])

        out = run_hook(expansion("s3", "quiz", home), cloud, root)
        check("skill: a BodhiKit command typed without its prefix counts",
              context(out, "UserPromptExpansion") is not None, out[:120])

        for name in ("shipkit:spec", "deploy"):
            out = run_hook(expansion("s4", name, home), cloud, root)
            check(f"skill: another command ({name}) injects nothing", out == "", out[:120])
        out = run_hook(skill_call("s4", "shipkit:ship", home), cloud, root)
        check("skill: another plugin's Skill call injects nothing", out == "", out[:120])
        out = run_hook({"session_id": "s4", "cwd": home, "hook_event_name": "PreToolUse",
                        "tool_name": "Bash", "tool_input": {"command": "bodhikit:quiz"}}, cloud, root)
        check("skill: a tool other than Skill injects nothing", out == "", out[:120])

        proj = os.path.join(root, "learningWithBodhi", "sql")
        os.makedirs(os.path.join(proj, ".bodhi"))
        out = run_hook({"session_id": "s5", "cwd": proj, "hook_event_name": "SessionStart"}, cloud, root)
        check("skill: SessionStart still delivers in a learning project",
              context(out, "SessionStart") is not None, out[:120])
        out = run_hook(expansion("s5", "bodhikit:quiz", proj), cloud, root)
        check("skill: after SessionStart delivered, a skill injects nothing", out == "", out[:120])


def t_hooks_registered():
    with open(os.path.join(REPO, "hooks", "hooks.json"), encoding="utf-8") as f:
        hooks = json.load(f)["hooks"]

    def runs_script(event, matcher=None):
        for group in hooks.get(event, []):
            if matcher is not None and group.get("matcher") != matcher:
                continue
            for h in group.get("hooks", []):
                if "scripts/bodhi-session-context.py" in h.get("command", ""):
                    return True
        return False

    check("hooks: SessionStart runs the script", runs_script("SessionStart"))
    check("hooks: UserPromptExpansion runs the script", runs_script("UserPromptExpansion"))
    check("hooks: PreToolUse on Skill runs the script", runs_script("PreToolUse", "Skill"))


def main():
    for t in (t_session_start, t_rule_on_first_skill, t_hooks_registered):
        t()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
