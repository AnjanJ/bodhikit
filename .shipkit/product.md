# Product: BodhiKit

> Product reviewed on 2026-10-22. *Now* updated 2026-11-05.

## One line
A research-informed tutor for any subject, with code first-class, that teaches by asking and keeps each learner's spaced-review record in files they own.

## Users
- Self-directed learners studying a subject on their own (code, a science, the humanities, a hands-on skill) in Claude Code, Codex, ChatGPT, or a claude.ai chat with Claude Desktop connected.
- Today: one real learner, the maintainer, with more than one subject, plus the outside learners who filed the 1.24.0 requests.

## Goals this quarter
- Outside learners on non-code subjects — metric: people other than the maintainer who study a non-code subject with BodhiKit, shown by the survey or an issue; target: 3; by: 2026-12-31
- Retention holds outside code — metric: delayed-review recall on non-code subjects minus code subjects in `docs/outcomes.md`; target: within 10 points; by: 2026-12-31
- The maintainer's own non-code learning — metric: concepts at *Solid* in one non-code project; target: 5; by: 2026-12-31

## Non-goals
- No change to how a code concept is taught, graded or evidenced (code keeps 1.24.1 behaviour).
- No certifying a physical skill, and no claiming to have seen what the tutor did not see.
- No personal medical or clinical advice, and no step-by-step coaching of dangerous procedures.
- No analysing audio or voice (pronunciation, an instrument's sound).
- No classroom, teacher or multi-learner features.
- No new runtime or app; Gemini and Antigravity stay deferred.

## Metrics that matter
- Delayed-review recall, overall and per evidence kind (`docs/outcomes.md`).
- *Solid* resting on the learner's own account, against *Solid* overall; decision 0001 is reversed if it fails delayed reviews at least 20 points more often.
- Live eval sweep: code groups at their recorded levels, and every grading boundary held on both sides.

## Constraints
- Coding stays as good as it is (the intake's fourth goal): `t_golden_code_path` and the code eval groups at their recorded levels must hold on every release.
- One maintainer. The feature freeze (CLAUDE.md) holds outside decision 0001, which is revisited if no outside learner has used a non-code subject by 2027-01-31.
- `scripts/bodhi-state` is stdlib-only Python 3; every SKILL.md stays under the 18 KB budget.
- Tracked study needs a computer; saved state with no computer connected is out of scope until its own spec.
- The ChatGPT listing depends on the OpenAI portal, which refused skills-only submissions on 2026-10-15.

## Now / Next / Later
- **Now:** finish 1.25.x. Shipped: 1.25.0 (2026-10-23) and 1.25.1 (2026-10-24), and 1.25.1 published on ChatGPT (confirmed 2026-11-05). Done on master, untagged: the `crossedBloom3` → `newlyLearned` rename (decision 0002) and the module kind on the syllabus view. Also done: write commands say the schedule in words, not the box (decision 0003; `kb-load` passes 3/3 with no box number). Also done: decision 0002's reversal condition was met (the tutor told the learner about the profile bump in 4 of 6 runs), so `record-review` now counts the learned concept itself (decision 0004). Left: its live runs (`kb-load` ×3, `teach-vocabulary` ×1); tagging the next release; and the live evals still pending on the release tree (`dev/eval/README.md`).
- **Next:** reach outside learners on non-code subjects, and the maintainer's own non-code project toward 5 *Solid*.
- **Later:** saved state on a phone or claude.ai with no computer connected, after a research spike on keeping state between chats.
