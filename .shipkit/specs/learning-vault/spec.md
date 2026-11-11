# Spec: Learning vault

> Spec accepted at commit `30e6b6d` on learning-vault (the maintainer approved the requirements on 2026-11-10).
> Status: shipped
> Paths: skills/notes-setup/, scripts/, hooks/, platforms/, dev/, docs/, README.md, GUIDE.md, PRIVACY.md, CLAUDE.md, CHANGELOG.md, .claude-plugin/

## Purpose
A learner's revision sheets and course plan live in a folder most learners never open again.
This spec gives each learner one place to find and revise what they studied, inside the notes
app they already use: a syllabus per course that shows the plan, where they stand and when
reviews are due, and the revision sheets beside it, all under one "Learn with Bodhi" home
arranged by course. It is optional and off until the learner turns it on. Disk stays the
record; the notes app holds a copy, and nothing is ever read back from it.

Serves none of this quarter's goals directly. The maintainer's reason (2026-11-10): it will be
helpful for learners. The nearest goal, *Outside learners on non-code subjects*, gains little
until sprint 2 reaches the hosts non-programmers use.

This is a plan. Nothing is built until the spec, the design and the tasks are accepted.

**Two sprints.** Sprint 1 needs no connector and no model step: on a host where `bodhi-state`
runs on the learner's own disk (Claude Code, and Codex with its hooks trusted), the setting,
the one-time offer, the syllabus file, and the copy into a vault that is a folder on the
learner's computer (Obsidian). This spec is sprint 1. Sprint 2 adds the hosts where the model
must carry the files: a claude.ai chat reaching the learner's folder through Claude Desktop,
and apps reached through a connector (Notion, Google Drive). It gets its own spec, started
only after the probe for each app and host has been run and recorded (probe D in
`docs/no-computer-probe.md` for connectors; a vault check added to `docs/cowork-probe.md` for
a claude.ai chat). See *Sprint 2* below.

**Words used here.**
- *Notes choice*: what the learner told BodhiKit about notes. One of: an app with its
  location, "files only" (the syllabus on disk and no copy), or "off". "I use no notes app"
  is an answer to the first question, not a choice (REQ-2).
- *Course*: one learning project, a folder under `learningWithBodhi/`. Its *course name* is
  that folder's name.
- *A host that keeps the learner's folder*: one where `bodhi-state` reads and writes the
  learner's `learningWithBodhi/` folder directly: Claude Code, and Codex in local state mode.
  A claude.ai chat reaches that folder only through Claude Desktop, and counts as such a host
  only from sprint 2. ChatGPT in conversation-only mode never does.
- *Vault*: the learner's notes store. For Obsidian it is a folder on their computer.
- *Home*: the folder or page named `Learn with Bodhi` that BodhiKit creates in the vault.
- *Session close*: the end of the first turn after this session has run `touch-state` on a
  course and that course's revision sheet for today exists. This is the moment the Stop hook
  already checks for the revision sheet. It can happen more than once in a day.
- *The offer*: one or two sentences telling the learner that `/bodhikit:notes-setup` can keep
  a syllabus and their revision sheets in their notes app.

## User stories
- As a learner who keeps notes in Obsidian, I want my syllabus and revision sheets to appear
  there under the course's name, so that I revise where I already work.
- As a learner who uses no notes app, I want BodhiKit to suggest one and set it up with me,
  so that I do not have to choose alone.
- As a learner who said no at first, I want one command to turn this on later, so that the
  choice is never final.
- As a learner studying code today, I want nothing to change unless I turn this on, so that
  what I rely on stays as it is.
- As any learner, I want to be told what leaves my computer and to agree first, so that my
  notes go only where I chose.

## Requirements (EARS)

### Choosing, changing and turning off (sprint 1)
- **REQ-1.** When the learner runs `/bodhikit:notes-setup` and no notes choice is recorded,
  the plugin shall ask which notes app they use, offering each app supported on the current
  host (REQ-29), "I use none", and "just keep the syllabus in my course folder" (files only).
- **REQ-2.** If the learner answers that they use no notes app, then `/bodhikit:notes-setup`
  shall suggest exactly one app and say why: Obsidian where the host keeps the learner's
  folder; otherwise the first app supported on this host (REQ-29); and where no app is
  supported, it shall say that notes cannot be kept on this host yet and record nothing.
- **REQ-3.** Before a notes choice is recorded, `/bodhikit:notes-setup` shall tell the learner
  in plain words what will be copied, where it will go, that a vault their notes app syncs
  carries the copy wherever the app syncs it, that it is optional and that it can be turned
  off, and shall record the choice only after the learner agrees.
