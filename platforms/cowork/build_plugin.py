#!/usr/bin/env python3
"""Build BodhiKit as a Claude Cowork `.plugin` package (learn-anything).

Cowork installs a plugin from a `.plugin` file: a zip whose root is the
plugin directory, with `.claude-plugin/plugin.json`, `skills/`, `agents/`
and `hooks/hooks.json` in the same schema Claude Code reads, and
`${CLAUDE_PLUGIN_ROOT}` for intra-plugin paths. That is BodhiKit's layout
already, so this copies the canonical tree as it is: no file is rewritten.

    python3 platforms/cowork/build_plugin.py --archive dist/bodhikit.plugin

Whether `python3`, the hooks and the working-folder markers hold inside
Cowork is unverified until the manual probe in docs/cowork-probe.md passes;
build the package, but make no claim of support before that.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[2]

# What an installed plugin loads, plus what it executes and the files a
# reader of the package needs. Nothing under dev/, docs/, platforms/,
# .shipkit/ or analysis/ ships.
PLUGIN_DIRS = ("skills", "agents", "hooks", "scripts", "rules")
PLUGIN_FILES = (".claude-plugin/plugin.json", "settings.json", "README.md", "LICENSE")
SKIP_NAMES = {".DS_Store", "__pycache__"}
SKIP_SUFFIXES = (".pyc", ".lock")


def package_files() -> list[Path]:
    """Repo-relative paths of every file the package carries, sorted."""
    files = [Path(f) for f in PLUGIN_FILES if (REPO_ROOT / f).is_file()]
    for d in PLUGIN_DIRS:
        for path in sorted((REPO_ROOT / d).rglob("*")):
            rel = path.relative_to(REPO_ROOT)
            if (path.is_file() and not SKIP_NAMES.intersection(rel.parts)
                    and not path.name.endswith(SKIP_SUFFIXES)):
                files.append(rel)
    return sorted(files)


def create_archive(archive: Path) -> dict[str, object]:
    archive = archive.resolve()
    archive.parent.mkdir(parents=True, exist_ok=True)
    files = package_files()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for rel in files:
            # write() keeps the file's mode, so bodhi-state stays executable:
            # skills invoke it directly as "${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state".
            bundle.write(REPO_ROOT / rel, rel.as_posix())
    manifest = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    return {
        "archive": os.path.relpath(archive, Path.cwd()),
        "name": manifest["name"],
        "version": manifest["version"],
        "files": len(files),
        "skills": sum(1 for f in files if f.parts[0] == "skills" and f.name == "SKILL.md"),
        "agents": sum(1 for f in files if f.parts[0] == "agents" and f.suffix == ".md"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--archive", type=Path, default=REPO_ROOT / "dist" / "bodhikit.plugin",
                        help="the .plugin file to write (default: dist/bodhikit.plugin)")
    return parser.parse_args()


def main() -> int:
    print(json.dumps(create_archive(parse_args().archive), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
