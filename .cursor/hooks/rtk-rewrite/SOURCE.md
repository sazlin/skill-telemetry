# rtk-rewrite hook source pin

| Field | Value |
| --- | --- |
| Upstream | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) |
| Release | `v0.48.0` |
| Commit | `fde0a8f185945556f51718de0f4c430bb62b3df6` |
| Upstream commands | `rtk hook cursor`, `rtk hook claude` |
| Imported | 2026-09-06 |

## Adaptations from upstream

Not a copy of `rtk init`. Loadout registers a project-local wrapper so sync
owns `.cursor/hooks.json` and `.claude/settings.json`.

1. **Delegate** — call `rtk hook cursor` or `rtk hook claude`; do not reimplement
   rewrite rules.
2. **Cursor payload** — native `beforeShellExecution` sends `.command`. Upstream
   `rtk hook cursor` reads `/tool_input/command`. The wrapper remaps before
   delegating so the rewrite applies on Cursor Cloud without `preToolUse`.
3. **Fail open** — missing `rtk`, missing `jq`, empty stdin, or a non-zero
   `rtk hook` exit (including crates.io `rtk` with no `hook` subcommand): Cursor
   `{"permission":"allow"}`, Claude silent exit 0. Do not call `rtk gain` on
   the hot path.
4. **Do not run `rtk init`** — that writes a global Cursor `preToolUse` entry
   (`rtk hook cursor`) and fights loadout-owned hook configs.
