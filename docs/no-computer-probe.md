# No-computer probe — can a learner keep a schedule without a laptop open?

Tracked study needs a computer today: Claude Code, Codex, or a Claude chat
with Claude Desktop connected (`docs/cowork-probe.md`). On a phone, on
claude.ai with no computer, and in ChatGPT, BodhiKit teaches and keeps
nothing (`docs/hosts-without-files.md`, `docs/openai.md` *Runtime behavior by
platform*). `.shipkit/product.md` lists saved state there under *Later*,
"after a research spike on keeping state between chats". This is that spike.

It asks four questions, cheapest first. Each can be answered by hand in
under an hour, and none needs a change to the plugin.

- **A. Phone to laptop.** Can a phone chat run tracked study through a
  computer that is on at home?
- **B. A carried file on Claude.** With no computer connected, can the chat
  run `bodhi-state` on a learning folder the learner uploads, and hand the
  updated folder back?
- **C. A carried file on ChatGPT.** The same, in ChatGPT.
- **D. A notes app or a cloud drive.** Can a chat write a note into the app
  the learner already uses, and can a drive carry the folder so nobody
  uploads and downloads by hand?

B and C keep the design BodhiKit already has: the same script writes the
same files, and the learner owns them. Only how the files reach the chat is
new. Nothing here stores a learner's record on a server, and nothing relies
on the host's own memory to hold a schedule.

**Make no claim about any of this — README, listing, guide — until its
checks read PASS below.** There is no headless runner for these hosts, so
every run is by hand. The runs use claude.ai and ChatGPT usage, not the eval
harness.

## What is already known

- A Claude chat runs in a cloud sandbox with a shell, and an installed
  plugin is synced into it. Measured with a computer connected
  (`docs/cowork-probe.md`, *Where things run*, 2026-10-22). Not measured with
  no computer connected, and not on a phone.
- A phone "can reach the computer's files only while the Desktop app is open
  on that machine" (Anthropic's article 15520349, as recorded in
  `dev/guide-writer/references/platform-facts.md`). Whether a phone chat can
  tick the computer under Devices and run BodhiKit tracked is untested.
- A running Claude Desktop counts as connected even with nothing ticked
  (`docs/hosts-without-files.md`, 2026-10-22). For B, quit it first.
- Notion's developer docs say Notion MCP lets an assistant "search your
  workspace, create and edit pages, and manage databases", and name Claude,
  ChatGPT and Gemini as clients (developers.notion.com/docs/mcp, read
  2026-11-10). Claude's docs say its Google Drive connector can "search your
  Google Drive, read the files it finds, and create new files there"
  (claude.com/docs/connectors/google/drive, read 2026-11-10). They list the
  document types it reads and do not say it can update a file or read a zip.
  What ChatGPT can write to Notion or Drive is not verified: OpenAI's help
  pages refused the fetch.
- ChatGPT runs BodhiKit conversation-only unless it exposes a shell and a
  writable folder (`platforms/openai/bodhikit/references/openai-runtime.md`).
  Whether a chat on the web or the phone exposes either is untested.

## Set up

Use a fixture, never real learner data.

```bash
mkdir -p ~/no-computer-probe
cp -R dev/eval/fixtures/performed-project ~/no-computer-probe/learningWithBodhi
cd ~/no-computer-probe && zip -r bodhi-bundle.zip learningWithBodhi
cp bodhi-bundle.zip bodhi-bundle-original.zip
```

The cooking project in it has two concepts due, Emulsions and Knife grip.
Both are performed skills, so a quiz offers a practice rep first: say you
have not practised since last time, and answer the knowledge question. Put
`bodhi-bundle.zip` where the phone can reach it (the phone's Files app or a
cloud drive) for the phone checks. Note the BodhiKit version each host has
installed.

## A. Phone to laptop

Claude Desktop open on the computer, with `~/no-computer-probe/learningWithBodhi`
as the folder to allow. Use the Claude phone app, on mobile data if you can,
so the phone and the computer are on different networks.

1. **The phone sees the computer.** In a new chat on the phone, look for
   + → Devices and tick the computer. PASS: it can be ticked. FAIL: no
   Devices entry, or the computer is not listed.
2. **A tracked review reaches the computer.** Run `/bodhikit:quiz current`,
   answer one question and let it finish. On the computer, run
   `scripts/bodhi-state --project ~/no-computer-probe/learningWithBodhi/cooking verify`
   from this repo. PASS: `"ok": true`, and today's `reviewHistory` entry has a
   `boxBefore` field. FAIL: nothing reached the computer, or the JSON was
   written by hand.
3. **It is honest when the computer is off.** Quit Claude Desktop. In a new
   phone chat, run `/bodhikit:continue`. PASS: it says once that it cannot
   keep the schedule here, and saves nothing. FAIL: it claims to have saved,
   or promises a review date.

## B. A carried file on Claude, no computer connected

