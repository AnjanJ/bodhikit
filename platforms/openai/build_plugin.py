#!/usr/bin/env python3
"""Build the OpenAI BodhiKit package from the Claude-compatible source tree.

The existing Claude plugin remains the canonical source. This builder creates
an isolated OpenAI package with Agent Skills frontmatter, portable role
procedures, progressively loaded knowledge references, and provider-neutral
invocation language.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import zipfile


PLATFORM_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PLATFORM_ROOT.parent.parent
TEMPLATE_ROOT = PLATFORM_ROOT / "bodhikit"
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "openai" / "bodhikit"
BUILD_MARKER = ".bodhikit-openai-build.json"

KB_SENTENCE = (
    "**Knowledge bases are skills.** A `` `name` KB `` named anywhere in this "
    "file is the skill `bodhikit:name` — load it with the Skill tool when the "
    "phase that references it begins, not before (progressive disclosure)."
)
PORTABLE_KB_SENTENCE = (
    "**Knowledge bases are packaged references.** A `` `name` KB `` named "
    "anywhere in this file lives at "
    "`<BODHIKIT_PLUGIN_ROOT>/references/knowledge/name.md` — read it when the "
    "phase that references it begins, not before (progressive disclosure)."
)


def split_frontmatter(text: str, source: Path) -> tuple[list[str], str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{source}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{source}: unterminated YAML frontmatter")
    return text[4:end].splitlines(), text[end + 5 :]


def field(frontmatter: list[str], key: str, source: Path) -> str:
    prefix = f"{key}:"
    for line in frontmatter:
        if line.startswith(prefix):
            value = line[len(prefix) :].strip()
            if value:
                return value
    raise ValueError(f"{source}: frontmatter missing {key}")


def is_user_skill(frontmatter: list[str]) -> bool:
    return any(line.strip() == "user-invocable: true" for line in frontmatter)


def command_span(name: str, raw_args: str) -> str:
    args = raw_args.strip()
    if args:
        return f"`{name}` skill with request context `{args}`"
    return f"`{name}` skill"


def neutralize(text: str, user_skill_names: set[str]) -> str:
    text = text.replace(KB_SENTENCE, PORTABLE_KB_SENTENCE)
    text = text.replace("${CLAUDE_PLUGIN_ROOT}", "<BODHIKIT_PLUGIN_ROOT>")
    text = text.replace("$ARGUMENTS", "request input")
    text = re.sub(
        r"If `CLAUDE_PLUGIN_ROOT` is not set in the Bash environment, locate the "
        r"script once with `find ~/.claude/plugins[^`]+` \(or the repo checkout's "
        r"`scripts/bodhi-state` when running via `--plugin-dir`\)\.",
        "Resolve `<BODHIKIT_PLUGIN_ROOT>` from the installed skill path as "
        "described in the OpenAI runtime adapter. When running from a repository "
        "checkout, use its `scripts/bodhi-state` executable.",
        text,
    )
    text = text.replace("CLAUDE_PLUGIN_ROOT", "BODHIKIT_PLUGIN_ROOT")
    text = text.replace("~/.claude/plugins", "the installed plugin package")

    role_patterns = (
        r"You MUST use the Agent tool to launch the `([a-z-]+)` agent",
        r"You MUST use the Agent tool to launch `([a-z-]+)`",
        r"You MUST use the Agent tool to launch the `([a-z-]+)`",
    )
    for pattern in role_patterns:
        text = re.sub(
            pattern,
            lambda match: (
                "You MUST apply the "
                f"`{match.group(1)}` portable role procedure"
            ),
            text,
        )
    text = re.sub(
        r"use the Agent tool to launch the `([a-z-]+)` agent",
        lambda match: f"apply the `{match.group(1)}` portable role procedure",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"the `([a-z-]+)` agent",
        lambda match: f"the `{match.group(1)}` role procedure",
        text,
    )
    text = text.replace("Agent tool", "portable role-procedure mechanism")
    text = text.replace("Skill tool", "skill/reference loader")
    text = text.replace("If the agent fails or hits its turn limit", "If delegation is unavailable or incomplete")
    text = text.replace("If the agent fails", "If delegation is unavailable")
    text = text.replace("agent invocation", "role-procedure step")
    text = text.replace("The agent returns", "The procedure returns")
    text = text.replace("The agent reads", "The procedure reads")
    text = text.replace("The agent will", "The procedure will")
    text = re.sub(r"\bAgent\b", "Role procedure", text)
    text = re.sub(r"\bagents\b", "role procedures", text)
    text = re.sub(r"\bagent\b", "role procedure", text)

    text = re.sub(
        r"`/bodhikit:([a-z0-9-]+)([^`]*)`",
        lambda match: command_span(match.group(1), match.group(2)),
        text,
    )
    if user_skill_names:
        names = "|".join(sorted(map(re.escape, user_skill_names), key=len, reverse=True))
        text = re.sub(
            rf"`/({names})([^`]*)`",
            lambda match: command_span(match.group(1), match.group(2)),
            text,
        )
        text = re.sub(
            rf"(?<![\w/])/({names})\b",
            lambda match: f"`{match.group(1)}` skill",
            text,
        )
    text = re.sub(
        r"/bodhikit:([a-z0-9-]+)\b",
        lambda match: f"`{match.group(1)}` skill",
        text,
    )
    text = text.replace("skill skill", "skill")
    text = text.replace(
        "the `find the installed plugin package` lookup",
        "the package-relative lookup",
    )

    text = text.replace("Read the files using the Read tool", "Read the files")
    text = text.replace("using the Read tool", "by reading the relevant file")
    text = text.replace("with the Write tool", "by writing it")
    text = text.replace("Claude Code", "the host")
    text = text.replace("tells Claude", "tells the model")

    text = text.replace(
        "A session that studied something does not end without one — the Stop hook checks.",
        "A session that studied something should not end without one. Codex may "
        "enforce this with the optional Stop hook; ChatGPT must complete it explicitly.",
    )
    text = text.replace(
        "The Stop hook will not let this session end without it once its bookkeeping "
        "(`touch-state`) has run.",
        "Codex may enforce this with the optional Stop hook after `touch-state`; "
        "ChatGPT must complete it explicitly before ending.",
    )
    return text


def write_text(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def prepare_output(output: Path) -> None:
    resolved = output.resolve()
    forbidden = {
        Path("/").resolve(),
        Path.home().resolve(),
        REPO_ROOT.resolve(),
        PLATFORM_ROOT.resolve(),
        TEMPLATE_ROOT.resolve(),
    }
    if resolved in forbidden:
        raise ValueError(f"refusing unsafe output path: {resolved}")
    if output.exists():
        marker = output / BUILD_MARKER
        if not marker.is_file():
            raise ValueError(
                f"refusing to replace {output}: {BUILD_MARKER} is missing"
            )
        shutil.rmtree(output)
    output.mkdir(parents=True)
    write_text(
        output / BUILD_MARKER,
        json.dumps({"generator": "platforms/openai/build_plugin.py"}, indent=2)
        + "\n",
    )


def copy_transformed_tree(
    source: Path, destination: Path, user_skill_names: set[str]
) -> None:
    for item in sorted(source.rglob("*")):
        relative = item.relative_to(source)
        target = destination / relative
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif item.suffix.lower() in {".md", ".txt"}:
            write_text(
                target,
                neutralize(item.read_text(encoding="utf-8"), user_skill_names),
            )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def build(output: Path) -> dict[str, int | str]:
    prepare_output(output)
    shutil.copytree(
        TEMPLATE_ROOT,
        output,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )

    source_manifest = json.loads(
        (REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    manifest_path = output / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = source_manifest["version"]
    write_text(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    skills_root = REPO_ROOT / "skills"
    skill_records: list[tuple[str, Path, list[str], str, bool]] = []
    for source in sorted(skills_root.glob("*/SKILL.md")):
        frontmatter, body = split_frontmatter(source.read_text(encoding="utf-8"), source)
        name = source.parent.name
        skill_records.append((name, source, frontmatter, body, is_user_skill(frontmatter)))

    user_skill_names = {name for name, _, _, _, user in skill_records if user}
    knowledge_names = {name for name, _, _, _, user in skill_records if not user}

    generated_skills = output / "skills"
    if generated_skills.exists():
        shutil.rmtree(generated_skills)
    generated_skills.mkdir(parents=True)

    runtime_notice = (
        "## OpenAI runtime\n\n"
        "Before using state, a knowledge base, a role procedure, or another "
        "BodhiKit skill, read the [OpenAI runtime adapter]"
        "(../../references/openai-runtime.md). Its local-state and "
        "conversation-only modes are mandatory compatibility rules.\n\n"
    )

    for name, source, frontmatter, body, user in skill_records:
        description = field(frontmatter, "description", source)
        if user:
            rendered = (
                "---\n"
                f"name: {name}\n"
                f"description: {description}\n"
                "---\n\n"
                + runtime_notice
                + neutralize(body, user_skill_names).lstrip()
            )
            destination = generated_skills / name
            write_text(destination / "SKILL.md", rendered)
            source_resources = source.parent / "references"
            if source_resources.is_dir():
                copy_transformed_tree(
                    source_resources, destination / "references", user_skill_names
                )
        else:
            rendered = (
                "<!-- Generated from "
                f"skills/{name}/SKILL.md; edit the canonical source. -->\n\n"
                + neutralize(body, user_skill_names).lstrip()
            )
            write_text(output / "references" / "knowledge" / f"{name}.md", rendered)

    roles_dir = output / "references" / "roles"
    for source in sorted((REPO_ROOT / "agents").glob("*.md")):
        _, body = split_frontmatter(source.read_text(encoding="utf-8"), source)
        role_name = source.stem
        rendered = (
            f"# Portable role procedure: {role_name}\n\n"
            "This procedure preserves the corresponding Claude agent's behavior. "
            "Apply it directly, or delegate it only when the host supports "
            "subagents.\n\n"
            + neutralize(body, user_skill_names).lstrip()
        )
        write_text(roles_dir / source.name, rendered)

    state_script = output / "scripts" / "bodhi-state"
    shutil.copy2(REPO_ROOT / "scripts" / "bodhi-state", state_script)
    state_script.chmod(state_script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    stop_core = output / "scripts" / "bodhi-stop-hook-core.py"
    stop_core_text = (REPO_ROOT / "scripts" / "bodhi-stop-hook.py").read_text(
        encoding="utf-8"
    )
    stop_core_text = stop_core_text.replace("tells Claude", "tells the model")
    write_text(stop_core, stop_core_text, mode=0o755)
    copy_transformed_tree(REPO_ROOT / "rules", output / "rules", user_skill_names)

    return {
        "output": str(output),
        "version": source_manifest["version"],
        "skills": len(user_skill_names),
        "knowledgeReferences": len(knowledge_names),
        "roleProcedures": len(list((REPO_ROOT / "agents").glob("*.md"))),
    }


def create_archive(output: Path, archive: Path) -> None:
    archive = archive.resolve()
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for item in sorted(output.rglob("*")):
            if item.is_file() and item.resolve() != archive:
                bundle.write(item, Path("bodhikit") / item.relative_to(output))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"generated plugin directory (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        help="optional ZIP path; the archive contains one top-level bodhikit directory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = build(args.output)
        if args.archive:
            create_archive(args.output, args.archive)
            summary["archive"] = str(args.archive.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
