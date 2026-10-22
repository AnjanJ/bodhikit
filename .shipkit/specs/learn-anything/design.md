# Design: Learn anything

> Design approved 2026-10-19 after a review against the code. That review found six local
> defects, and the corrections are folded in below.

## Approach

The kind of evidence is a project fact that the script owns. `bodhi-state` records it, works out
the effective kind of every concept (module override, else project, else `code`), and hands it
to the skills in the outputs they already read:
- `session-brief`, `due`, `revision-brief`
- `snapshot`, `mastery`, `syllabus`
- `gate-check`

Skills branch once. On `code` they run today's text. On any other kind they load one new
knowledge base, `evidence-kinds`, and follow its section for that kind. A code session loads no
new KB. That claim is checked, not assumed:
- a golden-output test proves the engine is byte-identical for code;
- a transcript assertion proves no code scenario loads `evidence-kinds`;
- the code eval suites must pass at their recorded levels.

Inside the engine, the kind reaches the counting code through a resolver that `main()` installs
once per process, not through new parameters. Only three places read applied work:
- `_evidence_counts` (`scripts/bodhi-state:2141`)
- `archive_history` (`:2173`)
- `exposure_of` (`:2256`)

All three go through one helper, `applied_basis()`, plus `admits(kind, basis)`. Every other
function reaches them through `applied_evidence` and `exposure_of`, so one rule governs gate,
mastery, tiers, rollups and export. A test pins that no other code reads `applied`.

Every applied-work entry gains a basis: `observed`, `inspected` or `reported`. The field is
written only for the last two. Absent means `observed`, which is what every existing entry is,
so code files stay byte-identical. The learner's word counts only on a `performed` concept, at
write time and at read time, including archived history.

Non-code kinds get the referee that code gets from running. Each exercise has its own folder,
and the tutor saves the key there before the attempt: `answers.md` for `problems`, `criteria.md`
for `writing`. The script checks the key sits beside the evidence.

For a performed skill, the tutor can't see the rep but can see the debrief. The debrief is graded
like any explain-back and carries the review's result and level, so the box, the streak and the
retention numbers stay tutor-graded in every subject. The rep rides on the same entry as
`reported` applied work.

Safety goes in the learning-project rule. Cowork gets a `.plugin` package built from the same
tree. Nobody claims Cowork support until a probe by hand passes.

**Releases.** Two stages, each green on `dev/check.sh` and the full eval suite with the code
groups unchanged:

| Release | Contents | REQs |
|---|---|---|
| **1: learn anything** | the engine; all four kinds end to end; practice reps and debriefs; photos; "by your account"; safety; the Cowork package | 1–37, 40 |
| **2: in the open** | Claude chats on a connected computer, hosts without files, outcomes per kind, repositioning, the voice | 38, 39, 41–43 |

Releases A and B from the first draft are merged at the maintainer's choice (2026-10-19), so
`performed` never ships half-built. REQ-38 moved to Release 2 at the maintainer's choice
(2026-10-22), after the first probe: the hooks need work in cloud chats, and Release 1 claims
no Cowork support.

## Decision: Classify subjects by the kind of evidence, not by subject   (→ REQ-4, REQ-6, REQ-20)

**Context.** BodhiKit must tell code curricula from everything else without forking its pedagogy
per subject. The research inventory found that every code assumption that matters is about
evidence: who can check the work, and how. Teaching dialogue, retrieval and spacing are the same
in every subject (Yang et al. 2021: classroom quizzing g = 0.50 across 18 subject areas).

**Alternatives.**
1. Binary: `code` vs `non-code`.
2. A subject taxonomy (humanities, sciences, arts, languages, crafts…).
3. Four evidence kinds: `code`, `problems`, `writing`, `performed`, with a per-module override.

**Case for evidence kinds.** The behaviour that differs between subjects follows the evidence:
- what an exercise looks like
- what counts as applied work
- what the referee is
- whether the learner's word is allowed

Four values cover every subject, and a mixed subject splits by module: bioinformatics is
`problems` plus `code`, music is `problems` (theory) plus `performed` (playing). Four kinds also
means four eval groups, a finite test matrix for an unbounded set of subjects. The binary option
would lump genetics problem sets in with cooking.

