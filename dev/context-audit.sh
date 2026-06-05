#!/usr/bin/env bash
# dev/context-audit.sh — measure context cost across skills, agents, KBs, rules,
# and tracking files. Writes a ranked report to dev/context-audit.txt.
#
# Read-only. No edits to plugin files. No edits to user data.
#
# Sections:
#   1. Skills — cold-fire load (bytes), top-level vs phase-scoped KB refs.
#   2. KBs — size and inbound references.
#   3. Agents and rules.
#   4. Always-loaded floor (settings + rules active inside learningWithBodhi/).
#   5. Per-skill tracking-file read classification:
#        - unconditional   (top-of-file or unguarded mention)
#        - phase-conditional (inside ## Phase header)
#        - branch-conditional (inside an "if" / "when" / "should" guard)
#   6. Demotion candidates — top-of-file KB refs only used inside one phase.
#   7. Duplicate phrases (>=60 chars, in 2+ files).
#   8. Tracking-file projection — scans docs/example-project/ by default; pass
#      --user-data <path> to score a real learningWithBodhi/ root. Reports
#      current size + projected size at 100 / 200 sessions.
#   9. Unified pollution score — skill bytes + eager KB bytes + sum of
#      (unconditional tracking-file reads × projected size at 100 sessions).
#      Ranked list = the punch list driving the skill-refactor PRs.

set -u
cd "$(dirname "$0")/.." || exit 2

out=dev/context-audit.txt
: > "$out"

# Parse --user-data <path>.
user_data=""
while [ $# -gt 0 ]; do
  case "$1" in
    --user-data)
      shift
      user_data="${1:-}"
      ;;
    --user-data=*)
      user_data="${1#--user-data=}"
      ;;
  esac
  shift || true
done

# Default tracking-file source for projection: the in-repo example project.
if [ -z "$user_data" ]; then
  tracking_root="docs/example-project"
  tracking_label="docs/example-project (in-repo sample)"
else
  tracking_root="$user_data"
  tracking_label="$user_data (user data)"
fi

emit() { printf '%s\n' "$1" | tee -a "$out" >/dev/null; }
emit_only() { printf '%s\n' "$1" >> "$out"; }

emit "================================================================"
emit "bodhikit context audit  ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
emit "tracking-file source: $tracking_label"
emit "================================================================"
emit ""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
body_after_frontmatter() {
  awk 'BEGIN{n=0} /^---$/{n++; next} n>=2 || (n==1 && NR>1) {print}' "$1"
}

top_of_body() {
  body_after_frontmatter "$1" | head -25
}

# Tracking-file names this audit knows about. v2 schema (1.7.0).
tracking_files="state.json progress.md spaced-review.json resources.md plan plan.md assessment.md assessments assessment-history.json .bodhi-profile.json .bodhi-profile.projects.json"

# KB names declared in knowledge/.
kb_names=$(find knowledge -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)

# ---------------------------------------------------------------------------
# 1. SKILLS — per-skill breakdown (cold-fire load)
# ---------------------------------------------------------------------------
emit "## 1. Skills — sorted by estimated cold-fire load (bytes)"
emit ""
emit "$(printf '%-22s %6s %6s %6s %6s %10s' SKILL LINES BYTES TOP_KB PHASE_KB COLD_LOAD)"
emit "$(printf '%-22s %6s %6s %6s %6s %10s' ------ ----- ----- ------ -------- ---------)"

