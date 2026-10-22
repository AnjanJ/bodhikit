# Hosts without lasting files — the manual check

On claude.ai on the web, or in a phone app, with no computer connected, a
chat starts with no learning project and keeps no files for the next one. BodhiKit can still teach there,
but it cannot keep a review schedule, so learn-anything REQ-39 asks for one
honest behaviour: say that tracked study needs a desktop surface, then teach
without a schedule. `/learn` and `/continue` follow
`skills/learn/references/host-without-files.md` when they find themselves on
such a host.

Nothing can drive claude.ai or the phone app headlessly, so this is checked by
hand. A chat with Claude Desktop connected does keep files (REQ-38,
`docs/cowork-probe.md`); the reference must tell the two apart. Saved state
with no computer connected is a later, separate spec that starts with a
research spike on keeping state between chats.

## How to run it

1. Load BodhiKit's skills on a host without lasting files: claude.ai on the
   web, or the Claude phone app. Record how you loaded them (the host's own
   skills upload, a project's instructions, or a pasted skill); the check is
   about the behaviour, not the install.
2. Start a chat with `/learn music theory: reading intervals` (or, where slash
   commands aren't available, "use the BodhiKit learn skill to start music
   theory").
3. Start with Claude Desktop closed: while it runs, a new chat sees the
   computer even with nothing ticked under + → Devices. After the tutor's
   first lesson, reopen Claude Desktop and answer the tutor's next question
   as usual, without mentioning it. When it offers a choice, choose to carry
   on without a schedule.
4. Let it run to a natural stopping point: answer its questions, do the
   explain-back, then say you are done for today.

## The checks

1. **Says it once.** Early on, the tutor says that this host can teach but
   cannot keep the review schedule, and names both ways to tracked study:
   Claude Code, or a Claude chat with Claude Desktop connected. It does not
   repeat it every turn.
2. **Teaches anyway.** A real lesson with an explain-back, graded honestly and
   reported in outcome words, with no Bloom or box numbers.
3. **Saves nothing it can't keep.** No `.bodhi/` scaffolding in a per-chat
   sandbox, no promised review date, and no "your progress is saved".
4. **Hands over a summary.** At the stopping point it offers a short Markdown
   note shaped like the revision sheet (covered, the explanation that landed,
   the slip, two prompts with answers, look again in about three days) and
   says it lives only where you save it.
5. **Notices a computer.** Once the computer is connected, the tutor says so,
   corrects what it said about tracking, and offers tracked study on the
   computer or carrying on without a schedule. It opens, reads and writes
   nothing on the computer before the learner chooses.

## Results

Newest first: the date, the host and how BodhiKit was loaded, the BodhiKit
version, and PASS or FAIL per check with one line of evidence.

| Date | Host and loading | BodhiKit | 1 says once | 2 teaches | 3 saves nothing | 4 summary | 5 computer connects | Notes |
|---|---|---|---|---|---|---|---|---|
| 2026-10-22 | claude.ai on the web (Opus 5.5, Medium), with Claude Desktop closed at the start. `/learn`, its `host-without-files.md` reference and the `teaching-personality` KB from `5e2ba58`, attached as one Markdown file with the instruction to follow it rather than the installed plugin ("Bodhikit by you", the `853364a` build). The learner's replies were typed by Claude Code through Chrome. | `5e2ba58` (1.25.0 with T37) | PASS: it checked for a connected computer, asked the new three-way question, and on "no computer connected" said "That needs a computer where your learning project lives in a folder you keep, either in Claude Code or in a Claude chat with Claude Desktop connected", naming what is lost (reviews timed to the right day, the record of what's solid); not repeated | PASS: a lesson on interval numbers with a worked example (C4 to G4) and the staff shortcut, then a four-question drill whose answers it said were fixed before the learner started (no key file was written). The slip (F4 to C♯5 as "a sixth, because the sharp…") was turned back on the lesson's rule until the learner recounted. "You can name the number of an interval on the staff and explain why the counting works"; no Bloom or box number anywhere | PASS: no `.bodhi/`, no file written, no review date, nothing said to be saved | PASS: a Markdown note dated 22 Oct 2026 with what was covered, the explanation that landed, the slip and its correction, two prompts (one on the learner's E major chord) with the answers below a rule, and "Look at this again in about three days"; "It lives only where you save it". Offered at a natural pause, unprompted | PASS: Claude Desktop was reopened after the lesson, with nothing ticked. The next reply graded the drill, then: "Something has changed on my side. Your computer now appears to be connected to this chat. Earlier I said I couldn't keep a review schedule here. With a computer connected, I could." It offered Tracked or Untracked and said "I won't open or write anything on your computer until you choose." The learner chose Untracked, and it opened nothing | A first chat, with Claude Desktop running and nothing ticked under + → Devices, saw the Mac as connected ("Your Mac is connected, so this runs as a tracked project rather than a one-off chat lesson") and went to the normal flow, asking for no folder before scoping; it was stopped there. A running Claude Desktop counts as connected without a tick, so step 3 now starts with it closed. |
| 2026-10-21 | claude.ai on the web (Opus 5.5, Medium). `/learn` from `learn-anything-r2`, its `host-without-files.md` reference and the `teaching-personality` KB attached as one Markdown file, with the instruction to follow it rather than the installed plugin (1.14.2, which has no such reference). The learner's replies were typed by Claude Code through Chrome. | `learn-anything-r2` (1.25.0 + Release 2) | PASS: in its first reply, "Here I can teach you, but I can't keep your review schedule. That needs Claude Code on a computer", naming what is lost (spaced reviews, *Solid*, the sheets), not Cowork, and not repeated in later turns | PASS: a lesson on interval numbers tied to the learner's guitar chords, a ten-question drill and an explain-back; 9/10 graded against the key, the slip (C up to D♯ as a 3rd, "same fret as E♭") turned back on the learner's own rule until they fixed it; "You can now name the interval number of any written interval reliably", and no Bloom or box number anywhere in the chat | PASS: no `.bodhi/`, no review date, no "saved"; "I won't keep any of this after the chat ends". The one file it wrote was the drill's answer key, in its own sandbox before the learner answered, which is the key protocol, not tracking | PASS: a Markdown note dated 2026-10-21 with what was covered, the explanation that landed, the slip and its fix, two retrieval prompts with the answers below a rule, and "Look at this again in about three days", offered "to save wherever you keep your notes" | not a check yet; see Notes | Finding: mid-chat, Claude Desktop on the Mac connected to the chat ("Computer actions available"). The tutor noticed, said "I need to correct what I said earlier … tracking is possible after all", saw `~/.bodhikit` from the connection's status, and offered (a) tracked study on the computer or (b) chat-only. The learner chose (b), and it opened nothing on the Mac. The reference's *How to tell* list does not name a web chat with a connected computer; the tutor's choice was sound, but the case is unwritten. |
