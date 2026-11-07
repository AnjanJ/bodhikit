# Command reference for guide writers

The source for a guide's "Every BodhiKit command" section. Rewrite the examples for the learner's subjects; keep the facts. One `###` entry per learner command: `dev/eval/test_guide_writer.py` fails if this list and the user-invocable skills in `skills/` differ. If the changelog shows a command's behaviour changed, re-read its `skills/<name>/SKILL.md` and correct the entry.

How to call a command:

- **Claude** (web, desktop app, phone): type `/` or click **+** and choose it, or type `/bodhikit:<name>`. Plain words ("Use BodhiKit to…") also start the right command.
- **ChatGPT** (web, desktop app, phone): type `@`, choose **BodhiKit** or one of its commands, and say what you want in plain words.
- **Saved progress:** only in Claude on a computer with the Claude Desktop app open and the computer ticked under **+** → **Devices**. Everywhere else BodhiKit teaches but keeps nothing between chats, and the learner keeps a learning log.

Most learners need five: **learn** once per subject, then **continue** (Claude with saved progress) or **teach**, **quiz** and **reflect** (everywhere else).

## Start and plan

### learn
- **What it does:** starts a new subject. It asks why and what "done" looks like, proposes how the work will be checked (code that runs, problems against answers worked out first, writing against criteria set first, or practice away from the screen that it debriefs), runs a short check of what the learner knows (about ten questions, 10–20 minutes, rating themselves before each topic), builds a plan of phases and modules, saves trusted sources for a subject that isn't code, and sets a first small exercise.
- **When:** once per subject.
- **Claude:** `/bodhikit:learn <subject>` followed by the learner's details.
- **ChatGPT:** `@BodhiKit Help me learn <subject>…`
- **Without saved files:** it says once that it can't keep a schedule, teaches anyway, and gives a plan and a note to keep. A note brought to a new chat is read as background.
- **Example patterns:** "Help me learn R for my biology course…", "Help me learn to communicate clearly at work…", "Help me prepare for <exam>…".

### assess
- **What it does:** checks the learner's level on one topic without starting a subject.
- **When:** before deciding whether to study something, or to see whether a topic is still solid.
- **Claude:** `/bodhikit:assess <topic>`
- **ChatGPT:** `@BodhiKit Assess what I know about <topic>.`
- **Example patterns:** "Assess what I know about data frames", "Assess my understanding of stakeholder management".

### plan
- **What it does:** shows the plan and where the learner is in it (*view*), changes it (*adjust*: reorder, skip after a quick check, add a topic), or rebuilds it (*regenerate*).
- **When:** a deadline, a job or a priority changes.
- **Claude:** `/bodhikit:plan`, `/bodhikit:plan adjust`, `/bodhikit:plan regenerate`
- **ChatGPT:** `@BodhiKit Adjust my <subject> plan: [paste plan]. <what changed>.`
- **Without saved files:** works on the plan the learner pastes.

### resources
- **What it does:** finds free, trustworthy sources, checks that the links work, and keeps a list (*find*, *add*, *remove*, *list*). Off code it looks for a standard reference and an open source in the subject's own literature.
- **Claude:** `/bodhikit:resources find <topic>`
- **ChatGPT:** `@BodhiKit Find free, trustworthy resources on <topic>.`

## Learn and practise

### continue
- **What it does:** a whole session in one command: a three-line check-in, the reviews that are due, the next lesson, and the close.
- **When:** every session, where progress is saved.
- **Claude:** `/bodhikit:continue` or `/bodhikit:continue <subject>`
- **ChatGPT:** `@BodhiKit Continue my <subject>. Here is my plan and my note from last time: …`
- **Without saved files:** it works from the note the learner pastes.

### teach
- **What it does:** teaches the next idea in the plan, or a topic the learner names. The order is: a guess first, then the new words for today, the explanation with an example, one example worked together, the learner's own exercise, and an explain-back that is graded. Hints come in three steps: direction, approach, near-answer. It also runs "understanding only" sessions (explain, then explain back, no exercise) and a short version for someone pressed for time.
- **Claude:** `/bodhikit:teach next`, `/bodhikit:teach <topic>`
- **ChatGPT:** `@BodhiKit Teach me the next module in my <subject> plan: <module>.` · `@BodhiKit I just want to understand <topic> today. No exercise.`

### practice
- **What it does:** an exercise at the learner's level.
  - Code: they write it and run it.
  - Problems: answers are worked out before the questions are shown.
  - Writing: criteria are set before they write, and the case is one the lesson didn't use.
  - Practice away from the screen: a task sized to 10–30 minutes, then a debrief of three questions (what did you do, what went wrong or surprised you, what would you change). The debrief is graded and the practice counts as the learner's account.
