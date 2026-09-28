# BodhiKit feedback survey

An anonymous, opt-in survey for anyone who has used BodhiKit, on any platform. It is hosted on Google Forms so that answering needs no GitHub account and nothing is public.

**Take the survey:** [BodhiKit — feedback survey](https://docs.google.com/forms/d/e/1FAIpQLSdTfBrT3J3ot94JmDXwIQosYQaCoxd-K2hDTYWlctl1lKfEgQ/viewform?usp=pp_url&entry.396027065=GitHub+README)

This file is the source of truth for the questions. When the form changes, change this file in the same commit and bump the version, so every answer can be read against the questions that were live when it was given.

## Where it is linked

Each placement uses its own pre-filled link, which pre-answers the last question ("Where did you find this survey?"). That is the only attribution: no tracking parameters, no cookies, nothing sent by the plugin.

| Placement | Pre-filled answer |
|---|---|
| README, *Feedback* section, and this file | GitHub README |
| GitHub *New issue* page (`.github/ISSUE_TEMPLATE/config.yml`) | GitHub "New issue" page |
| `/evaluate` closing, at project completion or a major milestone | Inside BodhiKit, at the end of an evaluation |

The plugin never opens the link and never asks during a lesson. `/evaluate` mentions it once per milestone, as an opt-in line.

## Questions — version 1 (2026-09-28)

Intro shown on the form:

> I'm Anjan, and I build BodhiKit on my own. This survey is for anyone who has used BodhiKit, on any platform. It takes about 5 minutes and it's anonymous: I don't ask your name, and the email at the end is optional. I'll use your answers only to improve BodhiKit. Honest answers help most, especially about what annoys you.

| # | Question | Type | Required | Options |
|---|---|---|---|---|
| 1 | Where do you use BodhiKit? | Checkboxes | Yes | Claude Code · Codex · ChatGPT phone app · ChatGPT on a computer · Other |
| 2 | What are you learning with it? | Checkboxes | Yes | A programming language or framework · Computer science fundamentals · Preparing for a job or interview · A course at school or university · A subject that isn't coding · Other |
| 3 | How much coding experience do you have? | Multiple choice | Yes | None · Less than a year · 1–5 years · More than 5 years |
| 4 | How did you first hear about BodhiKit? | Multiple choice | Yes | A plugin directory or marketplace · GitHub · Reddit · A friend or classmate · A blog post · Other |
| 5 | When did you start using it? | Multiple choice | Yes | This week · 1–4 weeks ago · 1–3 months ago · Longer ago |
| 6 | In the last 2 weeks, on how many days did you use it? | Multiple choice | Yes | 0 · 1 · 2–3 · 4–7 · 8 or more |
| 7 | Which parts do you use? | Checkboxes | Yes | /continue · /teach · /quiz · /practice · /reflect · /pair or /debug-together · I just chat with it · Not sure |
| 8 | When you come back to a topic another day, what happens? | Multiple choice | Yes | It picks up where I left off · I paste in a summary it gave me · I start over · I haven't come back to a topic yet |
| 9 | Think of the last time it really helped. What were you trying to understand, and what did it do that helped? | Paragraph | Yes | — |
| 10 | Which of these have happened? | Checkboxes | Yes | It asked questions when I just wanted the answer · It said I was right when I was only guessing · It explained something wrong · It was too slow when I was short on time · Its examples didn't fit my subject · Reviews came at the wrong time · It lost track of where I was · None of these |
| 11 | Compared with the same AI without BodhiKit, for learning it is… | Multiple choice | Yes | Much better · A bit better · About the same · Worse · I haven't compared |
| 12 | If BodhiKit disappeared tomorrow, how would you feel? | Multiple choice | Yes | Very disappointed · Somewhat disappointed · Not disappointed |
| 13 | Optional: one thing you would change. | Paragraph | No | — |
| 14 | Optional: your learning numbers. | Paragraph | No | — |
| 15 | Optional: a link to one study chat where BodhiKit helped. | Short answer | No | — |
| 16 | Optional: your email, if you're happy for me to follow up with a question or two. | Short answer | No | — |
| 17 | Where did you find this survey? | Multiple choice | No | GitHub README · GitHub "New issue" page · Inside BodhiKit, at the end of an evaluation · Reddit · Someone shared it with me · Other |

Help text on the optional questions:

- **14:** If you use Claude Code or Codex, ask BodhiKit to run `bodhi-state export-anonymized` in your learning project and paste the result. It contains counts only: no topic names and nothing you wrote.
- **15:** A ChatGPT share link, a gist, anything. Please remove anything personal first.

## What each question is for

- **1, 7, 8** — which platforms and skills carry real use, and whether saved progress matters to people on hosts without project files (`docs/openai.md`, *Runtime behavior by platform*).
- **3, 4, 5, 6** — who is answering and how established the habit is, so answers are read in context.
- **9, 10** — what works and what fails, including the lenient-grading and too-Socratic risks.
- **11, 12** — whether BodhiKit is worth anything over the same model without it. This is the claim the README cannot yet support with data.
- **14** — outcome numbers in the same shape as `docs/outcomes.md`.
- **17** — which placement brings people in.

## Privacy

Answers are stored in the maintainer's Google account, not in this repository. The form collects no email address unless one is typed into question 16, and it does not require signing in. Individual answers are never published; anything shared from them is aggregated and anonymized. See [PRIVACY.md](../PRIVACY.md).
