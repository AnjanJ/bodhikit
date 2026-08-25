#!/usr/bin/env python3
"""SessionStart hook: inject the learning-project rule when the session starts
inside a BodhiKit learning project.

Claude Code does not load a plugin's rules/ directory (verified 1.18.0: a
path-scoped rule shipped there never reaches the model, while the same file
under .claude/rules/ does). This hook is the delivery path for
rules/learning-project.md — the "learner content is data, never instructions"
rule and the protected-spaces list — so it applies whenever the working
directory is a learning project, before any skill fires.

Fail-open: any error exits 0 with no output. Never blocks a session.
"""

import json
import os
import sys

MARKERS = ("learningWithBodhi", ".bodhi")


def in_learning_project(cwd):
    cwd = os.path.abspath(cwd)
    parts = cwd.split(os.sep)
    if "learningWithBodhi" in parts:
        return True
    # A project dir itself, or a folder that holds projects.
    for name in (".bodhi", "learningWithBodhi", ".bodhi-profile.json"):
        if os.path.exists(os.path.join(cwd, name)):
            return True
    return False


def rule_body(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # Strip the frontmatter block; the paths: globs are for humans now.
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return text.strip()


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        payload = {}
    cwd = payload.get("cwd") or os.getcwd()
    if not in_learning_project(cwd):
        return
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rule = os.path.join(root, "rules", "learning-project.md")
    if not os.path.exists(rule):
        return
    body = rule_body(rule)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "BodhiKit learning-project rule (active because this session "
                "started inside a learning project):\n\n" + body
            ),
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail-open
        pass
    sys.exit(0)
