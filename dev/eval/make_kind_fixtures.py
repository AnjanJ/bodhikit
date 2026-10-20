#!/usr/bin/env python3
"""Build the evidence-kind eval fixtures (learn-anything) through bodhi-state.

    python3 dev/eval/make_kind_fixtures.py

writes dev/eval/fixtures/{problems,writing,performed}-project/ and
photo/one-point-perspective.png. What /learn scaffolds by hand is written
by hand here too (state.json, plan/, the profile files, progress.md,
resources.md, exercise folders); every kind, review and session goes
through bodhi-state with a pinned date, so each history is real engine
output. The original non-code-project fixture is copied, never changed:
it stays kind-less for REQ-3. Rebuild only on purpose; the evals read
these files."""
import json
import os
import shutil
import struct
import subprocess
import sys
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(REPO, "scripts", "bodhi-state")
FIX = os.path.join(REPO, "dev", "eval", "fixtures")


def bs(proj, day, *argv):
    r = subprocess.run([sys.executable, SCRIPT, "--project", proj, *argv],
                       capture_output=True, text=True,
                       env=dict(os.environ, BODHI_TODAY=day))
    if r.returncode != 0:
        sys.exit(f"bodhi-state {argv} failed: {r.stderr}")
    return json.loads(r.stdout)


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def text(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


def profile(ws, name, topic, started, phase, module, why, prior, style, area):
    dump(os.path.join(ws, ".bodhi-profile.json"), {
        "version": 2, "careerGoal": f"Learn {topic.lower()} well enough to use it",
        "whyLearning": why, "priorExperience": prior, "learningStyle": style,
        "overallBloomLevels": {area: 2},
        "cumulativeStats": {"totalSessions": 0, "totalExercises": 1,
                            "totalConceptsLearned": 1, "totalMilestonesReached": 0,
                            "totalProjects": 1, "teachBacksWritten": 0,
                            "teachBacksPublished": 0},
        "patterns": {"persistentChallenges": [], "consistentStrengths": []},
        "lastUpdated": f"{started}T09:00:00"})
    dump(os.path.join(ws, ".bodhi-profile.projects.json"), {
        "version": 2, "activeProjects": [{
            "name": name, "topic": topic, "startedAt": started, "currentPhase": phase,
            "currentModule": module, "bloomLevel": 2, "pace": "steady",
            "status": "active", "trackPurpose": "depth"}],
        "completedProjects": []})


def state(proj, name, topic, created, phase, module, index, activity, area):
    dump(os.path.join(proj, ".bodhi", "state.json"), {
        "version": 2, "projectName": name, "topic": topic,
        "createdAt": f"{created}T09:00:00", "lastSessionAt": f"{created}T09:00:00",
        "totalSessions": 0, "sessionDates": [], "currentStreak": 0,
        "currentPhase": phase, "currentModule": module, "currentModuleIndex": index,
        "lastActivity": activity,
        "initialBloomLevel": {area: 0}, "currentBloomLevel": {area: 2},
        "overallCompletion": 10})


def fresh(ws):
    if os.path.isdir(ws):
        shutil.rmtree(ws)
    os.makedirs(ws)


def draw_photo(path):
    """A one-point-perspective study of a box beside a road, pencil on paper,
    with one deliberate error a tutor can see: the box's top-right receding
    edge misses its construction line to the vanishing point."""
    W, H = 640, 480
    PAPER = (244, 240, 230)
    PENCIL = (70, 70, 74)
    LIGHT = (150, 150, 155)
    img = [[PAPER] * W for _ in range(H)]

    def plot(x, y, c, t=1):
        for dx in range(-(t // 2), t - t // 2):
            for dy in range(-(t // 2), t - t // 2):
                xx, yy = int(x) + dx, int(y) + dy
                if 0 <= xx < W and 0 <= yy < H:
                    img[yy][xx] = c

    def line(x0, y0, x1, y1, c=PENCIL, t=2):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) or 1
        for i in range(n + 1):
            plot(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n, c, t)

    def dashed(x0, y0, x1, y1, c=LIGHT):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) or 1
        for i in range(n + 1):
            if (i // 6) % 2 == 0:
                plot(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n, c, 1)

    VP = (330, 170)
    # horizon
    line(20, VP[1], 620, VP[1], LIGHT, 1)
    plot(VP[0], VP[1], PENCIL, 5)
    # road edges converging to the vanishing point
    line(200, 470, VP[0], VP[1], PENCIL, 2)
    line(460, 470, VP[0], VP[1], PENCIL, 2)
    # centre dashes on the road
    for k in range(6):
        a, b = 0.06 + k * 0.14, 0.06 + k * 0.14 + 0.07
        line(330, 470 + (VP[1] - 470) * a, 330, 470 + (VP[1] - 470) * b, PENCIL, 3)

    def toward_vp(x, y, f):
        return x + (VP[0] - x) * f, y + (VP[1] - y) * f

    # a box left of the road, below the horizon: front face square to the viewer,
    # so its top and right faces show
    fx0, fy0, fx1, fy1 = 40, 250, 160, 340
    depth = 0.3
    for (x, y) in ((fx0, fy0), (fx1, fy0), (fx1, fy1)):
        dashed(x, y, *VP)               # faint construction lines
    line(fx0, fy0, fx1, fy0)
    line(fx1, fy0, fx1, fy1)
    line(fx1, fy1, fx0, fy1)
    line(fx0, fy1, fx0, fy0)
    back_tl = toward_vp(fx0, fy0, depth)
    back_br = toward_vp(fx1, fy1, depth)
    # the deliberate error: the top-right receding edge climbs too steeply and
    # misses the vanishing point, so the back top edge tilts
    true_tr = toward_vp(fx1, fy0, depth)
    drawn_tr = (true_tr[0] + 4, true_tr[1] - 30)
    line(fx0, fy0, *back_tl)
    line(fx1, fy0, *drawn_tr)
    line(fx1, fy1, *back_br)
    line(*back_tl, *drawn_tr)
    line(*drawn_tr, *back_br)

    def png(path):
        raw = b"".join(b"\x00" + bytes(v for px in row for v in px) for row in img)
        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data
                    + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
            f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)))
            f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
            f.write(chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    png(path)


# --- problems: Mendelian genetics ------------------------------------------
ws = os.path.join(FIX, "problems-project")
fresh(ws)
proj = os.path.join(ws, "genetics")
profile(ws, "genetics", "Mendelian genetics", "2026-09-01", "0", "Single-gene inheritance",
        "Fixture for LLM evals: a subject of worked problems with exact answers",
        "School biology, years ago", "worked examples and problem sets", "genetics")
state(proj, "genetics", "Mendelian genetics", "2026-09-01", "0", "Single-gene inheritance",
      0, "Worked a monohybrid cross against the saved answers.", "genetics")
text(os.path.join(proj, ".bodhi", "plan", "README.md"),
     "# Learning Plan — Mendelian genetics\n\n**Current phase:** 0 (`phase-0.md`)\n"
     "**Target arc:** 6 weeks\n**Pace:** steady\n\n## Phases\n\n"
     "- **Phase 0 — Single genes to two genes** (6 weeks) → `phase-0.md`\n")
text(os.path.join(proj, ".bodhi", "plan", "phase-0.md"),
     "# Phase 0 — Single genes to two genes\n\n"
     "**Goals:** Predict offspring ratios from parental genotypes, by hand.\n"
     "**Duration:** 6 weeks\n"
     "**Success criteria:** Can set up and solve one- and two-gene crosses, and say why the ratios come out as they do.\n\n"
     "## Modules\n\n"
     "### Module 0.1 — Single-gene inheritance\n\n"
     "**Concepts:** Monohybrid crosses, Dominance and recessiveness\n\n"
     "**Key terms:** allele, genotype, phenotype, homozygous, heterozygous, Punnett square\n\n"
     "**Exercise:** A problem set in `exercises/`, its worked answers saved before the attempt.\n\n"
     "**Prerequisites for next module:** Monohybrid crosses\n\n"
     "### Module 0.2 — Two-gene inheritance\n\n"
     "**Concepts:** Dihybrid crosses, Independent assortment\n\n"
     "**Key terms:** dihybrid, independent assortment, 9:3:3:1\n")
text(os.path.join(proj, ".bodhi", "resources.md"),
     "# Resources — Mendelian genetics\n\n## Verified\n\n"
     "- Griffiths, Doebley, Peichel and Wassarman, *Introduction to Genetic Analysis*, "
     "12th ed. (W. H. Freeman, 2020), chapter 2, \"Single-Gene Inheritance\". The standard textbook account.\n"
     "- OpenStax, *Biology 2e*, chapter 12, \"Mendel's Experiments and Heredity\" — "
     "https://openstax.org/books/biology-2e/pages/12-introduction (free, peer-reviewed).\n")
ex = os.path.join(proj, "exercises", "01-monohybrid-crosses")
text(os.path.join(ex, "README.md"),
     "# Exercise 1 — Monohybrid crosses\n\n"
     "In pea plants, purple flowers (P) are dominant to white (p).\n\n"
     "1. Cross Pp × pp. What fraction of the offspring have white flowers?\n"
     "2. Cross Pp × Pp. Give the genotype ratio and the phenotype ratio.\n\n"
     "Work each cross in `work.md` in this folder, Punnett square included.\n")
text(os.path.join(ex, "answers.md"),
     "# Answers — Exercise 1 (saved before the attempt)\n\n"
     "1. Pp × pp → gametes P, p × p. Offspring Pp : pp = 1 : 1. White (pp): **1/2**.\n"
     "2. Pp × Pp → PP : Pp : pp = **1 : 2 : 1**; purple : white = **3 : 1**.\n")
text(os.path.join(ex, "work.md"),
     "# My work — Exercise 1\n\n"
     "1. Pp × pp. The Pp parent makes P or p, the pp parent only p.\n\n"
     "   |   | P  | p  |\n   |---|----|----|\n   | p | Pp | pp |\n\n"
     "   Half Pp (purple), half pp (white). **1/2 white.**\n\n"
     "2. Pp × Pp.\n\n"
     "   |   | P  | p  |\n   |---|----|----|\n   | P | PP | Pp |\n   | p | Pp | pp |\n\n"
     "   PP : Pp : pp = 1 : 2 : 1. Purple (PP, Pp) : white (pp) = **3 : 1**.\n")
bs(proj, "2026-09-01", "set-evidence-kind", "--kind", "problems")
bs(proj, "2026-09-01", "add-concept", "--concept", "Monohybrid crosses", "--module",
   "Single-gene inheritance", "--question",
   "Two heterozygous parents: what fraction of the offspring show the recessive trait, and why?")
bs(proj, "2026-09-01", "add-concept", "--concept", "Dominance and recessiveness",
   "--module", "Single-gene inheritance", "--bloom", "2", "--question",
   "Why can two purple-flowered plants have a white-flowered offspring?")
bs(proj, "2026-09-01", "record-review", "--concept", "Monohybrid crosses", "--result",
   "correct", "--tested-bloom", "2", "--source", "teach")
bs(proj, "2026-09-01", "touch-state", "--activity", "Taught monohybrid crosses with a worked Punnett square.")
bs(proj, "2026-09-02", "record-review", "--concept", "Monohybrid crosses", "--result",
   "correct", "--tested-bloom", "3", "--source", "practice", "--applied",
   "--evidence", "exercises/01-monohybrid-crosses/work.md")
bs(proj, "2026-09-02", "record-session", "--type", "practice", "--data",
   '{"conceptsReviewed": 1, "passes": 1}')
bs(proj, "2026-09-02", "touch-state", "--activity", "Worked a monohybrid cross against the saved answers.")
bs(proj, "2026-09-05", "record-review", "--concept", "Monohybrid crosses", "--result",
   "correct", "--tested-bloom", "3", "--confidence", "mostly", "--source", "quiz")
bs(proj, "2026-09-05", "touch-state", "--activity", "Quizzed a monohybrid cross on a new trait.")
text(os.path.join(proj, ".bodhi", "progress.md"),
     "# Progress Log\n\n## 2026-09-05 — Session 3 (Quiz: monohybrid crosses)\n\n"
     "**Outcomes:**\n- Predicted the ratio for a new trait from the parents' genotypes.\n\n"
     "**Next:** Dominance and recessiveness, then two-gene crosses.\n\n---\n\n"
     "## Summary of earlier sessions\n\n"
     "- 2026-09-02 — Exercise 1 worked against the saved answers; both crosses right.\n"
     "- 2026-09-01 — Kickoff; taught monohybrid crosses.\n")

# --- writing: the political-theory fixture with its kind recorded ----------
ws = os.path.join(FIX, "writing-project")
fresh(ws)
shutil.rmtree(ws)
shutil.copytree(os.path.join(FIX, "non-code-project"), ws,
                ignore=shutil.ignore_patterns("*.lock"))
proj = os.path.join(ws, "political-theory")
bs(proj, "2026-10-08", "set-evidence-kind", "--kind", "writing")
text(os.path.join(proj, ".bodhi", "resources.md"), '# Resources — Political theory from first principles\n\n## Verified\n\n- Anthony Weston, *A Rulebook for Arguments*, 5th ed. (Hackett, 2017) — premises, conclusions and how an argument is put together.\n- Jonathan Wolff, *An Introduction to Political Philosophy*, 3rd ed. (Oxford University Press, 2016) — the standard introduction.\n- Stanford Encyclopedia of Philosophy, "Positive and Negative Liberty" (Ian Carter) — https://plato.stanford.edu/entries/liberty-positive-negative/\n')

# --- performed: home cooking ------------------------------------------------
ws = os.path.join(FIX, "performed-project")
fresh(ws)
proj = os.path.join(ws, "cooking")
profile(ws, "cooking", "Home cooking: knife work and sauces", "2026-08-01", "0", "Emulsions",
        "Fixture for LLM evals: a performed skill practised away from the screen",
        "Cooks simple weeknight meals", "doing, then talking it through", "cooking")
state(proj, "cooking", "Home cooking: knife work and sauces", "2026-08-01", "0",
      "Emulsions", 1, "Debriefed a mayonnaise rep; it held this time.", "cooking")
text(os.path.join(proj, ".bodhi", "plan", "README.md"),
     "# Learning Plan — Home cooking: knife work and sauces\n\n"
     "**Current phase:** 0 (`phase-0.md`)\n**Target arc:** 8 weeks\n**Pace:** steady\n\n"
     "## Phases\n\n- **Phase 0 — Foundations at the board and the stove** (8 weeks) → `phase-0.md`\n")
text(os.path.join(proj, ".bodhi", "plan", "phase-0.md"),
     "# Phase 0 — Foundations at the board and the stove\n\n"
     "**Goals:** Cut safely and evenly; make and rescue the basic sauces.\n"
     "**Duration:** 8 weeks\n"
     "**Success criteria:** Can make a stable mayonnaise and a pan sauce, and say why each step matters.\n\n"
     "## Modules\n\n"
     "### Module 0.1 — Knife skills\n\n**Status:** done\n\n"
     "**Concepts:** Knife grip\n\n**Key terms:** pinch grip, claw, rocking cut\n\n"
     "**Prerequisites for next module:** none\n\n"
     "### Module 0.2 — Emulsions\n\n"
     "**Concepts:** Emulsions\n\n**Key terms:** emulsion, emulsifier, lecithin, split, re-emulsify\n\n"
     "**Exercise:** Practice reps at home, each debriefed.\n\n"
     "**Prerequisites for next module:** Emulsions\n\n"
     "### Module 0.3 — Pan sauces\n\n"
     "**Concepts:** Deglazing, Mounting with butter\n\n**Key terms:** fond, deglaze, reduce, monter au beurre\n")
text(os.path.join(proj, ".bodhi", "resources.md"),
     "# Resources — Home cooking\n\n## Verified\n\n"
     "- Harold McGee, *On Food and Cooking*, rev. ed. (Scribner, 2004), chapter 11, "
     "\"Sauces\" — the emulsion science.\n"
     "- J. Kenji López-Alt, *The Food Lab* (W. W. Norton, 2015), chapter 9 on emulsions.\n\n"
     "## Safety\n\n"
     "- USDA FSIS, Safe Minimum Internal Temperature Chart — "
     "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-supply-chain/food-safety-basics/safe-temperature-chart\n"
     "- National Center for Home Food Preservation (USDA-backed) — https://nchfp.uga.edu/ — "
     "the tested processes for home canning; never improvise one.\n")
ex = os.path.join(proj, "exercises", "01-knife-grip")
text(os.path.join(ex, "criteria.md"),
     "# Practice task — Knife grip (saved before the rep)\n\n"
     "**The rep (15 minutes, away from the screen):** dice one onion with a pinch grip on "
     "the knife and a claw on the guide hand.\n\n"
     "**Watch for:** where your guide-hand fingertips are on every cut; whether the pieces come out even.\n\n"
     "**Debrief questions (asked before anything is recorded):**\n"
     "1. What did you do, step by step?\n"
     "2. What went wrong or surprised you?\n"
     "3. What would you change next time, and why?\n")
ex = os.path.join(proj, "exercises", "02-mayonnaise")
text(os.path.join(ex, "criteria.md"),
     "# Practice task — Mayonnaise (saved before the rep)\n\n"
     "**The rep (20 minutes):** one yolk, a teaspoon of mustard, 200 ml neutral oil, by whisk. "
     "The first 50 ml drop by drop.\n\n"
     "**Watch for:** when it turns from runny to thick; what the whisking arm feels; any sign of oil pooling.\n\n"
     "**Debrief questions (asked before anything is recorded):**\n"
     "1. What did you do, step by step, with quantities and times?\n"
     "2. What went wrong or surprised you?\n"
     "3. What would you change next time, and why?\n")
bs(proj, "2026-08-01", "set-evidence-kind", "--kind", "performed")
bs(proj, "2026-08-01", "add-concept", "--concept", "Knife grip", "--module", "Knife skills",
   "--question", "Why does the claw keep your fingers safe while still guiding the cut?")
for day, bloom, extra in (("2026-08-01", "3", ["--source", "teach"]),
                          ("2026-08-02", "4", ["--source", "practice", "--applied", "reported"]),
                          ("2026-08-05", "4", ["--source", "quiz", "--applied", "reported"]),
                          ("2026-08-12", "4", ["--source", "quiz", "--applied", "reported"])):
    bs(proj, day, "record-review", "--concept", "Knife grip", "--result", "correct",
       "--tested-bloom", bloom, *extra)
    bs(proj, day, "touch-state", "--activity", "Debriefed a knife-grip rep.")
bs(proj, "2026-08-12", "set-feynman", "--concept", "Knife grip")
bs(proj, "2026-08-12", "touch-state", "--module", "Emulsions", "--module-index", "1",
   "--activity", "Knife skills done; starting emulsions.")
bs(proj, "2026-09-10", "add-concept", "--concept", "Emulsions", "--module", "Emulsions",
   "--question", "Why does mayonnaise split if the oil goes in too fast, and how do you bring it back?")
bs(proj, "2026-09-10", "record-review", "--concept", "Emulsions", "--result", "correct",
   "--tested-bloom", "2", "--source", "teach")
bs(proj, "2026-09-10", "touch-state", "--activity", "Taught emulsions with mayonnaise as the case.")
bs(proj, "2026-09-11", "record-review", "--concept", "Emulsions", "--result", "correct",
   "--tested-bloom", "3", "--source", "practice", "--applied", "reported")
bs(proj, "2026-09-11", "record-session", "--type", "practice", "--data",
   '{"conceptsReviewed": 1, "passes": 1, "notes": "first mayonnaise rep, debriefed"}')
bs(proj, "2026-09-11", "touch-state", "--activity", "Debriefed a mayonnaise rep; it held this time.")
text(os.path.join(proj, ".bodhi", "progress.md"),
     "# Progress Log\n\n## 2026-09-11 — Session 7 (Practice: mayonnaise)\n\n"
     "**Outcomes:**\n- First mayonnaise rep, at home, by the learner's account: it held. "
     "Debrief explained why the slow start matters.\n\n"
     "**Next:** Another rep, and why a split emulsion can be rescued.\n\n---\n\n"
     "## Summary of earlier sessions\n\n"
     "- 2026-09-10 — Taught emulsions.\n"
     "- 2026-08-01 to 2026-08-12 — Knife skills: four debriefed knife-grip reps; Solid by the learner's account.\n")

draw_photo(os.path.join(FIX, "photo", "one-point-perspective.png"))

for ws, p in (("problems-project", "genetics"), ("writing-project", "political-theory"),
              ("performed-project", "cooking")):
    proj = os.path.join(FIX, ws, p)
    r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                       capture_output=True, text=True)
    out = json.loads(r.stdout)
    print(ws, "verify ok" if out["ok"] else "verify FAIL", out["errors"], out["warnings"])
    for root, _, names in os.walk(os.path.join(FIX, ws)):
        for n in names:
            if n.endswith(".lock"):
                os.remove(os.path.join(root, n))