tmpsort=$(mktemp)
for f in skills/*/SKILL.md; do
  name=$(basename "$(dirname "$f")")
  lines=$(wc -l < "$f" | tr -d ' ')
  bytes=$(wc -c < "$f" | tr -d ' ')

  top=$(top_of_body "$f")
  rest=$(body_after_frontmatter "$f" | tail -n +26)

  top_kbs=""
  phase_kbs=""
  for kb in $kb_names; do
    if printf '%s' "$top" | grep -q "\`$kb\`"; then
      top_kbs="$top_kbs $kb"
    elif printf '%s' "$rest" | grep -q "\`$kb\`"; then
      phase_kbs="$phase_kbs $kb"
    fi
  done

  top_count=$(printf '%s' "$top_kbs" | wc -w | tr -d ' ')
  phase_count=$(printf '%s' "$phase_kbs" | wc -w | tr -d ' ')

  cold=$bytes
  for kb in $top_kbs; do
    kbfile="knowledge/$kb/SKILL.md"
    if [ -f "$kbfile" ]; then
      kbbytes=$(wc -c < "$kbfile" | tr -d ' ')
      cold=$((cold + kbbytes))
    fi
  done

  printf '%010d|%-22s %6d %6d %6d %6d %10d|%s|%s\n' \
    "$cold" "$name" "$lines" "$bytes" "$top_count" "$phase_count" "$cold" \
    "${top_kbs# }" "${phase_kbs# }" >> "$tmpsort"
done

sort -r "$tmpsort" | while IFS='|' read -r _key row top_list phase_list; do
  emit "$row"
  [ -n "$top_list" ]   && emit "    top-level KBs : $top_list"
  [ -n "$phase_list" ] && emit "    phase-scoped  : $phase_list"
done
rm -f "$tmpsort"

emit ""

# ---------------------------------------------------------------------------
# 2. KBs — per-KB size and inbound references
# ---------------------------------------------------------------------------
emit "## 2. Knowledge bases — sorted by size (largest first)"
emit ""
emit "$(printf '%-32s %6s %6s %5s' KB LINES BYTES IN_REF)"
emit "$(printf '%-32s %6s %6s %5s' --- ----- ----- ------)"

tmpsort=$(mktemp)
for f in knowledge/*/SKILL.md; do
  name=$(basename "$(dirname "$f")")
  lines=$(wc -l < "$f" | tr -d ' ')
  bytes=$(wc -c < "$f" | tr -d ' ')
  inref=$(grep -lE "\`$name\`" skills/*/SKILL.md agents/*.md rules/*.md 2>/dev/null | wc -l | tr -d ' ')
  printf '%010d|%-32s %6d %6d %5d\n' "$bytes" "$name" "$lines" "$bytes" "$inref" >> "$tmpsort"
done

sort -r "$tmpsort" | while IFS='|' read -r _key row; do
  emit "$row"
done
rm -f "$tmpsort"

emit ""

# ---------------------------------------------------------------------------
# 3. Agents and rules
# ---------------------------------------------------------------------------
emit "## 3. Agents — size and KB references"
emit ""
emit "$(printf '%-22s %6s %6s %s' AGENT LINES BYTES KBS)"
for f in agents/*.md; do
  name=$(basename "$f" .md)
  lines=$(wc -l < "$f" | tr -d ' ')
  bytes=$(wc -c < "$f" | tr -d ' ')
  kbs=""
  for kb in $kb_names; do
    grep -q "\`$kb\`" "$f" && kbs="$kbs $kb"
  done
  emit "$(printf '%-22s %6d %6d %s' "$name" "$lines" "$bytes" "${kbs# }")"
done

emit ""
emit "## Rules — size and what loads with them"
emit ""
for f in rules/*.md; do
  lines=$(wc -l < "$f" | tr -d ' ')
  bytes=$(wc -c < "$f" | tr -d ' ')
  kbs=""
  for kb in $kb_names; do
    grep -q "\`$kb\`" "$f" && kbs="$kbs $kb"
  done
  emit "  $f — $lines lines, $bytes bytes, KBs:${kbs:- (none)}"
done

emit ""

# ---------------------------------------------------------------------------
# 4. Always-loaded floor
# ---------------------------------------------------------------------------
emit "## 4. Always-loaded floor"
emit ""
floor_total=0
if [ -f settings.json ]; then
  b=$(wc -c < settings.json | tr -d ' ')
  emit "  settings.json — $b bytes"
  floor_total=$((floor_total + b))
fi
for f in rules/*.md; do
  b=$(wc -c < "$f" | tr -d ' ')
  emit "  $f — $b bytes (active inside learningWithBodhi/)"
  floor_total=$((floor_total + b))
done
emit "  TOTAL floor (inside a learning project): $floor_total bytes"

emit ""

# ---------------------------------------------------------------------------
# 5. Per-skill tracking-file read classification
# ---------------------------------------------------------------------------
# For each skill, find references to each tracking-file name. For each
# reference, walk backward through the skill body to determine context:
#   - inside a "## Phase" header section?
#   - inside a guarded paragraph (line containing "if ", "when ", "should ",
#     "MAY ", "rare", "reach", "only when", "branch", or starting with "If")?
# Classification:
#   unconditional      = mentioned but neither phase- nor branch-guarded
#   phase-conditional  = inside a Phase section, no branch guard
#   branch-conditional = inside (or one line after) a branch guard
# ---------------------------------------------------------------------------
emit "## 5. Per-skill tracking-file read classification"
emit ""
emit "  Legend: U = unconditional, P = phase-conditional, B = branch-conditional"
emit ""

# Build the column header.
hdr_files=""
for tf in $tracking_files; do
  # Truncate long names for the header to keep it readable.
  short=$(printf '%s' "$tf" | cut -c1-12)
  hdr_files="$hdr_files $(printf '%-12s' "$short")"
done
emit "$(printf '%-22s%s' SKILL "$hdr_files")"
emit "$(printf '%-22s%s' ------ "$(printf '%s' "$hdr_files" | sed 's/[^ ]/-/g')")"

# Per-skill classifier.
classify_skill() {
  local f="$1"
  body_after_frontmatter "$f" > /tmp/.audit-skill-body 2>/dev/null

  local row=""
  for tf in $tracking_files; do
    # Build a regex-safe needle. Match the literal name; escape dots.
    local needle=$(printf '%s' "$tf" | sed 's/[.]/\\./g')
    # Scan body line by line, tracking phase context and branch guards.
    local class=""
    local in_phase=0
    local branch_window=0
    while IFS= read -r line; do
      # Phase header detection.
      case "$line" in
        \#\#\ Phase*|\#\#\ Phase*) in_phase=1 ;;
        \#\#\ *) in_phase=0 ;;
      esac
      # Branch guard detection — set a 2-line window where a mention counts
      # as branch-conditional.
      case "$line" in
        *"only when"*|*"only if"*|*"reach for"*|*"reaches for"*|*"if learner"*|\
        *"when the learner"*|*"rarely"*|*"MAY "*|*"may invoke"*|*"may pull"*|\
        *"explicitly"*|*"branch"*|*"if the learner"*|*"If the learner"*|\
        *"If "*|*" if "*)
          branch_window=2
          ;;
      esac

      # Check for the tracking file mention.
      if printf '%s' "$line" | grep -qE "$needle"; then
        if [ "$branch_window" -gt 0 ]; then
          class="B"; break
        elif [ "$in_phase" -eq 1 ]; then
          class="P"; break
        else
          class="U"; break
        fi
      fi

      if [ "$branch_window" -gt 0 ]; then
        branch_window=$((branch_window - 1))
      fi
    done < /tmp/.audit-skill-body
    [ -z "$class" ] && class="."
    row="$row $(printf '%-12s' "$class")"
  done
  echo "$row"
}

for f in skills/*/SKILL.md; do
  name=$(basename "$(dirname "$f")")
  row=$(classify_skill "$f")
  emit "$(printf '%-22s%s' "$name" "$row")"
done
rm -f /tmp/.audit-skill-body

emit ""

# ---------------------------------------------------------------------------
# 6. Demotion candidates — top-of-file KB refs only used inside one phase
# ---------------------------------------------------------------------------
emit "## 6. Demotion candidates — KBs declared top-of-file but referenced only inside one phase"
emit ""

found_demotion=0
for f in skills/*/SKILL.md; do
  name=$(basename "$(dirname "$f")")
  top=$(top_of_body "$f")
  rest=$(body_after_frontmatter "$f" | tail -n +26)

  # For each KB referenced at the top, count its phase-localized mentions.
  for kb in $kb_names; do
    if ! printf '%s' "$top" | grep -q "\`$kb\`"; then
      continue
    fi
    # Skip universal references that every skill loads.
    case "$kb" in
      teaching-personality|state-schema) continue ;;
    esac
    # Count the phase sections (## Phase ...) in this skill, and the count of
    # those sections that mention this KB.
    phase_hits=$(printf '%s' "$rest" | awk -v kb="\`$kb\`" '
      /^## Phase/ { phase++; mention=0 }
      $0 ~ kb && phase > 0 && mention == 0 { hits++; mention=1 }
      END { print hits+0 }
    ')
    total_phases=$(printf '%s' "$rest" | grep -cE '^## Phase' || true)
    [ -z "$total_phases" ] && total_phases=0

    # Demotion candidate: KB is referenced top-of-file but also only inside
    # ONE phase (or zero — meaning the top reference is the only use).
    if [ "$phase_hits" -le 1 ] && [ "$total_phases" -ge 2 ]; then
      kbfile="knowledge/$kb/SKILL.md"
      kbbytes=0
      [ -f "$kbfile" ] && kbbytes=$(wc -c < "$kbfile" | tr -d ' ')
      emit "  $name: \`$kb\` (${kbbytes}b) — referenced top-of-file; used in $phase_hits / $total_phases phases"
      found_demotion=1
    fi
  done
done

if [ "$found_demotion" -eq 0 ]; then
  emit "  (none — every top-of-file KB ref is used across multiple phases)"
fi

emit ""

# ---------------------------------------------------------------------------
# 7. Duplicate phrases >=60 chars across 2+ files
# ---------------------------------------------------------------------------
emit "## 7. Duplicated phrases (>=60 chars, in 2+ files)"
emit ""

tmplines=$(mktemp)
for f in skills/*/SKILL.md agents/*.md rules/*.md knowledge/*/SKILL.md; do
  awk -v file="$f" '
    /^[[:space:]]*$/ {next}
    /^[[:space:]]*```/ {next}
    /^[[:space:]]*[#|]/ {next}
    {
      line=$0
      sub(/^[[:space:]]+/, "", line)
      if (length(line) >= 60) print line "\t" file
    }
  ' "$f"
done > "$tmplines"

sort "$tmplines" | awk -F'\t' '
{
  key=$1; file=$2
  if (key != prev) {
    if (count >= 2) {
      printf "%s\n", prev
      for (i in files) printf "    %s\n", i
      printf "\n"
    }
    count=0; delete files; prev=key
  }
  if (!(file in files)) { files[file]=1; count++ }
}
END {
  if (count >= 2) {
    printf "%s\n", prev
    for (i in files) printf "    %s\n", i
  }
}' >> "$out"

rm -f "$tmplines"

emit ""

# ---------------------------------------------------------------------------
# 8. Tracking-file projection
# ---------------------------------------------------------------------------
emit "## 8. Tracking-file projection ($tracking_label)"
emit ""

if [ ! -d "$tracking_root" ]; then
  emit "  (tracking root not found: $tracking_root)"
  emit ""
else
  # Resolve session count for projection: read first state.json under the
  # tracking root. Fallback to 1 if none / unparseable.
  state_file=$(find "$tracking_root" -name state.json -type f -print -quit 2>/dev/null)
  sessions=1
  if [ -n "$state_file" ] && [ -f "$state_file" ]; then
    # Extract totalSessions from JSON without jq dependency.
    val=$(grep -E '"totalSessions"' "$state_file" 2>/dev/null | head -1 | sed -E 's/.*: *([0-9]+).*/\1/')
    if [ -n "$val" ] && [ "$val" -ge 1 ] 2>/dev/null; then
      sessions=$val
    fi
  fi

  emit "  Sessions observed (from first state.json found): $sessions"
  emit ""
  emit "$(printf '%-42s %10s %12s %12s' FILE BYTES_NOW PROJ_100_SES PROJ_200_SES)"
  emit "$(printf '%-42s %10s %12s %12s' ---- --------- ------------ ------------)"

  # Per-file growth model:
  #   - Files that grow per-session (live narrative): linear in session count.
  #     progress.md, .bodhi-profile.json, assessment-history.json
  #   - Files bounded by housekeeping (live + summary): grow to ~5 KB then
  #     plateau as summary block absorbs entries. Project as min(current * factor, 8 KB).
  #     progress.md (after migration), assessments/latest.md
  #   - Files bounded by content (sectional or static): flat. plan/, resources.md, state.json
  #   - Concept-driven: spaced-review.json grows with concepts not sessions; project
  #     using a 2x heuristic for 200 sessions (concept introduction tapers).
  #
  # Project per file by name. Default model: linear in session count.

  while IFS= read -r f; do
    rel="${f#$tracking_root/}"
    size=$(wc -c < "$f" | tr -d ' ')
    base=$(basename "$f")

    # Pick a growth factor.
    case "$base" in
      state.json|state.recent.json)
        # Slim, bounded. Projection ~= current.
        p100=$size; p200=$size
        ;;
      progress.md)
        # v2 live + summary: bounded by housekeep. ~= current + summary growth.
        # Per-session summary grows ~150 bytes; cap at ~10 KB.
        if [ "$sessions" -ge 1 ]; then
          per_sess_growth=150
          add100=$(( (100 - sessions) * per_sess_growth ))
          add200=$(( (200 - sessions) * per_sess_growth ))
          [ "$add100" -lt 0 ] && add100=0
          [ "$add200" -lt 0 ] && add200=0
          p100=$(( size + add100 ))
          p200=$(( size + add200 ))
          [ "$p100" -gt 10240 ] && p100=10240
          [ "$p200" -gt 10240 ] && p200=10240
        else
          p100=$size; p200=$size
        fi
        ;;
      assessment.md)
        # v1 monolithic — pre-migration. Linear growth assumed.
        if [ "$sessions" -ge 1 ]; then
          per=$((size / sessions))
          [ "$per" -lt 100 ] && per=100
          p100=$((per * 100))
          p200=$((per * 200))
        else
          p100=$size; p200=$size
        fi
        ;;
      spaced-review.json)
        # Concept count grows with sessions but tapers. Use 2x heuristic over 200 sessions.
        if [ "$sessions" -ge 1 ]; then
          per_sess=$((size / sessions))
          [ "$per_sess" -lt 100 ] && per_sess=100
          # Tapered growth: linear until 50 sessions, then 1/4 rate.
          if [ "$sessions" -lt 50 ]; then
            p100=$(( size + (50 - sessions) * per_sess + 50 * per_sess / 4 ))
            p200=$(( size + (50 - sessions) * per_sess + 150 * per_sess / 4 ))
          else
            p100=$(( size + (100 - sessions) * per_sess / 4 ))
            p200=$(( size + (200 - sessions) * per_sess / 4 ))
          fi
          [ "$p100" -lt "$size" ] && p100=$size
          [ "$p200" -lt "$size" ] && p200=$size
        else
          p100=$size; p200=$size
        fi
        ;;
      assessment-history.json)
        # Append-only, linear.
        if [ "$sessions" -ge 1 ]; then
          per=$((size / sessions))
          [ "$per" -lt 50 ] && per=50
          p100=$((per * 100))
          p200=$((per * 200))
        else
          p100=$size; p200=$size
        fi
        ;;
      plan.md|README.md|plan-README.md)
        # Static after generation.
        p100=$size; p200=$size
        ;;
      resources.md)
        # Slow growth; ~10% over 200 sessions.
        p100=$size
        p200=$(( size + size / 10 ))
        ;;
      .bodhi-profile.json)
        # v2 slim — bounded. Project ~= current.
        p100=$size; p200=$size
        ;;
      .bodhi-profile.projects.json)
        # Grows with project count, NOT sessions. Project ~= current * 5 over time.
        p100=$(( size * 3 ))
        p200=$(( size * 5 ))
        ;;
      *)
        # Default: linear with sessions.
        if [ "$sessions" -ge 1 ]; then
          per=$((size / sessions))
          [ "$per" -lt 50 ] && per=50
          p100=$((per * 100))
          p200=$((per * 200))
        else
          p100=$size; p200=$size
        fi
        ;;
    esac

    emit "$(printf '%-42s %10d %12d %12d' "$rel" "$size" "$p100" "$p200")"
  done < <(find "$tracking_root" \( -path '*/.bodhi/*' -o -name '.bodhi-profile*.json' \) -type f \( -name '*.json' -o -name '*.md' \) ! -path '*/.bodhi/archive/*' ! -path '*/.pre-1.7.0-backup/*' | sort)

  emit ""
fi

# ---------------------------------------------------------------------------
# 9. Unified pollution score
# ---------------------------------------------------------------------------
# For each skill: cold-fire bytes + sum over each tracking file the skill
# reads UNCONDITIONALLY of that file's projected 100-session size.
# ---------------------------------------------------------------------------
emit "## 9. Unified pollution score — punch list (highest first)"
emit ""
emit "  Score = cold-fire skill bytes + sum of unconditional tracking-file reads"
emit "          (using projected size at 100 sessions from section 8)."
emit ""
emit "$(printf '%-22s %10s %10s %10s' SKILL COLD_FIRE WARM_READS TOTAL)"
emit "$(printf '%-22s %10s %10s %10s' ------ --------- ---------- -----)"

# Pre-compute projected sizes per tracking-file basename.
declare -A proj100 2>/dev/null || true
proj_get() {
  # Bash 3.2 compatibility on macOS — use a flat file as lookup.
  local key="$1"
  local file=/tmp/.audit-proj
  [ -f "$file" ] && grep -E "^$key " "$file" | awk '{print $2}'
}
: > /tmp/.audit-proj
if [ -d "$tracking_root" ]; then
  while IFS= read -r f; do
    base=$(basename "$f")
    size=$(wc -c < "$f" | tr -d ' ')
    # Same projection as section 8, simplified: re-use base for keying.
    case "$base" in
      state.json|state.recent.json|plan.md|README.md|.bodhi-profile.json|resources.md)
        p=$size
        ;;
      *)
        if [ "$sessions" -ge 1 ]; then
          per=$((size / sessions))
          [ "$per" -lt 100 ] && per=100
          p=$((per * 100))
          [ "$base" = "progress.md" ] && [ "$p" -gt 10240 ] && p=10240
        else
          p=$size
        fi
        ;;
    esac
    echo "$base $p" >> /tmp/.audit-proj
  done < <(find "$tracking_root" \( -path '*/.bodhi/*' -o -name '.bodhi-profile*.json' \) -type f \( -name '*.json' -o -name '*.md' \) ! -path '*/.bodhi/archive/*' ! -path '*/.pre-1.7.0-backup/*')
fi

tmpsort=$(mktemp)
for f in skills/*/SKILL.md; do
  name=$(basename "$(dirname "$f")")
  bytes=$(wc -c < "$f" | tr -d ' ')

  # Recompute cold-fire load (same as section 1).
  top=$(top_of_body "$f")
  cold=$bytes
  for kb in $kb_names; do
    if printf '%s' "$top" | grep -q "\`$kb\`"; then
      kbfile="knowledge/$kb/SKILL.md"
      [ -f "$kbfile" ] && cold=$((cold + $(wc -c < "$kbfile" | tr -d ' ')))
    fi
  done

  # Sum unconditional tracking-file reads.
  warm=0
  body_after_frontmatter "$f" > /tmp/.audit-skill-body
  for tf in $tracking_files; do
    needle=$(printf '%s' "$tf" | sed 's/[.]/\\./g')
    # Same classifier logic as section 5, but only counting U.
    class=""
    in_phase=0
    branch_window=0
    while IFS= read -r line; do
      case "$line" in
        \#\#\ Phase*) in_phase=1 ;;
        \#\#\ *) in_phase=0 ;;
      esac
      case "$line" in
        *"only when"*|*"only if"*|*"reach for"*|*"reaches for"*|*"if learner"*|\
        *"when the learner"*|*"rarely"*|*"MAY "*|*"may invoke"*|*"may pull"*|\
        *"explicitly"*|*"branch"*|*"if the learner"*|*"If the learner"*|\
        *"If "*|*" if "*)
          branch_window=2
          ;;
      esac
      if printf '%s' "$line" | grep -qE "$needle"; then
        if [ "$branch_window" -gt 0 ]; then class="B"; break
        elif [ "$in_phase" -eq 1 ]; then class="P"; break
        else class="U"; break
        fi
      fi
      if [ "$branch_window" -gt 0 ]; then branch_window=$((branch_window - 1)); fi
    done < /tmp/.audit-skill-body

    if [ "$class" = "U" ]; then
      p=$(proj_get "$tf")
      [ -z "$p" ] && p=0
      warm=$((warm + p))
    fi
  done

  total=$((cold + warm))
  printf '%010d|%-22s %10d %10d %10d\n' "$total" "$name" "$cold" "$warm" "$total" >> "$tmpsort"
done
rm -f /tmp/.audit-skill-body /tmp/.audit-proj

sort -r "$tmpsort" | while IFS='|' read -r _key row; do
  emit "$row"
done
rm -f "$tmpsort"

emit ""

# ---------------------------------------------------------------------------
# 10. Stdout summary
# ---------------------------------------------------------------------------
total_skills=$(find skills -name SKILL.md | wc -l | tr -d ' ')
total_kbs=$(find knowledge -name SKILL.md | wc -l | tr -d ' ')
total_skill_bytes=$(find skills -name SKILL.md -exec cat {} + | wc -c | tr -d ' ')
total_kb_bytes=$(find knowledge -name SKILL.md -exec cat {} + | wc -c | tr -d ' ')

echo ""
echo "Report written to: $out"
echo ""
echo "  Skills: $total_skills files, $total_skill_bytes bytes total"
echo "  KBs:    $total_kbs files, $total_kb_bytes bytes total"
echo ""
echo "Top 5 punch-list entries (unified pollution score):"
awk '/^## 9\./{flag=1; next} /^## /{flag=0} flag && /^[a-z]/' "$out" | head -5
echo ""
echo "Open $out for the full report."
