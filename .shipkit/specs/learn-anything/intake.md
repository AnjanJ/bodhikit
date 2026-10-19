# Intake: learn anything

> Intake taken on 2026-10-19.

## Request
Make BodhiKit a learning tool for every subject — political theory, art, humanities, science,
biotech, genetics, astronomy, cooking, languages and everything else — not only code, on all
platforms but mainly Claude. It must know what is a coding curriculum, session or path and what
is not, and not evaluate everything the way it evaluates code. Where the tutor cannot check the
evidence, it trusts the learner's word. "Lets plan and spec out our work … make it the best
learning tool there is on the market right now."

## Serves goal
No `.shipkit/product.md` exists (searched `.shipkit/`: the directory did not exist). The user
chose these goals for this work, in their words where given:
1. Outside learners: at least 3 people other than the maintainer study a non-code subject with
   BodhiKit this quarter, shown by the survey or an issue.
2. Retention holds outside code: delayed-review recall on non-code subjects within 10 points of
   code subjects in `docs/outcomes.md`.
3. The maintainer's own non-code learning: a non-code project with at least 5 concepts at Solid.
4. "We need to keep the coding as good as is and make sure the non code is brought up to par
   with coding learning experience."

## Conflicts found
- **Feature freeze, `CLAUDE.md:45–47`.** "No new skills, KBs, taxonomies, session types, or
  schema fields unless (a) a second real user files an issue asking for it, or (b) the
  maintainer personally hits the gap during a real learning session." This work adds tracking
  fields and eval groups. Exception (b) covers written subjects (the political-theory course,
  2026-10-16), not performed ones. **Decided:** the user chose in conversation on 2026-10-19 to
  make BodhiKit "a learning tool for everything". The freeze section must be rewritten first.
- **Applied-evidence rule, `skills/blooms-taxonomy/SKILL.md:72–74`.** Applied work is "a file
  the tutor read, not a chat reply", and "never applied evidence, on any topic: an explanation,
  a quiz answer, or work the tutor wrote or dictated." Trusting the learner's word is a chat
  reply. **Decided:** the user chose "where the tutor cant check evidence let it trust the
  users/learners word". The rule changes to admit a separate, labelled self-report kind for
  performed skills only; the "never" list stands for every subject the tutor can check.
- **Positioning, `README.md:5,7,15` and `.claude-plugin/plugin.json:4`.** "Research-informed
  interactive coding tutor", "the learner writes code". Not a decision record; the
  repositioning rewrites it.

## Answers
1. *Which measurable goal does this serve?* — All three offered (outside learners, retention
   holds outside code, the maintainer's own non-code learning), plus: "We need to keep the
   coding as good as is and make sure the non code is brought up to par with coding learning
   expereince."
2. *Are phones and claude.ai on the web in scope?* — "1 and 3": desktop surfaces only (Claude
   Code, Cowork, Codex) **and** full phone support with state kept between chats.
3. *For a performed skill, what comes back on the spaced schedule?* — Practice sessions +
   knowledge: a due review means doing it again with a short debrief, alongside quizzes on the
   why; reviews of practice are labelled learner-reported.

## Assumptions made
- **Phones, read as phased.** "1 and 3" is read as: desktop surfaces ship first, and full
  phone support is a later phase that starts with a research spike on keeping state between
  chats. Object if both were meant for the first release.
- **The axis is the kind of evidence, not the subject.** Four kinds — code, problems with
  answers, writing, performed — cover every subject; a subject can mix them per module (a
  bioinformatics course mixes genetics modules with Python modules).
- **Self-report fills only what cannot be seen.** For performed skills it can fill the fifth
  Solid condition (applied work), always labelled as the learner's word. The other four
  conditions — delayed recall, the streak, the level, an explain-back after the last miss —
  are still observed by the tutor in every subject. Precedent: `/forget` entries are already
  self-reports excluded from retention statistics (1.21.0; `scripts/bodhi-state:1499`).
- **Code does not regress.** Every existing eval scenario for code topics keeps passing at its
  recorded levels (the release checklist's grading sweep, executor-discipline and fidelity
  groups in `dev/eval/README.md`).
- **Cowork is the primary non-coder surface on Claude**, pending a probe the maintainer runs
  by hand (it cannot be driven from Claude Code). Its plugin format is shared with Claude
  Code's, per the locally installed `cowork-plugin-management` docs.
- **Codex and ChatGPT** receive the changes through `platforms/openai/build_plugin.py`, as
  every release does. The ChatGPT listing upload is blocked on the OpenAI portal (not
  accepting skills-only submissions), so ChatGPT users wait on that.
- **Name and persona stay.** BodhiKit, and the `teaching-personality` KB voice.
- **Ships in stages**, several releases, each passing `dev/check.sh` and the LLM evals.
- **Safety** lives in `rules/learning-project.md`, which every session inside a learning
  project receives.

## Out of scope
- Analysing audio or voice (pronunciation, an instrument's sound). Photos and written
  transcripts are in; listening is not.
- The tutor certifying a physical skill. It never claims to have seen what it did not.
- Medical or clinical advice, and step-by-step coaching of dangerous procedures (home
  chemistry, electrical work, foraging, medical techniques).
- Classroom, teacher or multi-learner features.
- A psychomotor taxonomy alongside Bloom's; performed skills use Bloom plus the evidence kind.
- A new runtime or app. Gemini and Antigravity stay deferred.
