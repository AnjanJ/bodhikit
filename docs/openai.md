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

The public-directory archive contains one top-level `bodhikit/` directory and
the native `.codex-plugin/plugin.json` manifest. It excludes lifecycle hooks,
their helper scripts, Python caches, and the internal build marker. The
generated directory retains the optional hooks for local Codex development.

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
Open the existing BodhiKit listing, upload the bundle as a skills-only update,
and complete the listing, prompts, applicable reviewer tests, availability, and
attestations. The prepared listing copy and
five positive plus three negative test cases are in
[openai-submission.md](./openai-submission.md).

The submitting organization needs Apps Management write access and a verified
developer or business identity. Submission starts OpenAI review; after
approval, the publisher chooses when to make the plugin public.

BodhiKit is listed publicly on the ChatGPT plugin marketplace. That listing is
a snapshot of the bundle last uploaded, not a link to this repository, so
**every release must be re-uploaded there** after the tag is pushed (release
checklist step 7 in `CLAUDE.md`): rebuild `dist/bodhikit-openai.zip` from the
tagged tree, then submit the new version through the same portal. Until that
upload is approved and published, ChatGPT users are on the previous release.

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
| SessionStart/Stop hooks | Native | Optional adapters in local directory builds after trust; omitted from the public ZIP | Not available; the runtime adapter carries their duties explicitly (the learning-project rule on first learner-file access; `verify` and the revision sheet at close) |
| Cross-chat/device persistence | Local project files | Local project files | Requires a future remote MCP state service |

In ChatGPT conversation-only mode, BodhiKit preserves the teaching interaction
but never claims that progress or revision files were persisted. It can return a
compact learning-state summary for the learner to save and reuse.

In ChatGPT local state mode (a desktop with a shell and a writable folder, which
is how the maintainer runs it) the state engine is the same script as on Claude
Code, byte for byte. What ChatGPT lacks is the two hooks, so the runtime adapter
(`references/openai-runtime.md`) states their duties as explicit steps: read the
packaged learning-project rule the first time a workflow touches a learner
project, and close every study session with `bodhi-state verify` and the day's
revision sheet before the final message. Every source sentence that promised
"the Stop hook checks" is rewritten at build time to point at that procedure;
the package test fails if one survives.

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

That is the deterministic certification for the OpenAI runtimes. The live-model
evals in `dev/eval/run-llm-evals.sh` certify only the executor they print in
their header. Since 1.23.1 they can run through headless Codex:

```bash
BODHI_EVAL_RUNTIME=codex dev/eval/run-llm-evals.sh quiz        # one scenario
BODHI_EVAL_RUNTIME=codex dev/eval/run-llm-evals.sh             # all of them
```

The runner builds `dist/openai/bodhikit` if it is missing, lays a sandboxed
`CODEX_HOME` out as that package (so `<BODHIKIT_PLUGIN_ROOT>` resolves exactly
as the adapter prescribes, with no marketplace registration), copies only
`auth.json` and `config.toml` from the real `CODEX_HOME`, and asserts the same
file state as the Claude runs. `BODHI_EVAL_MODEL` is optional; unset, Codex's
configured default runs and the header says so. The runner's `codex exec`
flags were confirmed against codex-cli 0.162.1 on the first local run
(2026-10-15). The run table in `dev/eval/README.md` is the record of what has
passed on an OpenAI executor: the executor-discipline group and the two 1.24.0
fidelity scenarios as of that date, no grading scenario yet. The byte-for-byte
state engine says nothing about whether the executor calls it; only those runs
do.

ChatGPT has no headless interface, so it stays on the manual smoke test: before
re-uploading a release, run one writing skill such as `$quiz` against a copy of
`dev/eval/fixtures/v2-project` in a ChatGPT session with a shell, and check the
result with `dev/eval/assert_scenario.py`, so the package is known to load,
write state, and close with `verify` and a revision sheet on that runtime.
