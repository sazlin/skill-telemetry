# Badge reference

Rules (from `evidence.md`): 3 to 6 badges, one line, directly under the title or the tagline,
ordered CI > version > license > adoption > community. Every badge links to what it measures.
Use one consistent shields style for all of them. Omit badges entirely rather than shipping
one that renders as "invalid" or points at a dead service.

Replace `OWNER`, `REPO`, `PACKAGE` before use. Verify each URL renders before committing:
a broken badge is worse than no badge.

## Build / CI

```markdown
[![CI](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/ci.yml?branch=main)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
```
`ci.yml` must be the real workflow filename. `?branch=main` pins it to the default branch.

## Version, by ecosystem

| Ecosystem | Badge URL | Link target |
| --- | --- | --- |
| npm | `https://img.shields.io/npm/v/PACKAGE` | `https://www.npmjs.com/package/PACKAGE` |
| PyPI | `https://img.shields.io/pypi/v/PACKAGE` | `https://pypi.org/project/PACKAGE/` |
| crates.io | `https://img.shields.io/crates/v/PACKAGE` | `https://crates.io/crates/PACKAGE` |
| Go | `https://pkg.go.dev/badge/MODULE.svg` | `https://pkg.go.dev/MODULE` |
| Maven Central | `https://img.shields.io/maven-central/v/GROUP/ARTIFACT` | the artifact page |
| NuGet | `https://img.shields.io/nuget/v/PACKAGE` | `https://www.nuget.org/packages/PACKAGE` |
| RubyGems | `https://img.shields.io/gem/v/PACKAGE` | `https://rubygems.org/gems/PACKAGE` |
| Packagist | `https://img.shields.io/packagist/v/VENDOR/PACKAGE` | the Packagist page |
| Hex | `https://img.shields.io/hexpm/v/PACKAGE` | `https://hex.pm/packages/PACKAGE` |
| Docker | `https://img.shields.io/docker/v/OWNER/REPO?sort=semver` | Docker Hub page |
| No registry | `https://img.shields.io/github/v/release/OWNER/REPO` | `https://github.com/OWNER/REPO/releases` |

## License

```markdown
[![License](https://img.shields.io/github/license/OWNER/REPO)](LICENSE)
```
Use a static badge instead when the repo's license file is non-standard:
`https://img.shields.io/badge/license-Apache--2.0-blue`.

## Adoption

```markdown
[![Downloads](https://img.shields.io/npm/dm/PACKAGE)](https://www.npmjs.com/package/PACKAGE)
[![Downloads](https://img.shields.io/pypi/dm/PACKAGE)](https://pypi.org/project/PACKAGE/)
[![Stars](https://img.shields.io/github/stars/OWNER/REPO)](https://github.com/OWNER/REPO/stargazers)
```
Downloads beat stars when the package is published. Use stars only when there is no registry
and the count is already respectable; a `12 stars` badge reads as a liability.

## Community / docs

```markdown
[![Discord](https://img.shields.io/discord/SERVER_ID?label=Discord&logo=discord)](https://discord.gg/INVITE)
[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://docs.example.com)
```

## Quality (optional, only if real)

```markdown
[![Coverage](https://img.shields.io/codecov/c/github/OWNER/REPO)](https://codecov.io/gh/OWNER/REPO)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/OWNER/REPO/badge)](https://scorecard.dev/viewer/?uri=github.com/OWNER/REPO)
```

## Status, for pre-1.0 or paused projects

```markdown
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange)]()
[![Status: maintenance](https://img.shields.io/badge/status-maintenance-yellow)]()
```
Honest status badges prevent the most expensive misunderstanding a README can cause.

## Do not use

Tech-stack logo rows (`Built with React`), "made with love", "PRs welcome" (write the sentence
instead), hit counters, visitor badges, "awesome" self-badges, and any badge that a human has
to update by hand.
