# Lessons from earlier guides

What the first guides (November 2026) taught, written so they apply to the next one. Load in phase 4. Re-read the *Verification* and *Layout* lessons in phases 3 and 7. Add a lesson when a guide teaches a new one, in the same generic form. Never name the learner, their employer or where they live (spec write-guide, REQ-18). The repository is public and learners may read it: write each lesson so the person it came from would not recognise themselves in it. State the rule, not the story.

## Planning the learning

1. **Look for the gate first.** A certification a job required had an experience requirement the learner didn't yet meet, so every schedule built for it would have been wrong. Check eligibility, licences and prerequisites at the certifying body's own source, and put the check before the schedule. Offer the paths both ways (eligible now; not yet, and what to do meanwhile, such as the body's entry-level credential or logging experience as it happens).
2. **Training rules change.** A body changed which live classes count toward its required hours from a set date, with training *completed* before the date still counting; enrolling or paying before the date didn't. When a guide recommends a course, give a checklist: provider recognition, hours confirmed in writing, alignment with the current exam outline, time zone, total cost and cancellation, employer funding, and a warning against providers that guarantee a pass.
3. **One home per subject.** Tracked study (Claude with Claude Desktop and Devices) and log-based study (ChatGPT, or Claude without a computer) must not mix within one subject, or the record splits.
4. **Three subjects at most,** and a smaller start for anyone already struggling: one subject first, with a second added in week 3.
5. **A busy-week minimum** (one short review and one short practice) and the fact that overdue reviews wait. People drop plans when one bad week feels like failure.
6. **Real-life skills are practised away from the screen and debriefed.** Speaking, meetings, feedback, a lab or kitchen technique follow the loop: prepare in the chat, rehearse with the tutor playing the other person, do it for real, then debrief with three questions. A rehearsal in the chat is preparation, not a practice rep.
7. **Give shapes they can use tomorrow.** A 60-second update (outcome, status, impact, ask), sharing a finding (finding, evidence, meaning, recommendation, question; facts kept apart from assumptions), saying how you feel (what happened, how I feel, what I need, what I'm asking for). Present them as starting shapes, not scripts.
8. **When work is going badly, add a manager section:** concrete questions for a one-to-one, a rehearsal prompt, and a small improvement loop (one behaviour, practised, with feedback after two to four weeks).
9. **Practise the job on made-up cases.** A fictional project, patient or client lets the learner practise the real work (scope, risks against issues, owners) without confidential data.
10. **Prompts for real days.** A table organised by situation ("a meeting full of words you don't know", "a disagreement is coming", "your week is full") is used more than one organised by command.
11. **Name their strengths honestly.** A background in another field often brings something real, such as an eye for audience, evidence or detail. Say how it helps; don't flatter.
12. **Wellbeing.** BodhiKit teaches skills, including saying how you feel; it is not a counsellor. Point to a person: someone they trust, a doctor, a counsellor, an employer's assistance programme if they have one (don't assume one exists).

## Platforms

13. **Menus move.** Claude renamed "Customize" to "Plugins" in the same week a guide was written. Name both labels while a rollout is under way, and add a line: "if a label differs, look for …".
14. **Say what was tested.** Tracked study was measured on claude.ai in a browser with Claude Desktop open; the Desktop app's own window and a phone reaching the laptop were not. Say so in the guide instead of implying they work.
15. **Country availability.** The ChatGPT listing's countries are set in OpenAI's portal and are not in the repository. For a learner outside the US, ask the maintainer to check, and give a fallback.
16. **A ChatGPT-only guide still gets one line on Claude:** the same commands as `/bodhikit:<name>`, and that Claude on a computer with Claude Desktop keeps the schedule.

## Verification

17. **Some official sites refuse the fetch tool** (HTTP 403 on every page) while their PDFs download with a plain `curl -sL`. Use the PDF. Never retry with a disguised user agent; that attempt was rightly blocked.
18. **A search snippet is not an opened page.** If a rule is visible only in search results, find a second source you *can* open (another official document, or a reputable provider quoting it), and write both into the ledger. In the guide, say the official page didn't open.
19. **Don't add details you didn't see.** "Members can read it free" was caught at the end because no page said so. A claim that makes a resource sound better needs its own source.
20. **Bibliographic records disagree.** A book had first-publication years of 1981 and 1987 in different catalogues. Cite the edition you can confirm, and drop the year you can't.
21. **Check the other guide's facts too.** When comparing guides, the other guide stated a training rule as fact with no caveat; it was right, but only checking showed that.

## Layout

22. **The contents list on its own page**, so the cover isn't followed by a page holding only the end of the list.
23. **Header rows in `thead`**, so a long table repeats its header on the next page. **Short tables `class="whole"`**, and keep an introducing sentence with its table (`<div class="keep">`).
24. **Read every contact sheet, then one dense page at higher resolution.** Stranded headers and split tables show only on the page.
25. **Grep for personal terms with word boundaries and case** (`grep -nw`). A case-insensitive search for a short name matched inside ordinary words.

## The command reference

26. **Tailor every example to their subjects;** keep the facts from `commands.md`. For a learner with no code, mark `pair` and `debug-together` as code-only; for a learner learning a programming language, they matter.
27. **In a ChatGPT-only guide, the commands that need saved files** (`forget`, `progress`, `housekeep`) are explained in terms of the learner's log.

## The learner's own material

28. **An anonymous survey stays anonymous.** Never quote a survey answer in a guide, even when the maintainer can tell whose it is: it shows the reader their answers were linked to them. Use only what the learner said directly.
29. **Screenshots the learner shares are evidence.** They confirm UI labels (date them, and mark them "seen on a learner's screenshot" in platform-facts), the subjects and topics they actually study, and the language they study in. Personal content in them stays out of the guide and the repository.
30. **Never help work look less like AI.** Cover instead the assignment's rule on AI, being able to explain every line and number, and saying how AI was used. Leave AI-detection claims out: detectors are unreliable, and the honest reason to do the work is that exams test you without the chat.
31. **Don't promise it never gives answers.** In ChatGPT a finished answer is a request away. Say what BodhiKit is built to do (README: it won't write your code), and that the choice is the learner's each time.
32. **Teach the learner's own workarounds.** A fix they found for themselves is worth turning into a habit in the guide.

## More verification

33. **Refused journal pages have official copies.** NCBI's E-utilities return PubMed abstracts with a plain request (`efetch.fcgi?db=pubmed&rettype=abstract`), and PMC often holds the article; OpenStax book details come from its CMS API. Record which copy you read.
34. **Run what you print.** Run every code example in an official container (`docker run r-base Rscript …`) and translate every sequence against NCBI's table by script, not by hand.
35. **Check example dates against the rules.** A review-table row must follow the gaps: an earlier guide showed a 7-day gap two days after an idea was learned.
36. **Check the repository's own links.** `gh api repos/<owner>/<repo>` shows whether Discussions or Issues are on; the template once linked to Discussions while it was off.
37. **A README figure can outrun its source.** "18 subject areas" was in the README but not in the study's abstract. Quote the abstract's numbers.
