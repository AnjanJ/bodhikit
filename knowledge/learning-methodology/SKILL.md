---
description: "Core learning science: spaced repetition, Bloom's taxonomy, ZPD, Feynman technique, deliberate practice, growth mindset, desirable difficulties"
user-invocable: false
---

# Learning Methodology — The Science Behind BodhiKit

This knowledge base contains the research-backed learning science that drives all BodhiKit teaching decisions. Every skill and agent references these principles.

---

## 1. Spaced Repetition (Ebbinghaus, Leitner)

### The Forgetting Curve

Without review, memory decays exponentially:
- 20 minutes: ~42% forgotten
- 1 hour: ~56% forgotten
- 24 hours: ~67% forgotten
- 1 week: ~75% forgotten
- 1 month: ~79% forgotten

Each successful recall resets and flattens the curve. The first review is the most critical.

### Leitner Box System (BodhiKit Implementation)

| Box | Review Interval | Meaning |
|-----|----------------|---------|
| 1   | 1 day          | New or forgotten concept |
| 2   | 3 days         | Recalled once successfully |
| 3   | 7 days         | Building retention |
| 4   | 14 days        | Strong retention |
| 5   | 30 days        | Long-term mastery |

**Rules:**
- New concepts start in Box 1
- Correct recall: move up one box
- Incorrect recall: move back to Box 1 (regardless of current box)
- `nextReview` = `lastReviewed` + box interval

### Application to Programming

Spaced repetition for coding is NOT just flashcards. It includes:
- **Spaced problem-solving**: Solve a coding problem, then solve it again from scratch (without referencing prior solution) at expanding intervals
- **Pattern-based spacing**: After learning a pattern (e.g., sliding window), solve new problems using that pattern at intervals
- **Code review as retrieval**: Revisit code you wrote days/weeks ago and explain what it does and why
- **Concept re-explanation**: Periodically explain previously learned concepts from memory (Feynman + spacing)
- **Predict before running**: Before executing code, predict the output — this forces retrieval

---

## 2. Bloom's Taxonomy for Programming

### The 6 Levels

| Level | Name | Programming Indicators | Example Assessment |
|-------|------|----------------------|-------------------|
| 1 | **Remember** | Recall syntax, name methods, recite definitions | "What keyword creates a variable in JavaScript?" |
| 2 | **Understand** | Explain code behavior, predict output, paraphrase concepts | "Explain what this function does in your own words" |
| 3 | **Apply** | Write code from requirements, use patterns in guided context | "Write a function that filters even numbers from an array" |
| 4 | **Analyze** | Debug code, compare approaches, identify performance issues | "This code has a bug when the array is empty. Find it." |
| 5 | **Evaluate** | Critique design decisions, justify choices, review code | "Which of these two implementations is better and why?" |
| 6 | **Create** | Design systems from scratch, build novel solutions, architect | "Design an API for a task management system" |

### Key Principles

- Track Bloom's level PER CONCEPT, not globally. A learner can be Level 5 on arrays and Level 2 on recursion.
- Progression is not always linear. A learner may jump from Level 2 to Level 4 on a concept they have real-world experience with.
- Exercises should target one level above the learner's current level (ZPD alignment).
- If a learner fails at Level N, drop back to Level N-1 to reinforce, do not push forward.

### Mastery Criteria

A concept is **mastered** when:
- Bloom's Level 4+ achieved
- 3 consecutive correct quiz answers at Level 4+
- Concept in Leitner Box 4 or 5
- Can explain to another person without jargon (Feynman check passed)

A concept is **familiar** when:
- Bloom's Level 3 achieved
- At least 1 correct quiz answer at Level 3
- Concept in Leitner Box 2 or 3

A concept is **introduced** when:
- Bloom's Level 1-2
- Concept in Leitner Box 1

---

## 3. Zone of Proximal Development (Vygotsky)

### Three Zones

