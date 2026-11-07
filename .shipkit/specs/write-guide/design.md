# Design: Write a learner guide

## Approach
A project skill kept in the repo but outside every plugin package. `SKILL.md` holds the workflow in eight phases (ground truth, intake, research and verification, learning design, writing, self-review, render and visual check, report) and loads its references only in the phase that needs them. The facts that go stale (platform menus, plans, availability) live in one dated file the skill re-checks and corrects. The facts that come from the repo (version, commands, how each platform keeps progress) are read from the repo at run time. A shell script renders the HTML guide to PDF and DOCX and makes a contact sheet for the page-by-page check. What can be checked without a model is checked by `dev/eval/test_guide_writer.py`; what is model behaviour is checked by the first real run.

```
dev/guide-writer/
├── SKILL.md                      # the eight phases; disable-model-invocation: true
├── references/
│   ├── intake-questions.md       # the question bank (phase 2)
│   ├── platform-facts.md         # dated facts with sources (phases 3, 5)
│   ├── commands.md               # the 18 commands, plain words, example patterns (phase 5)
│   ├── guide-template.html       # styles and section skeleton (phase 5)
│   └── lessons.md                # what earlier guides taught, written generically (phases 4, 6)
└── scripts/
    └── render.sh                 # HTML → PDF + DOCX + contact sheet (phase 7)
```

## Decision: The skill lives in `dev/guide-writer/`, linked from `.claude/skills/`   (→ REQ-2, REQ-3)

**Context.** Claude Code finds project skills only in `.claude/skills/<name>/SKILL.md` and follows a symlinked entry there (code.claude.com/docs/en/skills, read 2026-11-07). This repo ignores `.claude/`, and CLAUDE.md says not to commit it. `skills/` is what the plugin ships to every learner, and its lint requires the learner-skill contract.

**Alternatives.**
1. `dev/guide-writer/`, committed, with a local symlink `.claude/skills/write-guide → ../../dev/guide-writer`.
2. Un-ignore `.claude/skills/` (`.claude/*` plus `!.claude/skills/`) and commit the skill there.
3. Ship it in `skills/` as a plugin skill.

**Case for 1.** `dev/` is already where maintainer-only tools live, and the Cowork package test already fails on anything from `dev/` in the package. No repo rule changes. Claude Code reads the skill through the link exactly as if it were in `.claude/skills/`.

**Case against 1.** Each clone needs one `ln -s` before `/write-guide` appears, and a maintainer who skips the CLAUDE.md line will not find the skill. A symlink is also one more thing Windows clones handle badly.

**Decision.** Option 1. Option 2 changes a stated repo rule for one file; option 3 would put a maintainer tool in every learner's `/` menu and break the feature freeze.
**Falsifiability.** We would reverse this if a second maintainer works in the repo, since a committed `.claude/skills/` then saves each of them the link step, or if `/write-guide` fails to appear in the `/` menu with the link in place on a current Claude Code.
**Fired-if.** manual

## Decision: The skill runs only when typed   (→ REQ-1)

**Context.** The maintainer does not want any per-session context cost. By default a skill's description sits in context every session; with `disable-model-invocation: true` nothing does until `/write-guide` is typed (code.claude.com/docs/en/skills, read 2026-11-07).

**Alternatives.**
1. `disable-model-invocation: true`.
2. Default invocation, with a short description so Claude can start it from "write a guide for…".

**Case for 1.** Zero context in every session that does not write a guide, which is nearly all of them.

**Case against 1.** Asking in plain words does nothing; the maintainer has to remember the command. Writing a guide is rare and deliberate, so this costs little.

**Decision.** Option 1.
**Falsifiability.** We would reverse this if the maintainer asks for a guide in plain words and the skill does not start, three times, and says the extra context of a default description is worth paying.
**Fired-if.** manual

## Decision: Repository facts are read at run time; platform facts live in one dated file the skill corrects   (→ REQ-10, REQ-11, REQ-15)

**Context.** A guide states two kinds of fact. Repository facts (the version, the commands, that a Claude chat keeps files only with Claude Desktop connected) change with releases and already have a source of truth in the repo. Platform facts (menu names, plans, phone support, country availability) change without notice: Claude renamed its Customize menu during the week the first guides were written.

**Alternatives.**
1. Read repository facts from the repo each run; keep platform facts in `references/platform-facts.md`, each with source and date, re-check each one a guide uses, and correct the file when one has changed.
2. Write all facts into `SKILL.md`.
3. Store nothing; research every fact from scratch each run.

