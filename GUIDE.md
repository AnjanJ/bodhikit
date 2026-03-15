# BodhiKit User Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Starting a New Learning Project](#starting-a-new-learning-project)
- [Resuming Your Learning](#resuming-your-learning)
- [Daily Learning Workflow](#daily-learning-workflow)
- [Skills Reference](#skills-reference)
- [Using BodhiKit with Books and Courses](#using-bodhikit-with-books-and-courses)
- [Understanding Your Progress](#understanding-your-progress)
- [How Spaced Repetition Works](#how-spaced-repetition-works)
- [Tips for Effective Learning](#tips-for-effective-learning)

---

## Getting Started

Install BodhiKit:

```
/plugin marketplace add https://codeberg.org/AnjanJ/bodhikit.git
/plugin install bodhikit@bodhikit
```

Restart Claude Code after installing.

Start your first learning project:

```
/bodhikit:learn python
```

BodhiKit will ask you questions to understand your background, goals, and current skill level. Then it will create a personalized learning plan and give you your first exercise.

---

## Starting a New Learning Project

Use `/bodhikit:learn <topic>` to start learning anything:

```
/bodhikit:learn react
/bodhikit:learn rust
/bodhikit:learn system design
/bodhikit:learn web development
/bodhikit:learn zig
```

### What happens when you start:

1. **Topic Discovery** — BodhiKit asks clarifying questions about what you want to learn, why, and your timeline
2. **Skill Assessment** — A series of adaptive questions to understand where you stand (not a test, an exploration)
3. **Plan Generation** — A personalized learning plan with phases, modules, exercises, and spaced review checkpoints
4. **Project Setup** — Creates a `learningWithBodhi/<project-name>/` folder with tracking files
5. **First Exercise** — You get something to DO immediately, not just something to read

### Multiple learning projects

You can have as many learning projects as you want. Each lives in its own folder under `learningWithBodhi/`. One session should focus on one project at a time.

---

## Resuming Your Learning

Use `/bodhikit:continue` to pick up where you left off:

```
/bodhikit:continue                  # Auto-detect or choose from active projects
/bodhikit:continue react-fundamentals  # Resume a specific project
```

BodhiKit will:
- Show a quick status check (project, module, streak, concepts due)
- Find your active projects and show where you left off
- Check if any concepts are due for spaced review
- Offer options: continue current module, practice, or something else
- Auto-invoke `/teach` when you continue with the next module
- Auto-invoke `/reflect` when you say goodbye

This works across sessions. Your progress is saved in `.bodhi/` files.

---

## Daily Learning Workflow

A typical learning session with `/bodhikit:continue`:

1. **Status**: Quick 3-line check-in (auto)
2. **Review**: Spaced review of due concepts (auto, if any are due)
3. **Teach**: Guided teaching of the next concept (auto, when you choose to continue)
4. **Practice**: Hands-on exercise on the concept you just learned (auto, within /teach)
5. **Quiz**: Quick retention check (auto, within /teach)
6. **Reflect**: End-of-session reflection (auto, when you say goodbye)

You can also invoke any skill directly at any time. The auto-invocation just means `/continue` handles the full flow for you.

You do not need to follow this exact order. Use whatever skills feel right for your session.

---

## Skills Reference

### `/bodhikit:learn [topic]`
Start a new learning project. Creates a personalized plan based on your assessment.

### `/bodhikit:continue [project-name]`
Resume from where you left off. Auto-invokes `/status`, `/teach`, and `/reflect` for a complete guided session. Works across sessions.

### `/bodhikit:teach [topic|next]`
Proactive guided teaching. Walks you through a concept step by step: explains it, demonstrates with code, works through a problem together, gives you an exercise, then verifies retention. Auto-invoked by `/continue`.

### `/bodhikit:assess <topic>`
Standalone skill assessment. Get your Bloom's taxonomy level for any topic without starting a full project.

### `/bodhikit:review [file-path|repo-url]`
Educational code review. Analyzes what your code reveals about your understanding. Works with local files, GitHub, GitLab, and Codeberg URLs.

### `/bodhikit:quiz [topic|current]`
Quick knowledge check. 5-7 adaptive questions. Updates spaced repetition tracking. Uses active recall.

### `/bodhikit:plan [view|adjust|regenerate]`
Manage your learning plan. View current state, adjust modules, or regenerate from scratch.

### `/bodhikit:progress [project-name|all]`
View your progress dashboard. Module completion, Bloom's levels, streaks, spaced review health.

### `/bodhikit:resources [find topic|add url|list]`
Find verified free resources, add your own materials (books, courses), or list what you have.

### `/bodhikit:explain <concept>`
Deep-dive using the Feynman technique. BodhiKit explains simply, then asks you to explain back. Identifies and fills gaps.

### `/bodhikit:practice [topic|next]`
Get a hands-on exercise calibrated to your level. Beginners get starter files, advanced learners get problem statements.

### `/bodhikit:evaluate [project-name]`
Comprehensive evaluation of your entire learning journey. Compares where you started to where you are now.

### `/bodhikit:reflect`
End-of-session metacognitive reflection. Asks what was hardest, what surprised you, and your confidence rating. Feeds data back into spaced repetition scheduling. Auto-invoked by `/continue` when you say goodbye.

### `/bodhikit:status`
Quick 3-line check-in: current project, module, streak, and concepts due today. Auto-invoked by `/continue` at session start.

---

## Using BodhiKit with Books and Courses

BodhiKit works as a teaching assistant alongside your existing learning materials:

### Adding a book or course

```
/bodhikit:resources add "Eloquent JavaScript"
/bodhikit:resources add https://www.udemy.com/course/your-course
```

BodhiKit will:
- Analyze the material's structure (chapters, syllabus)
- Map it to your learning plan modules
- Ask how you want to use it: as primary material, supplement, or reference

### Using BodhiKit as a TA

If you are following a book or course, BodhiKit can:
- Explain concepts from the book in different ways (when the book's explanation does not click)
- Quiz you on what you read/watched
- Give you extra practice exercises on the same topics
- Review your code from the book's exercises
- Fill gaps the material does not cover

---

## Understanding Your Progress

### Bloom's Taxonomy Levels

BodhiKit tracks your skill level per concept using Bloom's Taxonomy:

| Level | Name | What It Means |
|-------|------|--------------|
| 1 | Remember | You have heard of this but cannot use it yet |
| 2 | Understand | You understand the idea but need practice applying it |
| 3 | Apply | You can use this with some guidance |
| 4 | Analyze | You can work with this independently and debug issues |
| 5 | Evaluate | You can evaluate approaches and make design decisions |
| 6 | Create | You can design novel solutions and teach others |

### Mastery Criteria

A concept is considered **mastered** when:
- Bloom's Level 4 or higher
- 3 consecutive correct quiz answers
- Spaced repetition Box 4 or 5
- Can explain it to someone else (Feynman check)

---

## How Spaced Repetition Works

BodhiKit uses a virtual Leitner box system to schedule concept reviews:

| Box | Review After | Meaning |
|-----|-------------|---------|
| 1 | 1 day | New or forgotten |
| 2 | 3 days | Recalled once |
| 3 | 7 days | Building retention |
| 4 | 14 days | Strong retention |
| 5 | 30 days | Long-term mastery |

- Get a concept right: it moves up one box (reviewed less often)
- Get it wrong: it drops back to Box 1 (reviewed tomorrow)
- When you run `/continue`, BodhiKit checks what is due for review

This is automatic. You do not need to manage it.

---

## Tips for Effective Learning

1. **Consistency beats intensity.** 30 minutes daily is better than 5 hours once a week.
2. **Struggle is learning.** If it feels hard, you are growing. If it feels easy, you are reviewing.
3. **Explain what you learn.** The Feynman technique is your best tool. If you cannot explain it simply, you do not understand it yet.
4. **Do not skip reviews.** Spaced repetition only works if you do the reviews when they are due.
5. **Write the code yourself.** Do not copy from BodhiKit or from examples. Type it. Change it. Break it. Fix it.
6. **Take breaks.** Your brain does important work during rest. After focused learning, walk away for a few minutes.
7. **Trust the process.** Some days will feel unproductive. Growth is often invisible. Keep showing up.

---

## Philosophy

BodhiKit is built on a simple belief: everyone can learn to code, and the best way to learn is by doing, with a wise guide by your side.

The plugin does not write code for you. It asks questions, gives hints, creates exercises, and reviews your work. The goal is not to be needed forever. The goal is to help you reach the point where you do not need it anymore.

"The obstacle is the path."
