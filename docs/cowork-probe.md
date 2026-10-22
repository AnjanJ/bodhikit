# Cowork probe — does BodhiKit's tracked state work in Claude Cowork?

BodhiKit's promise rests on three things outside the skills' text: the
`bodhi-state` script runs (so every tracking write is deterministic), the
SessionStart hook injects the learning-project rule, and the Stop hook refuses
to end a studied day without its revision sheet. Claude Code is verified for
all three. This probe checks them in Claude Cowork.

Cowork is no longer a separate mode: "Claude Cowork is now just Claude"
(support.claude.com, *Use Claude Cowork on web, desktop, and mobile*, article
15520349). A chat on claude.ai, desktop or mobile runs in a cloud sandbox, and
since 6 October 2026 there is no "only on your computer" option on Pro and
Max. Skills and plugins work on every surface. A folder on your computer is
reachable only through a connected Claude Desktop app, and only while it is
open.

There is no headless runner, so this is run by hand. **Make no claim of
Cowork support — README, listing, release notes — until every check below
reads PASS.** A FAIL on check 1 or 2 means the deterministic layer cannot run
there, and the design decision says an adapter becomes Release 1 work
(`.shipkit/specs/learn-anything/design.md`, *Cowork gets a `.plugin`
package*).

## Where things run

Measured on 2026-10-22; recheck it on every run.

- **The chat** runs in a cloud sandbox: Linux, user `root`, working folder
  `/home/claude`. The plugin is a synced copy under
  `/root/.claude/plugins/synced/<org>_<id>/bodhikit`. `$CLAUDE_PLUGIN_ROOT` is
  empty in the chat's shell, but the hooks' commands expand it.
- **The learner's folder** stays on the Mac. The chat reaches it through the
  `mcp__remote-devices__*` tools: `device_bash` runs in a Linux VM inside
  Claude Desktop, with each granted folder mounted at `$HOME/mnt/<name>`.
  `device_stage_files` copies files from the folder into the sandbox's
  `/mnt/user-data/uploads/`. `device_commit_files` copies files from
  `/mnt/user-data/outputs/` back into the folder, and refuses a file that
  changed on the Mac since it was staged.
- So `bodhi-state` runs in the sandbox on a staged copy, and its writes reach
  the Mac only when the model commits them back. The hooks also run in the
  sandbox. SessionStart sees only `/home/claude`, so in a cloud chat the rule
  arrives when a BodhiKit skill first runs instead (`UserPromptExpansion` for
  a typed command, `PreToolUse` on `Skill` when Claude calls one). The Stop
  hook checks every project the chat ran `touch-state` on, including a staged
  copy.
- The sandbox's automatic permission check can refuse a `bodhi-state`
  command: on 2026-10-22 it blocked a read-only `revision-brief` as
  "Irreversible Local Destruction".

## Set up

1. Build the package from the tree you are releasing:

   ```bash
   python3 platforms/cowork/build_plugin.py --archive dist/bodhikit.plugin
   python3 dev/eval/test_cowork_plugin.py
   ```

2. On claude.ai, open Customize → Plugins → Add → Upload plugin and choose
   `dist/bodhikit.plugin`. Turn off any other BodhiKit plugin (Customize →
   Plugins → Yours → the plugin → its switch), because both register
   `/bodhikit:*`. Switching off a marketplace copy removes it from the Yours
   list, and its page then offers Add to bring it back.
3. Copy the SQL eval fixture to a folder of its own:

   ```bash
   mkdir -p ~/cowork-probe && cp -R dev/eval/fixtures/v2-project ~/cowork-probe/learningWithBodhi
   ```

4. Open Claude Desktop on the Mac and leave it open. On claude.ai, start a
   new chat. In the composer, choose + → Devices → *Run tasks on* and tick
   your Mac. Settings → Account → *Local devices* lists the Macs with when
   each was last seen. Ticking a Mac applies to that chat only, so tick it in
   every new chat.
