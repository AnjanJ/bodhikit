#!/usr/bin/env python3
"""Codex Stop adapter for BodhiKit's canonical schema-safety hook.

Codex exposes a transcript path but does not guarantee the transcript's
internal format. This adapter recursively finds command strings in JSON or
JSONL records and emits a minimal normalized transcript for the canonical
BodhiKit hook. If normalization is impossible, schema verification still runs
and revision-sheet enforcement fails open for that turn.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)


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
        for candidate in walk_strings(record):
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
