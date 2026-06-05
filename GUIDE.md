# BodhiKit User Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Upgrading to 1.7.0](#upgrading-to-170)
- [Starting a New Learning Project](#starting-a-new-learning-project)
- [Resuming Your Learning](#resuming-your-learning)
- [Daily Learning Workflow](#daily-learning-workflow)
- [How Teaching Works](#how-teaching-works)
- [End-of-Session Reflection](#end-of-session-reflection)
- [Skills Reference](#skills-reference)
- [How Agents Work Behind the Scenes](#how-agents-work-behind-the-scenes)
- [Using BodhiKit with Books and Courses](#using-bodhikit-with-books-and-courses)
- [Learner Profile](#learner-profile)
- [Understanding Your Progress](#understanding-your-progress)
- [How Spaced Repetition Works](#how-spaced-repetition-works)
- [Housekeeping Your Tracking Files](#housekeeping-your-tracking-files)
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

**Context tip:** BodhiKit loads 18 knowledge bases. To keep other projects lean, enable it only where you need it. Add to your `learningWithBodhi/.claude/settings.json`:

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

## Upgrading to 1.7.0

If you already have learning projects from 1.6.x or earlier, run the one-shot migration once per project:

```
/bodhikit:housekeep migrate
```

You can run it from inside a specific project folder, or from the `learningWithBodhi/` root to convert every project at once.

### What it does

1.7.0 introduces a progressive-disclosure layout so routine skills load substantially less context per session. The migration converts:

- `state.json` — strips long narrative fields (`lastSessionSummary`, `bloomResetNote`); they move to `progress.md` where prose belongs. State stays slim: pointers, counts, current values.
- `plan.md` (monolithic) → `plan/README.md` + `plan/phase-{N}.md` (sectional). Skills like `/teach` and `/continue` load only the current phase, not the whole plan.
- `progress.md` (flat chronological log) → live + archive + summary. The latest session sits at the top; older sessions move to `progress/archive/` with one-line pointers in a summary block.
- `assessment.md` (flat) → `assessments/latest.md` + `assessments/archive/`. Same pattern.
- `.bodhi-profile.json` (monolithic) → `.bodhi-profile.json` (top-level: cumulative stats, patterns) + `.bodhi-profile.projects.json` (per-project metadata).

### Safety

- **Idempotent.** Running `/housekeep migrate` twice in a row is a no-op the second time.
- **Non-destructive.** The originals are preserved at `.bodhi/.pre-1.7.0-backup/` for one minor version (removed in 1.8.0). If anything looks off, you can restore from there.
- **Transparent.** The command prints a before/after byte report for every file and lists every archive entry it created.

### After migrating

Your skills work exactly as before — just faster, because routine sessions read less context. Sessions you don't need (history, full plan arc, prior assessments) stay on disk, accessible by pointer when a situation justifies it (e.g., `/evaluate` reading the full history for trajectory analysis, `/continue` reading recent archive entries when you've been gone for over 30 days).

The new `/housekeep` skill also handles ongoing rotation — at session boundaries, it moves the previous live session into `progress/archive/` and writes a one-line summary pointer. See [Housekeeping Your Tracking Files](#housekeeping-your-tracking-files) for details.

---

## Starting a New Learning Project

Use `/bodhikit:learn <topic>` to start learning anything:

```
/bodhikit:learn react
/bodhikit:learn rust
/bodhikit:learn system design
/bodhikit:learn web development
/bodhikit:learn zig
```

### What happens when you start:

1. **Topic Discovery** — BodhiKit asks clarifying questions about what you want to learn, why, and your timeline
2. **Skill Assessment** — A series of adaptive questions to understand where you stand (not a test, an exploration)
3. **Plan Generation** — A personalized learning plan with phases, modules, exercises, and spaced review checkpoints
4. **Project Setup** — Creates a `learningWithBodhi/<project-name>/` folder with tracking files
5. **First Exercise** — You get something to DO immediately, not just something to read

### Multiple learning projects

You can have as many learning projects as you want. Each lives in its own folder under `learningWithBodhi/`. One session should focus on one project at a time.

---

## Resuming Your Learning

Use `/bodhikit:continue` to pick up where you left off:

```
/bodhikit:continue                  # Auto-detect or choose from active projects
/bodhikit:continue react-fundamentals  # Resume a specific project
```

BodhiKit will:
- Show a quick status check (project, module, streak, concepts due)
- Find your active projects and show where you left off
- Check if any concepts are due for spaced review
- Offer options: continue current module, practice, or something else
- Auto-invoke `/teach` when you continue with the next module
- Auto-invoke `/reflect` when you say goodbye

This works across sessions. Your progress is saved in `.bodhi/` files.

---

## Daily Learning Workflow

A typical learning session with `/bodhikit:continue`:

1. **Status**: Quick 3-line check-in (auto)
2. **Review**: Spaced review of due concepts (auto, if any are due)
3. **Teach**: Guided teaching of the next concept (auto, when you choose to continue)
4. **Practice**: Hands-on exercise on the concept you just learned (auto, within /teach)
5. **Quiz**: Quick retention check (auto, within /teach)
6. **Reflect**: End-of-session reflection (auto, when you say goodbye)

You can also invoke any skill directly at any time. The auto-invocation just means `/continue` handles the full flow for you.

You do not need to follow this exact order. Use whatever skills feel right for your session.

---

## How Teaching Works

When you choose to continue with the next module (or run `/bodhikit:teach` directly), BodhiKit follows the **Gradual Release of Responsibility** model:

1. **I Do (Modeling)** — BodhiKit explains the concept with analogies, concrete code examples, and connects it to what you already know. It shows WHY the concept matters, not just what it does.

2. **We Do (Guided Practice)** — You and BodhiKit work through a problem together. It asks guiding questions: "How would you start? What data structure fits here?" You make the decisions, it keeps you on track.

3. **You Do (Independent Practice)** — BodhiKit gives you an exercise calibrated to your level. Beginners get starter files with TODO comments. Advanced learners get a problem statement only. You solve it yourself.

4. **Verify** — Quick retention check: 2-3 questions to confirm the concept stuck. Concepts are added to spaced repetition tracking.

The key rule: BodhiKit never lectures for more than 5 minutes without interaction. It is a conversation, not a presentation.

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

### `/bodhikit:learn [topic]`
Start a new learning project. Creates a personalized plan based on your assessment.

### `/bodhikit:continue [project-name]`
Resume from where you left off. Auto-invokes `/status`, `/teach`, and `/reflect` for a complete guided session. Works across sessions.

### `/bodhikit:teach [topic|next]`
Proactive guided teaching. Walks you through a concept step by step: explains it, demonstrates with code, works through a problem together, gives you an exercise, then verifies retention. Auto-invoked by `/continue`.

### `/bodhikit:assess <topic>`
Standalone skill assessment. Get your Bloom's taxonomy level for any topic without starting a full project.

### `/bodhikit:review [file-path|repo-url]`
Educational code review. Analyzes what your code reveals about your understanding. Works with local files, GitHub, GitLab, and Codeberg URLs.

### `/bodhikit:quiz [topic|current]`
Quick knowledge check. 5-7 adaptive questions. Updates spaced repetition tracking. Uses active recall.

### `/bodhikit:plan [view|adjust|regenerate]`
Manage your learning plan. View current state, adjust modules, or regenerate from scratch.

### `/bodhikit:progress [project-name|all]`
View your progress dashboard. Module completion, Bloom's levels, streaks, spaced review health.

### `/bodhikit:resources [find topic|add url|list]`
Find verified free resources, add your own materials (books, courses), or list what you have.

### `/bodhikit:explain <concept>`
Deep-dive using the Feynman technique. BodhiKit explains simply, then asks you to explain back. Identifies and fills gaps.

### `/bodhikit:practice [topic|next]`
Get a hands-on exercise calibrated to your level. Beginners get starter files, advanced learners get problem statements.

### `/bodhikit:evaluate [project-name]`
Comprehensive evaluation of your entire learning journey. Compares where you started to where you are now.

### `/bodhikit:reflect`
End-of-session metacognitive reflection. Asks what was hardest, what surprised you, and your confidence rating. Feeds data back into spaced repetition scheduling. Auto-invoked by `/continue` when you say goodbye.

### `/bodhikit:status`
Quick 3-line check-in: current project, module, streak, and concepts due today. Auto-invoked by `/continue` at session start.

### `/bodhikit:forget <concept>`
Demote a concept back to Box 1 for re-review tomorrow. Use it the moment you notice a concept has slipped — the algorithm will catch it eventually, but honest self-assessment beats waiting. Auto-invoked by `/reflect` when you self-rate confidence 1–4 on a specific concept.

### `/bodhikit:housekeep [migrate|--dry-run]`
Tends the garden of your `.bodhi/` tracking files. Two modes:

- **Default**: Rotates the previous live session entry into `progress/archive/` and writes a one-line summary pointer in the live `progress.md`. Same for assessments. Idempotent (safe to run twice). Non-destructive (archive content is permanent). Use it when `.bodhi/` feels heavy, at the end of a long session, or whenever you want.
- **`migrate`**: One-shot conversion of pre-1.7.0 tracking files into the new live + archive + summary layout. Run it once per existing project after upgrading. See [Upgrading to 1.7.0](#upgrading-to-170).
- **`--dry-run`**: Report mode — shows what would change without writing anything.

`/reflect` and `/continue` may invoke `/housekeep` for you at session boundaries. You can always run it explicitly.

### `/bodhikit:mentor [question]`
Career and learning path guidance. Uses the GROW model (Goal, Reality, Options, Will) and Kram's mentoring theory. Reads your learner profile and all learning projects to map your skill landscape against your career goals. Presents 2-3 concrete learning path options and lets you choose. Honest about what an AI cannot do (sponsorship, networking). Auto-invoked by `/evaluate` when you complete a major milestone.

Example: After finishing your React project, run `/bodhikit:mentor` and it will assess your full-stack readiness, suggest whether to learn Node.js, Rails, or go deeper in React, and offer to start the next project.

### `/bodhikit:pair [strong-style|ping-pong|navigate]`
Pair programming with BodhiKit as your partner. Three research-backed modes:
- **strong-style** (beginners): BodhiKit describes what to build, you type it. Forces explicit communication. Based on Falco's coaching method.
- **ping-pong** (intermediate): BodhiKit writes a failing test, you make it pass. Then you write the next test. Teaches TDD naturally.
- **navigate** (advanced): You describe the approach, BodhiKit follows your lead and asks strategic questions.

Mode auto-selects based on your Bloom's level, or you can choose. Auto-invoked by `/teach` during guided practice. After 15-20 minutes, roles reverse to exercise both tactical and strategic thinking.

### `/bodhikit:debug-together [file-path]`
Scientific debugging that teaches the process, not just the fix. Based on Zeller's TRAFFIC method: reproduce the bug, form a hypothesis, insert a probe (not a fix), evaluate the result, isolate the root cause, then correct. BodhiKit never fixes bugs for you. It catches novice anti-patterns (random code changes, print statements without hypothesis, ignoring error messages) and redirects to systematic investigation.

Example: Your todo delete button does not work. Instead of looking at the code, BodhiKit asks "What did you expect? What happened? What is your theory?" Then guides you to add a targeted probe, trace the data upstream, and find the real cause yourself. Auto-invoked by `/practice` and `/teach` when your code has bugs.

---

## Learner Profile

BodhiKit maintains a cross-project learner profile at the `learningWithBodhi/` root. In 1.7.0 it is split across two files so routine skills load only what they need:

- **`learningWithBodhi/.bodhi-profile.json`** — small, frequently read. Your career goals, learning motivations, overall Bloom's levels, cumulative stats (total sessions, exercises, concepts mastered, milestones), patterns (persistent challenges, consistent strengths), learning style preferences.
- **`learningWithBodhi/.bodhi-profile.projects.json`** — read only by cross-project skills like `/mentor` and `/evaluate`. Holds `activeProjects` and `completedProjects` arrays with per-project metadata (topic, started date, current phase, Bloom's level, pace, status, track purpose). Grows linearly with your project count, so isolating it from the smaller top-level file keeps daily skill reads lean.

Both files are created when you start your first learning project and updated as you progress. The split allows BodhiKit to personalize guidance across different projects and power the `/mentor` skill while keeping per-session context small.

---

## How Agents Work Behind the Scenes

BodhiKit uses three specialized AI agents that handle complex tasks. You never invoke agents directly. Skills launch them automatically when needed.

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
- 3 consecutive correct quiz answers
- Spaced repetition Box 4 or 5
- Can explain it to someone else (Feynman check)

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
