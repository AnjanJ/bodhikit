#!/usr/bin/env python3
"""Checks for the maintainer's guide-writing skill (spec write-guide).

`dev/guide-writer/` is a Claude Code skill that writes personalised guides to
using BodhiKit in Claude and ChatGPT. It is a maintainer tool: it never ships,
and it runs only when typed. What a model does during a run (asking, verifying,
keeping the claim ledger) is checked by hand on a real run, per the spec; this
suite checks what can be checked without one.

Run: python3 dev/eval/test_guide_writer.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "dev" / "guide-writer"
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


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def t_output_is_ignored():
    """write-guide/REQ-4: guides hold personal details, and the repo is public."""
    result = git("check-ignore", "-q", "output/any-guide.pdf")
    check("REQ-4 output/ is ignored by git", result.returncode == 0,
          "add `output/` to .gitignore")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    block = text.split("\n---\n", 1)[0][4:]
    fields = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"')
    return fields


def t_typed_only():
    """write-guide/REQ-1: nothing in context until /write-guide is typed."""
    skill = SKILL / "SKILL.md"
    check("REQ-1 dev/guide-writer/SKILL.md exists", skill.is_file())
    if not skill.is_file():
        return
    fields = frontmatter(skill)
    check("REQ-1 frontmatter sets disable-model-invocation: true",
          fields.get("disable-model-invocation") == "true", fields)
    check("REQ-1 frontmatter names the skill write-guide",
          fields.get("name") == "write-guide", fields.get("name"))
    check("REQ-1 frontmatter has a description", bool(fields.get("description")))


def t_not_in_any_package():
    """write-guide/REQ-2: a maintainer tool never reaches a learner."""
    cowork = load_module("cowork_build", REPO / "platforms" / "cowork" / "build_plugin.py")
    shipped = [p.as_posix() for p in cowork.package_files()]
    leaked = [p for p in shipped if "guide-writer" in p or p.startswith("dev/")]
    check("REQ-2 Cowork package carries nothing from dev/guide-writer/", not leaked, leaked[:4])
    openai = load_module("openai_build", REPO / "platforms" / "openai" / "build_plugin.py")
    with tempfile.TemporaryDirectory(prefix="bodhikit-gw-test-") as temp:
        out = Path(temp) / "bodhikit"
        openai.build(out)
        names = [p.relative_to(out).as_posix() for p in out.rglob("*")]
        leaked = [n for n in names if "guide-writer" in n or "write-guide" in n]
        check("REQ-2 OpenAI package carries nothing from dev/guide-writer/", not leaked, leaked[:4])


def learner_commands():
    return {f.parent.name for f in sorted((REPO / "skills").glob("*/SKILL.md"))
            if re.search(r"^user-invocable: true$", f.read_text(encoding="utf-8"), re.M)}


def t_commands_match_skills():
    """write-guide/REQ-9: one entry per learner command, no more, no fewer."""
    ref = SKILL / "references" / "commands.md"
    check("REQ-9 references/commands.md exists", ref.is_file())
    if not ref.is_file():
        return
    listed = re.findall(r"^### ([a-z][a-z-]*)\s*$", ref.read_text(encoding="utf-8"), re.M)
    skills = learner_commands()
    check("REQ-9 no command listed twice", len(listed) == len(set(listed)),
          sorted(n for n in set(listed) if listed.count(n) > 1))
    check("REQ-9 every learner command has an entry", not skills - set(listed),
          sorted(skills - set(listed)))
    check("REQ-9 no entry for a command that does not exist", not set(listed) - skills,
          sorted(set(listed) - skills))


def t_facts_dated_and_sourced():
    """write-guide/REQ-11: every platform fact can be re-checked at its source."""
    ref = SKILL / "references" / "platform-facts.md"
    check("REQ-11 references/platform-facts.md exists", ref.is_file())
    if not ref.is_file():
        return
    entries = re.split(r"^### ", ref.read_text(encoding="utf-8"), flags=re.M)[1:]
    check("REQ-11 platform-facts.md has entries", len(entries) > 0)
    unsourced = [e.splitlines()[0] for e in entries
                 if not re.search(r"^- Source: \S+", e, re.M)]
    undated = [e.splitlines()[0] for e in entries
               if not re.search(r"^- Checked: \d{4}-\d{2}-\d{2}\b", e, re.M)]
    unstated = [e.splitlines()[0] for e in entries
                if not re.search(r"^- Status: (verified|not verified)\b", e, re.M)]
    check("REQ-11 every entry names its source", not unsourced, unsourced[:4])
    check("REQ-11 every entry has a checked date (YYYY-MM-DD)", not undated, undated[:4])
    check("REQ-11 every entry says verified or not verified", not unstated, unstated[:4])


REFERENCED_DIRS = ("references/", "scripts/")


def t_referenced_files_exist():
    """Every file SKILL.md tells the model to load or run is there."""
    skill = SKILL / "SKILL.md"
    named = sorted(set(re.findall(r"\$\{CLAUDE_SKILL_DIR\}/([A-Za-z0-9_./-]+)",
                                  skill.read_text(encoding="utf-8"))))
    named = [n.rstrip(".,;:`)") for n in named]
    named = [n for n in named if n.startswith(REFERENCED_DIRS)]
    check("SKILL.md names its reference files", len(named) > 0)
    missing = [n for n in named if not (SKILL / n).is_file()]
    check("every reference file SKILL.md names exists", not missing, missing)


RENDER = SKILL / "scripts" / "render.sh"
TOOLS = ("weasyprint", "pandoc", "pdftoppm", "magick")
SAMPLE = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>t</title></head><body>
<h1>Sample guide</h1>
<div class="prompt">@BodhiKit Help me learn sample-subject-xyz.</div>
<table><thead><tr><th>Day</th><th>What</th></tr></thead>
<tr><td>Monday</td><td>row-one-lesson</td></tr><tr><td>Tuesday</td><td>row-two-review</td></tr></table>
</body></html>"""