- **Claude:** `/bodhikit:practice <topic>` or `/bodhikit:practice next`
- **ChatGPT:** `@BodhiKit Give me <n> problems on <topic>. Check my working.` · `@BodhiKit I <did the real thing> today. Debrief me.`

### review
- **What it does:** feedback on the learner's own work: code, a problem set's working, or a written piece. Off code it quotes the learner's lines, says what each shows, and asks one question per point; it never rewrites the piece or reworks the problem.
- **Claude:** `/bodhikit:review` and paste or name the work
- **ChatGPT:** `@BodhiKit Review my <work>. The task was: …`

## Remember and close

### quiz
- **What it does:** five to seven questions, one at a time. Where progress is saved it starts with what is due. A review question describes a situation without naming the topic, because recognising which idea a situation needs is part of knowing it.
- **Claude:** `/bodhikit:quiz current`, `/bodhikit:quiz <topic>`
- **ChatGPT:** `@BodhiKit Quiz me on these, one at a time, without naming the topic: <ideas due>.`

### reflect
- **What it does:** closes a session. It asks what was hard and what was easier than expected, then has the learner explain each idea *before* rating their confidence. It writes the day's revision sheet where progress is saved, and otherwise gives a summary note to keep.
- **Claude:** `/bodhikit:reflect`
- **ChatGPT:** `@BodhiKit Let's reflect and close the session. Then give me my summary note.`

### forget
- **What it does:** when the learner honestly feels an idea has slipped, it comes back for review tomorrow and its schedule starts again. `--park` sets an idea aside on purpose without losing anything; `--unpark` brings it back.
- **Claude:** `/bodhikit:forget <idea>`, `/bodhikit:forget --park <idea>`
- **ChatGPT:** `@BodhiKit I've lost <idea>. Start it again from tomorrow.`
- **Without saved files:** the learner sets that idea back to a 1-day gap in their log.

### progress
- **What it does:** where the learner stands: *quick* (three lines), a full dashboard, or *all* (one line per subject).
- **Claude:** `/bodhikit:progress quick`, `/bodhikit:progress`, `/bodhikit:progress all`
- **ChatGPT:** `@BodhiKit Here's my log. Summarise where I stand and what to review this week.`
- **Without saved files:** it can only summarise the log the learner pastes.

## Look back and grow

### mentor
- **What it does:** career and learning coaching with the GROW model (goal, reality, options, will). The learner suggests options before it adds any.
- **Claude:** `/bodhikit:mentor <question>`
- **ChatGPT:** `@BodhiKit Mentor me: <question>.`
- **Example patterns:** a 90-day plan at work, preparing a one-to-one, how a subject fits a career.

### evaluate
- **What it does:** a full look at a subject's whole journey. The learner predicts how they've done before seeing the data, then compares. It can mark a subject finished.
- **Claude:** `/bodhikit:evaluate <subject>`
- **ChatGPT:** `@BodhiKit Evaluate my <subject> journey. Here are all my notes: …`

### teach-back
- **What it does:** optional, only after *evaluate* marks a subject finished. The learner writes a short article explaining a topic they once found hard, compares it with how experts explain it, and decides whether to publish. It never writes a word of the piece.
- **Claude:** `/bodhikit:teach-back <subject>`
- **ChatGPT:** `@BodhiKit I've finished my <subject> subject. Help me plan a teach-back on <topic>.`

## For code only, and housekeeping

### pair
- **What it does:** pair programming in three styles: it guides while the learner types; they take turns; or, for more advanced learners, the learner directs while it describes the code and the learner checks it. Offered only on code.
- **Claude:** `/bodhikit:pair`, `/bodhikit:pair ping-pong`
- **ChatGPT:** `@BodhiKit Pair with me on <small program>. I'll type.`

### debug-together
- **What it does:** finds a bug in the learner's code step by step: reproduce it, guess why, test the guess, narrow it down. The learner makes the fix; it never fixes it for them. Offered only on code.
- **Claude:** `/bodhikit:debug-together <file>`
- **ChatGPT:** `@BodhiKit Help me debug this. Code: … Error: …`

### housekeep
- **What it does:** tidies long saved records into archives, and *migrate* updates old records after a big BodhiKit update.
- **When:** rarely; only when BodhiKit or its release notes suggest it.
- **Claude:** `/bodhikit:housekeep`, `/bodhikit:housekeep migrate`
- **Without saved files:** not needed.
