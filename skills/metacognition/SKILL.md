---
description: "Metacognition: teaching learners HOW to learn, Dunning-Kruger effect, illusions of competence (Oakley)"
user-invocable: false
---

# Metacognition

**Evidence tier: strong.** Confidence-calibration and self-monitoring research (Koriat 1997; Flavell 1979) is well-replicated; metacognitive-strategy instruction shows consistent positive effects.

## Teaching Learners HOW to Learn

- **Prediction**: Before attempting a problem, ask "How hard do you think this will be?"
- **Monitoring**: During work, ask "What is your strategy right now?"
- **Evaluation**: After completing, ask "What was harder than expected? What was easier?"
- **Self-assessment calibration**: "How confident are you in this answer, 1-10?" Then compare to actual result.

## Per-Item Confidence Tagging (Koriat)

The cheapest high-value calibration intervention: before an answer is judged, the learner tags it `sure` / `mostly` / `guessing`. The order is load-bearing — confidence stated **after** the reveal measures hindsight, not monitoring (Koriat, *Monitoring one's own knowledge during study*, 1997). Over time the tags expose the two patterns that matter:

- **Overconfidence** (`sure` + incorrect): the illusion-of-competence signature. These concepts need retrieval practice, not re-reading.
- **Underconfidence** (`guessing` + correct): knowledge is present but not trusted; name it to the learner — confidence calibration cuts both ways.

`/quiz` collects the tag with every answer; tags land in `reviewHistory[].confidence` (see `state-schema` KB) and `bodhi-state calibration` aggregates them for `/progress` and `/reflect`. Never scold a miscalibrated tag — the honest tag IS the rep. The `predictionDelta` block in `assessment-history.json` is the same mechanism at journey scale (`/evaluate` Phase 2.5: predict-before-reveal).

## The Dunning-Kruger Effect in Programming

Beginners overestimate their skills because they lack the knowledge to assess what they do not know. This is not arrogance — it is a genuine cognitive limitation. The antidote is calibrated self-assessment through repeated prediction-and-check cycles.

## Illusions of Competence (Oakley)

Watch for these dangerous patterns:
- **Passive rereading**: Moving eyes over text without recall
- **Glancing at solutions**: Looking at a worked solution and thinking "I get it" without reproducing it
- **Recognition vs recall**: "This looks familiar" is NOT the same as "I can produce this from memory"
- **The Einstellung effect**: An existing idea blocks finding a better solution

Antidote: Always test with retrieval. If the learner says "I understand," ask them to prove it by explaining or solving from scratch.
