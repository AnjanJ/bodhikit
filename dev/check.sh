#!/usr/bin/env bash
# dev/check.sh — bodhikit authoring-contract lint
#
# Verifies the contract documented in CLAUDE.md. Bash, no deps.
# Exit 0 = clean. Exit 1 = violations found.

set -u
cd "$(dirname "$0")/.." || exit 2

fail=0
note() { printf '  %s\n' "$1"; }
err() { printf 'FAIL: %s\n' "$1"; fail=1; }
ok() { printf 'OK:   %s\n' "$1"; }

# ---------------------------------------------------------------------------
# 1. Manifests exist and versions agree
# ---------------------------------------------------------------------------
plugin_v=$(grep -E '"version"' .claude-plugin/plugin.json | head -1 | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')
mp_top_v=$(grep -E '"version"' .claude-plugin/marketplace.json | sed -n '1p' | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')
mp_plugin_v=$(grep -E '"version"' .claude-plugin/marketplace.json | sed -n '2p' | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')

if [ -z "$plugin_v" ]; then
  err "plugin.json missing version"
elif [ "$plugin_v" != "$mp_top_v" ] || [ "$plugin_v" != "$mp_plugin_v" ]; then
  err "version drift: plugin.json=$plugin_v marketplace.metadata=$mp_top_v marketplace.plugins[0]=$mp_plugin_v"
else
  ok "version consistent ($plugin_v)"
fi

# ---------------------------------------------------------------------------
# 2. Skill frontmatter contract
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md; do
  if ! head -10 "$f" | grep -q '^description:'; then
    err "$f missing 'description:' in frontmatter"
  fi
  if ! head -10 "$f" | grep -q '^user-invocable: true'; then
    err "$f missing 'user-invocable: true'"
  fi
  if ! grep -q 'teaching-personality' "$f"; then
    err "$f does not reference teaching-personality KB"
  fi
done

# ---------------------------------------------------------------------------
# 3. Agent-using skills must include mandate phrase and Fallback
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md; do
  if grep -q 'Agent tool' "$f"; then
    if ! grep -q 'You MUST use the Agent tool' "$f"; then
      err "$f uses an Agent but lacks the literal mandate phrase"
    fi
    if ! grep -qi '\*\*Fallback' "$f"; then
      err "$f uses an Agent but has no **Fallback:** paragraph"
    fi
  fi
done

# ---------------------------------------------------------------------------
# 4. Files that touch tracking shapes must reference state-schema
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md agents/*.md rules/*.md; do
  # state-schema KB itself is allowed to redeclare shapes
  case "$f" in *state-schema*) continue;; esac
  if grep -qE 'state\.json|spaced-review\.json|progress\.md|bodhi-profile' "$f"; then
    if ! grep -q 'state-schema' "$f"; then
      err "$f touches tracking files but does not reference state-schema KB"
    fi
  fi
done

# ---------------------------------------------------------------------------
# 5. Files that touch Leitner boxes must reference spaced-repetition KB
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md agents/*.md rules/*.md; do
  case "$f" in *spaced-repetition*) continue;; esac
  if grep -qE 'Box [0-9]|Leitner' "$f"; then
    if ! grep -q 'spaced-repetition' "$f"; then
      err "$f mentions Leitner/boxes but does not reference spaced-repetition KB"
    fi
  fi
done

# ---------------------------------------------------------------------------
# 6. Voice rules MUST NOT be restated outside teaching-personality KB
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md agents/*.md rules/*.md; do
  # The personality KB itself is the canonical home; rule file is the path-scoped trigger
  # and may carry a one-line directive. Everywhere else, restating is drift.
  case "$f" in *teaching-personality*) continue;; esac
  if grep -qE 'Oogway.*Yoda.*Buddha|Buddha.*Ambedkar.*Oogway|Yoda.*Buddha.*Ambedkar' "$f"; then
    err "$f restates the personality list inline — reference the KB instead"
  fi
done

# ---------------------------------------------------------------------------
# 7. Agent frontmatter contract
# ---------------------------------------------------------------------------
for f in agents/*.md; do
  if ! head -10 "$f" | grep -q '^name:'; then
    err "$f missing 'name:' in frontmatter"
  fi
  if ! head -10 "$f" | grep -qE '^model: (sonnet|haiku|opus)'; then
    err "$f missing or invalid 'model:'"
  fi
  if ! head -15 "$f" | grep -q 'disallowedTools'; then
    err "$f missing disallowedTools (agents should be read-only)"
  fi
done

# ---------------------------------------------------------------------------
# 8. KB frontmatter contract
# ---------------------------------------------------------------------------
for f in knowledge/*/SKILL.md; do
  if ! head -10 "$f" | grep -q '^user-invocable: false'; then
    err "$f must declare 'user-invocable: false'"
  fi
done

# ---------------------------------------------------------------------------
# 9. README skill count sanity (best-effort)
# ---------------------------------------------------------------------------
declared=$(grep -oE 'Skills \([0-9]+\)' README.md | head -1 | grep -oE '[0-9]+')
actual=$(find skills -name SKILL.md | wc -l | tr -d ' ')
if [ -n "$declared" ] && [ "$declared" != "$actual" ]; then
  err "README says Skills ($declared) but $actual SKILL.md files exist under skills/"
fi

# ---------------------------------------------------------------------------
echo
if [ "$fail" -eq 0 ]; then
  echo "All checks passed."
  exit 0
else
  echo "Contract violations above."
  exit 1
fi
