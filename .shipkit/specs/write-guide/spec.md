# Spec: Write a learner guide

> Spec accepted at commit `a7eb6b8` on master.
> Status: open
> Paths: dev/guide-writer/, dev/eval/test_guide_writer.py, dev/check.sh, .gitignore, CLAUDE.md

## Purpose
A maintainer-only Claude Code skill, `/write-guide`, that writes a personalised guide to using BodhiKit in Claude and ChatGPT (web, desktop app, phone) for one person or one role, the way the two November 2026 guides were made: ask what it needs, research, verify every fact, design the learning, write, render, check, and report. It also revises an existing guide. It serves the quarter's goal of outside learners on non-code subjects (`intake.md`).

## User stories
- As the maintainer, I want to type `/write-guide <who it is for>` and be asked only what I can answer, so that a friend or a role gets a guide as good as the hand-made ones without my re-explaining the process.
- As the maintainer, I want every fact in a guide checked and every unchecked one marked, so that I can send it without re-reading every claim against its source.
- As the maintainer, I want the skill to cost no context until I call it, so that ordinary sessions in this repo are not paying for it.
- As a reader of a guide, I want prompts I can copy and a schedule that fits my week, so that I can start the same day.

## Requirements (EARS)

### Where it lives and what it costs
- **REQ-1.** The skill's `SKILL.md` frontmatter shall set `disable-model-invocation: true`.
- **REQ-2.** The skill shall live under `dev/guide-writer/`, and no file from `dev/guide-writer/` shall appear in the Cowork or OpenAI plugin packages.
- **REQ-3.** CLAUDE.md shall say where the skill lives and give the command that links it into `.claude/skills/write-guide`. [untested: prose, verified by reading]
- **REQ-4.** The repository shall ignore `output/`.

### Modes and intake
- **REQ-5.** When invoked with a description of a person or a role, the skill shall write a new guide. [untested: model behaviour, checked by a manual run]
- **REQ-6.** When invoked as `revise <path>`, the skill shall keep a copy of the original guide beside it before changing anything, then re-verify and extend the guide at that path. [untested: model behaviour, checked by a manual run]
- **REQ-7.** Before any research, the skill shall ask every question in its intake bank that the maintainer's request and the repository do not answer. [untested: model behaviour, checked by a manual run]
- **REQ-8.** If a personal detail (a name, pronouns, an employer, a country, a plan, a device) is not given, then the skill shall ask for it or leave it out, and shall not invent it. [untested: model behaviour, checked by a manual run]

### Ground truth from the repository
- **REQ-9.** The command reference `references/commands.md` shall name exactly the user-invocable skills in `skills/`, no more and no fewer.
- **REQ-10.** When it writes a guide, the skill shall read the BodhiKit version from `.claude-plugin/plugin.json` and how each platform keeps or loses progress from the repository's platform documents, not from its own memory. [untested: model behaviour, checked by a manual run]

### Verification
- **REQ-11.** Every entry in `references/platform-facts.md` shall carry a source and the date it was checked.
- **REQ-12.** The skill shall keep a claim ledger beside each guide, listing each factual claim with its source, the date it was checked and whether it was verified. [untested: model behaviour, checked by a manual run]
- **REQ-13.** The skill shall list a book, course, page or organisation as a resource only after opening its page and confirming the title, the author or publisher, and the year. [untested: model behaviour, checked by a manual run]
- **REQ-14.** If a source cannot be opened, then the skill shall mark the claim "not verified" in the guide or leave it out, and shall not disguise its client to get past a site's bot check. [untested: model behaviour, checked by a manual run]
- **REQ-15.** When a platform fact found during research differs from `references/platform-facts.md`, the skill shall update that entry with the new fact, source and date, and shall change no other file in the repository. [untested: model behaviour, checked by a manual run]

### What the guide says
- **REQ-16.** The guide template and the command reference shall contain no bare Bloom level or box number and no state-engine name (decision 0005).
- **REQ-17.** Where a subject is gated by eligibility, a licence or a prerequisite, the guide shall put that check before any schedule that depends on it. [untested: model behaviour, checked by a manual run]
- **REQ-18.** Files under `dev/guide-writer/` shall name no real learner, their employer or where they live. [untested: a denylist would itself publish the names; verified by reading]

### Output
- **REQ-19.** When given a guide's HTML file and an output folder, `scripts/render.sh` shall write the PDF and the DOCX beside the HTML, and a contact sheet of the PDF's pages.
- **REQ-20.** If the output folder is inside the repository, then `scripts/render.sh` shall refuse and exit non-zero.
- **REQ-21.** If a tool it needs (`weasyprint`, `pandoc`, `pdftoppm`, `magick`) is missing, then `scripts/render.sh` shall name it and exit non-zero.
- **REQ-22.** When it finishes, the skill shall report the output paths, every claim left not verified, and what the maintainer should check before sending the guide. [untested: model behaviour, checked by a manual run]

## Out of scope
- Shipping the skill to learners, or any change to the plugin's `skills/`, `agents/`, `hooks/` or `scripts/`.
- Publishing, sending or uploading a guide.
- Storing any guide, or any learner's personal details, in the repository.
- Committing: the maintainer reviews and commits.
