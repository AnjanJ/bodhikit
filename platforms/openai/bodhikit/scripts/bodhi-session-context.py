#!/usr/bin/env python3
"""Inject BodhiKit's learning-project safeguards at Codex SessionStart.

Fail-open: malformed input, missing files, or an unexpected runtime error
produces no output and never blocks a session. ChatGPT does not depend on this
hook; the generated skill runtime reference carries the same invariant.
"""

import json
import os
import sys


def in_learning_project(cwd):
    cwd = os.path.abspath(cwd)
    parts = cwd.split(os.sep)
    if "learningWithBodhi" in parts:
        return True
    for name in (".bodhi", "learningWithBodhi", ".bodhi-profile.json"):
        if os.path.exists(os.path.join(cwd, name)):
            return True
    return False


def rule_body(path):
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
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
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": (
                        "BodhiKit learning-project rule (active because this "
                        "session started inside a learning project):\n\n"
                        + rule_body(rule)
                    ),
                }
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    raise SystemExit(0)
