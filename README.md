# BodhiKit

**Research-backed interactive coding tutor for Claude Code.**

Bodhi (Pali: "awakening") is a patient, wise guide that teaches you anything in the world of coding, software engineering, and tech. It does not write code for you. It teaches you to write code yourself.

## What Makes BodhiKit Different

- **Research-backed**: Built on proven learning science (Oakley, Feynman, Bloom, Vygotsky, Ericsson, Dweck, Bjork)
- **Personalized**: Assesses your skill level, builds a custom learning plan, adapts to your pace
- **Hands-on**: Learn by doing. Exercises, projects, code review. Never just reading.
- **Remembers your journey**: Spaced repetition, progress tracking, cross-session continuity
- **Honest and wise**: Feedback that is respectful, specific, and genuinely helpful

## Install

```bash
claude plugin add https://codeberg.org/AnjanJ/bodhikit.git
```

## Quick Start

```
/bodhikit:learn react        # Start learning React
/bodhikit:continue           # Resume where you left off
/bodhikit:quiz               # Test your knowledge
/bodhikit:progress           # See your dashboard
```

## Skills (11)

| Skill | Description |
|-------|-------------|
| `/learn` | Start a new learning project with assessment and personalized plan |
| `/continue` | Resume from where you left off (cross-session) |
| `/assess` | Standalone skill assessment on any topic |
| `/review` | Educational code review (local files, GitHub, GitLab, Codeberg) |
| `/quiz` | Active recall check with spaced repetition tracking |
| `/plan` | View, adjust, or regenerate your learning plan |
| `/progress` | Learning progress dashboard |
| `/resources` | Find, verify, and manage learning resources |
| `/explain` | Deep-dive explanation using the Feynman technique |
| `/practice` | Hands-on exercise calibrated to your level |
| `/evaluate` | Comprehensive evaluation of your learning journey |

## Agents (3)

| Agent | Model | Purpose |
|-------|-------|---------|
| skill-assessor | Sonnet | Adaptive Bloom's taxonomy skill evaluation |
| code-reviewer | Sonnet | Educational code review (what code reveals about understanding) |
| resource-finder | Haiku | Web search for verified free learning resources |

## Knowledge Bases (3)

| Knowledge Base | Purpose |
|---------------|---------|
| learning-methodology | Spaced repetition, Bloom's taxonomy, ZPD, Feynman technique, deliberate practice |
| assessment-framework | Question templates by Bloom's level, mastery criteria, exercise design |
| teaching-personality | Oogway/Yoda/Buddha/Ambedkar personality guide for all interactions |

## Path-Scoped Rules (1)

| Rule | Activates On |
|------|-------------|
| learning-project | Files inside `learningWithBodhi/` directories |

## Learning Project Structure

When you start learning, BodhiKit creates a project folder:

```
learningWithBodhi/
├── react-fundamentals/
│   ├── .bodhi/              # Progress tracking
│   │   ├── state.json       # Current position, streak, session history
│   │   ├── plan.md          # Your personalized learning plan
│   │   ├── progress.md      # Per-topic mastery levels
│   │   ├── spaced-review.json  # Leitner box system for retention
│   │   ├── assessment.md    # Assessment history
│   │   └── resources.md     # Curated resources
│   ├── exercises/           # Hands-on exercises
│   ├── projects/            # Larger project work
│   └── notes/               # Your personal notes
```

We recommend backing this with git and a remote repository.

## The Science

BodhiKit integrates these research-backed methodologies:

- **Spaced Repetition** (Ebbinghaus, Leitner) — Review concepts at expanding intervals for durable memory
- **Bloom's Taxonomy** — Assess and track skills across 6 cognitive levels (Remember to Create)
- **Zone of Proximal Development** (Vygotsky) — Calibrate difficulty to where learning is most productive
- **Feynman Technique** — Explain concepts simply to reveal gaps in understanding
- **Deliberate Practice** (Ericsson) — Targeted exercises at the edge of ability with immediate feedback
- **Growth Mindset** (Dweck) — Feedback that promotes learning over performance
- **Desirable Difficulties** (Bjork) — Interleaving, retrieval practice, and variation for stronger retention
- **Active Recall** — Retrieve from memory rather than re-read for superior learning outcomes
- **Metacognition** — Teach learners HOW to learn, not just WHAT to learn
- **Mastery-Based Progression** — Demonstrate competence before advancing, not time-based

## The Philosophy

BodhiKit speaks with the voice of a wise, patient teacher. Think Oogway, Yoda, Buddha, Ambedkar.

- The learner writes code. BodhiKit asks questions.
- Every struggle is an opportunity for growth.
- Honest feedback, wrapped in compassion.
- The goal is to become unnecessary.

## Uninstall

```bash
claude plugin remove bodhikit
```

Your `learningWithBodhi/` project folders are not affected.

## License

MIT

Made with ❤️ by [Anjan](https://anjan.dev)

[Buy me a coffee ☕](https://buymeacoffee.com/anjanj)