def render(html, name, env=None):
    return subprocess.run(["bash", str(RENDER), str(html), name], capture_output=True,
                          text=True, timeout=180, env=env)


def t_render_refuses_repo():
    """write-guide/REQ-20: a guide with personal details never lands in the repo."""
    check("REQ-20 scripts/render.sh exists", RENDER.is_file())
    if not RENDER.is_file():
        return
    inside = REPO / "output" / "write-guide-test"
    inside.mkdir(parents=True, exist_ok=True)
    try:
        (inside / "guide.html").write_text(SAMPLE, encoding="utf-8")
        result = render(inside / "guide.html", "Refused")
        check("REQ-20 render.sh refuses a folder inside the repository", result.returncode != 0,
              result.stdout[-200:])
        check("REQ-20 the refusal says why", "inside the repository" in result.stderr,
              result.stderr[-200:])
        check("REQ-20 nothing was written there",
              not (inside / "Refused.pdf").exists() and not (inside / "Refused.docx").exists())
    finally:
        shutil.rmtree(inside, ignore_errors=True)


def t_render_names_missing_tool():
    """write-guide/REQ-21: a missing tool is named, not a stack trace."""
    if not RENDER.is_file():
        return
    with tempfile.TemporaryDirectory(prefix="bodhikit-gw-render-") as temp:
        html = Path(temp) / "guide.html"
        html.write_text(SAMPLE, encoding="utf-8")
        bare = {"PATH": "/usr/bin:/bin", "HOME": str(Path.home()), "TMPDIR": temp}
        hidden = [t for t in TOOLS if not any(Path(d, t).exists() for d in ("/usr/bin", "/bin"))]
        result = render(html, "Missing", env=bare)
        check("REQ-21 render.sh exits non-zero when a tool is missing", result.returncode != 0)
        check("REQ-21 it names each missing tool",
              hidden and all(t in result.stderr for t in hidden), result.stderr[-300:])


def t_render_outputs():
    """write-guide/REQ-19: PDF and DOCX beside the HTML, and a contact sheet."""
    if not RENDER.is_file():
        return
    missing = [t for t in TOOLS if shutil.which(t) is None]
    if missing:
        print(f"skip  REQ-19 render outputs: {', '.join(missing)} not installed")
        return
    with tempfile.TemporaryDirectory(prefix="bodhikit-gw-render-") as temp:
        html = Path(temp) / "guide.html"
        html.write_text(SAMPLE, encoding="utf-8")
        env = {**__import__("os").environ, "TMPDIR": temp}
        result = render(html, "Sample-Guide", env=env)
        check("REQ-19 render.sh exits zero", result.returncode == 0, result.stderr[-300:])
        pdf, docx = Path(temp) / "Sample-Guide.pdf", Path(temp) / "Sample-Guide.docx"
        check("REQ-19 the PDF is beside the HTML", pdf.is_file() and pdf.stat().st_size > 0)
        check("REQ-19 the DOCX is beside the HTML", docx.is_file() and docx.stat().st_size > 0)
        if docx.is_file():
            with zipfile.ZipFile(docx) as d:
                xml = d.read("word/document.xml").decode("utf-8")
            check("REQ-19 the DOCX keeps a prompt's text and a table's rows",
                  all(w in xml for w in ("sample-subject-xyz", "row-one-lesson", "row-two-review")))
        sheets = list((Path(temp) / "write-guide-qa" / "Sample-Guide").glob("sheet*.png"))
        check("REQ-19 a contact sheet of the pages is made", len(sheets) > 0)
        check("REQ-19 render.sh prints where the contact sheets are",
              "write-guide-qa" in result.stdout, result.stdout[-300:])


LEARNER_TEXT = ("references/commands.md", "references/guide-template.html")


def t_no_internals():
    """write-guide/REQ-16: decision 0005's detectors over the text guides copy from."""
    sys.path.insert(0, str(REPO / "dev" / "eval"))
    import assert_scenario as detectors
    for rel in LEARNER_TEXT:
        path = SKILL / rel
        check(f"REQ-16 {rel} exists", path.is_file())
        if not path.is_file():
            continue
        text = re.sub(r"<[^>]+>", " ", path.read_text(encoding="utf-8"))
        hits = [m.group(0) for r in (detectors.BARE_LEVEL_RE, detectors.INTERNAL_NAME_RE)
                for m in r.finditer(text)]
        check(f"REQ-16 {rel} has no level or box number and no state-engine name",
              not hits, hits[:6])


def main():
    t_output_is_ignored()
    t_typed_only()
    t_not_in_any_package()
    t_commands_match_skills()
    t_facts_dated_and_sourced()
    t_no_internals()
    t_referenced_files_exist()
    t_render_refuses_repo()
    t_render_names_missing_tool()
    t_render_outputs()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
