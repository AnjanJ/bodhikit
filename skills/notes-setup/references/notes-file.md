# The notes file — `learningWithBodhi/.bodhi-notes.json`

Loaded by `/bodhikit:notes-setup` and by the script-unavailable fallback only. No other skill
reads this file. It holds the learner's notes choice for every course, and sits beside
`.bodhi-profile.json` (found the same way: walking up from the course folder).

`bodhi-state` writes it, never a skill: `notes-set` records the choice the learner agreed to,
and `notes-offered` records that the one-time offer was made. `notes-show` reads it. `verify`
checks it when it exists. **No file means no choice and no offer** — every learner on 1.26.1.

```json
{
  "version": 1,
  "choice": "vault | files | off | null",
  "app": "obsidian | null",
  "location": "/absolute/path/to/the/vault | null",
  "agreedOn": "YYYY-MM-DD | null",
  "offerMadeOn": "YYYY-MM-DD | null",
  "announced": ["<course folder name>"]
}
```

| Field | Meaning |
|---|---|
| `choice` | `vault`: copy into the app's vault. `files`: keep `Syllabus.md` in each course folder, copy nothing. `off`: write neither; nothing written before is deleted. `null`: never chosen. |
| `app`, `location` | The app and its vault folder, for `vault`. Kept when the learner turns notes off, so turning them back on can start from them. |
| `agreedOn` | The day the learner last agreed to `vault` or `files`. |
| `offerMadeOn` | The day the one-time offer was made. Once set, the offer is never made again. |
| `announced` | Courses whose first arrival in the vault has been reported to the learner; later copies are silent. |

Unknown fields are kept on every write. The apps offered on a host come from `notes-show`
(`appsOffered`), never from this file.

**The home** is `<location>/Learn with Bodhi/`: `Courses.md`, then one folder per course
holding `Syllabus.md` and `revision/`. BodhiKit writes nothing in the vault outside it, and
reads nothing back from it.
