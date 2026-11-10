#!/usr/bin/env python3
"""Codex Stop adapter for BodhiKit's canonical schema-safety hook.

Codex exposes a transcript path but does not guarantee the transcript's
internal format. This adapter finds TOOL-CALL records — a dict carrying a
tool marker (`tool_name`, `name`, `function`, or a `type` of tool_use /
tool_call / function_call / tool) whose `command` (or `tool_input.command`,
`input.command`, `arguments.command`) is a string — and emits a minimal
normalized transcript for the canonical BodhiKit hook. Codex 0.167 writes
each command it ran as a `CommandExecution` item whose `command` is an argv
list (`["/bin/zsh", "-lc", "<script>"]`) and whose `cwd` is a `file://` URL;
the script is read from that list. The `exec` call that precedes it holds
JavaScript and is not parsed. When such a script runs `touch-state` but
names no `--project <path>` (the tutor wrapped bodhi-state in a Python
heredoc), it counts for the projects under the hook's usual roots whose
`.bodhi/` files changed after the command started (decision "in Codex,
touch-state run from a script counts for the projects it changed",
learning-vault design). Prose is never
inspected: an assistant paragraph that *mentions* a bodhi-state command is
not evidence the command ran (review finding 8, 2026-09-07 — a read-only
discussion used to block the stop with a revision-sheet demand). If no
tool-call record can be recognised, schema verification still runs and
revision-sheet enforcement fails open for that turn.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlparse


TOOL_MARKER_KEYS = ("tool_name", "name", "function")
TOOL_TYPES = {"tool_use", "tool_call", "function_call", "tool", "CommandExecution"}
SHELL_FLAGS = {"-c", "-lc", "-ic", "-lic"}
COMMAND_CONTAINERS = ("tool_input", "input", "arguments", "args", "parameters")
PROSE_KEYS = {"content", "text", "message", "output", "result", "stdout",
              "stderr", "last_assistant_message", "reasoning"}
# The canonical hook reads a project only from `--project <path>` or
# `--project=<path>` (its session_writes); a script without one names none.
PROJECT_ARG = re.compile(r"--project(?:\s+|=)")
TOUCH = re.compile(r"\btouch-state\b")
REGISTER = re.compile(r"\bprofile-add-project\b")
START_SLACK_SECONDS = 2.0


def _is_tool_record(d):
    if not isinstance(d, dict):
        return False
    if any(isinstance(d.get(k), str) and d[k] for k in TOOL_MARKER_KEYS):
        return True
    if isinstance(d.get("function"), dict):
        return True
    return isinstance(d.get("type"), str) and d["type"] in TOOL_TYPES


def _command_of(d):
    """The command string of a tool record, wherever the host put it."""
    cmd = d.get("command")
    if isinstance(cmd, str):
        return cmd
    if isinstance(cmd, list) and cmd and all(isinstance(a, str) for a in cmd):
        # Codex 0.167 CommandExecution: `<shell> -lc <script>`, or plain argv.
        if len(cmd) == 3 and cmd[1] in SHELL_FLAGS:
            return cmd[2]
        return shlex.join(cmd)
    for key in COMMAND_CONTAINERS:
        inner = d.get(key)
        if isinstance(inner, str):
            try:
                inner = json.loads(inner)   # OpenAI-style stringified arguments
            except (TypeError, ValueError):
                inner = None
        if isinstance(inner, dict) and isinstance(inner.get("command"), str):
            return inner["command"]
    fn = d.get("function")
    if isinstance(fn, dict):
        return _command_of(fn)
    return None


def walk_tool_commands(value):
    """Yield command strings from tool-call records only. Descends into
    structure but never into prose fields, and never treats a bare string
    as a command."""
    if isinstance(value, dict):
        if _is_tool_record(value):
            cmd = _command_of(value)
            if cmd:
                yield cmd
        for key, child in value.items():
            if key in PROSE_KEYS and isinstance(child, str):
                continue
            yield from walk_tool_commands(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_tool_commands(child)


def _local_path(cwd):
    """Codex 0.167 writes a CommandExecution's cwd as a file:// URL."""
    if cwd.startswith("file://"):
        return unquote(urlparse(cwd).path)
    return cwd


def find_cwd(value, fallback):
    if isinstance(value, dict):
        cwd = value.get("cwd")
        if isinstance(cwd, str) and cwd:
            return _local_path(cwd)
        for child in value.values():
            found = find_cwd(child, "")
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_cwd(child, "")
            if found:
                return found
    return fallback


