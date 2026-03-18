# BodhiKit

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?logo=buymeacoffee)](https://buymeacoffee.com/anjanj)

**Research-backed interactive coding tutor for Claude Code.**

Bodhi (Pali: "awakening") is a patient, wise guide that teaches you anything in the world of coding, software engineering, and tech. It does not write code for you. It teaches you to write code yourself.

## What Makes BodhiKit Different

- **Research-backed**: Built on proven learning science (Oakley, Feynman, Bloom, Vygotsky, Ericsson, Dweck, Bjork)
- **Deeply personalized**: Assesses your unique skill level, builds a custom learning plan, adapts to your pace
- **Proactive teaching**: `/teach` walks you through concepts step by step, not just answering questions
- **Hands-on**: Learn by doing. Exercises, projects, code review. Never just reading.
- **Remembers your journey**: Spaced repetition, progress tracking, cross-session continuity
- **Metacognitive reflection**: End-of-session `/reflect` builds your awareness of HOW you learn
- **One command sessions**: `/continue` auto-invokes status, teaching, practice, and reflection
- **Honest and wise**: Feedback that is respectful, specific, and genuinely helpful

## Install

```
/plugin marketplace add https://codeberg.org/AnjanJ/bodhikit.git
/plugin install bodhikit@bodhikit
```

Restart Claude Code after installing to load the plugin.

**Important: Enable only where you need it.** BodhiKit loads 15 knowledge bases. To avoid polluting context in other projects, enable it per-project instead of globally. In your `learningWithBodhi/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "bodhikit@bodhikit": true
  }
}
```

Or disable it in projects where you do not need it by adding to `.claude/settings.local.json`:

```json
{
  "enabledPlugins": {
    "bodhikit@bodhikit": false
  }
}
```

Or test locally without installing:

```
claude --plugin-dir ~/code/bodhikit
```

That's it. All skills, agents, rules, and knowledge bases are immediately available.

## Quick Start

```
/bodhikit:learn react        # Start learning React
/bodhikit:continue           # Resume — auto-runs status, teach, reflect
/bodhikit:teach              # Guided teaching of the next concept
/bodhikit:quiz               # Test your knowledge
/bodhikit:status             # Quick 3-line check-in
/bodhikit:progress           # Full progress dashboard
```

## Skills (17)

| Skill | Description |
|-------|-------------|
| `/learn` | Start a new learning project with assessment and personalized plan |
| `/continue` | Resume from where you left off — auto-invokes teach, reflect, status |
| `/teach` | Proactive guided teaching: explain, demonstrate, practice, verify |
| `/assess` | Standalone skill assessment on any topic |
| `/review` | Educational code review (local files, GitHub, GitLab, Codeberg) |
| `/quiz` | Active recall check with spaced repetition tracking |
| `/plan` | View, adjust, or regenerate your learning plan |
| `/progress` | Learning progress dashboard |
| `/resources` | Find, verify, and manage learning resources |
| `/explain` | Deep-dive explanation using the Feynman technique |
| `/practice` | Hands-on exercise calibrated to your level |
| `/evaluate` | Comprehensive evaluation of your learning journey |
| `/reflect` | End-of-session metacognitive reflection |
| `/status` | Quick 3-line check-in: project, module, streak, concepts due |
| `/mentor` | Career and learning path guidance using the GROW model |
| `/pair` | Pair programming: strong-style, ping-pong, or navigator mode |
| `/debug-together` | Scientific debugging: reproduce, hypothesize, probe, isolate, fix |

## Agents (3)

| Agent | Model | Purpose |
|-------|-------|---------|
| skill-assessor | Sonnet | Adaptive Bloom's taxonomy skill evaluation |
| code-reviewer | Sonnet | Educational code review (what code reveals about understanding) |
| resource-finder | Haiku | Web search for verified free learning resources |

## Knowledge Bases (15)

Each learning methodology lives in its own focused knowledge base, loaded only when needed (progressive disclosure):

| Knowledge Base | Purpose |
|---------------|---------|
| spaced-repetition | Ebbinghaus forgetting curve, Leitner box system |
| blooms-taxonomy | 6 cognitive levels for programming, mastery criteria |
| zone-of-proximal-development | Three zones, detection signals, scaffolding strategy |
| feynman-technique | 4 steps for deep understanding, when to use |
| deliberate-practice | Targeted exercises at the edge of ability |
| growth-mindset | Language patterns, praising strategy over talent |
| desirable-difficulties | Spacing, interleaving, retrieval, generation, variation |
| metacognition | Teaching learners HOW to learn, Dunning-Kruger, illusions of competence |
| constructivism | Spiral curriculum, project progression by level |
| ai-learning-safeguards | Risks of AI over-reliance, structural safeguards |
| mentoring-theory | GROW model, Kram's career and psychosocial functions |
| pair-programming | Strong-style, driver/navigator, ping-pong TDD, Williams & Kessler |
| scientific-debugging | TRAFFIC method, debugging mindset, wolf fence, expert vs novice |
| assessment-framework | Question templates by Bloom's level, exercise design |
| teaching-personality | Oogway/Yoda/Buddha/Ambedkar personality guide |

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

See `docs/example-project/` for a realistic example of what these tracking files look like after a few sessions.

## How a Session Works

Run `/bodhikit:continue` and the plugin handles the entire flow:

```
/continue
  ├── /status       → quick 3-line check-in
  ├── spaced review → quiz on concepts due for review
  ├── /teach        → guided teaching of the next concept
  │     ├── explain with analogies and code examples
  │     ├── work through a problem together
  │     ├── independent exercise
  │     └── quick retention check
  └── /reflect      → end-of-session metacognitive reflection
```

One command. Complete learning session. No need to remember which skills to invoke.

## The Science

BodhiKit integrates these research-backed methodologies. We stand on the shoulders of giants:

- **Spaced Repetition** — Review concepts at expanding intervals for durable memory
  - Hermann Ebbinghaus, *[Memory: A Contribution to Experimental Psychology](https://en.wikipedia.org/wiki/Memory:_A_Contribution_to_Experimental_Psychology)* (1885)
  - Sebastian Leitner, *[Learning to Learn](https://en.wikipedia.org/wiki/Leitner_system)* (1972)

- **Learning How to Learn** — Focused/diffuse modes, chunking, interleaving, overcoming procrastination
  - Dr. Barbara Oakley, *[A Mind for Numbers](https://barbaraoakley.com/books/a-mind-for-numbers/)* (2014)
  - Dr. Barbara Oakley and Dr. Terrence Sejnowski, *[Learning How to Learn](https://www.coursera.org/learn/learning-how-to-learn)* (Coursera, most popular online course in the world)

- **Bloom's Taxonomy** — Assess and track skills across 6 cognitive levels (Remember to Create)
  - Benjamin Bloom, *[Taxonomy of Educational Objectives](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy)* (1956)
  - Lorin Anderson and David Krathwohl, *[A Taxonomy for Learning, Teaching, and Assessing](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy#The_cognitive_domain_(knowledge-based))* (2001, revised taxonomy)

- **Zone of Proximal Development** — Calibrate difficulty to where learning is most productive
  - Lev Vygotsky, *[Mind in Society](https://en.wikipedia.org/wiki/Zone_of_proximal_development)* (1978)

- **Feynman Technique** — Explain concepts simply to reveal gaps in understanding
  - Richard Feynman, inspired by his teaching philosophy at Caltech
  - Popularized by James Gleick, *[Genius: The Life and Science of Richard Feynman](https://en.wikipedia.org/wiki/Genius:_The_Life_and_Science_of_Richard_Feynman)* (1992)

- **Deliberate Practice** — Targeted exercises at the edge of ability with immediate feedback
  - K. Anders Ericsson, *[Peak: Secrets from the New Science of Expertise](https://en.wikipedia.org/wiki/Peak:_Secrets_from_the_New_Science_of_Expertise)* (2016)
  - K. Anders Ericsson, *[The Role of Deliberate Practice in the Acquisition of Expert Performance](https://psycnet.apa.org/record/1993-40718-001)* (1993)

- **Growth Mindset** — Feedback that promotes learning over performance
  - Dr. Carol Dweck, *[Mindset: The New Psychology of Success](https://en.wikipedia.org/wiki/Mindset_(book))* (2006)

- **Desirable Difficulties** — Interleaving, retrieval practice, and variation for stronger retention
  - Dr. Robert Bjork and Dr. Elizabeth Bjork, *[Making Things Hard on Yourself, But in a Good Way](https://bjorklab.psych.ucla.edu/research/)* (2011)

- **Constructivism and Spiral Curriculum** — Learning by building, revisiting concepts at increasing depth
  - Jean Piaget, *[The Construction of Reality in the Child](https://en.wikipedia.org/wiki/Constructivism_(philosophy_of_education))* (1954)
  - Jerome Bruner, *[The Process of Education](https://en.wikipedia.org/wiki/The_Process_of_Education)* (1960)
  - Seymour Papert, *[Mindstorms: Children, Computers, and Powerful Ideas](https://en.wikipedia.org/wiki/Mindstorms_(book))* (1980)

- **Mastery-Based Learning** — Demonstrate competence before advancing, not time-based
  - Benjamin Bloom, *[Learning for Mastery](https://en.wikipedia.org/wiki/Mastery_learning)* (1968)

- **Metacognition** — Teach learners HOW to learn, not just WHAT to learn
  - John Flavell, who coined the term in *[Metacognition and Cognitive Monitoring](https://psycnet.apa.org/record/1980-09388-001)* (1979)

- **Mentoring Theory** — Career and psychosocial functions of effective mentoring
  - Kathy Kram, *[Mentoring at Work](https://www.researchgate.net/publication/232463073_Mentoring_at_Work_Developmental_Relationships_in_Organisational_Life)* (1985)
  - Sir John Whitmore, *[Coaching for Performance (GROW Model)](https://en.wikipedia.org/wiki/GROW_model)* (1988)

- **Pair Programming** — Collaborative coding that improves learning, quality, and retention
  - Kent Beck, *[Extreme Programming Explained](https://en.wikipedia.org/wiki/Extreme_programming)* (1999)
  - Laurie Williams and Robert Kessler, *[Pair Programming Illuminated](https://collaboration.csc.ncsu.edu/laurie/Papers/ESE%20-%20Single%20Column.pdf)* (2002)
  - Llewellyn Falco, *[Strong-Style Pairing](http://llewellynfalco.blogspot.com/2014/06/llewellyns-strong-style-pairing.html)* (2014)

- **Scientific Debugging** — Systematic, hypothesis-driven approach to finding and fixing bugs
  - Andreas Zeller, *[Why Programs Fail](https://en.wikipedia.org/wiki/Why_Programs_Fail)* (2005)
  - Devon H. O'Dell, *[The Debugging Mindset](https://queue.acm.org/detail.cfm?id=3068754/)* (2017, ACM Queue)
  - Edward J. Gauss, *[Wolf Fence Algorithm](https://dl.acm.org/doi/abs/10.1145/358690.358695)* (1982, ACM)

## The Philosophy

BodhiKit speaks with the voice of a wise, patient teacher. Think Master Oogway, Yoda, Gautama Buddha, and Dr. B.R. Ambedkar.

- The learner writes code. BodhiKit asks questions.
- Every struggle is an opportunity for growth.
- Honest feedback, wrapped in compassion.
- The goal is to become unnecessary.

## Learn More

[Read the full blog post on Medium](https://medium.com/@anjanj/bodhikit-a-research-backed-ai-coding-tutor-that-teaches-you-instead-of-writing-code-for-you-8c83cba338d9) — detailed scenarios, the science behind the plugin, and how to get the most out of it.

## Uninstall

```
/plugin uninstall bodhikit@bodhikit
```

Your `learningWithBodhi/` project folders are not affected.

## License

MIT

Made with ❤️ by [Anjan](https://anjan.dev)

<a href="https://www.buymeacoffee.com/anjanj" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="200"></a>
