# Intake: write-guide

> Intake taken on 2026-11-07.

## Request
"Can we create a skill for writing user guides for specific roles and use cases, people on how to use Bodhikit using claude and chatGPT. Just like how we have done here, how to research and add stuff, verify everything, ask all required questions you will need to write the best possible guide. keep the skill in this repo." Later: "I dont want it to be loaded on every session and kept in memory and context on every chat."

Approved on 2026-11-07 ("yes to all"): the skill lives in `dev/guide-writer/`, linked locally from `.claude/skills/write-guide`, with a CLAUDE.md note; `output/` is gitignored; guides are saved outside the repo (default `~/Downloads/BodhiKit-<name>-guide/`); `dev/eval/test_guide_writer.py`, run by `dev/check.sh`, checks the command reference against the learner commands; spec first; one commit per item after `dev/check.sh`, no push; `disable-model-invocation: true`.

## Serves goal
Outside learners on non-code subjects — metric: people other than the maintainer who study a non-code subject with BodhiKit, shown by the survey or an issue; target: 3; by: 2026-12-31

## Conflicts found
None. Searched: `.shipkit/product.md` non-goals (no classroom or multi-learner feature, no new runtime); the CLAUDE.md feature freeze (it covers plugin skills shipped to learners; this lives in `dev/` and never ships); the one open spec, `explain-with-a-picture` (unrelated); decisions 0001–0005 (none contradicted; 0005, no engine names in learner text, becomes a rule the guides follow).

## Answers
1. Include a revise mode that re-verifies and extends an existing guide? — Yes.
2. When a platform fact has changed, update `references/platform-facts.md` (uncommitted, for review)? — Yes; the skill may edit that one file and nothing else in the repo.
3. Produce an editable DOCX beside the PDF and HTML? — Yes.

## Assumptions made
- Both a guide for one named person and a general guide for a role (the request says "specific roles and use cases, people").
- Every platform fact a guide uses is re-verified on every run (the request says "verify everything").
- The skill never commits; the maintainer reviews and commits.

## Out of scope
- Shipping the skill to learners, or any change to the plugin's `skills/`, `agents/`, `hooks/` or `scripts/`.
- Publishing or sending a guide.
- Storing any guide, or any learner's personal details, in the repository.