**Case against.** Learners don't think in evidence kinds, so the proposal must be phrased in plain
words (REQ-5). Some modules are ambiguous: lab chemistry is `problems` on paper and `performed` at
the bench. Languages split three ways: vocabulary and grammar are `problems`, writing is
`writing`, speaking is `performed`. The axis puts more decisions on `/learn`.

**Decision.** We chose four evidence kinds with a per-module override.
**Falsifiability.** We would reverse this if learners change the proposed kind on more than 5 of
the first 20 non-code projects: the axis would not match how they see their subject.
**Fired-if.** manual

## Decision: The kind lives in `state.json`, written only by `bodhi-state`   (→ REQ-3, REQ-4, REQ-6, REQ-7, REQ-8, REQ-9)

**Context.** The engine needs a concept's effective kind on every evidence count and on every
write that might carry the learner's word. Plan files are the learner-visible syllabus, but
parsing them is fragile: 1.24.1 fixed plans whose single-number module headings parsed to
nothing, silently.

**Alternatives.**
1. `state.json` gets `evidenceKind` (project) and `moduleEvidenceKinds` (normalized module name →
   kind). Both are written by a new `set-evidence-kind` subcommand.
2. The project kind goes in `state.json`, and the module override is an `**Evidence:**` line in
   the plan phase files.
3. A per-concept field in `spaced-review.json`.

**Case for `state.json`.**
- It sits in the deterministic layer: validated writes, `verify` coverage, and no parsing.
- Readers resolve the module through `norm_module_name`, so a module with no review rows yet
  still joins.
- `set-evidence-kind` rejects a module that matches neither a plan heading nor a review row,
  as a typo guard.
- `/plan view` and `/progress` render `syllabus` output, so the learner still sees each
  module's kind.
- `snapshot` reports `project.evidenceKindRecorded`, so `/continue` can tell "never recorded"
  from "recorded `code`" (REQ-9).

**Case against.**
- A module rename orphans its override. `verify` checks plan names and review-row modules
  together, and reports an orphan as a **warning**, not an error. No subcommand can repair one,
  and an error would make the Stop hook block on it.
- A review row filed under a bare plan id joins the syllabus by id but not the resolver. That
  case gets a test and a warning.
- The kind is not visible in the plan file itself.

**Decision.** We chose `state.json`, with `moduleEvidenceKinds` keyed by normalized module name.
**Falsifiability.** We would reverse this, moving the override into the plan files, if `verify`
reports an orphaned module override in two or more real projects.
**Fired-if.** manual

## Decision: Applied work gets a basis beside the existing flag, read through one helper   (→ REQ-1, REQ-2, REQ-21, REQ-22, REQ-23)

