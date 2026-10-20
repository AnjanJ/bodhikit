# Cowork probe — does BodhiKit's tracked state work in Claude Cowork?

BodhiKit's promise rests on three things outside the skills' text: the
`bodhi-state` script runs (so every tracking write is deterministic), the
SessionStart hook injects the learning-project rule, and the Stop hook refuses
to end a studied day without its revision sheet. Claude Code is verified for
all three; Cowork is not. Cowork's plugin format matches Claude Code's (the
same `skills/`, `agents/`, `hooks/hooks.json` and `${CLAUDE_PLUGIN_ROOT}`),
but nobody has confirmed that `python3` exists there, that the hooks fire, or
that the hooks' working-folder markers match how Cowork opens a folder.

There is no headless Cowork runner, so this is run by hand. **Make no claim of
Cowork support — README, listing, release notes — until every check below
reads PASS.** A FAIL on check 1 or 2 means the deterministic layer cannot run
there, and the design decision says an adapter becomes Release 1 work
(`.shipkit/specs/learn-anything/design.md`, *Cowork gets a `.plugin`
package*).

## Set up

1. Build the package from the tree you are releasing:

   ```bash
   python3 platforms/cowork/build_plugin.py --archive dist/bodhikit.plugin
   python3 dev/eval/test_cowork_plugin.py
   ```

2. In the Cowork desktop app, add `dist/bodhikit.plugin` to a chat and accept
   it from the preview. The plugin's skills appear as BodhiKit's commands.
3. Give Cowork a working folder that holds a learning project. The quickest is
   a copy of the SQL eval fixture:

   ```bash
   mkdir -p ~/cowork-probe && cp -R dev/eval/fixtures/v2-project ~/cowork-probe/learningWithBodhi
   ```

   Open `~/cowork-probe/learningWithBodhi/sql-deep-dive` as the session's folder.

## The checks

Run them in order; each later check needs the earlier ones.

1. **`python3` is present.** Ask Cowork to run `command -v python3 && python3 --version`.
   PASS: a path and Python 3.8 or later. FAIL: not found, or a sandbox refusal.
2. **`bodhi-state` writes.** Run `/bodhikit:quiz current`, answer one question,
   and let it finish. Then ask Cowork to run
   `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project . verify` and to show
   the last entry of `.bodhi/spaced-review.json`'s reviewed concept.
   PASS: verify prints `"ok": true`, and today's `reviewHistory` entry has a
   `boxBefore` field (only the script writes it). FAIL: the script could not
   run and the model hand-edited the JSON, or nothing was written.
3. **The learning-project rule arrives at session start.** Start a fresh
   session on the same folder and ask, before anything else: "Quote the first
   heading of the learning-project rule you were given, and its Safety First
   section." PASS: *Learning Project Context*, and the safety bullets
   verbatim. FAIL: the model has no such rule (the SessionStart hook did not
   fire, or did not see the folder as a learning project).
4. **The Stop hook asks for the revision sheet.** In that session, ask Cowork
   to run `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project . touch-state --activity "probe"`
   and then to end its turn without writing anything under `revision/`.
   PASS: the turn does not end; the hook's message asks for
   `revision/<today>-*.md` (and the model writes it). FAIL: the session simply
   stops.
5. **Files persist across sessions.** Close the session, open a new one on the
   same folder, and run `/bodhikit:progress quick`. PASS: it shows today's
   review from check 2 and the probe activity from check 4. FAIL: the project
   is back at the fixture's state, or not found.

## Results

Record every run here, newest first: the date, the Cowork app version, the
BodhiKit version, and PASS or FAIL per check with one line of evidence.

| Date | Cowork version | BodhiKit | 1 python3 | 2 writes | 3 rule | 4 Stop hook | 5 persists | Notes |
|---|---|---|---|---|---|---|---|---|
| — | — | — | not yet run | not yet run | not yet run | not yet run | not yet run | The package builds and passes `test_cowork_plugin.py`; nothing has run inside Cowork yet. |
