---
name: rtk
description: Use when running noisy CLI commands (git status, git diff, git log, pytest,
  cargo test, npm test, ls, docker ps, ruff, grep) in an agent session, when bash
  output is eating context, or when the user mentions rtk, Token Killer, or token
  compression for command output.
license: Apache-2.0
metadata:
  loadout.managed: 'true'
  loadout.source: skills/rtk/SKILL.md
  loadout.sha: 9180c3a
---

# RTK (Token Killer)

RTK is a CLI proxy that compresses bash output before it reaches the model.
The `coding` loadout installs the GitHub `rtk-ai/rtk` binary and a fail-open
rewrite hook. Prefix noisy commands with `rtk` when the hook is not in play.

**Core principle:** the right binary answers `rtk gain`. crates.io `rtk` is a
different project (Rust Type Kit).

## When to use

- Shell output from git, test runners, directory listings, or linters is large
- The user asks for rtk / Token Killer
- You are about to install or verify `rtk`

**Skip** for interactive TTY tools, binary downloads, and commands the user
asked to see unfiltered.

## Install and identity

This loadout's `cli_tools` installs a pinned GitHub release into
`~/.local/bin`. Do not pipe an upstream install script to a shell. Do not
install the crates.io crate named rtk (Rust Type Kit). `cargo install --git
https://github.com/rtk-ai/rtk` is a last resort only if the user asks.

Verify: `rtk gain` prints a savings dashboard. If that fails, PATH has the
wrong binary or none.

Do not run `rtk init`. Loadout owns `.cursor/hooks.json` and
`.claude/settings.json`. `rtk init` writes a competing global hook. Sync
already registers `rtk hook cursor` / `rtk hook claude` via `hooks/rtk-rewrite`.

## Commands

```bash
rtk git status
rtk pytest -q
rtk gain          # confirm Token Killer, not crates.io
```

The rewrite hook remaps Cursor `.command` to `rtk hook cursor` and delegates
Claude PreToolUse to `rtk hook claude`. Missing `rtk` fails open.

## Common mistakes

| Excuse | Reality |
| --- | --- |
| "curl the install script" | Unpinned pipe-to-shell. Use loadout sync. |
| "install crates.io rtk" | Wrong package. Check `rtk gain`. |
| "rtk init to enable hooks" | Fights this loadout. Do not. |