**Context.** `applied` is a boolean that about fifteen functions depend on. The review traced
them to three reading sites (`_evidence_counts`, `archive_history`, `exposure_of`). The existing
self-report precedent (`/forget`'s `selfReport: true`) is excluded only from retention. Mastery,
the gate and exposure treat it as a real miss, so copying that pattern would leak reported work
into *Solid*. Several commands (`due`, `mastery`, `retention`, `calibration`, `record-review`)
never load `state.json` today, yet all of them would need the kind.

**Alternatives.**
1. Add `appliedBasis` (`inspected` | `reported`; absent = `observed`) and an optional `evidence`
   path to history entries.
   - The kind reaches the three reading sites through a resolver installed once in `main()`.
     `read_kinds` falls back to `code` when `state.json` is missing or invalid, so readers never
     fail.
   - The archive keeps counts per basis: `appliedEvidence` = observed; `appliedInspected`,
     `appliedReported` and `builtBy` are written only when non-zero.
2. Replace the boolean with an enum, `applied: "observed" | …`, migrate every file, and pass the
   kind as an explicit parameter to every counter.
3. Inject a `_kind` key into each concept at load time and strip it on write.

**Case for a basis field and a resolver.**
- No migration and no new key on any code entry. Bare `--applied` (`nargs='?'`, const
  `observed`) writes byte-identical output, which the review verified in argparse (REQ-1, REQ-3).
- Only `_evidence_counts` changes its signature. Nothing is written back, so nothing can leak.
  The two lint pins that grep exact source lines (`check.sh:311`, `:342`) stay valid.
- Per-basis archive counts let a later kind change (REQ-7) reach archived history.
- At write time, `record-review` refuses `reported` and `inspected` off `performed` (REQ-2). It
  also requires `--evidence` inside the project for `observed` on any non-code kind (REQ-22).
- Readers degrade to `code`, the strictest reading for reported work. Writers refuse an invalid
  kind. `verify` reports an invalid kind as an error, and a basis without `applied: true` as a
  warning.

**Case against.**
- The resolver is hidden per-process state. That is safe because each process handles one
  `--project` and the tests run the script as a subprocess, but a future in-process caller would
  need to install it.
- A reader that bypasses `applied_basis()` would count reported work as observed. The guard is a
  test, not the type system.

**Decision.** We chose a basis field written only when not observed, read through one helper,
with the kind from a resolver.
**Falsifiability.** We would reverse this, moving to the enum and explicit parameters, if a reader
is found counting `reported` work toward *Solid* or the gate on a non-performed concept twice
after release.
**Fired-if.** manual

## Decision: A practice rep is recorded as its graded debrief   (→ REQ-24, REQ-28, REQ-29, REQ-30, REQ-31, REQ-32)

**Context.** For a performed skill, the learner chose spaced practice reps plus knowledge
questions (intake answer 3). The tutor cannot see the rep. The box and retention statistics must
keep meaning "recall the tutor graded" for every subject.

**Alternatives.**
1. Make each due review one entry. The tutor grades the debrief (what you did, what went wrong,
   what you would change and why) with the explain-back rubric, and that grade is the review's
   result and level. The box moves as for any due review, and the rep rides on the same entry as
   `applied` with basis `reported`. Debriefs record under existing sources; a rep is not
   instruction, so `INSTRUCTIONAL_SOURCES` is unchanged.
2. Give reps their own schedule track, moved by the learner's report.
3. Record reps as history notes only, and schedule only the knowledge.

**Case for the graded debrief.** The box, the streak and every retention number stay tutor-graded
(REQ-24), with no second schedule and no new field. Retention does not exclude these entries,
because the result is the tutor's grade of the debrief. The helper is kept distinct from
`is_self_report` so the two never merge. The evidence supports each piece:
- Spaced practice is well supported for hands-on skills: Moulton et al. 2006 randomized
  microsurgery training, and Lee & Genovese 1988 meta-analysed motor practice.
- Structured debriefs improve performance: Tannenbaum & Cerasoli 2013, d = 0.67.
- Specific questions make self-assessment more accurate than "how did it go?": Zell & Krizan 2014.

**Case against.**
- The debrief measures understanding of the practice, not the hands. A learner who explains well
  but cooks badly can reach *Solid* "by your account", and one who cooks well but describes it
  poorly is held back.
- The rep and the knowledge share one due date.
- Interleaving reps is contested for performed skills (Ammar et al. 2023/2024), so the tutor
  offers it but does not impose it.

**Decision.** We chose to record a rep as its graded debrief.
**Falsifiability.** We would reverse this if concepts whose *Solid* rests on `reported` practice
fail their next delayed review at a recall rate at least 20 points below concepts resting on
`observed` work, over the first 30 such reviews.
**Fired-if.** manual

## Decision: Non-code teaching lives in one KB that code sessions never load   (→ REQ-1, REQ-10–REQ-18)

**Context.** The non-code paths touch `/learn`, `/teach`, `/practice`, `/quiz`, `/review`,
`/continue`, the gate reference and two agents. `/teach` has 158 bytes of headroom under the
18,432-byte lint budget, and `state-ops` and `state-schema` have 5 each.

The OpenAI build turns a KB into a single file and drops its `references/` folder
(`platforms/openai/build_plugin.py:303–311`). So a KB cannot lean on `references/`, and the
budget must be freed by removing duplication.

**Alternatives.**
1. A new `evidence-kinds` KB (`user-invocable: false`) with one section per kind and per phase:
   intake, assessment, teach, exercise and key, quiz, review, reconfirm, sources, debrief.
   - Skills load it only when the brief's `evidenceKind` is not `code`.
   - Agents never name it, because lint rule 2 would make them preload it into every code
     assessment. Callers pass the non-code instructions in the agent's prompt instead.
   - The four-row table of the kinds in plain words lives in `/learn`, so proposing `code` loads
     nothing new.
2. Inline branches in each skill.
3. Per-skill `references/<kind>.md` files.

**Case for one KB.**
- A code session loads no new KB.
- Each skill gains one routing line.
- Non-code pedagogy has one place to read, review and evaluate.
- The OpenAI build carries the KB as `references/knowledge/evidence-kinds.md` without changes.

**Case against.**
- It is one more load, roughly 10–15 KB, on every non-code session.
- A reader of `/teach` doesn't see the non-code behaviour in place.
- The KB could outgrow the budget. The fallback is splitting it into several KBs, not into
  `references/` files.
- The skills do change text (routing lines, trims), so REQ-1 is proven by tests, not by
  construction.

**Decision.** We chose one `evidence-kinds` KB, loaded only off the code path and never named by
an agent.
**Falsifiability.** We would reverse this, splitting it into several KBs, if it passes 17,408
bytes, 1 KB short of the lint budget that would otherwise fail first.
**Fired-if.** `test -f skills/evidence-kinds/SKILL.md && test "$(wc -c < skills/evidence-kinds/SKILL.md)" -gt 17408`

## Decision: Non-code work is judged against a key saved before the attempt   (→ REQ-11, REQ-12, REQ-22)

**Context.** Code has a referee the tutor can't argue with: it runs or it doesn't. Without one,
the tutor's grade of a problem set or an essay is its judgment alone, and that judgment can drift
toward whatever the learner wrote. `/practice` already uses one folder per exercise
(`exercises/NN-topic/`). `/teach` uses one folder per module, where an old key would satisfy a
check.

**Alternatives.**
1. Each non-code exercise gets its own folder.
   - Before presenting the exercise, the tutor writes `answers.md` (`problems`) or `criteria.md`
     (`writing`) there.
   - `record-review --applied observed --evidence <path>` on a non-code kind requires a key in
     the evidence file's own folder.
   - It rejects evidence that is the key itself, a `README.md`, anything under `.bodhi/`, or a
     path that resolves outside the project.
   - `rules/learning-project.md` gains an explicit exception: the tutor may write its key in
     `exercises/`.
2. A prose instruction only.
3. A `set-exercise` subcommand that registers the key with a timestamp, and `record-review`
   checks the order.

**Case for a saved key.** It gives non-code work a referee fixed before the learner's attempt, as
code has. It is cheap, the script can check it, and an eval checks the order (the key's write
precedes the attempt in the transcript). A photo of handwritten problem work, saved in the
exercise folder, is `observed` evidence with that path. The learner can open the key afterwards
to study it.

**Case against.** The key sits in the learner's own folder, so they could peek before trying;
only their own learning loses, and the tutor says so. The script checks that the key exists, not
that it came first. The order is checked by evals, not enforced.

**Decision.** We chose a per-exercise folder with a saved key, checked by the script.
**Falsifiability.** We would reverse this, enforcing order with a registered timestamp, if an eval
shows the key written after the learner's attempt in more than 1 of 10 runs.
**Fired-if.** manual

## Decision: `/review` reviews problems and writing itself; `code-reviewer` stays code-only   (→ REQ-1, REQ-18)

**Context.** The `code-reviewer` agent is mandatory in `/review` and used by `/teach` and
`/practice`. It reads code, quotes `[lang]` fences and never writes corrected code.

**Alternatives.**
1. `/review` reviews problems and writing in its own context, following the `evidence-kinds` KB.
   The mandatory-agent line and its "You MUST use the Agent tool" phrase stay, conditional on code.
2. Generalize `code-reviewer` into a `work-reviewer` that serves every kind.
3. Add a second agent for written work.

**Case for reviewing in `/review`.** `code-reviewer` stays untouched (REQ-1). There is no agent to
maintain, and a problem set or a short essay fits in context.

**Case against.** Long written work loses the agent's context isolation, and the agent-fallback
symmetry the other skills have is gone for non-code.

**Decision.** We chose to review problems and writing in `/review` itself.
**Falsifiability.** We would reverse this, adding a second agent, if evals show `/review` rewriting
the learner's work in 2 or more of 10 runs on non-code work.
**Fired-if.** manual

## Decision: Safety lives in the learning-project rule   (→ REQ-33, REQ-34)

**Context.** The research found no standard for AI tutors coaching hazardous practical work, so
BodhiKit writes its own rule. The rule reaches every session inside a learning project through
the SessionStart hook, and on hosts without hooks the OpenAI adapter reads it at first contact.

**Alternatives.**
1. Put it in `rules/learning-project.md`, capped at 4,096 bytes by a new rule-49 check.
2. Make it a safety KB that skills load per phase.
3. Write it into each skill's prose.

**Case for the rule.** It arrives before any skill fires, lives in one place and costs about 600
bytes. The principle is to decline step-by-step coaching wherever the learner's own report
would be the only safety check: mains electrical work, chemistry beyond the kitchen, foraging,
medical techniques. The tutor still teaches the concepts and points to qualified instruction and
to references such as the ACS lab-safety guidelines (RAMP) and the USDA safe-temperature chart.
It also bars personal medical advice.

**Case against.** It adds about 600 bytes to the floor of every learning session, code included.
That changes no code behaviour, but it is not zero. It also doesn't reach a learner before
`/learn` has made a project; the model's own safety training covers that gap.

**Decision.** We chose the learning-project rule.
**Falsifiability.** We would reverse this, moving to a KB loaded per phase, if the rule passes
3,584 bytes, 512 short of the lint cap that would otherwise fail first.
**Fired-if.** `test "$(wc -c < rules/learning-project.md)" -gt 3584`

## Decision: Cowork gets a `.plugin` package, and support is claimed only after a probe   (→ REQ-37, REQ-38)

**Context.** Cowork's plugin docs describe the same schema as Claude Code's: `skills/`, `agents/`,
`hooks/hooks.json` with `SessionStart` and `Stop`, and `${CLAUDE_PLUGIN_ROOT}`. Plugins ship as
`.plugin` zips. It is unverified whether `python3` is available there, whether the hooks fire,
and whether the working folder matches the hooks' path markers. There is no headless Cowork
runner.

**Alternatives.**
1. A `.plugin` zip built from the canonical tree by a script, with a deterministic package test,
   plus a probe checklist the maintainer runs by hand.
2. Tell Cowork users to install from the GitHub marketplace (unverified that Cowork supports it).
3. A Cowork-specific adapter like the OpenAI one, built up front.

**Case for the zip and a probe.** One source tree, a testable package, and no adapter until a
probe shows one is needed. 1.18.0's lesson applies: verify against the runtime before claiming
anything.

**Case against.** A `.plugin` must be downloaded again for every release. If `python3` is missing
in Cowork, the deterministic layer cannot run there and an adapter becomes Release 1 work.

**Decision.** We chose a built `.plugin` package and a probe by hand before any claim of support.
**Falsifiability.** We would reverse this, building an adapter, if the probe shows `bodhi-state`
cannot run in Cowork.
**Fired-if.** manual

**Probe, 2026-10-22.** Not fired: `bodhi-state` runs, and checks 1, 2 and 5 pass. Both hooks
fail; the next decision covers them.

## Decision: In a cloud chat, the hooks follow what the session touched, not its working folder   (→ REQ-38)

**Context.** Since October 2026 Cowork is an ordinary Claude chat. The chat runs in a cloud
sandbox whose working folder is `/home/claude`. The learner's folder stays on their computer:
the chat copies files into the sandbox, runs `bodhi-state` on the copy and copies them back.
The 2026-10-22 probe found that both hooks run there (the Stop hook blocked on a copy placed
under `/home/claude`), but both look only at the working folder, so neither sees the learner's
project. No folder is attached when a chat starts, so no SessionStart hook can see one.

**Alternatives.**
1. Two hook changes. The Stop hook also checks every project the session's transcript shows it
   closed with `touch-state`, wherever that project is. The learning-project rule is also
   injected when a BodhiKit skill first runs (`UserPromptExpansion` for a typed `/bodhikit:*`,
   `PreToolUse` on the `Skill` tool otherwise), once per session, only in a cloud chat (the
   sandbox has `/mnt/user-data` and the working folder is not a learning project).
2. The skills load the rule themselves when the session lacks it, and close by writing the sheet
   without a hook.
3. Accept the gap: claim tracked state in cloud chats, but not the rule or the sheet check.

**Case for the hooks.** They are deterministic and testable, which is the repo's rule for
executor discipline. The Stop hook already runs in cloud chats and already reads the
transcript; it only looks in the wrong place. The rule carries the safety layer (learner
content is data; Safety First) that learning any subject relies on, so alternative 3 ships the
riskiest gap. Alternative 2 asks a model to notice that something is missing from its context,
which models do not do reliably.

**Case against.** `UserPromptExpansion` and `PreToolUse` on `Skill` are documented for Claude
Code but unproven in cloud chats, and the `Skill` tool's input is undocumented, so a second
probe must confirm both. Telling a cloud chat apart rests on the sandbox's layout, which
Anthropic can change without notice; the rule would then stop arriving and only a probe would
notice. The Stop hook change reaches Claude Code and Codex too: a session started outside a
project that studied it is now asked for the sheet. A copy made without `revision/` can make the
hook ask for a sheet the learner's folder already has, so the reason has to say to bring that
folder over and add to today's sheet.

**Decision.** We chose the two hook changes. The rule's new path stays out of Claude Code: there
it would tell a session started in a code repository that it is in a learning project and should
not write code.
**Falsifiability.** We would reverse this, moving the rule into the skills, if the second probe
shows that neither `UserPromptExpansion` nor `PreToolUse` on `Skill` fires in a cloud chat.
**Fired-if.** manual

## Data / interface changes

**Tracking files.** All new fields are optional, written by the script, and default to today's
meaning. Order of change per the repo rule: the `state-schema` KB, then `scripts/bodhi-state`
plus tests, then skills.

| File | Field | Meaning | REQs |
|---|---|---|---|
| `state.json` | `evidenceKind` | `code`, `problems`, `writing` or `performed`; absent = `code` | 3, 4 |
| `state.json` | `moduleEvidenceKinds` | normalized module name → kind | 6, 7 |
| review entry | `appliedBasis` | `inspected` or `reported`; only with `applied: true`; absent = `observed` | 21, 23 |
| review entry | `evidence` | project-relative path of the applied work | 22 |
| `archivedSummary` | `appliedInspected`, `appliedReported`, `builtBy` | per-basis archive counts, only when non-zero; `appliedEvidence` = observed | 7, 23 |

**`bodhi-state` CLI and outputs.**

| Surface | Change | REQs |
|---|---|---|
| constants | `EVIDENCE_KINDS`, `APPLIED_BASES`, `UNSEEN_BASIS_KINDS = ("performed",)`, pinned by lint to the `evidence-kinds` KB and `state-schema` | 4, 21, 23 |
| resolver | `read_kinds`, `kind_of_module`, `effective_kind`, `applied_basis`, `admits`. `_evidence_counts` returns per-basis counts | 3, 6, 23 |
| `set-evidence-kind --kind K [--module M] [--clear]` | new subcommand. Keeps every review; rejects an unmatched module | 4, 6, 7 |
| `record-review --applied [BASIS] [--evidence PATH]` | bare = `observed`. Rejects `reported`/`inspected` off `performed`. `observed` off `code` needs `PATH` with a key beside it | 2, 21, 22 |
| `session-brief`, `due[*]`, `revision-brief[*]` | `evidenceKind` | 8, 15 |
| `snapshot` | `project.evidenceKind`, `project.evidenceKindRecorded`, `mastery.modules.*.evidenceKind`, `mastery.solidByReport`; per-concept `appliedBasis` behind *Solid* | 8, 9, 25 |
| `mastery`, `syllabus` | `evidenceKind` per module (and the project, for `syllabus`) | 8 |
| `gate-check` | `evidenceKind` per prerequisite row (the prerequisite's own kind) | 17 |
| `retention`, `export-anonymized` | top-level `byKind`, `byBasis` (the `export.project` key set is unchanged) | 27 |
| `verify`, `normalize` | new shapes. Invalid kind = error; basis without `applied` = warning; orphaned override = warning | 7, 21 |

**Knowledge bases and skills.**

| Where | Change | REQs |
|---|---|---|
| new `skills/evidence-kinds/SKILL.md` | one section per kind: intake, assessment, teach examples and analogy rung, exercise and key, quiz forms, review, reconfirm, sources, debrief and reps, photos | 10–18, 26, 28–32 |
| `/learn` | four-row kind table; propose and confirm; `set-evidence-kind` after `state.json` and the plan exist; `/resources` before the first lesson; non-code intake | 4, 5, 10, 35 |
| `/teach`, `/practice` | one routing line each; offers gated on `code`; basis and `--evidence` on `--applied`; cite a source; per-exercise folder with the key | 11–14, 16, 22, 36 |
| `/quiz`, `/continue`, `/reflect` | non-code question forms; performed due → rep + debrief + knowledge; legacy kind proposal | 9, 15, 28–32 |
| `/review` | non-code work reviewed in place; the code-reviewer line becomes conditional on code | 18 |
| `/progress` | "by your account" from `appliedBasis` and `solidByReport` | 25 |
| `skills/teach/references/prerequisite-gate.md` | the reconfirm and the single-evidence question shaped by the row's `evidenceKind` | 17 |
| `skills/reflect/references/revision-sheet.md` | "paste the code" generalized to the subject's own material | 14 |
| `blooms-taxonomy` *Applied Evidence* | the basis, and which kinds may use which | 21, 23 |
| `feynman-technique` | rung 4 stays "code-restatement" for code and defers to the KB otherwise | 14 |
| `teaching-personality` | "the learner does the work"; "writes the code" kept for code | 43 |
| `agents/skill-assessor.md`, `agents/resource-finder.md` | non-code wording; instructions arrive in the caller's prompt; the KB is never named | 10, 19 |
| `rules/learning-project.md` | the safety rule; the exception for the tutor's key in `exercises/` | 11, 12, 33, 34 |
| `state-ops`, `state-schema`, `teach`, `state-lifecycle`, `CLAUDE.md` | budget room from de-duplication | budget |

The budget room comes only from removing duplication:
- `state-ops`: about 790 bytes (the repeated carve-out paragraph; the verify note moves to
  `CLAUDE.md`; the legacy rule shortened).
- `state-schema`: about 1,450 bytes (the legacy fallthrough becomes a pointer; duplicated
  bullets dropped; the see-also list shortened; the guiding principle moves to `state-lifecycle`).
- `teach`: about 670 bytes (the gate paragraph that repeats `prerequisite-gate.md`; the duplicate
  chaining note; the analogy ladder defers to the `feynman-technique` KB).

Lint-pinned strings stay.

**Lint (`dev/check.sh`).**
- New pins and checks:
  - 45(g) pins the kind and basis constants.
  - 45(h) requires every subcommand to appear backticked in `state-ops`.
  - A new rule requires every KB to be referenced by at least one command, agent or rule.
  - Rule 54 extends: `--applied <basis>` or `--evidence` must cite `evidence-kinds`.
  - Rule 49 gains the 4,096-byte cap on the rule file.
  - Rule 46 runs the Cowork test.
- Forced edits:
  - The README `Knowledge Bases (18)` count, `marketplace.json` and `test_openai_plugin.py:130–134`
    go to 19.
  - The routing line stays out of the first 8 body lines (rule 14).
  - The offer lines stay in their phases (rules 22–24, 37).

**Platforms and measurement.**

| Where | Change | REQs |
|---|---|---|
| `platforms/cowork/build_plugin.py` → `dist/bodhikit.plugin` | new; `dev/eval/test_cowork_plugin.py` | 37 |
| `docs/cowork-probe.md` | the manual probe checklist and its recorded result | 38 |
| OpenAI package | its test asserts the KB, the fields and the rule are packaged, and that every packaged `<BODHIKIT_PLUGIN_ROOT>/…` path exists | 40 |
| Claude hosts without files | a shared reference adapted from the OpenAI adapter's conversation-only section | 39 |
| `dev/outcomes.py` | recall per kind; *Solid* by report counted separately | 41 |

**Evals.** The code groups stay as they are and must keep passing at their recorded levels, plus
a transcript assertion that no code scenario loads `evidence-kinds` (REQ-1). Fixtures:
- `problems`: genetics (Mendelian crosses)
- `writing`: a copy of the political-theory project with its kind recorded. The original stays
  kind-less, for REQ-3.
- `performed`: cooking (emulsions), plus a home-canning request for the safety check
- a one-point-perspective drawing PNG for the photo scenario

New groups:

| Group | Checks | REQs |
|---|---|---|
| `kind-grading` | apply-band, genuine and parrot on `problems` and `writing` | 20 |
| `kind-fidelity` | no code in quiz or teach; the key written before the attempt; intake without programming; offers gated; the legacy proposal | 9–16 |
| `performed` | debrief before record; no debrief means no record; rep-less review; "by your account" | 25, 28–32 |
| `photo` | the image fixture | 26 |
| `safety` | the canning request; a medical question | 33, 34 |
