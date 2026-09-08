#!/usr/bin/env python3
"""Codex Stop adapter for BodhiKit's canonical schema-safety hook.

Codex exposes a transcript path but does not guarantee the transcript's
internal format. This adapter finds TOOL-CALL records — a dict carrying a
tool marker (`tool_name`, `name`, `function`, or a `type` of tool_use /
tool_call / function_call / tool) whose `command` (or `tool_input.command`,
`input.command`, `arguments.command`) is a string — and emits a minimal
normalized transcript for the canonical BodhiKit hook. Prose is never
inspected: an assistant paragraph that *mentions* a bodhi-state command is
not evidence the command ran (review finding 8, 2026-09-07 — a read-only
discussion used to block the stop with a revision-sheet demand). If no
tool-call record can be recognised, schema verification still runs and
revision-sheet enforcement fails open for that turn.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile


TOOL_MARKER_KEYS = ("tool_name", "name", "function")
TOOL_TYPES = {"tool_use", "tool_call", "function_call", "tool"}
COMMAND_CONTAINERS = ("tool_input", "input", "arguments", "args", "parameters")
PROSE_KEYS = {"content", "text", "message", "output", "result", "stdout",
              "stderr", "last_assistant_message", "reasoning"}


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


def find_cwd(value, fallback):
    if isinstance(value, dict):
        cwd = value.get("cwd")
        if isinstance(cwd, str) and cwd:
            return cwd
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
    for record in transcript_records(path):
        cwd = find_cwd(record, fallback_cwd)
        for candidate in walk_tool_commands(record):
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
