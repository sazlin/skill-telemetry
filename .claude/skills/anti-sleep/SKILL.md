---
name: anti-sleep
description: Use when running long local tasks on a Mac or MacBook, waiting on CI,
  polling other systems, or when the user says /anti-sleep; also when idle sleep,
  lid close, battery sleep, or caffeinate -w PID might kill the agent between separate
  shell calls.
metadata:
  loadout.managed: 'true'
  loadout.source: skills/anti-sleep/SKILL.md
  loadout.sha: 9180c3a
---

# Anti-sleep

Keep a **local macOS** agent session from idle-sleeping during long waits and polls.

**Core principle:** One detached idle-sleep assertion for the whole session. Not per wait.

## When to use

- `/anti-sleep`, overnight/local MacBook work, CI waits, polling, idle sleep
- **Skip** on Linux, CI VMs, and Cursor Cloud — the script no-ops there

## Steps

1. Start once, before the first long wait:

```bash
scripts/keep-awake start
```

Run it from this skill's directory (next to `SKILL.md`). After sync that is usually `.claude/skills/anti-sleep/`.

Default timeout is 8 hours. Pass seconds to override: `keep-awake start 14400`.

2. Wait and poll with plain `sleep` / `gh` / HTTP. Do not wrap those commands.
3. After a long wait, `keep-awake status`. If it is not running, `start` again.
4. If work may exceed the timeout, `keep-awake renew` (overlap, then drop the old PID).
5. When the session is done: `keep-awake stop`.

Verify on macOS with `pmset -g assertions` — look for `PreventUserIdleSystemSleep`.

## Do not

| Temptation | Why it fails |
| --- | --- |
| `caffeinate -w $$` | Each agent shell call is a new PID; the assertion dies when that call ends |
| `caffeinate -i sleep 30` (wrap each wait) | Gaps between waits have no assertion |
| `caffeinate -d` / `-u` | Keeps the display on; wasteful. Idle sleep is `-i` only |
| `sudo pmset … disablesleep` | Persistent, needs root, bag/overheat risk. Never |
| Mouse jigglers / Amphetamine | Extra tools; `caffeinate` is built in |

Lid close is a different switch. `caffeinate -i` does **not** block clamshell sleep. Leave the lid open, or use AC + external display (Apple clamshell). Do not flip `disablesleep`.

## Red flags

- About to `sleep`/`AwaitShell` for minutes with no keeper running
- About to wrap a single wait instead of `keep-awake start`
- About to `sudo pmset` because the lid will close
