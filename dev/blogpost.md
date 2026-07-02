---
title: "BodhiKit: A Deeply Personalized, Research-Backed AI Coding Tutor That Teaches You Instead of Writing Code For You"
published: true
tags: programming, learning, ai, opensource
canonical_url: https://codeberg.org/AnjanJ/bodhikit
cover_image:
---

## The Problem With AI and Learning

AI tools are incredible at writing code. But writing code for you and teaching you to write code are two fundamentally different things.

When an AI writes your code, you get a working solution. When an AI teaches you to write code, you get a working brain.

Most AI coding tools optimize for the first. BodhiKit optimizes for the second.

## What is BodhiKit?

BodhiKit is a free, open source plugin for [Claude Code](https://claude.ai/code) that turns Claude into a deeply personalized, interactive coding tutor. The name comes from Pali, the language of early Buddhist texts. Bodhi means "awakening." Because learning, at its best, is exactly that.

It does not write code for you. It asks questions. It gives hints. It creates exercises. It tests your understanding. And it remembers where you left off, so every session builds on the last.

17 skills. 3 AI agents. 15 knowledge bases. Works with any programming topic: React, Rust, Python, Zig, system design, web development, databases, anything.

## The Philosophy

BodhiKit speaks with the voice of a wise, patient teacher. Think Master Oogway from Kung Fu Panda, Yoda, Gautama Buddha, and Dr. B.R. Ambedkar. Patient, honest, respectful, never condescending.

Three core principles:

1. **The learner writes code. BodhiKit asks questions.** If you ask it to write code for you, it will gently redirect: "The learning happens when your hands are on the keyboard."

2. **Struggle is sacred.** When you are stuck, BodhiKit gives the smallest hint that keeps you thinking. Not the answer. Productive struggle is where real learning happens.

3. **The goal is to become unnecessary.** A good teacher does not create dependency. A good teacher creates independence.

## The Science Behind It

BodhiKit is not built on vibes. It is built on decades of research in learning science:

**Spaced Repetition** (Ebbinghaus, Leitner): Your brain forgets 67% of new information within 24 hours. BodhiKit tracks every concept you learn and resurfaces it at optimal intervals. Get it right, and the interval grows. Get it wrong, and it comes back tomorrow. This is not flashcards. It is spaced problem-solving, code review, and concept re-explanation.

**Bloom's Taxonomy** (Bloom, Anderson): Not all knowledge is equal. "I can recall the syntax" is Level 1. "I can design a system from scratch" is Level 6. BodhiKit tracks your level per concept, not globally. You might be Level 5 on arrays and Level 2 on recursion. That granularity matters.

**Zone of Proximal Development** (Vygotsky): If a task is too easy, you learn nothing. If it is too hard, you shut down. The sweet spot is just beyond what you can do alone. BodhiKit calibrates every exercise to sit in that zone.

**Feynman Technique**: After explaining a concept, BodhiKit asks you to explain it back in your own words. No jargon. If you cannot explain it simply, you do not understand it yet. This is the single most powerful check for real understanding.

**Deliberate Practice** (Ericsson): Coding for 10 hours is not practice. Coding for 1 hour with targeted focus on your specific weakness, with immediate feedback, is practice. BodhiKit designs exercises that isolate one skill at a time and provide clear feedback.

**Growth Mindset** (Dweck): "You have not mastered this yet." The word "yet" changes everything. BodhiKit never says "that is wrong." It says "let us look at this differently."

**Desirable Difficulties** (Bjork): BodhiKit mixes problem types, varies contexts, and uses retrieval practice instead of re-reading. These feel harder in the moment but produce dramatically stronger long-term retention.

**Metacognition** (Flavell): BodhiKit does not just teach you WHAT to learn. It teaches you HOW you learn. End-of-session reflections build your awareness of your own learning process, which research shows improves retention by 20-30%.

**Mentoring Theory** (Kram, Whitmore): BodhiKit uses the GROW model (Goal, Reality, Options, Will) for career guidance and Kram's mentoring theory to balance coaching with encouragement. It is honest about what an AI cannot do (sponsorship, networking) and transparent about its limitations.

**Pair Programming** (Beck, Williams & Kessler, Falco): Three modes of collaborative coding. Strong-style pairing forces explicit communication of thinking. Ping-pong pairing with TDD teaches both specification and implementation. Research shows pairing improves learning outcomes, satisfaction, and retention.

**Scientific Debugging** (Zeller, O'Dell): Developers spend 35-50% of their time debugging, yet it is rarely taught. BodhiKit teaches Zeller's TRAFFIC method (reproduce, hypothesize, probe, isolate, fix) and frames bugs as puzzles, not failures. It never fixes bugs for you.

**Constructivism** (Piaget, Bruner, Papert): Learning by building. BodhiKit uses Bruner's spiral curriculum to revisit concepts at increasing depth, progressing from guided follow-along to fully independent projects.

## How to Install

You need [Claude Code](https://claude.ai/code) (Anthropic's CLI tool).

```
/plugin marketplace add https://codeberg.org/AnjanJ/bodhikit.git
/plugin install bodhikit@bodhikit
```

Restart Claude Code after installing. That is it.

Or test locally without installing:

```
claude --plugin-dir ~/code/bodhikit
```

## One Command, Complete Learning Session

This is what makes BodhiKit different from just "chatting with an AI about code." Run `/bodhikit:continue` and the entire session is orchestrated for you:

```
/continue
  ├── /status       → quick 3-line check-in (project, streak, concepts due)
  ├── spaced review → quiz on concepts due for review today
  ├── /teach        → guided teaching of the next concept
  │     ├── explain with analogies and code examples
  │     ├── work through a problem together (guided practice)
  │     ├── independent exercise (you write the code)
  │     └── quick retention check
  └── /reflect      → end-of-session metacognitive reflection
```

One command. No need to remember which skills to invoke. BodhiKit handles the flow, you focus on learning.

## How Teaching Works

When BodhiKit teaches, it follows the **Gradual Release of Responsibility** model:

**I Do (Modeling):** BodhiKit explains the concept. Not with a wall of text, but with analogies from everyday life, concrete code examples, and a clear connection to what you already know. It shows WHY the concept matters, not just what it does.

**We Do (Guided Practice):** You and BodhiKit work through a problem together. It asks guiding questions: "How would you start? What data structure fits here?" You make the decisions. It keeps you on track.

**You Do (Independent Practice):** BodhiKit gives you an exercise calibrated to your level. Beginners get starter files with TODO comments. Advanced learners get a problem statement and nothing else. You solve it yourself.

**Verify:** Quick retention check. 2-3 questions to confirm the concept stuck. New concepts are added to spaced repetition tracking.

The key rule: BodhiKit never lectures for more than 5 minutes without interaction. It is a conversation, not a presentation.

## End-of-Session Reflection

When you say goodbye, BodhiKit asks four questions:

1. **What felt hardest today?** Identifies concepts that need more time.
2. **Was anything easier than expected?** Calibrates your self-assessment.
3. **Confidence rating (1-10)?** Low-confidence concepts get reviewed sooner.
4. **What would you do differently?** Builds strategic thinking about learning itself.

This takes 3-5 minutes and multiplies the value of the entire session. Your confidence rating feeds directly into the spaced repetition system. A concept you rate at 3/10 comes back tomorrow. A concept you rate at 9/10 can wait a week.

## How to Use BodhiKit: Real Scenarios

### Scenario 1: "I want to learn Rust from scratch"

```
/bodhikit:learn rust
```

BodhiKit will:
1. Ask why you want to learn Rust, what your programming background is, and your timeline
2. Assess your current knowledge through adaptive questions (starting at Level 3, adjusting up or down based on your answers)
3. Build a personalized learning plan with phases, modules, and exercises
4. Create a project folder (`learningWithBodhi/rust-basics/`) with tracking files
5. Give you your first exercise immediately. Not "go read the Rust Book." An actual exercise you can do in 5-10 minutes.

The next day, run:

```
/bodhikit:continue
```

It shows your status, reviews due concepts, teaches the next topic, gives you an exercise, and runs a reflection when you are done. All automatic.

### Scenario 2: "I am reading a book and want a teaching assistant"

Say you are working through "The Rust Programming Language" (the Rust Book):

```
/bodhikit:resources add "The Rust Programming Language"
```

BodhiKit analyzes the book's structure and maps chapters to your learning plan. Then it can:
- Quiz you on what you just read
- Give you extra practice exercises on the same concepts
- Explain concepts differently when the book's explanation does not click
- Review your code from the book's exercises

It works as a TA, not a replacement. The book is the primary material. BodhiKit fills the gaps.

### Scenario 3: "I want to check where I stand with React"

```
/bodhikit:assess react
```

No learning project needed. It runs a standalone assessment: 8-12 adaptive questions, classifies your Bloom's level per sub-topic (JSX, components, hooks, state management, routing, etc.), and shows you where you stand.

If you want to go deeper after the assessment:

```
/bodhikit:learn react
```

Your assessment becomes the starting point for the learning plan.

### Scenario 4: "I wrote some code and want feedback"

```
/bodhikit:review ./my-project/src/app.tsx
```

This is not a production code review. It is an educational review. BodhiKit analyzes what your code reveals about your understanding:
- What concepts you demonstrate mastery of
- What misconceptions are visible
- What patterns you are ready to learn next

And instead of telling you what to fix, it asks Socratic questions: "I notice you used a for loop here. What do you know about array methods like map and filter?"

It also works with GitHub, GitLab, and Codeberg URLs:

```
/bodhikit:review https://github.com/username/repo
```

### Scenario 5: "I do not understand closures"

```
/bodhikit:explain closures
```

BodhiKit explains the concept simply, with analogies, no jargon. Then it asks you to explain it back. Then it identifies the gaps in your explanation and helps you fill them. This is the Feynman Technique in action.

### Scenario 6: "Give me something to practice"

```
/bodhikit:practice
```

It creates an exercise calibrated to your current level:
- **Beginners** get starter files with TODO comments and tests to run
- **Intermediate** learners get requirements and test cases, no starter code
- **Advanced** learners get a problem statement and nothing else

After you complete it, BodhiKit reviews your code educationally and suggests what to try next.

### Scenario 7: "How far have I come?"

```
/bodhikit:evaluate
```

This is the big picture. It reads your entire learning history, runs a fresh assessment, and compares where you started to where you are now. Growth map, strengths, gaps, recommendations, and a suggested project to solidify what you have learned.

### Scenario 8: "Quick check — where am I?"

```
/bodhikit:status
```

Three lines. Five seconds:

```
📍 react-fundamentals | State and Hooks | 45% complete
🔥 Streak: 3 days | 2 concepts due for review today
📅 Last session: yesterday
```

### Scenario 9: "My code has a bug and I am stuck"

```
/bodhikit:debug-together ./exercises/05-todo-list/TodoList.jsx
```

BodhiKit does not look at the code first. It starts with you:

> "What did you expect to happen?"
> "The todo should be removed when I click delete."
> "And what actually happened?"
> "Nothing happens. No error either."
> "Good. No error but wrong behavior. What is your theory?"
> "Maybe the filter is not working?"
> "That is a testable theory. Before changing anything, let us verify. Add a console.log before the filter that prints the array and the ID you are trying to remove. What do you expect to see?"

You add the probe. The array prints correctly, but the ID being passed is `undefined`.

> "Interesting. Your theory about the filter was reasonable, but the real cause is upstream. The ID is not reaching the function. What could cause that?"

You trace it back to the onClick handler and discover you forgot to pass the todo's ID. You fix it yourself. BodhiKit closes:

> "You systematically tested a hypothesis, found it was not the cause, followed the data upstream, and found the real issue. That is exactly how experienced developers debug."

This also auto-invokes during `/practice` or `/teach` when your code has bugs.

### Scenario 10: "I want to build something together"

```
/bodhikit:pair strong-style
```

BodhiKit explains the rule: "For an idea to go from my head into the computer, it must go through your hands. I will describe what to build. You type it."

> "Create a function called `calculateTotal`. It takes an array of items, each with a `price` and `quantity` property."

You start typing. You write `function calculateTotal(items)`.

> "Good. Now, inside the function, what do you think is the first step?"
> "Loop through the items?"
> "Yes. Which loop would you use here, and why?"
> "A for loop?"
> "That would work. Have you seen `reduce`? It is designed exactly for this kind of accumulation. Try it if you would like, or stick with the for loop. Your call."

You try reduce. You get it slightly wrong. BodhiKit guides without correcting:

> "Walk me through what your reduce callback does with each item."

You talk through it, spot the issue yourself, fix it.

> "Good. Now walk me through what you just wrote, line by line."

After 15 minutes, BodhiKit offers: "Now let us switch. You tell me what to build next. You navigate, I follow."

Mode auto-selects based on your Bloom's level, or you can choose: `strong-style` for beginners, `ping-pong` for intermediate (BodhiKit writes a test, you make it pass), `navigate` for advanced.

Also auto-invoked by `/teach` during Phase 3 (guided practice).

### Scenario 11: "I finished React. What should I learn next?"

```
/bodhikit:mentor
```

BodhiKit reads your learner profile and all your learning projects:

> "Let us step back and look at the bigger picture. You started learning React two months ago. You are now at Bloom's Level 4 on components, props, state, and hooks. Level 3 on effects and routing. That is real growth."
>
> "What draws you to programming? Is it a career change, a specific project, or something else?"
> "I want to become a full-stack developer."
> "Good. For a full-stack developer, here is what I see:
>
> **Strong foundation:** React, HTML/CSS, JavaScript
> **Growing:** React patterns (Level 3, almost there)
> **New territory:** Backend (Node.js, databases, APIs, deployment)
>
> This is not a deficit list. It is a map. And you are further along than most who set this goal."
>
> "Here are three paths I see:
> 1. **Node.js + Express** — builds on your JavaScript. You stay in one language.
> 2. **Ruby on Rails** — different language, but Rails teaches excellent patterns fast.
> 3. **Go deeper in React first** — state management, testing, performance. Solidify before adding backend.
>
> Each is valid. Which resonates?"

You choose Node.js. BodhiKit offers to start a new project:

> "Would you like me to start a learning project with `/learn nodejs`? Based on your pace, this would take about 6-8 weeks. After that, the next step would be databases."

It is honest about its limits: "I can help you build the skills. For visibility and advocacy in your career, seek human mentors and sponsors in your workplace or community."

Also auto-invoked by `/evaluate` when you complete a major milestone or finish a learning project.

### Scenario 12: "Quiz me on what I just learned"

```
/bodhikit:quiz
```

BodhiKit checks your current module and spaced review schedule, then generates 5-7 adaptive questions:

> "Let us see what has taken root. This is not a test. It is a conversation with your memory."
>
> "What does `useState` return in React?" (Level 2 — you should get this)
> "An array with the state value and a setter function."
> "Correct. Now, what happens if you call the setter function with the same value the state already has?" (Level 4 — stretch)
> "Hmm... it re-renders?"
> "Let us approach this differently. Think about what React is optimizing for. If nothing changed, would it need to update the DOM?"

After each wrong answer, BodhiKit does not give the answer. It asks a simpler version or gives a hint. At the end, concepts you got right move up a Leitner box (reviewed less often). Concepts you missed drop to Box 1 (reviewed tomorrow).

### Scenario 13: "I want to adjust my learning plan"

```
/bodhikit:plan adjust
```

> "What would you like to change about your learning plan?"
> "I want to skip the CSS module. I already know CSS well."
> "Let me verify. Can you explain the difference between `grid` and `flexbox` and when you would choose each?"

If you answer well, it skips the module. If your answer has gaps: "Your intuition is close, but there are a few pieces worth solidifying. Would you like to do a quick review instead of the full module?"

You can also reorder modules, add new topics, change pace, or integrate a book you started reading.

### Scenario 14: "How is my end-of-session reflection?"

When you say goodbye during any session, BodhiKit auto-invokes `/reflect`:

> "Before we close, let us look back at today's path. You worked on useEffect and dependency arrays."
>
> "What felt hardest today?"
> "The dependency array. I kept getting infinite loops."
> "That is one of the most common struggles with useEffect. The fact that you can name it means you are developing awareness of your own learning."
>
> "How confident would you feel explaining useEffect to a colleague right now, 1 to 10?"
> "About 4."
> "A 4 is honest. I have noted useEffect for review in your next session. We will approach it from a different angle."

Your confidence rating feeds directly into spaced repetition. A 4/10 concept comes back tomorrow. A 9/10 can wait a week.

## How Agents Work Behind the Scenes

BodhiKit uses three specialized AI agents that handle complex tasks automatically. You never invoke them directly. Skills launch them when needed.

**Skill Assessor Agent** (used by `/learn`, `/assess`, `/evaluate`): Runs adaptive Bloom's taxonomy assessments. Asks 8-12 questions, starting at Level 3, escalating or de-escalating based on your answers. Returns per-topic classifications with confidence ratings. This shapes your entire learning plan.

**Code Reviewer Agent** (used by `/review`, `/practice`, `/teach`): Performs educational code review. Not "is this good code" but "what does this code reveal about your understanding?" Returns Socratic questions and graduated hints, not fixes.

**Resource Finder Agent** (used by `/resources`): Searches the web for verified, community-recommended free resources. Prioritizes official docs, interactive platforms (Exercism, freeCodeCamp), and structured courses. Verifies every link is live. Returns ranked results with difficulty level and estimated time.

## The Daily Workflow

A typical 30-minute learning session:

```
/bodhikit:continue
```

That is it. One command. BodhiKit handles the rest:

1. **Status check** — where you are, what is due (auto)
2. **Spaced review** — quiz on due concepts, 5 minutes (auto)
3. **Teaching** — guided lesson on the next concept, 15 minutes (auto)
4. **Practice** — hands-on exercise within the lesson (auto)
5. **Reflection** — what was hard, what clicked, confidence rating (auto, when you say goodbye)

Consistency beats intensity. 30 minutes daily is better than 5 hours on a weekend.

## What Makes This Different From ChatGPT / Copilot / Other AI Tools

| Feature | Typical AI Tool | BodhiKit |
|---------|----------------|----------|
| Writes code for you | Yes | No. Guides you to write it yourself |
| Proactive teaching | No | Yes. Walks you through concepts step by step |
| Tracks your progress | No | Yes, per concept, across sessions |
| Spaced repetition | No | Yes, Leitner box system |
| Adapts to your level | Sometimes | Always, using Bloom's Taxonomy |
| Gives direct answers | Yes | No. Questions and hints only |
| Remembers where you left off | No | Yes, via `.bodhi/` tracking files |
| End-of-session reflection | No | Yes, metacognitive awareness building |
| Works with your books/courses | No | Yes, as a teaching assistant |
| One-command sessions | No | Yes, `/continue` orchestrates everything |
| Research-backed pedagogy | No | 13+ methodologies integrated |
| Pair programming | No | Yes, 3 modes (strong-style, ping-pong, navigator) |
| Scientific debugging | No | Yes, Zeller's TRAFFIC method |
| Career mentoring | No | Yes, GROW model with honest AI limitations |

## All 17 Skills

| Skill | What It Does |
|-------|-------------|
| `/learn` | Start a new learning project with assessment and personalized plan |
| `/continue` | Resume where you left off, auto-invokes teach, reflect, status |
| `/teach` | Proactive guided teaching: explain, demonstrate, practice, verify |
| `/assess` | Standalone skill assessment on any topic |
| `/review` | Educational code review (local files, GitHub, GitLab, Codeberg) |
| `/quiz` | Active recall check with spaced repetition tracking |
| `/plan` | View, adjust, or regenerate your learning plan |
| `/progress` | Full learning progress dashboard |
| `/resources` | Find, verify, and manage learning resources |
| `/explain` | Deep-dive explanation using the Feynman technique |
| `/practice` | Hands-on exercise calibrated to your level |
| `/evaluate` | Comprehensive evaluation of your learning journey |
| `/reflect` | End-of-session metacognitive reflection |
| `/status` | Quick 3-line check-in |
| `/mentor` | Career and learning path guidance using the GROW model |
| `/pair` | Pair programming: strong-style, ping-pong, or navigator mode |
| `/debug-together` | Scientific debugging: reproduce, hypothesize, probe, isolate, fix |

## Tips for Getting the Most Out of BodhiKit

1. **Be honest about what you do not know.** "I do not know" is the most useful answer you can give. It tells BodhiKit exactly where to focus.

2. **Do not skip spaced reviews.** They feel like a detour, but they are the reason you will remember this in 3 months instead of forgetting it in 3 days.

3. **Type the code yourself.** Do not copy from examples. Do not ask BodhiKit to write it. Your fingers on the keyboard is where the learning happens.

4. **Explain things out loud.** When BodhiKit asks you to explain a concept back, actually do it. The Feynman Technique works because it forces you to confront what you do not understand.

5. **Take breaks.** Your brain does important work during rest (diffuse mode thinking). After a focused session, walk away. The "aha moment" often comes in the shower, not at the keyboard.

6. **Trust the struggle.** If it feels hard, you are learning. If it feels easy, you are reviewing. Both have value, but growth lives in the struggle.

7. **Do the reflection.** When BodhiKit asks "what was hardest today?" at the end of a session, answer honestly. That 3-minute reflection multiplies the value of everything you just did.

## Open Source

BodhiKit is free and open source (MIT license).

Repository: [https://codeberg.org/AnjanJ/bodhikit](https://codeberg.org/AnjanJ/bodhikit)

Contributions, feedback, and bug reports are welcome.

I also built [ShipKit](https://codeberg.org/AnjanJ/shipkit), a developer productivity plugin for Claude Code with 15 skills, 2 agents, and 6 path-scoped rules.

---

*Made with ❤️ by [Anjan](https://anjan.dev)*

*[Buy me a coffee ☕](https://buymeacoffee.com/anjanj)*