def _executions(value):
    """Every Codex CommandExecution item inside a record."""
    if isinstance(value, dict):
        if value.get("type") == "CommandExecution":
            yield value
        for child in value.values():
            yield from _executions(child)
    elif isinstance(value, list):
        for child in value:
            yield from _executions(child)


def _started(record, item):
    """Epoch seconds the command started: the record's completion time less
    the command's duration. None when either is missing."""
    stamp, duration = record.get("timestamp"), item.get("duration")
    if not isinstance(stamp, str) or not isinstance(duration, dict):
        return None
    try:
        done = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()
        return done - float(duration.get("secs", 0)) - float(duration.get("nanos", 0)) / 1e9
    except (TypeError, ValueError):
        return None


def _load_core():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "bodhi-stop-hook-core.py")
    spec = importlib.util.spec_from_file_location("bodhi_stop_hook_core", path)
    if spec is None or spec.loader is None:
        return None
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    return core


def _changed_since(project, since):
    bdir = os.path.join(project, ".bodhi")
    try:
        return any(os.path.getmtime(os.path.join(bdir, name)) >= since
                   for name in os.listdir(bdir)
                   if os.path.isfile(os.path.join(bdir, name)))
    except OSError:
        return False


def script_touches(record, fallback_cwd, core):
    """(cwd, command) for each project a script's touch-state changed, when
    that script names no --project path the canonical hook can read."""
    for item in _executions(record):
        script = _command_of(item)
        if (not script or "bodhi-state" not in script or not TOUCH.search(script)
                or PROJECT_ARG.search(script)):
            continue
        started = _started(record, item)
        if started is None or core is None:
            continue
        cwd = _local_path(item.get("cwd") or "") or fallback_cwd
        verbs = "profile-add-project touch-state" if REGISTER.search(script) else "touch-state"
        for project in core.find_projects(core.configured_roots(cwd)):
            if _changed_since(project, started - START_SLACK_SECONDS):
                yield cwd, f'bodhi-state --project "{project}" {verbs}'


def transcript_records(path):
    if not path or not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            content = handle.read()
    except OSError:
        return []

    records = []
    for line in content.splitlines():
        if "bodhi-state" not in line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if records:
        return records
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else [parsed]


def normalized_commands(path, fallback_cwd):
    seen = set()
    normalized = []
    core = None
    for record in transcript_records(path):
        cwd = find_cwd(record, fallback_cwd)
        found = [(cwd, c) for c in walk_tool_commands(record)]
        if any(TOUCH.search(c) and not PROJECT_ARG.search(c) for _, c in found):
            try:
                core = core or _load_core()
            except Exception:
                core = None
            found += list(script_touches(record, fallback_cwd, core))
        for cwd, candidate in found:
            if "bodhi-state" not in candidate or "--project" not in candidate:
                continue
            key = (cwd, candidate)
            if key in seen:
                continue
            seen.add(key)
            normalized.append(
                {
                    "type": "assistant",
                    "cwd": cwd,
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Bash",
                                "input": {"command": candidate},
                            }
                        ]
                    },
                }
            )
    return normalized


def run_core(payload, transcript_path=None):
    root = os.path.dirname(os.path.abspath(__file__))
    core = os.path.join(root, "bodhi-stop-hook-core.py")
    if not os.path.isfile(core):
        return
    forwarded = dict(payload)
    if transcript_path:
        forwarded["transcript_path"] = transcript_path
    elif "transcript_path" in forwarded:
        forwarded["transcript_path"] = None
    try:
        result = subprocess.run(
            [sys.executable, core],
            input=json.dumps(forwarded),
            capture_output=True,
            text=True,
            timeout=25,
        )
    except (OSError, subprocess.SubprocessError):
        return
    if result.returncode == 0 and result.stdout.strip():
        print(result.stdout.strip())


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return
    records = normalized_commands(
        payload.get("transcript_path"), payload.get("cwd") or os.getcwd()
    )
    if not records:
        run_core(payload)
        return
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".jsonl", delete=False
    ) as handle:
        normalized_path = handle.name
        for record in records:
            handle.write(json.dumps(record) + "\n")
    try:
        run_core(payload, normalized_path)
    finally:
        try:
            os.unlink(normalized_path)
        except OSError:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    raise SystemExit(0)
