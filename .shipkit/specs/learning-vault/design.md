# Design: Learning vault

## Approach

A script does every write: no model step, and no change to any existing skill's text. Sprint 1
has five parts.

1. **A settings file of its own.** `learningWithBodhi/.bodhi-notes.json`, beside
   `.bodhi-profile.json`, is written only by four new `bodhi-state` commands. Its absence means
   "never offered, no choice", which is every learner on release 1.26.1.
2. **A syllabus renderer in `bodhi-state`.** `syllabus --markdown` prints the text of
   `Syllabus.md` from the same data the existing `syllabus` JSON carries, in the words of
   `skills/progress/references/module-row.md`.
3. **A sync command.** `notes-sync` writes `Syllabus.md` into the course folder and copies it,
   the revision sheets and `Courses.md` into the vault's `Learn with Bodhi/` home. Every write
   is atomic and happens only when the content changed.
4. **The Stop hook drives it.** `scripts/bodhi-stop-hook.py` already knows when this session
   ran `touch-state` on a course and whether today's revision sheet exists. When it has
   nothing to block for, it runs `notes-sync` for each course the session closed. It decides
   whether this is the moment for the one-time offer, and it tells the learner the offer or a
   failed copy through `systemMessage`.
5. **A new skill, `/bodhikit:notes-setup`.** It holds the conversation (which app, what
   leaves the computer, agree) and calls `notes-set`. The question, the list of apps and the
   description of the file live in this skill's own budget.

Sprint 2 (claude.ai chats, connector apps) is designed when its probes have run. Nothing below
commits it to a shape, except that the supported-apps list (REQ-29) is a table the sprint
extends.

---

## Decision: the feature freeze is lifted for this spec only   (→ every REQ)

**Context.** `CLAUDE.md` *Feature freeze* bars new skills and schema fields unless a second
real user asks or the maintainer hits the gap in a real session. Decision 0001 lifted it for
learn-anything only. This spec adds a skill, a settings file and five commands. The intake
recorded that building needs the freeze text changed first. The spec serves none of this
quarter's goals directly.

**Alternatives.**
1. A project-wide decision 0006 that admits this spec's sprint 1 only, with `CLAUDE.md`'s
   freeze section naming it beside 0001.
2. Lift the freeze entirely.
3. Keep the freeze and shelve the spec until a second learner asks.

**Case for 1.** It keeps the freeze's purpose, which is not to build for imagined users,
while admitting one bounded piece the maintainer judged useful. Naming sprint 1 only means
sprint 2 needs its own yes after its probes.

**Case against 1.** The freeze exists because one learner cannot validate features. This
lifts it on the maintainer's judgment, with no user asking, for a feature that serves no
current goal. That is the exception the freeze was written to prevent.

**Decision.** Option 1. Decision 0006 is written, and `CLAUDE.md` changed, as the first task.
**Falsifiability.** We would reverse this, and freeze the feature again with sprint 2 dropped,
if by 2027-03-31 neither the survey nor an issue shows a learner other than the maintainer
with notes turned on.
**Fired-if.** manual

## Decision: the setting lives in `.bodhi-notes.json`, not the profile   (→ REQ-4, REQ-7, REQ-10)

**Context.** The setting needs a home that `bodhi-state` writes and that is learner-wide, not
per course. `skills/state-schema/SKILL.md` is 18,419 bytes against an 18,432-byte budget. The
profile is read by every cross-project skill (`/mentor`, `/evaluate`, `/learn`). The owner
chose a separate file at the spec review (intake, answer 12).

**Alternatives.**
1. `learningWithBodhi/.bodhi-notes.json`, found the way `find_profile` finds the profile.
   Its fields are documented in `skills/notes-setup/references/notes-file.md`, and
   `CLAUDE.md`'s *Where things live* names that file.
2. A `notes` object in `.bodhi-profile.json`, documented in `state-schema`.
3. `~/.bodhikit/config.json`.

**Case for 1.** No routine skill pays to read it. Deleting it resets the feature. Its absence
is the 1.26.1 state, so `t_golden_code_path` cannot see it. It needs none of the schema
KB's budget.

**Case against 1.** It is a fifth tracking file whose shape lives outside `state-schema`,
against the `CLAUDE.md` rule that "schemas are pinned in `state-schema`". `verify` gains a
file to check. A learner with no profile (a course outside `learningWithBodhi/`, found
through `projectRoot`) has nowhere for it, so `notes-set` refuses there.

