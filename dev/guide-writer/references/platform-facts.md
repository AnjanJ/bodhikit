# Platform facts

The facts about Claude and ChatGPT that a guide relies on and that change without notice. Before a guide uses an entry, re-check it at its source. If it changed, rewrite the entry with the new fact, source and date, and say so in the report. If you can't re-open the source, set the status to `not verified` and say why. Add a new entry in the same shape for any new platform fact a guide uses. `dev/eval/test_guide_writer.py` fails on an entry without a source, a date or a status.

Facts about BodhiKit itself (the version, the commands, how each host keeps progress) are not kept here: read them from the repository each run (SKILL.md, phase 1).

## Claude

### Plugins need a paid Claude plan
- Fact: plugins are available on Pro, Max, Ultra, Team and Enterprise. Free is not listed. Plugins work in chat on the web, the Chat tab in Claude Desktop, Claude Cowork, and Claude Code signed in with the same account.
- Source: https://support.claude.com/en/articles/13837440-use-plugins-in-claude
- Checked: 2026-11-08
- Status: verified

### The sidebar menu is "Plugins" (formerly "Customize")
- Fact: "Customize" became "Plugins", one page for plugins, skills and connectors. Rollout began 29 October 2026, with general availability on 9 November 2026 for Free, Pro, Max, Ultra and Team; on by default for Enterprise from 30 November 2026. Accounts mid-rollout may still show Customize → Plugins.
- Source: https://support.claude.com/en/articles/17740565-manage-plugins-skills-and-connectors-from-one-plugins-page
- Checked: 2026-11-08
- Status: verified

### Adding BodhiKit from its marketplace
- Fact: Plugins (or Customize → Plugins) → Add → Add marketplace → Add from a repository → enter `AnjanJ/bodhikit` → Sync; then open Bodhikit and choose Add. Keep one BodhiKit switched on. Update: Add → Manage marketplaces → ⋯ beside bodhikit → Check for updates. Alternative: download `bodhikit.plugin` from the latest GitHub release and use Add → Upload plugin; that copy stays at its version.
- Source: https://support.claude.com/en/articles/13837440-use-plugins-in-claude ; README.md *Claude chats with your computer connected*
- Checked: 2026-11-07
- Status: verified

### Calling a plugin's skills in Claude
- Fact: in chat and Cowork, type `/` or click **+** to see a plugin's skills; in Cowork a command can be typed as `/plugin-name:command`. A plain-words request also starts a BodhiKit skill (docs/cowork-probe.md check 3).
- Source: https://support.claude.com/en/articles/13837440-use-plugins-in-claude ; docs/cowork-probe.md
- Checked: 2026-11-08
- Status: verified

### Hooks run only in Cowork and Claude Code
- Fact: plugin hooks and sub-agents run only in Cowork and Claude Code and appear greyed out in plain chat. BodhiKit's hooks deliver the learning-project rule and require the day's revision sheet. On claude.ai in a browser with the computer connected, they ran (docs/cowork-probe.md, 2026-10-22).
- Source: https://support.claude.com/en/articles/13837440-use-plugins-in-claude ; docs/cowork-probe.md
- Checked: 2026-11-07
- Status: verified

### Claude chats run in the cloud; a folder on the computer needs Claude Desktop open
- Fact: Cowork is part of every Claude surface and runs in a cloud sandbox. From 6 October 2026 on Pro, Max and Ultra there is no "only on your computer" option. Skills and plugins are available on desktop, web and mobile. A chat can reach folders on a computer only while the Claude Desktop app is open there ("Claude reaches only the folders you've connected, through the desktop app, and only while it's open"). Claude Desktop is listed for macOS, Windows and Linux (beta). Cowork is not available on Free.
- Source: https://support.claude.com/en/articles/15520349
- Checked: 2026-11-08
- Status: verified

### Tracked study in a Claude chat
- Fact: BodhiKit keeps the plan, review schedule and revision sheets only when Claude Desktop is open and the computer is ticked under **+** → **Devices** in that chat, with the `learningWithBodhi` folder allowed (the whole folder, not a subject inside it). Measured on claude.ai in Chrome with the Desktop app open; the Desktop app's own window was not tested.
- Source: docs/cowork-probe.md (2026-10-22 rerun) ; README.md
- Checked: 2026-11-07
- Status: verified

