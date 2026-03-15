# Contributing to BodhiKit

Thank you for your interest in contributing to BodhiKit. This document explains how to add skills, agents, knowledge bases, and rules to the plugin.

## Before You Start

BodhiKit is a research-backed educational tool. Every feature should:
1. Be grounded in learning science research (cite your sources)
2. Integrate the teaching personality (Oogway/Yoda/Gautama Buddha/Dr. B.R. Ambedkar)
3. Follow the core principle: the learner writes code, BodhiKit asks questions
4. Never give direct answers — use Socratic questioning and graduated hints

## File Formats

### Adding a Skill

Create `skills/<skill-name>/SKILL.md` with this frontmatter:

```yaml
---
description: "One-line description of what the skill does"
user-invocable: true
argument-hint: "[optional|arg|syntax]"
---
```

Requirements:
- Reference `teaching-personality` knowledge base for tone
- Reference the specific knowledge base for your methodology (e.g., `spaced-repetition`, `blooms-taxonomy`, `feynman-technique`)
- Include phase-based workflow with checkpoints
- If the skill uses an agent, use "You MUST use the Agent tool to launch the `<agent-name>` agent" and include a fallback instruction
- If the skill should be auto-invocable by other skills, note this in the description

### Adding an Agent

Create `agents/<agent-name>.md` with this frontmatter:

```yaml
---
name: agent-name
description: "What the agent does"
model: sonnet
tools: Read, Glob, Grep, Bash
disallowedTools: Edit, Write, Agent
maxTurns: 20
memory: project
---
```

Requirements:
- Agents should be read-only (disallow Edit, Write)
- Use `sonnet` for complex tasks, `haiku` for simpler ones
- Set reasonable `maxTurns` (15-30)
- Include the teaching personality in the agent's instructions

### Adding a Knowledge Base

Create `knowledge/<kb-name>/SKILL.md` with this frontmatter:

```yaml
---
description: "Knowledge base title and purpose"
user-invocable: false
---
```

Requirements:
- Always set `user-invocable: false`
- Cite research sources
- Organize with clear headings and tables
- Keep content actionable, not just theoretical

### Adding a Rule

Create `rules/<rule-name>.md` with this frontmatter:

```yaml
---
paths:
  - "**/<glob-pattern>"
---
```

Requirements:
- Use glob patterns that match relevant files
- Keep rules concise and actionable
- Include the teaching personality context

## Personality Integration

Every contribution must integrate the BodhiKit personality. This means:
- Never say "that is wrong" — say "let us look at this differently"
- Never say "this is easy" — say "this takes practice"
- Frame everything as exploration, not testing
- Use nature metaphors sparingly (seeds, roots, growth, paths)
- Celebrate effort and strategy, not talent

Read `knowledge/teaching-personality/SKILL.md` thoroughly before contributing.

## Research Requirement

If you add a new skill or methodology, include:
- The research it is based on (author, year, key finding)
- How it applies to programming education specifically
- Why it improves learning outcomes

Add citations to the README's "The Science" section if appropriate.

## Testing Your Contribution

```
claude --plugin-dir ~/code/bodhikit
```

Test your skill by:
1. Invoking it directly
2. Checking that it integrates with the personality
3. Verifying it updates tracking files correctly (if applicable)
4. Confirming it does not give direct answers

## Submitting

1. Fork the repository on Codeberg
2. Create a branch for your changes
3. Update README.md and GUIDE.md with your additions
4. Update CHANGELOG.md
5. Submit a pull request with a description of what you added and the research backing it

## Code of Conduct

Be respectful, patient, and constructive — the same values BodhiKit teaches.
