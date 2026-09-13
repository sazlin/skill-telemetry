# ponytail-activate hook source pin

| Field | Value |
| --- | --- |
| Upstream | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |
| Commit | `974d940a1c5344210874150b98ff0d2c861fab6a` |
| Upstream path | `hooks/ponytail-activate.js` |
| Imported | 2026-09-06 |

See also [`skills/ponytail/SOURCE.md`](../../skills/ponytail/SOURCE.md) for the
vendored skill pin and rule-sync contract.

## Adaptations from upstream

Vendored for loadout sync (skills + hooks land under the project tree; no plugin
install). Compared to the upstream Node SessionStart hook:

1. **Project root** — resolve three levels up from the script directory
   (`.cursor/hooks/ponytail-activate/` → project root), not plugin root.
2. **Skill path** — `resolve_skills_dir()` reads `skills_dir` from
   `.loadout.yaml` (default `.claude/skills`), then `resolve_skills_root()`
   joins it to the project root unless the value is already absolute. Skill file
   is `<skills_root>/ponytail/SKILL.md`. `validate_skill_file_path()` rejects
   symlinks and paths outside the canonical skills directory (via portable
   `python3` `os.path.realpath`, not GNU `realpath`).
3. **Harness detection** — if the first argument is `cursor` (from `hook.yaml`
   `cursor.args`), emit Cursor `{ "additional_context": "…" }`; otherwise emit
   Claude Code `hookSpecificOutput.additionalContext`. JSON encoding uses
   `python3` `json.dumps` for standards-compliant escaping.
4. **Mode** — `get_default_mode()` resolves `off|lite|full|ultra` in order:
   `PONYTAIL_DEFAULT_MODE` env var, then `~/.config/ponytail/config.json`
   `defaultMode` (or platform equivalent via `get_config_path()`), then `full`.
   Invalid values fall back to `full`. `off` skips injection.
   `filter_skill_body_for_mode()` strips YAML frontmatter and filters intensity
   table rows and `- lite:` / `- full:` / `- ultra:` example lines to match the
   active mode (same contract as upstream JS filtering).
5. **SessionStart matcher** — `startup` only. Upstream also runs on
   `resume`, `clear`, and `compact`; loadout skips those so resume/compact
   do not re-embed the full SKILL.md (avoids redundant I/O and token bloat
   after compaction).
6. **Resilience** — refuse skill files over 64 KiB; unreadable or missing files
   emit a short error string in context and exit 0 (no absolute paths in errors).
   Missing, failing, or hung `python3` (2s deadline per invocation, plus an ERR
   trap) fail-opens with empty `additional_context` / `additionalContext` and
   exit 0, so SessionStart never blocks the host or the stacked session-start
   hook. File reads (skill body, config) use the same deadline.
7. **Out of scope** — no statusline nudge, no `~/.claude/.ponytail-active`
   flag file, no UserPromptSubmit mode tracker, no SubagentStart injector.
   Those stay plugin-only. The globbed rule plus this SessionStart hook cover
   always-on activation in loadout consumer projects.
