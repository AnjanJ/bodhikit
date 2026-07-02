# BodhiKit User Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Upgrading from Earlier Versions](#upgrading-from-earlier-versions)
- [Your Journey from Zero to Completion](#your-journey-from-zero-to-completion)
- [How Teaching Works](#how-teaching-works)
- [When BodhiKit Reaches for an Analogy](#when-bodhikit-reaches-for-an-analogy)
- [End-of-Session Reflection](#end-of-session-reflection)
- [Skills Reference](#skills-reference)
  - [The four routine skills](#the-four-routine-skills) — `/learn`, `/continue`, `/teach`, `/reflect`
  - [Self-knowledge and tracking](#self-knowledge-and-tracking) — `/progress`, `/plan`, `/assess`
  - [Active recall and retention](#active-recall-and-retention) — `/quiz`, `/forget`, `/housekeep`
  - [Deep work skills](#deep-work-skills) — `/practice`, `/review`, `/resources`
  - [When you are stuck or stepping up](#when-you-are-stuck-or-stepping-up) — `/pair`, `/debug-together`
  - [Looking back and looking forward](#looking-back-and-looking-forward) — `/evaluate`, `/mentor`, `/teach-back`
- [How Agents Work Behind the Scenes](#how-agents-work-behind-the-scenes)
- [Using BodhiKit with Books and Courses](#using-bodhikit-with-books-and-courses)
- [Learner Profile](#learner-profile)
- [Understanding Your Progress](#understanding-your-progress)
- [The Pedagogy Behind BodhiKit](#the-pedagogy-behind-bodhikit) — what, why, when each methodology fires
- [How Spaced Repetition Works](#how-spaced-repetition-works)
- [Housekeeping Your Tracking Files](#housekeeping-your-tracking-files)
- [Finishing a Project: the Capstone](#finishing-a-project-the-capstone)
- [Example Project](#example-project)
- [Tips for Effective Learning](#tips-for-effective-learning)
- [Philosophy](#philosophy)

---

## Getting Started

Install BodhiKit:

```
/plugin marketplace add https://codeberg.org/AnjanJ/bodhikit.git
/plugin install bodhikit@bodhikit
```

Restart Claude Code after installing.

**Context tip:** BodhiKit loads 20 knowledge bases. To keep other projects lean, enable it only where you need it. Add to your `learningWithBodhi/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "bodhikit@bodhikit": true
  }
}
```

And disable it in projects where you do not need it via `.claude/settings.local.json`:

```json
{
  "enabledPlugins": {
    "bodhikit@bodhikit": false
  }
}
```

Start your first learning project:

```
/bodhikit:learn python
```

BodhiKit will ask you questions to understand your background, goals, and current skill level. Then it will create a personalized learning plan and give you your first exercise.

---

## Upgrading from Earlier Versions

If you already have learning projects from any version before 1.10, run the one-shot migration once per project:

```
/bodhikit:housekeep migrate
```

You can run it from inside a specific project folder, or from the `learningWithBodhi/` root to convert every project at once.

### What it does

The migration is chained — it runs whichever transforms are missing for your project, in version order. Two targets exist as of 1.10:

**1.7.0 target** (v1 → v2 layout — progressive disclosure). Converts:

- `state.json` — strips long narrative fields (`lastSessionSummary`, `bloomResetNote`); they move to `progress.md` where prose belongs. State stays slim: pointers, counts, current values.
- `plan.md` (monolithic) → `plan/README.md` + `plan/phase-{N}.md` (sectional). Skills like `/teach` and `/continue` load only the current phase, not the whole plan.
- `progress.md` (flat chronological log) → live + archive + summary. The latest session sits at the top; older sessions move to `progress/archive/` with one-line pointers in a summary block.
- `assessment.md` (flat) → `assessments/latest.md` + `assessments/archive/`. Same pattern.
- `.bodhi-profile.json` (monolithic) → `.bodhi-profile.json` (top-level: cumulative stats, patterns) + `.bodhi-profile.projects.json` (per-project metadata).

**1.10 target** (v2 → v3 schema bump on `spaced-review.json`). Per-concept Bloom + Feynman tracking — the fields that make mastery observable end-to-end:

- `concepts[].bloomLevel` (0–6, integer) — current Bloom's level for the concept. Set by `/quiz`, `/teach`, `/practice` as they observe the learner's level. Ratchet-up only.
- `concepts[].feynmanPassed` (boolean) — set to `true` when the learner produces a clear, jargon-free explain-back. Owned by `/teach` (Phase 2 checkpoint / understanding-only path / Phase 5). Set, never unset.
- `concepts[].consecutiveCorrectAtL4Plus` (integer) — running counter for the mastery criterion. Incremented by `/quiz` on correct answers at Bloom 4+; reset to 0 on any incorrect, any partial, or on `/forget` ("consecutive correct" means uninterrupted corrects — a partial breaks the streak).
- New entries in `reviewHistory[]` also include `bloomLevel` to record which level a given quiz question tested at.

Together these fields make the canonical mastery formula computable: `mastered = bloomLevel ≥ 4 AND consecutiveCorrectAtL4Plus ≥ 3 AND box ≥ 4 AND feynmanPassed`.

### Safety

- **Per-target idempotent.** Each transform's marker file (`.bodhi/.migration-1.7.0.md`, `.bodhi/.migration-1.10.md`) tracks whether it has run; running the command twice in a row is a no-op once both markers are present.
- **Non-destructive.** Each transform backs up its pre-state to a dedicated directory (`.bodhi/.pre-1.7.0-backup/`, `.bodhi/.pre-1.10-backup/`) for one minor version each. If anything looks off, you can restore from there.
- **Transparent.** The command prints a before/after byte report scoped to whichever transforms ran, and lists every archive entry it created.
- **End-to-end dogfooded.** The 1.10 transform was hardened through a seven-pass live dogfood on real learning projects (see CHANGELOG 1.10.7 through 1.10.13 for the bugs caught and fixed).

### After migrating

Your skills work exactly as before — just faster, because routine sessions read less context, and Bloom/mastery is now observable in the data instead of inferred. Sessions you don't need (history, full plan arc, prior assessments) stay on disk, accessible by pointer when a situation justifies it (e.g., `/evaluate` reading the full history for trajectory analysis, `/continue` reading recent archive entries when you've been gone for over 30 days).

The new `/housekeep` skill also handles ongoing rotation — at session boundaries, it moves the previous live session into `progress/archive/` and writes a one-line summary pointer. See [Housekeeping Your Tracking Files](#housekeeping-your-tracking-files) for details.

---

## Your Journey from Zero to Completion

The fastest way to understand how BodhiKit fits together is to walk a real learner through it from Day 1 to capstone. Meet **Priya** — a backend Python engineer with 5 years of Django experience who wants to learn **Rust** to write production network services. She has about 10 hours a week and a 10-week target. Her dialogue with BodhiKit below is illustrative — your exact phrasing will differ, but the structure of every interaction is real.

> If you are eager rather than patient, skip to the [Skills Reference](#skills-reference) — every skill has its own deep dive. Come back here when you want to see how they compose.

### Day 1 — Install and start

Priya installs BodhiKit (see [Getting Started](#getting-started)) and runs:

```
/bodhikit:learn rust
```

BodhiKit responds with **Topic Discovery** — clarifying questions to scope the goal:

> "Welcome. Before we begin: what is driving Rust for you — a project, a job, or curiosity? Any languages you bring with you? How much time per week, and what does 'done' look like to you?"

Priya answers: *production network services, strong Python/Django, 10h/week, 10 weeks, target = "comfortable writing a small TCP server with proper error handling and tests."*

BodhiKit then runs **Cross-Project Reconciliation** — since this is her first BodhiKit project, the cross-project profile is empty and this phase passes silently. (If she had three active projects already, BodhiKit would surface a capacity flag here. See [/learn](#learnbodhikitlearn-topic) for details.)

Next, the **skill-assessor agent** takes over for 8–10 adaptive questions. It starts at Bloom Level 3 ("can you apply this?") and adjusts up or down per topic. Priya answers questions on ownership, lifetimes, traits, async, error handling. She knows ownership conceptually but cannot write it; lifetimes are a blank wall; traits feel like Python's duck-typing-meets-interfaces; async she knows from Python. The agent returns a structured assessment:

> Ownership: Level 2 (HIGH conf), Borrowing: Level 1 (HIGH), Lifetimes: Level 0 (HIGH),
> Traits: Level 2 (MEDIUM), Generics: Level 1 (MEDIUM), Error handling (Result/?): Level 1 (HIGH),
> Async: Level 2 (HIGH), Tokio: Level 0 (HIGH), Testing: Level 3 (transferred from Python).

BodhiKit uses this to generate a **personalized learning plan**: 3 phases over ~10 weeks, with modules calibrated to Priya's starting points. Phase 0 (Week 1–2): ownership, borrowing, lifetimes — the hard foundation. Phase 1 (Week 3–6): traits, generics, error handling, modules. Phase 2 (Week 7–10): async runtime, tokio, the TCP server capstone project. The plan is written to `learningWithBodhi/rust-network-services/.bodhi/plan/README.md` plus per-phase files.

Finally, BodhiKit hands her the first exercise: a tiny program that demonstrates ownership transfer. She writes it. She gets her first compiler error. The Day 1 session ends with `/reflect` — three quick questions about what she just learned.

**Time invested:** ~90 minutes. **What now exists:** a `learningWithBodhi/rust-network-services/` folder with `state.json`, a sectional `plan/`, an initial `assessments/latest.md`, and Day 1's session in `progress.md`.

### Week 1 — Settling into the rhythm

Priya opens Claude Code the next day and types one command:

```
/bodhikit:continue
```

That single command runs her entire session. Here is what happens under the hood:

1. **`/progress quick`** fires first — a 3-line check-in: project, current module, streak (today = day 2, streak = 2), concepts due for review (1 concept from Day 1).
2. **Spaced review** — the one due concept gets a quick quiz question. Priya gets it right; the concept moves from Box 1 to Box 2 (next review in 3 days).
3. **`/teach`** is auto-invoked for the next module — *Borrowing*. BodhiKit follows the **I Do → We Do → You Do** flow ([How Teaching Works](#how-teaching-works)). It explains immutable vs mutable borrows with a metaphor about library books, walks her through a sample function, then gives her an exercise. Priya gets stuck — she cannot articulate why the borrow checker is rejecting her code. BodhiKit detects this is the moment for the [Analogy-Escalation Protocol](#when-bodhikit-reaches-for-an-analogy): it has no `learnerBackground.domains[]` on Priya yet, so it asks her once — *"what is a field, hobby, or job you know well?"* She says she gardens. Borrowing gets re-explained as "two people sharing a single pair of pruning shears — they can both look at them, but only one person can be using them at a time, and they have to give them back before the gardener can claim them again." That lands. The exercise unsticks. BodhiKit saves `cooking` and `gardening` to her profile.
4. **`/reflect`** fires when Priya says she is done. Three questions: hardest thing today? (lifetimes peeked their head out and were scary), confidence on borrowing (7/10), would you do anything differently? (she would re-read the chapter slower). Borrowing goes to Box 1 with `nextReview` tomorrow.

**Day 3, Day 4, Day 5** — same shape. `/continue`, ~75 minutes per session, one new concept per day, one or two reviews from prior days. By the end of Week 1, Priya has:

- 5 sessions logged, 5-day streak
- Box distribution: 1 concept in Box 3, 3 concepts in Box 2, 2 concepts in Box 1
- Module 0.1 (Ownership) marked complete, Module 0.2 (Borrowing) at 80%
- A growing `progress.md` — the latest session at the top, a 5-line summary block for the prior 4 sessions, full archives in `progress/archive/`

She has run only two commands so far: `/learn` once on Day 1, and `/continue` four times after. **This is the typical flow.** Every other skill is something to reach for when you have a specific need.

### Week 3 — When something stops clicking

Lifetimes are not making sense. Three sessions in a row Priya has gotten the syntax wrong, the compiler error scrolling for 40 lines. She does not want to just continue — she wants to **check her foundation**. Two skills are useful here:

```
/bodhikit:assess lifetimes
```

A standalone assessment, ~8 questions, 15 minutes. The result lands honestly: *Lifetimes: Level 1 (HIGH confidence) — recognition only, no productive use.* No shame, no judgment. The result also gets written to `assessment-history.json` so `/evaluate` can plot her trajectory later.

```
/bodhikit:teach lifetime elision
```

Priya tells `/teach` she just wants to understand, not exercise — its understanding-only path runs the Feynman deep dive on the specific sub-concept she suspects is the gap. BodhiKit explains it simply, asks her to explain back, finds the gap (she thinks all references need explicit lifetimes), refines with a counter-example. The gap closes, and the concept goes into spaced review to be revisited.

That night she runs `/continue` again and gets back into the rhythm with the foundation a bit firmer.

### Week 4 — Quiz miss, honest demotion

Wednesday morning's `/continue` runs spaced review and Priya gets *trait bounds* wrong. The system would auto-demote it to Box 1, but at the end of the session in `/reflect`, BodhiKit asks her confidence rating on the concepts she touched. She rates *traits* at 4/10 — lower than the algorithm assumed from her two correct answers last week. This is exactly what the `/forget` skill is for, and `/reflect` auto-invokes it:

```
# auto-invoked by /reflect when confidence ≤ 4
/bodhikit:forget traits
```

Traits drop to Box 1. Tomorrow's session will quiz it again. Honest self-assessment beats waiting for three quiz misses.

### Week 5 — Pairing on the first real-world task

Module 1.4 in her plan is a small CLI tool. The plan describes it as a 90-minute exercise. Priya has the Bloom levels but not the *integration* experience — she has written functions, not a whole program. So she invokes:

```
/bodhikit:pair strong-style
```

In **strong-style**, BodhiKit describes what to build (intent, not syntax) and Priya types. "Now create a function that parses a single command-line argument as a u32, returning a custom error if it fails." She types. When she gets stuck on syntax, BodhiKit gives the minimum hint — *"The function signature you want returns `Result<u32, MyError>`"* — but never types the code. After 20 minutes the roles reverse: she navigates, BodhiKit "drives" by describing what it would type. By the end she has a 60-line CLI, working tests, and a felt sense of building something whole.

### Week 6 — Debugging a real bug

Her tokio server is dropping connections silently. She does not want a fix; she wants to learn to debug Rust. So:

```
/bodhikit:debug-together src/server.rs
```

BodhiKit refuses to look at the code first. Phase 1: reproduce the bug precisely. Phase 2: hypothesize — what is Priya's theory? She thinks the listener is being dropped. Phase 3: a single targeted probe (a `dbg!` macro on the listener's drop point), not three random `println!`s. Phase 4 (Wolf Fence): binary-search the request lifecycle. Phase 5: the learner proposes the fix. She traces it: she was awaiting the wrong future. She writes the fix. Phase 6: reflect on what made the bug findable — the discipline of probing before changing. The bug also revealed a conceptual gap in her understanding of how `tokio::spawn` works with futures; that concept goes into `spaced-review.json` as a new Box-1 entry.

### Week 7 — Mid-journey checkpoint

She is past the foundation and starting the async track. She wants to take stock:

```
/bodhikit:evaluate
```

This is **not** a quiz. BodhiKit announces upfront that it is going to take a few minutes: it launches the **trajectory-analyzer agent** to read her entire history (all archives, all assessments, the spaced-review trail, every plan phase) in the agent's context — keeping her conversation light. Then it runs a fresh ~15-question assessment across the full plan via the skill-assessor agent. Then it synthesizes.

> "Here is the path you have walked. Ownership went 2 → 3 → 4 over Weeks 1–6, evidence from your Week-3 session: 'I rewrote the function so the caller owns the buffer.' Lifetimes went 0 → 1 → 2 — you have a working model now but stumble on multi-lifetime signatures (Week 5 quiz miss). Strong work on testing — Level 3 transferred from Python, now Level 4. Persistent challenge: trait bounds, three rounds of demote-and-recover. The plan still fits; suggest staying the course for Phase 2 (async/tokio). One thing worth naming: you have built a real CLI, debugged a real bug, and shipped your own tests. That is what Phase 1 was for."

Mid-journey `/evaluate` does NOT trigger the capstone offer — that only fires when a project moves to `completedProjects`. It can, however, *offer* `/mentor` when she is at a fork in the road (a major Bloom milestone) — accepting is always her call.

### Week 8 — A path question

Priya is starting to wonder: after Rust, what comes next for production network engineering? Should she go deeper in Rust (zero-copy, no-alloc, embedded?), or should she pivot to a related stack (Go for SRE work? Erlang/OTP for fault-tolerance?). She runs:

```
/bodhikit:mentor
```

`/mentor` uses the **GROW model** (Goal, Reality, Options, Will). It reads her full learner profile and the projects file, maps her skill landscape against her career goal, and presents 2–3 concrete next-project options with honest trade-offs. It will not romanticize the answer; if she does not have the foundation to specialize yet, it will say so. It is also honest about what AI cannot do — sponsorship, networking, vouching. The output is not a decision, it is a structured conversation that helps her make one.

### Week 10 — Completion

The capstone TCP server is built. Tests pass. `state.json` shows 100% module completion. Priya runs:

```
/bodhikit:evaluate
```

This time the evaluation moves the project from `activeProjects` to `completedProjects`. `cumulativeStats.totalConceptsLearned` and `totalMilestonesReached` bump. The closing section emits a one-paragraph **opt-in offer**:

> "You have walked this path well. There is one optional thing to consider before we close the book on this project: a teach-back. It is not a victory lap — it is a chance to write something defensible on a topic that was once hard for you. The candidates I would suggest are lifetimes, trait bounds, and tokio's spawn semantics — each of these climbed from Bloom < 3 to ≥ 4 in your history, and each has at least one demote-and-recover in your spaced review. Would you like to write a teach-back? You can skip this — completion already happened."

Priya picks lifetimes. She runs:

```
/bodhikit:teach-back
```

She drafts the post in her own voice, Socratically prompted by BodhiKit. *Then* — and only then — BodhiKit surfaces 3–5 acknowledged masters on lifetimes (the Rustonomicon, Niko Matsakis's blog, the *Programming Rust* chapter, a Without Boats post). She reads them with her draft already in hand. She revises. Two of her claims do not survive the masters; she strikes them. The rest survives sharper than before. She decides to publish — not because BodhiKit told her to, but because she can defend every remaining claim.

The post lives at `learningWithBodhi/rust-network-services/teach-backs/2026-08-19-lifetimes-without-the-handwave.md`. She keeps editing it in her normal workflow.

**Total journey:** ~10 weeks, ~70 sessions, ~$0 in BodhiKit cost (it is open source — see the [README](./README.md) for sponsorship if it earned her time back).

### What Priya never had to do

- Manage tracking files by hand (`/housekeep` ran when needed)
- Decide which skills to invoke daily (`/continue` orchestrated everything)
- Remember what was due for review (spaced repetition tracked it)
- Search for resources blind (`/resources` agent verified links)
- Wonder if she was making progress (`/progress`, `/evaluate` made it visible)

### The shape of the journey, abstracted

| Phase | What it feels like | Skills that matter most |
|---|---|---|
| Day 1 | Onboarding | `/learn` |
| Week 1–2 | Settling in | `/continue` (daily), `/reflect` (auto) |
| Week 3–4 | First stalls and corrections | `/assess`, `/teach`, `/forget`, `/quiz` |
| Week 5–6 | First real-world building and bugs | `/pair`, `/debug-together`, `/practice` |
| Week 7 | Mid-journey checkpoint | `/evaluate`, `/mentor` |
| Week 8–9 | Steady deep work | `/continue`, `/teach`, `/review` |
| Week 10 | Completion | `/evaluate` → optional `/teach-back` |
| After | Looking back / next project | `/mentor`, then `/learn <next-topic>` |

You will run `/continue` more times than every other skill combined. That is the point. Other skills are tools you reach for when you have a specific need.

---

## How Teaching Works

When you choose to continue with the next module (or run `/bodhikit:teach` directly), BodhiKit follows the **Gradual Release of Responsibility** model:

1. **I Do (Modeling)** — BodhiKit explains the concept with analogies, concrete code examples, and connects it to what you already know. It shows WHY the concept matters, not just what it does.

2. **We Do (Guided Practice)** — You and BodhiKit work through a problem together. It asks guiding questions: "How would you start? What data structure fits here?" You make the decisions, it keeps you on track.

3. **You Do (Independent Practice)** — BodhiKit gives you an exercise calibrated to your level. Beginners get starter files with TODO comments. Advanced learners get a problem statement only. You solve it yourself.

4. **Verify** — Quick retention check: 2-3 questions to confirm the concept stuck. Concepts are added to spaced repetition tracking.

The key rule: BodhiKit never lectures for more than 5 minutes without interaction. It is a conversation, not a presentation.

---

## When BodhiKit Reaches for an Analogy

Sometimes the first explanation does not land. The words are right, the code example is correct, but the concept has not arrived. When this happens, BodhiKit follows a deliberate four-rung ladder rather than throwing random analogies at you. This applies inside `/teach` (full sessions and understanding-only deep dives), `/debug-together`, and `/pair`.

### How BodhiKit notices you are stuck

It watches for a specific pattern, not a general feeling of struggle. Productive struggle is good — you should sit with it. The protocol fires only when:

- You cannot articulate what is confusing ("I just don't get it").
- The first explanation drew a blank — no echo of the key terms, no question, no partial attempt.
- An Approach-level hint (hint 2 of 3) did not move you forward.
- Your explain-back is correct in words but mechanical — no sign of the underlying mental model.
- A misconception survives one corrective re-explanation.

It does NOT fire on a single wrong answer to a hard question, or on a request for "more examples" — those are normal.

### The four rungs

**Rung 1 — Your own world.** BodhiKit reads `learnerBackground.domains[]` in your profile and constructs the analogy from a field you actually know. If you told it you cook, recursion gets explained as "a recipe that mid-step says 'now do this entire recipe with half the ingredients, then continue.'" If you play music, pure functions become "a scale played the same way every time — the room, the time, what came before, none of it changes the sound."

**Rung 2 — Asking once.** If your profile has no domains (or all listed domains have already been used for this concept), BodhiKit asks one question: "Before we keep going — what is a field, hobby, or job you know well? Cooking, sports, music, plumbing, accounting, anything. The next explanation will land better if I can borrow from it." Your answer gets saved so future sessions can use it without asking again. If you say "just explain it," the protocol drops to rung 3.

**Rung 3 — Universal physical.** Stoves, mailboxes, libraries, road maps, water flow, locks-and-keys. These are weakest because they are pre-cached for every learner — but they are still better than restating the same explanation a second time.

**Rung 4 — Code-restatement.** A second concrete code example that says the same thing differently (different data type, different scale). Used only when analogies have failed and the next step is to back off the concept anyway.

### The two-analogy cap

After two analogies on the same concept without traction, BodhiKit stops climbing. Reaching for a third would teach you the analogy instead of the concept. The right move at that point is not a better analogy — it is to back off and teach a smaller prerequisite first. You will hear something like: "Let us set [concept] down for a moment. There is a smaller piece underneath it that we should make solid first."

This is not a setback. It is the protocol working correctly. The original concept comes back into view once its foundation is in place.

### What gets remembered

Every analogy BodhiKit uses is logged with whether it landed for you. Next time the same concept comes up, it reaches for a different domain — so you do not get the same cooking-recursion story twice. This data lives in `.bodhi-profile.json` and is cross-project: domains you know carry over from your React project to your Rust project.

---

## End-of-Session Reflection

When you say goodbye, BodhiKit auto-invokes `/reflect` to run a brief metacognitive reflection. This takes 3-5 minutes and multiplies the value of the entire session.

It asks:
1. **What felt hardest today?** — Identifies concepts that need more time
2. **Was anything easier than expected?** — Calibrates your self-assessment
3. **Confidence rating (1-10)** — Low confidence concepts get scheduled for review sooner
4. **What would you do differently?** — Builds strategic thinking about learning itself

Why this matters: research shows learners who reflect on their learning process retain 20-30% more. Your confidence rating feeds directly into the spaced repetition system, so concepts you are unsure about get reviewed sooner.

---

## Skills Reference

Eighteen user-invocable skills, grouped by what they do for you. Each entry follows the same five-field structure: **What it does · When to use · When NOT to use · Pairs well with · Example**. The journey arc above shows them in context; this reference is the manual you reach for when you have a specific need.

### The four routine skills

These four are the ones you will run most often. Together they orchestrate a complete learning session.

#### `/bodhikit:learn [topic]`

**What it does.** Starts a new learning project. Runs topic discovery, cross-project reconciliation (if you have other projects), an adaptive skill assessment via the skill-assessor agent, plan generation, and gives you your first exercise. Creates `learningWithBodhi/<project-name>/` and its `.bodhi/` tracking files.

**When to use.** You are starting on a topic you have not learned before. Or you have a new project goal that is meaningfully distinct from your existing tracks (Phase 1.5 will tell you if it is not).

**When NOT to use.** You want to top up an existing project — use `/continue` instead. You only want to *check* a skill without committing to a plan — use `/assess`. You want career-arc guidance before picking the next topic — use `/mentor` first.

**Pairs well with.**
- `/mentor` — run it *before* `/learn` when you are unsure which topic to pick next.
- `/resources` — once the plan exists, find verified materials for it.
- `/continue` — every subsequent session of this project.

**Example.**
```
/bodhikit:learn rust
```
> "Welcome. Before we begin: what is driving Rust for you — a project, a job, or curiosity? Any languages you bring with you? How much time per week, and what does 'done' look like to you?"

Expect ~60–90 minutes for the full Day 1: discovery, ~8 assessment questions, plan generation, project scaffolding, and the first exercise (it closes by pointing you at `/bodhikit:continue` for tomorrow). Subsequent sessions are 30–90 minutes via `/continue`.

#### `/bodhikit:continue [project-name]`

**What it does.** The orchestrator. Resolves your project (auto-detect or by name), runs `/progress quick`, surfaces any concepts due for spaced review, auto-invokes `/teach` on the next module, and auto-invokes `/reflect` when you indicate you are done. One command runs an entire session.

**When to use.** Every regular learning session after Day 1. This should be your default.

**When NOT to use.** You have a specific, focused need (`/teach` a single concept — understanding-only is fine, `/quiz` yourself, `/debug-together` a bug). For routine practice, prefer this.

**Pairs well with.**
- Every other skill — `/continue` auto-invokes the right ones at the right time.
- `/progress` — when you want a wider view than its own 3-line quick check-in.

**Example.**
```
/bodhikit:continue
```
> "Welcome back. Day 12 with this project. Last time, you were working on Module 1.3 — trait bounds. One concept is due for spaced review: 'lifetime elision rules.' Shall we run the review first, then continue with the next module — generic functions? Or pick something else?"

#### `/bodhikit:teach [topic|next]`

**What it does.** Proactive guided teaching of a single concept. Follows **I Do → We Do → You Do**: BodhiKit explains the concept, walks you through a sample together, then gives you an exercise calibrated to your Bloom level. Verifies retention with 2–3 questions at the end. If you get stuck, the [Analogy-Escalation Protocol](#when-bodhikit-reaches-for-an-analogy) fires.

**When to use.** You want focused instruction on a specific concept (e.g., `/teach pattern matching`). Auto-invoked by `/continue` for the next-untaught concept in your plan.

**When NOT to use.** You have not started a project (use `/learn` first — there is no Bloom calibration to teach from). You want to test yourself rather than be taught (use `/quiz` or `/assess`).

**Pairs well with.**
- `/practice` — invoked inside `/teach` for the You-Do phase, but standalone for follow-up exercises.
- `/pair` — offered during the We-Do phase when collaborative coding fits better than guided discussion (you accept or decline).
- `/debug-together` — offered from the You-Do phase if your exercise produces a bug worth debugging together.

**Example.**
```
/bodhikit:teach lifetimes
```
> "Lifetimes. Let us start with why they exist. A reference points at memory owned by something else — and that something else can disappear. The compiler needs to know how long a reference is valid so it never points at memory that has been freed. Lifetimes are the syntax for telling the compiler 'this reference is valid as long as that data is alive.' Here is a tiny example, then we will build one together, then you will write one alone."

**Pedagogy:** [ZPD / Gradual Release](#3-zone-of-proximal-development-vygotsky), [Bloom](#1-blooms-taxonomy), [Feynman](#4-feynman-technique), [Desirable Difficulties](#6-desirable-difficulties-bjork).

#### `/bodhikit:reflect`

**What it does.** End-of-session metacognitive reflection. Asks four short questions (hardest concept today, what surprised you, confidence ratings, what would you do differently), records a Leitner update for concepts not already reviewed today — the retrieval outcome decides the box, the rating is pure calibration signal — auto-invokes `/forget` when confidence ≤ 4 or retrieval fails, and writes the session summary to `progress.md`. You can run `/housekeep` afterwards when the live docs feel heavy.

**When to use.** Every session, at the end. Auto-invoked by `/continue` when you say goodbye. Even when you are running solo skills, take 3 minutes to reflect — research shows reflection is where ~20–30% of retention comes from.

**When NOT to use.** You just spent 5 minutes asking a one-off question — there is no session to reflect on. You are in the middle of a session and not ready to close — reflection works best at the end.

**Pairs well with.**
- `/forget` — auto-invoked when you rate a concept low.
- `/housekeep` — run it at session boundaries to rotate the previous entry into the archive (`/continue` may offer it after long sessions).

**Example.**
```
/bodhikit:reflect
```
> "Before we close — what felt hardest today? ... Was anything easier than you expected? ... On a scale of 1–10, how confident do you feel about lifetimes right now? About trait bounds? ... If you replayed today's session, would you do anything differently? Even one sentence is enough."

**Pedagogy:** [Metacognition](#8-metacognition-flavell), [Growth Mindset](#7-growth-mindset-dweck).

---

### Self-knowledge and tracking

These three skills let you see what you know, what you have planned, and where you are heading.

#### `/bodhikit:progress [quick|all|project-name]`

**What it does.** Three views on the same question, at three depths. **`quick`**: a flourish-free 3-line check-in (project, current module + completion, streak, concepts due today) — this is what `/continue` shows first. **No argument** (or a project name): the full dashboard — module completion with mastery %, Bloom level per sub-topic, spaced-review retention by box, confidence calibration once you have tagged quiz answers, and a growth-trajectory closing. **`all`**: a one-line-per-project table across active, stale, and dormant tracks with health flags (unmigrated files, broken JSON, incomplete layouts).

**When to use.** `quick` when you want "where am I?" without committing to a session. The dashboard weekly or bi-weekly to take stock, or before deciding whether to push forward or shore up foundations. `all` when you run multiple projects and want the portfolio view.

**When NOT to use.** You want trajectory analysis ("how did I get here, and what next?") — use `/evaluate`, which is much deeper and narrative.

**Pairs well with.**
- `/continue` — auto-invokes `/progress quick` as its first phase.
- `/evaluate` — when you want narrative + recommendations on top of the numbers.
- `/plan adjust` — when the dashboard suggests pacing problems.

**Example.**
```
/bodhikit:progress all
```
> | Project | Phase/Module | Done | Last session | Status | Health |
> |---|---|---|---|---|---|
> | rust-network-services | Phase 1 · M1.3 | 60% | 2d ago | active | |
> | react-fundamentals | Phase 2 · M2.4 | 78% | 6w ago | dormant | |
> | system-design | Phase 0 · M0.2 | 10% | 6mo ago | dormant | ⚠ v1 fields |

#### `/bodhikit:plan [view|adjust|regenerate]`

**What it does.** Read, adjust, or regenerate your learning plan. `view` (default) prints `plan/README.md` plus the current phase. `adjust` opens a focused conversation about pace or scope — extend a phase, reorder modules, drop a sub-topic, change cadence. `regenerate` runs a fresh skill assessment and rebuilds the plan from current Bloom levels.

**When to use.** `view` — when you want to see where you are heading. `adjust` — when life happened (busy week, faster pace, scope creep). `regenerate` — when the original plan has drifted too far from reality (typically after 3+ months or a major skill shift).

**When NOT to use.** You want to skip a single concept rather than restructure — just say so during `/teach` ("let us skip pattern matching for now"). `regenerate` is heavy; do not run it for small course corrections.

**Pairs well with.**
- `/evaluate` — its recommendations may suggest a `/plan adjust`.
- `/mentor` — for arc-level changes (different topic entirely).

**Example.**
```
/bodhikit:plan adjust
```
> "Looking at your plan: Phase 1 was scoped for 4 weeks and you are 6 weeks in. Two options I see — (1) keep current pace, push Phase 2 out 2 weeks, or (2) trim Module 1.4 (Macros) which the trajectory shows you are not blocking on. Which fits better?"

#### `/bodhikit:assess <topic>`

**What it does.** A standalone skill assessment on any topic — no project commitment, no plan generation. Runs the skill-assessor agent for 8–12 adaptive questions, returns Bloom level per sub-topic with confidence ratings. Writes a structured entry to `assessment-history.json` if you are inside a learning project.

**When to use.** You want an honest read on a topic before deciding whether to learn it (or if you already "know" it). You suspect a sub-topic in your active project is shakier than its quiz history suggests. You are gauging your readiness for a job interview, a new role, a contribution.

**When NOT to use.** You want to *learn* the topic — use `/learn` (which includes an assessment). You want to quickly test a single concept — use `/quiz`. You want to know how much you have grown over time — use `/evaluate`.

**Pairs well with.**
- `/teach` — when an assessment surfaces a specific gap (its understanding-only path is enough to close it).
- `/learn` — when the assessment reveals you should formalize this into a project.

**Example.**
```
/bodhikit:assess kubernetes
```
> An 8–12 question assessment exploring pods, services, ingress, RBAC, networking, persistence, operators. Returns per-sub-topic Bloom levels with confidence and a one-paragraph honest read.

---

### Active recall and retention

These three skills keep what you have learned from leaking out.

#### `/bodhikit:quiz [topic|current]`

**What it does.** 5–7 adaptive questions on a concept (or on the concepts currently due for spaced review). Uses active recall — no multiple-choice, you generate the answer. Updates Leitner boxes based on your answers per the [spaced repetition](#how-spaced-repetition-works) rules.

**When to use.** Concepts are due for review (`/continue` auto-invokes this — you rarely need to invoke directly). You want to test yourself on a specific concept on demand (`/bodhikit:quiz lifetimes`).

**When NOT to use.** You are still learning the concept for the first time — `/teach` covers it. You want to *measure* level rather than *retain* — use `/assess`.

**Pairs well with.**
- `/continue` — auto-invokes for due concepts.
- `/forget` — when you realize after the quiz that your "passing" answer was lucky.

**Example.**
```
/bodhikit:quiz async
```
> 5 questions on async/await semantics — return types, executor pinning, send-bound futures, cancellation safety, the cost of `.await`. Box updates write to `spaced-review.json`.

**Pedagogy:** [Spaced Repetition](#2-spaced-repetition-ebbinghaus--leitner), [Desirable Difficulties](#6-desirable-difficulties-bjork) (retrieval > recognition).

#### `/bodhikit:forget <concept>[, <concept>, ...]`

**What it does.** Learner-initiated demotion of one or more concepts back to Box 1 — they will be re-quizzed tomorrow. Honest self-assessment. Auto-invoked by `/reflect` when you self-rate confidence 1–4 on a concept.

**When to use.** The moment you notice a concept has slipped. You "passed" a quiz on it but felt unsure. You can no longer recall something you knew last week. You read your own code from a month ago and could not explain a section.

**When NOT to use.** You want to remove the concept entirely from review — `/forget` only demotes, it does not delete. (Delete by editing `spaced-review.json` directly, but rarely worth doing.)

**Pairs well with.**
- `/reflect` — auto-invokes `/forget` for low-confidence concepts.
- `/teach` — once a concept is back in Box 1, an understanding-only deep dive makes the next quiz land.

**Example.**
```
/bodhikit:forget lifetime elision, trait bounds
```
> "Demoted: 'lifetime elision' (was Box 3), 'trait bounds' (was Box 2). Both back to Box 1, reviewing tomorrow. Honest self-assessment is how mastery sticks — well-named."

**Pedagogy:** [Metacognition](#8-metacognition-flavell), [Spaced Repetition](#2-spaced-repetition-ebbinghaus--leitner).

#### `/bodhikit:housekeep [migrate|--dry-run]`

**What it does.** Tends the garden of your `.bodhi/` tracking files. Default mode rotates the previous live session entry into `progress/archive/` and writes a one-line summary pointer back. Same for assessments. `migrate` converts pre-1.7.0 tracking files to the v2 layout (one-shot, idempotent, non-destructive). `--dry-run` reports what would change without writing.

**When to use.** `/continue` may invoke it at session end when entries pile up, but do not rely on that — run it yourself when `progress.md` feels heavy and you want to compact before continuing. After upgrading from 1.6.x → 1.7+ — run `/housekeep migrate` once per project (or once at the `learningWithBodhi/` root for all projects).

**When NOT to use.** You think it might lose data — it cannot. Archives are permanent and never edited.

**Pairs well with.**
- `/continue` — MAY invoke it silently when un-housekept state is detected.
- `/reflect` — pairs naturally; housekeep right after closing a session.

**Example.**
```
/bodhikit:housekeep --dry-run
```
> "Would rotate: 1 session entry from `progress.md` (Week-7 session, 2026-07-14) → `progress/archive/session-2026-07-14.md`. Would append a 4-line summary pointer to the live doc. No assessment rotation needed (no new assessment since last `/housekeep`). Live `progress.md` would go from 4.2 KB to 1.8 KB. Re-run without `--dry-run` to apply."

---

### Deep work skills

These three go beyond the routine when you need depth, materials, or a code-level conversation. (Want a Feynman-style deep dive on a single foggy concept? That lives inside `/teach` now — say "explain X" or decline the exercise, and `/teach` runs explain → explain-back → gap analysis → refinement at full depth, records the result, and stops. Typically 15–30 minutes for a meaty concept.)

#### `/bodhikit:practice [topic|next]`

**What it does.** A hands-on exercise calibrated to your current Bloom level on the topic. Beginners get a faded sequence (annotated worked example → completion problem → full problem, per cognitive-load theory); intermediate learners get a description and test cases; advanced learners get a problem statement only. After you solve it, the code-reviewer agent runs an educational review (what your code reveals about your understanding, not production-quality nits). Offers `/debug-together` if your code has a real bug (after the second hint).

**When to use.** You want to *do*, not just understand. You finished a `/teach` and want a second rep at greater independence. You want a calibrated drill on a specific weak spot.

**When NOT to use.** You have not been taught the concept — use `/teach` first. You want to play freely without a calibrated exercise — just open a file and code.

**Pairs well with.**
- `/teach` — invokes `/practice` for the You-Do phase.
- `/review` — once you have working code, review it for what it reveals.
- `/debug-together` — offered when your practice code has a real bug.

**Example.**
```
/bodhikit:practice error handling
```
> "Write a function `parse_config(path: &str) -> Result<Config, ConfigError>` that handles file-not-found, invalid TOML, and missing-required-field cases distinctly. No starter code — you are at Bloom Level 3 on errors. Tests are in `exercises/error-handling/tests.rs`. When you have a working version, say so and I will look at it."

**Pedagogy:** [Deliberate Practice](#5-deliberate-practice-ericsson), [Constructivism](#9-constructivism--spiral-curriculum-piaget-bruner-papert), [Bloom](#1-blooms-taxonomy) (calibration).

#### `/bodhikit:review [file-path|repo-url]`

**What it does.** Educational code review. Works on local files, GitHub, GitLab, Codeberg URLs. Launches the code-reviewer agent in its own context to read the code; the agent returns observations about what the code reveals about your understanding (concepts demonstrated, misconceptions visible, idiomatic patterns you are ready to learn). NOT a production review — no nit-picking style or naming unless they reveal a learning opportunity. Appends what the code revealed to `progress.md`.

**When to use.** You wrote something on your own (outside a `/practice` exercise) and want a learning-focused read. You wrote code last month and want a re-read with fresh eyes. You inherited code from a tutorial and want to be questioned about what each part does.

**When NOT to use.** You want production-grade review (use a real reviewer or `/code-review`-style tooling). You want to debug a specific failure — use `/debug-together`.

**Pairs well with.**
- `/practice` — for the post-exercise review.
- `/teach` — when the review surfaces a gap worth Feynman-treating (understanding-only path).

**Example.**
```
/bodhikit:review src/server.rs
```
> "Read your file. You used `Arc<Mutex<…>>` for shared state — clean choice. Two things to think about: (1) what happens if a handler panics while holding the lock? (2) you call `.lock().unwrap()` four times in handle_request — what does this signal about the function's job? I am not asking you to refactor; I am asking what your design is telling you."

#### `/bodhikit:resources [find <topic>|add <url-or-name>|list|remove <name>]`

**What it does.** Find, add, list, or remove learning materials. `find` launches the resource-finder agent to search the web for verified free resources, ranked by community reputation and link-aliveness. `add` registers a book, course, video, or repo you are already using — BodhiKit maps it to your plan modules. `list` shows what is registered. `remove` deletes an entry.

**When to use.** Starting a new project and want a curated reading/practice list. The plan mentions a concept and you want concrete materials for it. You bought a book/course and want BodhiKit to use it as a primary or supplementary material.

**When NOT to use.** You want BodhiKit to *teach* a concept rather than point you at materials — use `/teach`. You want recent news/blogposts on a topic — `find` prioritizes durable resources (official docs, structured courses, top books), not freshness.

**Pairs well with.**
- `/learn` — at project start, find resources for the plan.
- `/teach` — when explaining a concept, BodhiKit may point to a registered resource for deeper reading.

**Example.**
```
/bodhikit:resources find tokio
```
> "Verified free resources for tokio:
> 1. The official Tokio tutorial (https://tokio.rs/tokio/tutorial) — best starting point.
> 2. *Asynchronous Programming in Rust* (the async book, official) — concept depth.
> 3. Jon Gjengset's *Decrusting the Tokio crate* YouTube talk — internals.
> 4. Tokio examples repo (github.com/tokio-rs/tokio/tree/master/examples) — read-and-modify."

---

### When you are stuck or stepping up

These two skills are for the moments learning gets concrete: real bugs, real code, real time with the keyboard.

#### `/bodhikit:pair [strong-style|ping-pong|navigate]`

**What it does.** Pair programming with BodhiKit. Three research-backed modes. **strong-style** (Falco): BodhiKit navigates by describing intent ("create a function that takes a vec and returns the sum"), you type. **ping-pong** (TDD): BodhiKit writes a failing test, you make it pass, then you write the next test. **navigate**: you describe the approach, BodhiKit follows your lead and asks strategic questions. Mode auto-selects from your Bloom level (1–2 → strong-style, 3–4 → ping-pong, 5–6 → navigate). After 15–20 minutes, roles reverse.

**When to use.** You have the concept but not the integration experience — you have written functions but not a whole program. You want active typing with a thinking partner, not solo struggle. You are ready to step up from guided exercises to building something real.

**When NOT to use.** You do not yet know the concept — use `/teach` first. You want passive instruction — `/pair` is high-engagement, always typing. You have only 10 minutes — `/pair` sessions are 20–40 minutes minimum.

**Pairs well with.**
- `/teach` — offers `/pair` during the We-Do phase for collaborative coding (you accept or decline).
- `/practice` — `/pair` is an active alternative when a solo exercise feels too lonely.
- `/debug-together` — when pairing surfaces a bug worth a systematic dive.

**Example.**
```
/bodhikit:pair strong-style
```
> "Strong-style today. For an idea to go from my head into the computer, it must go through your hands. We are going to build a small CLI that takes a port number and serves 'hello' on it. Start by creating `src/main.rs` with a `main` function that prints 'starting on port…' — pick how to parse the port from argv when you are ready."

**Pedagogy:** [Pair Programming](#11-pair-programming-beck-williams--kessler-falco), [ZPD](#3-zone-of-proximal-development-vygotsky) (mode auto-selects on level).

#### `/bodhikit:debug-together [file-path]`

**What it does.** Scientific debugging using **Zeller's TRAFFIC method** (Track, Reproduce, Automate, Find origins, Focus, Isolate, Correct) plus **wolf-fence binary search** (Gauss). Six phases: reproduce, hypothesize, probe (not fix), isolate, fix, reflect. Refuses to look at the code before you can reproduce the bug. Refuses to fix the bug for you. Catches novice anti-patterns (random changes, print-spam without hypothesis, ignoring error messages) and redirects.

**When to use.** You have a real bug and want to *learn the debugging skill*, not just get the fix. You have been staring at the code for 20 minutes and you do not have a hypothesis yet — `/debug-together` makes you generate one. You are about to add seven `println!` statements at random — stop, run this instead.

**When NOT to use.** You need the fix immediately for production and learning comes second — get the fix elsewhere; come back later with `/debug-together` for the lesson. You are confident this is a typo, not a model gap — fix it directly.

**Pairs well with.**
- `/practice` — offers `/debug-together` when your practice code has a real bug.
- `/teach` — offers it when an exercise produces a bug.
- `/teach` — when the bug reveals a concept gap, an understanding-only deep dive after the fix closes it.

**Example.**
```
/bodhikit:debug-together src/server.rs
```
> "Before we look at the code: what did you expect to happen, and what actually happened? Walk me through the exact steps to reproduce. If you have an error message, read it to me out loud."

**Pedagogy:** [Scientific Debugging](#12-scientific-debugging-zeller--gauss--odell), [Growth Mindset](#7-growth-mindset-dweck) (bugs are clues).

---

### Looking back and looking forward

These three skills are the long-arc ones — for evaluating where you have been and deciding where to go next.

#### `/bodhikit:evaluate [project-name]`

**What it does.** A comprehensive evaluation of your entire journey on a project. Launches the trajectory-analyzer agent to read your full history (every archive, every assessment, every plan phase, the spaced-review trail) in the agent's context so your conversation stays light. Then asks you three quick predictions (biggest growth, biggest gap, per-topic Bloom guesses) BEFORE any evidence — calibration is measured against your standing self-model, not how the last 20 minutes felt. Then runs a fresh ~15-question assessment via the skill-assessor agent. Then synthesizes: per-topic Bloom trajectory with evidence quotes, retention distribution, biggest growth areas, persistent challenges, what to do next. At completion or a major milestone the closing turn offers `/mentor` and (on completion, which you confirm explicitly) `/teach-back` — both opt-in, never auto-invoked.

**When to use.** Mid-journey checkpoint (every 6–10 weeks, or at the end of a major phase). End-of-project for the completion verdict. After a long break (1+ month) to recalibrate.

**When NOT to use.** You want a quick read — use `/progress`. You want to test a single concept — use `/quiz` or `/assess`. You want career-arc guidance — use `/mentor` (`/evaluate` offers it at milestones).

**Pairs well with.**
- `/mentor` — auto-invoked from `/evaluate` when it spots a fork.
- `/teach-back` — offered as opt-in only when evaluation moves the project to `completedProjects`.
- `/plan adjust` — when evaluation reveals pacing or scope issues.

**Example.**
```
/bodhikit:evaluate
```
> "Let us look at the full path you have walked. I am pulling together the entire history — sessions, assessments, retention, growth patterns. Take a breath; this will take a moment to assemble." (Spawns trajectory-analyzer agent, then runs fresh assessment, then synthesizes a multi-section evaluation report — typically 15–25 minutes elapsed.)

#### `/bodhikit:mentor [question]`

**What it does.** Career and learning-path guidance using **Whitmore's GROW model** (Goal, Reality, Options, Will) and **Kram's mentoring functions** (career + psychosocial). Reads your full learner profile and every project, maps your skill landscape against your career goals, presents 2–3 concrete options with honest trade-offs, asks which fits. Honest about what AI cannot do — sponsorship, networking, vouching. The output is a structured conversation, not a decision.

**When to use.** You are between projects and unsure which topic comes next. You have a career goal and want to map your skills against it. You are wondering if you are ready for a specific role or contribution. After `/evaluate` completes a project and the closing turn invites a path conversation.

**When NOT to use.** You want a single topic recommendation without the conversation — `/mentor` is structured dialogue, not an oracle. You want emotional support rather than mentoring — that is not what this skill does (it is honest, sometimes uncomfortably so).

**Pairs well with.**
- `/evaluate` — auto-invokes `/mentor` at milestones.
- `/learn` — `/mentor` typically ends by offering to `/learn <chosen-topic>`.

**Example.**
```
/bodhikit:mentor
```
> "Let us go through this together. What is the goal you are working toward — concrete, time-bound if possible? ... Where are you with it right now — honestly? ... I see three plausible next-projects given your skills and that goal. Let me lay them out with what each costs and what each gets you."

**Pedagogy:** [GROW + Kram's mentoring functions](#10-mentoring-theory-kram--whitmore-grow).

#### `/bodhikit:teach-back`

**What it does.** Optional capstone, offered only after `/evaluate` confirms a project is complete. You write a Socratic-style blog post on a topic that was *formerly shaky and is now solid*. The protocol: BodhiKit surfaces 2–3 candidate topics meeting the formerly-shaky-now-solid signal (Bloom < 3 → ≥ 4, at least one demote-and-recover, currently Bloom ≥ 4 AND Box ≥ 3). You pick one and draft in your own voice — BodhiKit asks Socratic questions to sharpen your claims but does not write paragraphs. **After** drafting, the resource-finder agent surfaces 3–5 acknowledged masters on the topic; you read them with your draft in hand. You revise. You decide whether to publish — BodhiKit never pronounces a post ready, that verdict is yours. Posts persist at `learningWithBodhi/<project>/teach-backs/<YYYY-MM-DD>-<slug>.md`.

**When to use.** When `/evaluate` has moved your project to `completedProjects` and you want to demonstrate mastery the way the masters did — by writing something defensible on a topic that was once hard. See [Finishing a Project: the Capstone](#finishing-a-project-the-capstone) for the full arc.

**When NOT to use.** Mid-journey — the trigger is project completion, not "I feel like writing." Easy topics you never struggled on — the protocol picks formerly-shaky topics for a reason (Bjork's desirable difficulty, and the post is more useful to the next learner). You want validation that your understanding is "good enough" — the protocol declines to give you that; the masters give it to you, or they do not.

**Pairs well with.**
- `/evaluate` — the only invoker of the opt-in offer.
- `/resources` — under the hood for surfacing the masters' works after drafting.

**Example.**
```
/bodhikit:teach-back
```
> "Three topics from your history that meet the formerly-shaky-now-solid signal: (1) lifetimes — went from blank-wall in Week 1 to Bloom 4 by Week 9, with a demote-and-recover in Week 5; (2) trait bounds — three rounds of demote-and-recover, now stable at Box 4; (3) tokio spawn semantics — the bug you debugged in Week 6 reset this from 3 to 1, and it climbed back to 4 by Week 9. Which one do you want to write?"

**Pedagogy:** [Feynman](#4-feynman-technique) (writing as gap-revealer), [Desirable Difficulties](#6-desirable-difficulties-bjork) (formerly-shaky topics on purpose).

---

## Learner Profile

BodhiKit maintains a cross-project learner profile at the `learningWithBodhi/` root. In 1.7.0 it is split across two files so routine skills load only what they need:

- **`learningWithBodhi/.bodhi-profile.json`** — small, frequently read. Your career goals, learning motivations, overall Bloom's levels, cumulative stats (total sessions, exercises, concepts mastered, milestones), patterns (persistent challenges, consistent strengths), learning style preferences.
- **`learningWithBodhi/.bodhi-profile.projects.json`** — read only by cross-project skills like `/mentor` and `/evaluate`. Holds `activeProjects` and `completedProjects` arrays with per-project metadata (topic, started date, current phase, Bloom's level, pace, status, track purpose). Grows linearly with your project count, so isolating it from the smaller top-level file keeps daily skill reads lean.

Both files are created when you start your first learning project and updated as you progress. The split allows BodhiKit to personalize guidance across different projects and power the `/mentor` skill while keeping per-session context small.

---

## How Agents Work Behind the Scenes

BodhiKit uses four specialized AI agents that handle complex tasks. You never invoke agents directly. Skills launch them automatically when needed.

The shared design idea: agents run in their own context window. Heavy reads (archive history, web fetches, large code bases) happen in the agent's context, not in your main conversation. The agent returns a structured result; the parent skill uses it to drive the conversation with you in BodhiKit's own voice. Your dialogue stays focused; the analytical load happens out of sight.

### Skill Assessor Agent

**Used by:** `/learn`, `/assess`, `/evaluate`, `/plan` (regenerate mode)

When BodhiKit needs to understand your skill level, it launches the skill-assessor agent. This agent runs in a separate context so it does not clutter your main conversation. It asks 8-12 adaptive questions, starting at Bloom's Level 3 and adjusting up or down based on your answers. It classifies your level per sub-topic with a confidence rating (HIGH/MEDIUM/LOW) and returns a structured assessment.

Example: When you run `/bodhikit:learn react`, the skill-assessor takes over for Phase 2. It asks you about JSX, components, state, hooks. If you answer the components question easily, it escalates to a harder one. If you struggle with hooks, it de-escalates. After 8-10 questions, it returns: "JSX: Level 2, Components: Level 3, Props: Level 1, State: Level 0, Hooks: Level 0" with confidence ratings. This shapes your entire learning plan.

### Code Reviewer Agent

**Used by:** `/review`, `/practice` (review loop), `/teach` (after exercises)

When BodhiKit reviews your code, it launches the code-reviewer agent. This is NOT a production code review. The agent analyzes what your code reveals about your understanding: what concepts you demonstrate mastery of, what misconceptions are visible, what patterns you are ready to learn next, and where your Zone of Proximal Development sits.

Example: You complete a React exercise and the code works. The code-reviewer notices you used a `for` loop where `map` would be idiomatic, and that you mutated state directly instead of using spread syntax. Instead of saying "use map and spread," it returns Socratic questions: "What do you know about array methods like map?" and graduated hints if needed.

### Resource Finder Agent

**Used by:** `/resources` (find mode)

When you need learning materials, the resource-finder agent searches the web for verified, community-recommended free resources. It prioritizes official documentation, interactive platforms (Exercism, freeCodeCamp), and structured courses over random blog posts. It verifies each link is live and returns resources with title, type, difficulty level, and estimated time.

Example: You run `/bodhikit:resources find rust`. The agent searches for Rust learning materials, verifies links, and returns: The Rust Book (official docs), Rustlings (interactive exercises), Exercism Rust Track (practice problems), and a few curated tutorials, ranked by interactivity and community reputation.

### Trajectory Analyzer Agent

**Used by:** `/evaluate` (Phase 1 Journey Review and Phase 3 Comparative Analysis)

When `/evaluate` runs against a project with real depth — archived sessions, prior assessments, accumulated precision-gap notes — it launches the trajectory-analyzer agent. The agent reads every archive file, every plan phase, the full assessment history, and the spaced-review trail in its own context window. It returns a structured report: per-topic Bloom movement over time (initial / intermediate / current, with an evidence quote drawn verbatim from a real session), retention distribution by Leitner box, exercises and quizzes timeline, precision-gap movements (closed, preserved, newly opened), and project completion.

This means `/evaluate` can do honest trajectory analysis across a learner's entire history without your dialogue with BodhiKit getting crowded by the load. For a learner six months in with dozens of archived sessions, the win is real — the heavy reading happens out of sight, and the evaluation conversation stays focused on what the trajectory means for what to do next.

Example: You finish your React project after four months and run `/bodhikit:evaluate`. The agent reads your 30+ archived sessions, three earlier assessments, and the full spaced-review history. It returns: "JSX went 0 → 3 → 4 over March-June, evidence: 'self-corrected on the comparison';" "Hooks plateaued at 3 since April — three quiz misses on dependency arrays;" "Closed precision gap: PG memory 14-18 → 10-14 MB on April 12;" "Project completion 78%, eight of ten modules marked complete." BodhiKit uses that report to drive the milestone conversation with you in its own voice.

---

## Using BodhiKit with Books and Courses

BodhiKit works as a teaching assistant alongside your existing learning materials:

### Adding a book or course

```
/bodhikit:resources add "Eloquent JavaScript"
/bodhikit:resources add https://www.udemy.com/course/your-course
```

BodhiKit will:
- Analyze the material's structure (chapters, syllabus)
- Map it to your learning plan modules
- Ask how you want to use it: as primary material, supplement, or reference

### Using BodhiKit as a TA

If you are following a book or course, BodhiKit can:
- Explain concepts from the book in different ways (when the book's explanation does not click)
- Quiz you on what you read/watched
- Give you extra practice exercises on the same topics
- Review your code from the book's exercises
- Fill gaps the material does not cover

---

## Understanding Your Progress

### Bloom's Taxonomy Levels

BodhiKit tracks your skill level per concept using Bloom's Taxonomy:

| Level | Name | What It Means |
|-------|------|--------------|
| 1 | Remember | You have heard of this but cannot use it yet |
| 2 | Understand | You understand the idea but need practice applying it |
| 3 | Apply | You can use this with some guidance |
| 4 | Analyze | You can work with this independently and debug issues |
| 5 | Evaluate | You can evaluate approaches and make design decisions |
| 6 | Create | You can design novel solutions and teach others |

### Mastery Criteria

A concept is considered **mastered** when:
- Bloom's Level 4 or higher
- 3 consecutive correct quiz answers at Bloom's Level 4+ questions
- Spaced repetition Box 4 or 5
- Can explain it to someone else (Feynman check)

---

## The Pedagogy Behind BodhiKit

BodhiKit is built on sixteen research-backed methodologies. None of them are decorative — each one solves a specific learning problem that comes up during a real journey, and each one fires inside specific skills at specific moments. This section maps the twelve core ones in full cards: what each methodology is, what problem it solves, when BodhiKit reaches for it, and where to read the primary source. The four added in 1.11.0 — cognitive load / faded worked examples (Sweller), pretesting (Kornell, Hays & Bjork), successive relearning (Rawson & Dunlosky), and confidence calibration (Koriat) — are cited in the README's Science section; in short: `/teach` opens with an ungraded guess-first question and fades scaffolding from worked example to full problem, `/quiz` collects a sure/mostly/guessing tag before every reveal and re-asks missed concepts until one successful retrieval, and `/progress` shows you what your confidence is worth.

If you only have time for one paragraph: **BodhiKit's job is to make the next move in your learning the one most likely to grow durable, transferable understanding — not the one most likely to feel productive in the moment.** The methodologies below are the operationalization of that.

---

### 1. Bloom's Taxonomy

**What it is.** A six-level hierarchy of cognitive engagement with a concept — Remember → Understand → Apply → Analyze → Evaluate → Create. Each level is qualitatively different from the one below, not just "more of the same."

**Why BodhiKit uses it.** "Did you learn it?" is the wrong question. *At what level* did you learn it is the right one. Bloom gives BodhiKit a concrete vocabulary for the gap between "I have heard of monads" (Level 1) and "I can design a monad for a new domain" (Level 6). Without this, calibration is impossible — exercises are either too easy or too hard, hints either condescend or overshoot.

**When it fires.**
- `/learn` Phase 2: the skill-assessor agent classifies your level per sub-topic before generating a plan.
- `/teach` Phase 4: exercise scaffolding is calibrated to Bloom level (1-2 get starter files; 3-4 get tests; 5-6 get problem statements only).
- `/quiz`: questions mix levels deliberately — Level 2 recall, Level 3 prediction, Level 4 "what breaks if…"
- `/assess`, `/evaluate`, `/progress`: per-topic Bloom levels are the unit of "where you are."

**Go deeper.**
- Benjamin Bloom, *[Taxonomy of Educational Objectives](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy)* (1956) — the original.
- Lorin Anderson & David Krathwohl, *[A Taxonomy for Learning, Teaching, and Assessing](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy#The_cognitive_domain_(knowledge-based))* (2001) — the revised taxonomy BodhiKit uses.

---

### 2. Spaced Repetition (Ebbinghaus + Leitner)

**What it is.** Reviewing material at expanding intervals defeats the forgetting curve. Leitner's box system operationalizes this: a concept you got right moves up a box (longer interval); a concept you got wrong drops to Box 1 (review tomorrow).

**Why BodhiKit uses it.** Without scheduled review, learning leaks. You finish a module on hooks, feel solid, and a month later cannot remember the rules of dependency arrays. Spaced repetition is the only known way to make recall *durable* without spending more time per concept overall.

**When it fires.**
- `/continue` Phase 4: surfaces concepts where `nextReview ≤ today`.
- `/quiz`: every answer updates the box per the canonical mapping (Box 1 → 1 day, Box 2 → 3, Box 3 → 7, Box 4 → 14, Box 5 → 30).
- `/forget`: learner-initiated demotion to Box 1 — honest self-assessment.
- `/teach` Phase 5 (and its understanding-only path): new and refined concepts enter the system.

**Go deeper.**
- Hermann Ebbinghaus, *[Memory: A Contribution to Experimental Psychology](https://en.wikipedia.org/wiki/Memory:_A_Contribution_to_Experimental_Psychology)* (1885) — the original forgetting-curve experiments.
- Sebastian Leitner, *[Leitner system](https://en.wikipedia.org/wiki/Leitner_system)* (1972) — the box implementation.

---

### 3. Zone of Proximal Development (Vygotsky)

**What it is.** Three zones around your current ability: *can do alone* (too easy, no learning), *can do with guidance* (the ZPD — where learning happens), *cannot do even with help* (overload). The right task is always in the middle zone.

**Why BodhiKit uses it.** Most learning failures are calibration failures. A task that is too easy bores you out of engagement; a task that is too hard cognitively overloads you and you give up. Without a ZPD model, BodhiKit would either patronize advanced learners or break beginners.

**When it fires.**
- `/teach` Phase 3: scaffolds problems with the **Gradual Release of Responsibility** model (I Do → We Do → You Do).
- `/teach` Phase 2 Checkpoint and Phase 4 hint chain: detects "Beyond the ZPD" signals (cannot articulate confusion, Approach hint did not unstick) and triggers the analogy protocol or a step back to a prerequisite.
- `/pair`: mode auto-selects from Bloom level (1-2 → strong-style, 3-4 → ping-pong, 5-6 → navigate) — each mode is calibrated to a different ZPD position.

**Go deeper.**
- Lev Vygotsky, *[Mind in Society](https://en.wikipedia.org/wiki/Zone_of_proximal_development)* (1978) — the foundational text.

---

### 4. Feynman Technique

**What it is.** Four steps: choose a concept, explain it simply (as if to a 12-year-old), identify the gaps your explanation revealed, refine and repeat. The check is the *simple* part — jargon hides confusion from yourself.

**Why BodhiKit uses it.** Recognition feels like understanding but is not. You can "follow along" with a lecture on monads and still not be able to write one. Forcing you to *generate* the explanation in your own words breaks the illusion of competence and surfaces the actual gap.

**When it fires.**
- `/teach`'s understanding-only path — a direct application of all four steps.
- `/teach` Phase 5: explain-back check.
- `/teach-back`: a Feynman application scaled to a blog post; reading the masters happens *after* drafting so your gaps surface before they get hidden.
- The [Analogy-Escalation Protocol](#when-bodhikit-reaches-for-an-analogy): operationalizes Feynman step 4 ("create better analogies") with a structured ladder.

**Go deeper.**
- James Gleick, *[Genius: The Life and Science of Richard Feynman](https://en.wikipedia.org/wiki/Genius:_The_Life_and_Science_of_Richard_Feynman)* (1992) — the most cited source for Feynman's teaching philosophy.

---

### 5. Deliberate Practice (Ericsson)

**What it is.** Targeted exercises at the edge of your ability, with immediate feedback. Not just "more practice" — *correct* practice, focused on the specific sub-skill you are growing, with a clear success signal and a correction loop when you miss.

**Why BodhiKit uses it.** Hours-of-practice does not produce expertise. Hours-of-correct-practice does. Without deliberate practice, learners drill on what they are already good at (which feels productive) and avoid the uncomfortable edge where actual growth happens.

**When it fires.**
- `/practice`: every exercise is calibrated to your current Bloom level on the topic, with the success criterion stated explicitly upfront.
- `/teach` Phase 4: You-Do exercises follow the same calibration.
- `/pair` ping-pong mode: rapid red-green-refactor cycles with immediate feedback.
- `/review`: the post-exercise feedback loop closes the deliberate-practice cycle.

**Go deeper.**
- K. Anders Ericsson, *[The Role of Deliberate Practice in the Acquisition of Expert Performance](https://psycnet.apa.org/record/1993-40718-001)* (1993) — the foundational paper.
- K. Anders Ericsson, *[Peak: Secrets from the New Science of Expertise](https://en.wikipedia.org/wiki/Peak:_Secrets_from_the_New_Science_of_Expertise)* (2016) — the readable book version.

---

### 6. Desirable Difficulties (Bjork)

**What it is.** Some kinds of difficulty during learning produce *better* long-term retention even though they make practice feel slower or harder in the moment. Examples: interleaving topics rather than blocking, spacing rather than cramming, retrieval practice rather than re-reading, generation rather than recognition.

**Why BodhiKit uses it.** What feels effective during learning is often the worst for retention, and what feels uncomfortable is often the most durable. Without this principle, BodhiKit would optimize for in-session smoothness and produce learners who forget everything in a month.

**When it fires.**
- `/teach`: interleaves prior concepts with new ones in examples (rather than mono-topic blocks).
- `/quiz` and spaced review: retrieval practice (you generate the answer) and spacing (review at expanding intervals).
- `/practice`: variation in context — learned with arrays, practice with objects.
- `/teach-back`: picks *formerly-shaky* topics (not easy wins) precisely because the difficulty is desirable for both writer and reader.

**Go deeper.**
- Robert & Elizabeth Bjork, *[Making Things Hard on Yourself, But in a Good Way](https://bjorklab.psych.ucla.edu/research/)* (2011) — the named-and-explained version.

---

### 7. Growth Mindset (Dweck)

**What it is.** Whether learners believe ability is fixed or developable changes how they respond to difficulty. Fixed-mindset learners avoid challenge (failure threatens identity); growth-mindset learners seek it (challenge is the path to growth).

**Why BodhiKit uses it.** Feedback language has measurable effects on whether learners persist through stalls. Praise strategy ("you stuck with that problem until you cracked it") not talent ("you are smart"). Frame mistakes as data, not verdict.

**When it fires.**
- The `teaching-personality` KB encodes the voice across every skill — celebrate effort and strategy, not talent; reframe "I can't" as "I can't yet."
- `/reflect`: questions explicitly probe what was hardest and what the learner would do differently — building growth-orientation through metacognition.
- `/debug-together` Phase 0: bugs framed as clues, not failures.
- `/forget`: honest self-demotion framed as awareness, not setback.

**Go deeper.**
- Carol Dweck, *[Mindset: The New Psychology of Success](https://en.wikipedia.org/wiki/Mindset_(book))* (2006) — the readable summary.

---

### 8. Metacognition (Flavell)

**What it is.** Thinking about your thinking. Knowing what you know, what you do not know, and what tactics work for *you* specifically.

**Why BodhiKit uses it.** The Dunning-Kruger curve and "illusions of competence" mean learners routinely overestimate their own understanding. Without explicit metacognitive practice, you do not know that you do not know. Reflection is also where retention is durably encoded — research shows learners who reflect retain 20-30% more.

**When it fires.**
- `/reflect`: the entire skill is direct metacognitive practice — four questions probing what was hardest, what surprised you, your confidence ratings, and what you would do differently.
- `/forget`: explicit self-assessment of confidence, with consequences (Box demotion) — keeps metacognition honest.
- `/evaluate`: comparative analysis ("you said you were Bloom 3 on hooks in March; the trajectory shows you are now Bloom 4 — but the recent quiz misses suggest a precision gap") confronts illusion of competence with evidence.

**Go deeper.**
- John Flavell, *[Metacognition and Cognitive Monitoring](https://psycnet.apa.org/record/1980-09388-001)* (1979) — the paper that coined the term.

---

### 9. Constructivism & Spiral Curriculum (Piaget, Bruner, Papert)

**What it is.** Learning is *built* in the learner's head, not transmitted. The same concept benefits from being revisited at increasing depth — the spiral curriculum — rather than treated as "done" after one pass.

**Why BodhiKit uses it.** A learner who *uses* a concept builds a model; a learner who *reads about* it does not. And concepts seen once are surface-level; concepts revisited in different contexts get integrated into a working mental model. Without these principles, BodhiKit would lecture you instead of giving you problems to chew on.

**When it fires.**
- "The learner writes the code from Phase 3 onward" — the core teaching principle in `/teach` and `/pair`.
- Plans are organized by phase (Phase 0 → Phase 1 → Phase 2) with topics revisited at higher Bloom levels in later phases — Bruner's spiral.
- `/practice` exercises calibrate to *building*, not reading.

**Go deeper.**
- Jean Piaget, *[The Construction of Reality in the Child](https://en.wikipedia.org/wiki/Constructivism_(philosophy_of_education))* (1954).
- Jerome Bruner, *[The Process of Education](https://en.wikipedia.org/wiki/The_Process_of_Education)* (1960) — the spiral curriculum.
- Seymour Papert, *[Mindstorms](https://en.wikipedia.org/wiki/Mindstorms_(book))* (1980) — constructionism applied to programming.

---

### 10. Mentoring Theory (Kram + Whitmore GROW)

**What it is.** Effective mentoring has two functions: **career** (advice, exposure, sponsorship — what to do) and **psychosocial** (acceptance, confirmation, role-modeling — who to be). Whitmore's **GROW** model gives a four-step structure: Goal, Reality, Options, Will.

**Why BodhiKit uses it.** A learner asking "what should I learn next?" is rarely just asking about topics — they are asking about path, identity, fit. GROW gives the conversation structure without prescribing the answer. Kram's distinction reminds BodhiKit which functions it *can* serve (career advice grounded in your skill data) and which it *cannot* (sponsorship, networking, vouching).

**When it fires.**
- `/mentor`: the entire skill is a direct application of GROW + Kram.
- `/evaluate` offers `/mentor` at major milestones (opt-in).

**Go deeper.**
- Kathy Kram, *[Mentoring at Work](https://www.researchgate.net/publication/232463073_Mentoring_at_Work_Developmental_Relationships_in_Organisational_Life)* (1985) — the foundational study.
- John Whitmore, *[Coaching for Performance (GROW Model)](https://en.wikipedia.org/wiki/GROW_model)* (1988) — the four-step structure.

---

### 11. Pair Programming (Beck, Williams & Kessler, Falco)

**What it is.** Two people, one keyboard. One drives (types), one navigates (thinks strategically). Research shows pair programming improves learning outcomes, satisfaction, and retention compared to solo coding for novices.

**Why BodhiKit uses it.** Some skills transfer through talk, not text — design intuition, debugging instinct, code-reading habits. Pairing makes those tacit skills *visible*. Strong-style specifically (Falco) is designed for coaching novices: the experienced person navigates so the novice must engage physically with the keyboard.

**When it fires.**
- `/pair`: three modes calibrated to ZPD position (strong-style for novices, ping-pong for intermediate, navigate for advanced).
- `/teach` Phase 3 (We Do): auto-invokes `/pair` when collaborative coding fits better than guided discussion.

**Go deeper.**
- Kent Beck, *[Extreme Programming Explained](https://en.wikipedia.org/wiki/Extreme_programming)* (1999).
- Laurie Williams & Robert Kessler, *[Pair Programming Illuminated](https://collaboration.csc.ncsu.edu/laurie/Papers/ESE%20-%20Single%20Column.pdf)* (2002) — the research synthesis.
- Llewellyn Falco, *[Strong-Style Pairing](http://llewellynfalco.blogspot.com/2014/06/llewellyns-strong-style-pairing.html)* (2014) — the coaching variant.

---

### 12. Scientific Debugging (Zeller + Gauss + O'Dell)

**What it is.** Debugging as scientific method: reproduce the failure, form a falsifiable hypothesis, insert a probe (not a fix), evaluate, isolate via binary search, correct. Then *reflect* on what made the bug findable. Zeller's TRAFFIC method (Track, Reproduce, Automate, Find origins, Focus, Isolate, Correct) and Gauss's Wolf Fence algorithm operationalize the loop.

**Why BodhiKit uses it.** Developers spend 35-50% of their time debugging (O'Dell, 2017), yet debugging is rarely *taught* explicitly. Novices tinker randomly; experts hypothesize. The difference is a teachable skill — and like all skills, it grows through deliberate practice, not exposure.

**When it fires.**
- `/debug-together`: six phases directly map to TRAFFIC + wolf fence + reflection.
- `/practice` and `/teach`: auto-invoke `/debug-together` when learner code has a real bug.

**Go deeper.**
- Andreas Zeller, *[Why Programs Fail](https://en.wikipedia.org/wiki/Why_Programs_Fail)* (2005) — the TRAFFIC method.
- Edward J. Gauss, *[Wolf Fence Algorithm](https://dl.acm.org/doi/abs/10.1145/358690.358695)* (1982) — binary search for bugs.
- Devon H. O'Dell, *[The Debugging Mindset](https://queue.acm.org/detail.cfm?id=3068754/)* (2017, ACM Queue) — growth mindset applied to bugs.

---

### How they compose

| Phase of the journey | Pedagogies that fire |
|---|---|
| Day 1 — `/learn` onboarding | Bloom (assessment), Constructivism (start by building, not reading) |
| Daily — `/continue` rhythm | Spaced Repetition (due reviews), ZPD (next-concept calibration) |
| Teaching a concept — `/teach` | ZPD (Gradual Release), Feynman (explain-back), Bloom (exercise calibration), Desirable Difficulties (interleaving) |
| A concept stalls — `/teach` understanding-only, analogy protocol | Feynman (4-step refinement), ZPD (Beyond signals → protocol fires) |
| Honest self-assessment — `/reflect`, `/forget` | Metacognition, Growth Mindset, Spaced Repetition (box updates) |
| Hands-on building — `/practice`, `/pair` | Deliberate Practice, Pair Programming, Constructivism |
| A real bug — `/debug-together` | Scientific Debugging, Growth Mindset (bugs as clues) |
| Mid-journey checkpoint — `/evaluate` | Bloom (trajectory), Metacognition (confronting illusion of competence) |
| Path question — `/mentor` | GROW, Kram's mentoring functions |
| Capstone — `/teach-back` | Feynman (writing as gap-revealer), Desirable Difficulties (formerly-shaky topics) |

If you notice a pattern: most skills compose 2-3 methodologies. None of them works alone. The reason `/teach` is calibrated to Bloom *and* follows ZPD *and* uses Feynman *and* leans on Desirable Difficulties is that real learning happens at the intersection, not in any single dimension.

---

## How Spaced Repetition Works

BodhiKit uses a virtual Leitner box system to schedule concept reviews:

| Box | Review After | Meaning |
|-----|-------------|---------|
| 1 | 1 day | New or forgotten |
| 2 | 3 days | Recalled once |
| 3 | 7 days | Building retention |
| 4 | 14 days | Strong retention |
| 5 | 30 days | Long-term mastery |

- Get a concept right: it moves up one box (reviewed less often)
- Get it wrong: it drops back to Box 1 (reviewed tomorrow)
- When you run `/continue`, BodhiKit checks what is due for review

This is automatic. You do not need to manage it.

---

## Housekeeping Your Tracking Files

Your tracking files accumulate honest evidence of your learning over time — sessions, assessments, Bloom-level shifts, precision gaps closed and opened. Nothing of yours is ever deleted. But routine skills should not have to load everything you have ever done to answer "where do I pick up tomorrow?"

BodhiKit handles this with `/bodhikit:housekeep` — a single skill that tends the garden. Other skills append to live documents; `/housekeep` moves the previous live entry into the archive and writes a one-line summary pointer back to it. The live document stays small. The archive grows but is loaded only when a situation justifies it.

### What gets housekept

- **`progress.md`** — at session boundaries, the previous session entry moves to `progress/archive/session-<YYYY-MM-DD>.md`. The new live `progress.md` carries only the most recent session in full, plus a growing "Summary of earlier sessions" block (2-5 lines per archived session, up to 20 for milestone sessions).
- **`assessments/latest.md`** — when a new assessment lands, the previous one rotates to `assessments/archive/`. Same summary-block pattern.
- **Summary collapse** — when the summary block grows past 200 lines, the oldest entries roll into a single phase summary ("Phase 0 (12 sessions, 2026-03-23 → 2026-04-30): outcomes summary. Archives: archive/2026-03-*.md"). The individual archive files are never modified.

### When `/housekeep` runs

- Manually, whenever you want. Safe to run twice — idempotent.
- At the end of `/reflect` (it may invoke `/housekeep` automatically).
- At the start of `/continue`, if un-housekept state is detected.
- Via `/bodhikit:housekeep --dry-run` if you want to see what would change without writing.

### Safety guarantees

- Archive content is permanent. `/housekeep` never deletes archive files and never edits an existing archive file.
- The previous live entry is moved, not copied — but the entire chain is preserved through the pointer in the summary block.
- Transparent: every rotation prints what moved where, and the before/after byte sizes of the live documents.

You will rarely think about housekeeping. The point is that you can be aggressive about logging detail in real time (`progress.md` can hold a 20-line session entry, an assessment can be 200 lines) without worrying about context cost, because the next `/housekeep` will tuck it cleanly away while keeping the pointer visible.

---

## Finishing a Project: the Capstone

When `/evaluate` confirms you have finished a project — Bloom's levels climbed across the topics that mattered, mastery criteria met, spaced-review retention strong — it moves the project from `activeProjects` to `completedProjects` and offers you one optional, opt-in step: a teach-back.

A teach-back is a Socratic-style blog post you write on a topic that was *formerly shaky and is now solid*. Not your easiest win — your hardest-won one. The point is that the next learner benefits more from "I kept getting this wrong until I realized X" than from a clean summary of what X is.

### How it works

1. **Candidate surfacing.** BodhiKit reads your full project history (with the trajectory-analyzer agent) and proposes 2-3 topics that meet the formerly-shaky-now-solid signal: multiple assessments climbing from Bloom < 3 to ≥ 4, at least one demote-and-recover in spaced review, currently sitting at Bloom ≥ 4 AND Box ≥ 3. You pick one (or decline the capstone — it is always optional).

2. **Draft.** You write the post in your own voice. BodhiKit asks Socratic questions to sharpen your claims, but does not write paragraphs for you.

3. **Read the masters after, not before.** Once you have a draft, BodhiKit uses the resource-finder agent to surface 3-5 acknowledged masters on the topic — books, talks, papers, essays. You read them with your draft already in hand. This is the second half of the Feynman technique applied to writing: you find out what you missed only after you have committed to what you know.

4. **Revise.** Your claims get checked against the masters. What survives is real. What does not, you revise or strike. BodhiKit prompts you on every claim it sees that the masters would push back on, but never overwrites your prose.

5. **Decide.** You decide whether the post is defensible enough to publish, keep as personal notes, or set aside. BodhiKit will not pronounce it ready — the publish question is framed as credibility-protection, not credibility-building. Publish only when you can defend every claim against a master who knows more than you.

### Why this exists

The system already had a clear ending — `/evaluate` confirms completion. But "completed" measured mastery; it did not demonstrate it. The capstone gives you a way to show mastery the way the masters themselves did: by writing something defensible on a topic that was once hard.

Posts persist at `learningWithBodhi/<project>/teach-backs/<YYYY-MM-DD>-<slug>.md`. They are not housekept; they are yours, sibling to `.bodhi/` so you can keep editing them in your normal workflow long after the skill closes.

---

## Example Project

Want to see what a learning project looks like after a few sessions? Check out `docs/example-project/` in the BodhiKit repository.

It contains realistic `.bodhi/` tracking files for a "React Fundamentals" learner who has completed 5 sessions, laid out in the v2 layout:

**Live surfaces (loaded by routine skills):**
- `state.json` — slim: 5 sessions, 3-day streak, working on Module 2.1 (State and Hooks), per-area Bloom's levels.
- `progress.md` — latest session at the top (2026-03-14 quiz + useState practice), followed by a "Summary of earlier sessions" block with one-line pointers to four archived sessions.
- `plan/README.md` — arc overview, current phase pointer.
- `plan/phase-1.md` / `plan/phase-2.md` / `plan/phase-3.md` — per-phase detailed plans. Routine skills load only the current phase file.
- `assessments/latest.md` — most recent assessment (Module 2.1 quiz), followed by a summary pointing back at the initial assessment.
- `spaced-review.json` — 8 concepts across Leitner boxes 1-4.
- `assessment-history.json` — structured Bloom's-over-time data for `/evaluate`.
- `resources.md` — curated resources.

**Archived surfaces (loaded only when justified):**
- `progress/archive/session-*.md` — full text of each archived session.
- `assessments/archive/*.md` — full text of each archived assessment.

This gives you a clear picture of what to expect before you start your own learning project. The split between live and archived surfaces is the core of v2's progressive disclosure: skills load the live documents by default and reach into the archive only when the situation justifies it.

---

## Tips for Effective Learning

1. **Consistency beats intensity.** 30 minutes daily is better than 5 hours once a week.
2. **Struggle is learning.** If it feels hard, you are growing. If it feels easy, you are reviewing.
3. **Explain what you learn.** The Feynman technique is your best tool. If you cannot explain it simply, you do not understand it yet.
4. **Do not skip reviews.** Spaced repetition only works if you do the reviews when they are due.
5. **Write the code yourself.** Do not copy from BodhiKit or from examples. Type it. Change it. Break it. Fix it.
6. **Take breaks.** Your brain does important work during rest. After focused learning, walk away for a few minutes.
7. **Trust the process.** Some days will feel unproductive. Growth is often invisible. Keep showing up.

---

## Philosophy

BodhiKit is built on a simple belief: everyone can learn to code, and the best way to learn is by doing, with a wise guide by your side.

The plugin does not write code for you. It asks questions, gives hints, creates exercises, and reviews your work. The goal is not to be needed forever. The goal is to help you reach the point where you do not need it anymore.

"The obstacle is the path."
