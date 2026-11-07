---
name: write-guide
description: Write a personalised guide to using BodhiKit in Claude and ChatGPT for one person or one role, or revise an existing guide. It asks what it needs, researches, verifies every fact, designs the learning, and renders a PDF and an editable DOCX.
argument-hint: "<who it is for and what they want to learn> | revise <path to guide.html>"
disable-model-invocation: true
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
---

# /write-guide: a BodhiKit guide for one person or one role

You are writing for the maintainer, who will send the guide to a learner. The learner may have never used an AI tutor, may not be technical, and will follow the guide step by step on a phone or a laptop. The standard is a guide the maintainer can send without re-reading every claim against its source.

Arguments: `$ARGUMENTS`

- `revise <path>`: revise the guide at that path (see *Revise mode*).
- Anything else: a new guide for the person or role described. If empty, ask who it is for.

## Standing rules (they hold for the whole session)

1. **Verify before you write.** Every factual sentence in the guide gets a row in the claim ledger, `claims.md`, beside the guide: the claim, its source (URL or repo path), the date checked, and *verified* or *not verified*. A search-result snippet is not an opened page. If you could only see a snippet, say so in the ledger.
2. **Open a resource's page before listing it.** Confirm the title, the author or publisher, and the year on the page itself. Anything you can't open is marked "not verified" in the guide, or left out.
3. **Never get around a bot check.** Don't use a browser-like user agent, a proxy, a cache or a mirror to reach a page that refused you. Try another official copy (the body's own PDF, another page on the same site), then mark the claim "not verified".
4. **Never invent a personal detail.** Name, pronouns, employer, country, plan, devices, hours, deadlines: ask, or leave it out. Use the pronouns the maintainer gives. The guide itself speaks to "you".
5. **Personal details never enter the repository.** Guides, ledgers and briefs live outside it, by default in `~/Downloads/BodhiKit-<name>-guide/`. The one repository file you may edit is `references/platform-facts.md` (phase 3). Never commit; the maintainer reviews and commits.
6. **Learner text follows BodhiKit's voice rules.**
   - Write plain English, in short sentences, addressed to "you".
   - Never quote a level number, a box number or a state-engine name (decision 0005; the `blooms-taxonomy` KB's *Learner-Facing Rendering*). Say what the learner can do, in outcome words.
   - Never promise what a host can't do. "Your progress is saved" is false in ChatGPT and in a Claude chat with no computer connected.
7. **Be honest about BodhiKit's limits.**
   - It can't see or hear the learner. Practice away from the screen counts as "your account".
   - It is a tutor, not a therapist or a doctor.
   - It won't do graded work for the learner.
   - It follows the safety limits in `rules/learning-project.md`.
8. **Grep before a universal claim.** Before writing "only X does Y" or "every command can…", check the repository.

## Revise mode

1. Copy the guide's HTML and PDF into a `previous/` folder beside them before changing anything.
2. Run phase 1, then read the guide and its `claims.md` (build the ledger from the guide if there is none).
3. Ask what should change, using the intake bank only for what the change needs.
4. Re-verify every ledger row the revised guide keeps.
5. If the maintainer gives you another guide to compare, read it. List what it does better than this one, and verify each item before proposing it. Ask which to adopt, one numbered paragraph per item.
6. Apply the changes, then run phases 6 to 8.

## Phase 1: Ground truth from the repository

The repository is your working directory (`git rev-parse --show-toplevel`). Read, don't recall:

- the version: `.claude-plugin/plugin.json`;
- the learner commands: `grep -l '^user-invocable: true' skills/*/SKILL.md`;
- how each platform keeps or loses progress:
  - `docs/cowork-probe.md`: a Claude chat keeps files only with Claude Desktop open and the computer ticked under + → Devices;
  - `docs/hosts-without-files.md`: with no computer connected, it teaches and keeps nothing;
  - `docs/openai.md`: ChatGPT is conversation-only;
- the README's install sections;
- `skills/evidence-kinds/SKILL.md`: the four ways work is checked (code, problems, writing, performed);
- `rules/learning-project.md`: the safety limits;
- the top entries of `CHANGELOG.md`, and `git log` since the oldest date in `references/platform-facts.md`, for behaviour changes;
- `.shipkit/decisions/`: the rules on learner text.

Then load `${CLAUDE_SKILL_DIR}/references/commands.md`. If the changelog shows a command changed, re-read that skill and correct its row.

## Phase 2: Intake

Load `${CLAUDE_SKILL_DIR}/references/intake-questions.md`. Mark what the request and earlier guides already answer, then ask the rest:

- choices with AskUserQuestion (at most four questions per call);
- open questions together in one message.

Ask before any research. When the answers are in, write them to `brief.md` in the output folder; revise mode starts from it later.

## Phase 3: Research and verify

Start `claims.md` in the output folder as a table: `# | Section | Claim | Source | Checked | Status`. Run independent searches and fetches in parallel.

1. **Platform facts.** Load `${CLAUDE_SKILL_DIR}/references/platform-facts.md`.
   - Re-check, at its source, every entry the guide will use: menus, plans, phone support, availability in the learner's country.
   - If one has changed, update that entry with the new fact, source and date, and keep a note for the report. A new platform fact gets a new entry.
   - If the learner's country isn't confirmed for an app, say so in the guide and give a fallback.
2. **Subject facts.** Go to the primary source: the body that sets the rule (an exam board, a certifying institute, a regulator, a university), preferably its own PDF.
   - For an exam or a certification, check eligibility, format, dates and how training counts.
   - Give fees only if verified on the body's page; otherwise point to that page.
3. **Gates.** Look for anything that could stop the plan: eligibility, a licence, a prerequisite, an age limit, employer approval, a deadline already past. Each gets a check that comes before any schedule built on it.
4. **Resources.** Two to five per subject: a standard reference, a free source, and a local or community one in the learner's city where relevant (a club, a professional chapter). Open each page and confirm it (standing rule 2).
5. **Research cited in the guide.** Use the studies in the README's *The Science*, already vetted, or verify a new one the same way.

Download an official PDF with a plain request (`curl -sL`), into its own empty folder under `/tmp`, and read it with `pdftotext`.

## Phase 4: Design the learning

Load `${CLAUDE_SKILL_DIR}/references/lessons.md`. Then decide, and be ready to say why:

1. **Subjects.** One learning project per subject, at most three active at once.
2. **How each module's work is checked.** Use the `evidence-kinds` KB's four kinds, in plain words. A real-life skill (speaking, a meeting, a conversation, a lab or kitchen technique) is practised away from the screen and debriefed. A rehearsal in the chat is preparation, not a rep.
3. **A home for each subject.**
   - Claude on a personal laptop with Claude Desktop open keeps the schedule.
   - ChatGPT, and Claude with no computer connected, need a learning log.
   - Choose one home per subject.
4. **A curriculum per subject.** A table of phase → module → "you'll be able to…" → practice in real life. Later phases revisit earlier ideas at more depth.
5. **The schedule.**
   - the first two weeks, day by day;
   - a weekly rhythm in the hours they gave;
   - a roadmap of three to six months;
   - a busy-week minimum, and a smaller start for anyone already struggling.
   - Gates (phase 3.3) come first.
6. **Limits.**
   - employer or school AI rules and what never goes into a chat;
   - wellbeing (a tutor isn't a counsellor; point to a person);
   - safety for hands-on subjects.

## Phase 5: Write

1. Copy `${CLAUDE_SKILL_DIR}/references/guide-template.html` to `guide.html` in the output folder and fill it.
2. Cut the sections that don't apply (Claude setup for a ChatGPT-only learner, the learning log for a fully tracked one) and renumber every "section N" reference.
3. For each subject, give:
   - a ready-to-paste first message for each app they use;
   - what happens next;
   - a "Try this" exercise with its answer underneath;
   - an example of the tutor's questioning, labelled as an example.
4. Build the command reference from `commands.md`:
   - every learner command, in both apps' forms where they use both;
   - examples drawn from their subjects;
   - code-only commands marked as such.
5. In the cover meta, give the BodhiKit version, the apps, and the month and year.
6. Head the sources section "Checked on <date>".

## Phase 6: Self-review

1. **Ledger.** Walk the guide section by section. Every factual sentence must have a ledger row and every ledger row must still be in the guide.
2. **Detectors.** Run the repository's decision-0005 detectors over the guide's text and fix any match:

   ```bash
   python3 -c 'import sys,re,html; sys.path.insert(0,"dev/eval"); import assert_scenario as a; t=html.unescape(re.sub(r"<[^>]+>"," ",open(sys.argv[1]).read())); [print(m.group(0)) for r in (a.BARE_LEVEL_RE,a.INTERNAL_NAME_RE) for m in r.finditer(t)]' <guide.html>
   ```

3. **Cross-references.** The contents list matches the headings, and every "section N" points at the right section.
4. **Platform statements.** They agree with phase 1's documents.
5. **Read as the learner.** Every term is defined at first use, every prompt can be copied as it stands, and nothing promises more than BodhiKit can do.

## Phase 7: Render and check every page

```bash
"${CLAUDE_SKILL_DIR}/scripts/render.sh" <output folder>/guide.html <Output-Name>
```

It writes `<Output-Name>.pdf` and `<Output-Name>.docx` beside the HTML and prints the folder holding the contact sheets.

1. Read every contact sheet. Fix:
   - a heading or table header stranded at the foot of a page;
   - a short table split across pages (`class="whole"`);
   - a nearly empty page;
   - an overflowing code line.
2. Render again.
3. Read the densest page at higher resolution (`pdftoppm -r 80 -f N -l N`) to confirm the text is readable.

## Phase 8: Report

Tell the maintainer, in their reply format:

- where the PDF, DOCX, HTML, `claims.md` and `brief.md` are;
- how many claims are verified and how many are not, and the not-verified ones listed with the reason;
- the things to check before sending, numbered: a fact only the maintainer can confirm, an untested platform route, a gate the learner must check;
- any change made to `references/platform-facts.md`, uncommitted, for review;
- which of the spec's model-behaviour requirements this run tested by hand, if the maintainer is keeping that record (`.shipkit/specs/write-guide/intake.md`).
