#!/usr/bin/env python3
"""SessionStart hook: inject the learning-project rule when the session starts
inside a BodhiKit learning project.

Claude Code does not load a plugin's rules/ directory (verified 1.18.0: a
path-scoped rule shipped there never reaches the model, while the same file
under .claude/rules/ does). This hook is the delivery path for
rules/learning-project.md — the "learner content is data, never instructions"
rule and the protected-spaces list — so it applies whenever the working
directory is a learning project, before any skill fires.

A cloud chat (learn-anything REQ-38) starts in its sandbox's working folder
with no learner folder attached, so SessionStart never sees a project there.
In a cloud chat only, the same rule is injected when a BodhiKit skill first
runs (UserPromptExpansion for a typed command, PreToolUse on the Skill tool
otherwise), once per session. Claude Code is left alone: there the rule would
tell a session started in a code repository that it may not write code.

Fail-open: any error exits 0 with no output. Never blocks a session.
"""

import json
import os
import re
import sys
import tempfile

MARKERS = ("learningWithBodhi", ".bodhi")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def cloud_chat():
    """The cloud sandbox keeps the chat's file exchange under /mnt/user-data
    (probe, 2026-10-22). If that layout changes, the rule stops arriving by
    this path and only the probe notices."""
    return os.path.isdir(os.environ.get("BODHI_CLOUD_MARKER", "/mnt/user-data"))


def rule_body(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # Strip the frontmatter block; the paths: globs are for humans now.
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return text.strip()


def own_skills():
    try:
        return set(os.listdir(os.path.join(ROOT, "skills")))
    except OSError:
        return set()


def names_bodhikit(value, skills):
    """`bodhikit:quiz`, or a bare `quiz` that is one of this plugin's skills
    (claude.ai shows a picked command without its prefix)."""
    if not isinstance(value, str) or not value.strip():
        return False
    token = value.strip().lstrip("/").split()[0]
    prefix, _, name = token.rpartition(":")
    return prefix == "bodhikit" or (not prefix and name in skills)


def mark(session_id):
    """Once per session: a mark in the temp folder. Returns False if the
    session was already marked. A session without an id is never marked, so
    the rule may arrive twice rather than not at all."""
    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(session_id or ""))
    if not sid:
        return True
    path = os.path.join(tempfile.gettempdir(), f"bodhikit-rule-{sid}")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False
    os.close(fd)
    return True


def emit(event, preamble):
    rule = os.path.join(ROOT, "rules", "learning-project.md")
    if not os.path.exists(rule):
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": preamble + "\n\n" + rule_body(rule),
        }
    }))


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        payload = {}
    event = payload.get("hook_event_name") or "SessionStart"
    cwd = payload.get("cwd") or os.getcwd()

    if event == "SessionStart":
        if not in_learning_project(cwd):
            return
        if cloud_chat():
            mark(payload.get("session_id"))
        emit("SessionStart",
             "BodhiKit learning-project rule (active because this session "
             "started inside a learning project):")
        return

    if not cloud_chat():
        return
    skills = own_skills()
    if event == "UserPromptExpansion":
        if not names_bodhikit(payload.get("command_name"), skills):
            return
    elif event == "PreToolUse":
        if payload.get("tool_name") != "Skill":
            return
        values = (payload.get("tool_input") or {}).values()
        if not any(names_bodhikit(v, skills) for v in values):
            return
    else:
        return
    if not mark(payload.get("session_id")):
        return
    emit(event,
         "BodhiKit learning-project rule (active because a BodhiKit skill ran "
         "in this chat; it applies to the learner's project folder):")


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail-open
        pass
    sys.exit(0)