1. **Can do alone** (current level): Tasks requiring no help. Too easy = no learning.
2. **Can do with guidance** (ZPD): Tasks achievable with support. THIS IS WHERE LEARNING HAPPENS.
3. **Cannot do even with help** (beyond reach): Tasks causing cognitive overload. Too hard = frustration.

### Detecting the Learner's Zone

**In the ZPD (productive struggle):**
- Can articulate what they are trying to do but unsure how
- Make partial progress and ask specific questions
- With a small hint, make forward progress
- Errors show partial understanding (correct approach, wrong details)

**Below the ZPD (too easy):**
- Complete tasks quickly without engagement
- Show boredom or impatience
- Do not learn anything new from the exercise

**Beyond the ZPD (overwhelmed):**
- Cannot articulate what they are confused about
- Hints do not help — they cannot act on guidance
- Show frustration, disengagement, or random guessing
- Cognitive overload: too many new concepts at once

### Scaffolding Strategy

Use the **Gradual Release of Responsibility** model:

1. **I Do** (Modeling): Tutor solves a problem while thinking aloud
2. **We Do** (Guided Practice): Learner and tutor work through a problem together
3. **You Do Together** (Collaborative): Learner attempts with tutor available for questions
4. **You Do Alone** (Independent): Learner solves independently, tutor reviews afterward

**Scaffolding must fade as competence grows.** The goal is independence.

---

## 4. Feynman Technique

### The 4 Steps

1. **Choose a concept** and study it
2. **Explain it simply** — as if to a 12-year-old, no jargon, use analogies
3. **Identify gaps** — where did you struggle, use vague language, or skip steps?
4. **Simplify and refine** — go back to source for gaps, create better analogies, repeat until clean

### When to Use

- Deep conceptual understanding needed (design patterns, architectural principles)
- Suspected illusions of competence ("I think I understand but...")
- Abstract concepts that benefit from analogies
- Central, high-leverage concepts where deep understanding pays dividends

### When NOT to Use

- Procedural/motor skills (typing speed, keyboard shortcuts) — use deliberate practice
- Syntax memorization — use spaced repetition
- Simple, straightforward concepts — just practice
- Time-constrained situations — too time-intensive for universal application

### Implementation in BodhiKit

After teaching a concept, always ask: "Now, explain this back to me in your own words. Pretend I have never heard of it."

If the learner uses jargon, ask them to define each technical term simply. If they skip steps, ask about the missing steps. If they use vague language ("it kind of does..."), probe for precision.

---

## 5. Deliberate Practice (Ericsson)

### What Makes Practice "Deliberate"

1. **Targeted**: Each session has a specific skill improvement goal
2. **At the edge of ability**: Slightly beyond comfort zone, not too easy, not too hard
3. **Immediate feedback**: Know right away if the approach worked
4. **High repetition with variation**: Same skill, different contexts, adjusting each time
5. **Focused attention**: Cannot be done on autopilot — mentally taxing
6. **Expert-guided**: Practice designed by someone who can diagnose weaknesses

### NOT Deliberate Practice

- Following tutorials passively
- Building the same type of project repeatedly
- Coding for hours without reviewing or reflecting
- Solving problems well within comfort zone
- Grinding problems without understanding underlying patterns

### Application

Design exercises that:
- Isolate ONE skill at a time
- Require focused effort (not busy work)
- Have clear success criteria
- Provide immediate feedback (tests, output comparison)
- Include variations that prevent rote memorization

---

## 6. Growth Mindset (Dweck)

### Key Language Patterns

| Fixed Mindset (Avoid) | Growth Mindset (Use) |
|----------------------|---------------------|
| "You are a natural at this" | "You worked hard on this and it shows" |
| "This is not your thing" | "You have not mastered this yet" |
| "Some people just cannot code" | "Everyone learns at different paces" |
| "You are so smart" | "Your strategy here was effective" |
| "That was easy, right?" | "That took practice. Well done." |

### Critical Nuance

Growth mindset is NOT just praising effort. Dweck warns against "false growth mindset" that praises effort without providing specific guidance on effective strategies. Effort alone without productive strategy is not enough.

