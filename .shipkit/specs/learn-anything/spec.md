# Spec: Learn anything

> Spec accepted at commit `dde609a` on master.
> Status: open
> Paths: skills/, agents/, rules/, scripts/, hooks/, dev/, platforms/, docs/, README.md, GUIDE.md, CLAUDE.md, .claude-plugin/

## Purpose
BodhiKit teaches code well because the tutor can check the work: the code runs or it does not.
This spec extends it to every subject (humanities, sciences, art, cooking, music, languages)
by classifying each subject by the kind of evidence that shows a learner can use what they
learned, and teaching, grading and tracking each kind honestly. Coding keeps working exactly
as it does today. Where the tutor cannot see the work (a performed skill), it takes the
learner's word and labels it as the learner's word everywhere it shows.

**Evidence kinds.** Every concept has one effective kind, from its module or its project:

| Kind | Subjects (examples) | Applied work | Who checks it |
|---|---|---|---|
| `code` | programming, data, infrastructure | code that ran | the tutor read it and saw it run |
| `problems` | genetics, physics, chemistry, astronomy, maths, grammar | worked problems with answers | the tutor, against answers saved before the attempt |
| `writing` | political theory, history, philosophy, literature, art history | a written piece applying the concept to a new case | the tutor, against criteria saved before the writing |
| `performed` | cooking, drawing, an instrument, speaking a language, lab or craft technique | a practice rep done away from the screen | the learner's word, or a photo the tutor examined |

## User stories
- As a learner studying code, I want BodhiKit to work exactly as it does now, so that nothing I rely on gets weaker.
- As a learner studying genetics or physics, I want problem sets checked against real answers, so that I know I can solve them, not just talk about them.
- As a learner studying political theory or history, I want written work judged against criteria stated before I write, so that "applied" means I used the idea on a case I had not been shown.
- As a learner studying cooking, drawing or an instrument, I want my practice scheduled and debriefed, and counted honestly as my account, so that I can reach *Solid* without the tool pretending it watched me.
- As any learner, I want the tutor to put safety first and to cite sources in subjects where nothing runs, so that I can trust what it teaches me.

## Requirements (EARS)

### Coding stays as it is
- **REQ-1.** Where a concept's effective evidence kind is `code`, the plugin shall teach, grade, schedule and track it exactly as release 1.24.1 does.
- **REQ-2.** If a review records the learner's word as applied work on a concept whose effective kind is `code`, `problems` or `writing`, then `bodhi-state` shall reject the write with an error naming the concept's kind.
- **REQ-3.** If a project has no recorded evidence kind, then `bodhi-state` shall treat the project as `code`.

### Knowing what kind of subject it is
- **REQ-4.** When `/learn` scaffolds a project, the plugin shall record exactly one evidence kind for the project: `code`, `problems`, `writing` or `performed`.
- **REQ-5.** When `/learn` proposes an evidence kind, the plugin shall describe it to the learner in plain words and record it only after the learner confirms or changes it.
- **REQ-6.** Where a plan module declares its own evidence kind, `bodhi-state` shall use the module's kind for that module's concepts instead of the project's.
- **REQ-7.** When the learner asks to change a project's or a module's evidence kind, `bodhi-state` shall record the new kind and keep every existing review.
- **REQ-8.** `bodhi-state` shall report a concept's effective evidence kind in `session-brief`, and the project's and each module's kind in `snapshot` and `syllabus`.
- **REQ-9.** If a project has no recorded evidence kind and its topic is not about code, then `/continue` shall propose a kind once and record it after the learner confirms.

### Teaching each kind
- **REQ-10.** When `/learn` starts a project whose kind is not `code`, the intake shall ask about the learner's background in that subject and shall not ask about programming experience.
- **REQ-11.** When `/teach` or `/practice` sets an exercise on a `problems` concept, the plugin shall save the worked answers in the project before the learner attempts it and shall grade the attempt against them.
- **REQ-12.** When `/teach` or `/practice` sets an exercise on a `writing` concept, the plugin shall save the task and the criteria the work will be judged on before the learner writes, and the task shall apply the concept to a case the lesson did not use.
- **REQ-13.** When `/teach` or `/practice` sets an exercise on a `performed` concept, the plugin shall describe a practice task the learner does away from the screen together with the debrief questions that will follow it.
- **REQ-14.** While a concept's effective kind is not `code`, `/teach` shall draw its examples, checkpoint questions and the last rung of its analogy ladder from the subject's own material (a case, a formula, a diagram, a recipe step) and shall not use code.
- **REQ-15.** While a concept's effective kind is not `code`, `/quiz` shall pose each question as a case, a problem or a situation from the subject and shall not include code.
- **REQ-16.** While a concept's effective kind is not `code`, the tutor shall not offer `/pair` or `/debug-together`.
- **REQ-17.** When the prerequisite check asks to reconfirm a concept that has no applied work since its last miss, the reconfirm shall be applied work of that concept's kind: a small piece of code, one problem, a short written application, or one practice rep with its debrief.
- **REQ-18.** When the learner asks `/review` to look at work on a `problems` or `writing` concept, the plugin shall review what the work shows about understanding, quoting the learner's own lines, and shall not rewrite it.
- **REQ-19.** When `/resources` or `/learn` searches for learning resources on a subject whose kind is not `code`, the plugin shall search for that subject's sources and shall not return programming catalogs. [untested: needs live web search; verified by a manual run]
- **REQ-20.** The explain-back rubric shall grade an explanation on a concept of any kind by the same five checks and the same rows it uses for code.

