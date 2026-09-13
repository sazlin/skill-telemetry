# ponytail skill source pin

| Field | Value |
| --- | --- |
| Upstream | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |
| Commit | `974d940a1c5344210874150b98ff0d2c861fab6a` |
| Upstream path | `skills/ponytail` |
| Imported | 2026-09-06 |
| Current SKILL.md sha256 | `8891b013aec55a182926abfd3ac314e74400acdb04409ab179d67dafb4c2d550` |

Copied from the MIT-licensed ponytail plugin. Not imported with `just add_skill`
because the plugin is a multi-harness tree, not a skills.sh package.

## Adaptations from upstream

1. **First-party** — `SOURCE.md` and `evals/` are loadout-repo owned and must
   survive a bump.
2. **Adapted** — dropped `argument-hint` from SKILL.md frontmatter. Loadout
   skill lint allows only name, description, license, allowed-tools, metadata,
   and compatibility.
3. **Rule excerpt** — `rules/coding/ponytail.mdc` mirrors selected SKILL.md
   sections. On every bump, refresh that rule per adaptation #5; ladder rungs
   are validated by `test_ponytail_rule_core_ladder_matches_skill`.
4. **Hook intensity** — the loadout `ponytail-activate` SessionStart hook filters
   SKILL.md body per `PONYTAIL_DEFAULT_MODE` / config `defaultMode`
   (`off` skips injection; `lite`/`full`/`ultra` strip other intensity rows
   and examples). Same behavior as upstream JS filtering, vendored in bash.
5. **Fail-open markup, CLI, and API trust-boundary sync** — loadout-owned excerpts in
   `rules/coding/ponytail.mdc` must stay aligned with SKILL.md on bumps:
   ladder (see #3), fail-open markup (skip-depth tag walk, not
   match-until-close regex), CLI trust boundaries (required argc, URL
   http(s) scheme, redirect validation, fetch timeout, 5 MiB body cap with
   reject-only), parser self-checks (unclosed and nested skip-tags), and
   CLI `main` entry, malformed JSON as 400, whitespace-only text
   rejection, and fields named in the spec (wrong type is 400). Canonical
   source: `skills/ponytail/SKILL.md`.
