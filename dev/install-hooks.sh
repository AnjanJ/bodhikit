#!/usr/bin/env bash
# dev/install-hooks.sh — install the pre-commit hook for bodhikit authoring lint.
# Run once after cloning, or whenever the hook needs to be refreshed.
#
# This is dev-only. End users installing the plugin never see this.

set -e
cd "$(dirname "$0")/.."

mkdir -p .git/hooks
cat > .git/hooks/pre-commit <<'HOOK'
#!/usr/bin/env bash
# bodhikit pre-commit — runs the authoring-contract lint.
exec "$(git rev-parse --show-toplevel)/dev/check.sh"
HOOK
chmod +x .git/hooks/pre-commit

echo "Installed .git/hooks/pre-commit -> dev/check.sh"
