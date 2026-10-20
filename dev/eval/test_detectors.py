#!/usr/bin/env python3
"""Deterministic checks on the LLM-eval detectors (learn-anything).

A transcript detector is evidence only if it tells a good run from a bad
one. Each check builds a synthetic transcript (and, where the detector
reads files, a project) that the scenario should pass and one it should
fail, and runs the detector on both. Free; run by dev/check.sh.

Run: python3 dev/eval/test_detectors.py
"""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIXTURES = os.path.join(HERE, "fixtures")
sys.path.insert(0, HERE)
import assert_scenario as A  # noqa: E402

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"ok    {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def passes(fn, *args, **kw):
    """(passed, output): a detector fails by exiting 1 through A.fail()."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            fn(*args, **kw)
        except SystemExit as e:
            return e.code == 0, buf.getvalue()
    return True, buf.getvalue()


def transcript(root, name, *items):
    """A claude stream-json transcript: ("text", str) or ("tool", name, input)."""
    path = os.path.join(root, f"{name}.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            block = ({"type": "text", "text": it[1]} if it[0] == "text"
                     else {"type": "tool_use", "name": it[1], "input": it[2]})
            f.write(json.dumps({"type": "assistant", "message": {"content": [block]}}) + "\n")
    return path


def pair(label, fn, good, bad, **kw):
    ok_good, out_good = passes(fn, *good, **kw)
    ok_bad, out_bad = passes(fn, *bad, **kw)
    check(f"{label}: passes the good run", ok_good, out_good.strip()[-300:])
    check(f"{label}: fails the bad run", not ok_bad, out_bad.strip()[-300:])


def project(root, workspace, name):
    dest = os.path.join(root, workspace)
    if not os.path.isdir(dest):
        shutil.copytree(os.path.join(FIXTURES, workspace), dest)
    return os.path.join(dest, name)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def bash(cmd):
    return ("tool", "Bash", {"command": cmd})


BS = '"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project . '
LESSON = ("Purple is dominant to white. Cross Pp × pp: the Pp parent gives P or p, the pp "
          "parent only p, so half the offspring are white.\n\n"
          "| | P | p |\n|---|---|---|\n| p | Pp | pp |\n\n"
          "This is the standard account — OpenStax, *Biology 2e*, chapter 12.")


def t_code_never_loads_kinds(root):
    good = transcript(root, "code-good", ("tool", "Skill", {"skill": "bodhikit:state-ops"}),
                      bash(BS + "session-brief --concept 'B-tree indexes'"), ("text", "Let's begin."))
    bad = transcript(root, "code-bad", ("tool", "Skill", {"skill": "bodhikit:evidence-kinds"}))
    pair("code never loads kinds (KB)", A.assert_code_never_loads_kinds, (None, good), (None, bad))
    bad = transcript(root, "code-bad-2", bash(BS + "set-evidence-kind --kind code"))
    pair("code never loads kinds (record)", A.assert_code_never_loads_kinds, (None, good), (None, bad))


def t_teach_no_code(root):
    good = transcript(root, "teach-good", ("text", LESSON))
    bad = transcript(root, "teach-bad", ("text", LESSON + "\n\n```python\ndef cross(a, b):\n"
                                         "    return [x + y for x in a for y in b]\n```"))
    pair("kind teach no code (fence)", A.assert_kind_teach_no_code, (None, good), (None, bad))
    bad = transcript(root, "teach-bad-2", ("text", "Now write a function that lists the gametes."))
    pair("kind teach no code (talk)", A.assert_kind_teach_no_code, (None, good), (None, bad))


def t_quiz_no_code(root):
    good = transcript(root, "quiz-good", ("text", "**Q1.** Two heterozygous purple plants are "
                                          "crossed. What fraction of the offspring are white, and why?"))
    bad = transcript(root, "quiz-bad", ("text", "**Q1.** What would this code output?\n"
                                        "```python\nprint(cross('Pp', 'pp'))\n```"))
    pair("kind quiz no code", A.assert_kind_quiz_no_code, (None, good), (None, bad))
    bad = transcript(root, "quiz-bad-2", ("text", "**Q1.** Define a heterozygous genotype."))
    pair("kind quiz no definitions", A.assert_kind_quiz_no_code, (None, good), (None, bad))


def t_offers(root):
    good = transcript(root, "offers-good", ("text", LESSON + "\n\nShall we set an exercise?"))
    bad = transcript(root, "offers-bad", ("text", "Want to switch to "
                                          "`/bodhikit:pair --invoked-from=teach crosses`?"))
    pair("kind offers", A.assert_kind_offers, (None, good), (None, bad))


def t_sources(root):
    proj = project(root, "problems-project", "genetics")
    good = transcript(root, "sources-good", ("text", LESSON))
    bad = transcript(root, "sources-bad", ("text", "Purple is dominant to white."))
    pair("kind sources (named)", A.assert_kind_sources, (proj, good), (proj, bad))
    catalog = os.path.join(root, "catalog", "genetics")
    shutil.copytree(proj, catalog)
    write(os.path.join(catalog, ".bodhi", "resources.md"),
          "# Resources\n\n- freeCodeCamp — https://www.freecodecamp.org/\n"
          "- OpenStax, *Biology 2e* — https://openstax.org/\n")
    pair("kind sources (no catalogs)", A.assert_kind_sources, (proj, good), (catalog, good))


def t_key_before_attempt(root):
    proj = project(root, "problems-project", "genetics")
    folder = "exercises/02-dominance"
    for name in ("README.md", "answers.md", "work.md"):
        write(os.path.join(proj, folder, name), name)
    readme = ("tool", "Write", {"file_path": f"{proj}/{folder}/README.md", "content": "task"})
    key = ("tool", "Write", {"file_path": f"{proj}/{folder}/answers.md", "content": "key"})
    work = ("tool", "Write", {"file_path": f"{proj}/{folder}/work.md", "content": "work"})
    review = bash(BS + f"record-review --concept 'Dominance and recessiveness' --result correct "
                  f"--tested-bloom 3 --applied --evidence {folder}/work.md")
    good = transcript(root, "key-good", readme, key, ("text", "The key is saved."), work, review)
    bad = transcript(root, "key-bad", readme, work, key, review)
    pair("kind key before attempt (order)", A.assert_kind_key_before_attempt, (proj, good), (proj, bad))
    bad = transcript(root, "key-bad-2", readme, work, review)
    pair("kind key before attempt (missing)", A.assert_kind_key_before_attempt,
         (proj, good), (proj, bad))
    stray = bash(BS + "record-review --concept 'Dominance and recessiveness' --result correct "
                 "--applied --evidence exercises/01-monohybrid-crosses/work.md")
    bad = transcript(root, "key-bad-3", readme, key, work, stray)
    pair("kind key before attempt (evidence elsewhere)", A.assert_kind_key_before_attempt,
         (proj, good), (proj, bad))


def t_intake(root):
    proj = project(root, "v2-project", "sql-deep-dive")
    parent = os.path.dirname(proj)
    music = os.path.join(parent, "music-theory")
    write(os.path.join(music, ".bodhi", "state.json"),
          json.dumps({"version": 2, "projectName": "music-theory", "evidenceKind": "problems"}))
    write(os.path.join(music, ".bodhi", "resources.md"),
          "# Resources\n\n- Kostka and Payne, *Tonal Harmony* (McGraw-Hill)\n"
          "- Open Music Theory — https://viva.pressbooks.pub/openmusictheory/\n")
    lists_path = os.path.join(parent, ".bodhi-profile.projects.json")
    lists = json.load(open(lists_path))
    lists["activeProjects"].append({"name": "music-theory"})
    write(lists_path, json.dumps(lists))
    ask = ("text", "What have you played or read in music so far? Can you read treble clef?")
    propose = ("text", "Your work here will be worked problems — intervals and chords to name — "
                       "checked against worked answers I save before you try. Does that fit?")
    record = bash(f'"${{CLAUDE_PLUGIN_ROOT}}/scripts/bodhi-state" --project {music} '
                  "set-evidence-kind --kind problems")
    good = transcript(root, "intake-good", ask, propose, record)
    bad = transcript(root, "intake-bad", ("text", "What programming languages have you used?"),
                     propose, record)
    pair("kind intake (no programming questions)", A.assert_kind_intake, (proj, good), (proj, bad))
    bad = transcript(root, "intake-bad-2", ask, record, propose)
    pair("kind intake (propose before recording)", A.assert_kind_intake, (proj, good), (proj, bad))


def t_legacy_proposal(root):
    proj = project(root, "non-code-project", "political-theory")
    st_path = os.path.join(proj, ".bodhi", "state.json")
    st = json.load(open(st_path))
    st["evidenceKind"] = "writing"
    write(st_path, json.dumps(st))
    propose = ("text", "One thing first: here the evidence that you can use an idea is a written "
                       "piece applying it to a new case, read against criteria I save first. "
                       "Shall I record that?")
    record = bash(BS + "set-evidence-kind --kind writing")
    good = transcript(root, "legacy-good", propose, record)
    bad = transcript(root, "legacy-bad", propose, record, record)
    pair("kind legacy proposal (once)", A.assert_kind_legacy_proposal, (proj, good), (proj, bad))
    bad = transcript(root, "legacy-bad-2", record, propose)
    pair("kind legacy proposal (proposed first)", A.assert_kind_legacy_proposal,
         (proj, good), (proj, bad))


def t_review_no_rewrite(root):
    proj = project(root, "writing-project", "political-theory")
    piece = "exercises/02-claims-in-a-new-case/my-analysis.md"
    source = open(os.path.join(FIXTURES, "applied", "claims-analysis.md"), encoding="utf-8").read()
    write(os.path.join(proj, piece), source)
    review = ("> \"Drivers should pay for the road space they take up.\" Normative: it says what "
              "ought to happen.\n\nRight, and you say why no count can settle it. What principle "
              "would?\n\n> The data can test 1 and 3, and the premise inside 4, but never 2 or the "
              "verdict in 4.\n\nWhat would the council need to agree on first?")
    good = transcript(root, "review-good", ("text", review))
    bad = transcript(root, "review-bad", ("text", review + "\n\nHere's a revised version of your "
                                          "last paragraph: The council argued past each other..."))
    pair("kind review no rewrite (prose)", A.assert_kind_review_no_rewrite, (proj, good), (proj, bad))
    bad = transcript(root, "review-bad-2", ("text", "Good work overall; the reasoning holds."))
    pair("kind review no rewrite (quotes)", A.assert_kind_review_no_rewrite,
         (proj, good), (proj, bad))
    edited = os.path.join(root, "edited", "political-theory")
    shutil.copytree(proj, edited)
    write(os.path.join(edited, piece), source.replace("talked past each other", "disagreed"))
    pair("kind review no rewrite (file)", A.assert_kind_review_no_rewrite,
         (proj, good), (edited, good))


def main():
    with tempfile.TemporaryDirectory() as root:
        for t in (t_code_never_loads_kinds, t_teach_no_code, t_quiz_no_code, t_offers,
                  t_sources, t_key_before_attempt, t_intake, t_legacy_proposal,
                  t_review_no_rewrite):
            print(f"-- {t.__name__}")
            sub = os.path.join(root, t.__name__)
            os.makedirs(sub)
            try:
                t(sub)
            except Exception as e:  # one crashed check must not hide the summary
                global FAIL
                FAIL += 1
                print(f"FAIL  {t.__name__} crashed: {type(e).__name__}: {e}")
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