**Case for 1.** Nothing is copied from the repo, so nothing drifts from it. The facts file gives each run a starting point and a source to re-open, so re-checking is fast, and each correction helps the next guide.

**Case against 1.** Re-checking every platform fact on every run costs web fetches and tokens, and the skill edits a committed file that the maintainer must review.

**Decision.** Option 1. Option 2 goes stale silently; option 3 repeats research that has a known source.
**Falsifiability.** We would reverse the re-check-everything rule, re-checking only facts older than 30 days, if five consecutive runs change nothing in `platform-facts.md`.
**Fired-if.** manual

## Decision: A claim ledger is a separate file beside the guide   (→ REQ-12, REQ-14, REQ-22)

**Context.** The maintainer wants to send a guide without re-reading every claim. The first guides were checked by hand, and two claims ("PMI members can read it free", a book's first-edition year) were caught only at the end.

**Alternatives.**
1. `claims.md` beside the guide: one row per factual claim with section, claim, source, date checked, and verified or not verified.
2. HTML comments next to each claim in the guide.
3. No ledger; a list of unverified claims in the final report only.

**Case for 1.** One place to review, sort and re-check later; `revise` mode starts from it. It never reaches the reader.

**Case against 1.** It is one more file to keep in step with the guide, and a claim edited in the guide but not in the ledger goes unnoticed.

**Decision.** Option 1. Phase 6 compares the two before the report.
**Falsifiability.** We would reverse this if a guide's review finds a factual sentence missing from its ledger in two separate guides; the ledger would then move inline, next to each claim (option 2).
**Fired-if.** manual

## Decision: The guide is written in HTML and rendered by WeasyPrint and pandoc   (→ REQ-19, REQ-20, REQ-21)

**Context.** The first two guides were HTML with print CSS rendered by WeasyPrint, which gives page footers, repeated table headers and boxes. Readers also need a copy they can paste prompts from, and `pandoc` is installed.

**Alternatives.**
1. HTML + CSS → WeasyPrint for the PDF; pandoc HTML → DOCX; pdftoppm + ImageMagick for the contact sheet.
2. Markdown → pandoc → LaTeX PDF.
3. Write straight into a Google Doc.

**Case for 1.** It is the process that made the two guides, so the template and the visual check carry over. One HTML source feeds every output.

**Case against 1.** It needs four tools installed, and pandoc's DOCX drops the print styling: no coloured boxes, plain tables. The DOCX is for copying, not for reading.

**Decision.** Option 1. `render.sh` refuses an output folder inside the repo, so a guide with personal details cannot land beside committed files.
**Falsifiability.** We would reverse the DOCX step if a reader reports that the DOCX loses a prompt's text or a table's rows.
**Fired-if.** manual

## Decision: The command reference is written by hand and checked against `skills/` by a test   (→ REQ-9, REQ-16)

**Context.** A guide's command reference explains each learner command in plain words with example prompts. The commands change with releases: 1.26.0 added none, but `learn-anything` changed what several do off code.

**Alternatives.**
1. Hand-written `references/commands.md`; `test_guide_writer.py` fails when its set of commands differs from the user-invocable skills in `skills/`.
2. Generate the reference from each skill's frontmatter at run time.

**Case for 1.** Frontmatter descriptions are written for Claude, not for learners ("Rotate live tracking files into archive + summary form"). A hand-written reference reads the way the guides do, and the test catches a missing or extra command on the next `dev/check.sh`.

**Case against 1.** The test catches a command added or removed, not one whose behaviour changed; a changed command can leave a stale description until someone reads it.

**Decision.** Option 1. The same test runs the repo's decision-0005 detectors (`BARE_LEVEL_RE`, `INTERNAL_NAME_RE` in `dev/eval/assert_scenario.py`) over the template and the reference.
**Falsifiability.** We would reverse this if a guide ships with a stale command description that the test did not catch, twice.
**Fired-if.** manual

## Data / interface changes
- `scripts/render.sh <guide.html> <output-name>`: reads `<guide.html>`, writes `<output-name>.pdf` and `<output-name>.docx` in the HTML's folder and a contact sheet under `${TMPDIR:-/tmp}/write-guide-qa/<output-name>/`, prints the paths, exits 0. It exits non-zero, naming the problem, when the HTML's folder is inside this repository (REQ-20) or a tool is missing (REQ-21).
- `dev/check.sh` runs `dev/eval/test_guide_writer.py` beside the other suites.
- `.gitignore` gains `output/` (REQ-4).
- CLAUDE.md *Where things live* gains one line: the skill's folder and `ln -s ../../dev/guide-writer .claude/skills/write-guide` (REQ-3).