5. The chat asks for a folder the first time it needs one ("Claude wants to
   use a folder on your computer"). Allow `~/cowork-probe/learningWithBodhi`,
   not just the project folder, because the profile
   (`learningWithBodhi/.bodhi-profile.json`) lives one level up. Decline
   anything outside `~/cowork-probe`. With memory on, the chat may ask for
   folders it remembers, such as `~/.bodhikit` or your code folder, and
   `~/.bodhikit/config.json` can point at real learner data.

## The checks

Run them in order; each later check needs the earlier ones. Read every reply
for which machine a command ran on.

1. **`python3` is present.** Ask the chat to run `command -v python3 && python3 --version`
   in its sandbox, and again on the Mac through `device_bash`, and to print the
   `version` line of the bodhikit plugin's `.claude-plugin/plugin.json`.
   PASS: Python 3.8 or later where the plugin's scripts run, and the version
   you uploaded. FAIL: not found, or a sandbox refusal.
2. **`bodhi-state` writes.** Run `/bodhikit:quiz current`, answer one question,
   and let it finish. Then run `scripts/bodhi-state --project <the fixture project> verify`
   from this repo on the Mac, and read the last `reviewHistory` entry of the
   reviewed concept in `.bodhi/spaced-review.json`.
   PASS: verify prints `"ok": true`, and today's entry has a `boxBefore` field
   (only the script writes it). FAIL: the script could not run and the model
   hand-edited the JSON, or nothing reached the Mac.
3. **The learning-project rule arrives with the first BodhiKit skill.** In
   check 2's chat, before the quiz, ask without tools whether it has a
   BodhiKit learning-project rule (it should not). After the quiz, ask again,
   and ask it to quote the rule's first heading and its Safety First section.
   Then, in a new chat with the Mac ticked, ask in plain words ("Use BodhiKit
   to give me a quick progress check-in…") so Claude calls the skill itself,
   and ask the same. PASS: both chats quote *Learning Project Context* and the
   safety bullets verbatim. FAIL: either has no rule.
4. **The Stop hook asks for the revision sheet.** In the second chat, ask it
   to stage only the project's `.bodhi`, run `bodhi-state --project <staged copy> touch-state --activity "probe"`,
   commit `state.json` back, and end its turn without writing anything under
   `revision/`. Note the checksum of today's sheet on the Mac first.
   PASS: the turn does not end; the hook's message names the staged copy of
   the Mac's project and says to bring `revision/` over; afterwards today's
   sheet on the Mac is unchanged or added to, never replaced. FAIL: the turn
   ends, or the sheet is overwritten.
5. **Files persist across chats.** Start another new chat, tick the Mac, and
   run `/bodhikit:progress quick`. Then ask for `lastActivity` from
   `.bodhi/state.json` and the reviewed concept's last `reviewHistory` entry.
   PASS: the review from check 2 and the activity from check 4. FAIL: the
   project is back at the fixture's state, or not found.

## Results

Record every run here, newest first: the date, the host, the BodhiKit
version, and PASS or FAIL per check with one line of evidence.

| Date | Host | BodhiKit | 1 python3 | 2 writes | 3 rule | 4 Stop hook | 5 persists | Notes |
|---|---|---|---|---|---|---|---|---|
| 2026-10-22, rerun | claude.ai in Chrome, cloud chat, Opus 5.5; Mac ticked under Devices | 1.25.0 built from `learn-anything-r2`: checks 1, 2, 3 and 5 at `922b2a6`, check 4 at `853364a` (the Stop hook's variable fix, the only change between them) | PASS: `/usr/bin/python3` 3.13.16; the synced plugin registers SessionStart, UserPromptExpansion, PreToolUse and Stop | PASS: verify on the Mac `"ok": true`; the entry has `"boxBefore": 1, "source": "quiz"`; the profile was updated too, with `~/cowork-probe` granted | PASS: before any skill, "No". After a typed `/bodhikit:quiz`, the rule "came in with your /bodhikit:quiz current message, as extra context added by the plugin's UserPromptExpansion hook". After a plain-words request, it arrived as "PreToolUse:Skill hook additional context". Both quoted the heading and Safety First verbatim | PASS at `853364a`: the hook blocked the stop, naming `/mnt/user-data/uploads/learningWithBodhi/sql-deep-dive` and saying to bring `revision/` over. The chat found today's sheet on the Mac and added nothing; its checksum is unchanged. At `922b2a6` the turn ended: the chat passed `--project $S/sql-deep-dive` | PASS: a new chat's `/progress quick` printed "Last session: today" and "0 concepts due", and read `lastActivity: "probe"` and the quiz entry | The fixture was copied fresh for this run. The progress chats asked for `~/code/bodhi-projects` and `~/.bodhikit` (declined). The sandbox's permission check blocked a read-only `bodhi-state … revision-brief`. |
| 2026-10-22 | claude.ai in Chrome, cloud chat, Opus 5.5; Mac ticked under Devices (Claude Desktop, macOS) | 1.25.0, uploaded as "Bodhikit by you"; 1.14.2 switched off | PASS: `/usr/bin/python3` 3.13.16 in the sandbox, where the plugin's synced copy reads `"version": "1.25.0"`; 3.10.12 in the Mac's VM | PASS: the quiz staged `.bodhi`, ran `bodhi-state` in the sandbox, and committed six files back. Verify on the Mac: `"ok": true`, and the entry has `"boxBefore": 1, "source": "quiz"` | FAIL: "I wasn't given a BodhiKit learning-project rule at the start of this session". The hook's `cwd` is `/home/claude`, and no folder is attached when a chat starts | FAIL: no message for the Mac's project. On the `/home/claude` copy, the hook blocked the stop: "This session studied a project and has not written today's revision sheet" | PASS: a new chat's `/progress quick` printed "Last session: today" and "0 concepts due" (the fixture had 3), and read `lastActivity: "probe"` and the quiz entry from the Mac | The Stop hook runs (python3, `${CLAUDE_PLUGIN_ROOT}` and the transcript scan all work) but walks only `/home/claude`, while the learner's files are on the Mac. With only the project folder granted, the quiz could not reach the profile one level up. Files committed back are mode 0600. |
