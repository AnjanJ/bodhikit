# BodhiKit

[![Version](https://img.shields.io/badge/version-1.17.0-blue)](./CHANGELOG.md) [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?logo=buymeacoffee)](https://buymeacoffee.com/anjanj) [![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa?logo=githubsponsors)](https://github.com/sponsors/AnjanJ)

**Research-informed interactive coding tutor for Claude Code.**

Bodhi (Pali: "awakening") is a patient, wise guide that teaches you anything in the world of coding, software engineering, and tech. It does not write code for you. It teaches you to write code yourself.

## TL;DR

BodhiKit turns Claude Code into a research-informed coding tutor. Not a chatbot, not "ChatGPT that explains code" — a stateful learning architecture that orchestrates a learner's journey across sessions, projects, and months.

### Purpose & philosophy

The animating constraint: **"The learner writes code. BodhiKit asks questions. The goal is to become unnecessary."**

The *voice* comes from four named teachers (Gautama Buddha, Dr. B.R. Ambedkar, Master Oogway, Yoda) — a persona layer in the `teaching-personality` KB that sets the tone: patience, directness with care, "try it and see", education as empowerment. The pedagogy itself is owned by the methodology KBs below, each with its own citations.

### How it achieves excellence

1. **Pedagogical theories wired into behavior, not vibes.** Bloom's taxonomy (per-concept level tracking), Vygotsky's ZPD (calibrated difficulty), Leitner spaced repetition (5-box system with date-computed reviews), Feynman (explain-back gates), Sweller's cognitive load (faded worked examples), Bjork's pretesting, Rawson & Dunlosky's successive relearning, Koriat's confidence calibration, deliberate practice, Whitmore's GROW, Kram's mentoring functions, Flavell's metacognition. Each lives in its own KB, loaded only when its phase fires (progressive disclosure).

2. **Socratic enforcement as architecture, not suggestion.** `/teach` uses graduated hints (Direction → Approach → Near-solution) and forbids "Hint 4." `/debug-together` says "Do NOT look at the code yet." `dev/check.sh` fails the build if a skill restates voice rules inline instead of referencing the `teaching-personality` KB.

3. **Cross-session memory.** `.bodhi/state.json`, `spaced-review.json`, `progress.md`, and `.bodhi-profile.json` form a learner profile that persists. Streaks, Box-3 review dates, Bloom level per sub-topic, persistent challenges — all carried forward.

4. **A deterministic state layer (1.11.0).** Every JSON mutation goes through `scripts/bodhi-state` — Leitner math, the Bloom ratchet, mastery formula, migration, and schema validation run in code, not in model prose. A Stop hook verifies tracking files before a session ends, and a two-layer test harness (free deterministic tests + pre-tag LLM evals asserting on file state) guards the contracts that manual dogfooding used to.

5. **Single sources of truth + lint as contract.** `state-ops` KB owns the operational surface; `state-schema` KB owns every tracking-file shape (and loads only where a skill legitimately hand-mutates JSON). `spaced-repetition` KB owns every Leitner interval. `teaching-personality` owns the voice. `dev/check.sh` enforces the contracts — version sync (badge included), KB references, agent fallbacks, `--invoked-from=` chaining, the `bodhi-state` write path, skill size budgets — and runs the deterministic test suite.

6. **Sub-skill chaining for context efficiency.** `/continue` → `/progress quick` → `/teach` → `/reflect`, each passing `--invoked-from=<caller>` so callees skip redundant KB loads.

## What Makes BodhiKit Different

- **Research-informed**: Built on well-studied learning science (Oakley, Feynman, Bloom, Vygotsky, Ericsson, Dweck, Bjork) — see the honest note in [The Science](#the-science) for what that does and does not claim
- **Deeply personalized**: Assesses your unique skill level, builds a custom learning plan, adapts to your pace
- **Proactive teaching**: `/teach` walks you through concepts step by step, not just answering questions
- **Hands-on**: Learn by doing. Exercises, projects, code review. Never just reading.
- **Remembers your journey**: Spaced repetition, progress tracking, cross-session continuity
- **Metacognitive reflection**: End-of-session `/reflect` builds your awareness of HOW you learn
- **One command sessions**: `/continue` auto-invokes the quick check-in, teaching, practice, and reflection
- **Honest and wise**: Feedback that is respectful, specific, and genuinely helpful

## Install

```
/plugin marketplace add https://github.com/AnjanJ/bodhikit.git
/plugin install bodhikit@bodhikit
```

Restart Claude Code after installing. (To try a checkout without installing: `claude --plugin-dir ~/code/bodhikit`.)

## Your first 15 minutes

**Install** — the two commands above, then restart Claude Code.

**Pick a place to learn.** `cd` into a folder you want to learn in (an empty one is fine). On your first project BodhiKit asks where to keep learning projects — the current folder is a fine answer — and creates `learningWithBodhi/<topic>/` there. That is where your plan, progress, and review schedule live, and you can put it under git.

**Start.**

```
/bodhikit:learn <topic>
```

This is interactive. BodhiKit asks what is driving the topic and what "done" looks like, then runs a short adaptive assessment — around ten questions, roughly 10–20 minutes — so the plan starts from what you actually know rather than from zero. You will rate yourself before each sub-topic; the gap between your rating and your answers is the first thing the tutor learns about you. It ends with a personalized plan and a first small exercise.

**Learn something.**

```
/bodhikit:teach
```

The tutor explains the next concept in your plan, works a problem with you, hands you an exercise, and asks you to explain it back. It will not write the code for you. When you are stuck you get graduated hints — direction, then approach, then near-solution — and never a fourth.

**Close the session.**

```
/bodhikit:reflect
```

Three quick questions: what was hard, what you would do differently, how confident you feel — checked against what you actually did today, so the review schedule reflects evidence rather than mood.

**Tomorrow:** `/bodhikit:continue`. One command resumes where you left off: a 3-line check-in, any concepts due for review, the next lesson, and reflection.

<details>
<summary><strong>Tip: enable BodhiKit only in your learning folder</strong></summary>

BodhiKit loads 20 knowledge bases. To avoid polluting context in unrelated projects, enable it per-project instead of globally. In your `learningWithBodhi/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "bodhikit@bodhikit": true
  }
}
```

Or disable it in projects where you do not need it by adding to `.claude/settings.local.json`:

```json
{
  "enabledPlugins": {
    "bodhikit@bodhikit": false
  }
}
```

</details>

**Upgrading from an earlier version?** See [MIGRATION.md](./MIGRATION.md) — one command, `/bodhikit:housekeep migrate`, handles every tracking-file change since 1.6.

## Feedback

BodhiKit currently has a very small number of real learners. If you try it, your experience is the most valuable thing you can send — one honest account of one session beats any feature request.

- [Something broke or graded you wrong](./.github/ISSUE_TEMPLATE/bug-report.md) — bug report
- [How did a session go?](./.github/ISSUE_TEMPLATE/feedback.md) — five short prompts
- [Share your learning data](./.github/ISSUE_TEMPLATE/learning-data-report.md) — one command, numbers only, no concept names or free text

**Full guide:** see [GUIDE.md](./GUIDE.md) — a complete worked example from Day 1 to capstone (10-week Rust journey), every skill with *when to use / when not to / pairs well with / example*, how teaching and analogies work, the spaced-review system, the optional capstone, and tips for using BodhiKit alongside books and courses.

## Skills (18)

| Skill | Description |
|-------|-------------|
| `/learn` | Start a new learning project with assessment and personalized plan |
| `/continue` | Resume from where you left off — auto-invokes check-in, teach, reflect |
| `/teach` | Proactive guided teaching: explain, demonstrate, practice, verify — or an understanding-only Feynman deep dive when that is all you want |
| `/assess` | Standalone skill assessment on any topic |
| `/review` | Educational code review (local files, GitHub, GitLab, Codeberg) |
| `/quiz` | Active recall check with spaced repetition tracking |
| `/plan` | View, adjust, or regenerate your learning plan |
| `/progress` | Progress dashboard — plus `quick` (3-line check-in) and `all` (cross-project table with health flags) |
| `/resources` | Find, verify, and manage learning resources |
| `/practice` | Hands-on exercise calibrated to your level |
| `/evaluate` | Comprehensive evaluation of your learning journey |
| `/reflect` | End-of-session metacognitive reflection |
| `/mentor` | Career and learning path guidance using the GROW model |
| `/pair` | Pair programming: strong-style, ping-pong, or navigator mode |
| `/debug-together` | Scientific debugging: reproduce, hypothesize, probe, isolate, fix |
| `/forget` | Demote a concept back to Box 1 — for honest self-assessment |
| `/housekeep` | Rotate tracking files into archive + summary form; one-shot 1.7.0 migration |
| `/teach-back` | Optional capstone after completion: Socratic-style blog post on a formerly-shaky topic, master comparison, learner-decided publish |

## Agents (4)

| Agent | Model | Purpose |
|-------|-------|---------|
| skill-assessor | Sonnet | Adaptive Bloom's taxonomy skill evaluation |
| code-reviewer | Sonnet | Educational code review (what code reveals about understanding) |
| resource-finder | Haiku | Web search for verified free learning resources |
| trajectory-analyzer | Sonnet | Reads full project history (sessions, archives, assessments) and returns a structured trajectory report — used by `/evaluate` so the heavy archive load happens in the agent's context, not the parent skill's |

## Knowledge Bases (20)

Each learning methodology lives in its own focused knowledge base, loaded only when needed (progressive disclosure):

| Knowledge Base | Purpose |
|---------------|---------|
| spaced-repetition | Ebbinghaus forgetting curve, Leitner box system, update rules |
| blooms-taxonomy | 6 cognitive levels for programming, mastery criteria |
| zone-of-proximal-development | Three zones, detection signals, scaffolding strategy |
| feynman-technique | 4 steps for deep understanding, when to use |
| deliberate-practice | Targeted exercises at the edge of ability |
| growth-mindset | Language patterns, praising strategy over talent |
| desirable-difficulties | Spacing, interleaving, retrieval, generation, variation |
| metacognition | Teaching learners HOW to learn, Dunning-Kruger, confidence calibration |
| cognitive-load | Sweller's worked examples, faded scaffolding, expertise reversal |
| constructivism | Spiral curriculum, project progression by level |
| ai-learning-safeguards | Risks of AI over-reliance, structural safeguards |
| mentoring-theory | GROW model, Kram's career and psychosocial functions |
| pair-programming | Strong-style, driver/navigator, ping-pong TDD, Williams & Kessler |
| scientific-debugging | TRAFFIC method, debugging mindset, wolf fence, expert vs novice |
| assessment-framework | Question templates by Bloom's level, exercise design |
| teaching-personality | Voice and tone — the four-teacher persona layer (patience, directness with care, "try it and see", education as empowerment); no pedagogy lives here |
| state-ops | Operational surface: project discovery, the `bodhi-state` write path, session-type vocabulary, gate/mastery semantics — what every skill loads |
| state-schema | Field-level reference for `.bodhi/` tracking files (loaded only by manual carve-outs, fallbacks, and `/housekeep`) |
| state-lifecycle | Rotation, archiving, summary collapse, retirement (loaded by `/housekeep` only) |
| state-migration | Schema versioning + one-shot conversion procedures (loaded by `/housekeep migrate`) |

## Path-Scoped Rules (1)

| Rule | Activates On |
|------|-------------|
| learning-project | Files inside `learningWithBodhi/` directories |

## Learning Project Structure

When you start learning, BodhiKit creates a project folder. The v2 layout (1.7.0) uses live documents for the current state and archive directories for the historical detail — routine skills load only the live documents:

```
learningWithBodhi/
├── .bodhi-profile.json            # Top-level profile (career goals, cumulative stats)
├── .bodhi-profile.projects.json   # Per-project metadata (active + completed)
└── react-fundamentals/
    ├── .bodhi/
    │   ├── state.json             # Slim — current position, counts, streak
    │   ├── progress.md            # Latest session + "Summary of earlier sessions"
    │   ├── progress/archive/      # Full text of each archived session
    │   ├── plan/
    │   │   ├── README.md          # Arc overview, current phase pointer
    │   │   └── phase-{N}.md       # Per-phase detailed plan
    │   ├── assessments/
    │   │   ├── latest.md          # Most recent assessment + summary
    │   │   └── archive/           # Full text of each archived assessment
    │   ├── spaced-review.json     # Leitner box system for retention
    │   ├── assessment-history.json # Structured Bloom's-over-time data
    │   └── resources.md           # Curated resources
    ├── exercises/                 # Hands-on exercises
    ├── projects/                  # Larger project work
    └── notes/                     # Your personal notes
```

We recommend backing this with git and a remote repository.

See `docs/example-project/` for a realistic example of what these tracking files look like after a few sessions. Upgrading from any earlier version: run `/bodhikit:housekeep migrate` once per project — see [MIGRATION.md](./MIGRATION.md).

## How a Session Works

Run `/bodhikit:continue` and the plugin handles the entire flow:

```
/continue
  ├── /progress quick → 3-line check-in
  ├── spaced review → quiz on concepts due for review
  ├── /teach        → guided teaching of the next concept
  │     ├── explain with analogies and code examples
  │     ├── work through a problem together
  │     ├── independent exercise
  │     └── quick retention check
  └── /reflect      → end-of-session metacognitive reflection
```

One command. Complete learning session. No need to remember which skills to invoke.

## The Science

BodhiKit integrates these methodologies from the learning-science literature. We stand on the shoulders of giants.

#### An honest note on the claim

- BodhiKit's *design* follows the learning-science literature below — each mechanism cites its primary source and fires where the research says it should.
- What we do not (yet) have is outcome data showing the plugin itself improves learning versus vanilla Claude; the thresholds and intervals are tuned on real but small-N usage.
- "Research-informed" is a design claim, not an efficacy guarantee.
- If you run real learning projects through BodhiKit and want to help change that, open an issue with your (anonymized) experience — what held, what decayed, where the calibration felt off. As of 1.11.3 this is one command: `bodhi-state export-anonymized` produces a shareable stats block (counts and rates only — no concept names, no free text), and the repo has a ["Share your learning data"](./.github/ISSUE_TEMPLATE/learning-data-report.md) issue template for it.
- `bodhi-state retention` shows you the same numbers privately: your %-correct at review time, by spacing gap and by box — the empirical check on whether the intervals are working *for you*.

- The maintainer's own anonymized numbers — one learner, five projects, thin — are published in [docs/outcomes.md](./docs/outcomes.md) and regenerated from `bodhi-state export-anonymized`. They are there to be falsifiable, not persuasive.

#### Evidence tiers

The citations below do not all carry equal weight, and each knowledge base declares which tier it sits in (since 1.11.2):

- **Load-bearing, most-replicated** — retrieval practice, spacing, pretesting, worked examples, successive relearning. John Dunlosky et al., *[Improving Students' Learning With Effective Learning Techniques](https://journals.sagepub.com/doi/10.1177/1529100612453266)* (2013), rates practice testing and distributed practice as the two highest-utility techniques of the ten reviewed.
- **Organizing frameworks** — Bloom's, ZPD, and GROW give structure; they are not measured interventions.
- **Kept with explicit caveats** — growth-mindset interventions show small-to-null average effects in meta-analyses (Sisk et al. 2018; BodhiKit uses only the low-cost language patterns), and deliberate practice's domain-generality claims are contested (Macnamara et al. 2014; BodhiKit uses only the uncontested core: targeted practice with immediate feedback).

Fencing the weak claims is what lets you trust the strong ones.

> **Want to know *why* each one is used and *when* it fires inside BodhiKit?** See **[GUIDE.md → The Pedagogy Behind BodhiKit](./GUIDE.md#the-pedagogy-behind-bodhikit)** — per-methodology cards with what / why / when (skills + phases) / primary source, plus a "How they compose" table mapping methodology clusters to journey phases. The citations below are the primary sources; the GUIDE section explains how BodhiKit operationalizes them.

- **Spaced Repetition** — Review concepts at expanding intervals for durable memory
  - Hermann Ebbinghaus, *[Memory: A Contribution to Experimental Psychology](https://en.wikipedia.org/wiki/Memory:_A_Contribution_to_Experimental_Psychology)* (1885)
  - Sebastian Leitner, *[Learning to Learn](https://en.wikipedia.org/wiki/Leitner_system)* (1972)

- **Learning How to Learn** — Focused/diffuse modes, chunking, interleaving, overcoming procrastination
  - Dr. Barbara Oakley, *[A Mind for Numbers](https://barbaraoakley.com/books/a-mind-for-numbers/)* (2014)
  - Dr. Barbara Oakley and Dr. Terrence Sejnowski, *[Learning How to Learn](https://www.coursera.org/learn/learning-how-to-learn)* (Coursera, most popular online course in the world)

- **Bloom's Taxonomy** — Assess and track skills across 6 cognitive levels (Remember to Create)
  - Benjamin Bloom, *[Taxonomy of Educational Objectives](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy)* (1956)
  - Lorin Anderson and David Krathwohl, *[A Taxonomy for Learning, Teaching, and Assessing](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy#The_cognitive_domain_(knowledge-based))* (2001, revised taxonomy)

- **Zone of Proximal Development** — Calibrate difficulty to where learning is most productive
  - Lev Vygotsky, *[Mind in Society](https://en.wikipedia.org/wiki/Zone_of_proximal_development)* (1978)

- **Feynman Technique** — Explain concepts simply to reveal gaps in understanding
  - Richard Feynman, inspired by his teaching philosophy at Caltech
  - Popularized by James Gleick, *[Genius: The Life and Science of Richard Feynman](https://en.wikipedia.org/wiki/Genius:_The_Life_and_Science_of_Richard_Feynman)* (1992)

- **Deliberate Practice** — Targeted exercises at the edge of ability with immediate feedback
  - K. Anders Ericsson, *[Peak: Secrets from the New Science of Expertise](https://en.wikipedia.org/wiki/Peak:_Secrets_from_the_New_Science_of_Expertise)* (2016)
  - K. Anders Ericsson, *[The Role of Deliberate Practice in the Acquisition of Expert Performance](https://psycnet.apa.org/record/1993-40718-001)* (1993)

- **Growth Mindset** — Feedback that promotes learning over performance
  - Dr. Carol Dweck, *[Mindset: The New Psychology of Success](https://en.wikipedia.org/wiki/Mindset_(book))* (2006)

- **Desirable Difficulties** — Interleaving, retrieval practice, and variation for stronger retention
  - Dr. Robert Bjork and Dr. Elizabeth Bjork, *[Making Things Hard on Yourself, But in a Good Way](https://bjorklab.psych.ucla.edu/research/)* (2011)

- **Pretesting** — Attempting a question *before* instruction improves learning of the material that follows
  - Nate Kornell, Matthew Hays, and Robert Bjork, *[Unsuccessful retrieval attempts enhance subsequent learning](https://psycnet.apa.org/record/2009-09556-006)* (2009)

- **Cognitive Load Theory** — Worked examples and faded scaffolding for novices; expertise reversal for the rest
  - John Sweller, *[Cognitive load during problem solving](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1202_4)* (1988)
  - Sweller, Ayres, and Kalyuga, *[Cognitive Load Theory](https://link.springer.com/book/10.1007/978-1-4419-8126-4)* (2011)

- **Successive Relearning** — Re-retrieving a missed concept to criterion within the session, on top of spaced review
  - Katherine Rawson and John Dunlosky, *[Optimizing schedules of retrieval practice for durable and efficient learning](https://link.springer.com/article/10.1007/s10648-011-9182-7)* (2011)

- **Confidence Calibration** — Tagging answers sure/mostly/guessing *before* the reveal, then tracking the gap
  - Asher Koriat, *[Monitoring one's own knowledge during study](https://psycnet.apa.org/record/1997-04181-008)* (1997)

- **Constructivism and Spiral Curriculum** — Learning by building, revisiting concepts at increasing depth
  - Jean Piaget, *[The Construction of Reality in the Child](https://en.wikipedia.org/wiki/Constructivism_(philosophy_of_education))* (1954)
  - Jerome Bruner, *[The Process of Education](https://en.wikipedia.org/wiki/The_Process_of_Education)* (1960)
  - Seymour Papert, *[Mindstorms: Children, Computers, and Powerful Ideas](https://en.wikipedia.org/wiki/Mindstorms_(book))* (1980)

- **Mastery-Based Learning** — Demonstrate competence before advancing, not time-based
  - Benjamin Bloom, *[Learning for Mastery](https://en.wikipedia.org/wiki/Mastery_learning)* (1968)

- **Metacognition** — Teach learners HOW to learn, not just WHAT to learn
  - John Flavell, who coined the term in *[Metacognition and Cognitive Monitoring](https://psycnet.apa.org/record/1980-09388-001)* (1979)

- **Mentoring Theory** — Career and psychosocial functions of effective mentoring
  - Kathy Kram, *[Mentoring at Work](https://www.researchgate.net/publication/232463073_Mentoring_at_Work_Developmental_Relationships_in_Organisational_Life)* (1985)
  - Sir John Whitmore, *[Coaching for Performance (GROW Model)](https://en.wikipedia.org/wiki/GROW_model)* (1988)

- **Pair Programming** — Collaborative coding that improves learning, quality, and retention
  - Kent Beck, *[Extreme Programming Explained](https://en.wikipedia.org/wiki/Extreme_programming)* (1999)
  - Laurie Williams and Robert Kessler, *[Pair Programming Illuminated](https://collaboration.csc.ncsu.edu/laurie/Papers/ESE%20-%20Single%20Column.pdf)* (2002)
  - Llewellyn Falco, *[Strong-Style Pairing](http://llewellynfalco.blogspot.com/2014/06/llewellyns-strong-style-pairing.html)* (2014)

- **Scientific Debugging** — Systematic, hypothesis-driven approach to finding and fixing bugs
  - Andreas Zeller, *[Why Programs Fail](https://en.wikipedia.org/wiki/Why_Programs_Fail)* (2005)
  - Devon H. O'Dell, *[The Debugging Mindset](https://queue.acm.org/detail.cfm?id=3068754/)* (2017, ACM Queue)
  - Edward J. Gauss, *[Wolf Fence Algorithm](https://dl.acm.org/doi/abs/10.1145/358690.358695)* (1982, ACM)

## Reliability Architecture (1.11.0)

The 1.10.x release line proved a structural lesson: a spec being *correct* is not the same as a spec being *binding* on an LLM executor. 1.11.0 closes that class of bug at the architecture level instead of patching instances:

- **`scripts/bodhi-state`** — a dependency-free Python CLI that performs every tracking-JSON mutation: Leitner box math, the Bloom ratchet, counter rules, `sessionHistory` vocabulary enforcement, the prerequisite-gate verdict, the mastery formula, migration with backup + verification. Skills decide *what happened* (the pedagogical judgment); the script decides *what the file looks like*. Unknown learner fields are preserved in code, atomically.
- **A Stop hook** (`hooks/hooks.json`) that runs `bodhi-state verify` on touched projects before a session ends — broken tracking state blocks the stop once with a repair instruction instead of silently persisting.
- **A three-layer test harness** (`dev/eval/`): a free deterministic suite covering every script contract (run by `dev/check.sh` on every change); headless LLM evals that run real skills against fixture projects and assert on the resulting *file state* — the automated successor to the manual dogfood passes of the 1.10.x line; and (1.12.0) **grading-calibration evals** — scripted learner answers of controlled quality asserted against honest grading bands (a jargon parrot must not pass the Feynman gate; missing trade-offs must cap tested-bloom at 4) — plus transcript-fidelity checks on the teaching protocol itself (pretest fires on first exposure, no fourth hint, ever). The deterministic layer makes the file mechanics trustworthy; the grading layer measures the judgment feeding them, and doubles as the model-drift detector.

## Learn More

[Read the full blog post on Medium](https://medium.com/@anjanj/bodhikit-a-research-backed-ai-coding-tutor-that-teaches-you-instead-of-writing-code-for-you-8c83cba338d9) — detailed scenarios, the science behind the plugin, and how to get the most out of it.

## Uninstall

```
/plugin uninstall bodhikit@bodhikit
```

Your `learningWithBodhi/` project folders are not affected.

## License

MIT

## Support

If this project saves you time, consider sponsoring. It keeps development going and lets me know people are finding it useful.

<a href="https://github.com/sponsors/AnjanJ" target="_blank"><img src="https://img.shields.io/badge/Sponsor_on_GitHub-ea4aaa?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="Sponsor on GitHub"></a>&nbsp;&nbsp;<a href="https://www.buymeacoffee.com/anjanj" target="_blank"><img src="https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=black" alt="Buy Me A Coffee"></a>

---

**Made with ❤️ by [Anjan](https://anjan.dev)**
