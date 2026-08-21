#!/usr/bin/env python3
"""Aggregate `bodhi-state export-anonymized` across learning projects into a
markdown outcomes report (docs/outcomes.md).

Usage:
    python3 dev/outcomes.py <project-dir>... > docs/outcomes.md

Reads only. Every number comes from the anonymized export, which carries no
concept names, no topic names, no free text — distributions and rates only.
Projects are labelled P1..Pn in the order given.
"""
import datetime
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "bodhi-state")
GAPS = ["same-day", "1d", "2-3d", "4-7d", "8-14d", "15-30d", "31d+"]


def export(project):
    r = subprocess.run([sys.executable, SCRIPT, "--project", project, "export-anonymized"],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def pct(x):
    return "—" if x is None else f"{round(x * 100)}%"


def main(paths):
    exports = [export(p) for p in paths]
    today = datetime.date.today().isoformat()
    out = []
    w = out.append
    w("# BodhiKit outcomes — what the tracking data actually shows")
    w("")
    w(f"_Generated {today} by `dev/outcomes.py` from `bodhi-state export-anonymized`. "
      "No concept names, topic names, or free text leave the learner's machine — "
      "only counts, distributions, and rates._")
    w("")
    w("## Read this first")
    w("")
    w(f"This is **one learner, {len(exports)} projects**. It is published because a "
      "project whose thesis is pedagogy should show its numbers, not because the "
      "numbers prove anything. They are too few to support a claim in either direction. "
      "What they can do is make the claim falsifiable over time: if BodhiKit works, "
      "the retention rate at long gaps should hold near the Leitner target and the "
      "mastered count should grow; if it does not, this table will say so.")
    w("")
    w("## Per project")
    w("")
    w("| | Days active | Sessions | Concepts | Classified | Mastered | Feynman passed | Reviews | Overall recall |")
    w("|---|---|---|---|---|---|---|---|---|")
    tot = {"sessions": 0, "concepts": 0, "classified": 0, "mastered": 0,
           "feynman": 0, "reviews": 0, "correct": 0}
    for i, e in enumerate(exports, 1):
        proj = e.get("project") or {}
        bd = e.get("bloomDistribution", {})
        classified = sum(v for k, v in bd.items() if k != "0")
        ret = e.get("retention", {})
        reviews = ret.get("reviews", 0)
        rate = ret.get("overallSuccessRate")
        days = proj.get("daysSinceStart")
        w(f"| P{i} | {'—' if days is None else days} | {proj.get('totalSessions', '—')} | "
          f"{e.get('concepts', 0)} | {classified} | {e.get('mastered', 0)} | "
          f"{e.get('feynmanPassed', 0)} | {reviews} | {pct(rate)} |")
        tot["sessions"] += proj.get("totalSessions", 0) or 0
        tot["concepts"] += e.get("concepts", 0)
        tot["classified"] += classified
        tot["mastered"] += e.get("mastered", 0)
        tot["feynman"] += e.get("feynmanPassed", 0)
        tot["reviews"] += reviews
        if rate is not None:
            tot["correct"] += round(rate * reviews)
    overall = tot["correct"] / tot["reviews"] if tot["reviews"] else None
    w(f"| **All** | | {tot['sessions']} | {tot['concepts']} | {tot['classified']} | "
      f"{tot['mastered']} | {tot['feynman']} | {tot['reviews']} | {pct(overall)} |")
    w("")
    w("_Classified_ = concepts a teaching or review session has actually graded "
      "(Bloom ≥ 1); the rest were scaffolded by the plan and never reached. "
      "_Mastered_ uses the four-part formula (Analyze-level or above, three "
      "consecutive correct at that level, Box 4-5, Feynman explain-back passed).")
    w("")
    w("## Retention by gap since the previous review (all projects pooled)")
    w("")
    w("The Leitner literature targets roughly 80-90% recall at each scheduled "
      "review. Below that, intervals are too long; far above it, too short.")
    w("")
    w("| Gap | Reviews | Correct | Partial | Incorrect | Recall |")
    w("|---|---|---|---|---|---|")
    pooled = {g: {"reviews": 0, "correct": 0, "partial": 0, "incorrect": 0} for g in GAPS}
    for e in exports:
        for g, row in (e.get("retention", {}).get("byGap") or {}).items():
            if g in pooled:
                for k in ("reviews", "correct", "partial", "incorrect"):
                    pooled[g][k] += row.get(k, 0)
    for g in GAPS:
        r = pooled[g]
        rate = r["correct"] / r["reviews"] if r["reviews"] else None
        w(f"| {g} | {r['reviews']} | {r['correct']} | {r['partial']} | {r['incorrect']} | {pct(rate)} |")
    w("")
    w("## Where concepts sit")
    w("")
    w("| Bloom rung | Concepts |")
    w("|---|---|")
    labels = {"0": "— (not yet observed)", "1": "Remember", "2": "Understand", "3": "Apply",
              "4": "Analyze", "5": "Evaluate", "6": "Create"}
    bd_tot = {k: 0 for k in labels}
    for e in exports:
        for k, v in e.get("bloomDistribution", {}).items():
            bd_tot[k] = bd_tot.get(k, 0) + v
    for k in labels:
        w(f"| {labels[k]} | {bd_tot.get(k, 0)} |")
    w("")
    w("| Leitner box | Concepts |")
    w("|---|---|")
    box_tot = {str(i): 0 for i in range(1, 6)}
    for e in exports:
        for k, v in e.get("boxDistribution", {}).items():
            box_tot[k] = box_tot.get(k, 0) + v
    for k in sorted(box_tot):
        w(f"| Box {k} | {box_tot[k]} |")
    w("")
    w("## Confidence calibration")
    w("")
    tagged = sum(e.get("calibration", {}).get("taggedAnswers", 0) for e in exports)
    over = [e["calibration"].get("overconfidenceRate") for e in exports
            if e.get("calibration", {}).get("taggedAnswers")]
    w(f"{tagged} answers carried a confidence tag. "
      + ("Too few to report a rate." if tagged < 20 else
         f"Over-confidence (sure-but-wrong ÷ all sure): {pct(sum(o for o in over if o is not None) / max(1, len([o for o in over if o is not None])))}."))
    w("")
    w("## Session mix")
    w("")
    mix = {}
    for e in exports:
        for k, v in e.get("sessionTypeCounts", {}).items():
            mix[k] = mix.get(k, 0) + v
    w("| Session type | Count |")
    w("|---|---|")
    for k in sorted(mix, key=lambda x: -mix[x]):
        w(f"| {k} | {mix[k]} |")
    w("")
    w("## What this does and does not say")
    w("")
    w("- It says the plugin's tracking pipeline records real reviews at real gaps and "
      "that the numbers are inspectable. That was not true before 1.11.0.")
    w("- It does not say the learner learned more than they would have otherwise. "
      "There is no control condition and the sample is a handful of sessions.")
    w("- The thing to watch over the next months is the **15-30d** and **31d+** rows: "
      "that is where spaced repetition either earns its keep or does not.")
    w("- If you use BodhiKit, `bodhi-state export-anonymized` on your own project "
      "produces the same JSON; the `learning-data-report` issue template is the "
      "place to send it.")
    print("\n".join(out))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
