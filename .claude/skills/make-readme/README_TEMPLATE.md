<!-- ==========================================================================
     HOW TO USE THIS TEMPLATE                                    (delete block)
     ==========================================================================
     Every instruction in this file lives inside an HTML comment that opens with
     "INSTRUCTIONS" and closes with "END INSTRUCTIONS". Those blocks are invisible
     when GitHub renders the page, but they must still be DELETED before you ship.
     Everything OUTSIDE those blocks is real README content that you edit in place.

     PLACEHOLDERS look like {{THIS}}. Every one must be replaced or its line deleted.

     PROCESS
       1. Work top to bottom. Do not skip a section; decide to keep or cut it.
       2. Each section starts with a STATUS line telling you how often the top 40
          OSS developer tools on GitHub actually use it, and a KEEP IF / CUT IF test.
          When in doubt, cut. The median top-tier README is ~130 lines, ~10 sections.
       3. Fill content, then delete that section's instruction block.
       4. Run the final CHECKLIST at the bottom, then delete the checklist too.

     FINAL VERIFICATION (run both; both must return nothing)
       grep -n "INSTRUCTIONS" README.md
       grep -n "{{" README.md
     ========================================================================== -->

<!-- INSTRUCTIONS: HEADER BLOCK -------------------------------------------------
STATUS: Required. A centered header is used by 70% of the top 40; 87% put a visual
        in the first 1.5 KB; 77% ship badges.

STEPS
  1. LOGO (optional): if you have one, keep the <img> line and point src at a file
     committed in this repo (docs/ or assets/). Use a relative path so forks render it.
     Height 80 to 120 px. No logo? Delete the <img> line entirely.
  2. NAME: replace {{PROJECT_NAME}}. Use the name users type to install or import,
     not the repo slug, if they differ. Exactly one H1 in the whole file.
  3. TAGLINE: one sentence, under 120 characters, no period-ending marketing fluff.
     Formula: [what it is] + [for whom / what it beats].
     Good: "An extremely fast Python package manager, written in Rust."
     Bad:  "This project is a tool that aims to help developers be more productive."
     Copy this exact sentence into the GitHub repo description and your package
     manifest description. All three must match.
  4. BADGES: 3 to 6, one line, in this order: CI, version, license, downloads/stars,
     chat/docs. Every badge must be a link. See references/badges.md for URLs.
     No badges available and nothing published? Delete all badge lines. Zero badges
     beats broken badges.
  5. Keep the centered <div>; it is the corpus norm. If you prefer plain markdown,
     replace the whole block with "# Name" then the tagline then the badge line.
END INSTRUCTIONS -->

<div align="center">

<img src="{{RELATIVE_PATH_TO_LOGO}}" alt="{{PROJECT_NAME}} logo" height="96">

# {{PROJECT_NAME}}

{{ONE_SENTENCE_TAGLINE}}