**Decision.** Option 1. `state-schema` is not edited, not even with a pointer line: REQ-11
leaves every existing `SKILL.md` unchanged. (The design approved on 2026-11-10 had a pointer
line; it was dropped while the tasks were written, because it broke REQ-11.)
**Falsifiability.** We would reverse this, and move the setting into a profile `preferences`
object, if a second learner-wide setting is specified.
**Fired-if.** manual

## Decision: the Stop hook performs the session-close writes   (→ REQ-11, REQ-12, REQ-20–22, REQ-26)

**Context.** REQ-11 forbids changing any existing skill's text, and `CLAUDE.md` says
executor-discipline gaps are fixed in the script, not with louder prose. The hook already
finds session close: it blocks until today's revision sheet exists, so a Stop it does not
block, after this session's `touch-state`, is a session close. `hooks.json` gives it 30
seconds, of which the project search may take 8.

**Alternatives.**
1. The Stop hook runs `bodhi-state notes-sync` itself when it has no reason to block.
2. The Stop hook blocks once and tells the model to run `notes-sync`.
3. The five closing skills (`reflect`, `continue`, `teach`, `quiz`, `practice`) run
   `notes-sync` after the revision sheet.

**Case for 1.** It is deterministic, costs no model turn and no context, and changes no skill.
It reuses the hook's existing knowledge of which courses this session closed.

**Case against 1.** The hook stops being read-only. It now writes into a folder outside the
learning folder, in a process the learner never sees, and a bug there writes where the
learner keeps their own notes. It runs at every Stop after `touch-state`, so it must be cheap
when nothing changed. Where hooks do not run (Codex without trust), nothing happens unless
the runtime adapter states the step (REQ-36). Option 3 would put a line in `/teach`, which
has 380 bytes left.

**Decision.** Option 1. `notes-sync` writes through a temp file and `os.replace`, writes
nothing when the content is unchanged, and refuses any path that resolves outside the home
(REQ-24).
**Falsifiability.** We would reverse this, and move to option 2, if `notes-sync` on the
largest test fixture with notes on takes more than 5 seconds.
**Fired-if.** manual

## Decision: the hook speaks through `systemMessage`, not a block   (→ REQ-8, REQ-9, REQ-26, REQ-27)

**Context.** The hook must tell the learner two things: the one-time offer, and a copy that
failed. Claude Code's hooks reference (code.claude.com/docs/en/hooks.md, read 2026-11-10)
lists `systemMessage` as a "Warning message shown to the user". `decision: "block"` "prevents
Claude from stopping" and its `reason` "tells Claude why it should continue". The reference
does not say whether the model sees a Stop hook's `systemMessage`, or where the terminal
shows it. Codex's handling of it is not verified.

**Alternatives.**
1. `systemMessage` with fixed text from the script.
2. `decision: "block"`, with a reason telling the model to make the offer or report the
   failure in its own words.

