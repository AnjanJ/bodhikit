#!/usr/bin/env python3
"""Black-box checks for the Claude Cowork `.plugin` package (learn-anything).

learn-anything/REQ-37: the build produces a Cowork package from the same
source tree as the Claude Code plugin. This builds it and reads the zip:
the plugin's surfaces are present and byte-identical to the source, every
`${CLAUDE_PLUGIN_ROOT}` path the package names resolves inside it, and no
development material ships. Whether it runs in Cowork is the manual probe's
question (docs/cowork-probe.md), not this test's.

Run: python3 dev/eval/test_cowork_plugin.py
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "platforms" / "cowork" / "build_plugin.py"
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


def source_files(top):
    return {p.relative_to(REPO).as_posix() for p in (REPO / top).rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith((".pyc", ".lock"))
            and p.name != ".DS_Store"}


def test_package_contents():
    with tempfile.TemporaryDirectory(prefix="bodhikit-cowork-test-") as temp:
        archive = Path(temp) / "bodhikit.plugin"
        result = subprocess.run([sys.executable, str(BUILDER), "--archive", str(archive)],
                                capture_output=True, text=True, timeout=60)
        check("build: exits zero", result.returncode == 0, result.stderr[-400:])
        summary = json.loads(result.stdout or "{}")
        with zipfile.ZipFile(archive) as bundle:
            names = set(bundle.namelist())
            manifest = json.loads(bundle.read(".claude-plugin/plugin.json"))
            source_manifest = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
            check("manifest: at the archive root, the source plugin.json",
                  manifest == source_manifest and manifest.get("name") == "bodhikit",
                  manifest)
            check("build: summary names the plugin and counts",
                  summary.get("name") == "bodhikit" and summary.get("version") == manifest["version"]
                  and summary.get("skills") == len([n for n in names if re.fullmatch(r"skills/[^/]+/SKILL\.md", n)])
                  and summary.get("agents") == 4, summary)
            for top in ("skills", "agents", "hooks", "scripts", "rules"):
                want = source_files(top)
                check(f"surfaces: every {top}/ file ships", want <= names,
                      sorted(want - names)[:5])
                same = all(bundle.read(n) == (REPO / n).read_bytes() for n in want & names)
                check(f"surfaces: {top}/ is byte-identical to the source", same)
            info = bundle.getinfo("scripts/bodhi-state")
            check("scripts: bodhi-state stays executable",
                  bool((info.external_attr >> 16) & 0o111))
            hooks = json.loads(bundle.read("hooks/hooks.json"))
            check("hooks: SessionStart and Stop, both through ${CLAUDE_PLUGIN_ROOT}",
                  {"SessionStart", "Stop"} <= set(hooks.get("hooks", {}))
                  and all("${CLAUDE_PLUGIN_ROOT}/scripts/" in h["command"]
                          for event in hooks["hooks"].values() for group in event
                          for h in group["hooks"]))
            unresolved = []
            for n in sorted(names):
                if not n.endswith((".md", ".json")):
                    continue
                text = bundle.read(n).decode("utf-8")
                for rel in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)", text):
                    rel = rel.rstrip(".,;:)")
                    if rel not in names and not any(x.startswith(rel.rstrip("/") + "/") for x in names):
                        unresolved.append(f"{n} -> {rel}")
            check("paths: every ${CLAUDE_PLUGIN_ROOT}/ path named in the package resolves in it",
                  not unresolved, unresolved[:6])
            dev_only = sorted(n for n in names if n.split("/")[0] in
                              ("dev", "docs", "platforms", ".shipkit", "analysis", "dist",
                               ".github", ".git") or "__pycache__" in n or n.endswith(".pyc"))
            check("package: no dev/, docs/, platforms/, .shipkit/ or caches", not dev_only,
                  dev_only[:6])
            check("package: no marketplace manifest (a .plugin is installed directly)",
                  ".claude-plugin/marketplace.json" not in names)


def main():
    test_package_contents()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
