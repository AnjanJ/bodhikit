# Upgrading BodhiKit

Upgrading the plugin itself is `/plugin update bodhikit@bodhikit` (or reinstall) followed by a Claude Code restart. Your `learningWithBodhi/` folders are never touched by an install. This page covers the one thing that *can* need attention: the tracking files inside existing learning projects.

## 1.18.0

No tracking-file change. Run `/plugin update bodhikit@bodhikit` (or reinstall) and **restart Claude Code** — the knowledge bases are now registered skills and the learning-project rule arrives through a SessionStart hook, and both take effect on the next session start. If you had been enabling the plugin per-project, nothing else changes.

## The one command

If you have learning projects from any version before 1.10, run this once per project (or once from the `learningWithBodhi/` root to convert every project):

```
/bodhikit:housekeep migrate
```

It runs whichever transforms your project is missing, in version order, backs up first, and is safe to run twice.

## By the version you are coming from

**From 1.11.x or later** — nothing to do. Tracking files are unchanged across 1.11 → 1.16. If you upgraded from a pre-1.11 version *without* running `migrate`, or your files were hand-edited by an older executor, the Stop hook may flag them once after upgrade; the message names the repair (`bodhi-state normalize` or `verify`), and it is one command.

**From 1.10.x** — no data migration. 1.11.0 added the deterministic state layer (`scripts/bodhi-state`), which requires `python3` on PATH (present by default on macOS and Linux). **Windows:** use WSL, or make sure a `python3` alias exists on PATH — without it the plugin degrades to hand-edited JSON fallbacks and the Stop-hook safety net stays silent rather than erroring. Two commands moved: `/explain <concept>` is now `/teach <concept>` (tell it you just want to understand — same Feynman deep dive, no exercise), and `/status` is now `/progress quick` (with `/progress all` for the cross-project table).

**From 1.9.x or earlier** — run `/bodhikit:housekeep migrate`. It handles the chained v1 → v2 → v3 conversion in one command: if the project is on the pre-1.7.0 layout both transforms run; if it already migrated to 1.7.0, only the 1.10 transform runs.

**From 1.6.x** — same command. The 1.7.0 transform and the 1.10 transform both run in one invocation.

## What the transforms do

**1.7.0 target** (v1 → v2 layout — progressive disclosure). Converts:

- `state.json` — strips long narrative fields (`lastSessionSummary`, `bloomResetNote`); they move to `progress.md` where prose belongs. State stays slim: pointers, counts, current values.
- `plan.md` (monolithic) → `plan/README.md` + `plan/phase-{N}.md` (sectional). Skills like `/teach` and `/continue` load only the current phase, not the whole plan.
- `progress.md` (flat chronological log) → live + archive + summary. The latest session sits at the top; older sessions move to `progress/archive/` with one-line pointers in a summary block.
- `assessment.md` (flat) → `assessments/latest.md` + `assessments/archive/`. Same pattern.
- `.bodhi-profile.json` (monolithic) → `.bodhi-profile.json` (top-level: cumulative stats, patterns) + `.bodhi-profile.projects.json` (per-project metadata).

**1.10 target** (v2 → v3 schema bump on `spaced-review.json`). Per-concept Bloom + Feynman tracking — the fields that make mastery observable end-to-end:

- `concepts[].bloomLevel` (0–6, integer) — current Bloom's level for the concept. Set by `/quiz`, `/teach`, `/practice` as they observe the learner's level. Ratchet-up only.
- `concepts[].feynmanPassed` (boolean) — set to `true` when the learner produces a clear, jargon-free explain-back. Owned by `/teach`. Set, never unset.
- `concepts[].consecutiveCorrectAtL4Plus` (integer) — running counter for the mastery criterion. Incremented by `/quiz` on correct answers at Bloom 4+; reset to 0 on any incorrect, any partial, or on `/forget` ("consecutive correct" means uninterrupted corrects — a partial breaks the streak).
- New entries in `reviewHistory[]` also include `bloomLevel` (which level a given quiz question tested at) and, since 1.11.3, `boxBefore` — the box the concept occupied when the review was answered, which makes `bodhi-state retention` exact rather than reconstructed.

Together these fields make the canonical mastery formula computable: `mastered = bloomLevel ≥ 4 AND consecutiveCorrectAtL4Plus ≥ 3 AND box ≥ 4 AND feynmanPassed`.

## Safety

- **Per-target idempotent.** Each transform's marker file (`.bodhi/.migration-1.7.0.md`, `.bodhi/.migration-1.10.md`) tracks whether it has run; running the command twice in a row is a no-op once both markers are present.
- **Non-destructive.** Each transform backs up its pre-state to a dedicated directory (`.bodhi/.pre-1.7.0-backup/`, `.bodhi/.pre-1.10-backup/`) for one minor version each. If anything looks off, you can restore from there.
- **Transparent.** The command prints a before/after byte report scoped to whichever transforms ran, and lists every archive entry it created.
- **Verified on real data.** The 1.10 transform was hardened through a multi-pass live run on real learning projects before 1.11.0, and since 1.11.0 the transform itself runs in `bodhi-state` (backup → in-place transform preserving every non-canonical field → field-loss verification → marker), covered by the deterministic test suite.

## After migrating

Your skills work exactly as before — just faster, because routine sessions read less context, and Bloom/mastery is now observable in the data instead of inferred. History you do not need right now (older sessions, the full plan arc, prior assessments) stays on disk, reachable by pointer when a situation justifies it (for example `/evaluate` reading the full history for trajectory analysis, or `/continue` reading recent archive entries when you have been away for over 30 days).

`/housekeep` also handles ongoing rotation — at session boundaries it moves the previous live session into `progress/archive/` and writes a one-line summary pointer. See [GUIDE.md → Housekeeping Your Tracking Files](./GUIDE.md#housekeeping-your-tracking-files).