### Evidence the tutor can and cannot check
- **REQ-21.** When `bodhi-state` records applied work, it shall store its basis: `observed` (the tutor read the work in the project), `inspected` (the tutor examined a photo or transcript the learner shared) or `reported` (the learner's word).
- **REQ-22.** When applied work on a concept whose effective kind is not `code` is recorded as `observed`, `bodhi-state` shall require the path of the saved work and shall reject a path that does not exist inside the project, or that is the exercise's key, its README or a tracking file. *(Amended 2026-10-19 with the design approval: it covered only `problems` and `writing`, which left `observed` on `performed` unconstrained.)*
- **REQ-23.** `bodhi-state` shall count `inspected` or `reported` applied work toward *Solid* and the prerequisite check only while the concept's effective kind is `performed`.
- **REQ-24.** While a concept's effective kind is `performed`, `bodhi-state` shall still require the level, the streak, the box and a current explain-back from reviews the tutor graded before counting the concept as *Solid*.
- **REQ-25.** While a concept's *Solid* status rests on `reported` applied work, every place the plugin shows that status to the learner shall say the practice is by the learner's account.
- **REQ-26.** When the learner shares a photo of their work, the tutor shall examine it, say what it could and could not judge from the image, and only then record the work as `inspected`.
- **REQ-27.** `bodhi-state` retention statistics and `export-anonymized` shall break their counts down by evidence kind and by applied-work basis.

### Practice reps for performed skills
- **REQ-28.** When the learner reports a practice rep, the tutor shall ask the debrief questions (what you did, what went wrong or surprised you, what you would change and why) before recording anything.
- **REQ-29.** When the tutor records a debriefed practice rep, it shall grade the debrief with the explain-back rubric as the review's result and level, and mark the rep itself as `reported` applied work.
- **REQ-30.** If the learner declines the debrief, then the tutor shall record no review for that rep and shall say the rep will count once it is debriefed.
- **REQ-31.** While a `performed` concept is due for review, `/continue` and `/quiz` shall offer a practice rep with its debrief together with a question on the knowledge behind the skill.
- **REQ-32.** If the learner has not practised a due `performed` concept since its last review, then the tutor shall run the knowledge question alone and shall record no applied work.

### Safety and accuracy where nothing runs
- **REQ-33.** The learning-project rule shall direct the tutor to put safety first in hands-on subjects and to decline step-by-step coaching of hazardous procedures (home chemistry, electrical work, foraging, medical techniques), pointing the learner to qualified instruction while still teaching the concepts.
- **REQ-34.** While a subject touches health or medicine, the tutor shall not give personal medical advice.
- **REQ-35.** When `/learn` scaffolds a project whose kind is not `code`, the plugin shall save verified sources to `.bodhi/resources.md` before the first lesson.
- **REQ-36.** While a concept's effective kind is not `code`, `/teach` shall name at least one source from `.bodhi/resources.md` for the lesson's central claim.

### Where it runs
- **REQ-37.** The build shall produce a Claude Cowork `.plugin` package from the same source tree as the Claude Code plugin.
- **REQ-38.** The plugin shall keep tracked state in Claude Cowork: `bodhi-state` writes, the learning-project rule at session start, and the revision-sheet check at the end. [untested: no headless Cowork runner; verified by the manual probe checklist]
- **REQ-39.** Where the host cannot keep project files between chats, the tutor shall say that tracked study needs a desktop surface and shall offer teaching that keeps no schedule. [untested: no headless claude.ai runner; verified by a manual run]
- **REQ-40.** The OpenAI package built from this tree shall carry the evidence kinds, the applied-work basis and the safety rule.

### Measurement and positioning
- **REQ-41.** `dev/outcomes.py` shall report delayed recall per evidence kind and shall count *Solid* concepts resting on `reported` practice separately.
- **REQ-42.** The README, `plugin.json`, `marketplace.json` and the Codex manifest shall describe BodhiKit as a tutor for any subject that keeps code first-class, and shall say what it cannot verify. [untested: prose, verified by reading]
- **REQ-43.** The `teaching-personality` KB shall describe the learner doing the work in any subject, keeping "the learner writes the code" for code. [untested: prose, verified by reading]

## Out of scope
- Any change to how a `code` concept is taught, graded or evidenced, including requiring a file path for code's applied work. Code keeps 1.24.1 behaviour (REQ-1).
- Full phone and claude.ai support with saved state. It gets its own spec after a research spike on keeping state between chats; until then REQ-39 is the behaviour.
- Analysing audio or voice (pronunciation, an instrument's sound). Photos and written transcripts are in.
- The tutor certifying a physical skill, or claiming to have seen what it did not.
- Personal medical or clinical advice; step-by-step coaching of dangerous procedures.
- Classroom, teacher or multi-learner features.
- A psychomotor taxonomy beside Bloom's.
- A new runtime or app. Gemini and Antigravity stay deferred.

## Release steps (not requirements)
- Rewrite the feature-freeze section of `CLAUDE.md` before the first change lands (intake conflict 1).
- Run the Cowork probe by hand and record the result.
- Per release: `dev/check.sh`, the full LLM eval suite with code groups unchanged, and the new groups for `problems`, `writing` and `performed` on both sides of each grading boundary.
- Write `.shipkit/product.md` with the four goals from the intake.
- Re-upload the ChatGPT listing once the OpenAI portal accepts skills-only submissions.
