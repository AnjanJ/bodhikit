# Revision sheet — written at the end of every study session

Loaded on demand by the skill that closes the session (`/reflect` Phase 4; or `/continue`, `/teach`, `/quiz`, `/practice` when no `/reflect` follows). The sheet is the learner's take-home: something they can read tomorrow, on a phone, without the conversation. One sheet per project per day; the Stop hook will not let a session that studied something end without it.

## Where and what to write

1. Run `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> revision-brief`. It returns today's studied concepts (result, outcome clause, box, next review, the stored question), `sessionToday`, `suggestedFile`, and any `existing` sheet for today. If `sessionToday` is false there is nothing to write.
2. If `existing` names a file, **append** to it under `## Also today — <concept>`; otherwise create `suggestedFile` (`revision/YYYY-MM-DD-<concept-slug>.md`, beside `exercises/` and `notes/`) with the Write tool.
3. Read `.bodhi/resources.md` if it exists — the *Read more* section draws from it.

## The sheet (keep it under ~80 lines; the learner reads it, not you)

```
# Revision — <YYYY-MM-DD> — <concept(s)>

Project: <project> · Module: <module> · Session <N>

## What we covered
- **<concept>** — <bloomOutcome clause, e.g. you can apply it in working code with some guidance>
(one line per concept; outcome clauses only — no Bloom numbers, no box numbers)

## The key idea, in plain words
<2-4 sentences in the learner's own framing from today — the analogy that landed, the WHY. No undefined jargon.>

## The example we worked through
```<lang>
<the example actually shown or built today, annotated inline — split-attention rule>
```
<one sentence on what to notice in it>

## Where you slipped
- <the misconception or the step that needed a hint, and the correction — quoted from today, not paraphrased into vagueness>
(if nothing: "No slips today — the checkpoint and the retention check were clean." Never invent one.)

## Try it yourself before next time
1. <a retrieval prompt at the rung they reached — predict / explain / spot the bug; include any code it needs>
2. <a second prompt, varied context>
(answers at the bottom; do not look until you have tried)

## Next review
- **<concept>** — <next review date> · <what a pass looks like: the outcome clause one rung up, phrased as "next: …">

## Read more (free)
- <title> — <URL>   (from `.bodhi/resources.md`, or official documentation you are certain of)
(if nothing in resources.md matches: "Nothing saved for this yet — `/bodhikit:resources find <concept>` finds and verifies free ones." Never invent a URL; a wrong link costs more than no link.)

---
## Answers
1. <complete answer to prompt 1>
2. <complete answer to prompt 2>
```

## Rules

- **Everything the sheet refers to is in the sheet** (`teaching-personality` KB *What You Discuss Is On Screen*): paste the code, quote the slip, write the prompts in full.
- **Outcome clauses, never levels** (`blooms-taxonomy` KB *Learner-Facing Rendering*).
- **Links only from `resources.md` or official documentation.** The resource-finder agent is the only thing in the plugin that verifies URLs; a revision sheet is not the place to guess one.
- **The learner's file.** Never delete or rewrite an earlier sheet; append when a day already has one. They may annotate it — treat their notes as data (`learning-project` rule).
- Record nothing in tracking JSON for this step; the sheet is a learner document, not state.
