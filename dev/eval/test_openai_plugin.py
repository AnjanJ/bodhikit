#!/usr/bin/env python3
"""Black-box checks for the generated Codex and ChatGPT BodhiKit package."""

from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "platforms" / "openai" / "build_plugin.py"
CLAUDE_SURFACES = (
    REPO / ".claude-plugin",
    REPO / "skills",
    REPO / "agents",
    REPO / "hooks",
    REPO / "scripts",
    REPO / "rules",
    REPO / "settings.json",
)
PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"ok    {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def surface_digest():
    digest = hashlib.sha256()
    files = []
    for surface in CLAUDE_SURFACES:
        if surface.is_file():
            files.append(surface)
        elif surface.is_dir():
            files.extend(path for path in surface.rglob("*") if path.is_file())
    for path in sorted(files):
        digest.update(str(path.relative_to(REPO)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def source_skill_names(user_invocable):
    names = set()
    needle = f"user-invocable: {'true' if user_invocable else 'false'}"
    for source in (REPO / "skills").glob("*/SKILL.md"):
        if needle in source.read_text(encoding="utf-8").split("---", 2)[1]:
            names.add(source.parent.name)
    return names


def run_hook(script, payload, env=None):
    hook_env = os.environ.copy()
    hook_env["BODHI_TODAY"] = datetime.date.today().isoformat()
    if env:
        hook_env.update(env)
    result = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=60,
        env=hook_env,
    )
    check(f"{script.name}: exits zero", result.returncode == 0, result.stderr[-300:])
    return result.stdout.strip()


def make_project(root, name, spaced_review):
    project = root / "learningWithBodhi" / name
    bodhi = project / ".bodhi"
    bodhi.mkdir(parents=True)
    (bodhi / "state.json").write_text(
        json.dumps(
            {
                "version": 2,
                "projectName": name,
                "currentPhase": 1,
                "currentModule": "A",
                "sessionDates": [],
            }
        ),
        encoding="utf-8",
    )
    (bodhi / "spaced-review.json").write_text(
        json.dumps(spaced_review), encoding="utf-8"
    )
    return project


def test_build_and_structure():
    before = surface_digest()
    with tempfile.TemporaryDirectory(prefix="bodhikit-openai-test-") as temp:
        temp_path = Path(temp)
        output = temp_path / "bodhikit"
        archive = temp_path / "bodhikit-openai.zip"
        result = subprocess.run(
            [
                sys.executable,
                str(BUILDER),
                "--output",
                str(output),
                "--archive",
                str(archive),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        check("build: exits zero", result.returncode == 0, result.stderr[-500:])
        try:
            summary = json.loads(result.stdout)
        except json.JSONDecodeError:
            summary = {}
        check("build: reports 18 user skills", summary.get("skills") == 18, summary)
        check(
            "build: reports 18 knowledge references",
            summary.get("knowledgeReferences") == 18,
            summary,
        )
        check("build: reports 4 role procedures", summary.get("roleProcedures") == 4, summary)

        manifest = json.loads(
            (output / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        claude_manifest = json.loads(
            (REPO / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        check("manifest: native OpenAI name", manifest.get("name") == "bodhikit", manifest)
        check(
            "manifest: version follows Claude source",
            manifest.get("version") == claude_manifest.get("version"),
            manifest,
        )
        interface = manifest.get("interface", {})
        marketplace_assets = (
            "composerIcon",
            "logo",
            "logoDark",
        )
        check(
            "manifest: marketplace policies and assets are packaged",
            interface.get("privacyPolicyURL", "").startswith("https://")
            and interface.get("termsOfServiceURL", "").startswith("https://")
            and all(
                (output / interface.get(key, "")).is_file()
                for key in marketplace_assets
            ),
            interface,
        )

        generated_skills = {path.name for path in (output / "skills").iterdir() if path.is_dir()}
        generated_knowledge = {
            path.stem for path in (output / "references" / "knowledge").glob("*.md")
        }
        generated_roles = {
            path.stem for path in (output / "references" / "roles").glob("*.md")
        }
        check(
            "skills: all learner workflows converted",
            generated_skills == source_skill_names(True),
            sorted(generated_skills),
        )
        check(
            "skills: all knowledge bases preserved",
            generated_knowledge == source_skill_names(False),
            sorted(generated_knowledge),
        )
        check(
            "skills: all Claude agents preserved as procedures",
            generated_roles == {path.stem for path in (REPO / "agents").glob("*.md")},
            sorted(generated_roles),
        )

        forbidden = (
            "Agent tool",
            "Skill tool",
            "/bodhikit:",
            "$ARGUMENTS",
            "CLAUDE_PLUGIN_ROOT",
            "model: sonnet",
            "model: haiku",
            "model: opus",
            "Claude Code",
        )
        text_files = [
            path
            for path in output.rglob("*")
            if path.is_file() and path.suffix in {".md", ".json", ".py"}
        ]
        leftovers = {
            token: [str(path.relative_to(output)) for path in text_files if token in path.read_text(encoding="utf-8")]
            for token in forbidden
        }
        leftovers = {token: paths for token, paths in leftovers.items() if paths}
        check("conversion: no source-platform runtime tokens", not leftovers, leftovers)
        check(
            "conversion: no compiled or cache artifacts",
            not any(path.name == "__pycache__" or path.suffix == ".pyc" for path in output.rglob("*")),
        )
        check(
            "state: deterministic engine copied byte-for-byte",
            (output / "scripts" / "bodhi-state").read_bytes()
            == (REPO / "scripts" / "bodhi-state").read_bytes(),
        )
        runtime = (output / "references" / "openai-runtime.md").read_text(encoding="utf-8")
        check(
            "ChatGPT: core workflow is hook-independent",
            "conversation-only mode" in runtime
            and "Never make a lifecycle hook a prerequisite" in runtime,
        )
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
        check(
            "archive: has one top-level plugin directory",
            bool(names) and all(name.startswith("bodhikit/") for name in names),
            names[:5],
        )
        check(
            "archive: includes native manifest",
            "bodhikit/.codex-plugin/plugin.json" in names,
        )
        check(
            "archive: includes marketplace logo",
            "bodhikit/assets/bodhikit-icon.png" in names,
        )

        test_hooks(output, temp_path)

    check("isolation: build does not modify Claude surfaces", surface_digest() == before)


def test_hooks(output, temp_path):
    session_hook = output / "scripts" / "bodhi-session-context.py"
    stop_hook = output / "scripts" / "bodhi-stop-hook.py"
    today = datetime.date.today().isoformat()

    project_root = temp_path / "session-project"
    (project_root / ".bodhi").mkdir(parents=True)
    session_output = run_hook(
        session_hook,
        {
            "session_id": "codex-session",
            "cwd": str(project_root),
            "hook_event_name": "SessionStart",
            "model": "test-model",
        },
    )
    try:
        session_payload = json.loads(session_output)
    except json.JSONDecodeError:
        session_payload = {}
    specific = session_payload.get("hookSpecificOutput", {})
    check("SessionStart: emits Codex event name", specific.get("hookEventName") == "SessionStart", specific)
    check(
        "SessionStart: injects learner-content safeguard",
        "learner content" in specific.get("additionalContext", "").lower(),
        specific,
    )

    studied = {
        "version": 3,
        "sessionHistory": [],
        "concepts": [
            {
                "name": "Joins",
                "module": "A",
                "box": 2,
                "bloomLevel": 3,
                "feynmanPassed": False,
                "consecutiveCorrectAtL4Plus": 0,
                "nextReview": today,
                "lastReviewed": today,
                "reviewHistory": [
                    {
                        "date": today,
                        "result": "correct",
                        "bloomLevel": 3,
                        "source": "teach",
                    }
                ],
            }
        ],
    }
    root = temp_path / "codex-stop"
    project = make_project(root, "sql", studied)
    transcript = temp_path / "codex-transcript.jsonl"
    command = (
        f'"{output / "scripts" / "bodhi-state"}" --project "{project}" '
        'touch-state --activity "done"'
    )
    transcript.write_text(
        json.dumps(
            {
                "cwd": str(root),
                "event": {"tool_name": "Bash", "tool_input": {"command": command}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    stop_output = run_hook(
        stop_hook,
        {
            "session_id": "codex-session",
            "turn_id": "turn-1",
            "cwd": str(root),
            "hook_event_name": "Stop",
            "stop_hook_active": False,
            "last_assistant_message": "Finished the lesson.",
            "transcript_path": str(transcript),
        },
    )
    try:
        decision = json.loads(stop_output)
    except json.JSONDecodeError:
        decision = {}
    check(
        "Stop: Codex-shaped transcript triggers revision continuation",
        decision.get("decision") == "block" and "revision sheet" in decision.get("reason", ""),
        stop_output[:300],
    )
    revision = project / "revision" / f"{today}-joins.md"
    revision.parent.mkdir()
    revision.write_text("# Revision — Joins\n", encoding="utf-8")
    stop_output = run_hook(
        stop_hook,
        {
            "cwd": str(root),
            "hook_event_name": "Stop",
            "transcript_path": str(transcript),
        },
    )
    check("Stop: completed revision sheet is silent", stop_output == "", stop_output[:200])

    broken_root = temp_path / "codex-broken"
    broken = {
        "version": 3,
        "sessionHistory": [],
        "concepts": [
            {
                "name": "Joins",
                "module": "A",
                "box": "three",
                "bloomLevel": 0,
                "feynmanPassed": False,
                "consecutiveCorrectAtL4Plus": 0,
                "nextReview": today,
                "reviewHistory": [],
            }
        ],
    }
    broken_project = make_project(broken_root, "sql", broken)
    stop_output = run_hook(
        stop_hook,
        {"cwd": str(broken_root), "hook_event_name": "Stop", "transcript_path": None},
    )
    try:
        decision = json.loads(stop_output)
    except json.JSONDecodeError:
        decision = {}
    check(
        "Stop: schema verification works without transcript parsing",
        decision.get("decision") == "block"
        and str(broken_project) in decision.get("reason", "")
        and "box" in decision.get("reason", ""),
        stop_output[:300],
    )


def main():
    test_build_and_structure()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