**Case for 1.** The text is fixed, so a test checks the offer's wording and its name check
(REQ-16's `assert_no_internal_names`). It costs no turn. It cannot interrupt a question the
tutor just asked. A block makes the model speak after its own closing line, and blocking a
stop for a message is what the 1.18.1 fix stopped the hook doing.

**Case against 1.** The voice is the plugin's, not the tutor's. If the model does not see the
message, a learner who answers "yes" to it confuses the tutor, so the offer must name the
command to type rather than ask a question. Where it appears in the terminal is
undocumented, and in Codex it may not appear at all.

**Decision.** Option 1. The offer reads as a statement that ends with
`/bodhikit:notes-setup`, never as a question. A copy that succeeded is announced only the
first time a course reaches the home; later successes are silent. A failure is always
reported.
**Falsifiability.** We would reverse this, for the host concerned, if the hand check finds
that a Stop hook's `systemMessage` is not shown in the Claude Code terminal, or is not shown
in Codex.
**Fired-if.** manual

## Decision: the offer's moments are read from the transcript   (→ REQ-8, REQ-9, REQ-10, REQ-38)

**Context.** The hook must tell three things apart: a session where `/learn` registered a
new course, a session that began with `/continue`, and any other session. `session_writes`
already parses the transcript's Bash tool calls. A typed command appears as a user message
holding `<command-name>/bodhikit:continue</command-name>`, as seen in an eval transcript on
2026-11-10. The hooks reference documents no such marker. A model-chained `/continue` appears
as a `Skill` tool call.

**Alternatives.**
1. Parse the transcript: `profile-add-project` plus `touch-state` in Bash calls means `/learn`
   gave its first step. A `/bodhikit:continue` command-name or `Skill` call, plus `touch-state`
   and today's sheet, means a `/continue` session closed.
2. A `UserPromptExpansion` hook writes a per-session mark when `/bodhikit:continue` or
   `/bodhikit:learn` is typed, and the Stop hook reads the mark.
3. Offer at the first session close of any kind, whatever command began it.

**Case for 1.** It reuses the parser the hook already trusts. It needs no new hook event
locally, where today's `UserPromptExpansion` deliberately does nothing. It catches both
typed and chained commands.

**Case against 1.** The command-name marker is undocumented and could change without notice,
silently stopping the `/continue` offer. Codex's hook adapter keeps only tool calls, so in
Codex a typed `/continue` is invisible and only the `/learn` moment works there. Option 3 is
simpler, and the owner's two moments differ from it only in excluding a session begun with
`/teach` or `/quiz`.

**Decision.** Option 1. A test fixture holds both forms. In a cloud chat (the
`/mnt/user-data` marker the session-context hook uses), sprint 1 makes no offer and no copy.
**Falsifiability.** We would reverse this, and move to option 2, if a live `/continue` eval
transcript on a new Claude Code release no longer carries the `<command-name>` marker.
**Fired-if.** manual

## Decision: `bodhi-state` holds its own copy of the module-row words   (→ REQ-13, REQ-14, REQ-17, REQ-19)

**Context.** `/progress` and `/plan view` render the `syllabus` JSON in model prose from the
tables in `skills/progress/references/module-row.md`. REQ-17 needs the same words produced
byte-for-byte by the script.

**Alternatives.**
1. Python tables in `bodhi-state` that mirror module-row.md, with a test that fails when a
   phrase in one is missing from the other.
2. Generate module-row.md's tables from the Python, so there is one source.
3. Have the model render `Syllabus.md` from the JSON, as `/progress` does.

**Case for 1.** `/progress` stays exactly as it is for every learner. The test turns drift into
a failing check.

**Case against 1.** The words live in two places. A change to module-row.md now needs a
matching edit in the script, and the test checks the phrases, not the layout. Option 3 breaks
REQ-17. Option 2 changes a file `/progress` loads, which is a change for code learners
(REQ-7) and a larger refactor than this spec.

**Decision.** Option 1.
**Falsifiability.** We would reverse this, and move to option 2, if the drift test fails on
two separate commits.
**Fired-if.** manual

---

## Data / interface changes

**`learningWithBodhi/.bodhi-notes.json`** (→ REQ-4, REQ-10), version 1:

```json
{ "version": 1,
  "choice": "vault | files | off | null",
  "app": "obsidian | null",
  "location": "/absolute/path/to/vault | null",
  "agreedOn": "YYYY-MM-DD | null",
  "offerMadeOn": "YYYY-MM-DD | null",
  "announced": ["<course name>"] }
```

`announced` lists the courses whose first arrival in the home has been reported (Decision:
`systemMessage`). `verify` checks the file when it exists. Every reader handles any file that
`verify` passes (`t_verify_implies_readers`).

**New `bodhi-state` commands.**

- `notes-show` (read-only): the file, or its defaults when there is none, plus
  `appsOffered` for this host and the home path. The skill reads it for REQ-1, REQ-2 and REQ-5.
  `appsOffered` comes from a table `NOTES_APPS` keyed by host kind. The host kinds are
  `local` (a host that keeps the learner's folder: no `/mnt/user-data` marker, per the
  session-context hook's test) and `cloud-chat` (the marker is present). Sprint 2 adds kinds
  for connector hosts. In sprint 1, `local` offers `obsidian`, and `cloud-chat` offers
  nothing. Each entry carries `carriedBy`: `script` or `model`. (→ REQ-1, REQ-2, REQ-29)

  **The REQ-29 test.** For every entry whose `carriedBy` is `model`, the test looks for a row
  in a *Results* table with the columns of `docs/no-computer-probe.md` (*Date, Probe, Host,
  plan and how BodhiKit was loaded, BodhiKit, Checks, Notes*). The row must meet three
  conditions: its *Probe* cell is `D` or `vault`, its *Host…* cell contains the entry's host
  name, and its *Notes* cell contains the app's name. Its *Checks* cell must read `1 PASS`,
  `2 PASS` and `3 PASS`. The claude.ai vault check that sprint 2 adds to
  `docs/cowork-probe.md` gets its own *Results* table in those columns, because that file's
  existing table has a different shape. In sprint 1 no entry is `model`, so the test also
  runs on a synthetic table with one `model` entry and no matching row, and must fail there.
- `notes-set --choice vault --app obsidian --location <dir> | --choice files | --choice off`.
  It refuses a location that does not exist, lies inside the profile's folder, or holds it
  (REQ-37), and refuses where no profile is found. On `vault` it creates the home, writes and
  removes a test file there, and then runs a full sync of every course in the profile, active
  or completed (REQ-23). On `files` it writes every course's `Syllabus.md`. On `off` it only
  records the choice (REQ-6). (→ REQ-4, REQ-6, REQ-23, REQ-37)
- `notes-offered`: sets `offerMadeOn` if it is null. Idempotent. (→ REQ-10)
- `notes-sync --project <p> [--all]`: does nothing unless the choice is `vault` or `files`.
  Otherwise it writes the course's `Syllabus.md` (REQ-12), and on `vault` copies it, the
  revision sheets by REQ-21's rule, and `Courses.md` (REQ-20–22). It prints
  `{written, unchanged, failed:[{path, why}], firstArrival}`. A failure for one file does not
  stop the others, and the command exits 0 so the hook never traps a session. (→ REQ-12,
  REQ-20–27)
- `syllabus --markdown`: prints the `Syllabus.md` text. Without the flag, `syllabus` prints
  the JSON it prints today, so the golden replay is unchanged. (→ REQ-13–19)

**`Syllabus.md`** (→ REQ-13–19). In order:

1. A header saying BodhiKit rewrites the file each session and the learner's notes belong in
   `notes/`.
2. `## Due in the next seven days`: one line per review, earliest first, in the form
   `- <YYYY-MM-DD> — <concept> (<module>)`. A review due today or earlier reads
   `- due now — <concept> (<module>)` and sorts first. With none, the section says
   `Nothing due this week.`
3. One section per plan module, then each unplanned module: status, position, planned
   concepts and key terms, all in module-row words.
4. Under each module, its tracked concepts with their outcome clause and next date (or
   "parked"), and "by your account" where `solidBasis` says so.

Dates are ISO. The text depends only on the tracking files and today's date.

**The vault** (→ REQ-20–24). Under `<vault>/Learn with Bodhi/`:

- `Courses.md`, with one Markdown link per course folder, `[<course>](<course>/Syllabus.md)`,
  path percent-encoded.
- `<course>/Syllabus.md`.
- `<course>/revision/<sheet>.md`.

Nothing else is written. Every path is resolved and checked to lie under the home before it
is written.

**`scripts/bodhi-stop-hook.py`** (→ REQ-8, REQ-9, REQ-12, REQ-20–22, REQ-26). After its
current checks, and only when it is not blocking:

1. For each course this session ran `touch-state` on, it runs `notes-sync`.
2. If `offerMadeOn` is null, no choice is recorded, and the transcript shows either moment
   (Decision: transcript), it runs `notes-offered` and adds the offer to `systemMessage`.
3. It adds any `failed` entry, and any `firstArrival`, to `systemMessage`.

With no `.bodhi-notes.json` and neither moment, its output is exactly today's (REQ-7). It does
nothing new in a cloud chat in sprint 1.

**`skills/notes-setup/SKILL.md`** (→ REQ-1–6, REQ-37). It opens with the "Knowledge bases are
skills" sentence and references `teaching-personality` for voice. It reads `notes-show`, asks
the app question with the options it lists, gives REQ-3's explanation, records through
`notes-set`, and reports what `notes-set` printed. A `**Fallback:**` paragraph covers
`bodhi-state` being unavailable: it records nothing and says notes need the script.
Learner-facing text names no command, key or box.

**Packages and documents** (→ REQ-33–36). The OpenAI and Cowork builds pick the skill up from
`skills/`. The OpenAI adapter's *Close a study session without a Stop hook* gains two steps
for local state mode: run `notes-sync` and report a failure; then, if `notes-show` reports no
choice and no `offerMadeOn`, and this was `/learn`'s first step or a `/continue` session, make
the offer in the same words and run `notes-offered`. Conversation-only mode does neither
(REQ-38).

**How each host meets REQ-38.** The rule is that the offer is never made where nothing can
record it.
- ChatGPT in conversation-only mode runs neither the hook nor `bodhi-state`, so nothing can
  make the offer except the adapter. The adapter's text says conversation-only mode makes no
  offer, and a check on the built adapter tests that text.
- A cloud chat runs the hook, which sees the `/mnt/user-data` marker and makes no offer. A
  hook test covers this.
- Codex without trusted hooks is in local state mode, so it keeps the learner's folder, and
  the adapter's step makes the offer there. The counts move to 19 skills in the files REQ-34
names. `PRIVACY.md` gains the REQ-33 paragraph.