[![CI](https://img.shields.io/github/actions/workflow/status/{{OWNER}}/{{REPO}}/{{WORKFLOW}}.yml?branch=main)](https://github.com/{{OWNER}}/{{REPO}}/actions)
[![Version](https://img.shields.io/{{REGISTRY_BADGE_PATH}})]({{REGISTRY_URL}})
[![License](https://img.shields.io/github/license/{{OWNER}}/{{REPO}})](LICENSE)

</div>

<!-- INSTRUCTIONS: HERO VISUAL --------------------------------------------------
STATUS: Strongly recommended. 87% of the top 40 have a visual above the fold, and
        84% of READMEs praised in awesome-readme are praised for a visual.

STEPS
  1. Pick ONE, by project type:
       CLI            -> terminal GIF or asciinema cast of a real session
       Web / GUI app  -> a single screenshot of the main screen
       Library / SDK  -> no image; the Quick start code block below IS the visual,
                         so DELETE this whole visual section
       Infrastructure -> one simple architecture diagram (mermaid renders natively)
  2. Commit the asset in the repo (docs/ or assets/) and use a relative path. EXCEPTION: if this
     README is also your package's long description (pyproject.toml has readme = "README.md",
     or setup.py sets long_description), relative paths break on the package page. Use
     https://raw.githubusercontent.com/OWNER/REPO/BRANCH/path instead, and use full GitHub URLs
     for LICENSE and CONTRIBUTING.md too.
  3. Under 1 MB, under 15 seconds, no music, no intro card. Show the tool doing its
     actual job, starting from the first command.
  4. Alt text is mandatory: it is what a screen reader and a broken image show.
  5. Do not stack a logo, a screenshot, and a GIF. One visual above the fold.
END INSTRUCTIONS -->

<p align="center">
  <img src="{{RELATIVE_PATH_TO_DEMO}}" alt="{{SHORT_DESCRIPTION_OF_WHAT_THE_DEMO_SHOWS}}" width="720">
</p>

<!-- INSTRUCTIONS: WHY / FEATURES -----------------------------------------------
STATUS: Keep by default. 55% of the top 40 put a bullet list in the first 3 KB.
KEEP IF: the tagline plus the visual do not already make the value obvious.
CUT IF:  the project is a one-purpose utility whose name says everything, or the
         bullets would all be table stakes.

STEPS
  1. Write 3 to 6 bullets. Never more than 6.
  2. Each bullet: bold benefit, then one clause of detail. Lead with the verb or noun,
     not with "It".
       **Zero config.** Detects your framework and picks working defaults.
  3. Prefer what makes you DIFFERENT: speed numbers, offline, single binary, no
     telemetry, works with X. Delete any bullet that a competitor could copy verbatim.
  4. Use real numbers where you have them ("cold start 40 ms", "40+ providers").
  5. Never list unreleased work here. Shipped only.
  6. Rename the heading to "Why {{PROJECT_NAME}}" if the bullets are comparative
     rather than a feature inventory.
END INSTRUCTIONS -->

## Features

- **{{BENEFIT_1}}.** {{ONE_CLAUSE_OF_DETAIL}}
- **{{BENEFIT_2}}.** {{ONE_CLAUSE_OF_DETAIL}}
- **{{BENEFIT_3}}.** {{ONE_CLAUSE_OF_DETAIL}}

<!-- INSTRUCTIONS: INSTALLATION -------------------------------------------------
STATUS: Required for anything installable (52% have the heading; 100% of installable
        projects need it). CUT IF: the project is cloned and run, in which case move
        the clone+run commands into Quick start and delete this section.

STEPS
  1. ONE primary command, in one fenced block, tagged ```bash. The single path most
     of your users will take. No alternatives in the primary block.
  2. Prerequisites go on ONE line above the block ("Requires Node 20+."), never as
     their own section. Only list what actually blocks installation.
     READ THE FLOOR FROM THE MANIFEST, not from memory or the old README:
     requires-python (pyproject.toml), engines.node (package.json), rust-version (Cargo.toml),
     the go directive (go.mod). Stating a lower floor than the manifest sends users into an
     install error, and it is the most common factual defect in real READMEs.
  2b. If your installer needs its own bootstrap (uv, pnpm, rustup), give the one-line install
     for it too, or link its install page. Do not assume the reader already has your tool.
  3. No "$" prompt characters inside the block; they break copy-paste.
  4. Do not pin a version in the primary command unless the project requires it.
  5. Extra platforms (Homebrew, Docker, Windows, build from source) go inside the
     <details> block below. Delete the <details> block if you have only one path.
  6. VERIFY: run the exact command in a clean container or fresh VM before shipping.
     A failing install command is the single most damaging README defect.
END INSTRUCTIONS -->

## Installation

{{ONE_LINE_OF_PREREQUISITES_OR_DELETE_THIS_LINE}}

```bash
{{PRIMARY_INSTALL_COMMAND}}
```

<details>
<summary>Other install methods</summary>

```bash
# Homebrew
{{BREW_COMMAND}}

# Docker
{{DOCKER_COMMAND}}

# From source
{{SOURCE_BUILD_COMMANDS}}
```

</details>

<!-- INSTRUCTIONS: QUICK START --------------------------------------------------
STATUS: Required. 52% have this exact heading; 77% of the top 40 ship a fenced code
        block. With Installation, this is the highest-value section in the file.

STEPS
  1. Show the SMALLEST COMPLETE thing that works. Under ~15 lines.
  2. It must run as written against the current release. Copy it out and run it.
  3. Show the expected output, either as a comment in the block or in a second block.
     Output turns your example into a test the reader can self-check.
  4. Tag the fence with a language (```bash, ```python, ```ts, ```go). 75% of the
     top 40 do; untagged fences lose syntax highlighting.
  5. If the project has both a CLI and a library face, show one example of each and
     stop there. Two examples maximum.
  6. Do not teach the language or the domain. Show YOUR shape: the import, the call,
     the flags, the result.
  7. Anything longer belongs in docs/ or examples/, linked from the Documentation
     section below.
END INSTRUCTIONS -->

## Quick start

```{{LANGUAGE_TAG}}
{{MINIMAL_RUNNABLE_EXAMPLE}}
```

```
{{EXPECTED_OUTPUT}}
```

<!-- INSTRUCTIONS: OPTIONAL DOMAIN SECTION --------------------------------------
STATUS: Pick AT MOST ONE of the options below, or delete this whole block.
        These are the only "extra" sections that data supports, and each is
        conditional. Using two or more makes the README bloat.

  A. Supported integrations / models / providers  (40% of the top 40, and the one
     place a table earns its keep). USE WHEN the matrix of what you support IS the
     product (AI tooling, connectors, plugins, drivers). Table columns: name,
     status, notes. Cap at ~12 rows, then link the full list.

  B. Deployment / self-hosting  (20%). USE WHEN self-hosting is a primary path.
     One command to run it (Docker or compose), then link the deployment docs.
     State clearly whether a hosted version exists and how it differs.

  C. Comparison / alternatives  (12%). USE WHEN entering a crowded category where
     readers already use a competitor. Be scrupulously fair; an unfair table is
     read as a red flag. Facts only, no adjectives, link your sources.

  D. How it works / architecture  (5%). USE WHEN the mechanism is the reason to
     trust the project (protocols, security tools, infrastructure). 5 to 10 lines
     plus one diagram. Mermaid blocks render natively on GitHub.

STEPS
  1. Delete the options you are not using, including their example markup.
  2. Rename the heading to the concrete thing ("Supported models", "Self-hosting").
END INSTRUCTIONS -->

## {{OPTIONAL_DOMAIN_SECTION_NAME}}

| {{COLUMN_1}} | {{COLUMN_2}} | {{COLUMN_3}} |
| --- | --- | --- |
| {{ROW}} | {{ROW}} | {{ROW}} |

<!-- INSTRUCTIONS: DOCUMENTATION ------------------------------------------------
STATUS: Keep. 90% of the top 40 link a docs site, making this the most common
        element measured in the entire study.
CUT IF:  there is genuinely no documentation anywhere. In that case, write the docs.

STEPS
  1. Link the docs home first, then AT MOST 3 deep links that match the reader's
     next question: Getting started, API reference, Configuration, Migration.
  2. No docs site? Point at files in this repo with relative links (docs/guide.md).
     Relative links are used by 72% of the top 40 and keep working in forks.
  3. Do NOT inline the API reference or the full configuration table here. Link them.
     Inlined references go stale and push the important parts below the fold.
  4. Keep it to 3 to 5 lines total.
END INSTRUCTIONS -->

## Documentation

- [Documentation]({{DOCS_URL}}) for the full guide
- [{{DEEP_LINK_1_NAME}}]({{DEEP_LINK_1_URL}})
- [{{DEEP_LINK_2_NAME}}]({{DEEP_LINK_2_URL}})

<!-- INSTRUCTIONS: COMMUNITY / SUPPORT ------------------------------------------
STATUS: Keep when at least one real channel exists. 55% of the top 40 have it.
CUT IF:  the only channel is Issues; in that case fold one Issues line into
         Contributing below and delete this section.

STEPS
  1. Route by intent, one line each. Bug to Issues. Question to Discussions or chat.
     Security to SECURITY.md. Commercial to an email address.
  2. List only channels a maintainer actually reads. A dead Discord is worse than
     no Discord.
  3. 2 to 4 lines. This is a switchboard, not a manifesto.
END INSTRUCTIONS -->

## Community and support

- Bugs and feature requests: [open an issue](https://github.com/{{OWNER}}/{{REPO}}/issues)
- Questions and ideas: [{{CHANNEL_NAME}}]({{CHANNEL_URL}})
- Security reports: see [SECURITY.md](SECURITY.md)

<!-- INSTRUCTIONS: CONTRIBUTING -------------------------------------------------
STATUS: Keep as a LINK, not as a section. 85% of the top 40 link CONTRIBUTING.md
        while only 22% write an inline contributing section. Follow the 85%.

STEPS
  1. One sentence stating your posture, then the link. Be honest if the project is
     not taking outside PRs; that saves everyone time and is respected.
  2. Dev setup, test commands, style rules, and the PR checklist go in
     CONTRIBUTING.md, NOT here.
  3. Link CODE_OF_CONDUCT.md from CONTRIBUTING.md, not from the README.
  4. If CONTRIBUTING.md does not exist: create it, or reduce this to one sentence
     pointing at Issues. Never link a file that is not in the repo.
  5. First-timer hook (optional, one clause): link the good-first-issue label.
END INSTRUCTIONS -->

## Contributing

{{ONE_SENTENCE_POSTURE}} See [CONTRIBUTING.md](CONTRIBUTING.md) to get started, or browse
[good first issues](https://github.com/{{OWNER}}/{{REPO}}/labels/good%20first%20issue).

<!-- INSTRUCTIONS: LICENSE ------------------------------------------------------
STATUS: Required for public repos, and always LAST. 82% of the top 40 state a
        license; in 100% of those that give it a section, it is the final section.

STEPS
  1. One line is enough and is what half the corpus does.
  2. Name the license explicitly (MIT, Apache-2.0, AGPL-3.0). "Open source" is not
     a license name.
  3. Link the actual LICENSE file with a relative link, and make sure that file exists.
  4. Dual licensing, a commercial exception, or a source-available license (BSL,
     SSPL, Elastic, fair-code)? Say so here in one extra clause. A surprising
     license discovered late destroys trust.
  5. Third-party/data licenses that differ from the code license get one extra line.
END INSTRUCTIONS -->

## License

Licensed under the [{{LICENSE_NAME}}]({{LICENSE_FILE_PATH}}).

<!-- ==========================================================================
     FINAL CHECKLIST                                            (delete block)
     ==========================================================================
     CONTENT
       [ ] A stranger can say what this does and who it is for within 10 seconds.
       [ ] The tagline matches the GitHub repo description and the package manifest.
       [ ] Exactly one H1 in the file.
       [ ] Install command was run on a clean machine and worked.
       [ ] Quick start example was copy-pasted and run against the current version.
       [ ] Expected output shown.
       [ ] Every fenced block has a language tag.
       [ ] 3 to 6 badges, every one links somewhere, every one renders.
       [ ] Every linked in-repo file exists (LICENSE, CONTRIBUTING.md, SECURITY.md,
           images). Relative links, not absolute github.com URLs.
       [ ] Every image has alt text.
       [ ] Runtime version floors match the manifest exactly.
       [ ] If this README is a package long description, images and in-repo links are absolute.
       [ ] Any carried-over caveat is still true in the newest CHANGELOG entry.
       [ ] Any table that duplicates a docs page names that page as the source of truth.
       [ ] No section describes unreleased work as if it shipped.
       [ ] License named explicitly and last.

     SHAPE
       [ ] Roughly 100 to 200 lines. Over 300 means move content into docs/.
       [ ] About 6 to 10 H2 sections.
       [ ] No table of contents unless the file is over ~150 lines.
       [ ] No section that exists only because a template had it.

     HYGIENE
       [ ] grep -n "INSTRUCTIONS" README.md   returns nothing
       [ ] grep -n "{{" README.md             returns nothing
       [ ] Markdown preview checked on GitHub, not only in an editor.
     ========================================================================== -->
