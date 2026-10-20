# Hosts without lasting files — the manual check

On claude.ai on the web, or in a phone app, a chat starts with no learning
project and keeps no files for the next one. BodhiKit can still teach there,
but it cannot keep a review schedule, so learn-anything REQ-39 asks for one
honest behaviour: say that tracked study needs a desktop surface, then teach
without a schedule. `/learn` and `/continue` follow
`skills/learn/references/host-without-files.md` when they find themselves on
such a host.

Nothing can drive claude.ai or the phone app headlessly, so this is checked by
hand. Full phone and claude.ai support with saved state is a later, separate
spec that starts with a research spike on keeping state between chats.

## How to run it

1. Load BodhiKit's skills on a host without lasting files: claude.ai on the
   web, or the Claude phone app. Record how you loaded them (the host's own
   skills upload, a project's instructions, or a pasted skill); the check is
   about the behaviour, not the install.
2. Start a chat with `/learn music theory: reading intervals` (or, where slash
   commands aren't available, "use the BodhiKit learn skill to start music
   theory").
3. Let it run to a natural stopping point: answer its questions, do the
   explain-back, then say you are done for today.

## The checks

1. **Says it once.** Early on, the tutor says that this host can teach but
   cannot keep the review schedule, and names Claude Code or Cowork on a
   computer for tracked study. It does not repeat it every turn.
2. **Teaches anyway.** A real lesson with an explain-back, graded honestly and
   reported in outcome words, with no Bloom or box numbers.
3. **Saves nothing it can't keep.** No `.bodhi/` scaffolding in a per-chat
   sandbox, no promised review date, and no "your progress is saved".
4. **Hands over a summary.** At the stopping point it offers a short Markdown
   note shaped like the revision sheet (covered, the explanation that landed,
   the slip, two prompts with answers, look again in about three days) and
   says it lives only where you save it.

## Results

Newest first: the date, the host and how BodhiKit was loaded, the BodhiKit
version, and PASS or FAIL per check with one line of evidence.

| Date | Host and loading | BodhiKit | 1 says once | 2 teaches | 3 saves nothing | 4 summary | Notes |
|---|---|---|---|---|---|---|---|
| — | — | — | not yet run | not yet run | not yet run | not yet run | The reference is written; no run is recorded yet. |
