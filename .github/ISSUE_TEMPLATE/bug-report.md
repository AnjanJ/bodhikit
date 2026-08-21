---
name: Bug report
about: Something broke, graded wrong, or did not do what the docs say
title: "Bug: [skill] short description"
labels: bug
---

## What happened

<!-- What the tutor did. A short paste of the relevant turn(s) is ideal. -->

## What you expected

<!-- What the docs (README / GUIDE) or common sense led you to expect instead. -->

## Which skill

<!-- e.g. /bodhikit:teach, /bodhikit:continue, /bodhikit:housekeep migrate. If it happened mid-chain (e.g. inside /continue), say so. -->

## Plugin version

<!-- Run /plugin in Claude Code and copy the bodhikit version shown. -->

## Tracking files (only if the bug is about tracking state)

If the bug is about progress, reviews, boxes, Bloom levels, streaks, or migration, paste the relevant file from `.bodhi/` (`state.json`, `spaced-review.json`, or the output of `bodhi-state verify`).

**Before pasting: strip anything personal.** These files can contain your own notes, concept names from work projects, and session commentary. Remove or replace anything you would not want public. If you would rather share only numbers, `bodhi-state export-anonymized` produces a stats-only block with no concept names or free text.

```json

```

## Anything else

<!-- OS, whether python3 is on PATH (Windows users especially), anything unusual about your setup. -->
