# Section playbook

One entry per POPULAR element from `evidence.md`. Each entry gives the job the section does,
the include/omit test, the rules that make it good, and the failure modes seen in the corpus.
Quoted examples are real, from the 40-repo corpus.

---

## 1. Title

**Job:** tell a reader which project they are looking at in under one second.

**Include:** always. Exactly one H1 (67% of corpus), or a centered HTML block containing the
name (70% use a centered header). Never both.

**Rules**
- The title is the project name, nothing else. No tagline appended, no version, no emoji.
- Match the name to the package/binary name users will type. If the repo name differs, show the
  canonical name and put the other in italic parentheses: `# Standard Readme Style _(standard-readme)_`.
- If a logo exists, the logo replaces nothing: logo first, then the name as text so search and
  screen readers still find it.

**Failure modes:** H1 that repeats the org name; multiple H1s (33% of corpus, which breaks
GitHub's auto-outline); a title that is a sentence.

---

## 2. One-line description (tagline)

**Job:** answer "what is this and who is it for" before the reader scrolls.

**Include:** always. Directly under the title (or under the badge row).

**Rules**
- One sentence, under ~120 characters (standard-readme's hard limit).
- Say the category plus the differentiator: noun phrase first, benefit second.
  `An extremely fast Python package and project manager, written in Rust.` (uv)
  `Get up and running with large language models locally.` (ollama)
- It must match the GitHub repo description and the package manager description. Three copies
  that disagree is the most common inconsistency in the corpus.
- No marketing superlatives that cannot be checked ("revolutionary", "best-in-class"). Claims
  that can be checked ("10-100x faster than pip") are fine and are common in high-traffic repos.
- Do not use a blockquote (`>`) for it; 95% of the corpus does not, and standard-readme forbids it.

**Failure modes:** starting with "This project is a ..."; describing the implementation
("A Python package that uses asyncio and Pydantic") instead of the outcome.

---

## 3. Badges

**Job:** answer maintenance, version, and trust questions at a glance.

**Include:** yes for anything published or CI-tested. Omit entirely for an internal or toy repo:
zero badges reads better than three broken ones.

**Rules**
- 3 to 6. Median in the corpus is 3; p75 is 6. More than 8 is a badge wall.
- Each badge must answer a question a real evaluator asks. Ranked by usefulness:
  1. Build/CI status (is it green right now)
  2. Package version (npm/PyPI/crates/Maven/Go) with a link to the package page
  3. License
  4. Downloads or stars (adoption)
  5. Docs link or chat invite
- Order them in that order, one line, no line breaks between them.
- Every badge must be a link to the thing it measures. Non-clickable badges are dead weight.
- Avoid: tech-stack logo rows, "made with love", "PRs welcome" (say it in words), maintained-manually
  badges that go stale.
- Use `https://img.shields.io/...` with `?style=flat` (default) or one consistent style for all.

See `badges.md` for copy-paste badge URLs by ecosystem.

---

## 4. Hero visual (screenshot, GIF, diagram, or logo)

**Job:** prove the thing works and show what it looks like, faster than prose can.

**Include:** almost always. 87% of the corpus has a visual in the first 1.5 KB, and 84% of
READMEs praised in awesome-readme cite a visual as the reason.
**Omit** only if the project genuinely has no visible output and no architecture worth drawing
(rare: even a terminal command with its output rendered as a GIF beats nothing).

**Rules**
- Pick by project type: CLI to a terminal GIF or asciinema; GUI/web app to a screenshot;
  library to a short code sample (code is the visual); infrastructure to a small diagram.
- Keep it under ~1 MB and under ~15 seconds. Long GIFs are skipped.
- Store it in the repo (`docs/`, `assets/`, or `.github/`) and use a relative link, so forks and
  clones still render it. GitHub user-content URLs work but tie the image to one upload.
- Always set alt text; it is the accessibility floor and it shows when the image 404s.
- A logo is not proof. If you have a logo *and* a demo, the demo goes above the fold and the
  logo goes inline with the title.

---

## 5. Features / why

**Job:** convert "what is this" into "why would I switch".

**Include:** when the one-liner plus the demo do not already make the value obvious, which is
most of the time. 55% of the corpus has a bullet list within the first 3 KB.
**Omit** when the project is a single-purpose utility whose name says everything.

**Rules**
- 3 to 6 bullets. Not 12.
- Lead each bullet with the benefit in bold, then one clause of detail:
  `**Zero config.** Detects your framework and picks sane defaults.`
- Prefer differentiators over table stakes. "Written in Rust", "works offline",
  "no telemetry", "single static binary" are differentiators. "Easy to use" is not.
- Numbers beat adjectives: "starts in 40 ms", "installs in one command", "supports 40+ providers".
- Never use this section as a roadmap. Features that do not exist yet belong nowhere near it.

---

## 6. Installation

**Job:** get the reader from zero to installed with one copy-paste.

**Include:** always, for anything installable. Omit only for a repo that is cloned and run
directly, and in that case the clone command lives in Quick start instead.

**Rules**
- Lead with the single most common path, in one fenced block, language-tagged:
  ```bash
  npm install -g my-tool
  ```
- Prerequisites go as one line above the command, not as their own section
  (own-section requirements appear in only 15% of the corpus): "Requires Node 20+."
- Additional platforms/managers (Homebrew, Docker, Windows, build from source) go in a
  `<details>` block or a small table, not as five more H3s.
- Verify the command on a clean machine. An install command that fails is the fastest way to
  lose a user, and both 2026 guides name it as the top mistake.
- Never use `$` prompt prefixes inside a copyable block; they break paste.
- Pin nothing that will age badly (no `@1.2.3` in the primary command) unless the project
  requires it.

---

## 7. Quick start / usage

**Job:** show the smallest complete thing that works, and what it prints.

**Include:** always. This plus Installation are the only two near-universal substantive sections.

**Rules**
- One minimal, runnable example. It must run against the current version, unmodified.
- Show the output. "Use examples liberally, and show the expected output if you can"
  (makeareadme). Expected output turns an example into a self-test for the reader.
- Language-tag every fence (75% of the corpus does): ```bash, ```python, ```ts, ```go.
- Keep the first example under ~15 lines. Depth goes to the docs site or an `examples/` folder.
- Two examples maximum above the fold: one CLI, one library call, if the project has both faces.
- Don't teach the domain. Assume the reader knows their language; they need *your* API shape.

---

## 8. Documentation links

**Job:** route the 80% of questions the README should not answer.

**Include:** whenever any docs exist. 90% of the corpus links a docs site, making this the
single most common element in the entire study.

**Rules**
- Link the docs *home* plus at most 3 deep links that match the reader's next question
  (Getting started, API reference, Configuration, Migration guide).
- Use a short bulleted list or one line of pipe-separated links. Not a table.
- If there is no docs site, this section becomes "Learn more" pointing to `docs/` in the repo
  via relative links.
- Do not inline the API reference. 15% of the corpus does; all of them regret it when the API
  changes.

---

## 9. Community / support

**Job:** tell a stuck reader exactly where to go, and show the project is alive.

**Include:** when at least one real channel exists (Discussions, Discord, Slack, forum, mailing
list). 55% of the corpus has this section; 42% link a chat platform.

**Rules**
- Route by intent, one line each: bug to Issues, question to Discussions/Discord,
  security to SECURITY.md, commercial to email.
- Only list channels someone actually reads. A dead Discord is worse than no Discord.
- Keep it 2 to 4 lines. This is a switchboard, not a community manifesto.

---

## 10. Contributing (as a link)

**Job:** signal openness and route contributors, without spending README space.

**Include:** always, as 1 to 3 lines linking `CONTRIBUTING.md`. 85% of the corpus links it;
only 22% writes an inline section. Follow the 85%.

**Rules**
- State the posture in one sentence ("Contributions are welcome" / "We are not taking feature
  PRs right now"), then link the file. Honesty about a closed process saves everyone time.
- Put the dev setup, test commands, and PR checklist in CONTRIBUTING.md, not here.
- Link Code of Conduct from CONTRIBUTING.md, not from the README (only 7% of the corpus gives
  it a README section).
- If `CONTRIBUTING.md` does not exist, either create it or drop this to a single sentence
  pointing at Issues. Never link a file that is not there.

---

## 11. License

**Job:** make the legal answer findable in one scroll, and satisfy the community-profile check.

**Include:** always for public repos. 82% of the corpus mentions a license; 80% link the file.

**Rules**
- One line is enough, and is what half the corpus does:
  `Licensed under the [MIT License](LICENSE).`
- Name the license explicitly. "Open source" is not a license.
- Link the actual `LICENSE` file with a relative link.
- If the project is dual-licensed or has a commercial exception (BSL, SSPL, Elastic, fair-code),
  say so in one extra clause here. Surprising license terms discovered late are a trust event.
- The license badge is not a substitute for the line, but it is a good complement.

---

---

## 12. Cross-cutting rules learned from field-testing

**If the README is also a package long description, links must be absolute.**
PyPI (and most registries other than npm) renders `README.md` as the project page but resolves
nothing relative to the repo: `./demo.gif`, `LICENSE`, and `./CONTRIBUTING.md` all break there.
Check for `readme = "README.md"` in `pyproject.toml`, `long_description` in `setup.py` or
`setup.cfg`, or the equivalent in your packaging config. When it is present, use
`https://raw.githubusercontent.com/OWNER/REPO/BRANCH/path` for images and full GitHub URLs for
in-repo files. Otherwise, prefer relative links. `scripts/score_readme.py --repo .` detects this
and flips the rule automatically.

**Never restate a runtime floor from memory.** Read it out of the manifest:
`requires-python` (pyproject), `engines.node` (package.json), `rust-version` (Cargo.toml),
the `go` directive (go.mod). A README that says "Python 3.9 or above" while the package
requires 3.10 sends users into an install error, and this exact drift was present in the
real-world repo used to test this skill.

**A list that already lives in the docs is a staleness bomb.** Tables of adapters, plugins,
integrations, or supported platforms drift the moment one is added. Either keep the table short
and add one line naming the docs page as the source of truth, or cut the table and keep the
sentence. Never ship the table alone.

**Check caveats against the changelog before repeating them.** Known limitations get fixed.
A caveat copied from an old release note or an old README ("not supported on Python 3.14")
can be false by the time you write it. Search `CHANGELOG.md` for the newest entry on that
topic, and drop the caveat if it was resolved.

**Steal the small operational details.** The lines users thank maintainers for are tiny:
the short flag alias, "it creates the file if it does not exist", "press F1 for help",
"this bundles three extra adapters, so it is larger". They cost one clause and prevent
a support thread each.

## Ordering

Median position across the corpus, 0.0 = top, 1.0 = bottom:

```
Features 0.05  >  Quick start 0.12  >  Installation 0.14  >  Usage 0.33  >  API 0.34
>  Requirements 0.39  >  Integrations 0.42  >  Documentation 0.44  >  Community 0.50
>  Deployment 0.52  >  Examples/Config 0.63  >  Contributing 0.71  >  Security 0.83
>  Contributors 0.91  >  License 1.00
```

The canonical order that follows from this, and the order the template uses:

1. Header block (name, tagline, badges, visual)
2. Features / why
3. Installation
4. Quick start / usage
5. Documentation
6. (optional domain section: integrations, deployment, comparison, architecture)
7. Community / support
8. Contributing (link)
9. License

License is last in 100% of the corpus that has it. Never open with a table of contents.
