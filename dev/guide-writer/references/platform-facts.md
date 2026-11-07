# Platform facts

The facts about Claude and ChatGPT that a guide relies on and that change without notice. Before a guide uses an entry, re-check it at its source. If it changed, rewrite the entry with the new fact, source and date, and say so in the report. If you can't re-open the source, set the status to `not verified` and say why. Add a new entry in the same shape for any new platform fact a guide uses. `dev/eval/test_guide_writer.py` fails on an entry without a source, a date or a status.

Facts about BodhiKit itself (the version, the commands, how each host keeps progress) are not kept here: read them from the repository each run (SKILL.md, phase 1).

## Claude

### Plugins need a paid Claude plan
- Fact: plugins are available on Pro, Max, Ultra, Team and Enterprise. Free is not listed. Plugins work in chat on the web, the Chat tab in Claude Desktop, Claude Cowork, and Claude Code signed in with the same account.
- Source: https://support.claude.com/en/articles/13837440-use-plugins-in-claude
- Checked: 2026-11-07
- Status: verified

### The sidebar menu is "Plugins" (formerly "Customize")
- Fact: "Customize" became "Plugins", one page for plugins, skills and connectors. Rollout began 29 October 2026, with general availability on 9 November 2026 for Free, Pro, Max, Ultra and Team; on by default for Enterprise from 30 November 2026. Accounts mid-rollout may still show Customize → Plugins.
- Source: https://support.claude.com/en/articles/17740565-manage-plugins-skills-and-connectors-from-one-plugins-page
- Checked: 2026-11-07
- Status: verified

### Adding BodhiKit from its marketplace
- Fact: Plugins (or Customize → Plugins) → Add → Add marketplace → Add from a repository → enter `AnjanJ/bodhikit` → Sync; then open Bodhikit and choose Add. Keep one BodhiKit switched on. Update: Add → Manage marketplaces → ⋯ beside bodhikit → Check for updates. Alternative: download `bodhikit.plugin` from the latest GitHub release and use Add → Upload plugin; that copy stays at its version.
- Source: https://support.claude.com/en/articles/13837440-use-plugins-in-claude ; README.md *Claude chats with your computer connected*
- Checked: 2026-11-07
- Status: verified

### Calling a plugin's skills in Claude
- Fact: in chat and Cowork, type `/` or click **+** to see a plugin's skills; in Cowork a command can be typed as `/plugin-name:command`. A plain-words request also starts a BodhiKit skill (docs/cowork-probe.md check 3).
- Source: https://support.claude.com/en/articles/13837440-use-plugins-in-claude ; docs/cowork-probe.md
- Checked: 2026-11-07
- Status: verified

### Hooks run only in Cowork and Claude Code
- Fact: plugin hooks and sub-agents run only in Cowork and Claude Code and appear greyed out in plain chat. BodhiKit's hooks deliver the learning-project rule and require the day's revision sheet. On claude.ai in a browser with the computer connected, they ran (docs/cowork-probe.md, 2026-10-22).
- Source: https://support.claude.com/en/articles/13837440-use-plugins-in-claude ; docs/cowork-probe.md
- Checked: 2026-11-07
- Status: verified

### Claude chats run in the cloud; a folder on the computer needs Claude Desktop open
- Fact: Cowork is part of every Claude surface and runs in a cloud sandbox. From 6 October 2026 on Pro, Max and Ultra there is no "only on your computer" option. Skills and plugins are available on desktop, web and mobile. A chat can reach folders on a computer only while the Claude Desktop app is open there.
- Source: https://support.claude.com/en/articles/15520349
- Checked: 2026-11-07
- Status: verified

### Tracked study in a Claude chat
- Fact: BodhiKit keeps the plan, review schedule and revision sheets only when Claude Desktop is open and the computer is ticked under **+** → **Devices** in that chat, with the `learningWithBodhi` folder allowed (the whole folder, not a subject inside it). Measured on claude.ai in Chrome with the Desktop app open; the Desktop app's own window was not tested.
- Source: docs/cowork-probe.md (2026-10-22 rerun) ; README.md
- Checked: 2026-11-07
- Status: verified

### A phone chat reaching the laptop's folder
- Fact: Anthropic says a cloud session can reach connected folders while the Desktop app is open. Whether a phone chat can tick the laptop under Devices and run BodhiKit tracked has not been tested.
- Source: https://support.claude.com/en/articles/15520349
- Checked: 2026-11-07
- Status: not verified (untested with BodhiKit; say so in the guide)

### Where to get the apps
- Fact: Claude Desktop for macOS and Windows (Linux in beta) at claude.com/download; the iOS app from the App Store; other phones via claude.ai/mobile.
- Source: https://claude.com/download
- Checked: 2026-11-07
- Status: verified

### Claude's pricing page doesn't list plugins per plan
- Fact: the pricing page lists skills on every plan but has no row for plugins or Cowork. Cite the plugins article for plan eligibility, and the pricing page only for prices.
- Source: https://claude.com/pricing
- Checked: 2026-11-07
- Status: verified

## ChatGPT

### Plugins in ChatGPT
- Fact: "Select plugins are available in all plans" (Free, Plus, Pro, Business, Enterprise, Edu, ChatGPT for Teachers); some plugins need a paid plan. Add from the sidebar or chatgpt.com/plugins; call one with `@` and its name. On Enterprise and Edu, an administrator must enable plugins first.
- Source: https://chatgpt.com/features/plugins/
- Checked: 2026-11-07
- Status: verified

### OpenAI's help article on plugins
- Fact: OpenAI's help article *Plugins in ChatGPT* is the step-by-step reference, but it returned HTTP 403 to the fetch tool. Use the features page above, or ask the maintainer to open it.
- Source: https://help.openai.com/en/articles/20001256-plugins-in-chatgpt
- Checked: 2026-11-07
- Status: not verified (page wouldn't open)

### The BodhiKit listing
- Fact: BodhiKit is in ChatGPT's plugin directory, published by Abhaya Code Labs. The listing is a snapshot of the last approved upload: 1.26.1, confirmed published on 2026-11-07. Check `docs/openai-submission.md` for the current version before stating one.
- Source: docs/openai-submission.md ; commit a7eb6b8
- Checked: 2026-11-07
- Status: verified

### BodhiKit's availability by country in ChatGPT
- Fact: the countries the listing is offered in are set in OpenAI's portal and are not recorded in the repository. Third-party sources say some plugins are unavailable in the EEA, the UK or Switzerland; no OpenAI page confirmed it. For a learner outside the US, tell the maintainer to check the portal's availability settings, and give the learner a fallback (Claude).
- Source: docs/openai-submission.md *Availability* ; https://chatgpt.com/features/plugins/
- Checked: 2026-11-07
- Status: not verified (not recorded; ask the maintainer)

### ChatGPT keeps nothing between chats
- Fact: in ChatGPT on the web, desktop app and phone, BodhiKit runs conversation-only. It teaches as usual, never claims progress was saved, and offers a summary to keep. The learner's log carries the plan and review dates.
- Source: docs/openai.md *Runtime behavior by platform* ; platforms/openai/bodhikit/references/openai-runtime.md
- Checked: 2026-11-07
- Status: verified