**Do**: "Your approach of breaking the problem into smaller functions was effective. That strategy will serve you well."
**Do Not**: "Great effort!" (empty, uninformative)

---

## 7. Desirable Difficulties (Bjork)

### The 5 Key Difficulties

1. **Spacing**: Distribute practice over time (not cramming)
2. **Interleaving**: Mix different problem types in a session (not blocking)
3. **Retrieval practice**: Recall from memory (not re-reading)
4. **Generation**: Produce answers before being shown them
5. **Variation**: Practice in varied contexts (not identical conditions)

### The Paradox

These all SLOW DOWN apparent progress but produce significantly STRONGER long-term retention and transfer. Learners often rate these methods as less effective precisely because the struggle feels bad — even when outcomes are superior.

### Application

- Never present 10 problems of the same type in a row (interleave)
- After teaching a concept, ask the learner to solve a problem BEFORE showing examples (generation)
- Mix old and new concepts in every session (spacing + interleaving)
- Vary the format: sometimes explanation, sometimes code, sometimes debugging (variation)

---

## 8. Metacognition

### Teaching Learners HOW to Learn

- **Prediction**: Before attempting a problem, ask "How hard do you think this will be?"
- **Monitoring**: During work, ask "What is your strategy right now?"
- **Evaluation**: After completing, ask "What was harder than expected? What was easier?"
- **Self-assessment calibration**: "How confident are you in this answer, 1-10?" Then compare to actual result.

### The Dunning-Kruger Effect in Programming

Beginners overestimate their skills because they lack the knowledge to assess what they do not know. This is not arrogance — it is a genuine cognitive limitation. The antidote is calibrated self-assessment through repeated prediction-and-check cycles.

### Illusions of Competence (Oakley)

Watch for these dangerous patterns:
- **Passive rereading**: Moving eyes over text without recall
- **Glancing at solutions**: Looking at a worked solution and thinking "I get it" without reproducing it
- **Recognition vs recall**: "This looks familiar" is NOT the same as "I can produce this from memory"
- **The Einstellung effect**: An existing idea blocks finding a better solution

Antidote: Always test with retrieval. If the learner says "I understand," ask them to prove it by explaining or solving from scratch.

---

## 9. Constructivism and Project-Based Learning

### Spiral Curriculum (Bruner)

Topics are revisited at increasing levels of complexity:
- **Pass 1**: Basic concept in isolation (variables, loops)
- **Pass 2**: Concept in combination (functions using loops and variables)
- **Pass 3**: Concept in context (building a CLI tool that uses all of the above)
- **Pass 4**: Concept at depth (refactoring with patterns, testing, error handling)

Each pass revisits earlier concepts in a more sophisticated context.

### Project Progression by Level

1. **Follow-along**: Learner types provided code with explanations (beginner)
2. **Fill-in-the-blank**: Tutor provides structure, learner implements functions (early intermediate)
3. **Spec-driven**: Tutor provides requirements, learner designs and implements (intermediate)
4. **Open-ended with check-ins**: Learner chooses what to build, tutor reviews at milestones (advanced)
5. **Fully independent**: Learner defines, designs, builds, evaluates on their own (expert)

---

## 10. Anti-Patterns in AI-Assisted Learning

### Risks to Guard Against

- **Cognitive offloading**: Learner outsources thinking to AI instead of building mental models
- **Shallow completion**: Learner prioritizes finishing tasks over understanding
- **Skill atrophy**: Constant AI assistance prevents developing independent problem-solving
- **Diminished self-confidence**: Learner begins to doubt their ability to work without AI
- **The substitution effect**: Learner replaces learning effort with AI output

### Structural Safeguards

- Learner ALWAYS writes the code, never the plugin
- Socratic method: questions over answers
- Graduated hints, never direct solutions
- Track dependency patterns — if a learner always asks for help on the same type of problem, redirect to independent practice
- Build metacognitive awareness: the learner should know HOW they learn, not just WHAT they learn
- The goal is to become unnecessary
