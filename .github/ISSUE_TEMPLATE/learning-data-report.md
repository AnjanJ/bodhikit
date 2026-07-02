---
name: Share your learning data
about: Contribute anonymized outcome data — help turn "research-informed" into "outcome-validated"
title: "Learning data: [topic], [rough duration]"
labels: outcome-data
---

Thank you — this is the single most useful thing a BodhiKit user can send. One command produces everything below. The export contains **no concept names, no questions, no notes, no free text** — only counts and rates. Inspect it before pasting if you like.

## Your export

Run this inside your learning project (the folder containing `.bodhi/`):

```
"$(find ~/.claude/plugins -type f -name bodhi-state -path "*bodhikit*" 2>/dev/null | head -1)" --project . export-anonymized
```

(Or from a repo checkout: `scripts/bodhi-state --project <your-project> export-anonymized`.)

Paste the JSON here:

```json

```

## Context (optional, but it makes the numbers interpretable)

- What were you learning, roughly? (e.g. "Rust", "SQL", "system design")
- How did the review pacing feel — too frequent, about right, too sparse?
- Where did the tutor's judgment feel off (graded too generously/harshly, questions pitched at the wrong level)?
- Anything that made you stop using a skill?
