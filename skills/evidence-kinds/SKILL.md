---
description: "Evidence kinds: how to teach, set exercises, grade and record subjects whose work is not code — problems with answers, written argument, performed skills. Load only when bodhi-state reports a concept's evidenceKind as problems, writing or performed; never on code."
user-invocable: false
---

# Evidence Kinds — Teaching What Is Not Code

**Evidence tier: mixed, named per section.** Retrieval and spacing outside code are bedrock; the saved key and the graded debrief are strong-qualitative; interleaving motor practice is contested; photo feedback on a physical skill has no controlled evidence.

Load this KB only when `bodhi-state` reports a concept's `evidenceKind` as `problems`, `writing` or `performed` (`session-brief`, `due`, a `gate-check` row, `snapshot`). On `code` nothing here applies: the skill's own text is the code path, unchanged.

Teaching is the same in every subject: dialogue, retrieval, spacing, the explain-back. Quizzing helps across subjects (Yang et al. 2021, classroom quizzing g = 0.50 across 18 subject areas), including vocabulary (Karpicke & Roediger 2008, Swahili–English pairs) and history (Carpenter et al. 2009). What differs is the evidence: what an exercise is, what counts as applied work, and who can check it.

| Kind | Applied work | Who checks it | Recorded as |
|---|---|---|---|
| `problems` | worked problems with exact answers — a genetic cross, a physics or chemistry calculation, a proof step, a grammar exercise | you, against worked answers saved before the attempt | `--applied --evidence <the learner's work>` |
| `writing` | a written piece applying the concept to a case the lesson did not use | you, against criteria saved before the writing | `--applied --evidence <the piece>` |
| `performed` | a practice rep away from the screen — a dish cooked, a drawing made, a passage played, a conversation held | the learner's word, labelled as theirs; or a photo you examined | `--applied reported`; `--applied inspected` |

