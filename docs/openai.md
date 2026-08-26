# BodhiKit for Codex and ChatGPT

BodhiKit ships an isolated OpenAI-native package generated from the existing
Claude Code implementation. The Claude package remains the canonical source;
the build converts its learner workflows, knowledge bases, delegated roles,
state engine, and supported hooks without changing the Claude runtime files.

OpenAI's current plugin format and Claude conversion guidance are documented in
[Package your plugin](https://developers.openai.com/plugins/build/plugins) and
[Submit your Claude Code plugin](https://developers.openai.com/plugins/guides/submit-claude-plugin).

## Build the OpenAI package

From the repository root:

```bash
python3 platforms/openai/build_plugin.py
```

This creates the ignored build output at:

```text
dist/openai/bodhikit/
├── .codex-plugin/plugin.json
├── hooks/hooks.json
├── references/
│   ├── knowledge/       # 18 progressively loaded pedagogy/state references
│   ├── roles/           # 4 portable role procedures
│   └── openai-runtime.md
├── rules/
├── scripts/
│   ├── bodhi-state
│   ├── bodhi-session-context.py
│   ├── bodhi-stop-hook.py
│   └── bodhi-stop-hook-core.py
└── skills/              # 18 OpenAI Agent Skills
```

To also create an uploadable archive:

```bash
python3 platforms/openai/build_plugin.py \
  --archive dist/bodhikit-openai.zip
```

The archive contains one top-level `bodhikit/` directory and the native
`.codex-plugin/plugin.json` manifest.

## Install for Codex development

Codex installs plugins through a marketplace. For a local checkout, use the
built-in `$plugin-creator` skill to add the generated package to your personal
marketplace:

```text
$plugin-creator Add the existing plugin at <repo>/dist/openai/bodhikit to my
personal marketplace as bodhikit for local testing. Do not edit the canonical
Claude package.
```

Then install it:

```bash
codex plugin add bodhikit@personal
```

Restart or refresh Codex after rebuilding/reinstalling. Review and trust the
plugin's hooks when prompted; Codex does not trust newly installed plugin hooks
automatically.

Invoke a workflow naturally or explicitly, for example:

```text
$learn Help me learn Rust ownership from a JavaScript background.
$quiz Quiz me on the concepts due for review.
$reflect Help me close today's learning session.
```

## Install or test in ChatGPT

For local development in a supported ChatGPT Work/Desktop environment, use
`@plugin-creator` to add `dist/openai/bodhikit` to a personal marketplace, then
install BodhiKit from that marketplace source in the Plugin Directory.

For public submission, build `dist/bodhikit-openai.zip`, then use the
[OpenAI plugin submission portal](https://platform.openai.com/apps-manage).
Choose **Skills only**, upload the bundle, and complete the listing, prompts,
reviewer tests, availability, and attestations. The prepared listing copy and
five positive plus three negative test cases are in
[openai-submission.md](./openai-submission.md).

The submitting organization needs Apps Management write access and a verified
developer or business identity. Submission starts OpenAI review; after
approval, the publisher chooses when to make the plugin public.

After installation, mention the plugin and state the learning goal:

```text
@BodhiKit Help me learn SQL query planning through guided practice.
```

## Runtime behavior by platform

| Capability | Claude Code | Codex | ChatGPT |
|---|---|---|---|
| Learner workflows | 18 native skills | 18 generated Agent Skills | Same 18 Agent Skills |
| Pedagogy knowledge | 18 model-only skills | 18 progressive references | 18 progressive references |
| Delegated roles | 4 Claude agents | Portable procedures; delegation optional | Portable procedures in the current conversation |
| Deterministic state | Local `bodhi-state` | Same script, copied byte-for-byte | Local when shell/files are exposed; otherwise conversation-only |
| SessionStart/Stop hooks | Native | Native command-hook adapters after trust | Not available; core workflow does not depend on hooks |
| Cross-chat/device persistence | Local project files | Local project files | Requires a future remote MCP state service |

In ChatGPT conversation-only mode, BodhiKit preserves the teaching interaction
but never claims that progress or revision files were persisted. It can return a
compact learning-state summary for the learner to save and reuse.

## Verify the conversion

Run the full repository gate:

```bash
bash dev/check.sh
```

Or run the OpenAI checks directly:

```bash
python3 dev/eval/test_openai_plugin.py
```

The OpenAI suite verifies package isolation, manifest/version synchronization,
18 workflow conversions, all knowledge and role mappings, source-platform token
removal, archive structure, byte-for-byte state-engine reuse, Codex-shaped
SessionStart and Stop events, ChatGPT hook independence, and schema/revision
enforcement.
