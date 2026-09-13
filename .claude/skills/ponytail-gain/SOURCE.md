# ponytail-gain skill source pin

| Field | Value |
| --- | --- |
| Upstream | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |
| Commit | `974d940a1c5344210874150b98ff0d2c861fab6a` |
| Upstream path | `skills/ponytail-gain` |
| Imported | 2026-09-06 |
| Imported SKILL.md sha256 | `24e01d1c9715cb136ba1c4f1e52a95940c0193558b876828e537736480d6408b` |

Copied from the MIT-licensed ponytail plugin. Not imported with `just add_skill`
because the plugin is a multi-harness tree, not a skills.sh package.

## Adaptations from upstream

1. **First-party** — `SOURCE.md` and `evals/` are loadout-repo owned and must
   survive a bump.
2. **Upstream-verbatim** — `SKILL.md` is copied from upstream unless a later
   adaptation is listed.