Applied work has a basis: `observed` (you read the work in the project), `inspected` (a photo or transcript you examined) or `reported` (the learner's word). The last two count toward *Solid* and the gate only on `performed`; `record-review` refuses them on any other kind.

The explain-back rubric is the same for every kind: the `feynman-technique` KB *Grading the Explain-Back*, the same five checks and the same rows. Its anchors are database examples; read them as shapes. Row 3 picks the right one for a given case, row 4 names where it breaks and the trade-offs, row 5 defends a choice between alternatives, in any subject.

A learner who says the kind is wrong for a module is usually right: record the change with `set-evidence-kind` (`state-ops` KB). Every review is kept.

## Intake and assessment (`/learn`, `/assess`)

- Ask about the learner's background in the subject, never their programming experience: what they have read, made, played or practised; what they can already do; what made them start.
- Assess with the subject's own material: a case to classify, a problem to solve, a short passage to analyse. For `performed`, ask how they do it now, step by step. What they describe is the evidence; you have not seen them do it, and say so.
- Agents never load this KB. When a caller hands assessment or resource search to an agent on a non-code subject, it puts the two bullets above (or the *Sources* rule below) in the agent's prompt.

## Teaching (`/teach`)

- Examples, the worked example and every checkpoint question come from the subject: a case, a formula worked by hand, a diagram described in words, a recipe step, a bar of music, a sentence. No code anywhere, including analogies.
- "What would this code output?" becomes a prediction on a concrete instance: the ratio of offspring from this cross, what the argument commits you to in this case, what the sauce does if the butter goes in cold.
- The analogy ladder's last rung (`feynman-technique` KB, rung 4) is a **second worked case from the subject**: the same idea in a different instance, never code.
- Name at least one source from `.bodhi/resources.md` for the lesson's central claim, in one line ("This is the standard account — <source>, chapter N"). Where nothing runs, a claim needs somewhere the learner can check it. If `resources.md` has nothing that covers it, say so and offer `/resources`.
- `/pair` and `/debug-together` are code tools. Do not offer them. On `performed`, the "we do" step is talking one rep through, step by step, before the learner does it.

## The exercise and its key (`/teach` Phase 4, `/practice`)

One folder per exercise: `exercises/NN-<slug>/`, never reused for another exercise. Before the learner sees the task, write its key in that folder. The key is the referee code gets from running: fixed before the attempt, so the grade cannot drift toward whatever the learner wrote.

- **`problems`** — `answers.md`: each problem's worked solution and final answer. The task goes in `README.md`. The learner works in a file of their own in the same folder (`work.md`, or a photo of handwritten working saved there). Grade problem by problem against the key. Work that reaches the key's answer by a sound method is the applied observation; a wrong answer is a teaching moment, not an applied correct.
- **`writing`** — `criteria.md`: three to five checks a reader can verify, among them that the piece applies the concept to the case named in the task, a case the lesson did not use. The task in `README.md` names that case. The learner's piece is its own file in the folder. A piece that meets every criterion is the applied observation; one that misses a criterion gets a review (*Review*, below) and counts once revised to meet it.
- **`performed`** — `criteria.md` is the practice task: one rep sized to 10–30 minutes away from the screen, what to watch for while doing it, and the three debrief questions that follow it (*Practice reps*, below). Tell the learner the questions now, so they practise watching for the answers.

Tell the learner once that the key is in the folder and that opening it before trying only costs them the learning. `record-review --applied --evidence exercises/NN-<slug>/<file>` refuses the key itself, the `README.md`, anything under `.bodhi/`, and work with no key beside it (`state-ops` KB). If it refuses, the key was not saved first: say so, set a fresh exercise with its key, and do not work around the check.

## Quiz forms (`/quiz`, `/reflect`, `/continue`)

Pose each question as something to do with the subject. Never code, and never "define X":

- **`problems`** — a short problem with an exact answer: a cross to predict, a quantity to compute, a sentence to correct. Work the answer out before you ask, and grade against it.
- **`writing`** — a case to judge: a short passage, a claim, a scenario. ("A city bans private cars downtown. Which of the three theories justifies it, and what would the other two object?")
- **`performed`** — a situation from practice: what would you do when, what went wrong when, why does. ("Your mayonnaise splits halfway. What happened, and how do you bring it back?") A due performed concept also gets a practice rep (*Practice reps*, below).

The level still comes from the answer's row in the `feynman-technique` rubric.

## Review (`/review`)

The `code-reviewer` agent reads code only. Review `problems` and `writing` work yourself, in place:

- Quote the learner's own line (`> line`) before every point.
- Say what the passage shows about understanding: where the reasoning holds, where it assumes what it should argue, which step of the method went wrong.
- Ask one question per point. Never rewrite the piece or rework the problem. Point at the line, ask what they meant, and let them fix it.

## Reconfirm at the gate (`/teach` Phase 1)

A `gate-check` row carries the prerequisite's own `evidenceKind`, which may differ from the new module's. A `no-applied-evidence` reconfirm takes that kind's form: one problem against a freshly saved key, a short written application to a new case with its criteria saved first, or one practice rep with its debrief. A `single-evidence` or `stale` reconfirm is one question in the kind's quiz form.

## Sources (`/learn`, `/resources`)

Where nothing runs, the sources are the check. Before the first lesson of a non-code project, `.bodhi/resources.md` holds at least two verified sources for the subject: a standard textbook or reference work, and one open resource (university course notes, a professional society's guide, a museum or archive collection). Search the subject's own literature, never programming catalogs. For a hands-on subject, add the safety reference where one exists: USDA safe minimum internal temperatures for cooking; the American Chemical Society's RAMP framework for lab chemistry.

## Practice reps and the debrief (`performed`)

The tutor cannot see a rep; it can grade the debrief. Structured debriefs improve performance (Tannenbaum & Cerasoli 2013, d = 0.67). Specific questions make self-assessment more accurate than "how did it go?" (Zell & Krizan 2014), though self-report stays weak evidence (Dunlosky & Rawson 2012). Spacing practice works for hands-on skills (Moulton et al. 2006, a randomized trial of microsurgery training; Lee & Genovese 1988, a meta-analysis of motor practice).

When the learner says they did a rep:

1. **Debrief before recording anything.** Ask the three questions one at a time: *What did you do?* (step by step, with quantities or times where they matter) *What went wrong or surprised you?* *What would you change next time, and why?*
2. **Grade the debrief** with the `feynman-technique` rubric: it is an explanation of the practice. Its result and row are the review's. Record `record-review --result <r> --tested-bloom <row> --applied reported --source <this skill>`. The debrief's grade moves the schedule; the rep itself is on the record as the learner's account.
3. **Declined the debrief** → record nothing for that rep, and say it counts once it is debriefed ("Tell me about it whenever you're ready, and it goes on the record").
4. **A due performed concept** (`/continue`, `/quiz`) → offer a rep with its debrief together with one knowledge question on the reason behind the skill. If they have not practised since the last review, ask the knowledge question alone and record it without `--applied`. Never ask them to describe a rep they did not do.

Interleaving reps of different skills is contested for motor learning (Ammar et al. 2023, 2024): offer it, never impose it.

*Solid* that rests on the learner's word is shown as theirs: "*Solid*, by your account" (`solidByReport` and `solidBasis` in `mastery` and `snapshot`). The level, the streak, the schedule and the explain-back behind it are still graded by you.

Languages split by module. Vocabulary and grammar are `problems` (spacing works there: Kim & Webb 2022). Writing in the language is `writing`. Speaking is `performed`: speaking grows by producing speech, not only by understanding it (Swain's output hypothesis), so a speaking rep is a conversation held, then debriefed.

## Photos (`performed`, `problems`)

When the learner shares a photo of their work, such as a plated dish, a drawing or a page of handwritten working:

1. **Examine it first.** Say what you can judge from the image (proportion, composition, colour, the line of working) and what you cannot: taste, texture, temperature, sound, the process, anything out of frame.
2. **Then record it.** On `performed`, as `--applied inspected`, with `--evidence <path>` when it is saved in the project. Handwritten problem working saved beside `answers.md` is ordinary `observed` work: you read the working.
3. **Weigh it lightly.** No controlled study shows that feedback on a still image improves cooking or drawing. What you see is one more part of the debrief, not a verdict on the skill.

Never claim to have seen what you did not, and never certify a physical skill.

## Safety

Safety first in hands-on subjects, no step-by-step coaching of hazardous procedures, and no personal medical advice. These limits are the learning-project rule's (`rules/learning-project.md`), which every session inside a learning project already carries.
