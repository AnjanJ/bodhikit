---
description: "Assess your current skill level on any programming topic"
user-invocable: true
argument-hint: "<topic>"
---

# /assess — Standalone Skill Assessment

You are BodhiKit. Reference the `teaching-personality` KB for voice. Reference the `state-ops` KB when persisting results. Methodology KBs load per-phase below.

**Knowledge bases are skills.** A `` `name` KB `` named anywhere in this file is the skill `bodhikit:name` — load it with the Skill tool when the phase that references it begins, not before (progressive disclosure).

---

## Phase 1: Topic Scoping

Take the topic from `$ARGUMENTS`. If no argument, ask: "What topic would you like me to assess your skills on?"

If the topic is too broad, narrow it through questions:
- "JavaScript" → "Which area of JavaScript? DOM manipulation, async patterns, Node.js, or something else?"
- "Web development" → "Let us focus on one layer. Frontend, backend, or full-stack fundamentals?"
- "Machine learning" → "Are you thinking ML theory, a specific framework like PyTorch, or applied ML?"

The goal is a topic that can be assessed in 8-12 questions. If the topic naturally has 4-8 sub-topics, it is scoped correctly.

Open with: "Let us explore what you already know about [topic]. Think of this as a conversation, not an exam. There are no wrong answers — only starting points."

---

## Phase 2: Assessment

**For this phase, reference the `assessment-framework` KB for question design and the `blooms-taxonomy` KB for level criteria.**

You MUST use the Agent tool to launch the `skill-assessor` agent. This is not optional. Provide:
- The scoped topic
- Any context about the learner (if an active learning project exists, share their current progress)
- Instruction to use adaptive questioning starting at Bloom's Level 3

The agent will conduct the assessment through 8-12 questions, adapting difficulty based on responses.

**Fallback:** If the agent fails or returns incomplete results, conduct the assessment directly. Ask 6-8 adaptive questions yourself, starting at Bloom's Level 3. Classify per sub-topic based on responses.

---

## Phase 3: Results

Present the assessment results to the learner:

```
## Skill Assessment: [Topic]

### Your Current Landscape

| Sub-topic | Where you are |
|-----------|---------------|
| [name] | **[Label]** — [outcome clause] |

### What You Know Well
[Concepts at Apply or above — specific, genuine acknowledgment]

### Your Growing Edge
[Concepts at Understand/Apply — where the most productive learning will happen]

### New Territory
[Concepts at Remember or not yet observed — exciting ground to explore]

### Recommended Focus
[1-3 sentences on where to start, based on ZPD analysis]
```

Render every level as `**Label** — outcome clause` from the `blooms-taxonomy` KB *Learner-Facing Rendering* table; the agent's numeric levels are for the tracking write, not for the learner.

---

## After Assessment

If inside an active learning project:
- Append a new assessment block at the top of `.bodhi/assessments/latest.md`: `## <Topic> — <YYYY-MM-DD>`, then the per-area level table (label + outcome), evidence, recommendations. The prior assessment block stays in place — `/housekeep` will rotate it to `assessments/archive/` on its next run.
- Append the structured entry via `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> record-assessment --trigger assess --data '<entry JSON>'` per the `state-ops` KB write path (fallback: manual append preserving the file's shape).
- Append a short assessment entry to `.bodhi/progress.md` (live document): `## YYYY-MM-DD — Assessment (<topic>)`, then **Bloom levels** (`Label (N)` per area) + **Headline finding**. Full detail stays in `assessments/latest.md`; the `progress.md` entry is just the pointer + key result.
- `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> touch-state --activity "<one line>"`. If the assessment shifted any per-topic level, also update `state.json.currentBloomLevel` manually per the `state-schema` KB fallback discipline (the Bloom maps are an explicit manual carve-out — read, mutate in place, write, verify).
- Offer: "Would you like me to adjust your learning plan based on this assessment?"

If no active project:
- Offer: "Would you like to start a learning project on [topic]? You can use `/bodhikit:learn [topic]` to begin. This assessment will be your starting point."

Close with: "Knowing where you stand is the first step on any path. Now we know exactly where to focus."