### A phone chat reaching the laptop's folder
- Fact: Anthropic says a phone can reach the computer's files only while the Desktop app is open on that machine. Whether a phone chat can tick the laptop under Devices and run BodhiKit tracked has not been tested.
- Source: https://support.claude.com/en/articles/15520349
- Checked: 2026-11-08
- Status: not verified (untested with BodhiKit; say so in the guide)

### Where to get the apps
- Fact: Claude Desktop for macOS and Windows (a separate Windows arm64 download, and a Microsoft Store listing; Linux in beta for Ubuntu and Debian) at claude.com/download; the iOS app from the App Store; other phones via claude.ai/mobile or the page's QR code. The page doesn't mention Google Play.
- Source: https://claude.com/download
- Checked: 2026-11-08
- Status: verified

### Claude's pricing page doesn't list plugins per plan
- Fact: the pricing page lists skills on every plan but has no row for plugins or Cowork. Cite the plugins article for plan eligibility, and the pricing page only for prices.
- Source: https://claude.com/pricing
- Checked: 2026-11-08
- Status: verified

## Claude Code

### Claude Code needs a paid plan or a Console account
- Fact: "Claude Code requires a Pro, Max, Ultra, Team, Enterprise, or Console account. The free claude.ai plan does not include Claude Code access." On Pro, Max and Ultra, usage limits are shared: "all activity in both tools counts against the same limits".
- Source: https://code.claude.com/docs/en/setup (*Authenticate*) ; https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan
- Checked: 2026-11-09
- Status: verified

### Installing Claude Code
- Fact: native installer, recommended: `curl -fsSL https://claude.ai/install.sh | bash` (macOS, Linux, WSL); `irm https://claude.ai/install.ps1 | iex` (Windows PowerShell); a CMD form too. Also Homebrew (`brew install --cask claude-code`) and WinGet. It shows no progress while downloading; check with `claude --version` in a new terminal. Native installs update themselves. Requirements: macOS 13.0+, Windows 10 1809+, Ubuntu 20.04+, Debian 10+; 4 GB+ RAM. On Windows, Git for Windows is optional (without it Claude Code uses PowerShell). First run of `claude` asks you to log in through the browser. Anthropic's *Terminal guide for new users* walks a first-time terminal user through it.
- Source: https://code.claude.com/docs/en/setup ; https://code.claude.com/docs/en/quickstart ; https://code.claude.com/docs/en/terminal-guide
- Checked: 2026-11-08
- Status: verified

### Installing a plugin in Claude Code
- Fact: in a session, `/plugin marketplace add <source>` (GitHub `owner/repo` or a full git URL) prints `Successfully added marketplace: <name>`. `/plugin install <plugin>@<marketplace>` opens the plugin's details; choose a scope ("Install for you (user scope)" is every project on this machine). The install summary says either `Plugin is now active.` or `Run /reload-plugins to apply.` Skills then appear as `/<plugin>:<skill>` when you type `/`. Third-party marketplaces don't auto-update by default: `/plugin` → **Marketplaces** → select it → **Update marketplace**.
- Source: https://code.claude.com/docs/en/discover-plugins
- Checked: 2026-11-09
- Status: verified