- **REQ-4.** When the learner agrees to a notes choice, `bodhi-state` shall record the choice,
  the app and its location where there is one, and the date of the agreement.
- **REQ-5.** When the learner runs `/bodhikit:notes-setup` while a notes choice is recorded,
  the plugin shall show the current choice and let the learner change it or turn it off.
- **REQ-6.** When the learner turns the notes choice off, the plugin shall stop writing the
  syllabus and the copies, shall delete nothing it wrote before, and shall tell the learner
  that those files stay where they are and will no longer be refreshed.
- **REQ-7.** While no notes choice is recorded, the plugin shall write no `Syllabus.md` and
  nothing outside the files release 1.26.1 writes, apart from the record that the offer was
  made (REQ-10); every existing `bodhi-state` command shall print and write what 1.26.1 does
  (`t_golden_code_path` unchanged), and the Stop hook shall block for no reason 1.26.1 does
  not block for.
- **REQ-37.** If the vault folder the learner names does not exist, lies inside
  `learningWithBodhi/`, or holds `learningWithBodhi/`, then `/bodhikit:notes-setup` shall say
  why it cannot be used and shall not record it. (A vault holding `learningWithBodhi/` already
  shows the files; "files only" is suggested instead.)

### The one-time offer (sprint 1)
- **REQ-8.** When a session that registered a new course with `/learn` reaches session close,
  or the end of the turn that gave its first step, while no notes choice is recorded and the
  offer has never been made to this learner, the plugin shall make the offer once, at the end
  of that turn.
- **REQ-9.** When a session that began with `/continue` on an existing course reaches session
  close, while no notes choice is recorded and the offer has never been made to this learner,
  the plugin shall make the offer once, at the end of that turn.
- **REQ-10.** When the offer is made, `bodhi-state` shall record that it was made, and the
  plugin shall not make it again, whatever the learner answered or if they ignored it.
- **REQ-11.** The offer and the session-close writes shall reach the learner with no change
  to the text of any existing `SKILL.md`.
- **REQ-38.** Where the host keeps no learner folder, the plugin shall not make the offer.

### The syllabus (sprint 1)
- **REQ-12.** While a notes choice other than "off" is recorded, at session close the plugin
  shall write `Syllabus.md` in the root folder of each course the session closed.
- **REQ-13.** `Syllabus.md` shall list every module of the plan in order, then every tracked
  module the plan does not declare, each with its name, its status, its planned concepts and
  its key terms, using the same words `/progress` uses for the same row
  (`skills/progress/references/module-row.md`).
- **REQ-14.** `Syllabus.md` shall show, under its module, every concept with a review on
  record: where the learner stands as an outcome clause, and the date of its next review, or
  "parked" for a parked concept.
- **REQ-15.** `Syllabus.md` shall list at its top every review due on or before the date seven
  days after today, earliest first, with any review due today or earlier shown as due now.
- **REQ-16.** `Syllabus.md` shall pass the name check the transcript scenarios use
  (`assert_no_internal_names`) and shall contain no Bloom number and no box number.
- **REQ-17.** `bodhi-state` shall produce the whole text of `Syllabus.md` from the tracking
  files, so that two runs on the same files on the same day give the same bytes.
- **REQ-18.** `Syllabus.md` shall say, before its first `##` heading, that BodhiKit rewrites it
  at each session and that the learner's own notes belong in `notes/`.
- **REQ-19.** Where a module's or a concept's *Solid* rests on practice the learner reported,
  `Syllabus.md` shall say "by your account" beside it, as `/progress` does.

### The copy into a vault that is a folder (sprint 1)
- **REQ-20.** While the notes choice names a vault folder, at session close the plugin shall
  copy the course's `Syllabus.md` to `<vault>/Learn with Bodhi/<course name>/Syllabus.md`.
- **REQ-21.** While the notes choice names a vault folder, at session close the plugin shall
  copy each of the course's revision sheets into
  `<vault>/Learn with Bodhi/<course name>/revision/` as follows: a sheet the home does not
  hold is copied; today's sheet is replaced with the disk's version; a sheet from an earlier
  day that the home already holds is never touched again.
- **REQ-22.** While the notes choice names a vault folder, at session close the plugin shall
  write `<vault>/Learn with Bodhi/Courses.md`, listing every course folder in the home with a
  link to its syllabus.
- **REQ-23.** When a notes choice naming a vault folder is recorded, first or changed, the
  plugin shall write the syllabus of every course in the learner's profile, active or
  completed, and copy it and every existing revision sheet into the home.