Quit Claude Desktop. Run checks 1–6 on claude.ai in a browser, then repeat 2,
4 and 5 in the phone app.

1. **The sandbox can run the script.** Ask the chat to run
   `command -v python3 && python3 --version` and to print the path of the
   BodhiKit plugin's `scripts/bodhi-state`. PASS: Python 3.8 or later and a
   path that exists. FAIL: no shell, no Python, or no plugin files.
2. **An upload becomes a project.** Attach `bodhi-bundle.zip` and ask the
   chat to unpack it and run `bodhi-state --project <unpacked>/cooking verify`
   and `due`. PASS: `"ok": true`, with Emulsions and Knife grip listed as due. FAIL: the upload
   is refused, or the chat cannot read it.
3. **A real session writes to it.** Say: "This unpacked folder is my learning
   project. Run `/bodhikit:quiz current` on it." Answer the question and let
   it finish. Note whether the tutor took the folder as a project or said it
   cannot track here; the no-files reference was written for a chat with no
   folder at all. PASS: a review recorded through `bodhi-state`.
4. **The folder comes back.** Ask for the updated `learningWithBodhi` folder
   as one zip to download. Unpack it on the computer into a new folder and
   run `verify` from this repo. PASS: `"ok": true`, today's entry with
   `boxBefore`, and today's sheet under `revision/`. FAIL: no download, or a
   file missing or hand-written.
5. **The next chat picks it up.** In a new chat, attach the zip from check 4
   and run `/bodhikit:progress quick`. PASS: it shows the review from check 3.
6. **An old file.** In another new chat, attach `bodhi-bundle-original.zip`
   instead and run `/bodhikit:progress quick`. This is a finding, not a pass
   or fail: record whether anything tells the learner that this file is older
   than the one they last downloaded. A spec has to solve this.

## C. A carried file on ChatGPT

Run on the plan a new learner would have. Record which plan it was.

1. **The listing installs on that plan.** PASS: BodhiKit can be added.
2. **The state mode.** Call BodhiKit and ask which state mode it is in, and
   to run `python3 --version` and print the path of its packaged
   `scripts/bodhi-state`. PASS: a shell, Python 3.8 or later, and the script.
   FAIL: conversation-only, which ends this probe at "no".
3. **Checks B2 to B6,** in ChatGPT on the web, then B2, B4 and B5 in the phone
   app.

## D. A notes app or a cloud drive

Use a test Notion workspace or page and a test Drive folder, not the ones you
work in. Run each check on Claude with no computer connected, then in
ChatGPT. Record which connector was used and who publishes it.

1. **A note is written.** After a short untracked lesson, ask the chat to
   save its closing summary as a page under a parent page named
   `BodhiKit / Cooking` in Notion, and as a document in a Drive folder of the
   same name. PASS: the page or document exists with the summary's headings
   and its two self-test prompts. FAIL: no write tool, or the chat says it
   saved and nothing is there.
2. **It lands under the course.** Ask for a second note for the same course.
   PASS: it sits beside the first under the same parent. FAIL: a second
   parent is created, or the note lands at the top level.
3. **It says so when it cannot.** Disconnect the connector and ask again.
   PASS: the tutor says the note was not saved and offers it in the chat.
   FAIL: it claims the save.
4. **A drive carries the folder.** Only if B or C passed through check 5. Put
   `bodhi-bundle.zip` in the Drive folder and ask the chat to fetch it, run
   check B3 on it, and write the updated zip back to the same folder. PASS:
   the zip in Drive, unpacked on the computer, passes `verify` with today's
   entry. FAIL: the connector cannot read or write a zip. Record whether it
   replaced the file or made a second one.

Checks 1 to 3 are about notes, which are a copy. Check 4 is about the record
itself. A pass on 1 to 3 says nothing about 4.

## What the results decide

| Result | Next step |
|---|---|
| A passes | Documentation only: the README, the no-files reference and the guides say a phone works while the computer is on. No spec. |
| B or C passes through check 5 | A spec for carried state, with a decision record first, because the feature freeze does not admit it today. Check 6 is its first requirement. The engine's existing commands do not change, and `t_golden_code_path` holds. |
| D passes checks 1 to 3 on a host | The learning-vault spec may offer that app on that host. Where it fails, the spec offers the note in the chat and names no app. |
| D passes check 4 | The carried-state spec may use a drive in place of upload and download. Otherwise the learner carries the file by hand. |
| B and C fail at check 1 or 2 | Saved state with no computer stays under *Later*. The honest behaviour is the one shipped: teach, keep no schedule, hand over a summary. |

## Results

Record every run here, newest first: the date, the host and plan, the
BodhiKit version, and PASS or FAIL per check with one line of evidence.

| Date | Probe | Host, plan and how BodhiKit was loaded | BodhiKit | Checks | Notes |
|---|---|---|---|---|---|
