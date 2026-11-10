# Intake: Learning vault

> Intake taken on 2026-11-10.

## Request
Ask the learner first which notes application they use. If they use none, suggest the app
BodhiKit can put notes into most easily. Copy their notes there, and add a syllabus of each
course as well, arranged and categorised under the course name, so the learner has "a perfect
place to find and revise their knowledge". Disk stays the main place; the notes app is a copy.
Give a command, "something like /bodhikit:notes-setup", so a learner who does not use it now
can start later. "We are just creating a sprint plan for notes taking right now - no
implementation."

## Serves goal
None directly (answered 2026-11-10): "this is something I thought will be helpful for
learners". The nearest goal, "Outside learners on non-code subjects", gains little until
sprint 2.

## Conflicts found
- **Feature freeze, `CLAUDE.md` *Feature freeze*.** It bars new skills and schema fields, and
  this adds a command and a learner setting; decision 0001 does not admit it. **Decided:** "we
  can safely ignore this for now", because this work is a plan with no implementation. No
  decision record is written now. Building it needs the freeze text changed first, so the plan
  carries that as its first task.
- **Privacy, `PRIVACY.md:6-7`, `:16-17`, `:29`.** "The plugin does not send learner data
  anywhere" and "does not require network access" would be untrue once notes go to an app
  through a connector. **Decided:** the text will say that BodhiKit sends notes only with the
  learner's permission, only to the notes app the learner chose, that the feature is optional,
  and that nothing breaks for a learner who does not use it.
- **Code unchanged, `.shipkit/product.md` non-goal and learn-anything REQ-1.** A question
  inside `/learn` changes `/learn` on a code topic. **Decided:** `/learn` is not edited; "we
  can add a hook or use something else to do this instead of /learn".
- **`notes/` is the learner's, `rules/learning-project.md:23`** ("Do not modify unless
  asked"). **Decided:** the syllabus lives at the course's root folder, not in `notes/`.
- **Lint budget, `dev/check.sh:227-235`.** `state-schema` has 13 bytes of headroom, `state-ops`
  6 and `/learn` 152. **Decided:** the question, the list of apps and the setting's
  description live in the new skill, which has its own budget. Where the setting is stored,
  given that `state-schema` has no room for a new field, is a design decision for the spec.
- No open spec overlaps (`explain-with-a-picture` changes only how `/teach` explains), and no
  decision record is contradicted (read: 0001 to 0005).

## Answers
1. *Go ahead despite the freeze and the privacy text?* — Yes, as decided above.
2. *Which quarterly goal does this serve?* — None directly; "helpful for learners"
   (2026-11-10).
3. *Where do the notes live?* — In the learner's own vault: "we create a folder or new page or
   whatever applicable with name - Learn with bodhi". The syllabus also sits at the course's
   root folder on disk.
4. *What does the syllabus show?* — "The plan plus where you stand and when reviews are due,
   refreshed each session."
5. *When is the learner asked?* — Once at the end of `/learn`, and once at the next
   `/continue` for a learner who already has projects: yes. Read together with the code
   conflict above: the asking is delivered by a hook or the new skill, at those two moments,
   and `/learn`'s own text does not change.
6. *The connector phase waits for probe D* (`docs/no-computer-probe.md`). — "Okay."
7. *On a host with no disk, only the chat summary is copied, never a schedule.* — Not
   accepted as final: "any way we can do a schedule as well somehow using the note taking app
   or something else". Open; see *Out of scope*.

Answered 2026-11-10, at the spec review:

8. *The syllabus appears only after a learner opts in, and "files only" is a choice?* — Yes.
9. *Code learners see the one-time offer too?* — Yes; REQ-8 to REQ-10 stand.
10. *A claude.ai chat moves to sprint 2, after a vault check in the cowork probe?* — Yes.
11. *In the vault, today's revision sheet is replaced at each close and an earlier day's is
    never touched again?* — Yes.
12. *The setting lives in its own file, `learningWithBodhi/.bodhi-notes.json`, written only by
    `bodhi-state`?* — Yes; it is the first decision record in `design.md`.
13. *The spec's `Paths` line?* — Yes, as written.
14. *Commit the intake and spec once the requirements are approved, leaving `handoff.md`
    out?* — Yes.

## Assumptions made
- Disk is the record and the notes app holds a copy. Nothing is read back from the notes app
  into the tracking files (the maintainer's "disk is our main place", 2026-11-10).
- The setting is written by a `bodhi-state` command, never by hand (`CLAUDE.md`, *The
  deterministic state layer*).
- Notes and the syllabus use outcome words and never a level or box number (`CLAUDE.md`,
  *Authoring contract*; decision 0005).
- A failed copy never blocks a session, and the tutor never says a note was saved unless the
  write succeeded (probe D, check 3).
- Apps offered, by what was verified on 2026-11-10: Obsidian (a vault is a folder of Markdown
  files, obsidian.md/help), Notion (Notion MCP creates and edits pages,
  developers.notion.com/docs/mcp), Google Drive on Claude (the connector creates files,
  claude.com/docs/connectors/google/drive). What ChatGPT can write to Notion or Drive is not
  verified. Logseq and Joplin are not verified. OneNote, Apple Notes and Evernote are not
  offered.
- A Claude chat reaches only the folders the learner allowed, so a copy into a vault outside
  `learningWithBodhi` needs that folder allowed too (`docs/cowork-probe.md`, *Set up*).
- The revision sheets copied are the ones the closing skill already writes
  (`skills/reflect/references/revision-sheet.md`); their content does not change.

## Out of scope
- Any implementation. This is a plan.
- The notes app as the record, or anything read back from it into tracking files.
- A review schedule on a host with no disk. It depends on probes B, C and D check 4: a real
  schedule needs the script to run and somewhere to keep its files. Until they are run, the
  plan may put engine-computed review dates into the vault only where a disk exists.
- OneNote, Apple Notes, Evernote, audio notes, and two-way sync.
