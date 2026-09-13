# ponytail-debt skill source pin

| Field | Value |
| --- | --- |
| Upstream | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |
| Commit | `974d940a1c5344210874150b98ff0d2c861fab6a` |
| Upstream path | `skills/ponytail-debt` |
| Imported | 2026-09-06 |
| Imported SKILL.md sha256 | `c84fba75f0ca12bfe83f9a78ea02fd125c5dd3f1fbb18124105a489937f284e6` |

Copied from the MIT-licensed ponytail plugin. Not imported with `just add_skill`
because the plugin is a multi-harness tree, not a skills.sh package.

## Adaptations from upstream

1. **First-party** — `SOURCE.md` and `evals/` are loadout-repo owned and must
   survive a bump.
2. **Upstream-verbatim** — `SKILL.md` is copied from upstream unless a later
   adaptation is listed.