- **REQ-24.** The plugin shall write, change or delete no file in the vault outside
  `Learn with Bodhi/`, and shall write a file in the home only when its content differs from
  what is there.
- **REQ-25.** The plugin shall read nothing from the vault into a tracking file.
- **REQ-26.** If a copy cannot be written, then the session shall still close, and the plugin
  shall tell the learner that the copy did not happen and why.
- **REQ-27.** The plugin shall tell the learner that a note was saved to the vault only after
  the write succeeded.

### Which apps are offered on which host (sprint 1)
- **REQ-29.** `/bodhikit:notes-setup` shall offer an app on a host only where the plugin's own
  list of supported apps names it for that host, and a test shall fail if an entry for a host
  where the model carries the files has no PASS recorded in `docs/no-computer-probe.md`
  (checks 1 to 3 of probe D) or `docs/cowork-probe.md` for that app on that host. (A folder
  vault on a host with the learner's folder rests on the Obsidian hand check in *Release
  steps*.)

### Privacy, hosts and documents
- **REQ-33.** `PRIVACY.md` shall say that BodhiKit copies notes only with the learner's
  permission and only to the place the learner chose; that the place is a folder on their
  computer, which their notes app may sync elsewhere; that the feature is optional; and that
  nothing breaks for a learner who does not use it. [untested: prose, verified by reading]
- **REQ-34.** The README, `GUIDE.md`, `marketplace.json`, `docs/openai.md`,
  `dev/guide-writer/references/commands.md` and `dev/eval/test_openai_plugin.py` shall list
  `/bodhikit:notes-setup` and count 19 skills. Dated records of past runs
  (`docs/openai-submission.md`) are not changed.
- **REQ-35.** The OpenAI package and the Cowork package built from this tree shall carry
  `/bodhikit:notes-setup` and a `scripts/bodhi-state` that has the `notes-show`, `notes-set`,
  `notes-offered` and `notes-sync` commands and the `syllabus --markdown` option.
- **REQ-36.** Where the host runs no hooks, the runtime adapter shall state the one-time offer
  and the session-close writes as explicit steps.

## Sprint 2 (to be specified after the probes)
Not requirements of this spec. They were REQ-28, REQ-30, REQ-31 and REQ-32 in the draft
approved on 2026-11-10, and were moved here because they cannot be designed or tested before
probe D and the claude.ai vault check are recorded. Those numbers are retired, not reused.
Sprint 2 gets its own spec, which starts from these notes:
- In a claude.ai chat, if the vault folder is not one the learner has allowed Claude Desktop
  to reach, `/bodhikit:notes-setup` says which folder to allow, and records the choice only
  after a test file was written there and removed. (Was REQ-28.)
- While the notes choice names a connector app, at session close the course's syllabus page
  under `Learn with Bodhi / <course name>` is created or replaced, and the day's revision
  sheet is added as a page beside it. (Was REQ-30.)
- If the connector is not available in the chat at session close, the learner is told the
  notes were not saved to the app, and the files on disk stay the place to find them. (Was
  REQ-31.)
- Where the host keeps no learner folder, only the closing summary note is copied to the app,
  and no review date is written that `bodhi-state` did not compute. (Was REQ-32.)

## Out of scope
- The notes app as the record, two-way sync, or anything read back from a note.
- A review schedule on a host that keeps no learner folder. It waits on probes B, C and D
  check 4.
- OneNote, Apple Notes, Evernote, Logseq and Joplin. Logseq and Joplin may follow once their
  storage is verified at their own documentation.
- Creating the vault itself, or an Obsidian plugin.
- Reminders pushed to a phone or a calendar. The syllabus shows the dates; nothing notifies.
- Changing what a revision sheet contains.
- Any change to how a concept is taught, graded, scheduled or tracked, on any evidence kind.

## Release steps (not requirements)
- Rewrite the feature-freeze section of `CLAUDE.md` to admit this spec before the first change
  lands (intake, *Conflicts found*).
- Open a test vault in Obsidian by hand: the home appears, `Courses.md` opens each syllabus,
  and a revision sheet reads as on disk. Record it in `dev/eval/README.md`.
- Run probe D for each connector app on each host, and the vault check in
  `docs/cowork-probe.md`, before sprint 2 starts, and record them.
- Per release: `dev/check.sh`, with `t_golden_code_path` passing, and the code eval groups at
  their recorded levels. Rebuild and re-upload the ChatGPT package (CLAUDE.md, *Release
  checklist* step 7).