### BodhiKit's learning rule in Claude Code depends on the folder
- Fact: in Claude Code the learning-project rule (guide, don't solve; protected folders; safety) is injected at session start only when the working folder is inside, or holds, `learningWithBodhi`. A session started in another code repository is left alone, so Claude Code writes code there as usual. `~/learningWithBodhi` is on the default discovery path, so projects are found from any folder.
- Source: scripts/bodhi-session-context.py ; skills/state-ops/SKILL.md *Project Discovery Config*
- Checked: 2026-11-09
- Status: verified (repository)

## ChatGPT

### Plugins in ChatGPT
- Fact: "Select plugins are available in all plans"; some plugins need a paid plan. Add from the sidebar or chatgpt.com/plugins; call one from the Tools menu or by typing `@` and its name. On Enterprise and Edu, an administrator must enable plugins first. The page doesn't say whether ChatGPT picks a plugin by itself, which devices it works on, or anything about countries.
- Source: https://chatgpt.com/features/plugins/
- Checked: 2026-11-08
- Status: verified

### OpenAI's help article on plugins
- Fact: OpenAI's help article *Plugins in ChatGPT* is the step-by-step reference, but it returned HTTP 403 to the fetch tool. Use the features page above, or ask the maintainer to open it.
- Source: https://help.openai.com/en/articles/20001256-plugins-in-chatgpt
- Checked: 2026-11-08 (403 again; use "OpenAI's plugin docs on learn.chatgpt.com" below)
- Status: not verified (page wouldn't open)

### OpenAI's plugin docs on learn.chatgpt.com
- Fact: OpenAI's *Plugins* page (ChatGPT Learn): open the **Plugins** tab, search, open a plugin's details and "Select the plus button to install the plugin". "Type `@` to invoke the plugin or one of its bundled skills explicitly"; describing the task instead lets ChatGPT "choose the right installed tools for the task". "Plugins work in Chat and Work across ChatGPT on the web, desktop, and mobile." On mobile you use plugins your account already has; the page says installation happens on the web or in the desktop app (a learner's phone screenshot, below, showed an **Install plugin** button, so say "install on the web or desktop app" to be safe). It doesn't say how long an `@` mention lasts within a chat.
- Source: https://learn.chatgpt.com/docs/plugins
- Checked: 2026-11-08
- Status: verified

### What a learner's ChatGPT screens show
- Fact: in the phone app the page is titled **Plugins**, search lists each plugin with **+** (not installed) or **⋯** (installed), and a plugin's detail page has an **Install plugin** button. BodhiKit's subtitle there is "Learn through guided practice". In the desktop app, a **BodhiKit** chip stayed in the message box after BodhiKit was called. Seen on a learner's screenshots, not in OpenAI's docs; re-check before relying on the chip.
- Source: screenshots supplied by the maintainer (October 2026) ; docs/openai-submission.md (short description)
- Checked: 2026-11-08
- Status: verified (screenshots; the chip's behaviour is not documented)

### The BodhiKit listing
- Fact: BodhiKit is in ChatGPT's plugin directory, published by Abhaya Code Labs. The listing is a snapshot of the last approved upload: 1.26.1, confirmed published on 2026-11-07. Check `docs/openai-submission.md` for the current version before stating one.
- Source: docs/openai-submission.md ; commit a7eb6b8
- Checked: 2026-11-07
- Status: verified

### BodhiKit's availability by country in ChatGPT
- Fact: the countries the listing is offered in are set in OpenAI's portal and are not recorded in the repository. Third-party sources say some plugins are unavailable in the EEA, the UK or Switzerland; no OpenAI page confirmed it. For a learner outside the US, tell the maintainer to check the portal's availability settings, and give the learner a fallback (Claude).
- Source: docs/openai-submission.md *Availability* ; https://chatgpt.com/features/plugins/
- Checked: 2026-11-08: a user's screenshot (October 2026) shows BodhiKit installed and in use in Europe, so the third-party claims don't hold everywhere there. Other countries are still unknown.
- Status: not verified (not recorded; ask the maintainer)

### ChatGPT keeps nothing between chats
- Fact: in ChatGPT on the web, desktop app and phone, BodhiKit runs conversation-only. It teaches as usual, never claims progress was saved, and offers a summary to keep. The learner's log carries the plan and review dates.
- Source: docs/openai.md *Runtime behavior by platform* ; platforms/openai/bodhikit/references/openai-runtime.md
- Checked: 2026-11-07
- Status: verified

## Both

### Claude's prices (for a guide that compares the apps)
- Fact: claude.com/pricing lists Pro at $20 a month billed monthly, or $17 a month billed yearly ($200 up front); Max $100 and Ultra $200 a month. Prices are shown in US dollars and "don't include applicable tax". No student discount for individual plans; an Education plan is for institutions. Give the learner the page, and the price only with its date.
- Source: https://claude.com/pricing
- Checked: 2026-11-08
- Status: verified

### Where Claude is offered
- Fact: Anthropic's *Supported Regions Policy* lists the countries and regions where its products are available. Check the learner's country on that page.
- Source: https://www.anthropic.com/supported-countries
- Checked: 2026-11-08
- Status: verified
