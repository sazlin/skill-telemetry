# Agent Instructions

<!-- BEGIN LOADOUT: agent-rules (generated, do not edit) -->
## Agent Rules

This project's coding rules live as individual files under `.cursor/rules/`. Cursor loads
them automatically based on the scopes below. Other agents do not, so you have to load them
yourself.

Before editing files that match a rule's scope, read that rule file and follow it. These are
binding project conventions, not suggestions. Rules scoped `Always` apply to all work in this
repo, so read them at the start of a session.

| Rule | Scope | What it covers |
| --- | --- | --- |
| `.cursor/rules/colocated-evals.mdc` | Always | Keep agent and skill eval fixtures next to the artifact they test. Applies when adding or moving evals. |
| `.cursor/rules/commit-style.mdc` | Always | Write focused, reviewable commits with clear intent. |
| `.cursor/rules/no-cursor-coauthor.mdc` | Always | Never include Cursor as a git commit co-author. |
| `.cursor/rules/pr-ready-for-review.mdc` | Always | Open GitHub PRs ready for review, never as drafts. If the change is not ready, do not open a PR; ask the user what is blocking. |
| `.cursor/rules/repo-conventions.mdc` | Always | Preserve repository conventions and verify scoped changes. |
| `.cursor/rules/agent-authoring.mdc` | `agents/*/*.md`, `agents/_agent_template.md` | Author and import agents from agents/_agent_template.md. Applies only when working on files under agents/. |
| `.cursor/rules/ponytail.mdc` | `**/*.py`, `**/*.pyi`, `**/*.ts`, `**/*.tsx`, `**/*.js`, `**/*.jsx`, `**/*.mjs`, `**/*.cjs`, `**/*.go`, `**/*.rs`, `**/*.rb`, `**/*.java`, `**/*.kt`, `**/*.swift`, `**/*.c`, `**/*.h`, `**/*.cpp`, `**/*.hpp`, `**/*.cs`, `**/*.php`, `**/*.sh` | Ponytail, lazy senior dev mode. Always pick the simplest solution that works. |
| `.cursor/rules/typescript-code-style.mdc` | `**/*.ts`, `**/*.tsx`, `**/*.mts`, `**/*.cts` | Write simple, typed, maintainable TypeScript that a reviewer can read in one pass. |

Skills are installed at `.claude/skills/`, which both Cursor and Claude Code load
automatically. You do not need to read those manually.

Managed by [loadout](https://github.com/sazlin/loadout). Run `just loadout-sync` to regenerate.
Edits inside this block are overwritten.
<!-- END LOADOUT: agent-rules -->
